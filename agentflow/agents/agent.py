"""Core Agent implementation."""

import json
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from agentflow.llm.base import LLMProvider, Message, Role
from agentflow.llm.openai_provider import OpenAIProvider
from agentflow.tools.base import Tool


class AgentConfig(BaseModel):
    """Configuration for an Agent."""

    name: str
    role: str = Field(default="Assistant")
    system_prompt: Optional[str] = None
    max_iterations: int = Field(default=10, description="Maximum tool calling iterations")
    verbose: bool = Field(default=False, description="Enable verbose logging")


class Agent:
    """An autonomous agent that can use tools and interact with LLMs."""

    def __init__(
        self,
        name: str,
        role: str = "Assistant",
        system_prompt: Optional[str] = None,
        llm: Optional[Union[str, LLMProvider]] = None,
        tools: Optional[List[Tool]] = None,
        max_iterations: int = 10,
        verbose: bool = False,
    ) -> None:
        """Initialize an Agent.

        Args:
            name: Agent name
            role: Agent role/purpose
            system_prompt: Custom system prompt (auto-generated if not provided)
            llm: LLM provider instance or string (e.g., 'gpt-4', 'claude-3-5-sonnet-20241022')
            tools: List of tools the agent can use
            max_iterations: Maximum iterations for tool calling
            verbose: Enable verbose logging
        """
        self.config = AgentConfig(
            name=name,
            role=role,
            system_prompt=system_prompt,
            max_iterations=max_iterations,
            verbose=verbose,
        )
        self.tools = tools or []
        self.conversation_history: List[Message] = []

        # Initialize LLM
        if llm is None:
            self.llm = OpenAIProvider(model="gpt-4")
        elif isinstance(llm, str):
            # Auto-detect provider from model string
            if "gpt" in llm.lower():
                self.llm = OpenAIProvider(model=llm)
            elif "claude" in llm.lower():
                from agentflow.llm.anthropic_provider import AnthropicProvider

                self.llm = AnthropicProvider(model=llm)
            elif any(model in llm.lower() for model in ["llama", "mistral", "codellama", "phi", "gemma", "qwen"]):
                from agentflow.llm.ollama_provider import OllamaProvider

                self.llm = OllamaProvider(model=llm)
            else:
                # Default to OpenAI
                self.llm = OpenAIProvider(model=llm)
        else:
            self.llm = llm

        # Build system prompt
        self._build_system_prompt()

    def _build_system_prompt(self) -> None:
        """Build the system prompt for the agent."""
        if self.config.system_prompt:
            prompt = self.config.system_prompt
        else:
            prompt = f"You are {self.config.name}, a helpful AI assistant."
            if self.config.role:
                prompt += f"\n\nYour role: {self.config.role}"

            if self.tools:
                tool_names = ", ".join([t.name for t in self.tools])
                prompt += f"\n\nYou have access to the following tools: {tool_names}"
                prompt += "\n\nUse these tools when necessary to accomplish your tasks."

        self.conversation_history.append(Message(role=Role.SYSTEM, content=prompt))

    def _get_tool_by_name(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    def execute(self, task: str) -> str:
        """Execute a task.

        Args:
            task: The task description

        Returns:
            The agent's response
        """
        if self.config.verbose:
            print(f"[{self.config.name}] Executing task: {task}")

        # Add user message
        self.conversation_history.append(Message(role=Role.USER, content=task))

        iterations = 0
        while iterations < self.config.max_iterations:
            iterations += 1

            # Get LLM response
            tool_schemas = [t.to_openai_format() for t in self.tools] if self.tools else None
            response = self.llm.complete(
                messages=self.conversation_history, tools=tool_schemas
            )

            # Add assistant response to history
            self.conversation_history.append(
                Message(
                    role=Role.ASSISTANT,
                    content=response.content,
                    tool_calls=response.tool_calls,
                )
            )

            # Check if we need to call tools
            if response.tool_calls:
                if self.config.verbose:
                    print(f"[{self.config.name}] Tool calls requested: {len(response.tool_calls)}")

                for tool_call in response.tool_calls:
                    function_name = tool_call["function"]["name"]
                    function_args = tool_call["function"]["arguments"]

                    if isinstance(function_args, str):
                        function_args = json.loads(function_args)

                    if self.config.verbose:
                        print(f"[{self.config.name}] Calling tool: {function_name}({function_args})")

                    # Execute tool
                    tool = self._get_tool_by_name(function_name)
                    if tool:
                        try:
                            result = tool.execute(**function_args)
                            result_str = str(result)
                        except Exception as e:
                            result_str = f"Error executing tool: {str(e)}"

                        if self.config.verbose:
                            print(f"[{self.config.name}] Tool result: {result_str}")

                        # Add tool result to history
                        self.conversation_history.append(
                            Message(
                                role=Role.TOOL,
                                content=result_str,
                                tool_call_id=tool_call.get("id"),
                                name=function_name,
                            )
                        )
                    else:
                        self.conversation_history.append(
                            Message(
                                role=Role.TOOL,
                                content=f"Tool {function_name} not found",
                                tool_call_id=tool_call.get("id"),
                                name=function_name,
                            )
                        )
            else:
                # No more tool calls, return response
                if self.config.verbose:
                    print(f"[{self.config.name}] Task completed")
                return response.content

        return response.content

    async def aexecute(self, task: str) -> str:
        """Async version of execute.

        Args:
            task: The task description

        Returns:
            The agent's response
        """
        if self.config.verbose:
            print(f"[{self.config.name}] Executing task: {task}")

        # Add user message
        self.conversation_history.append(Message(role=Role.USER, content=task))

        iterations = 0
        while iterations < self.config.max_iterations:
            iterations += 1

            # Get LLM response
            tool_schemas = [t.to_openai_format() for t in self.tools] if self.tools else None
            response = await self.llm.acomplete(
                messages=self.conversation_history, tools=tool_schemas
            )

            # Add assistant response to history
            self.conversation_history.append(
                Message(
                    role=Role.ASSISTANT,
                    content=response.content,
                    tool_calls=response.tool_calls,
                )
            )

            # Check if we need to call tools
            if response.tool_calls:
                if self.config.verbose:
                    print(f"[{self.config.name}] Tool calls requested: {len(response.tool_calls)}")

                for tool_call in response.tool_calls:
                    function_name = tool_call["function"]["name"]
                    function_args = tool_call["function"]["arguments"]

                    if isinstance(function_args, str):
                        function_args = json.loads(function_args)

                    if self.config.verbose:
                        print(f"[{self.config.name}] Calling tool: {function_name}({function_args})")

                    # Execute tool
                    tool = self._get_tool_by_name(function_name)
                    if tool:
                        try:
                            result = tool.execute(**function_args)
                            result_str = str(result)
                        except Exception as e:
                            result_str = f"Error executing tool: {str(e)}"

                        if self.config.verbose:
                            print(f"[{self.config.name}] Tool result: {result_str}")

                        # Add tool result to history
                        self.conversation_history.append(
                            Message(
                                role=Role.TOOL,
                                content=result_str,
                                tool_call_id=tool_call.get("id"),
                                name=function_name,
                            )
                        )
                    else:
                        self.conversation_history.append(
                            Message(
                                role=Role.TOOL,
                                content=f"Tool {function_name} not found",
                                tool_call_id=tool_call.get("id"),
                                name=function_name,
                            )
                        )
            else:
                # No more tool calls, return response
                if self.config.verbose:
                    print(f"[{self.config.name}] Task completed")
                return response.content

        return response.content

    def reset(self) -> None:
        """Reset the agent's conversation history."""
        self.conversation_history = []
        self._build_system_prompt()
