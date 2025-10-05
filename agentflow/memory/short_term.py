"""Short-term memory (conversation history)."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from agentflow.memory.base import Memory, MemoryEntry


class ShortTermMemory(Memory):
    """Short-term memory for recent conversation history.

    Stores recent messages with optional size limit and time window.
    """

    def __init__(
        self,
        max_entries: Optional[int] = None,
        max_age_seconds: Optional[int] = None,
    ) -> None:
        """Initialize short-term memory.

        Args:
            max_entries: Maximum number of entries to keep (None for unlimited)
            max_age_seconds: Maximum age of entries in seconds (None for unlimited)
        """
        self.max_entries = max_entries
        self.max_age_seconds = max_age_seconds
        self.entries: List[MemoryEntry] = []

    def add(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a memory entry."""
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            content=content,
            metadata=metadata or {},
            timestamp=datetime.now(),
        )

        self.entries.append(entry)

        # Enforce max entries limit
        if self.max_entries and len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries :]

        # Clean old entries if age limit is set
        if self.max_age_seconds:
            self._clean_old_entries()

        return entry.id

    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        """Get a memory entry by ID."""
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None

    def search(
        self, query: str, limit: int = 5, min_score: float = 0.0
    ) -> List[MemoryEntry]:
        """Search for relevant memories using simple keyword matching."""
        query_lower = query.lower()
        results = []

        for entry in reversed(self.entries):  # Most recent first
            # Simple keyword-based relevance scoring
            content_lower = entry.content.lower()
            score = 0.0

            # Check if query terms are in content
            query_terms = query_lower.split()
            for term in query_terms:
                if term in content_lower:
                    score += 1.0 / len(query_terms)

            if score >= min_score:
                results.append((score, entry))

        # Sort by score (descending) and return top entries
        results.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in results[:limit]]

    def get_recent(self, limit: int = 10) -> List[MemoryEntry]:
        """Get the most recent entries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of recent memory entries
        """
        return list(reversed(self.entries[-limit:]))

    def clear(self) -> None:
        """Clear all memories."""
        self.entries.clear()

    def size(self) -> int:
        """Get the number of memory entries."""
        return len(self.entries)

    def _clean_old_entries(self) -> None:
        """Remove entries older than max_age_seconds."""
        if not self.max_age_seconds:
            return

        now = datetime.now()
        self.entries = [
            entry
            for entry in self.entries
            if (now - entry.timestamp).total_seconds() <= self.max_age_seconds
        ]
