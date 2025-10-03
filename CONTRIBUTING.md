# Contributing to AgentFlow

Thank you for your interest in contributing to AgentFlow! We're excited to welcome contributors of all skill levels.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)

---

## Code of Conduct

Be respectful, inclusive, and constructive. We're all here to build something great together.

---

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic understanding of Python and async programming

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/agentflow.git
   cd agentflow
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/thdev01/agentflow.git
   ```

4. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install development dependencies**:
   ```bash
   pip install -e ".[dev,all]"
   ```

6. **Install pre-commit hooks** (optional but recommended):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

---

## How to Contribute

### Types of Contributions

- **Bug fixes**: Fix issues or unexpected behavior
- **Features**: Add new functionality
- **Documentation**: Improve docs, examples, or comments
- **Tests**: Add test coverage
- **Performance**: Optimize existing code
- **Refactoring**: Improve code quality

### Finding Issues to Work On

1. Browse [open issues](https://github.com/thdev01/agentflow/issues)
2. Look for labels:
   - `good first issue` - Great for newcomers
   - `help wanted` - We need community help
   - `bug` - Something isn't working
   - `enhancement` - New feature or request
   - `documentation` - Documentation improvements

3. Comment on the issue to let others know you're working on it

---

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 100 characters
- **Formatting**: Use `black` for auto-formatting
- **Linting**: Use `ruff` for linting
- **Type hints**: Use type hints for all public functions
- **Docstrings**: Use Google-style docstrings

### Example

```python
from typing import List, Optional

def example_function(
    param1: str,
    param2: int,
    optional_param: Optional[bool] = None
) -> List[str]:
    """Short description of the function.

    More detailed description if needed. Explain what the function
    does, when to use it, and any important caveats.

    Args:
        param1: Description of param1
        param2: Description of param2
        optional_param: Description of optional parameter

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is negative
    """
    if param2 < 0:
        raise ValueError("param2 must be non-negative")

    return [param1] * param2
```

### Running Code Quality Tools

```bash
# Format code
black .

# Lint code
ruff check .

# Type checking
mypy agentflow

# Run all checks
black . && ruff check . && mypy agentflow
```

---

## Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agentflow

# Run specific test file
pytest tests/test_agent.py

# Run specific test
pytest tests/test_agent.py::test_agent_creation
```

### Writing Tests

- Place tests in the `tests/` directory
- Mirror the source structure (e.g., `tests/test_agents/test_agent.py`)
- Use descriptive test names: `test_agent_executes_tool_correctly`
- Cover edge cases and error conditions

Example test:

```python
import pytest
from agentflow import Agent, tool

@tool
def mock_tool(x: int) -> int:
    """Mock tool for testing."""
    return x * 2

def test_agent_uses_tool_correctly():
    """Test that agent correctly uses a tool."""
    agent = Agent(
        name="test_agent",
        tools=[mock_tool],
        llm="gpt-4"  # You'll need to mock this
    )

    result = agent.execute("Double the number 5")
    assert "10" in result.lower()
```

---

## Pull Request Process

### Before Submitting

1. **Sync with upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
4. **Add tests** for new functionality
5. **Run all checks**:
   ```bash
   pytest
   black .
   ruff check .
   mypy agentflow
   ```

6. **Commit with conventional commits**:
   ```bash
   git commit -m "feat: add new feature"
   git commit -m "fix: resolve bug in agent execution"
   git commit -m "docs: update README"
   git commit -m "test: add tests for tools"
   git commit -m "refactor: improve code structure"
   ```

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Adding or updating tests
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `chore:` - Maintenance tasks

### Submitting the PR

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub

3. **Fill out the PR template** with:
   - Clear description of changes
   - Related issue numbers (e.g., "Fixes #123")
   - Testing steps
   - Screenshots (if applicable)

4. **Respond to review feedback**
   - Be open to suggestions
   - Make requested changes
   - Re-request review when ready

### PR Review Criteria

Your PR will be reviewed for:
- ✅ Code quality and style
- ✅ Test coverage
- ✅ Documentation updates
- ✅ Backwards compatibility
- ✅ Performance implications

---

## Issue Guidelines

### Reporting Bugs

Use the bug report template and include:
- Clear description of the bug
- Steps to reproduce
- Expected vs. actual behavior
- Environment details (Python version, OS, etc.)
- Error messages or stack traces

### Requesting Features

Use the feature request template and include:
- Clear description of the feature
- Use case / motivation
- Proposed API or implementation (if applicable)
- Alternatives considered

### Asking Questions

- Check existing [issues](https://github.com/thdev01/agentflow/issues) and [discussions](https://github.com/thdev01/agentflow/discussions)
- Use [GitHub Discussions](https://github.com/thdev01/agentflow/discussions) for general questions
- Use issues for specific bugs or feature requests

---

## Project Structure

```
agentflow/
├── agentflow/              # Main package
│   ├── agents/            # Agent implementations
│   ├── orchestration/     # Multi-agent patterns
│   ├── tools/             # Tool system
│   ├── llm/               # LLM providers
│   ├── memory/            # Memory systems (TODO)
│   └── observability/     # Logging & tracing (TODO)
├── examples/              # Example scripts
├── tests/                 # Test suite
├── docs/                  # Documentation
├── .github/               # GitHub templates & workflows
└── pyproject.toml         # Project configuration
```

---

## Development Tips

### Adding a New LLM Provider

1. Create a file in `agentflow/llm/` (e.g., `ollama_provider.py`)
2. Inherit from `LLMProvider` base class
3. Implement `complete()` and `acomplete()` methods
4. Add to `pyproject.toml` optional dependencies
5. Update documentation

### Adding a New Orchestration Pattern

1. Create a file in `agentflow/orchestration/`
2. Implement the pattern (reference `supervisor.py`)
3. Add to `agentflow/orchestration/__init__.py`
4. Create example in `examples/`
5. Add tests

### Adding Built-in Tools

1. Create tool in `agentflow/tools/builtin.py`
2. Use the `@tool` decorator
3. Add comprehensive docstring
4. Add tests
5. Update documentation

---

## Release Process

Releases are handled by maintainers:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a git tag: `git tag v0.2.0`
4. Push tag: `git push --tags`
5. GitHub Actions will publish to PyPI

---

## Getting Help

- **Documentation**: Check [README.md](README.md) and examples
- **Discussions**: [GitHub Discussions](https://github.com/thdev01/agentflow/discussions)
- **Issues**: [GitHub Issues](https://github.com/thdev01/agentflow/issues)
- **Maintainer**: [@thdev01](https://github.com/thdev01)

---

## Recognition

Contributors will be:
- Listed in README.md
- Mentioned in release notes
- Added to GitHub contributors page

---

Thank you for contributing to AgentFlow! 🎉
