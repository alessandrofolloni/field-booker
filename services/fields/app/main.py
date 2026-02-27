"""
Fields Service — Main Application
Handles sports fields CRUD, geospatial queries, reviews, and sport types.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.database import init_db
from app.routers import fields_router, sports_router, reviews_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize DB on startup."""
    await init_db()
    yield


app = FastAPI(
    title="Field Booker — Fields Service",
    description="Sports fields management & geospatial queries",
    version="1.0.0",
    lifespan=lifespan,
    root_path="/api/fields",
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
    return {"status": "healthy", "service": "fields"}


# Register routers
# Specific routers FIRST to avoid shadowing by /{field_id}
app.include_router(sports_router.router, prefix="/sports", tags=["Sports"])
app.include_router(reviews_router.router, prefix="/reviews", tags=["Reviews"])
app.include_router(fields_router.router, tags=["Fields"])
