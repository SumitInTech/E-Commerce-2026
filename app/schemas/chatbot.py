"""
Pydantic schemas for RAG Conversational Chatbot (Model 4).
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=2, json_schema_extra={"example": "What is your return policy for wrong sizes?"})
    session_id: Optional[str] = Field(None, json_schema_extra={"example": "user_sess_123"})


class ChatResponse(BaseModel):
    status: str = "success"
    query: str
    response: str
    citations: List[Dict[str, Any]]
