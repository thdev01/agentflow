"""Multi-agent team with Supervisor example."""

import os
from agentflow import Agent, Supervisor, tool

# Set your API key
# os.environ["OPENAI_API_KEY"] = "your-key-here"


# Define tools for different agents
@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    # Mock implementation - replace with real web search
    return f"Search results for '{query}': AgentFlow is a developer-first multi-agent framework released in 2025. It supports OpenAI, Anthropic, and local LLMs."


@tool
def analyze_data(data: str) -> str:
    """Analyze data and provide insights."""
    # Mock implementation
    return f"Analysis of '{data}': The framework shows strong potential with good architecture and developer experience."


@tool
def write_content(topic: str, style: str) -> str:
    """Write content on a topic in a specific style."""
    # Mock implementation
    return f"# {topic}\n\nThis is a {style} article about {topic}. The content is engaging and informative."


def main() -> None:
    # Create specialized agents
    researcher = Agent(
        name="researcher",
        role="Research topics and gather information from the web",
        llm="gpt-4",
        tools=[search_web],
    )

    analyst = Agent(
        name="analyst",
        role="Analyze data and provide insights",
        llm="gpt-4",
        tools=[analyze_data],
    )

    writer = Agent(
        name="writer",
        role="Write engaging content based on research and analysis",
        llm="gpt-4",
        tools=[write_content],
    )

    # Create supervisor to coordinate the team
    team = Supervisor(
        agents=[researcher, analyst, writer],
        llm="gpt-4",
        verbose=True,
    )

    # Execute a complex task
    task = "Research AgentFlow framework, analyze its potential, and write a blog post about it"
    result = team.execute(task)

    print(f"\n{'='*80}")
    print("FINAL RESULT:")
    print(f"{'='*80}")
    print(result)


if __name__ == "__main__":
    main()
