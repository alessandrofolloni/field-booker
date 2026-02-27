"""
Shared configuration using Pydantic Settings.
All services share the same base configuration.
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings

# Calculate project root (assuming this file is in services/shared/config.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_FILE = os.path.join(BASE_DIR, ".env")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://fieldbooker:fieldbooker_secret@db:5432/fieldbooker"

    # JWT
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # Services
    AUTH_SERVICE_URL: str = "http://auth:8001"
    FIELDS_SERVICE_URL: str = "http://fields:8002"
    SUBMISSIONS_SERVICE_URL: str = "http://submissions:8003"
    AI_SERVICE_URL: str = "http://ai:8004"

    # AI
    GOOGLE_API_KEY: str = ""

    # Admin
    ADMIN_EMAILS: str = ""

    model_config = {
        "env_file": ENV_FILE,
        "case_sensitive": True,
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
