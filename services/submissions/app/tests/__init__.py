"""
Unit tests for the Submissions service.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone

from app.models import Submission, SubmissionStatus
from app.services import SubmissionsService
from app.schemas import SubmissionCreate, SubmissionFieldData, SubmissionReview


# ──────────────────────────────────────
# Submission Model Tests
# ──────────────────────────────────────

class TestSubmissionModel:
    """Tests for the Submission model."""

    def test_submission_status_enum(self):
        """SubmissionStatus enum should have correct values."""
        assert SubmissionStatus.PENDING.value == "pending"
        assert SubmissionStatus.APPROVED.value == "approved"
        assert SubmissionStatus.REJECTED.value == "rejected"

    def test_submission_repr(self):
        """Submission __repr__ should be descriptive."""
        sub = Submission.__new__(Submission)
        sub.id = uuid4()
        sub.status = SubmissionStatus.PENDING
        assert "pending" in repr(sub)


# ──────────────────────────────────────
# Submissions Service Tests
# ──────────────────────────────────────

class TestSubmissionsService:
    """Tests for the SubmissionsService."""

    @pytest.fixture
    def mock_db(self):
        db = AsyncMock()
        db.flush = AsyncMock()
        db.add = MagicMock()
        return db

    @pytest.fixture
    def service(self, mock_db):
        return SubmissionsService(mock_db)

    @pytest.mark.asyncio
    async def test_create_submission(self, service, mock_db):
        """Should create a new submission."""
        field_data = {
            "name": "Campo Test",
            "latitude": 41.9028,
            "longitude": 12.4964,
            "address": "Via Test 1",
            "city": "Roma",
            "sport_ids": [str(uuid4())],
        }

        submission = await service.create(
            user_id=uuid4(),
            user_email="test@example.com",
            user_name="Test User",
            field_data=field_data,
        )

        mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, service, mock_db):
        """Should return None for non-existent submission."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await service.get_by_id(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_review_already_reviewed(self, service, mock_db):
        """Should raise ValueError if submission already reviewed."""
        reviewed_sub = MagicMock(spec=Submission)
        reviewed_sub.status = SubmissionStatus.APPROVED

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = reviewed_sub
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="already been reviewed"):
            await service.review(
                submission_id=uuid4(),
                status="rejected",
                admin_notes="Too late",
                reviewer_id=uuid4(),
                reviewer_token="fake-token",
            )

    @pytest.mark.asyncio
    async def test_review_not_found(self, service, mock_db):
        """Should return None for non-existent submission review."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await service.review(
            submission_id=uuid4(),
            status="approved",
            admin_notes=None,
            reviewer_id=uuid4(),
            reviewer_token="fake-token",
        )
        assert result is None


# ──────────────────────────────────────
# Schema Validation Tests
# ──────────────────────────────────────

class TestSubmissionSchemas:
    """Tests for submission Pydantic schemas."""

    def test_submission_field_data_valid(self):
        """Should validate valid field data."""
        data = SubmissionFieldData(
            name="Campo Test",
            latitude=41.9028,
            longitude=12.4964,
            address="Via Test 1",
            city="Roma",
            sport_ids=[uuid4()],
        )
        assert data.name == "Campo Test"

    def test_submission_field_data_empty_name(self):
        """Should reject empty field name."""
        with pytest.raises(Exception):
            SubmissionFieldData(
                name="",
                latitude=41.9,
                longitude=12.5,
                address="Via Test",
                city="Roma",
                sport_ids=[uuid4()],
            )

    def test_submission_field_data_no_sports(self):
        """Should reject submission with no sports."""
        with pytest.raises(Exception):
            SubmissionFieldData(
                name="Test",
                latitude=41.9,
                longitude=12.5,
                address="Via Test",
                city="Roma",
                sport_ids=[],
            )

    def test_submission_review_valid_status(self):
        """Should accept 'approved' and 'rejected' statuses."""
        review_approve = SubmissionReview(status="approved")
        assert review_approve.status == "approved"

        review_reject = SubmissionReview(status="rejected", admin_notes="Not valid")
        assert review_reject.status == "rejected"

    def test_submission_review_invalid_status(self):
        """Should reject invalid review status."""
        with pytest.raises(Exception):
            SubmissionReview(status="pending")

        with pytest.raises(Exception):
            SubmissionReview(status="invalid")
