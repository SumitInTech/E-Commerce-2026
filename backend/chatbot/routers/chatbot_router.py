"""
AI Chatbot API Router.
Registers HTTP endpoints for semantic store policy queries and conversational order tracking.
Includes legacy_router alias mounted under /chatbot for backward compatibility.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.supabase_client import get_db
from backend.chatbot.schemas.chatbot_schema import (
    ChatQueryRequest,
    ChatbotAnswerResponse,
    ChatHistoryResponse
)
from backend.chatbot.controllers.chatbot_controller import chatbot_controller

# Autonomous Microservice Router
router = APIRouter(prefix="/ai/chat", tags=["AI Chatbot Service"])


@router.post("/query", response_model=ChatbotAnswerResponse)
async def query_chatbot(req: ChatQueryRequest, db: Session = Depends(get_db)):
    """Answers customer queries grounded in store policies & live order status."""
    return await chatbot_controller.query(db, req)


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """Retrieves conversation thread for an active session."""
    return chatbot_controller.get_history(db, session_id)


# Legacy Compatibility Router (/api/v1/chatbot/*)
legacy_router = APIRouter(prefix="/chatbot", tags=["AI Chatbot (Legacy Alias)"])


@legacy_router.post("/query", response_model=ChatbotAnswerResponse)
async def legacy_query_chatbot(req: ChatQueryRequest, db: Session = Depends(get_db)):
    """Legacy endpoint for RAG query and live order tracking."""
    return await chatbot_controller.query(db, req)
