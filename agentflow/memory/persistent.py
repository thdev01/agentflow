"""Persistent memory storage."""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from agentflow.memory.base import Memory, MemoryEntry


class JSONMemoryStore(Memory):
    """JSON-based persistent memory storage."""

    def __init__(self, file_path: str) -> None:
        """Initialize JSON memory store.

        Args:
            file_path: Path to JSON file for storage
        """
        self.file_path = Path(file_path)
        self.entries: Dict[str, MemoryEntry] = {}
        self._load()

    def add(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a memory entry."""
        import uuid
        from datetime import datetime

        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            content=content,
            metadata=metadata or {},
            timestamp=datetime.now(),
        )

        self.entries[entry.id] = entry
        self._save()
        return entry.id

    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        """Get a memory entry by ID."""
        return self.entries.get(entry_id)

    def search(
        self, query: str, limit: int = 5, min_score: float = 0.0
    ) -> List[MemoryEntry]:
        """Search for relevant memories using keyword matching."""
        query_lower = query.lower()
        results = []

        for entry in self.entries.values():
            content_lower = entry.content.lower()
            score = 0.0

            query_terms = query_lower.split()
            for term in query_terms:
                if term in content_lower:
                    score += 1.0 / len(query_terms)

            if score >= min_score:
                results.append((score, entry))

        results.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in results[:limit]]

    def clear(self) -> None:
        """Clear all memories."""
        self.entries.clear()
        self._save()

    def size(self) -> int:
        """Get the number of memory entries."""
        return len(self.entries)

    def _load(self) -> None:
        """Load memories from JSON file."""
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.entries = {
                        entry_id: MemoryEntry(**entry_data)
                        for entry_id, entry_data in data.items()
                    }
            except Exception as e:
                print(f"Warning: Could not load memories from {self.file_path}: {e}")
                self.entries = {}

    def _save(self) -> None:
        """Save memories to JSON file."""
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                data = {
                    entry_id: entry.model_dump()
                    for entry_id, entry in self.entries.items()
                }
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save memories to {self.file_path}: {e}")


class SQLiteMemoryStore(Memory):
    """SQLite-based persistent memory storage."""

    def __init__(self, db_path: str) -> None:
        """Initialize SQLite memory store.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                metadata TEXT,
                timestamp TEXT NOT NULL,
                importance REAL DEFAULT 0.5
            )
        """)

        conn.commit()
        conn.close()

    def add(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a memory entry."""
        import uuid
        from datetime import datetime

        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            content=content,
            metadata=metadata or {},
            timestamp=datetime.now(),
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO memories (id, content, metadata, timestamp, importance)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                entry.id,
                entry.content,
                json.dumps(entry.metadata),
                entry.timestamp.isoformat(),
                entry.importance,
            ),
        )

        conn.commit()
        conn.close()

        return entry.id

    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        """Get a memory entry by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM memories WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return self._row_to_entry(row)
        return None

    def search(
        self, query: str, limit: int = 5, min_score: float = 0.0
    ) -> List[MemoryEntry]:
        """Search for relevant memories using SQLite FTS or LIKE."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Simple LIKE-based search
        query_pattern = f"%{query}%"
        cursor.execute(
            """
            SELECT * FROM memories
            WHERE content LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (query_pattern, limit),
        )

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_entry(row) for row in rows]

    def clear(self) -> None:
        """Clear all memories."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memories")
        conn.commit()
        conn.close()

    def size(self) -> int:
        """Get the number of memory entries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM memories")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def _row_to_entry(self, row: tuple) -> MemoryEntry:
        """Convert database row to MemoryEntry."""
        from datetime import datetime

        return MemoryEntry(
            id=row[0],
            content=row[1],
            metadata=json.loads(row[2]) if row[2] else {},
            timestamp=datetime.fromisoformat(row[3]),
            importance=row[4],
        )
