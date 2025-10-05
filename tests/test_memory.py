"""Tests for memory systems."""

import tempfile
from pathlib import Path
from typing import List

import pytest

from agentflow.memory import (
    ShortTermMemory,
    LongTermMemory,
    JSONMemoryStore,
    SQLiteMemoryStore,
)


def test_short_term_memory_basic() -> None:
    """Test basic short-term memory functionality."""
    memory = ShortTermMemory()

    entry_id = memory.add("Test memory", {"type": "test"})
    assert entry_id is not None
    assert memory.size() == 1

    entry = memory.get(entry_id)
    assert entry is not None
    assert entry.content == "Test memory"
    assert entry.metadata["type"] == "test"


def test_short_term_memory_max_entries() -> None:
    """Test short-term memory with max entries limit."""
    memory = ShortTermMemory(max_entries=3)

    memory.add("Entry 1")
    memory.add("Entry 2")
    memory.add("Entry 3")
    memory.add("Entry 4")  # Should remove Entry 1

    assert memory.size() == 3
    # Most recent entries should be kept
    recent = memory.get_recent(limit=3)
    assert len(recent) == 3
    assert recent[0].content == "Entry 4"


def test_short_term_memory_search() -> None:
    """Test short-term memory search."""
    memory = ShortTermMemory()

    memory.add("Python programming")
    memory.add("JavaScript development")
    memory.add("Python web frameworks")

    results = memory.search("Python", limit=5)
    assert len(results) == 2
    assert all("Python" in r.content or "python" in r.content for r in results)


def test_short_term_memory_clear() -> None:
    """Test clearing short-term memory."""
    memory = ShortTermMemory()

    memory.add("Test 1")
    memory.add("Test 2")
    assert memory.size() == 2

    memory.clear()
    assert memory.size() == 0


def test_long_term_memory_basic() -> None:
    """Test basic long-term memory functionality."""
    memory = LongTermMemory()

    entry_id = memory.add("Long-term memory test", {"important": True})
    assert entry_id is not None

    entry = memory.get(entry_id)
    assert entry is not None
    assert entry.content == "Long-term memory test"


def test_long_term_memory_keyword_search() -> None:
    """Test long-term memory keyword search (without embeddings)."""
    memory = LongTermMemory()

    memory.add("Machine learning basics")
    memory.add("Deep learning networks")
    memory.add("Python programming")

    results = memory.search("learning", limit=5)
    assert len(results) == 2


def test_long_term_memory_with_embedding() -> None:
    """Test long-term memory with custom embedding function."""

    def simple_embedding(text: str) -> List[float]:
        """Simple embedding: character counts as vector."""
        return [float(ord(c)) for c in text[:10].ljust(10)]

    memory = LongTermMemory(embedding_function=simple_embedding)

    memory.add("Test A")
    memory.add("Test B")

    results = memory.search("Test", limit=5)
    assert len(results) > 0


def test_json_memory_store() -> None:
    """Test JSON memory store persistence."""
    with tempfile.TemporaryDirectory() as tmpdir:
        json_file = Path(tmpdir) / "memory.json"

        # Create and add memories
        memory1 = JSONMemoryStore(str(json_file))
        id1 = memory1.add("Persistent memory 1")
        id2 = memory1.add("Persistent memory 2")
        assert memory1.size() == 2

        # Reload from same file
        memory2 = JSONMemoryStore(str(json_file))
        assert memory2.size() == 2
        assert memory2.get(id1) is not None
        assert memory2.get(id2) is not None


def test_json_memory_store_search() -> None:
    """Test JSON memory store search."""
    with tempfile.TemporaryDirectory() as tmpdir:
        json_file = Path(tmpdir) / "memory.json"

        memory = JSONMemoryStore(str(json_file))
        memory.add("Python is great")
        memory.add("JavaScript is useful")

        results = memory.search("Python")
        assert len(results) == 1
        assert "Python" in results[0].content


def test_sqlite_memory_store() -> None:
    """Test SQLite memory store persistence."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "memory.db"

        # Create and add memories
        memory1 = SQLiteMemoryStore(str(db_file))
        id1 = memory1.add("Database memory 1")
        id2 = memory1.add("Database memory 2")
        assert memory1.size() == 2

        # Reload from same database
        memory2 = SQLiteMemoryStore(str(db_file))
        assert memory2.size() == 2
        assert memory2.get(id1) is not None
        assert memory2.get(id2) is not None


def test_sqlite_memory_store_search() -> None:
    """Test SQLite memory store search."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "memory.db"

        memory = SQLiteMemoryStore(str(db_file))
        memory.add("Learning Python")
        memory.add("Learning Go")

        results = memory.search("Python")
        assert len(results) >= 1
        assert any("Python" in r.content for r in results)


def test_memory_clear() -> None:
    """Test clearing different memory types."""
    # Short-term
    stm = ShortTermMemory()
    stm.add("Test")
    stm.clear()
    assert stm.size() == 0

    # Long-term
    ltm = LongTermMemory()
    ltm.add("Test")
    ltm.clear()
    assert ltm.size() == 0

    # JSON
    with tempfile.TemporaryDirectory() as tmpdir:
        json_file = Path(tmpdir) / "test.json"
        jmem = JSONMemoryStore(str(json_file))
        jmem.add("Test")
        jmem.clear()
        assert jmem.size() == 0

        # SQLite
        db_file = Path(tmpdir) / "test.db"
        smem = SQLiteMemoryStore(str(db_file))
        smem.add("Test")
        smem.clear()
        assert smem.size() == 0
