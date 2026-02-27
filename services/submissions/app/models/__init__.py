"""
Submission model for the approval workflow.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Column, String, Text, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB

from shared.database import Base


class SubmissionStatus(str, PyEnum):
    """Submission status enumeration."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class SubmissionType(str, PyEnum):
    """Type of suggestion."""
    NEW = "new"
    UPDATE = "update"


class Submission(Base):
    """User submission for a sports field (new or fix)."""

    __tablename__ = "submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_email = Column(String(255), nullable=False)
    user_name = Column(String(255), nullable=False)

    # Optional field_id if it's a FIX for an existing field
    field_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    submission_type = Column(
        Enum(SubmissionType, name="submission_type", create_type=True),
        default=SubmissionType.NEW,
        nullable=False,
    )

    # All field data stored as JSON for flexibility
    field_data = Column(JSONB, nullable=False)

    # Workflow
    status = Column(
        Enum(SubmissionStatus, name="submission_status", create_type=True),
        default=SubmissionStatus.PENDING,
        nullable=False,
        index=True,
    )
    admin_notes = Column(Text, nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Submission {self.id} ({self.status.value})>"
