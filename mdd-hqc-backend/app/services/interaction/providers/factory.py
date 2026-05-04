"""Factory helpers that instantiate the configured LLM provider."""

from app.core.config import config

from .base import LLMProvider
from .lmstudio import LMStudioProvider
from .ollama import OllamaProvider
from .openrouter import OpenRouterProvider


def get_provider(provider_name: str | None = None) -> LLMProvider:
    """Returns the configured provider implementation for one interaction request."""

    selected_provider = (provider_name or config.LLM_PROVIDER).lower()
    if selected_provider == "ollama":
        return OllamaProvider()
    if selected_provider == "lmstudio":
        return LMStudioProvider()
    if selected_provider == "openrouter":
        return OpenRouterProvider()
    raise ValueError(f"Unknown LLM provider: {selected_provider}")
