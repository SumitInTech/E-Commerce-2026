"""
AI Chatbot HTTP Controller.
Coordinates natural language support queries, live order tracking, and chat sessions.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.chatbot.services.chatbot_service import chatbot_service
from backend.chatbot.schemas.chatbot_schema import (
    ChatQueryRequest,
    ChatbotAnswerResponse,
    ChatHistoryResponse,
    ChatMessageDTO
)


class ChatbotController:
    @staticmethod
    async def query(db: Session, req: ChatQueryRequest) -> ChatbotAnswerResponse:
        try:
            data = await chatbot_service.answer_query(db, req)
            return ChatbotAnswerResponse(**data)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Chatbot error: {str(e)}")

    @staticmethod
    def get_history(db: Session, session_id: str) -> ChatHistoryResponse:
        messages = chatbot_service.get_history(db, session_id)
        dtos = [ChatMessageDTO.model_validate(m) for m in messages]
        return ChatHistoryResponse(session_id=session_id, messages=dtos)


chatbot_controller = ChatbotController()
