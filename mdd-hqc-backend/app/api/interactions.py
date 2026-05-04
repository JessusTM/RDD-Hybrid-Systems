"""Interaction endpoints that expose clarification utilities for UVL drafts."""

from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.api.schemas.path import PathRequest
from app.services.interaction.contracts import InteractionInput, InteractionReport
from app.services.artifacts.uvl_service import UvlService
from app.services.interaction.service import run_interaction

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
        output_uvl_content = uvl_path.read_text(encoding="utf-8")
        payload = InteractionInput(
            output_uvl_path=str(uvl_path),
            output_uvl_content=output_uvl_content,
        )
        report = run_interaction(payload)
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
        output_uvl_content = uvl_path.read_text(encoding="utf-8")
        service = UvlService()
        subfunciones = service.extract_functionality_names(output_uvl_content)
        return {f"subfuncion_{i + 1}": nombre for i, nombre in enumerate(subfunciones)}

    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
