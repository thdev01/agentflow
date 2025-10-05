"""Code execution tools.

WARNING: These tools execute arbitrary code and should be used with caution.
Only use in trusted environments.
"""

import subprocess
import sys
from io import StringIO
from typing import Optional

from agentflow.tools.base import tool


@tool
def execute_python(code: str) -> str:
    """Execute Python code and return the output.

    WARNING: This executes arbitrary code. Use with caution!

    Args:
        code: Python code to execute

    Returns:
        Output from code execution
    """
    try:
        # Capture stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        # Create a namespace for execution
        namespace: dict = {}

        try:
            # Execute the code
            exec(code, namespace)

            # Get output
            stdout_value = sys.stdout.getvalue()
            stderr_value = sys.stderr.getvalue()

            output = ""
            if stdout_value:
                output += f"STDOUT:\n{stdout_value}\n"
            if stderr_value:
                output += f"STDERR:\n{stderr_value}\n"

            return output if output else "Code executed successfully (no output)"

        except Exception as e:
            return f"Execution Error: {type(e).__name__}: {str(e)}"

        finally:
            # Restore stdout and stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    except Exception as e:
        return f"Error: {str(e)}"


@tool
def execute_shell(command: str, timeout: int = 30) -> str:
    """Execute a shell command and return the output.

    WARNING: This executes arbitrary shell commands. Use with caution!

    Args:
        command: Shell command to execute
        timeout: Maximum execution time in seconds

    Returns:
        Command output or error message
    """
    try:
        # Execute command with timeout
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"

        output += f"\nReturn Code: {result.returncode}"

        return output if output else "Command executed successfully (no output)"

    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"
