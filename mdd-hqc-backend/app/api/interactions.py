"""Interaction endpoints that expose clarification utilities for UVL drafts."""

import asyncio
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request

from app.api.schemas.path import PathRequest
from app.models.llm_contract import InteractionInput, InteractionReport
from app.models.llm_contract import UvlModel
from app.services.artifacts.uvl_service import UvlService
from app.services.interaction.service import run_interaction

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("/report", response_model=InteractionReport)
async def get_interaction_report(path_req: PathRequest, request: Request):
    """Builds the interaction report for the UVL file referenced by the request path.

    This endpoint loads the current UVL draft and runs the interaction workflow so the
    caller can inspect pending questions or proposals.

    CANCELLATION SUPPORT:
    If the user reloads the page or closes the tab, the frontend's AbortController 
    will trigger a disconnection that this endpoint captures to stop LLM processing.
    """
    uvl_path = Path(path_req.path)
    if not uvl_path.exists():
        raise HTTPException(status_code=404, detail=f"No se encontró UVL en {uvl_path}")

    try:
        if await request.is_disconnected():
            print(f"DEBUG: Cliente desconectado antes de procesar {path_req.path}")
            return

        uvl_content = uvl_path.read_text(encoding="utf-8")
        service = UvlService()
        uvl_dict = service.parse_uvl_to_dict(uvl_content)
        uvl_model = UvlModel(**uvl_dict)

        payload = InteractionInput(nodes=[], links=[], uvl=uvl_model)
        
        report = await run_interaction(payload)
        
        return report

    except asyncio.CancelledError:
        print(f"DEBUG: Generación de reporte cancelada por el usuario: {path_req.path}")
        raise 

    except Exception as exc:
        print(f"ERROR en get_interaction_report: {str(exc)}")
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/functionality-names")
async def get_functionality_names(path_req: PathRequest):
    """Returns the direct functionality names extracted from the requested UVL file.

    This endpoint exposes a lightweight view of the functionality block so the caller can
    reuse the declared names without parsing the whole UVL artifact.
    """
    uvl_path = Path(path_req.path)
    if not uvl_path.exists():
        raise HTTPException(status_code=404, detail=f"No se encontró UVL en {uvl_path}")

    try:
        uvl_content = uvl_path.read_text(encoding="utf-8")
        service = UvlService()
        subfunciones = service.extract_functionality_names(uvl_content)
        return {f"subfuncion_{i + 1}": nombre for i, nombre in enumerate(subfunciones)}

    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    