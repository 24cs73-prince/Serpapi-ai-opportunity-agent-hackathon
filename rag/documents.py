"""
OpportunityIQ — Document Chunking & Processing

Chunks user resume text and opportunity records into structured document snippets
suitable for vector indexing and semantic retrieval.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class DocumentChunk:
    doc_id: str
    text: str
    metadata: Dict[str, Any]

class DocumentProcessor:
    """Processes raw text and structured data into indexable document chunks."""

    def __init__(self, chunk_size: int = 400, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, doc_id_prefix: str = "doc", metadata: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        """Splits long text into overlapping chunks."""
        if not text:
            return []

        meta = metadata or {}
        words = text.split()
        chunks = []

        if len(words) <= self.chunk_size:
            return [DocumentChunk(doc_id=f"{doc_id_prefix}_0", text=text, metadata=meta)]

        step = self.chunk_size - self.overlap
        chunk_idx = 0
        for i in range(0, len(words), step):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            chunks.append(DocumentChunk(
                doc_id=f"{doc_id_prefix}_{chunk_idx}",
                text=chunk_text,
                metadata={**meta, "chunk_index": chunk_idx}
            ))
            chunk_idx += 1

        return chunks
