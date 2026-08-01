"""OpenRouter provider implementation for interaction analyzers."""

import json
import logging

import requests

from app.core.config import config

from .base import LLMProvider

logger = logging.getLogger(__name__)


class OpenRouterProvider(LLMProvider):
    """Calls the OpenRouter chat completions API and returns the raw model response."""

    def __init__(self):
        self.api_key = config.OPENROUTER_API_KEY
        self.model_name = config.OPENROUTER_MODEL
        self.url = config.OPENROUTER_URL
        self.temperature = config.LLM_TEMPERATURE
        self.timeout = config.LLM_TIMEOUT

    def generate(self, prompt: str) -> str:
        from app.services.interaction.service import cancellation_context

        cancellation_event = cancellation_context.get()
        if cancellation_event and cancellation_event.is_set():
            return ""

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
            "stream": True,
        }
        content_parts = []

        with requests.post(
            self.url,
            headers=headers,
            json=payload,
            timeout=self.timeout,
            stream=True,
        ) as response:
            response.raise_for_status()

            for line in response.iter_lines(decode_unicode=True):
                if cancellation_event and cancellation_event.is_set():
                    logger.info("OpenRouter stream closed after request cancellation.")
                    response.close()
                    return ""

                if not line or not line.startswith("data:"):
                    continue

                data = line.removeprefix("data:").strip()
                if data == "[DONE]":
                    break

                try:
                    chunk = json.loads(data)
                except json.JSONDecodeError:
                    logger.debug("Ignored invalid OpenRouter stream chunk.")
                    continue

                choices = chunk.get("choices", [])
                if not choices:
                    continue

                text = choices[0].get("delta", {}).get("content")
                if text:
                    content_parts.append(text)

        return "".join(content_parts).strip()
