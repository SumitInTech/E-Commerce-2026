"""
Router for Model 4: Conversational Stylist & Store Advisory RAG Chatbot.
"""
from fastapi import APIRouter, Depends
from app.schemas.chatbot import ChatRequest, ChatResponse
from app.dependencies import get_rag_service
from services.rag_service import RAGService

router = APIRouter(prefix="/api/v1", tags=["Model 4: RAG Chatbot"])


@router.post("/chat", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Answers customer inquiries on sizing, garment care, and store policies
    using grounded knowledge base context.
    """
    result = await rag_service.answer_query(request.query)

    return ChatResponse(
        status="success",
        query=result["query"],
        response=result["response"],
        citations=result["citations"]
    )
