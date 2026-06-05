"""Transformation endpoints that expose the CIM, PIM, and PSM flows."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.api.schemas.path import PathRequest
from app.models.uvl import UVL

from app.services.artifacts.xml_service import XmlService
from app.services.artifacts.uvl_service import UvlService
from app.services.artifacts.plantuml_service import PlantumlService

from app.services.transformations.cim_to_pim import CimToPim
from app.services.transformations.pim_to_psm import PimToPsm

from app.services.metrics.istar_metrics import IstarMetricsService
from app.services.metrics.uvl_metrics import UvlMetricsService
from app.services.metrics.uml_metrics import UmlMetricsService


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/transformations", tags=["transformations"])


def _run_cim_to_pim(input_path: str) -> tuple[XmlService, UVL]:
    """Builds the PIM UVL model from a CIM XML artifact."""
    xml_service = XmlService(input_path)
    uvl_service = UvlService()
    uvl = UVL()

    cim_to_pim = CimToPim(xml_service=xml_service, uvl_service=uvl_service, uvl=uvl)
    cim_to_pim.apply_r1()
    cim_to_pim.apply_r2()
    cim_to_pim.apply_r4()
    cim_to_pim.apply_r5()
    cim_to_pim.apply_r3()
    return xml_service, uvl


def _load_uvl_from_file(uvl_path: Path) -> UVL:
    """Loads the backend UVL text format into the in-memory UVL model."""
    uvl = UVL()
    lines = uvl_path.read_text(encoding="utf-8").splitlines()

    section = None
    current_category = None
    current_subgroup = None
    pending_metadata: list[str] = []
    feature_stack: list[tuple[int, str]] = []
    group_parent_by_indent: dict[int, str] = {}
    last_feature = None

    category_by_label = {
        "Functionality": "@Functionality",
        "Algorithm": "@Algorithm",
        "Programming": "@Programming",
        "Integration_model": "@Integration_model",
        "Quantum_HW_constraint": "@Quantum_HW_constraint",
    }
    subgroups = {"Classical", "Quantum"}

    def close_stack(indent: int) -> None:
        while feature_stack and feature_stack[-1][0] >= indent:
            feature_stack.pop()

    def parent_for(indent: int) -> str | None:
        candidates = [
            group_indent for group_indent in group_parent_by_indent if group_indent < indent
        ]
        if candidates:
            return group_parent_by_indent[max(candidates)]
        if feature_stack:
            return feature_stack[-1][1]
        return None

    for raw_line in lines:
        stripped = raw_line.strip()
        indent = len(raw_line) - len(raw_line.lstrip(" "))

        if not stripped:
            continue
        if stripped == "features":
            section = "features"
            continue
        if stripped == "constraints":
            section = "constraints"
            current_category = None
            current_subgroup = None
            feature_stack.clear()
            group_parent_by_indent.clear()
            last_feature = None
            continue

        if section == "constraints":
            uvl.add_constraint(stripped)
            continue

        if section != "features":
            continue

        if stripped.startswith("#"):
            pending_metadata.append(stripped[1:].strip())
            continue

        if stripped in category_by_label:
            current_category = category_by_label[stripped]
            current_subgroup = None
            feature_stack.clear()
            group_parent_by_indent.clear()
            last_feature = None
            continue

        if current_category == "@Algorithm" and stripped in subgroups:
            current_subgroup = stripped
            feature_stack.clear()
            group_parent_by_indent.clear()
            last_feature = None
            continue

        if stripped in {"mandatory", "or"}:
            if last_feature is not None:
                group_parent_by_indent[indent] = last_feature
            continue

        if stripped in {"{", "}"}:
            continue

        if stripped.startswith("kind "):
            if last_feature is not None:
                kind = (
                    stripped.split('"', maxsplit=2)[1]
                    if '"' in stripped
                    else stripped.split(maxsplit=1)[1]
                )
                feature = uvl.get_feature(last_feature)
                if feature is not None:
                    feature.kind = kind
            continue

        close_stack(indent)
        parent_name = parent_for(indent)
        feature = uvl.add_feature(
            category=current_category or "@Functionality",
            metadata=pending_metadata,
            name=stripped,
            kind=None,
            subgroup=current_subgroup,
        )
        pending_metadata = []

        if parent_name:
            uvl.add_mandatory_child(parent_name, feature.name)

        feature_stack.append((indent, feature.name))
        last_feature = feature.name

    return uvl


@router.post("/cim-to-pim")
async def transform_cim_pim(request: PathRequest):
    """Runs the CIM-to-PIM flow and returns the generated UVL artifact plus metrics.

    This endpoint parses the source XML, applies the CIM-to-PIM rules, and exposes the
    resulting UVL model together with the relevant CIM and PIM summaries.
    """
    logger.info("CIM-to-PIM transformation requested: input_path=%s", request.path)
    try:
        xml_service, uvl = _run_cim_to_pim(request.path)

        istar_metrics = IstarMetricsService(xml_service).calculate()
        uvl.create_file()

        uvl_metrics = UvlMetricsService(uvl).calculate()

        output_uvl_content = ""
        if uvl.FILE_NAME.exists():
            output_uvl_content = uvl.FILE_NAME.read_text(encoding="utf-8")

        logger.info(
            "CIM-to-PIM transformation completed: input_path=%s, output_uvl_path=%s, features=%s",
            request.path,
            uvl.FILE_NAME,
            uvl_metrics.get("total_features"),
        )
        return {
            "detail": "Transformación CIM -> PIM completada",
            "input_xml": request.path,
            "output_uvl_path": str(uvl.FILE_NAME),
            "output_uvl_content": output_uvl_content,
            "metrics": {"cim": istar_metrics, "pim": uvl_metrics},
        }
    except Exception as exc:
        logger.error(
            "CIM-to-PIM transformation failed: input_path=%s, error=%s",
            request.path,
            exc,
            exc_info=True,
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/cim-to-psm")
async def transform_cim_psm(request: PathRequest):
    """Runs the full CIM-to-PSM flow and returns the UVL and PlantUML artifacts.

    This endpoint parses the source XML, generates the PIM UVL model, and then renders
    the final UML artifact from that PIM model.
    """
    logger.info("CIM-to-PSM transformation requested: input_path=%s", request.path)
    try:
        xml_service, uvl = _run_cim_to_pim(request.path)

        istar_metrics = IstarMetricsService(xml_service).calculate()
        uvl.create_file()

        uvl_metrics = UvlMetricsService(uvl).calculate()

        pim_to_psm = PimToPsm(uvl)
        uml_model = pim_to_psm.transform()

        uml_metrics = UmlMetricsService(uml_model).calculate()

        uml_output = Path("data/model.puml")
        plantuml_service = PlantumlService()
        uml_path = plantuml_service.write(uml_model, uml_output)

        output_uvl_content = ""
        if uvl.FILE_NAME.exists():
            output_uvl_content = uvl.FILE_NAME.read_text(encoding="utf-8")

        uml_content = ""
        if uml_path.exists():
            uml_content = uml_path.read_text(encoding="utf-8")

        logger.info(
            "CIM-to-PSM transformation completed: input_path=%s, output_uvl_path=%s, output_puml=%s, classes=%s",
            request.path,
            uvl.FILE_NAME,
            uml_path,
            uml_metrics.get("total_classes"),
        )
        return {
            "detail": "Transformación CIM -> PSM completada",
            "input_xml": request.path,
            "output_uvl_path": str(uvl.FILE_NAME),
            "output_puml": str(uml_path),
            "output_uvl_content": output_uvl_content,
            "puml_content": uml_content,
            "metrics": {
                "cim": istar_metrics,
                "pim": uvl_metrics,
                "psm": uml_metrics,
            },
        }
    except Exception as exc:
        logger.error(
            "CIM-to-PSM transformation failed: input_path=%s, error=%s",
            request.path,
            exc,
            exc_info=True,
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/pim-to-psm")
async def transform_pim_psm(request: PathRequest):
    """Runs the PIM-to-PSM flow from an existing UVL artifact."""
    logger.info("PIM-to-PSM transformation requested: input_path=%s", request.path)
    try:
        uvl_path = Path(request.path)
        if not uvl_path.exists():
            raise HTTPException(status_code=404, detail=f"No se encontró UVL en {uvl_path}")

        uvl = _load_uvl_from_file(uvl_path)
        uvl_metrics = UvlMetricsService(uvl).calculate()

        pim_to_psm = PimToPsm(uvl)
        uml_model = pim_to_psm.transform()
        uml_metrics = UmlMetricsService(uml_model).calculate()

        uml_output = Path("data/model.puml")
        plantuml_service = PlantumlService()
        uml_path = plantuml_service.write(uml_model, uml_output)

        uml_content = ""
        if uml_path.exists():
            uml_content = uml_path.read_text(encoding="utf-8")

        logger.info(
            "PIM-to-PSM transformation completed: input_path=%s, output_puml=%s, classes=%s",
            request.path,
            uml_path,
            uml_metrics.get("total_classes"),
        )
        return {
            "detail": "Transformación PIM -> PSM completada",
            "input_uvl": request.path,
            "output_puml": str(uml_path),
            "puml_content": uml_content,
            "metrics": {"pim": uvl_metrics, "psm": uml_metrics},
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            "PIM-to-PSM transformation failed: input_path=%s, error=%s",
            request.path,
            exc,
            exc_info=True,
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
