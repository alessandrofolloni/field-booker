"""
Auth Service — Main Application
Handles Google OAuth login and JWT token management.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.database import init_db
from app.routers import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize DB on startup."""
    await init_db()
    yield


app = FastAPI(
    title="Field Booker — Auth Service",
    description="Authentication & user management service",
    version="1.0.0",
    lifespan=lifespan,
    root_path="/api/auth",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router.router, tags=["Authentication"])


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "auth"}
