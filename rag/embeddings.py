"""
OpportunityIQ — RAG Embeddings Manager

Provides vector embedding generation for resume chunks and opportunity descriptions.
Uses sentence-transformers (all-MiniLM-L6-v2) with TF-IDF fallback.
"""

from typing import List
import numpy as np
import logging

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """Manages document and query embedding generation."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self._fallback_vectorizer = None

    def _load_model(self):
        if self._model is not None or self._fallback_vectorizer is not None:
            return

        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading SentenceTransformer model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
        except Exception as e:
            logger.warning(f"Failed to load SentenceTransformer ({e}). Falling back to TF-IDF.")
            from sklearn.feature_extraction.text import TfidfVectorizer
            self._fallback_vectorizer = TfidfVectorizer(stop_words='english')

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Embed a list of text strings into numpy float32 matrix."""
        if not texts:
            return np.array([], dtype=np.float32)

        self._load_model()

        if self._model is not None:
            try:
                embeddings = self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
                return embeddings.astype(np.float32)
            except Exception as e:
                logger.error(f"SentenceTransformer encoding error: {e}")

        # Fallback to TF-IDF
        from sklearn.feature_extraction.text import TfidfVectorizer
        if self._fallback_vectorizer is None:
            self._fallback_vectorizer = TfidfVectorizer(stop_words='english')
        
        try:
            tfidf_matrix = self._fallback_vectorizer.fit_transform(texts)
            return tfidf_matrix.toarray().astype(np.float32)
        except Exception as ex:
            logger.error(f"TF-IDF embedding failed: {ex}")
            return np.random.rand(len(texts), 384).astype(np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single query string into a 1D vector."""
        vecs = self.embed_texts([query])
        return vecs[0] if len(vecs) > 0 else np.zeros(384, dtype=np.float32)
