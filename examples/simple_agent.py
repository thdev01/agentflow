"""Simple agent example."""

import os
from agentflow import Agent, tool

# Set your API key
# os.environ["OPENAI_API_KEY"] = "your-key-here"


@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    # This is a mock function - in reality, you'd call a weather API
    return f"The weather in {location} is sunny and 72°F"


@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression)
        return f"The result is {result}"
    except Exception as e:
        return f"Error: {str(e)}"


def main() -> None:
    # Create an agent with tools
    agent = Agent(
        name="helpful_assistant",
        role="A helpful assistant that can check weather and do calculations",
        llm="gpt-4",  # or "claude-3-5-sonnet-20241022"
        tools=[get_weather, calculate],
        verbose=True,
    )

    # Execute a task
    result = agent.execute("What's the weather in San Francisco and what's 15 * 23?")
    print(f"\nFinal Result:\n{result}")


if __name__ == "__main__":
    main()
