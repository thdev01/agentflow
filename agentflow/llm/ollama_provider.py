"""Ollama LLM provider for local models."""

from typing import Any, Dict, List, Optional

try:
    import httpx
except ImportError:
    raise ImportError(
        "Ollama provider requires the 'httpx' package. "
        "Install it with: pip install agentflow[ollama]"
    )

from agentflow.llm.base import LLMProvider, LLMResponse, Message, Role


class OllamaProvider(LLMProvider):
    """Ollama LLM provider for local models."""

    def __init__(
        self,
        model: str = "llama2",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize Ollama provider.

        Args:
            model: Model name (e.g., 'llama2', 'mistral', 'codellama')
            base_url: Ollama server URL (defaults to localhost:11434)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Ollama parameters
        """
        super().__init__(model, temperature, max_tokens, **kwargs)
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=300.0)  # 5 minute timeout
        self.async_client = httpx.AsyncClient(timeout=300.0)

    def _convert_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert Message objects to Ollama format."""
        ollama_messages = []

        for msg in messages:
            # Ollama uses 'system', 'user', 'assistant' roles
            role = msg.role.value

            # Handle tool messages by converting to user messages
            if role == "tool":
                role = "user"
                content = f"Tool '{msg.name}' returned: {msg.content}"
            else:
                content = msg.content

            ollama_messages.append({
                "role": role,
                "content": content
            })

        return ollama_messages

    def _parse_tool_calls(self, content: str) -> Optional[List[Dict[str, Any]]]:
        """Parse tool calls from model response.

        Ollama doesn't natively support tool calling, so we look for JSON patterns
        that indicate tool usage.
        """
        import json
        import re

        # Look for tool call patterns in the response
        # Pattern: {"tool": "tool_name", "arguments": {...}}
        tool_pattern = r'\{\s*"tool"\s*:\s*"([^"]+)"\s*,\s*"arguments"\s*:\s*(\{[^}]+\})\s*\}'
        matches = re.findall(tool_pattern, content)

        if not matches:
            return None

        tool_calls = []
        for i, (tool_name, args_str) in enumerate(matches):
            try:
                arguments = json.loads(args_str)
                tool_calls.append({
                    "id": f"call_{i}",
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": arguments
                    }
                })
            except json.JSONDecodeError:
                continue

        return tool_calls if tool_calls else None

    def complete(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate completion using Ollama."""
        ollama_messages = self._convert_messages(messages)

        # Add tool information to system prompt if tools are provided
        if tools:
            tool_descriptions = []
            for tool in tools:
                func = tool.get("function", {})
                tool_descriptions.append(
                    f"- {func.get('name')}: {func.get('description')}"
                )

            tools_prompt = (
                "\n\nYou have access to these tools:\n" +
                "\n".join(tool_descriptions) +
                '\n\nTo use a tool, respond with JSON: {"tool": "tool_name", "arguments": {...}}'
            )

            # Add to system message or create one
            if ollama_messages and ollama_messages[0]["role"] == "system":
                ollama_messages[0]["content"] += tools_prompt
            else:
                ollama_messages.insert(0, {"role": "system", "content": tools_prompt})

        params: Dict[str, Any] = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                **self.kwargs,
                **kwargs,
            }
        }

        if self.max_tokens:
            params["options"]["num_predict"] = self.max_tokens

        response = self.client.post(
            f"{self.base_url}/api/chat",
            json=params
        )
        response.raise_for_status()

        data = response.json()
        content = data.get("message", {}).get("content", "")

        # Parse tool calls if present
        tool_calls = None
        if tools:
            tool_calls = self._parse_tool_calls(content)

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=data.get("done_reason", "stop"),
            usage={
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
                "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
            }
        )

    async def acomplete(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Async generate completion using Ollama."""
        ollama_messages = self._convert_messages(messages)

        # Add tool information to system prompt if tools are provided
        if tools:
            tool_descriptions = []
            for tool in tools:
                func = tool.get("function", {})
                tool_descriptions.append(
                    f"- {func.get('name')}: {func.get('description')}"
                )

            tools_prompt = (
                "\n\nYou have access to these tools:\n" +
                "\n".join(tool_descriptions) +
                '\n\nTo use a tool, respond with JSON: {"tool": "tool_name", "arguments": {...}}'
            )

            # Add to system message or create one
            if ollama_messages and ollama_messages[0]["role"] == "system":
                ollama_messages[0]["content"] += tools_prompt
            else:
                ollama_messages.insert(0, {"role": "system", "content": tools_prompt})

        params: Dict[str, Any] = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                **self.kwargs,
                **kwargs,
            }
        }

        if self.max_tokens:
            params["options"]["num_predict"] = self.max_tokens

        response = await self.async_client.post(
            f"{self.base_url}/api/chat",
            json=params
        )
        response.raise_for_status()

        data = response.json()
        content = data.get("message", {}).get("content", "")

        # Parse tool calls if present
        tool_calls = None
        if tools:
            tool_calls = self._parse_tool_calls(content)

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=data.get("done_reason", "stop"),
            usage={
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
                "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
            }
        )

    def __del__(self) -> None:
        """Cleanup HTTP clients."""
        try:
            self.client.close()
        except Exception:
            pass
