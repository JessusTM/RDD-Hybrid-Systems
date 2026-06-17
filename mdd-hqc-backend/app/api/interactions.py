"""Interaction endpoints that expose clarification utilities for UVL drafts."""

import asyncio
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

from app.api.schemas.path import PathRequest
from app.services.interaction.contracts import InteractionInput, InteractionReport
from app.services.artifacts.uvl_service import UvlService
from app.services.interaction.service import run_interaction, cancellation_context
from app.services.interaction.security import security_shield

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("/report", response_model=InteractionReport)
async def get_interaction_report(request: PathRequest, fastapi_request: Request):
    """Builds the interaction report for the UVL file referenced by the request path.

    This endpoint loads the current UVL draft and runs the interaction workflow so the
    caller can inspect pending questions or proposals.
    """
    uvl_path = Path(request.path)
    
    client_ip = fastapi_request.client.host if fastapi_request.client else "127.0.0.1"
    endpoint_name = "/interactions/report"
    is_allowed = security_shield.check_request(ip=client_ip, endpoint=endpoint_name, path=str(uvl_path))

    if not is_allowed:
        raise HTTPException(status_code=429, detail="Too Many Requests.")

    if not uvl_path.exists():
        raise HTTPException(status_code=404, detail=f"No se encontró UVL")

    client_ip = fastapi_request.client.host if fastapi_request.client else "127.0.0.1"
    endpoint_name = "/interactions/report"

    is_allowed = security_shield.check_request(
        ip=client_ip, 
        endpoint=endpoint_name, 
        path=str(uvl_path)
    )

    if not is_allowed:
        raise HTTPException(
            status_code=429, 
            detail="Too Many Requests. Límite de frecuencia excedido o solicitud duplicada inmediata."
        )

    ctx = {"is_cancelled": False}
    cancellation_context.set(ctx)

    try:
        payload = InteractionInput(
            output_uvl_path=str(uvl_path),
            output_uvl_content=output_uvl_content,
        )
        
        loop = asyncio.get_running_loop()
        task = loop.run_in_executor(None, run_interaction, payload)
        
        while not task.done():
            if await fastapi_request.is_disconnected():
                ctx["is_cancelled"] = True
                task.cancel()
                logger.warning("Client disconnected from interaction report generation flow.")
                raise asyncio.CancelledError()
            await asyncio.sleep(0.2)
            
        report = await task
        return report

    except asyncio.CancelledError:
        logger.warning("Request execution cancelled natively due to user connection loss.")
        raise
    except Exception as exc:
        logger.error("Error during interaction report generation: %s", str(exc), exc_info=True)
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
        sub_elements = service.get_functionality_sub_elements(output_uvl_content)
        return {"names": sub_elements}

    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc