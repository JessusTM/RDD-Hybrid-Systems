"""Service helpers that run optional LLM-backed interaction analysis on generated UVL."""

import logging
from contextvars import ContextVar
from threading import Event
from typing import Dict, Optional

from app.services.interaction.contracts import InteractionInput, InteractionReport
from app.models.uvl import UVL
from app.services.interaction.analyzers.uvl_completeness import UvlCompletenessAnalyzer
from app.services.interaction.providers.factory import get_provider
from app.services.interaction.questions import build_questions_from_missing

logger = logging.getLogger(__name__)

cancellation_context: ContextVar[Event | None] = ContextVar(
    "cancellation_context", default=None
)


def run_interaction(
    payload: InteractionInput, provider: Optional[str] = None
) -> InteractionReport:
    """Runs the UVL interaction analysis with the selected provider and returns its report.

    This helper keeps provider selection, UVL analysis, and question generation in one
    shared entry point used by the API layer.
    """
    cancellation_event = cancellation_context.get()
    if cancellation_event and cancellation_event.is_set():
        raise RuntimeError("Operation cancelled by user.")

    llm_provider = get_provider(provider)
    analyzer = UvlCompletenessAnalyzer(llm_provider)
    analysis = analyzer.analyze(payload)

    if cancellation_event and cancellation_event.is_set():
        raise RuntimeError("Operation cancelled by user.")

    questions = build_questions_from_missing(analysis.get("missing", []))

    logger.debug("Interaction analysis result: %s", analysis)
    logger.info(
        "Interaction questions generated: provider=%s, question_count=%s",
        provider or "configured-default",
        len(questions),
    )

    return InteractionReport(questions=questions, proposals=[])


def apply_user_answers(uvl: UVL, answers: Dict) -> str:
    """Placeholder kept for future UVL updates after the guided interaction step.

    Applying user answers back into the generated UVL is intentionally left out of the
    current phase, where the interaction module only analyzes artifacts.
    """
    raise NotImplementedError(
        "Applying user answers back into the UVL is not implemented in this phase."
    )
