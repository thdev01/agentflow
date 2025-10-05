"""Base classes for memory systems."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MemoryEntry(BaseModel):
    """A single memory entry."""

    id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)


class Memory(ABC):
    """Base class for memory systems."""

    @abstractmethod
    def add(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a memory entry.

        Args:
            content: Memory content
            metadata: Optional metadata

        Returns:
            Memory entry ID
        """
        pass

    @abstractmethod
    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        """Get a memory entry by ID.

        Args:
            entry_id: Memory entry ID

        Returns:
            Memory entry or None if not found
        """
        pass

    @abstractmethod
    def search(
        self, query: str, limit: int = 5, min_score: float = 0.0
    ) -> List[MemoryEntry]:
        """Search for relevant memories.

        Args:
            query: Search query
            limit: Maximum number of results
            min_score: Minimum relevance score

        Returns:
            List of relevant memory entries
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all memories."""
        pass

    @abstractmethod
    def size(self) -> int:
        """Get the number of memory entries.

        Returns:
            Number of entries
        """
        pass
