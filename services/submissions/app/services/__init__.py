"""
Submissions service business logic.
Handles submission creation, listing, and admin approval/rejection
with inter-service communication to the Fields service.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

import httpx
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Submission, SubmissionStatus
from shared.config import get_settings

logger = logging.getLogger(__name__)


class SubmissionsService:
    """Service layer for submission operations."""

    def __init__(self, db: AsyncSession):
        self._db = db
        self._settings = get_settings()

    async def create(
        self,
        *,
        user_id: UUID,
        user_email: str,
        user_name: str,
        field_data: dict,
        field_id: Optional[UUID] = None,
        submission_type: str = "new",
    ) -> Submission:
        """
        Create a new field submission (new or update).
        """
        # Convert UUID objects to strings for JSON storage
        if "sport_ids" in field_data:
            field_data["sport_ids"] = [str(sid) for sid in field_data["sport_ids"]]

        submission = Submission(
            user_id=user_id,
            user_email=user_email,
            user_name=user_name,
            field_id=field_id,
            submission_type=submission_type,
            field_data=field_data,
        )
        self._db.add(submission)
        await self._db.flush()
        return submission

    async def get_by_id(self, submission_id: UUID) -> Optional[Submission]:
        """Get a submission by ID."""
        result = await self._db.execute(
            select(Submission).where(Submission.id == submission_id)
        )
        return result.scalar_one_or_none()

    async def get_user_submissions(
        self, user_id: UUID, page: int = 1, page_size: int = 20
    ) -> tuple[list[Submission], int]:
        """Get all submissions by a specific user."""
        # Count
        count_result = await self._db.execute(
            select(func.count()).where(Submission.user_id == user_id)
        )
        total = count_result.scalar() or 0

        # Fetch
        result = await self._db.execute(
            select(Submission)
            .where(Submission.user_id == user_id)
            .order_by(Submission.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        submissions = list(result.scalars().all())
        return submissions, total

    async def get_pending(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[Submission], int]:
        """Get all pending submissions (for admin review)."""
        count_result = await self._db.execute(
            select(func.count()).where(
                Submission.status == SubmissionStatus.PENDING
            )
        )
        total = count_result.scalar() or 0

        result = await self._db.execute(
            select(Submission)
            .where(Submission.status == SubmissionStatus.PENDING)
            .order_by(Submission.created_at.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        submissions = list(result.scalars().all())
        return submissions, total

    async def get_all(
        self,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Submission], int]:
        """Get all submissions with optional status filter."""
        query = select(Submission)
        count_query = select(func.count()).select_from(Submission)

        if status:
            query = query.where(Submission.status == status)
            count_query = count_query.where(Submission.status == status)

        count_result = await self._db.execute(count_query)
        total = count_result.scalar() or 0

        result = await self._db.execute(
            query
            .order_by(Submission.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        submissions = list(result.scalars().all())
        return submissions, total

    async def review(
        self,
        *,
        submission_id: UUID,
        status: str,
        admin_notes: Optional[str],
        reviewer_id: UUID,
        reviewer_token: str,
    ) -> Optional[Submission]:
        """
        Review a submission (approve or reject).

        If approved, creates or updates the field via the Fields service.
        """
        submission = await self.get_by_id(submission_id)
        if not submission:
            return None

        if submission.status != SubmissionStatus.PENDING:
            raise ValueError("Submission has already been reviewed")

        submission.status = SubmissionStatus(status)
        submission.admin_notes = admin_notes
        submission.reviewed_by = reviewer_id
        submission.reviewed_at = datetime.now(timezone.utc)

        # If approved, apply changes to Fields service
        if status == "approved":
            if submission.submission_type == "update" and submission.field_id:
                # Update existing field
                await self._update_field_from_submission(
                    submission.field_id, submission.field_data, reviewer_token
                )
            else:
                # Create new field
                await self._create_field_from_submission(
                    submission.field_data, reviewer_token
                )

        await self._db.flush()
        return submission

    async def _create_field_from_submission(
        self, field_data: dict, token: str
    ) -> None:
        """Create a new field in the Fields service."""
        fields_url = f"{self._settings.FIELDS_SERVICE_URL}/fields/"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    fields_url,
                    json=field_data,
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0,
                )
                if response.status_code not in (200, 201):
                    if response.status_code == 422:
                        # Validation error from Fields service
                        detail = response.json().get("detail", response.text)
                        logger.error("Field validation error from Fields service: %s", detail)
                        raise RuntimeError(f"Dati del campo non validi: {detail}")
                    elif response.status_code == 400:
                        logger.error("Bad request to Fields service: %s", response.text)
                        raise RuntimeError(f"Richiesta non valida al servizio campi: {response.text[:200]}")
                    else:
                        logger.error("Fields service error %s: %s", response.status_code, response.text[:200])
                        raise RuntimeError(f"Errore del servizio campi ({response.status_code}). Riprova più tardi.")
        except httpx.TimeoutException:
            logger.error("Timeout calling Fields service to create field")
            raise RuntimeError("Timeout durante la comunicazione con il servizio campi.")
        except httpx.RequestError as e:
            logger.error("Network error calling Fields service: %s", e)
            raise RuntimeError("Errore di rete durante la comunicazione con il servizio campi.")

    async def _update_field_from_submission(
        self, field_id: UUID, field_data: dict, token: str
    ) -> None:
        """Update an existing field in the Fields service."""
        fields_url = f"{self._settings.FIELDS_SERVICE_URL}/fields/{field_id}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    fields_url,
                    json=field_data,
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0,
                )
                if response.status_code not in (200, 201, 204):
                    if response.status_code == 404:
                        logger.error("Field %s not found in Fields service", field_id)
                        raise RuntimeError(f"Campo {field_id} non trovato nel servizio.")
                    elif response.status_code == 422:
                        detail = response.json().get("detail", response.text)
                        logger.error("Validation error updating field: %s", detail)
                        raise RuntimeError(f"Dati di aggiornamento non validi: {detail}")
                    else:
                        logger.error("Fields service error %s updating field: %s", response.status_code, response.text[:200])
                        raise RuntimeError(f"Errore del servizio campi ({response.status_code}). Riprova più tardi.")
        except httpx.TimeoutException:
            logger.error("Timeout calling Fields service to update field %s", field_id)
            raise RuntimeError("Timeout durante la comunicazione con il servizio campi.")
        except httpx.RequestError as e:
            logger.error("Network error calling Fields service: %s", e)
            raise RuntimeError("Errore di rete durante la comunicazione con il servizio campi.")
