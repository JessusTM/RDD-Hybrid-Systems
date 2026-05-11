"""Factory helpers that instantiate the configured LLM interaction client."""

import logging
from .ollama_client import OllamaClient
from .lmstudio_client import LMStudioClient
from .openrouter_client import OpenRouterClient
from app.core.config import config

logger = logging.getLogger(__name__)

def get_llm_client(provider: str = None):
    """
    Retorna el cliente LLM según el proveedor indicado.
    
    Orden de prioridad:
    1. El parámetro 'provider' si se pasa explícitamente a la función.
    2. El valor de LLM_PROVIDER definido en el archivo .env
    3. 'lmstudio' como valor por defecto si no hay nada configurado.
    """
    
    # Determinamos el proveedor final
    active_provider = provider or config.LLM_PROVIDER or "lmstudio"
    active_provider = active_provider.strip().lower()

    # Logs de depuración en consola de Docker
    print(f"\n--- [LLM FACTORY DEBUG] ---")
    print(f"Argumento recibido: {provider}")
    print(f"Configuración .env: {config.LLM_PROVIDER}")
    print(f"Resultado final: {active_provider}")
    print(f"---------------------------\n")

    logger.info(f"Instanciando cliente LLM para el proveedor: {active_provider}")

    if active_provider == "lmstudio":
        return LMStudioClient(
            base_url=config.LMSTUDIO_BASE_URL,
            model_name=config.LMSTUDIO_MODEL_NAME
        )

    elif active_provider == "openrouter":
        return OpenRouterClient(
            api_key=config.OPENROUTER_API_KEY, 
            model_name=config.OPENROUTER_MODEL_NAME
        )

    elif active_provider == "ollama":
        logger.warning("Iniciando cliente Ollama (Puerto 11434 por defecto)")
        return OllamaClient(model_name="mistral:latest")

    else:
        logger.error(f"Proveedor desconocido: '{active_provider}'. Usando LM Studio por defecto.")
        return LMStudioClient(
            base_url=config.LMSTUDIO_BASE_URL,
            model_name=config.LMSTUDIO_MODEL_NAME
        )