"""OpenRouter provider implementation for interaction analyzers."""

import json  # AÑADIDO: Requerido para procesar los fragmentos JSON del streaming
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
        # Local import to safely break the circular dependency chain during startup
        from app.services.interaction.service import cancellation_context
        
        ctx = cancellation_context.get()
        if ctx and ctx.get("is_cancelled"):
            logger.warning("OpenRouter generation aborted before request due to user cancellation.")
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
            "stream": True,  # CORREGIDO: Activamos streaming nativo en OpenRouter
        }
        
        full_content = ""
        try:
            # CORREGIDO: Se añade stream=True para evitar el bloqueo síncrono absoluto del hilo
            response = requests.post(
                self.url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
                stream=True,
            )
            response.raise_for_status()
            
            # CORREGIDO: Procesamos la respuesta en tiempo real línea por línea (SSE)
            for line in response.iter_lines(decode_unicode=True):
                # EVALUACIÓN DINÁMICA: Consultamos el contexto en medio de la transferencia de datos
                dynamic_ctx = cancellation_context.get()
                if dynamic_ctx and dynamic_ctx.get("is_cancelled"):
                    logger.warning(
                        "OpenRouter request interrupted mid-stream due to user cancellation. "
                        "Closing network socket immediately to save tokens!"
                    )
                    response.close()  # CORREGIDO: Corta la conexión de red con OpenRouter YA
                    return ""

                if not line:
                    continue
                
                # OpenRouter envía las respuestas en formato Server-Sent Events (data: {...})
                if line.startswith("data: "):
                    data_str = line[6:].strip()
                    
                    # OpenRouter avisa que terminó enviando la palabra clave [DONE]
                    if data_str == "[DONE]":
                        break
                    
                    try:
                        data_json = json.loads(data_str)
                        choices = data_json.get("choices", [])
                        if choices:
                            # En modo streaming, el texto acumulado viaja en 'delta' en vez de 'message'
                            delta = choices[0].get("delta", {})
                            content = delta.get("content", "")
                            full_content += content
                    except Exception:
                        continue  # Ignoramos líneas de control o vacías transitorias

        except Exception as exc:
            if ctx and ctx.get("is_cancelled"):
                logger.warning("OpenRouter request interrupted or failed due to user cancellation.")
                return ""
            logger.error("OpenRouter request failed: %s", str(exc))
            raise

        if ctx and ctx.get("is_cancelled"):
            logger.warning("OpenRouter generation aborted after request due to user cancellation.")
            return ""

        return full_content