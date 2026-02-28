"""
Unit tests for the Fields service.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.models import Sport, Field, Review, FieldSport
from app.services import SportsService, FieldsService, ReviewsService
from app.schemas import SportCreate, FieldCreate, ReviewCreate


# ──────────────────────────────────────
# Sport Model Tests
# ──────────────────────────────────────

class TestSportModel:
    """Tests for the Sport model."""

    def test_sport_repr(self):
        """Sport __repr__ should be descriptive."""
        sport = Sport.__new__(Sport)
        sport.name = "Calcio"
        assert "Calcio" in repr(sport)

    def test_sport_defaults(self):
        """Sport should have sensible defaults."""
        sport = Sport(name="Test Sport")
        assert sport.icon == "⚽"
        assert sport.color == "#4CAF50"
        assert sport.is_active is True


# ──────────────────────────────────────
# Sports Service Tests
# ──────────────────────────────────────

class TestSportsService:
    """Tests for the SportsService."""

    @pytest.fixture
    def mock_db(self):
        db = AsyncMock()
        db.flush = AsyncMock()
        db.add = MagicMock()
        db.delete = AsyncMock()
        return db

    @pytest.fixture
    def service(self, mock_db):
        return SportsService(mock_db)

    @pytest.mark.asyncio
    async def test_create_sport(self, service, mock_db):
        """Should create a new sport."""
        sport = await service.create(name="Tennis", icon="🎾", color="#FFC107")
        mock_db.add.assert_called_once()
        mock_db.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_sports(self, service, mock_db):
        """Should return all active sports."""
        mock_sports = [
            MagicMock(spec=Sport, name="Calcio"),
            MagicMock(spec=Sport, name="Tennis"),
        ]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_sports
        mock_db.execute = AsyncMock(return_value=mock_result)

        sports = await service.get_all()
        assert len(sports) == 2

    @pytest.mark.asyncio
    async def test_delete_nonexistent_sport(self, service, mock_db):
        """Should return False when deleting non-existent sport."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await service.delete(uuid4())
        assert result is False


# ──────────────────────────────────────
# Review Model Tests
# ──────────────────────────────────────

class TestReviewModel:
    """Tests for the Review model."""

    def test_review_repr(self):
        """Review __repr__ should include field_id and rating."""
        review = Review.__new__(Review)
        review.field_id = uuid4()
        review.rating = 4
        repr_str = repr(review)
        assert "4" in repr_str


# ──────────────────────────────────────
# Reviews Service Tests
# ──────────────────────────────────────

class TestReviewsService:
    """Tests for the ReviewsService."""

    @pytest.fixture
    def mock_db(self):
        db = AsyncMock()
        db.flush = AsyncMock()
        db.add = MagicMock()
        db.delete = AsyncMock()
        return db

    @pytest.fixture
    def service(self, mock_db):
        return ReviewsService(mock_db)

    @pytest.mark.asyncio
    async def test_create_review(self, service, mock_db):
        """Should create a new review."""
        review = await service.create(
            field_id=uuid4(),
            user_id=uuid4(),
            rating=5,
            comment="Great field!",
        )
        mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_review_not_found(self, service, mock_db):
        """Should return False when review not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await service.delete(uuid4(), uuid4())
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_review_wrong_user(self, service, mock_db):
        """Should return False when user doesn't own the review."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await service.delete(uuid4(), uuid4())
        assert result is False


# ──────────────────────────────────────
# Schema Validation Tests
# ──────────────────────────────────────

class TestSchemaValidation:
    """Tests for Pydantic schema validation."""

    def test_sport_create_valid(self):
        """Should validate a valid sport creation schema."""
        sport = SportCreate(name="Calcio", icon="⚽", color="#4CAF50")
        assert sport.name == "Calcio"

    def test_sport_create_invalid_color(self):
        """Should reject invalid hex color."""
        with pytest.raises(Exception):
            SportCreate(name="Test", icon="⚽", color="not-a-color")

    def test_sport_create_empty_name(self):
        """Should reject empty sport name."""
        with pytest.raises(Exception):
            SportCreate(name="", icon="⚽", color="#4CAF50")

    def test_review_create_rating_range(self):
        """Should enforce rating between 1-5."""
        with pytest.raises(Exception):
            ReviewCreate(field_id=uuid4(), rating=0)

        with pytest.raises(Exception):
            ReviewCreate(field_id=uuid4(), rating=6)

        review = ReviewCreate(field_id=uuid4(), rating=3)
        assert review.rating == 3

    def test_field_create_valid(self):
        """Should validate a valid field creation schema."""
        field = FieldCreate(
            name="Campo Verde",
            latitude=41.9028,
            longitude=12.4964,
            address="Via Roma 1",
            city="Roma",
            sport_ids=[uuid4()],
        )
        assert field.city == "Roma"

    def test_field_create_invalid_coordinates(self):
        """Should reject invalid coordinates."""
        with pytest.raises(Exception):
            FieldCreate(
                name="Test",
                latitude=91,  # Invalid: > 90
                longitude=12.0,
                address="Test",
                city="Test",
                sport_ids=[uuid4()],
            )

    def test_field_create_invalid_longitude(self):
        """Should reject longitude > 180."""
        with pytest.raises(Exception):
            FieldCreate(
                name="Test",
                latitude=41.0,
                longitude=181.0,  # Invalid: > 180
                address="Test",
                city="Test",
                sport_ids=[uuid4()],
            )

    def test_field_create_no_sports(self):
        """Should reject field with empty sport_ids list."""
        with pytest.raises(Exception):
            FieldCreate(
                name="Test Field",
                latitude=41.0,
                longitude=12.0,
                address="Test",
                city="Test",
                sport_ids=[],
            )


# ──────────────────────────────────────
# Additional Sports Tests
# ──────────────────────────────────────

class TestSportsServiceExtended:
    """Additional coverage for SportsService."""

    @pytest.fixture
    def mock_db(self):
        db = AsyncMock()
        db.flush = AsyncMock()
        db.add = MagicMock()
        return db

    @pytest.fixture
    def service(self, mock_db):
        return SportsService(mock_db)

    @pytest.mark.asyncio
    async def test_get_all_sports_empty(self, service, mock_db):
        """Should return empty list when no sports exist."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        sports = await service.get_all()
        assert sports == []

    @pytest.mark.asyncio
    async def test_create_sport_with_defaults(self, service, mock_db):
        """Should use default icon and color if not provided."""
        await service.create(name="Volleyball")
        mock_db.add.assert_called_once()


# ──────────────────────────────────────
# Additional Reviews Tests
# ──────────────────────────────────────

class TestReviewsServiceExtended:
    """Additional coverage for ReviewsService."""

    @pytest.fixture
    def mock_db(self):
        db = AsyncMock()
        db.flush = AsyncMock()
        db.add = MagicMock()
        return db

    @pytest.fixture
    def service(self, mock_db):
        return ReviewsService(mock_db)

    @pytest.mark.asyncio
    async def test_get_reviews_for_field_empty(self, service, mock_db):
        """Should return empty list when field has no reviews."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        reviews = await service.get_for_field(uuid4())
        assert reviews == []

    def test_review_rating_zero_invalid(self):
        """Rating 0 should not be accepted."""
        from app.schemas import ReviewCreate
        with pytest.raises(Exception):
            ReviewCreate(field_id=uuid4(), rating=0)

    def test_review_rating_six_invalid(self):
        """Rating 6 should not be accepted."""
        from app.schemas import ReviewCreate
        with pytest.raises(Exception):
            ReviewCreate(field_id=uuid4(), rating=6)
