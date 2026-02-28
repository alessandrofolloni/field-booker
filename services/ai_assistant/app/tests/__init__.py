"""
Unit tests for the AI Assistant service.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx


# ──────────────────────────────────────
# Tool: geocode_address
# ──────────────────────────────────────

class TestGeocodeAddress:
    """Tests for the geocode_address tool."""

    @pytest.fixture
    def service(self):
        """Create AIAgentService with mocked ADK dependencies."""
        with patch('app.services.agent_service.Agent'), \
             patch('app.services.agent_service.InMemoryRunner'), \
             patch('app.services.agent_service.FunctionTool'):
            from app.services.agent_service import AIAgentService
            svc = AIAgentService.__new__(AIAgentService)
            svc.settings = MagicMock()
            svc.settings.FIELDS_SERVICE_URL = "http://fields:8002"
            return svc

    @pytest.mark.asyncio
    async def test_geocode_success(self, service):
        """Should return coordinates for a valid address."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"lat": "41.9028", "lon": "12.4964", "display_name": "Roma, Italy"}
        ]

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            result = await service.geocode_address("Roma")

        assert result["latitude"] == 41.9028
        assert result["longitude"] == 12.4964
        assert "Roma" in result["display_name"]

    @pytest.mark.asyncio
    async def test_geocode_not_found(self, service):
        """Should return error when address not found."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            result = await service.geocode_address("xyznonexistentplace12345")

        assert "error" in result
        assert "not found" in result["error"].lower() or "non trovato" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_geocode_empty_address(self, service):
        """Should reject empty address."""
        result = await service.geocode_address("")
        assert "error" in result

    @pytest.mark.asyncio
    async def test_geocode_timeout(self, service):
        """Should handle timeout gracefully."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.TimeoutException("timeout")
            )
            result = await service.geocode_address("Roma")

        assert "error" in result
        assert "timeout" in result["error"].lower() or "timed out" in result["error"].lower()


# ──────────────────────────────────────
# Tool: search_nearby_fields
# ──────────────────────────────────────

class TestSearchNearbyFields:
    """Tests for the search_nearby_fields tool."""

    @pytest.fixture
    def service(self):
        with patch('app.services.agent_service.Agent'), \
             patch('app.services.agent_service.InMemoryRunner'), \
             patch('app.services.agent_service.FunctionTool'):
            from app.services.agent_service import AIAgentService
            svc = AIAgentService.__new__(AIAgentService)
            svc.settings = MagicMock()
            svc.settings.FIELDS_SERVICE_URL = "http://fields:8002"
            return svc

    @pytest.mark.asyncio
    async def test_search_returns_fields(self, service):
        """Should return list of fields from the fields service."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"id": "abc", "name": "Campo Test"}], "total": 1}

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            result = await service.search_nearby_fields(41.9028, 12.4964, 10.0)

        assert "items" in result

    @pytest.mark.asyncio
    async def test_search_invalid_latitude(self, service):
        """Should reject latitude > 90."""
        result = await service.search_nearby_fields(91.0, 12.0)
        assert "error" in result
        assert "latitude" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_search_invalid_longitude(self, service):
        """Should reject longitude > 180."""
        result = await service.search_nearby_fields(41.0, 181.0)
        assert "error" in result
        assert "longitude" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_search_with_sport_ids(self, service):
        """Should pass sport_ids as comma-separated string."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [], "total": 0}

        captured_params = {}

        async def mock_get(url, params=None, **kwargs):
            captured_params.update(params or {})
            return mock_response

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(side_effect=mock_get)
            await service.search_nearby_fields(41.9, 12.5, sport_ids=["uuid1", "uuid2"])

        assert "sport_ids" in captured_params
        assert "uuid1" in captured_params["sport_ids"]
        assert "uuid2" in captured_params["sport_ids"]

    @pytest.mark.asyncio
    async def test_search_timeout(self, service):
        """Should handle timeout gracefully."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.TimeoutException("timeout")
            )
            result = await service.search_nearby_fields(41.9, 12.5)

        assert "error" in result


# ──────────────────────────────────────
# Tool: get_available_sports
# ──────────────────────────────────────

class TestGetAvailableSports:
    """Tests for the get_available_sports tool."""

    @pytest.fixture
    def service(self):
        with patch('app.services.agent_service.Agent'), \
             patch('app.services.agent_service.InMemoryRunner'), \
             patch('app.services.agent_service.FunctionTool'):
            from app.services.agent_service import AIAgentService
            svc = AIAgentService.__new__(AIAgentService)
            svc.settings = MagicMock()
            svc.settings.FIELDS_SERVICE_URL = "http://fields:8002"
            return svc

    @pytest.mark.asyncio
    async def test_get_sports_success(self, service):
        """Should return sports list from the fields service."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "uuid1", "name": "Calcio", "icon": "⚽"},
            {"id": "uuid2", "name": "Tennis", "icon": "🎾"},
        ]

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            result = await service.get_available_sports()

        assert len(result) == 2
        assert result[0]["name"] == "Calcio"

    @pytest.mark.asyncio
    async def test_get_sports_service_error(self, service):
        """Should return error dict when fields service fails."""
        mock_response = MagicMock()
        mock_response.status_code = 500

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            result = await service.get_available_sports()

        assert "error" in result


# ──────────────────────────────────────
# Chat Method
# ──────────────────────────────────────

class TestChatMethod:
    """Tests for the AIAgentService.chat method."""

    @pytest.fixture
    def service(self):
        with patch('app.services.agent_service.Agent'), \
             patch('app.services.agent_service.InMemoryRunner'), \
             patch('app.services.agent_service.FunctionTool'):
            from app.services.agent_service import AIAgentService
            svc = AIAgentService.__new__(AIAgentService)
            svc.settings = MagicMock()
            svc.runner = MagicMock()
            return svc

    @pytest.mark.asyncio
    async def test_chat_empty_message(self, service):
        """Should return helpful response for empty message."""
        result = await service.chat("", session_id="test")
        assert "response" in result
        assert "message" in result["response"].lower() or result["response"]

    @pytest.mark.asyncio
    async def test_chat_returns_session_id(self, service):
        """Should return session_id in response."""
        async def mock_run_async(**kwargs):
            return
            yield  # Make it an async generator

        service.runner.run_async = mock_run_async
        result = await service.chat("Cerca campi a Roma", session_id="session_abc")
        assert result["session_id"] == "session_abc"

    @pytest.mark.asyncio
    async def test_chat_fallback_on_empty_response(self, service):
        """Should return fallback message if runner returns no text."""
        async def empty_generator(**kwargs):
            return
            yield

        service.runner.run_async = empty_generator
        result = await service.chat("test message", session_id="test")
        assert result["response"]  # Not empty
        assert "response" in result
