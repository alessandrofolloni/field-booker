"""
Sports types API routes.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_db
from shared.security import require_admin
from app.schemas import SportCreate, SportUpdate, SportResponse
from app.services import SportsService

router = APIRouter()


@router.get("/", response_model=list[SportResponse])
async def get_sports(
    db: AsyncSession = Depends(get_db),
):
    """Get all available sport types."""
    service = SportsService(db)
    sports = await service.get_all()
    return [SportResponse.model_validate(s) for s in sports]


@router.post("/", response_model=SportResponse, status_code=status.HTTP_201_CREATED)
async def create_sport(
    request: SportCreate,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    """Create a new sport type (admin only)."""
    service = SportsService(db)
    sport = await service.create(
        name=request.name,
        icon=request.icon,
        color=request.color,
    )
    return SportResponse.model_validate(sport)


@router.put("/{sport_id}", response_model=SportResponse)
async def update_sport(
    sport_id: UUID,
    request: SportUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    """Update a sport type (admin only)."""
    service = SportsService(db)
    update_data = request.model_dump(exclude_unset=True)
    sport = await service.update(sport_id, **update_data)

    if not sport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sport not found",
        )
    return SportResponse.model_validate(sport)


@router.delete("/{sport_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sport(
    sport_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    """Delete a sport type (admin only)."""
    service = SportsService(db)
    deleted = await service.delete(sport_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sport not found",
        )
