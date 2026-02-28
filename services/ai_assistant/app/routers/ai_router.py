"""
AI Assistant API Routes.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Optional
from app.services.agent_service import AIAgentService
from shared.config import get_settings
from shared.security import get_current_user

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
    current_user: dict = Depends(get_current_user),
    service: AIAgentService = Depends(get_ai_service)
):
    """
    Send a message to the Gemini AI Agent (powered by Google ADK).
    """
    if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "your_gemini_api_key_here":
        raise HTTPException(
            status_code=500,
            detail="Gemini API Key non configurata nel server."
        )
        
    try:
        # Use user email as session_id to maintain history in the runner
        session_id = f"session_{current_user.get('email', 'anonymous')}"
        result = await service.chat(message, history, session_id=session_id)
        return result
    except Exception as e:
        logger.exception("AI Chat Error")
        raise HTTPException(status_code=500, detail=str(e))
