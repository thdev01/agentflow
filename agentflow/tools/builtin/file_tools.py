"""File operation tools."""

import os
from pathlib import Path
from typing import List

from agentflow.tools.base import tool


@tool
def read_file(file_path: str) -> str:
    """Read contents from a file.

    Args:
        file_path: Path to the file to read

    Returns:
        File contents as string
    """
    try:
        path = Path(file_path).expanduser().resolve()

        if not path.exists():
            return f"Error: File '{file_path}' does not exist"

        if not path.is_file():
            return f"Error: '{file_path}' is not a file"

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def write_file(file_path: str, content: str) -> str:
    """Write content to a file.

    Args:
        file_path: Path to the file to write
        content: Content to write to the file

    Returns:
        Success or error message
    """
    try:
        path = Path(file_path).expanduser().resolve()

        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Successfully wrote {len(content)} characters to '{file_path}'"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@tool
def list_files(directory: str) -> str:
    """List files and directories in a directory.

    Args:
        directory: Path to the directory

    Returns:
        List of files and directories
    """
    try:
        path = Path(directory).expanduser().resolve()

        if not path.exists():
            return f"Error: Directory '{directory}' does not exist"

        if not path.is_dir():
            return f"Error: '{directory}' is not a directory"

        items = []
        for item in sorted(path.iterdir()):
            item_type = "DIR" if item.is_dir() else "FILE"
            size = item.stat().st_size if item.is_file() else "-"
            items.append(f"[{item_type}] {item.name} ({size} bytes)" if size != "-" else f"[{item_type}] {item.name}")

        return "\n".join(items) if items else "Directory is empty"
    except Exception as e:
        return f"Error listing directory: {str(e)}"
