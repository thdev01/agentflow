"""Base classes and decorators for tools."""

import inspect
import json
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, get_type_hints

from pydantic import BaseModel


class Tool(BaseModel):
    """A tool that can be used by agents."""

    name: str
    description: str
    function: Callable[..., Any]
    parameters: Dict[str, Any]

    class Config:
        arbitrary_types_allowed = True

    def execute(self, **kwargs: Any) -> Any:
        """Execute the tool with given arguments."""
        return self.function(**kwargs)

    def to_openai_format(self) -> Dict[str, Any]:
        """Convert tool to OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def to_anthropic_format(self) -> Dict[str, Any]:
        """Convert tool to Anthropic tool format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
        }


def tool(func: Optional[Callable[..., Any]] = None, *, name: Optional[str] = None, description: Optional[str] = None) -> Any:
    """Decorator to convert a function into a Tool.

    Args:
        func: The function to convert
        name: Override the tool name (defaults to function name)
        description: Tool description (defaults to function docstring)

    Example:
        @tool
        def search_web(query: str) -> str:
            \"\"\"Search the web for information.\"\"\"
            return f"Results for: {query}"

        @tool(name="custom_name", description="Custom description")
        def my_tool(x: int, y: int) -> int:
            return x + y
    """

    def decorator(f: Callable[..., Any]) -> Tool:
        tool_name = name or f.__name__
        tool_description = description or (f.__doc__ or "").strip()

        # Get function signature
        sig = inspect.signature(f)
        type_hints = get_type_hints(f)

        # Build parameters schema
        properties: Dict[str, Dict[str, Any]] = {}
        required: List[str] = []

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            param_type = type_hints.get(param_name, str)
            python_type_to_json = {
                int: "integer",
                float: "number",
                str: "string",
                bool: "boolean",
                list: "array",
                dict: "object",
            }

            json_type = python_type_to_json.get(param_type, "string")

            properties[param_name] = {"type": json_type}

            # Add description from annotations if available
            if param.annotation != inspect.Parameter.empty:
                properties[param_name]["description"] = f"Parameter of type {param_type.__name__}"

            # Mark as required if no default value
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        parameters = {
            "type": "object",
            "properties": properties,
            "required": required,
        }

        return Tool(
            name=tool_name,
            description=tool_description,
            function=f,
            parameters=parameters,
        )

    if func is None:
        return decorator
    else:
        return decorator(func)
