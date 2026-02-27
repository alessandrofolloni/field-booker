"""
Reviews API routes.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_db
from shared.security import get_current_user
from app.schemas import ReviewCreate, ReviewResponse
from app.services import ReviewsService

router = APIRouter()


@router.get("/field/{field_id}", response_model=list[ReviewResponse])
async def get_field_reviews(
    field_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get all reviews for a specific field."""
    service = ReviewsService(db)
    reviews = await service.get_by_field(field_id)
    return [ReviewResponse.model_validate(r) for r in reviews]


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    request: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new review (authenticated users only)."""
    service = ReviewsService(db)

    try:
        review = await service.create(
            field_id=request.field_id,
            user_id=UUID(current_user["sub"]),
            rating=request.rating,
            comment=request.comment,
        )
    except Exception as e:
        if "uq_field_user_review" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already reviewed this field",
            )
        raise

    return ReviewResponse.model_validate(review)


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a review (only by the author)."""
    service = ReviewsService(db)
    deleted = await service.delete(review_id, UUID(current_user["sub"]))

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found or not authorized",
        )
