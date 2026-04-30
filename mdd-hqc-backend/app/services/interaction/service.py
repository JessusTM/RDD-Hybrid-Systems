"""Service helpers that run optional LLM-backed interaction analysis on generated UVL."""

from typing import Dict, Optional

from app.models.llm_contract import InteractionInput, InteractionReport
from app.models.uvl import UVL
from app.services.interaction.analyzers.uvl_completeness import UvlCompletenessAnalyzer
from app.services.interaction.providers.factory import get_provider
from app.services.interaction.questions import build_questions_from_missing


def run_interaction(
    payload: InteractionInput, provider: Optional[str] = None
) -> InteractionReport:
    """Runs the UVL interaction analysis with the selected provider and returns its report.

    This helper keeps provider selection, UVL analysis, and question generation in one
    shared entry point used by the API layer.
    """
    llm_provider = get_provider(provider)
    analyzer = UvlCompletenessAnalyzer(llm_provider)
    analysis = analyzer.analyze(payload)
    questions = build_questions_from_missing(analysis.get("missing", []))
    return InteractionReport(questions=questions, proposals=[])


def apply_user_answers(uvl: UVL, answers: Dict) -> str:
    """Placeholder kept for future UVL updates after the guided interaction step.

    Applying user answers back into the generated UVL is intentionally left out of the
    current phase, where the interaction module only analyzes artifacts.
    """
    raise NotImplementedError(
        "Applying user answers back into the UVL is not implemented in this phase."
    )
