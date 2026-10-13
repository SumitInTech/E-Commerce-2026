"""
Model 4: RAG Orchestration Service.
Manages document ingestion, chunking, semantic retrieval, and prompt synthesis.
"""
import os
import glob
from typing import Dict, Any, List, Optional

from core.interfaces.vector_store import AbstractVectorStore, DocumentChunk
from core.interfaces.llm_provider import AbstractLLMProvider
from services.vector_db import InMemoryTFIDFVectorStore
from services.gemini_llm import GeminiLLMProvider
from core.config import settings


class RAGService:
    """
    Retrieval-Augmented Generation service for apparel styling,
    sizing guidelines, and customer support.
    """

    def __init__(
        self,
        vector_store: Optional[AbstractVectorStore] = None,
        llm_provider: Optional[AbstractLLMProvider] = None,
        docs_dir: Optional[str] = None
    ):
        self.vector_store = vector_store or InMemoryTFIDFVectorStore()
        self.llm_provider = llm_provider or GeminiLLMProvider()
        self.docs_dir = docs_dir or settings.KNOWLEDGE_DOCS_DIR
        self._ingest_documents()

    def _ingest_documents(self) -> None:
        """Reads markdown files from docs_dir and indexes them."""
        if not os.path.exists(self.docs_dir):
            return

        chunks: List[DocumentChunk] = []
        md_files = glob.glob(os.path.join(self.docs_dir, "*.md"))

        for file_path in md_files:
            filename = os.path.basename(file_path)
            topic = filename.replace(".md", "").replace("_", " ").title()

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Split by markdown headers
            sections = content.split("## ")
            for idx, section in enumerate(sections):
                text = section.strip()
                if not text:
                    continue

                if idx > 0:
                    text = f"## {text}"

                chunk_id = f"{filename}_{idx}"
                chunks.append(
                    DocumentChunk(
                        id=chunk_id,
                        text=text,
                        metadata={"source": filename, "topic": topic}
                    )
                )

        if chunks:
            self.vector_store.upsert(chunks)

    async def answer_query(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Retrieves relevant context and generates a grounded response.
        """
        retrieved_chunks = self.vector_store.query(query, top_k=top_k)

        context_texts = [
            f"Source [{c.metadata.get('topic', 'General')}]:\n{c.text}"
            for c in retrieved_chunks
        ]
        context_block = "\n\n".join(context_texts) if context_texts else "No specific store documents found."

        system_instruction = (
            "You are an expert AI fashion stylist and e-commerce sizing support specialist. "
            "Answer the customer's question using ONLY the provided context. "
            "Be polite, concise, and helpful. If the information is not contained in the context, "
            "politely mention that and suggest contacting customer care."
        )

        prompt = (
            f"CONTEXT:\n{context_block}\n\n"
            f"USER QUERY: {query}\n\n"
            f"ANSWER:"
        )

        response_text = await self.llm_provider.generate_response(
            prompt=prompt,
            system_instruction=system_instruction
        )

        return {
            "query": query,
            "response": response_text,
            "citations": [
                {
                    "id": c.id,
                    "topic": c.metadata.get("topic"),
                    "source": c.metadata.get("source"),
                    "relevance_score": c.score
                }
                for c in retrieved_chunks
            ]
        }
