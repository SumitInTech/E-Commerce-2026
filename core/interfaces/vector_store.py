"""
Abstract Base Class for Vector Stores.
Enables transparent decoupling between ChromaDB, pgvector, FAISS, and In-Memory TF-IDF vectors.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class DocumentChunk(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any] = {}
    score: Optional[float] = None


class AbstractVectorStore(ABC):
    @abstractmethod
    def upsert(self, chunks: List[DocumentChunk]) -> None:
        """Indexes or updates document chunks in the vector store."""
        pass

    @abstractmethod
    def query(self, query_text: str, top_k: int = 3) -> List[DocumentChunk]:
        """Retrieves top_k relevant document chunks ranked by semantic similarity."""
        pass
