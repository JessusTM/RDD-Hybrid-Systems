"""Ollama provider implementation for interaction analyzers."""

import requests

from app.core.config import config

from .base import LLMProvider


class OllamaProvider(LLMProvider):
    """Calls the Ollama generation API and returns the raw model response."""

    def __init__(self):
        self.url = config.OLLAMA_URL
        self.model_name = config.OLLAMA_MODEL
        self.temperature = config.LLM_TEMPERATURE
        self.timeout = config.LLM_TIMEOUT

    def generate(self, prompt: str) -> str:
        response = requests.post(
            self.url,
            json={
                "model": self.model_name,
                "prompt": prompt,
                "options": {"temperature": self.temperature},
                "stream": False,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        response_data = response.json()
        generated_text = response_data.get("response", "")
        return generated_text.strip()
