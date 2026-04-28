"""Interaction endpoints that expose clarification utilities for UVL drafts."""

from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.api.schemas.path import PathRequest
from app.models.llm_contract import InteractionInput, InteractionReport
from app.models.llm_contract import UvlModel
from app.services.artifacts.uvl_service import UvlService
from app.services.interaction.service import run_interaction
from app.services.interaction.service import apply_user_answers
from app.api.schemas.answers import AnswerRequest
from app.models.uvl import UVL

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("/report", response_model=InteractionReport)
async def get_interaction_report(request: PathRequest):
    """Builds the interaction report for the UVL file referenced by the request path.

    This endpoint loads the current UVL draft and runs the interaction workflow so the
    caller can inspect pending questions or proposals.
    """
    uvl_path = Path(request.path)
    if not uvl_path.exists():
        raise HTTPException(status_code=404, detail=f"No se encontró UVL en {uvl_path}")

    try:
        uvl_content = uvl_path.read_text(encoding="utf-8")
        service = UvlService()
        uvl_dict = service.parse_uvl_to_dict(uvl_content)
        uvl_model = UvlModel(**uvl_dict)

        payload = InteractionInput(nodes=[], links=[], uvl=uvl_model)
        report = run_interaction(payload, provider="ollama")
        return report

    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/functionality-names")
async def get_functionality_names(request: PathRequest):
    """Returns the direct functionality names extracted from the requested UVL file.

    This endpoint exposes a lightweight view of the functionality block so the caller can
    reuse the declared names without parsing the whole UVL artifact.
    """
    uvl_path = Path(request.path)
    if not uvl_path.exists():
        raise HTTPException(status_code=404, detail=f"No se encontró UVL en {uvl_path}")

    try:
        uvl_content = uvl_path.read_text(encoding="utf-8")
        service = UvlService()
        subfunciones = service.extract_functionality_names(uvl_content)
        return {f"subfuncion_{i + 1}": nombre for i, nombre in enumerate(subfunciones)}

    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    
@router.post("/answers")
async def save_user_answers(request: AnswerRequest):
    """Applies user-selected answers to the UVL model and returns the updated content."""
    uvl_path = Path(request.path)
    if not uvl_path.exists():
        raise HTTPException(status_code=404, detail=f"No se encontró UVL en {uvl_path}")

    try:
        uvl = UVL(file_path=str(uvl_path))
        updated_content = apply_user_answers(uvl, request.answers)

        return {
            "detail": "Respuestas aplicadas exitosamente",
            "output_uvl": str(UVL.FILE_NAME),
            "uvl_content": updated_content
        }

    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
