"""
AI Agent Service — Gemini with automatic function calling.
Uses Python callables as tools so Gemini handles the entire tool-call loop.
"""

import asyncio
import logging
import os
from typing import List, Optional

import httpx
import google.generativeai as genai
from shared.config import get_settings

logger = logging.getLogger(__name__)


def _resolve_fields_url(configured_url: str) -> str:
    """Swap Docker internal hostnames to localhost when running outside Docker."""
    docker_hostnames = ("http://fields:", "http://auth:", "http://submissions:", "http://ai:")
    if any(configured_url.startswith(h) for h in docker_hostnames):
        port = configured_url.split(":")[-1].rstrip("/")
        return f"http://localhost:{port}"
    return configured_url


_SYSTEM_INSTRUCTION = (
    "You are the Field Booker Assistant, an expert at helping users find sports fields in Italy. "
    "When a user asks to find fields near a city or address: "
    "1. Call geocode_address to get coordinates from the place name. "
    "2. If they mention a sport by name, call get_available_sports to find the correct sport ID. "
    "3. Call search_nearby_fields with those coordinates (and optional sport_ids). "
    "List the results clearly: field name, address, sports available. "
    "If nothing is found, suggest trying a larger radius_km. "
    "Respond in the same language the user wrote in (Italian or English)."
)


class AIAgentService:
    def __init__(self):
        self.settings = get_settings()
        self.fields_url = _resolve_fields_url(self.settings.FIELDS_SERVICE_URL)
        logger.info(f"AI service -> fields URL: {self.fields_url}")

        if self.settings.GOOGLE_API_KEY:
            os.environ["GOOGLE_API_KEY"] = self.settings.GOOGLE_API_KEY
            genai.configure(api_key=self.settings.GOOGLE_API_KEY)

        # Build sync tool functions as closures so they capture fields_url
        fields_url = self.fields_url

        def geocode_address(address: str) -> dict:
            """Convert a city name, neighbourhood or street address into latitude/longitude.

            Args:
                address: The place to geocode, e.g. "Roma", "Milano centro", "Via Garibaldi 10 Roma".

            Returns:
                Dict with latitude, longitude, display_name  — or {"error": "..."}.
            """
            if not address or not address.strip():
                return {"error": "address cannot be empty"}
            try:
                with httpx.Client(timeout=10.0) as client:
                    r = client.get(
                        "https://nominatim.openstreetmap.org/search",
                        params={"q": address.strip(), "format": "json", "limit": 1},
                        headers={"User-Agent": "FieldBooker/1.0"},
                    )
                    data = r.json()
                    if data:
                        return {
                            "latitude": float(data[0]["lat"]),
                            "longitude": float(data[0]["lon"]),
                            "display_name": data[0]["display_name"],
                        }
                    return {"error": f"location not found: '{address}'"}
            except Exception as exc:
                logger.exception("geocode_address error")
                return {"error": str(exc)}

        def get_available_sports() -> list:
            """Return the full list of sports supported by the platform.
            Call this to translate a sport name (e.g. "padel") into its system ID.

            Returns:
                List of sport objects, each with id, name, icon, color.
            """
            try:
                with httpx.Client(timeout=10.0) as client:
                    r = client.get(f"{fields_url}/sports/")
                    if r.status_code == 200:
                        return r.json()
                    return {"error": f"sports endpoint returned {r.status_code}"}
            except Exception as exc:
                logger.exception("get_available_sports error")
                return {"error": str(exc)}

        def search_nearby_fields(
            latitude: float,
            longitude: float,
            radius_km: float = 10.0,
            sport_ids: str = "",
        ) -> dict:
            """Search for sports fields near a geographic coordinate.
            Always call geocode_address first to convert a city/address to coordinates.

            Args:
                latitude: Latitude of the centre point (−90 to 90).
                longitude: Longitude of the centre point (−180 to 180).
                radius_km: Search radius in kilometres, default 10, max 100.
                sport_ids: Comma-separated sport IDs to filter by (optional).

            Returns:
                Dict with "items" list of matching fields (name, address, sports, distance_km).
            """
            try:
                params: dict = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "radius_km": min(max(float(radius_km), 1.0), 100.0),
                    "page": 1,
                    "page_size": 10,
                }
                if sport_ids:
                    params["sport_ids"] = sport_ids
                with httpx.Client(timeout=12.0) as client:
                    r = client.get(f"{fields_url}/nearby", params=params)
                    if r.status_code == 200:
                        return r.json()
                    return {"error": f"fields service returned {r.status_code}"}
            except Exception as exc:
                logger.exception("search_nearby_fields error")
                return {"error": str(exc)}

        self._tools = [geocode_address, get_available_sports, search_nearby_fields]
        self._model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            tools=self._tools,
            system_instruction=_SYSTEM_INSTRUCTION,
        )

    # ------------------------------------------------------------------

    def _chat_sync(self, user_message: str, chat_history: list) -> str:
        """Run a full Gemini conversation turn synchronously (called in a thread)."""
        chat = self._model.start_chat(
            history=chat_history,
            enable_automatic_function_calling=True,
        )
        response = chat.send_message(user_message)
        return response.text or ""

    async def chat(
        self,
        user_message: str,
        history: Optional[List[dict]] = None,
        session_id: str = "default",
    ) -> dict:
        """Async entry-point: wraps the synchronous Gemini call in a thread pool."""
        if not user_message or not user_message.strip():
            return {"response": "Inserisci un messaggio.", "session_id": session_id}

        # Convert frontend history format → Gemini format
        chat_history = []
        if history:
            for msg in history:
                role = msg.get("role", "user")
                parts = msg.get("parts", [])
                text = parts[0].get("text", "") if parts else ""
                if text and role in ("user", "model"):
                    chat_history.append({"role": role, "parts": [text]})

        loop = asyncio.get_event_loop()
        try:
            text = await loop.run_in_executor(
                None, self._chat_sync, user_message.strip(), chat_history
            )
            if not text:
                text = "Non ho trovato risultati. Prova a specificare una città o uno sport."
            return {"response": text, "session_id": session_id}
        except Exception as exc:
            logger.exception("Gemini chat error")
            # Surface the real error so it's visible in the chat bubble for debugging
            return {
                "response": f"⚠️ Errore: {str(exc)[:400]}",
                "session_id": session_id,
                "error": str(exc),
            }
