"""
Sports fields API routes.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_db
from shared.security import get_current_user, require_admin
from app.schemas import (
    FieldCreate, FieldUpdate, FieldResponse, FieldListResponse,
)
from app.services import FieldsService

router = APIRouter()


@router.get("/nearby", response_model=FieldListResponse)
async def get_nearby_fields(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(default=10.0, ge=0.1, le=100.0),
    sport_ids: Optional[str] = Query(None, description="Comma-separated sport UUIDs"),
    min_rating: Optional[float] = Query(None, ge=1, le=5),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Search for sports fields near a location.

    Returns fields within the specified radius, optionally filtered
    by sport type and minimum rating.
    """
    parsed_sport_ids = None
    if sport_ids:
        try:
            parsed_sport_ids = [UUID(s.strip()) for s in sport_ids.split(",")]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid sport ID format",
            )

    service = FieldsService(db)
    fields, total = await service.search_nearby(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        sport_ids=parsed_sport_ids,
        min_rating=min_rating,
        page=page,
        page_size=page_size,
    )

    return FieldListResponse(
        items=[FieldResponse(**f) for f in fields],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{field_id}", response_model=FieldResponse)
async def get_field(
    field_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a sports field by ID."""
    service = FieldsService(db)
    field = await service.get_by_id(field_id)

    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found",
        )

    field_dict = service._field_to_dict(field)
    return FieldResponse(**field_dict)


@router.post("/", response_model=FieldResponse, status_code=status.HTTP_201_CREATED)
async def create_field(
    request: FieldCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """Create a new sports field (admin only)."""
    service = FieldsService(db)

    field = await service.create(
        name=request.name,
        description=request.description,
        latitude=request.latitude,
        longitude=request.longitude,
        address=request.address,
        city=request.city,
        phone=request.phone,
        email=request.email,
        website=request.website,
        booking_url=request.booking_url,
        price_info=request.price_info,
        opening_hours=request.opening_hours,
        photos=request.photos,
        sport_ids=request.sport_ids,
        created_by=UUID(current_user["sub"]),
    )

    field_dict = service._field_to_dict(field)
    return FieldResponse(**field_dict)


@router.put("/{field_id}", response_model=FieldResponse)
async def update_field(
    field_id: UUID,
    request: FieldUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    """Update a sports field (admin only)."""
    service = FieldsService(db)
    update_data = request.model_dump(exclude_unset=True)

    field = await service.update(field_id, **update_data)
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found",
        )

    field_dict = service._field_to_dict(field)
    return FieldResponse(**field_dict)


@router.delete("/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_field(
    field_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    """Delete a sports field (admin only)."""
    service = FieldsService(db)
    deleted = await service.delete(field_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found",
        )
