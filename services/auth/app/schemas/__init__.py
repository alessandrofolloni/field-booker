"""
Pydantic schemas for the Auth service.
"""

from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


# ──────────────────────────────────────
# Request Schemas
# ──────────────────────────────────────

class GoogleLoginRequest(BaseModel):
    """Schema for Google OAuth login request."""
    credential: str  # Google ID token


# ──────────────────────────────────────
# Response Schemas
# ──────────────────────────────────────

class UserResponse(BaseModel):
    """Schema for user data in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: str
    avatar_url: Optional[str] = None
    role: str
    created_at: datetime


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserProfileResponse(BaseModel):
    """Schema for user profile response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: str
    avatar_url: Optional[str] = None
    role: str
    created_at: datetime
    updated_at: datetime
