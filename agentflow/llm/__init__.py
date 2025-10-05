"""LLM providers for AgentFlow."""

from agentflow.llm.base import LLMProvider, Message, Role

# Optional imports - fail gracefully if dependencies not installed
try:
    from agentflow.llm.openai_provider import OpenAIProvider
except ImportError:
    OpenAIProvider = None  # type: ignore

try:
    from agentflow.llm.anthropic_provider import AnthropicProvider
except ImportError:
    AnthropicProvider = None  # type: ignore

try:
    from agentflow.llm.ollama_provider import OllamaProvider
except ImportError:
    OllamaProvider = None  # type: ignore

__all__ = ["LLMProvider", "Message", "Role", "OpenAIProvider", "AnthropicProvider", "OllamaProvider"]
