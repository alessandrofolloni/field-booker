"""
Unit tests for the Auth service.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from app.models import User, UserRole
from app.services import AuthService
from shared.security import create_access_token, decode_access_token


# ──────────────────────────────────────
# JWT Token Tests
# ──────────────────────────────────────

class TestJWTTokens:
    """Tests for JWT token creation and validation."""

    def test_create_access_token(self):
        """Should create a valid JWT token."""
        data = {"sub": str(uuid4()), "email": "test@example.com", "role": "user"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_token(self):
        """Should decode a valid JWT token."""
        user_id = str(uuid4())
        data = {"sub": user_id, "email": "test@example.com", "role": "user"}
        token = create_access_token(data)

        payload = decode_access_token(token)

        assert payload["sub"] == user_id
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "user"

    def test_decode_invalid_token_raises(self):
        """Should raise HTTPException for invalid token."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            decode_access_token("invalid-token")

        assert exc_info.value.status_code == 401

    def test_token_contains_expiration(self):
        """Token should contain an expiration claim."""
        data = {"sub": str(uuid4())}
        token = create_access_token(data)
        payload = decode_access_token(token)

        assert "exp" in payload


# ──────────────────────────────────────
# Auth Service Tests
# ──────────────────────────────────────

class TestAuthService:
    """Tests for the AuthService business logic."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        db = AsyncMock()
        db.flush = AsyncMock()
        db.add = MagicMock()
        return db

    @pytest.fixture
    def auth_service(self, mock_db):
        """Create an AuthService instance with mock DB."""
        return AuthService(mock_db)

    @pytest.mark.asyncio
    async def test_get_or_create_user_creates_new(self, auth_service, mock_db):
        """Should create a new user when no existing user found."""
        # Mock: no existing user found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        google_info = {
            "google_id": "google123",
            "email": "test@example.com",
            "name": "Test User",
            "avatar_url": "https://photo.url",
        }

        with patch.object(auth_service, '_settings') as mock_settings:
            mock_settings.ADMIN_EMAILS = ""
            user = await auth_service.get_or_create_user(google_info)

        # Verify add was called (new user created)
        mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_or_create_user_returns_existing(self, auth_service, mock_db):
        """Should return existing user when found."""
        existing_user = MagicMock(spec=User)
        existing_user.google_id = "google123"
        existing_user.email = "test@example.com"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_user
        mock_db.execute = AsyncMock(return_value=mock_result)

        google_info = {
            "google_id": "google123",
            "email": "test@example.com",
            "name": "Updated Name",
            "avatar_url": "https://new-photo.url",
        }

        user = await auth_service.get_or_create_user(google_info)

        assert user == existing_user
        # Verify add was NOT called (user already exists)
        mock_db.add.assert_not_called()

    def test_generate_token(self, auth_service):
        """Should generate a valid JWT token for a user."""
        mock_user = MagicMock(spec=User)
        mock_user.id = uuid4()
        mock_user.email = "test@example.com"
        mock_user.name = "Test User"
        mock_user.role = UserRole.USER

        token = auth_service.generate_token(mock_user)

        assert token is not None
        payload = decode_access_token(token)
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "user"

    def test_generate_token_admin(self, auth_service):
        """Should include admin role in token."""
        mock_user = MagicMock(spec=User)
        mock_user.id = uuid4()
        mock_user.email = "admin@example.com"
        mock_user.name = "Admin User"
        mock_user.role = UserRole.ADMIN

        token = auth_service.generate_token(mock_user)
        payload = decode_access_token(token)

        assert payload["role"] == "admin"


# ──────────────────────────────────────
# User Model Tests
# ──────────────────────────────────────

class TestUserModel:
    """Tests for the User model."""

    def test_user_role_enum(self):
        """UserRole enum should have correct values."""
        assert UserRole.USER.value == "user"
        assert UserRole.ADMIN.value == "admin"

    def test_user_repr(self):
        """User __repr__ should be descriptive."""
        user = User.__new__(User)
        user.email = "test@example.com"
        user.role = UserRole.USER

        assert "test@example.com" in repr(user)
        assert "user" in repr(user)
