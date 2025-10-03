"""Tests for tool system."""

import pytest
from agentflow.tools.base import Tool, tool


def test_tool_decorator() -> None:
    """Test that @tool decorator works correctly."""

    @tool
    def sample_tool(x: int, y: str) -> str:
        """Sample tool for testing."""
        return f"{y}: {x}"

    assert isinstance(sample_tool, Tool)
    assert sample_tool.name == "sample_tool"
    assert sample_tool.description == "Sample tool for testing."
    assert "x" in sample_tool.parameters["properties"]
    assert "y" in sample_tool.parameters["properties"]


def test_tool_decorator_with_args() -> None:
    """Test @tool decorator with custom name and description."""

    @tool(name="custom_name", description="Custom description")
    def my_func(a: int) -> int:
        return a * 2

    assert my_func.name == "custom_name"
    assert my_func.description == "Custom description"


def test_tool_execution() -> None:
    """Test tool execution."""

    @tool
    def add(x: int, y: int) -> int:
        """Add two numbers."""
        return x + y

    result = add.execute(x=5, y=3)
    assert result == 8


def test_tool_to_openai_format() -> None:
    """Test conversion to OpenAI format."""

    @tool
    def test_func(param: str) -> str:
        """Test function."""
        return param

    openai_format = test_func.to_openai_format()
    assert openai_format["type"] == "function"
    assert openai_format["function"]["name"] == "test_func"
    assert "parameters" in openai_format["function"]


def test_tool_to_anthropic_format() -> None:
    """Test conversion to Anthropic format."""

    @tool
    def test_func(param: str) -> str:
        """Test function."""
        return param

    anthropic_format = test_func.to_anthropic_format()
    assert anthropic_format["name"] == "test_func"
    assert "input_schema" in anthropic_format
