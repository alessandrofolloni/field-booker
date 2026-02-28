"""
Pydantic schemas for the Fields service.
"""

from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ──────────────────────────────────────
# Sport Schemas
# ──────────────────────────────────────

class SportCreate(BaseModel):
    """Schema for creating a new sport."""
    name: str = Field(..., min_length=1, max_length=100)
    icon: str = Field(default="⚽", max_length=50)
    color: str = Field(default="#4CAF50", pattern=r"^#[0-9A-Fa-f]{6}$")


class SportUpdate(BaseModel):
    """Schema for updating a sport."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    is_active: Optional[bool] = None


class SportResponse(BaseModel):
    """Schema for sport in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    icon: str
    color: str
    is_active: bool


# ──────────────────────────────────────
# Opening Hours Schema
# ──────────────────────────────────────

class DayHours(BaseModel):
    """Schema for a single day's opening hours."""
    open: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    close: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    closed: bool = False


class OpeningHours(BaseModel):
    """Schema for weekly opening hours."""
    monday: Optional[DayHours] = None
    tuesday: Optional[DayHours] = None
    wednesday: Optional[DayHours] = None
    thursday: Optional[DayHours] = None
    friday: Optional[DayHours] = None
    saturday: Optional[DayHours] = None
    sunday: Optional[DayHours] = None


# ──────────────────────────────────────
# Field Schemas
# ──────────────────────────────────────

class FieldCreate(BaseModel):
    """Schema for creating a new sports field."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: str = Field(..., min_length=1, max_length=500)
    city: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=500)
    booking_url: Optional[str] = Field(None, max_length=500)
    price_info: Optional[str] = None
    opening_hours: Optional[dict] = None
    photos: Optional[list[str]] = None
    sport_ids: list[UUID] = Field(..., min_length=1)


class FieldUpdate(BaseModel):
    """Schema for updating a sports field."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    address: Optional[str] = Field(None, min_length=1, max_length=500)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=500)
    booking_url: Optional[str] = Field(None, max_length=500)
    price_info: Optional[str] = None
    opening_hours: Optional[dict] = None
    photos: Optional[list[str]] = None
    sport_ids: Optional[list[UUID]] = None
    is_active: Optional[bool] = None


class FieldResponse(BaseModel):
    """Schema for field in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str]
    latitude: float
    longitude: float
    address: str
    city: str
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    booking_url: Optional[str]
    price_info: Optional[str]
    opening_hours: Optional[dict]
    photos: Optional[list[str]]
    is_active: bool
    sports: list[SportResponse]
    avg_rating: Optional[float] = None
    review_count: int = 0
    created_at: datetime


class FieldListResponse(BaseModel):
    """Schema for paginated field list."""
    items: list[FieldResponse]
    total: int
    page: int
    page_size: int


# ──────────────────────────────────────
# Nearby Search Schema
# ──────────────────────────────────────

class NearbySearchParams(BaseModel):
    """Schema for nearby field search parameters."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(default=10.0, ge=0.1, le=100.0)
    sport_ids: Optional[list[UUID]] = None
    min_rating: Optional[float] = Field(None, ge=1, le=5)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ──────────────────────────────────────
# Review Schemas
# ──────────────────────────────────────

class ReviewCreate(BaseModel):
    """Schema for creating a review."""
    field_id: UUID
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    """Schema for review in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    field_id: UUID
    user_id: UUID
    rating: int
    comment: Optional[str]
    created_at: datetime
    user_name: Optional[str] = None


# ──────────────────────────────────────
# Analytics Schemas
# ──────────────────────────────────────

class AnalyticsEventCreate(BaseModel):
    """Schema for logging an analytics event."""
    event_type: str = Field(..., min_length=1, max_length=50)
    field_id: Optional[UUID] = None
    session_id: Optional[str] = Field(None, max_length=128)
    metadata: Optional[dict] = None


class FieldAnalyticsStat(BaseModel):
    """Analytics stats for a single field."""
    field_id: UUID
    field_name: str
    view_count: int
    booking_clicks: int
    conversion_rate: float  # booking_clicks / view_count * 100


class AnalyticsStats(BaseModel):
    """Aggregated analytics response."""
    period_days: int
    total_field_views: int
    total_booking_clicks: int
    total_ai_messages: int
    total_searches: int
    total_filter_applied: int
    total_field_submitted: int
    top_fields: list[FieldAnalyticsStat]
    events_by_day: list[dict]  # [{date, event_type, count}]
