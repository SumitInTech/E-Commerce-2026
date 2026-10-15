"""
Pydantic v2 Schemas for Conversational RAG Support & Live Tracking.
Supports both autonomous microservice models and legacy response structures.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ChatQueryRequest(BaseModel):
    query: str = Field(..., min_length=2)
    session_id: Optional[str] = None
    user_id: Optional[int] = None
    order_number: Optional[str] = None
    top_k: int = 3


# Backward-compatibility alias
ChatbotQueryRequest = ChatQueryRequest


class CitationItem(BaseModel):
    id: Any
    topic: Optional[str] = "Store Policy"
    source: Optional[str] = None
    relevance_score: Optional[float] = 0.95


class ChatbotAnswerResponse(BaseModel):
    session_id: str
    answer: str
    response: Optional[str] = None
    status: str = "success"
    query: Optional[str] = None
    sources: List[str] = []
    citations: List[CitationItem] = []
    order_context: Optional[Dict[str, Any]] = None
    timestamp: datetime

    def model_post_init(self, __context):
        if self.response is None:
            self.response = self.answer
        if not self.citations and self.sources:
            self.citations = [
                CitationItem(id=idx + 1, topic="Store Policy", source=s, relevance_score=0.95)
                for idx, s in enumerate(self.sources)
            ]


# Backward-compatibility alias
ChatbotQueryResponse = ChatbotAnswerResponse


class ChatMessageDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role: str
    content: str
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[ChatMessageDTO]
