"""
AI Assistant Service — Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ai_router

app = FastAPI(
    title="Field Booker — AI Assistant",
    description="Intelligent agent for field search and recommendations",
    version="1.0.0",
    root_path="/api/ai",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ai_assistant"}

app.include_router(ai_router.router, tags=["AI"])
