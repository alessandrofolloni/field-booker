"""
AI Assistant API Routes.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Optional
from app.services.agent_service import AIAgentService
from shared.config import get_settings
from shared.security import get_optional_user

logger = logging.getLogger(__name__)

router = APIRouter()
settings = get_settings()

# Singleton service instance
_service: Optional[AIAgentService] = None


def get_ai_service():
    global _service
    if _service is None:
        _service = AIAgentService()
    return _service


@router.post("/chat")
async def chat_with_agent(
    message: str = Body(..., embed=True),
    history: Optional[List[dict]] = Body(None),
    current_user: Optional[dict] = Depends(get_optional_user),
    service: AIAgentService = Depends(get_ai_service),
):
    """
    Send a message to the Gemini AI Assistant.
    Auth is optional — anonymous users get an anonymous session.
    """
    if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY in ("", "your_gemini_api_key_here"):
        raise HTTPException(
            status_code=503,
            detail="Il servizio AI non è disponibile: GOOGLE_API_KEY non configurata.",
        )

    # Use email-based session for authenticated users, anonymous otherwise
    email = current_user.get("email", "anonymous") if current_user else "anonymous"
    session_id = f"session_{email}"

    result = await service.chat(message, history, session_id=session_id)
    return result
