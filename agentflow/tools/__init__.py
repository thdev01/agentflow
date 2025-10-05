"""Tools for AgentFlow agents."""

from agentflow.tools.base import Tool, tool

# Built-in tools - imported separately to avoid circular imports
try:
    from agentflow.tools.builtin import (
        read_file,
        write_file,
        list_files,
        web_search,
        fetch_url,
        execute_python,
        execute_shell,
    )

    __all__ = [
        "Tool",
        "tool",
        "read_file",
        "write_file",
        "list_files",
        "web_search",
        "fetch_url",
        "execute_python",
        "execute_shell",
    ]
except ImportError:
    # If builtin tools can't be imported, just export base tools
    __all__ = ["Tool", "tool"]
