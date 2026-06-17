import time
import logging
from collections import defaultdict
from threading import Lock

logger = logging.getLogger(__name__)

class AISecurityShield:
    def __init__(self):
        self.rate_limit_records = defaultdict(list)
        
        self.duplicate_records = defaultdict(float)
        
        self.lock = Lock()

    def check_request(self, ip: str, endpoint: str, path: str) -> bool:
        """
        Evalúa las políticas de seguridad contra vulnerabilidades económicas.
        Retorna True si la solicitud es válida y permitida.
        Retorna False si debe ser inmediatamente bloqueada (429).
        """
        current_time = time.time()
        duplicate_key = f"{ip}:{endpoint}:{path}"

        with self.lock:
            last_request_time = self.duplicate_records.get(duplicate_key, 0.0)
            elapsed_since_last = current_time - last_request_time

            if elapsed_since_last < 10.0:
                logger.warning(
                    f"[SECURITY SHIELD] [BLOQUEO] Intento de solicitud duplicada inmediata. "
                    f"Clave identificadora: {duplicate_key}. "
                    f"Tiempo transcurrido desde el último intento: {elapsed_since_last:.2f}s (Mínimo requerido: 10s)."
                )
                return False

            self.rate_limit_records[ip] = [
                timestamp for timestamp in self.rate_limit_records[ip] 
                if current_time - timestamp < 60.0
            ]

            requests_in_last_minute = len(self.rate_limit_records[ip])
            if requests_in_last_minute >= 5:
                logger.warning(
                    f"[SECURITY SHIELD] [BLOQUEO] Límite de frecuencia excedido para la IP: {ip}. "
                    f"Cantidad de solicitudes en el último minuto: {requests_in_last_minute} (Máximo permitido: 5)."
                )
                return False

            self.rate_limit_records[ip].append(current_time)
            self.duplicate_records[duplicate_key] = current_time
            
            logger.info(
                f"[SECURITY SHIELD] [PERMITIDO] Solicitud autorizada. "
                f"IP: {ip} | Endpoint: {endpoint} | Path: {path}."
            )
            return True

security_shield = AISecurityShield()