"""
Database models for the Fields service.
Includes Sport, Field, FieldSport (M2M), and Review.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, DateTime,
    ForeignKey, Float, CheckConstraint, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from shared.database import Base


class Sport(Base):
    """Sport type model (e.g., Calcio, Tennis, Padel)."""

    __tablename__ = "sports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    icon = Column(String(50), nullable=False, default="⚽")
    color = Column(String(7), nullable=False, default="#4CAF50")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    field_sports = relationship("FieldSport", back_populates="sport", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Sport {self.name}>"


class Field(Base):
    """Sports field model with geospatial location."""

    __tablename__ = "fields"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Geospatial — stored as PostGIS Point (longitude, latitude)
    location = Column(Geometry("POINT", srid=4326), nullable=False)
    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False, index=True)

    # Contact
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)
    booking_url = Column(String(500), nullable=True)

    # Info
    price_info = Column(Text, nullable=True)
    opening_hours = Column(JSONB, nullable=True, default=dict)
    photos = Column(JSONB, nullable=True, default=list)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Metadata
    created_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    field_sports = relationship("FieldSport", back_populates="field", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="field", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Field {self.name} ({self.city})>"


class FieldSport(Base):
    """Many-to-many relationship between Fields and Sports."""

    __tablename__ = "field_sports"
    __table_args__ = (
        UniqueConstraint("field_id", "sport_id", name="uq_field_sport"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fields.id", ondelete="CASCADE"),
        nullable=False,
    )
    sport_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sports.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    field = relationship("Field", back_populates="field_sports")
    sport = relationship("Sport", back_populates="field_sports")


class Review(Base):
    """User review for a sports field."""

    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("field_id", "user_id", name="uq_field_user_review"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_rating_range"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fields.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    field = relationship("Field", back_populates="reviews")

    def __repr__(self) -> str:
        return f"<Review field={self.field_id} rating={self.rating}>"


class AnalyticsEvent(Base):
    """Tracks user interaction events for analytics (field views, booking clicks, etc.)."""

    __tablename__ = "analytics_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(50), nullable=False, index=True)
    field_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fields.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    user_id = Column(UUID(as_uuid=True), nullable=True)
    session_id = Column(String(128), nullable=True)
    # Note: 'metadata' is reserved by SQLAlchemy's DeclarativeBase — use 'event_metadata'
    # The DB column is still named 'metadata' via the `name` kwarg for backwards compatibility
    event_metadata = Column("metadata", JSONB, nullable=True, default=dict)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<AnalyticsEvent {self.event_type} field={self.field_id}>"
