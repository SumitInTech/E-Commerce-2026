"""
AI Chatbot Service Schemas.
"""
from typing import List, Optional
from pydantic import BaseModel


class CitationItem(BaseModel):
    id: str
    topic: Optional[str] = None
    source: Optional[str] = None
    relevance_score: Optional[float] = None


class ChatbotQueryRequest(BaseModel):
    query: str
    top_k: int = 3
    order_number: Optional[str] = None  # If querying about specific order


class ChatbotQueryResponse(BaseModel):
    status: str = "success"
    query: str
    response: str
    order_context: Optional[dict] = None
    citations: List[CitationItem] = []
