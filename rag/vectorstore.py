"""
OpportunityIQ — Vector Store (FAISS / Cosine Similarity)

Provides in-memory vector indexing and similarity retrieval.
Uses FAISS if available, with numpy cosine similarity fallback.
"""

from typing import List, Tuple, Dict, Any
import numpy as np
import logging
from rag.documents import DocumentChunk
from rag.embeddings import EmbeddingManager

logger = logging.getLogger(__name__)

class VectorStore:
    """Vector store for semantic search over resume and opportunity chunks."""

    def __init__(self, embedding_manager: EmbeddingManager):
        self.embedder = embedding_manager
        self.chunks: List[DocumentChunk] = []
        self.embeddings: Optional[np.ndarray] = None
        self._faiss_index = None

    def add_documents(self, chunks: List[DocumentChunk]):
        """Embeds and indexes document chunks."""
        if not chunks:
            return

        texts = [c.text for c in chunks]
        vecs = self.embedder.embed_texts(texts)

        if self.embeddings is None:
            self.embeddings = vecs
        else:
            self.embeddings = np.vstack([self.embeddings, vecs])

        self.chunks.extend(chunks)
        self._build_index()

    def _build_index(self):
        """Builds FAISS index if available."""
        if self.embeddings is None or len(self.embeddings) == 0:
            return

        try:
            import faiss
            dim = self.embeddings.shape[1]
            index = faiss.IndexFlatIP(dim)  # Inner product (cosine sim after norm)
            
            # Normalize vectors for cosine similarity
            norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            norm_embeddings = self.embeddings / norms

            index.add(norm_embeddings)
            self._faiss_index = index
            logger.info(f"FAISS index built with {index.ntotal} vectors.")
        except Exception as e:
            logger.warning(f"FAISS index creation failed ({e}). Using Numpy cosine similarity fallback.")
            self._faiss_index = None

    def similarity_search(self, query: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """Searches for top_k relevant chunks for a given query."""
        if not self.chunks or self.embeddings is None:
            return []

        query_vec = self.embedder.embed_query(query)

        # Normalize query vector
        q_norm = np.linalg.norm(query_vec)
        if q_norm > 0:
            query_vec = query_vec / q_norm

        if self._faiss_index is not None:
            try:
                import faiss
                scores, indices = self._faiss_index.search(np.array([query_vec], dtype=np.float32), top_k)
                results = []
                for idx, score in zip(indices[0], scores[0]):
                    if 0 <= idx < len(self.chunks):
                        results.append((self.chunks[idx], float(score)))
                return results
            except Exception as e:
                logger.error(f"FAISS search failed: {e}")

        # Numpy fallback cosine search
        norms = np.linalg.norm(self.embeddings, axis=1)
        norms[norms == 0] = 1.0
        doc_norms = self.embeddings / norms[:, np.newaxis]
        
        sims = np.dot(doc_norms, query_vec)
        top_indices = np.argsort(sims)[::-1][:top_k]

        return [(self.chunks[i], float(sims[i])) for i in top_indices]
