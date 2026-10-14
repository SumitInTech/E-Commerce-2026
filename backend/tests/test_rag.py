"""
Unit tests for Model 4: Decoupled RAG Knowledge Engine.
"""
import pytest
from ai_models.chatbot.rag_service import RAGService


@pytest.mark.anyio
async def test_rag_document_retrieval():
    """Querying return policies should retrieve return_policy.md chunk with high score."""
    rag = RAGService()
    res = await rag.answer_query("Can I return an item if the size does not fit?")

    assert res["query"] is not None
    assert len(res["citations"]) > 0
    top_citation = res["citations"][0]
    assert "return_policy.md" in top_citation["source"] or "sizing_guidelines.md" in top_citation["source"]
    assert len(res["response"]) > 20
