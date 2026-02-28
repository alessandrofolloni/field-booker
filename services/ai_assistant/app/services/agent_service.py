"""
AI Agent Service — Powered by Google ADK (Agent Development Kit).
"""

import logging
import os
from typing import List, Optional, Any
import httpx
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import InMemoryRunner
from google.genai import types
from shared.config import get_settings

logger = logging.getLogger(__name__)


def _resolve_fields_url(configured_url: str) -> str:
    """
    When running locally (run_local.sh), services use Docker hostnames like
    'http://fields:8002' which are unreachable from the host machine.
    Detect this and fall back to localhost keeping the same port.
    """
    docker_hostnames = ("http://fields:", "http://auth:", "http://submissions:", "http://ai:")
    if any(configured_url.startswith(h) for h in docker_hostnames):
        port = configured_url.split(":")[-1].rstrip("/")
        return f"http://localhost:{port}"
    return configured_url


class AIAgentService:
    def __init__(self):
        self.settings = get_settings()

        # Ensure the API key is in the environment for the underlying genai client
        if self.settings.GOOGLE_API_KEY:
            os.environ['GOOGLE_API_KEY'] = self.settings.GOOGLE_API_KEY

        # Resolve correct URL: Docker hostname → localhost when running locally
        self.fields_url = _resolve_fields_url(self.settings.FIELDS_SERVICE_URL)
        logger.info(f"AI service → Fields URL resolved to: {self.fields_url}")

        # Track created ADK sessions to avoid duplicate creation errors
        self._sessions: set = set()

        # Define the agent with tools
        self.agent = Agent(
            model='gemini-1.5-flash',
            name='FieldBookerAssistant',
            instruction=(
                "You are the Field Booker Assistant. Help users find sports fields and venues. "
                "If they specify a location (city, neighborhood, address), use 'geocode_address' "
                "to get coordinates, then use 'search_nearby_fields'. "
                "If they mention a sport, use 'get_available_sports' to find the correct IDs. "
                "Be proactive: if you find fields, list the most relevant ones with their key details. "
                "Always be helpful, professional, and concise in Italian or English depending on the user's language."
            ),
            tools=[
                FunctionTool(self.search_nearby_fields),
                FunctionTool(self.geocode_address),
                FunctionTool(self.get_available_sports)
            ]
        )
        
        # Use InMemoryRunner for development (manages sessions in memory)
        self.runner = InMemoryRunner(agent=self.agent)

    async def _ensure_session(self, session_id: str) -> None:
        """Create the ADK session if it doesn't already exist."""
        if session_id not in self._sessions:
            try:
                await self.runner.session_service.create_session(
                    app_name=self.agent.name,
                    user_id="user_1",
                    session_id=session_id,
                )
            except Exception as e:
                # Session may already exist — that's fine
                logger.debug(f"Session note ({session_id}): {e}")
            finally:
                self._sessions.add(session_id)

    async def search_nearby_fields(self, latitude: float, longitude: float, radius_km: float = 10.0, sport_ids: Optional[List[str]] = None) -> Any:
        """
        Search for sports fields near specific coordinates.
        Args:
            latitude: The latitude of the location (-90 to 90).
            longitude: The longitude of the location (-180 to 180).
            radius_km: The search radius in kilometers. Defaults to 10.0.
            sport_ids: Optional list of sport IDs to filter by.
        """
        # Validate coordinates
        if not (-90 <= latitude <= 90):
            return {"error": f"Invalid latitude {latitude}: must be between -90 and 90"}
        if not (-180 <= longitude <= 180):
            return {"error": f"Invalid longitude {longitude}: must be between -180 and 180"}
        if not (0 < radius_km <= 500):
            radius_km = min(max(radius_km, 1), 500)

        url = f"{self.fields_url}/nearby"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "radius_km": radius_km
        }
        if sport_ids:
            params["sport_ids"] = ",".join(str(sid) for sid in sport_ids)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                if response.status_code == 200:
                    return response.json()
                return {"error": f"Fields service returned {response.status_code}: {response.text[:200]}"}
            except httpx.TimeoutException:
                return {"error": "Fields service timed out. Please try again."}
            except Exception as e:
                logger.exception("search_nearby_fields error")
                return {"error": str(e)}

    async def geocode_address(self, address: str) -> Any:
        """
        Convert a city name or address into geographical coordinates (latitude and longitude).
        Use this when a user provides a name of a place instead of coordinates.
        """
        if not address or not address.strip():
            return {"error": "Address cannot be empty"}

        async with httpx.AsyncClient() as client:
            try:
                url = "https://nominatim.openstreetmap.org/search"
                params = {"q": address.strip(), "format": "json", "limit": 1}
                headers = {"User-Agent": "FieldBooker/1.0 (field-booker-assistant)"}
                response = await client.get(url, params=params, headers=headers, timeout=10.0)
                if response.status_code == 200:
                    results = response.json()
                    if results:
                        data = results[0]
                        return {
                            "latitude": float(data["lat"]),
                            "longitude": float(data["lon"]),
                            "display_name": data["display_name"]
                        }
                return {"error": f"Address not found: '{address}'. Try a city name or full address."}
            except httpx.TimeoutException:
                return {"error": "Geocoding service timed out. Try again."}
            except Exception as e:
                logger.exception("geocode_address error")
                return {"error": str(e)}

    async def get_available_sports(self) -> Any:
        """
        Retrieve the list of available sports and their unique IDs.
        Essential for translating common names like 'padel' into the system's sport IDs.
        """
        url = f"{self.fields_url}/sports/"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=10.0)
                if response.status_code == 200:
                    return response.json()
                return {"error": "Failed to fetch sports"}
            except Exception as e:
                return {"error": str(e)}

    async def chat(self, user_message: str, history: List[dict] = None, session_id: str = "default"):
        """
        Process a user message and return the agent response.
        Session history is managed by the InMemoryRunner keyed on session_id.
        """
        if not user_message or not user_message.strip():
            return {"response": "Please enter a message.", "session_id": session_id}

        # Ensure the ADK session exists before running
        await self._ensure_session(session_id)

        new_content = types.Content(
            role='user',
            parts=[types.Part(text=user_message.strip())]
        )

        response_text = ""

        try:
            # ADK run_async returns an AsyncGenerator of events
            async for event in self.runner.run_async(
                user_id="user_1",
                session_id=session_id,
                new_message=new_content
            ):
                # Use is_final_response() to get the agent's final text output
                if hasattr(event, 'is_final_response') and event.is_final_response():
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                response_text += part.text
                # Fallback: also collect from any content event with text
                elif hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts') and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text and not response_text:
                                response_text += part.text
        except Exception as e:
            logger.exception("Error during ADK runner execution")
            return {
                "response": "Si è verificato un errore durante l'elaborazione. Riprova.",
                "session_id": session_id,
                "error": str(e)
            }

        if not response_text:
            response_text = "Non ho trovato risultati per la tua richiesta. Puoi fornire più dettagli sulla posizione o lo sport che cerchi?"

        return {
            "response": response_text,
            "session_id": session_id
        }
