"""Service helpers that select and run the backend interaction engines."""

import asyncio
from typing import Dict
from app.models.llm_contract import InteractionInput, InteractionReport
from app.services.interaction.llm_client import LLMInteractionEngine
from app.services.interaction.rule_based import RuleBasedInteractionEngine
from app.services.interaction.llm.factory import get_llm_client
from app.models.uvl import UVL


# ====== Public API ======
# Functions below select the interaction engine and apply the resulting user decisions.


async def get_interaction_engine(provider: str = None) -> object:
    """Returns the interaction engine that matches the requested provider.

    CUIDADO: Se ha cambiado el default a None para que la factory decida 
    basándose en el archivo .env si no se especifica uno.
    """

    if provider == "rule_based":
        return RuleBasedInteractionEngine()

    if provider is None or provider in ["ollama", "lmstudio", "openrouter"]:
        llm_client = get_llm_client(provider)
        return LLMInteractionEngine(llm_client)

    return RuleBasedInteractionEngine()


async def run_interaction(
    payload: InteractionInput, provider: str = None
) -> InteractionReport:
    """Runs the interaction flow with the selected provider and returns its report.

    Se elimina el hardcode de 'openrouter' para permitir flexibilidad total.
    """
    try:
        engine = await get_interaction_engine(provider)
        
        return await engine.run(payload)

    except asyncio.CancelledError:
        print(f"DEBUG: [Service] Cancelando ejecución de interacción para el proveedor: {provider}")
        raise


def apply_user_answers(uvl: UVL, answers: Dict) -> str:
    """Applies the provided answers to the UVL model and returns the saved text."""

    for block, value in answers.items():
        category = (
            f"@{block}" if f"@{block}" in uvl.allowed_categories else "@Functionality"
        )
        uvl.add_feature(name=value, category=category)

    uvl.create_file()

    if uvl.FILE_NAME.exists():
        return uvl.FILE_NAME.read_text(encoding="utf-8")
    return ""
