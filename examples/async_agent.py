"""Async agent example."""

import asyncio
import os
from agentflow import Agent, tool

# Set your API key
# os.environ["OPENAI_API_KEY"] = "your-key-here"


@tool
def fetch_data(source: str) -> str:
    """Fetch data from a source."""
    return f"Data from {source}: [sample data]"


async def main() -> None:
    # Create an async agent
    agent = Agent(
        name="async_agent",
        role="Process data asynchronously",
        llm="gpt-4",
        tools=[fetch_data],
        verbose=True,
    )

    # Execute multiple tasks concurrently
    tasks = [
        agent.aexecute("Fetch data from source A and summarize it"),
        agent.aexecute("Fetch data from source B and analyze it"),
    ]

    results = await asyncio.gather(*tasks)

    for i, result in enumerate(results, 1):
        print(f"\nTask {i} Result:\n{result}")


if __name__ == "__main__":
    asyncio.run(main())
