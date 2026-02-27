"""
Fields service business logic.
Handles CRUD operations for fields, sports, and reviews with geospatial queries.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from geoalchemy2.functions import ST_DWithin, ST_MakePoint, ST_SetSRID, ST_Distance
from geoalchemy2.shape import to_shape

from app.models import Field, Sport, FieldSport, Review


class SportsService:
    """Service layer for sport type operations."""

    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_all(self, active_only: bool = True) -> list[Sport]:
        """Get all sport types."""
        query = select(Sport).order_by(Sport.name)
        if active_only:
            query = query.where(Sport.is_active.is_(True))
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, sport_id: UUID) -> Optional[Sport]:
        """Get a sport by ID."""
        result = await self._db.execute(
            select(Sport).where(Sport.id == sport_id)
        )
        return result.scalar_one_or_none()

    async def create(self, name: str, icon: str, color: str) -> Sport:
        """Create a new sport type."""
        sport = Sport(name=name, icon=icon, color=color)
        self._db.add(sport)
        await self._db.flush()
        return sport

    async def update(self, sport_id: UUID, **kwargs) -> Optional[Sport]:
        """Update a sport type."""
        sport = await self.get_by_id(sport_id)
        if not sport:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(sport, key, value)
        await self._db.flush()
        return sport

    async def delete(self, sport_id: UUID) -> bool:
        """Delete a sport type."""
        sport = await self.get_by_id(sport_id)
        if not sport:
            return False
        await self._db.delete(sport)
        await self._db.flush()
        return True


class FieldsService:
    """Service layer for sports field operations with geospatial support."""

    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(
        self,
        *,
        name: str,
        description: Optional[str],
        latitude: float,
        longitude: float,
        address: str,
        city: str,
        phone: Optional[str],
        email: Optional[str],
        website: Optional[str],
        booking_url: Optional[str],
        price_info: Optional[str],
        opening_hours: Optional[dict],
        photos: Optional[list[str]],
        sport_ids: list[UUID],
        created_by: Optional[UUID] = None,
    ) -> Field:
        """Create a new sports field with associated sports."""
        # Create field with PostGIS point
        point_wkt = f"POINT({longitude} {latitude})"
        field = Field(
            name=name,
            description=description,
            location=point_wkt,
            address=address,
            city=city,
            phone=phone,
            email=email,
            website=website,
            booking_url=booking_url,
            price_info=price_info,
            opening_hours=opening_hours or {},
            photos=photos or [],
            created_by=created_by,
        )
        self._db.add(field)
        await self._db.flush()

        # Add sport associations
        for sport_id in sport_ids:
            field_sport = FieldSport(field_id=field.id, sport_id=sport_id)
            self._db.add(field_sport)

        await self._db.flush()
        return await self.get_by_id(field.id)

    async def get_by_id(self, field_id: UUID) -> Optional[Field]:
        """Get a field by ID with all relationships loaded."""
        result = await self._db.execute(
            select(Field)
            .where(Field.id == field_id)
            .options(
                selectinload(Field.field_sports).selectinload(FieldSport.sport),
                selectinload(Field.reviews),
            )
        )
        return result.scalar_one_or_none()

    async def search_nearby(
        self,
        *,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0,
        sport_ids: Optional[list[UUID]] = None,
        min_rating: Optional[float] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict], int]:
        """
        Search for fields near a given location.

        Uses PostGIS ST_DWithin for efficient spatial queries.
        Returns fields within radius_km kilometers.
        """
        # Create reference point
        ref_point = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)

        # Base query — active fields within radius
        # ST_DWithin uses meters for geography type, so convert km → m
        radius_meters = radius_km * 1000

        query = (
            select(
                Field,
                ST_Distance(
                    func.Geography(Field.location),
                    func.Geography(ref_point),
                ).label("distance"),
            )
            .where(Field.is_active.is_(True))
            .where(
                ST_DWithin(
                    func.Geography(Field.location),
                    func.Geography(ref_point),
                    radius_meters,
                )
            )
            .options(
                selectinload(Field.field_sports).selectinload(FieldSport.sport),
                selectinload(Field.reviews),
            )
        )

        # Filter by sports
        if sport_ids:
            query = query.join(Field.field_sports).where(
                FieldSport.sport_id.in_(sport_ids)
            ).distinct()

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self._db.execute(count_query)
        total = total_result.scalar() or 0

        # Order by distance and paginate
        query = (
            query
            .order_by("distance")
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await self._db.execute(query)
        rows = result.all()

        # Build response with computed fields
        fields_data = []
        for field, distance in rows:
            field_dict = self._field_to_dict(field)
            field_dict["distance_km"] = round(distance / 1000, 2) if distance else None

            # Apply min_rating filter
            if min_rating and (field_dict["avg_rating"] or 0) < min_rating:
                total -= 1
                continue

            fields_data.append(field_dict)

        return fields_data, total

    async def update(self, field_id: UUID, **kwargs) -> Optional[Field]:
        """Update a sports field."""
        field = await self.get_by_id(field_id)
        if not field:
            return None

        sport_ids = kwargs.pop("sport_ids", None)

        # Update location if coordinates changed
        lat = kwargs.pop("latitude", None)
        lng = kwargs.pop("longitude", None)
        if lat is not None and lng is not None:
            kwargs["location"] = f"POINT({lng} {lat})"

        for key, value in kwargs.items():
            if value is not None:
                setattr(field, key, value)

        # Update sport associations
        if sport_ids is not None:
            await self._db.execute(
                delete(FieldSport).where(FieldSport.field_id == field_id)
            )
            for sport_id in sport_ids:
                self._db.add(FieldSport(field_id=field_id, sport_id=sport_id))

        await self._db.flush()
        return await self.get_by_id(field_id)

    async def delete(self, field_id: UUID) -> bool:
        """Delete a sports field."""
        field = await self.get_by_id(field_id)
        if not field:
            return False
        await self._db.delete(field)
        await self._db.flush()
        return True

    def _field_to_dict(self, field: Field) -> dict:
        """Convert a Field model to a response dictionary."""
        # Extract coordinates from PostGIS geometry
        point = to_shape(field.location)

        # Calculate average rating
        ratings = [r.rating for r in field.reviews] if field.reviews else []
        avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else None

        return {
            "id": field.id,
            "name": field.name,
            "description": field.description,
            "latitude": point.y,
            "longitude": point.x,
            "address": field.address,
            "city": field.city,
            "phone": field.phone,
            "email": field.email,
            "website": field.website,
            "booking_url": field.booking_url,
            "price_info": field.price_info,
            "opening_hours": field.opening_hours,
            "photos": field.photos,
            "is_active": field.is_active,
            "sports": [
                {
                    "id": fs.sport.id,
                    "name": fs.sport.name,
                    "icon": fs.sport.icon,
                    "color": fs.sport.color,
                    "is_active": fs.sport.is_active,
                }
                for fs in field.field_sports
            ],
            "avg_rating": avg_rating,
            "review_count": len(ratings),
            "created_at": field.created_at,
        }


class ReviewsService:
    """Service layer for review operations."""

    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(
        self, *, field_id: UUID, user_id: UUID, rating: int, comment: Optional[str]
    ) -> Review:
        """Create a new review."""
        review = Review(
            field_id=field_id,
            user_id=user_id,
            rating=rating,
            comment=comment,
        )
        self._db.add(review)
        await self._db.flush()
        return review

    async def get_by_field(self, field_id: UUID) -> list[Review]:
        """Get all reviews for a field."""
        result = await self._db.execute(
            select(Review)
            .where(Review.field_id == field_id)
            .order_by(Review.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, review_id: UUID, user_id: UUID) -> bool:
        """Delete a review (only by the author)."""
        result = await self._db.execute(
            select(Review).where(
                Review.id == review_id,
                Review.user_id == user_id,
            )
        )
        review = result.scalar_one_or_none()
        if not review:
            return False
        await self._db.delete(review)
        await self._db.flush()
        return True
