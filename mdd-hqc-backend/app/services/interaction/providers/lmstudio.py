"""LM Studio provider implementation for interaction analyzers."""

import requests

from app.core.config import config

from .base import LLMProvider


class LMStudioProvider(LLMProvider):
    """Calls the LM Studio completions API and returns the raw model response."""

    def __init__(self):
        self.url = config.LMSTUDIO_URL
        self.model_name = config.LMSTUDIO_MODEL
        self.temperature = config.LLM_TEMPERATURE
        self.timeout = config.LLM_TIMEOUT

    def generate(self, prompt: str) -> str:
        response = requests.post(
            self.url,
            json={
                "model": self.model_name,
                "prompt": prompt,
                "temperature": self.temperature,
                "max_tokens": 512,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()

        response_data = response.json()
        choices = response_data.get("choices", [])
        if not choices:
            return ""

        first_choice = choices[0]
        generated_text = first_choice.get("text") or ""
        return generated_text.strip()
