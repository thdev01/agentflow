"""OpenAI LLM provider."""

from typing import Any, Dict, List, Optional

try:
    from openai import AsyncOpenAI, OpenAI
except ImportError:
    raise ImportError(
        "OpenAI provider requires the 'openai' package. "
        "Install it with: pip install agentflow[openai]"
    )

from agentflow.llm.base import LLMProvider, LLMResponse, Message, Role


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""

    def __init__(
        self,
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize OpenAI provider.

        Args:
            model: Model name (e.g., 'gpt-4', 'gpt-3.5-turbo')
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional OpenAI parameters
        """
        super().__init__(model, temperature, max_tokens, **kwargs)
        self.client = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)

    def _convert_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert Message objects to OpenAI format."""
        return [
            {
                "role": msg.role.value,
                "content": msg.content,
                **({"name": msg.name} if msg.name else {}),
                **({"tool_calls": msg.tool_calls} if msg.tool_calls else {}),
                **({"tool_call_id": msg.tool_call_id} if msg.tool_call_id else {}),
            }
            for msg in messages
        ]

    def complete(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate completion using OpenAI."""
        params: Dict[str, Any] = {
            "model": self.model,
            "messages": self._convert_messages(messages),
            "temperature": self.temperature,
            **self.kwargs,
            **kwargs,
        }

        if self.max_tokens:
            params["max_tokens"] = self.max_tokens

        if tools:
            params["tools"] = tools

        response = self.client.chat.completions.create(**params)
        choice = response.choices[0]

        return LLMResponse(
            content=choice.message.content or "",
            tool_calls=(
                [tc.model_dump() for tc in choice.message.tool_calls]
                if choice.message.tool_calls
                else None
            ),
            finish_reason=choice.finish_reason,
            usage=response.usage.model_dump() if response.usage else None,
        )

    async def acomplete(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Async generate completion using OpenAI."""
        params: Dict[str, Any] = {
            "model": self.model,
            "messages": self._convert_messages(messages),
            "temperature": self.temperature,
            **self.kwargs,
            **kwargs,
        }

        if self.max_tokens:
            params["max_tokens"] = self.max_tokens

        if tools:
            params["tools"] = tools

        response = await self.async_client.chat.completions.create(**params)
        choice = response.choices[0]

        return LLMResponse(
            content=choice.message.content or "",
            tool_calls=(
                [tc.model_dump() for tc in choice.message.tool_calls]
                if choice.message.tool_calls
                else None
            ),
            finish_reason=choice.finish_reason,
            usage=response.usage.model_dump() if response.usage else None,
        )
