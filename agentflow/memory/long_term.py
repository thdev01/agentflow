"""Long-term memory with vector similarity search."""

import json
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple

from agentflow.memory.base import Memory, MemoryEntry


class LongTermMemory(Memory):
    """Long-term memory using vector embeddings for semantic search.

    Supports custom embedding functions for semantic similarity search.
    """

    def __init__(
        self,
        embedding_function: Optional[Callable[[str], List[float]]] = None,
        embedding_dim: int = 384,
    ) -> None:
        """Initialize long-term memory.

        Args:
            embedding_function: Function to generate embeddings from text
            embedding_dim: Dimension of embeddings
        """
        self.embedding_function = embedding_function
        self.embedding_dim = embedding_dim
        self.entries: Dict[str, MemoryEntry] = {}
        self.embeddings: Dict[str, List[float]] = {}

    def add(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a memory entry with optional embedding."""
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            content=content,
            metadata=metadata or {},
        )

        self.entries[entry.id] = entry

        # Generate embedding if function is provided
        if self.embedding_function:
            self.embeddings[entry.id] = self.embedding_function(content)

        return entry.id

    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        """Get a memory entry by ID."""
        return self.entries.get(entry_id)

    def search(
        self, query: str, limit: int = 5, min_score: float = 0.0
    ) -> List[MemoryEntry]:
        """Search for relevant memories using vector similarity or keyword search."""
        if self.embedding_function and self.embeddings:
            return self._vector_search(query, limit, min_score)
        else:
            return self._keyword_search(query, limit, min_score)

    def _vector_search(
        self, query: str, limit: int, min_score: float
    ) -> List[MemoryEntry]:
        """Search using vector similarity (cosine similarity)."""
        query_embedding = self.embedding_function(query)  # type: ignore
        results: List[Tuple[float, MemoryEntry]] = []

        for entry_id, entry_embedding in self.embeddings.items():
            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_embedding, entry_embedding)

            if similarity >= min_score:
                results.append((similarity, self.entries[entry_id]))

        # Sort by similarity (descending)
        results.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in results[:limit]]

    def _keyword_search(
        self, query: str, limit: int, min_score: float
    ) -> List[MemoryEntry]:
        """Fallback to keyword-based search."""
        query_lower = query.lower()
        results: List[Tuple[float, MemoryEntry]] = []

        for entry in self.entries.values():
            content_lower = entry.content.lower()
            score = 0.0

            # Simple keyword matching
            query_terms = query_lower.split()
            for term in query_terms:
                if term in content_lower:
                    score += 1.0 / len(query_terms)

            if score >= min_score:
                results.append((score, entry))

        results.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in results[:limit]]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def clear(self) -> None:
        """Clear all memories."""
        self.entries.clear()
        self.embeddings.clear()

    def size(self) -> int:
        """Get the number of memory entries."""
        return len(self.entries)

    def get_all(self) -> List[MemoryEntry]:
        """Get all memory entries.

        Returns:
            List of all memory entries
        """
        return list(self.entries.values())
