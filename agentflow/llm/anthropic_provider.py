"""Anthropic LLM provider."""

from typing import Any, Dict, List, Optional

try:
    from anthropic import Anthropic, AsyncAnthropic
except ImportError:
    raise ImportError(
        "Anthropic provider requires the 'anthropic' package. "
        "Install it with: pip install agentflow[anthropic]"
    )

from agentflow.llm.base import LLMProvider, LLMResponse, Message, Role


class AnthropicProvider(LLMProvider):
    """Anthropic (Claude) LLM provider."""

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 4096,
        **kwargs: Any,
    ) -> None:
        """Initialize Anthropic provider.

        Args:
            model: Model name (e.g., 'claude-3-5-sonnet-20241022')
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Anthropic parameters
        """
        super().__init__(model, temperature, max_tokens, **kwargs)
        self.client = Anthropic(api_key=api_key)
        self.async_client = AsyncAnthropic(api_key=api_key)

    def _convert_messages(self, messages: List[Message]) -> tuple[Optional[str], List[Dict[str, Any]]]:
        """Convert Message objects to Anthropic format.

        Returns:
            Tuple of (system_message, messages_list)
        """
        system_message = None
        converted_messages = []

        for msg in messages:
            if msg.role == Role.SYSTEM:
                system_message = msg.content
            else:
                converted_messages.append(
                    {
                        "role": "assistant" if msg.role == Role.ASSISTANT else "user",
                        "content": msg.content,
                    }
                )

        return system_message, converted_messages

    def complete(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate completion using Anthropic."""
        system, converted_messages = self._convert_messages(messages)

        params: Dict[str, Any] = {
            "model": self.model,
            "messages": converted_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens or 4096,
            **self.kwargs,
            **kwargs,
        }

        if system:
            params["system"] = system

        if tools:
            params["tools"] = tools

        response = self.client.messages.create(**params)

        content = ""
        tool_calls = None

        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                if tool_calls is None:
                    tool_calls = []
                tool_calls.append(
                    {
                        "id": block.id,
                        "type": "function",
                        "function": {"name": block.name, "arguments": block.input},
                    }
                )

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=response.stop_reason,
            usage={"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens},
        )

    async def acomplete(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Async generate completion using Anthropic."""
        system, converted_messages = self._convert_messages(messages)

        params: Dict[str, Any] = {
            "model": self.model,
            "messages": converted_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens or 4096,
            **self.kwargs,
            **kwargs,
        }

        if system:
            params["system"] = system

        if tools:
            params["tools"] = tools

        response = await self.async_client.messages.create(**params)

        content = ""
        tool_calls = None

        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                if tool_calls is None:
                    tool_calls = []
                tool_calls.append(
                    {
                        "id": block.id,
                        "type": "function",
                        "function": {"name": block.name, "arguments": block.input},
                    }
                )

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=response.stop_reason,
            usage={"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens},
        )
