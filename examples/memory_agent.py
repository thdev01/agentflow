"""Example: Using memory systems with agents.

This example demonstrates how to use different memory systems:
- ShortTermMemory: Recent conversation history
- LongTermMemory: Semantic search with embeddings
- JSONMemoryStore: Persistent storage to JSON file
- SQLiteMemoryStore: Persistent storage to SQLite database
"""

from agentflow import Agent, tool
from agentflow.memory import (
    ShortTermMemory,
    LongTermMemory,
    JSONMemoryStore,
    SQLiteMemoryStore,
)


@tool
def save_to_memory(content: str) -> str:
    """Save important information to memory."""
    # This is a placeholder - in practice, the agent's memory system
    # would handle this automatically
    return f"Saved to memory: {content}"


def demo_short_term_memory() -> None:
    """Demonstrate short-term memory usage."""
    print("\n" + "=" * 60)
    print("Short-Term Memory Demo")
    print("=" * 60)

    # Create short-term memory with limits
    memory = ShortTermMemory(max_entries=10, max_age_seconds=3600)  # 1 hour

    # Add some memories
    memory.add("User asked about Python", {"type": "question"})
    memory.add("Explained Python basics", {"type": "response"})
    memory.add("User wants to learn asyncio", {"type": "question"})

    print(f"\nTotal memories: {memory.size()}")

    # Search for relevant memories
    print("\nSearching for 'Python':")
    results = memory.search("Python", limit=3)
    for entry in results:
        print(f"  - {entry.content} (at {entry.timestamp})")

    # Get recent memories
    print("\nRecent memories:")
    for entry in memory.get_recent(limit=2):
        print(f"  - {entry.content}")


def demo_long_term_memory() -> None:
    """Demonstrate long-term memory with semantic search."""
    print("\n" + "=" * 60)
    print("Long-Term Memory Demo (without embeddings)")
    print("=" * 60)

    # Create long-term memory without embeddings (keyword search fallback)
    memory = LongTermMemory()

    # Add memories
    memory.add("Python is a high-level programming language", {"topic": "python"})
    memory.add("JavaScript is used for web development", {"topic": "javascript"})
    memory.add("React is a JavaScript library for building UIs", {"topic": "react"})
    memory.add("Django is a Python web framework", {"topic": "python"})

    print(f"\nTotal memories: {memory.size()}")

    # Search
    print("\nSearching for 'Python web':")
    results = memory.search("Python web", limit=3)
    for entry in results:
        print(f"  - {entry.content}")

    print("\nNote: For true semantic search, provide an embedding function:")
    print("  memory = LongTermMemory(embedding_function=your_embedding_fn)")


def demo_json_persistence() -> None:
    """Demonstrate JSON-based persistent storage."""
    print("\n" + "=" * 60)
    print("JSON Persistent Memory Demo")
    print("=" * 60)

    # Create JSON store
    memory = JSONMemoryStore("./memory_data.json")

    # Add memories
    memory.add("First persistent memory", {"source": "demo"})
    memory.add("Second persistent memory", {"source": "demo"})

    print(f"\nTotal memories: {memory.size()}")
    print("Memories saved to: ./memory_data.json")

    # Search
    print("\nSearching for 'persistent':")
    results = memory.search("persistent", limit=5)
    for entry in results:
        print(f"  - {entry.content}")

    print("\n✅ Memories are persisted to disk and will survive restarts")


def demo_sqlite_persistence() -> None:
    """Demonstrate SQLite-based persistent storage."""
    print("\n" + "=" * 60)
    print("SQLite Persistent Memory Demo")
    print("=" * 60)

    # Create SQLite store
    memory = SQLiteMemoryStore("./memory_data.db")

    # Add memories
    memory.add("Database-stored memory 1", {"type": "important"})
    memory.add("Database-stored memory 2", {"type": "important"})

    print(f"\nTotal memories: {memory.size()}")
    print("Memories saved to: ./memory_data.db")

    # Search
    print("\nSearching for 'memory':")
    results = memory.search("memory", limit=5)
    for entry in results:
        print(f"  - {entry.content}")

    print("\n✅ Memories are stored in SQLite and queryable with SQL")


def demo_agent_with_memory() -> None:
    """Demonstrate agent using memory (conceptual example)."""
    print("\n" + "=" * 60)
    print("Agent with Memory (Conceptual)")
    print("=" * 60)

    print("\n📝 Note: Future versions will integrate memory directly into Agent")
    print("For now, you can use memory systems alongside agents:\n")

    # Create memory
    memory = ShortTermMemory(max_entries=50)

    # Simulate agent interactions
    memory.add("User: What is Python?", {"role": "user"})
    memory.add("Assistant: Python is a programming language...", {"role": "assistant"})
    memory.add("User: How do I learn it?", {"role": "user"})

    print("Conversation history:")
    for entry in memory.get_recent(limit=10):
        role = entry.metadata.get("role", "unknown")
        print(f"  [{role}] {entry.content}")

    print("\nSearching conversation for 'Python':")
    results = memory.search("Python", limit=3)
    for entry in results:
        print(f"  - {entry.content}")


def main() -> None:
    """Run all memory demos."""
    print("\n🧠 AgentFlow Memory System Demos\n")

    demo_short_term_memory()
    demo_long_term_memory()
    demo_json_persistence()
    demo_sqlite_persistence()
    demo_agent_with_memory()

    print("\n" + "=" * 60)
    print("All demos completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
