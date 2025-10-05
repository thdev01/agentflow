"""Example: Using built-in tools.

This example demonstrates the built-in tools provided by AgentFlow for
common tasks like file operations, web requests, and code execution.
"""

from agentflow import Agent
from agentflow.tools import (
    read_file,
    write_file,
    list_files,
    web_search,
    fetch_url,
    execute_python,
)


def main() -> None:
    """Run the built-in tools example."""
    print("=" * 60)
    print("AgentFlow: Built-in Tools Demo")
    print("=" * 60)
    print()

    # Create agent with file operation tools
    file_agent = Agent(
        name="file_assistant",
        role="File operations assistant",
        llm="gpt-4",
        tools=[read_file, write_file, list_files],
        verbose=True
    )

    # Test 1: File operations
    print("\n📁 Test 1: File Operations")
    print("-" * 60)
    result = file_agent.execute(
        "Create a file called 'test_output.txt' with content 'Hello from AgentFlow!'"
    )
    print(f"\n✅ Result: {result}\n")

    # Test 2: Web tools
    web_agent = Agent(
        name="web_assistant",
        role="Web research assistant",
        llm="gpt-4",
        tools=[web_search, fetch_url],
        verbose=True
    )

    print("\n🌐 Test 2: Web Search")
    print("-" * 60)
    result = web_agent.execute("Search for information about Python asyncio")
    print(f"\n✅ Result: {result}\n")

    # Test 3: Code execution (use with caution!)
    code_agent = Agent(
        name="code_assistant",
        role="Code execution assistant",
        llm="gpt-4",
        tools=[execute_python],
        verbose=True
    )

    print("\n💻 Test 3: Code Execution")
    print("-" * 60)
    result = code_agent.execute(
        "Calculate the factorial of 5 using Python"
    )
    print(f"\n✅ Result: {result}\n")

    # Test 4: Combined tools
    multi_agent = Agent(
        name="multi_tool_assistant",
        role="Multi-purpose assistant",
        llm="gpt-4",
        tools=[read_file, write_file, execute_python, web_search],
        verbose=True
    )

    print("\n🔧 Test 4: Multiple Tools")
    print("-" * 60)
    result = multi_agent.execute(
        "Calculate 2^10 using Python, then write the result to a file called 'result.txt'"
    )
    print(f"\n✅ Result: {result}\n")

    print("\n" + "=" * 60)
    print("Demo completed! Check the generated files:")
    print("- test_output.txt")
    print("- result.txt")
    print("=" * 60)


if __name__ == "__main__":
    import os

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("\nPlease set your API key:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("\nOr use Ollama (no API key needed):")
        print("  See examples/ollama_agent.py")
    else:
        main()
