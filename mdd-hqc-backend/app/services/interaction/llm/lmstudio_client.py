"""LM Studio client used to infer missing HQC evidence from iStar elements."""

import requests
from typing import Dict, List
import json
import re
import asyncio  # Libería para manejar la ejecución asíncrona
from app.models.llm_contract import CimNode
from app.services.interaction.llm.base import LLMInterface

class LMStudioClient(LLMInterface):
    """Calls LM Studio to analyze iStar elements for the interaction workflow.

    This client adapts the backend interaction contract to the LM Studio API
    using the base_url and model_name provided by the factory.
    """

    def __init__(
        self, 
        base_url: str, 
        model_name: str, 
        temperature: float = 0.0, 
        max_tokens: int = 512
    ):
        """Initializes the LM Studio client with settings from the factory/env."""
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def analyze_istar_elements(self, elements: List[CimNode]) -> Dict:
        """Analyzes the provided iStar elements and returns the HQC evidence signals.
        
        MODIFICACIÓN: Ahora es 'async' para ser compatible con el motor de interacción.
        """

        prompt = self._build_prompt(elements)
        
        endpoint = f"{self.base_url}/chat/completions"

        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system", 
                    "content": "Responde solo con JSON válido. No incluyas explicaciones."
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        try:
            loop = asyncio.get_event_loop()
            
            def make_request():
                return requests.post(endpoint, json=payload, timeout=60)

            resp = await loop.run_in_executor(None, make_request)
            resp.raise_for_status()
            data = resp.json()

            raw = ""
            if "choices" in data and len(data["choices"]) > 0:
                message = data["choices"][0].get("message", {})
                raw = message.get("content", "") or data["choices"][0].get("text", "")

            return self._safe_parse_json(raw.strip())
            
        except Exception as e:
            print(f"ERROR conectando a LM Studio en {endpoint}: {str(e)}")
            return self._get_empty_response()

    def _build_prompt(self, elements: List[CimNode]) -> str:
        """Builds the prompt sent to LM Studio for one interaction request."""
        text_elements = "\n".join(
            [f"{element.type}: {element.label_raw}" for element in elements]
        )
        return (
            "Analiza los siguientes elementos iStar y determina si hay evidencia "
            "para los bloques HQC_SPL: Functionality, Algorithm, Programming, "
            "Integration_model, Quantum_HW_constraint.\n\n"
            f"Elementos:\n{text_elements}\n\n"
            "Reglas:\n"
            "- Responde SOLO con un objeto JSON.\n"
            "- Si no hay evidencia clara, marca false y añade la clave a 'missing'.\n"
            "- Claves requeridas: Functionality, Algorithm, Programming, Integration_model, Quantum_HW_constraint, missing."
        )

    def _safe_parse_json(self, raw: str) -> Dict:
        """Extracts the expected JSON object from the raw response."""
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return self._get_empty_response()
            
        try:
            parsed = json.loads(match.group(0))
        except Exception:
            return self._get_empty_response()

        keys = [
            "Functionality",
            "Algorithm",
            "Programming",
            "Integration_model",
            "Quantum_HW_constraint",
        ]
        
        result = {k: bool(parsed.get(k, False)) for k in keys}
        result["missing"] = parsed.get(
            "missing", [k for k, v in result.items() if not v]
        )
        return result

    def _get_empty_response(self) -> Dict:
        """Helper to return a default state on parse error."""
        keys = ["Functionality", "Algorithm", "Programming", "Integration_model", "Quantum_HW_constraint"]
        return {k: False for k in keys} | {"missing": keys}