"""Interaction endpoints that expose clarification utilities for UVL drafts."""

import asyncio
import logging
from pathlib import Path
from threading import Event

from fastapi import APIRouter, HTTPException, Request

from app.api.schemas.path import PathRequest
from app.services.interaction.contracts import InteractionInput, InteractionReport
from app.services.artifacts.uvl_service import UvlService
from app.services.interaction.security import security_shield
from app.services.interaction.service import cancellation_context, run_interaction
from app.api.schemas.answers import AnswerRequest
from app.models.uvl import UVL

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("/report", response_model=InteractionReport)
async def get_interaction_report(request: PathRequest, http_request: Request):
    """Builds the interaction report for the UVL file referenced by the request path.

    This endpoint loads the current UVL draft and runs the interaction workflow so the
    caller can inspect pending questions or proposals.
    """
    uvl_path = Path(request.path)
    if not uvl_path.exists():
        raise HTTPException(status_code=404, detail=f"No se encontró UVL en {uvl_path}")

    client_ip = http_request.client.host if http_request.client else "unknown"
    if not security_shield.check_request(
        ip=client_ip,
        endpoint="/interactions/report",
        path=str(uvl_path),
    ):
        raise HTTPException(status_code=429, detail="Too Many Requests.")

    cancellation_event = Event()
    token = cancellation_context.set(cancellation_event)
    task = None

    try:
        output_uvl_content = uvl_path.read_text(encoding="utf-8")
        payload = InteractionInput(
            output_uvl_path=str(uvl_path),
            output_uvl_content=output_uvl_content,
        )
        task = asyncio.create_task(asyncio.to_thread(run_interaction, payload))

        while not task.done():
            if await http_request.is_disconnected():
                cancellation_event.set()
                task.cancel()
                logger.info("Interaction report cancelled after client disconnect.")
                raise asyncio.CancelledError
            await asyncio.sleep(0.2)

        return await task

    except asyncio.CancelledError:
        cancellation_event.set()
        if task:
            task.cancel()
        raise
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        cancellation_context.reset(token)


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


@router.post("/answers")
async def save_user_answers(request: AnswerRequest):
    """Acknowledges answers for a generated UVL without modifying the model yet."""
    uvl_path = Path(request.path).resolve()
    generated_data_dir = UVL.FILE_NAME.parent.resolve()

    if uvl_path.suffix.lower() != ".uvl" or not uvl_path.is_relative_to(
        generated_data_dir
    ):
        raise HTTPException(status_code=400, detail="La ruta UVL no es válida")
    if not uvl_path.is_file():
        raise HTTPException(status_code=404, detail=f"No se encontró UVL en {uvl_path}")

    try:
        return {
            "detail": "Respuestas recibidas correctamente",
            "answers": request.answers,
            "output_uvl": str(uvl_path),
            "uvl_content": uvl_path.read_text(encoding="utf-8"),
        }

    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
