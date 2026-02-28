"""
Analytics routes — event logging and admin statistics.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_db
from shared.security import require_admin, get_optional_user
from app.schemas import AnalyticsEventCreate, AnalyticsStats, FieldAnalyticsStat
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.post("/event", status_code=201)
async def log_event(
    request: AnalyticsEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    Log a user interaction event. Public endpoint — works for both anonymous
    and authenticated users. Errors are swallowed to never block the UX.
    """
    try:
        service = AnalyticsService(db)
        user_id: Optional[UUID] = None
        if current_user and current_user.get("sub"):
            try:
                user_id = UUID(current_user["sub"])
            except (ValueError, AttributeError):
                pass

        await service.log_event(
            event_type=request.event_type,
            field_id=request.field_id,
            user_id=user_id,
            session_id=request.session_id,
            metadata=request.metadata,
        )
        await db.commit()
    except Exception:
        # Silently swallow — analytics must never crash the app
        pass

    return {"status": "ok"}


@router.get("/stats", response_model=AnalyticsStats)
async def get_stats(
    period_days: int = Query(default=30, ge=1, le=365),
    _admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated analytics stats for the given period. Admin only."""
    service = AnalyticsService(db)
    stats = await service.get_stats(period_days=period_days)
    top_fields_raw = await service.get_top_fields(limit=10)
    top_fields = [FieldAnalyticsStat(**f) for f in top_fields_raw]
    return AnalyticsStats(**stats, top_fields=top_fields)


@router.get("/fields/top")
async def get_top_fields(
    limit: int = Query(default=10, ge=1, le=50),
    metric: str = Query(default="views", pattern="^(views|bookings)$"),
    _admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get top N fields by metric (views or bookings). Admin only."""
    service = AnalyticsService(db)
    return await service.get_top_fields(limit=limit, metric=metric)
