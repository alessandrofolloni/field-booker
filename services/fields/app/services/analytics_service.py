"""
Analytics service — event logging and aggregation.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AnalyticsEvent, Field


class AnalyticsService:
    """Service layer for analytics event logging and aggregation."""

    def __init__(self, db: AsyncSession):
        self._db = db

    async def log_event(
        self,
        *,
        event_type: str,
        field_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        session_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> AnalyticsEvent:
        """Insert a new analytics event row."""
        event = AnalyticsEvent(
            event_type=event_type,
            field_id=field_id,
            user_id=user_id,
            session_id=session_id,
            event_metadata=metadata or {},
        )
        self._db.add(event)
        await self._db.flush()
        return event

    async def get_stats(self, period_days: int = 30) -> dict:
        """Aggregate event counts by type for the given time period."""
        since = datetime.now(timezone.utc) - timedelta(days=period_days)

        # Total counts per event_type
        counts_query = (
            select(
                AnalyticsEvent.event_type,
                func.count(AnalyticsEvent.id).label("cnt"),
            )
            .where(AnalyticsEvent.created_at >= since)
            .group_by(AnalyticsEvent.event_type)
        )
        result = await self._db.execute(counts_query)
        counts = {row.event_type: row.cnt for row in result.all()}

        # Events per day (date + event_type granularity)
        day_query = (
            select(
                func.date_trunc("day", AnalyticsEvent.created_at).label("day"),
                AnalyticsEvent.event_type,
                func.count(AnalyticsEvent.id).label("cnt"),
            )
            .where(AnalyticsEvent.created_at >= since)
            .group_by("day", AnalyticsEvent.event_type)
            .order_by("day")
        )
        day_result = await self._db.execute(day_query)
        events_by_day = [
            {
                "date": row.day.strftime("%Y-%m-%d"),
                "event_type": row.event_type,
                "count": row.cnt,
            }
            for row in day_result.all()
        ]

        return {
            "period_days": period_days,
            "total_field_views": counts.get("field_viewed", 0),
            "total_booking_clicks": counts.get("booking_clicked", 0),
            "total_ai_messages": counts.get("ai_message_sent", 0),
            "total_searches": counts.get("search_performed", 0),
            "total_filter_applied": counts.get("filter_applied", 0),
            "total_field_submitted": counts.get("field_submitted", 0),
            "events_by_day": events_by_day,
        }

    async def get_top_fields(self, limit: int = 10, metric: str = "views") -> list[dict]:
        """Return top N fields by view count or booking clicks (last 30 days)."""
        since = datetime.now(timezone.utc) - timedelta(days=30)

        # Subquery: view counts per field
        views_sq = (
            select(
                AnalyticsEvent.field_id,
                func.count(AnalyticsEvent.id).label("view_count"),
            )
            .where(
                and_(
                    AnalyticsEvent.event_type == "field_viewed",
                    AnalyticsEvent.field_id.is_not(None),
                    AnalyticsEvent.created_at >= since,
                )
            )
            .group_by(AnalyticsEvent.field_id)
            .subquery()
        )

        # Subquery: booking click counts per field
        bookings_sq = (
            select(
                AnalyticsEvent.field_id,
                func.count(AnalyticsEvent.id).label("booking_clicks"),
            )
            .where(
                and_(
                    AnalyticsEvent.event_type == "booking_clicked",
                    AnalyticsEvent.field_id.is_not(None),
                    AnalyticsEvent.created_at >= since,
                )
            )
            .group_by(AnalyticsEvent.field_id)
            .subquery()
        )

        query = (
            select(
                Field.id,
                Field.name,
                func.coalesce(views_sq.c.view_count, 0).label("view_count"),
                func.coalesce(bookings_sq.c.booking_clicks, 0).label("booking_clicks"),
            )
            .outerjoin(views_sq, Field.id == views_sq.c.field_id)
            .outerjoin(bookings_sq, Field.id == bookings_sq.c.field_id)
            .where(Field.is_active.is_(True))
        )

        if metric == "bookings":
            query = query.order_by(
                func.coalesce(bookings_sq.c.booking_clicks, 0).desc()
            )
        else:
            query = query.order_by(func.coalesce(views_sq.c.view_count, 0).desc())

        query = query.limit(limit)
        result = await self._db.execute(query)

        top_fields = []
        for row in result.all():
            views = row.view_count or 0
            bookings = row.booking_clicks or 0
            rate = round((bookings / views * 100), 1) if views > 0 else 0.0
            top_fields.append(
                {
                    "field_id": row.id,
                    "field_name": row.name,
                    "view_count": views,
                    "booking_clicks": bookings,
                    "conversion_rate": rate,
                }
            )

        return top_fields
