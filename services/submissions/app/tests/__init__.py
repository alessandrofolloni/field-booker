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


# ──────────────────────────────────────
# Additional Submissions Service Tests
# ──────────────────────────────────────

class TestSubmissionsServiceExtended:
    """Additional coverage for SubmissionsService."""

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
    async def test_get_pending_returns_submissions(self, service, mock_db):
        """get_pending should return tuple of (list, total) with pending submissions."""
        pending_sub = MagicMock(spec=Submission)
        pending_sub.status = SubmissionStatus.PENDING

        # First call = count query, second = fetch query
        count_result = MagicMock()
        count_result.scalar.return_value = 1
        fetch_result = MagicMock()
        fetch_result.scalars.return_value.all.return_value = [pending_sub]

        mock_db.execute = AsyncMock(side_effect=[count_result, fetch_result])

        results, total = await service.get_pending()
        assert len(results) == 1
        assert total == 1

    @pytest.mark.asyncio
    async def test_get_pending_empty(self, service, mock_db):
        """get_pending should return ([], 0) when nothing is pending."""
        count_result = MagicMock()
        count_result.scalar.return_value = 0
        fetch_result = MagicMock()
        fetch_result.scalars.return_value.all.return_value = []

        mock_db.execute = AsyncMock(side_effect=[count_result, fetch_result])

        results, total = await service.get_pending()
        assert results == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_create_update_submission(self, service, mock_db):
        """Should create an update-type submission with field_id."""
        field_data = {
            "name": "Updated Campo",
            "latitude": 41.9,
            "longitude": 12.5,
            "address": "Via Roma 2",
            "city": "Roma",
            "sport_ids": [str(uuid4())],
        }

        await service.create(
            user_id=uuid4(),
            user_email="user@test.com",
            user_name="Test User",
            field_data=field_data,
            field_id=uuid4(),
            submission_type="update",
        )
        mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_review_already_approved_raises(self, service, mock_db):
        """Should raise ValueError for already-approved submission."""
        approved_sub = MagicMock(spec=Submission)
        approved_sub.status = SubmissionStatus.APPROVED

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = approved_sub
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="already been reviewed"):
            await service.review(
                submission_id=uuid4(),
                status="approved",
                admin_notes=None,
                reviewer_id=uuid4(),
                reviewer_token="fake-token",
            )


# ──────────────────────────────────────
# Additional Schema Edge Case Tests
# ──────────────────────────────────────

class TestSubmissionSchemasExtended:
    """Additional schema validation edge cases."""

    def test_submission_field_data_negative_latitude(self):
        """Should accept valid negative latitude (southern hemisphere)."""
        data = SubmissionFieldData(
            name="Campo Sud",
            latitude=-33.8688,
            longitude=151.2093,
            address="Test St",
            city="Sydney",
            sport_ids=[uuid4()],
        )
        assert data.latitude == -33.8688

    def test_submission_field_data_invalid_large_latitude(self):
        """Should reject latitude > 90."""
        with pytest.raises(Exception):
            SubmissionFieldData(
                name="Test",
                latitude=95.0,
                longitude=12.0,
                address="Test",
                city="Test",
                sport_ids=[uuid4()],
            )
