"""
OpportunityIQ — Context Retriever

Retrieves relevant profile context and domain evidence for LLM prompt augmentation.
"""

from typing import List, Dict, Any, Optional
from rag.embeddings import EmbeddingManager
from rag.documents import DocumentProcessor, DocumentChunk
from rag.vectorstore import VectorStore
from profile.models import UserProfile

class ProfileRetriever:
    """Manages RAG index over a user profile and performs context retrieval."""

    def __init__(self, profile: UserProfile):
        self.profile = profile
        self.embedder = EmbeddingManager()
        self.processor = DocumentProcessor(chunk_size=200, overlap=30)
        self.vector_store = VectorStore(self.embedder)
        self._initialize_index()

    def _initialize_index(self):
        """Indexes the user's profile sections into the vector store."""
        summary_text = self.profile.to_text_summary()
        chunks = self.processor.chunk_text(summary_text, doc_id_prefix="profile")
        self.vector_store.add_documents(chunks)

    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """Retrieves top_k context chunks for a given opportunity or query."""
        results = self.vector_store.similarity_search(query, top_k=top_k)
        context_str = "\n---\n".join([c.text for c, score in results])
        return context_str
