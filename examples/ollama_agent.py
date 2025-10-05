"""Example: Using Ollama for local LLM inference.

This example shows how to use AgentFlow with Ollama for running
LLMs locally (no API keys needed).

Prerequisites:
1. Install Ollama: https://ollama.ai
2. Pull a model: ollama pull llama2
3. Run: python examples/ollama_agent.py
"""

from agentflow import Agent, tool


@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def get_system_info() -> str:
    """Get system information."""
    import platform

    return f"""System: {platform.system()}
Release: {platform.release()}
Machine: {platform.machine()}
Python: {platform.python_version()}"""


def main() -> None:
    """Run the Ollama agent example."""
    print("=" * 60)
    print("AgentFlow + Ollama: Local LLM Agent")
    print("=" * 60)
    print()

    # Create agent with Ollama (llama2, mistral, codellama, etc.)
    # The model name automatically triggers Ollama provider detection
    agent = Agent(
        name="local_assistant",
        role="A helpful local assistant running on Ollama",
        llm="llama2",  # or "mistral", "codellama", etc.
        tools=[calculate, get_system_info],
        verbose=True
    )

    # Test 1: Simple question
    print("\n📝 Test 1: Simple question")
    print("-" * 60)
    result = agent.execute("What is 42 + 58?")
    print(f"\n✅ Result: {result}\n")

    # Reset for next test
    agent.reset()

    # Test 2: System info
    print("\n📝 Test 2: Get system information")
    print("-" * 60)
    result = agent.execute("What system am I running on?")
    print(f"\n✅ Result: {result}\n")

    # Reset for next test
    agent.reset()

    # Test 3: Complex calculation
    print("\n📝 Test 3: Complex calculation")
    print("-" * 60)
    result = agent.execute("Calculate the result of (100 * 5) + (200 / 4)")
    print(f"\n✅ Result: {result}\n")


if __name__ == "__main__":
    # Check if Ollama is running
    import httpx

    try:
        response = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama is running with {len(models)} model(s)")
            if models:
                print(f"Available models: {', '.join([m['name'] for m in models])}\n")
        main()
    except Exception as e:
        print("❌ Error: Ollama is not running!")
        print("\nPlease start Ollama:")
        print("1. Install: https://ollama.ai")
        print("2. Pull a model: ollama pull llama2")
        print("3. Ollama should start automatically\n")
        print(f"Error details: {e}")
