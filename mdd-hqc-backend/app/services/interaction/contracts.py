"""Shared contracts for interaction analysis inputs and outputs."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel


class InteractionInput(BaseModel):
    """Bundles the generated artifact inputs required by one interaction run.

    This model gives the interaction layer the generated UVL artifact it must analyze
    without coupling the analyzer to filesystem reads performed by the API layer.
    """

    output_uvl_path: Optional[str] = None
    output_uvl_content: str


QuestionScope = Literal[
    "missing_information",
    "classification_disambiguation",
    "consistency_check",
    "other",
]


class InteractionQuestion(BaseModel):
    """Represents one clarification question emitted by the interaction flow.

    This model keeps the user-facing text and answer metadata together so the
    frontend can present pending decisions in a consistent format.
    """

    id: str
    text: str
    scope: QuestionScope = "other"
    options: Optional[List[str]] = None
    answers: Optional[str] = None


ProposalKind = Literal[
    "move_feature_category",
    "add_feature",
    "add_attribute",
    "add_constraint",
    "add_or_group_child",
    "add_comment",
]


class InteractionProposal(BaseModel):
    """Represents one suggested change to the UVL draft.

    This model packages the proposed action, target, and rationale so the user can
    review structured updates before they are applied to the backend model.
    """

    id: str
    kind: ProposalKind
    target: Dict[str, Any] = {}
    data: Dict[str, Any] = {}
    rationale: str


class InteractionReport(BaseModel):
    """Collects the questions and proposals produced by one interaction pass.

    This model is the final payload returned by the interaction layer so callers can
    inspect both missing information and suggested UVL adjustments together.
    """

    questions: List[InteractionQuestion] = []
    proposals: List[InteractionProposal] = []
