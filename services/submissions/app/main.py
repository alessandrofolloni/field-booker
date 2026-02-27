"""
Submissions Service — Main Application
Handles user-submitted sports fields and admin approval workflow.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.database import init_db
from app.routers import submissions_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize DB on startup."""
    await init_db()
    yield


app = FastAPI(
    title="Field Booker — Submissions Service",
    description="Field submission & approval workflow",
    version="1.0.0",
    lifespan=lifespan,
    root_path="/api/submissions",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(submissions_router.router, tags=["Submissions"])


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "submissions"}
