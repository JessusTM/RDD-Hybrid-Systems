import json
import re
import httpx
import asyncio
import logging
from typing import Dict, List
from app.models.llm_contract import CimNode
from .base import LLMInterface # type: ignore

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTIONS = (
    "Analiza los elementos UVL/iStar y responde SOLO con un JSON válido..."
)

class LMStudioClient(LLMInterface):
    def __init__(self, base_url: str, model_name: str):
        self.url = f"{base_url}/chat/completions"
        self.model_name = model_name

    async def analyze_istar_elements(self, elements: List[CimNode]) -> Dict:
        """Envía los elementos a LM Studio de forma asíncrona."""
        # Se convierten los objetos CimNode a algo que la IA pueda leer fácilmente
        elements_str = json.dumps([e.dict() for e in elements], indent=2)
        prompt_content = f"Elementos iStar a analizar:\n{elements_str}"
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                {"role": "user", "content": prompt_content}
            ],
            "temperature": 0.1 # Bajamos la temperatura para mayor consistencia en JSON
        }

        try:
            # Se usa un timeout largo ya que los modelos locales pueden ser lentos
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(self.url, json=payload)
                response.raise_for_status()
                res_json = response.json()
            
            raw_text = res_json['choices'][0]['message']['content']
            return self._safe_parse_json(raw_text)
            
        except asyncio.CancelledError:
            logger.warning("Petición a LM Studio cancelada por el usuario o tiempo de espera.")
            raise
        except httpx.ConnectError:
            logger.error(f"No se pudo conectar a LM Studio en {self.url}. ¿Está abierta la aplicación?")
            return {}
        except Exception as e:
            logger.error(f"Error inesperado en LM Studio: {e}")
            return {}

    def _safe_parse_json(self, raw: str) -> Dict:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            logger.error("La IA no devolvió un JSON válido")
            return {}
        try:
            return json.loads(match.group(0))
        except Exception:
            return {}