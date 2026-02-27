"""
Submissions API routes.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_db
from shared.security import get_current_user, require_admin
from app.schemas import (
    SubmissionCreate, SubmissionReview, SubmissionResponse, SubmissionListResponse,
)
from app.services import SubmissionsService

router = APIRouter()
security = HTTPBearer()


@router.post("/", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_submission(
    request: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Submit a new field or a fix for admin review."""
    service = SubmissionsService(db)

    submission = await service.create(
        user_id=UUID(current_user["sub"]),
        user_email=current_user["email"],
        user_name=current_user["name"],
        field_data=request.field_data.model_dump(),
        field_id=request.field_id,
        submission_type=request.submission_type,
    )

    return SubmissionResponse.model_validate(submission)


@router.get("/my", response_model=SubmissionListResponse)
async def get_my_submissions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get the current user's submissions."""
    service = SubmissionsService(db)
    submissions, total = await service.get_user_submissions(
        user_id=UUID(current_user["sub"]),
        page=page,
        page_size=page_size,
    )

    return SubmissionListResponse(
        items=[SubmissionResponse.model_validate(s) for s in submissions],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/pending", response_model=SubmissionListResponse)
async def get_pending_submissions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    """Get all pending submissions (admin only)."""
    service = SubmissionsService(db)
    submissions, total = await service.get_pending(page=page, page_size=page_size)

    return SubmissionListResponse(
        items=[SubmissionResponse.model_validate(s) for s in submissions],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/all", response_model=SubmissionListResponse)
async def get_all_submissions(
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    """Get all submissions with optional status filter (admin only)."""
    service = SubmissionsService(db)
    submissions, total = await service.get_all(
        status=status_filter, page=page, page_size=page_size
    )

    return SubmissionListResponse(
        items=[SubmissionResponse.model_validate(s) for s in submissions],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific submission."""
    service = SubmissionsService(db)
    submission = await service.get_by_id(submission_id)

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )

    # Users can only see their own submissions, admins can see all
    if (
        str(submission.user_id) != current_user["sub"]
        and current_user.get("role") != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this submission",
        )

    return SubmissionResponse.model_validate(submission)


@router.post("/{submission_id}/review", response_model=SubmissionResponse)
async def review_submission(
    submission_id: UUID,
    request: SubmissionReview,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Review a submission — approve or reject (admin only).

    If approved, the field is automatically created in the Fields service.
    """
    service = SubmissionsService(db)

    try:
        submission = await service.review(
            submission_id=submission_id,
            status=request.status,
            admin_notes=request.admin_notes,
            reviewer_id=UUID(current_user["sub"]),
            reviewer_token=credentials.credentials,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to create field: {str(e)}",
        )

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )

    return SubmissionResponse.model_validate(submission)
