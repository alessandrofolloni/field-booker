"""
Auth service API routes.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_db
from shared.security import get_current_user
from app.schemas import GoogleLoginRequest, TokenResponse, UserResponse, UserProfileResponse
from app.services import AuthService

router = APIRouter()


@router.post("/login/google", response_model=TokenResponse)
async def google_login(
    request: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate a user via Google OAuth.

    Accepts a Google ID token, verifies it, creates or retrieves
    the user, and returns a JWT access token.
    """
    auth_service = AuthService(db)

    try:
        google_user_info = await auth_service.verify_google_token(request.credential)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    user = await auth_service.get_or_create_user(google_user_info)
    token = auth_service.generate_token(user)

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current authenticated user's profile."""
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(UUID(current_user["sub"]))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserProfileResponse.model_validate(user)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: dict = Depends(get_current_user),
):
    """Get a user by ID (authenticated users only)."""
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(user)
