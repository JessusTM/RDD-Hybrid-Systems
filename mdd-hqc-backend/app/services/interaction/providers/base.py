"""Base contract for pluggable LLM providers."""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Defines the minimal interface exposed by all LLM providers."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Sends one prompt to the provider and returns the raw text response."""
