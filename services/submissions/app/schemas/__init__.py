"""
Pydantic schemas for the Submissions service.
"""

from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SubmissionFieldData(BaseModel):
    """Schema for the field data within a submission."""
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


class SubmissionCreate(BaseModel):
    """Schema for creating a new submission."""
    field_data: SubmissionFieldData
    field_id: Optional[UUID] = None
    submission_type: str = Field(default="new", pattern=r"^(new|update)$")


class SubmissionReview(BaseModel):
    """Schema for admin reviewing a submission."""
    status: str = Field(..., pattern=r"^(approved|rejected)$")
    admin_notes: Optional[str] = None


class SubmissionResponse(BaseModel):
    """Schema for submission in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    user_email: str
    user_name: str
    field_id: Optional[UUID] = None
    submission_type: str
    field_data: dict
    status: str
    admin_notes: Optional[str]
    reviewed_by: Optional[UUID]
    created_at: datetime
    reviewed_at: Optional[datetime]


class SubmissionListResponse(BaseModel):
    """Schema for paginated submission list."""
    items: list[SubmissionResponse]
    total: int
    page: int
    page_size: int
