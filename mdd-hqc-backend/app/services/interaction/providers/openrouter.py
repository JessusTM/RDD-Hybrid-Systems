"""OpenRouter provider implementation for interaction analyzers."""

import requests

from app.core.config import config

from .base import LLMProvider


class OpenRouterProvider(LLMProvider):
    """Calls the OpenRouter chat completions API and returns the raw model response."""

    def __init__(self):
        self.api_key = config.OPENROUTER_API_KEY
        self.model_name = config.OPENROUTER_MODEL
        self.url = config.OPENROUTER_URL
        self.temperature = config.LLM_TEMPERATURE
        self.timeout = config.LLM_TIMEOUT

    def generate(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://mdd-hqc.project",
            "X-Title": "MDD-HQC Transformation Engine",
        }
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
        }
        response = requests.post(
            self.url,
            headers=headers,
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()

        response_data = response.json()
        choices = response_data.get("choices", [])
        if not choices:
            return ""

        first_choice = choices[0]
        message = first_choice.get("message", {})
        content = message.get("content", "")
        return content.strip()
