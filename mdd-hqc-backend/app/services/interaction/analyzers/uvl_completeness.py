"""UVL completeness analyzer backed by one pluggable LLM provider."""

import json
import re
from typing import Dict

from app.models.llm_contract import InteractionInput
from app.services.interaction.providers.base import LLMProvider

HQC_EXTENDED_FEATURE_MODEL = [
    "Functionality",
    "Algorithm",
    "Programming",
    "Integration_model",
    "Quantum_HW_constraint",
]

PROMPT_TEMPLATE = """
Analiza el siguiente modelo UVL y responde SOLO con un JSON valido con las claves exactas:
Functionality, Algorithm, Programming, Integration_model, Quantum_HW_constraint, missing.

No uses otras claves como questions o proposals.
No incluyas explicaciones, comentarios ni texto adicional fuera del JSON.

Objetivo del analisis:
- Revisar solo la completitud de los grupos principales del modelo de caracteristicas extendido para sistemas hibridos cuantico-clasicos.
- Determinar si el UVL contiene evidencia suficiente de los grupos principales: Functionality, Algorithm, Programming, Integration_model y Quantum_HW_constraint.
- Si no hay evidencia textual de un grupo principal en el UVL, marca false y agregalo a missing.

Reglas de interpretacion:
- Functionality=true si existe evidencia del grupo Functionality en el UVL.
- Algorithm=true si existe evidencia del grupo Algorithm en el UVL.
- Programming=true si existe evidencia del grupo Programming en el UVL.
- Integration_model=true si existe evidencia del grupo Integration_model en el UVL.
- Quantum_HW_constraint=true si existe evidencia del grupo Quantum_HW_constraint en el UVL.
- missing debe contener TODAS las claves anteriores que esten en false.

Formato de salida:
{{
  "Functionality": true|false,
  "Algorithm": true|false,
  "Programming": true|false,
  "Integration_model": true|false,
  "Quantum_HW_constraint": true|false,
  "missing": ["..."]
}}

UVL a analizar:
{uvl_content}
""".strip()


class UvlCompletenessAnalyzer:
    """Builds one UVL completeness prompt and normalizes the LLM response."""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def analyze(self, payload: InteractionInput) -> Dict:
        prompt = PROMPT_TEMPLATE.format(uvl_content=payload.output_uvl_content)
        raw_response = self.provider.generate(prompt)
        return self._safe_parse_json(raw_response)

    def _safe_parse_json(self, raw: str) -> Dict:
        try:
            parsed = json.loads(raw)
        except Exception:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not match:
                return {}
            try:
                parsed = json.loads(match.group(0))
            except Exception:
                return {}

        if not self._contains_all_required_keys(parsed):
            return {}

        result = self._build_boolean_result(parsed)
        missing = parsed.get("missing", [])
        result["missing"] = missing if isinstance(missing, list) else []
        if not result["missing"]:
            result["missing"] = self._collect_missing_groups(result)
        return result

    def _contains_all_required_keys(self, parsed: Dict) -> bool:
        for required_key in HQC_EXTENDED_FEATURE_MODEL:
            if required_key not in parsed:
                return False
        return True

    def _build_boolean_result(self, parsed: Dict) -> Dict:
        result: Dict = {}
        for group_name in HQC_EXTENDED_FEATURE_MODEL:
            result[group_name] = bool(parsed.get(group_name, False))
        return result

    def _collect_missing_groups(self, result: Dict) -> list[str]:
        missing_groups: list[str] = []
        for group_name in HQC_EXTENDED_FEATURE_MODEL:
            if not result.get(group_name, False):
                missing_groups.append(group_name)
        return missing_groups
