"""
AI Chatbot Service Router.
Exposes Model 4: Real-time contextual support grounded in store policy,
care guides, return protocols, and live database order tracking.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.chatbot import ChatbotQueryRequest, ChatbotQueryResponse
from backend.services.ai_chatbot_service import AIChatbotService

router = APIRouter(prefix="/chatbot", tags=["7. AI Chatbot Service"])


@router.post("/query", response_model=ChatbotQueryResponse)
async def chat_query(req: ChatbotQueryRequest, db: Session = Depends(get_db)):
    """
    Model 4: Contextual RAG Customer Support & Advisory Chatbot.
    Answers inquiries using verified store policies, garment specifications,
    and live order fulfillment databases.
    """
    return await AIChatbotService.answer_query(db, req)
