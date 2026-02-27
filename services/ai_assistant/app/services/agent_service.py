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

class AIAgentService:
    def __init__(self):
        self.settings = get_settings()
        
        # Ensure the API key is in the environment for the underlying genai client
        if self.settings.GOOGLE_API_KEY:
            os.environ['GOOGLE_API_KEY'] = self.settings.GOOGLE_API_KEY
        
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

    async def search_nearby_fields(self, latitude: float, longitude: float, radius_km: float = 10.0, sport_ids: Optional[List[str]] = None) -> Any:
        """
        Search for sports fields near specific coordinates.
        Args:
            latitude: The latitude of the location.
            longitude: The longitude of the location.
            radius_km: The search radius in kilometers. Defaults to 10.0.
            sport_ids: Optional list of sport IDs to filter by.
        """
        url = f"{self.settings.FIELDS_SERVICE_URL}/nearby"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "radius_km": radius_km
        }
        if sport_ids:
            params["sport_ids"] = ",".join(sport_ids)
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                if response.status_code == 200:
                    return response.json()
                return {"error": f"Fields service returned {response.status_code}"}
            except Exception as e:
                return {"error": str(e)}

    async def geocode_address(self, address: str) -> Any:
        """
        Convert a city name or address into geographical coordinates (latitude and longitude).
        Use this when a user provides a name of a place instead of coordinates.
        """
        async with httpx.AsyncClient() as client:
            try:
                url = f"https://nominatim.openstreetmap.org/search"
                params = {"q": address, "format": "json", "limit": 1}
                # Nominatim requires a User-Agent
                headers = {"User-Agent": "FieldBooker/1.0"}
                response = await client.get(url, params=params, headers=headers, timeout=10.0)
                if response.status_code == 200 and response.json():
                    data = response.json()[0]
                    return {
                        "latitude": float(data["lat"]),
                        "longitude": float(data["lon"]),
                        "display_name": data["display_name"]
                    }
                return {"error": "Address not found"}
            except Exception as e:
                return {"error": str(e)}

    async def get_available_sports(self) -> Any:
        """
        Retrieve the list of available sports and their unique IDs.
        Essential for translating common names like 'padel' into the system's sport IDs.
        """
        url = f"{self.settings.FIELDS_SERVICE_URL}/sports/"
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
        History is managed by the runner's session if session_id is consistent.
        """
        new_content = types.Content(
            role='user',
            parts=[types.Part(text=user_message)]
        )

        response_text = ""
        
        # ADK run_async returns an AsyncGenerator of events
        async for event in self.runner.run_async(
            user_id="user_1", # Simplified for now
            session_id=session_id,
            new_message=new_content
        ):
            # We are interested in the final response parts
            if event.type == 'model_response' and event.content:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text
        
        # Fetch updated history from the session service if needed by the frontend
        # For now, we'll return a simple response
        return {
            "response": response_text,
            "session_id": session_id
        }
