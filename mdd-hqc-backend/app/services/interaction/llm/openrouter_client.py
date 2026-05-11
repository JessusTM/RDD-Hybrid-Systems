"""
OpenRouter client used to infer missing HQC evidence from iStar elements.
Optimized for DeepSeek R1 reasoning models.
"""

import os
import json
import re
import httpx  # Librería asíncrona para soportar cancelación
import asyncio
import logging
from typing import Dict, List
from app.models.llm_contract import CimNode
from .base import LLMInterface

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTIONS = (
    "Analiza los elementos UVL/iStar y responde SOLO con un JSON válido con las claves exactas: "
    "Functionality, Algorithm, Programming, Integration_model, Quantum_HW_constraint, missing.\n"
    "No uses otras claves como 'questions' o 'proposals'.\n"
    "No incluyas explicaciones, comentarios ni texto adicional fuera del JSON.\n\n"
    "Reglas de interpretación:\n"
    "- Functionality=true si existe un bloque @Functionality con metas o tareas.\n"
    "- Algorithm=true Si existe un bloque @Algorithm con cualquier tarea.\n"
    "- Programming=true SOLO si aparecen referencias explícitas a lenguajes o frameworks.\n"
    "- Integration_model=true SOLO si aparecen términos como SOA, middleware, microservicios o API REST.\n"
    "- Quantum_HW_constraint=true SOLO si se mencionan restricciones físicas de hardware cuántico.\n"
    "- missing: Debe ser UNA LISTA con los nombres de las claves anteriores que sean false.\n\n"
    "- Importante: No copies los ejemplos. Analiza los elementos UVL/iStar y decide cada clave.\n"
    "- Responde SOLO con el JSON."
)

class OpenRouterClient(LLMInterface):
    def __init__(self, api_key: str = None, model_name: str = "deepseek/deepseek-r1-distill-llama-70b"):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model_name = model_name
        self.url = "https://openrouter.ai/api/v1/chat/completions"

        if not self.api_key:
            logger.error("OpenRouter API Key no configurada en las variables de entorno.")

    async def analyze_istar_elements(self, elements: List[CimNode]) -> Dict:
        """
        Envía los elementos al modelo de forma asíncrona.
        """
        prompt_content = f"Elementos iStar a analizar:\n{elements}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Title": "MDD-HQC Transformation Engine"
        }

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                {"role": "user", "content": prompt_content}
            ],
            "temperature": 0.6 
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.url, headers=headers, json=payload, timeout=60.0)
                response.raise_for_status()
                res_json = response.json()
            
            raw_text = res_json['choices'][0]['message']['content']
            return self._safe_parse_json(raw_text)
            
        except asyncio.CancelledError:
            logger.warning("Petición abortada: El usuario cerró la pestaña o navegó fuera.")
            raise
        except Exception as e:
            logger.error(f"Error en la conexión con OpenRouter: {e}")
            return {}

    def _safe_parse_json(self, raw: str) -> Dict:
        """
        Limpia la respuesta eliminando etiquetas <think> y extrayendo el JSON.
        """
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

        required_keys = [
            "Functionality",
            "Algorithm",
            "Programming",
            "Integration_model",
            "Quantum_HW_constraint",
        ]

        result = {k: bool(parsed.get(k, False)) for k in required_keys}
        extracted_missing = parsed.get("missing", [])
        result["missing"] = extracted_missing if isinstance(extracted_missing, list) else []
        
        return result