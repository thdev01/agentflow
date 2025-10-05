# AgentFlow

**A developer-first multi-agent framework for building LLM-powered applications.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Why AgentFlow?

Building multi-agent systems shouldn't require a PhD. AgentFlow makes it simple:

- **🎯 Clean API** - Write agents in 10 lines, not 100
- **🔍 Transparent** - See exactly what your agents are doing
- **🔌 Flexible** - Works with OpenAI, Anthropic, and local LLMs
- **⚡ Production-Ready** - Built for real applications, not just demos
- **🧪 Test-Friendly** - Easy to test and debug

### Comparison with Other Frameworks

| Feature | AgentFlow | CrewAI | AutoGen | LangGraph |
|---------|-----------|--------|---------|-----------|
| Learning Curve | ⭐ Easy | ⭐⭐ Medium | ⭐⭐⭐ Hard | ⭐⭐⭐ Hard |
| Transparency | ✅ Full | ⚠️ Partial | ⚠️ Partial | ✅ Full |
| LLM Support | 🌐 Any | 🌐 Any | 🌐 Any | 🌐 Any |
| Async Support | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Built-in Tools | ✅ Yes | ✅ Yes | ⚠️ Limited | ⚠️ Limited |
| Documentation | 📚 Clear | 📚 Clear | ⚠️ Complex | ⚠️ Technical |

---

## Installation

```bash
# Basic installation
pip install agentflow

# With OpenAI support
pip install agentflow[openai]

# With Anthropic (Claude) support
pip install agentflow[anthropic]

# With all providers
pip install agentflow[all]

# For development
pip install agentflow[dev]
```

---

## Quick Start

### Simple Agent

```python
from agentflow import Agent, tool

@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    return f"The weather in {location} is sunny and 72°F"

# Create an agent
agent = Agent(
    name="assistant",
    role="A helpful assistant",
    llm="gpt-4",  # or "claude-3-5-sonnet-20241022"
    tools=[get_weather],
    verbose=True
)

# Execute a task
result = agent.execute("What's the weather in San Francisco?")
print(result)
```

### Multi-Agent Team

```python
from agentflow import Agent, Supervisor, tool

@tool
def search_web(query: str) -> str:
    """Search the web."""
    return f"Results for: {query}"

@tool
def write_content(topic: str) -> str:
    """Write content on a topic."""
    return f"Article about {topic}..."

# Create specialized agents
researcher = Agent(
    name="researcher",
    role="Research topics",
    tools=[search_web],
    llm="gpt-4"
)

writer = Agent(
    name="writer",
    role="Write content",
    tools=[write_content],
    llm="gpt-4"
)

# Create a supervisor to coordinate them
team = Supervisor(agents=[researcher, writer], verbose=True)

# Execute a complex task
result = team.execute("Research AI agents and write a blog post")
print(result)
```

### Async Support

```python
import asyncio
from agentflow import Agent

async def main():
    agent = Agent(name="async_agent", llm="gpt-4")
    result = await agent.aexecute("Analyze this data...")
    print(result)

asyncio.run(main())
```

---

## Features

### 🎯 Simple Agent Creation

Create agents with minimal boilerplate:

```python
agent = Agent(
    name="my_agent",
    role="What this agent does",
    llm="gpt-4",  # Auto-detects provider
    tools=[tool1, tool2],
    max_iterations=10,
    verbose=True
)
```

### 🔧 Easy Tool Definition

Turn any function into a tool with a decorator:

```python
@tool
def my_tool(param1: str, param2: int) -> str:
    """Tool description goes here."""
    return f"Result: {param1} * {param2}"
```

### 🧰 Built-in Tool Library

Common tools ready to use:

```python
from agentflow.tools import (
    read_file, write_file, list_files,    # File operations
    web_search, fetch_url,                 # Web tools
    execute_python, execute_shell          # Code execution (use with caution!)
)

agent = Agent(
    name="assistant",
    llm="gpt-4",
    tools=[read_file, write_file, web_search]
)
```

### 🧠 Memory Systems

Multiple memory types for different use cases:

```python
from agentflow.memory import (
    ShortTermMemory,      # Recent conversation history
    LongTermMemory,       # Semantic search with embeddings
    JSONMemoryStore,      # Persistent JSON storage
    SQLiteMemoryStore     # Persistent SQLite storage
)

# Short-term memory with limits
memory = ShortTermMemory(max_entries=100, max_age_seconds=3600)
memory.add("User prefers concise answers", {"type": "preference"})

# Long-term memory with semantic search
memory = LongTermMemory(embedding_function=embed_fn)
results = memory.search("Python programming", limit=5)

# Persistent storage
memory = JSONMemoryStore("./agent_memory.json")
memory = SQLiteMemoryStore("./agent_memory.db")
```

### 🤝 Multiple Orchestration Patterns

- **Supervisor**: Central coordinator delegates tasks to specialized agents
- **Hierarchical** *(coming soon)*: Multi-level management structure
- **Peer-to-Peer** *(coming soon)*: Agents collaborate directly

### 🔌 LLM Provider Support

Works with any LLM provider:

```python
# OpenAI
agent = Agent(llm="gpt-4")
agent = Agent(llm="gpt-3.5-turbo")

# Anthropic
agent = Agent(llm="claude-3-5-sonnet-20241022")
agent = Agent(llm="claude-3-opus-20240229")

# Ollama (local models - no API key needed!)
agent = Agent(llm="llama2")
agent = Agent(llm="mistral")
agent = Agent(llm="codellama")

# Custom provider
from agentflow.llm import LLMProvider
agent = Agent(llm=MyCustomProvider())
```

### 📊 Built-in Observability

Track what your agents are doing:

```python
agent = Agent(name="my_agent", verbose=True)
# Outputs:
# [my_agent] Executing task: ...
# [my_agent] Tool calls requested: 2
# [my_agent] Calling tool: search_web(query='AI agents')
# [my_agent] Tool result: ...
# [my_agent] Task completed
```

---

## Architecture

```
agentflow/
├── agents/          # Core agent implementation
├── orchestration/   # Supervisor, hierarchical patterns
├── memory/          # Short/long-term memory (coming soon)
├── tools/           # Built-in and custom tools
├── llm/             # LLM providers (OpenAI, Anthropic, etc.)
└── observability/   # Logging, tracing, debugging (coming soon)
```

---

## Examples

Check out the [`examples/`](examples/) directory for more:

- [`simple_agent.py`](examples/simple_agent.py) - Basic agent with tools
- [`multi_agent_team.py`](examples/multi_agent_team.py) - Supervisor coordinating multiple agents
- [`async_agent.py`](examples/async_agent.py) - Async agent execution
- [`ollama_agent.py`](examples/ollama_agent.py) - Using local LLMs with Ollama
- [`builtin_tools.py`](examples/builtin_tools.py) - Using built-in tools for file, web, and code operations
- [`memory_agent.py`](examples/memory_agent.py) - Using memory systems for conversation history and persistence

---

## Roadmap

- [x] Core agent system
- [x] Tool system
- [x] OpenAI provider
- [x] Anthropic provider
- [x] Supervisor orchestration
- [x] Async support
- [x] Ollama provider (local LLMs)
- [x] Built-in tool library (file ops, web, code execution)
- [x] Memory system (short-term, long-term, persistent storage)
- [ ] Observability & tracing
- [ ] Hierarchical orchestration
- [ ] Peer-to-peer orchestration
- [ ] Testing utilities
- [ ] Documentation site

---

## Contributing

We welcome contributions! AgentFlow is designed to be contributor-friendly.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Run linters (`black . && ruff check .`)
6. Commit your changes (`git commit -m 'feat: add amazing feature'`)
7. Push to your branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Good First Issues

Looking for a place to start? Check out issues labeled [`good first issue`](https://github.com/thdev01/agentflow/labels/good%20first%20issue).

---

## Development Setup

```bash
# Clone the repository
git clone https://github.com/thdev01/agentflow.git
cd agentflow

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linters
black .
ruff check .
mypy agentflow
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Citation

If you use AgentFlow in your research or project, please cite:

```bibtex
@software{agentflow2025,
  title = {AgentFlow: A Developer-First Multi-Agent Framework},
  author = {thdev01},
  year = {2025},
  url = {https://github.com/thdev01/agentflow}
}
```

---

## Acknowledgments

AgentFlow is inspired by:
- [AutoGen](https://github.com/microsoft/autogen) - Conversational multi-agent framework
- [CrewAI](https://github.com/joaomdmoura/crewAI) - Role-based agent coordination
- [LangGraph](https://github.com/langchain-ai/langgraph) - Graph-based agent workflows

---

## Community & Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/thdev01/agentflow/issues)
- **Discussions**: [Ask questions and share ideas](https://github.com/thdev01/agentflow/discussions)
- **Twitter**: [@thdev01](https://twitter.com/thdev01) *(optional)*

---

Made with ❤️ by [thdev01](https://github.com/thdev01)
