"""
Auth service business logic.
Handles Google token verification and user creation/retrieval.
"""

from typing import Optional
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, UserRole
from shared.config import get_settings
from shared.security import create_access_token


class AuthService:
    """Service layer for authentication operations."""

    GOOGLE_TOKEN_INFO_URL = "https://oauth2.googleapis.com/tokeninfo"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

    def __init__(self, db: AsyncSession):
        self._db = db
        self._settings = get_settings()

    async def verify_google_token(self, credential: str) -> dict:
        """
        Verify a Google ID token and return user info.

        Args:
            credential: Google ID token string.

        Returns:
            Dictionary with user info from Google.

        Raises:
            ValueError: If the token is invalid.
        """
        async with httpx.AsyncClient() as client:
            # Verify the ID token with Google
            response = await client.get(
                self.GOOGLE_TOKEN_INFO_URL,
                params={"id_token": credential},
            )

            if response.status_code != 200:
                raise ValueError("Invalid Google token")

            token_data = response.json()

            # Validate the audience matches our client ID
            if token_data.get("aud") != self._settings.GOOGLE_CLIENT_ID:
                raise ValueError("Token audience mismatch")

            return {
                "google_id": token_data["sub"],
                "email": token_data["email"],
                "name": token_data.get("name", token_data["email"]),
                "avatar_url": token_data.get("picture"),
            }

    async def get_or_create_user(self, google_user_info: dict) -> User:
        """
        Get existing user or create a new one from Google user info.

        Args:
            google_user_info: Dictionary with Google user data.

        Returns:
            User model instance.
        """
        # Try to find existing user
        result = await self._db.execute(
            select(User).where(User.google_id == google_user_info["google_id"])
        )
        user = result.scalar_one_or_none()

        if user:
            # Update user info from Google (name, avatar might change)
            user.name = google_user_info["name"]
            user.avatar_url = google_user_info.get("avatar_url")
            await self._db.flush()
            return user

        # Determine role based on admin emails
        admin_emails = [
            e.strip()
            for e in self._settings.ADMIN_EMAILS.split(",")
            if e.strip()
        ]
        role = (
            UserRole.ADMIN
            if google_user_info["email"] in admin_emails
            else UserRole.USER
        )

        # Create new user
        user = User(
            google_id=google_user_info["google_id"],
            email=google_user_info["email"],
            name=google_user_info["name"],
            avatar_url=google_user_info.get("avatar_url"),
            role=role,
        )
        self._db.add(user)
        await self._db.flush()
        return user

    def generate_token(self, user: User) -> str:
        """
        Generate a JWT access token for a user.

        Args:
            user: User model instance.

        Returns:
            JWT token string.
        """
        return create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "name": user.name,
                "role": user.role.value,
            }
        )

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Retrieve a user by their ID.

        Args:
            user_id: User UUID.

        Returns:
            User model instance or None.
        """
        result = await self._db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
