"""In-memory request limits for paid LLM-backed endpoints."""

import logging
import time
from collections import defaultdict
from threading import Lock

logger = logging.getLogger(__name__)


class AISecurityShield:
    """Limits bursts and immediate duplicate LLM requests per backend process."""

    def __init__(self, max_requests: int = 5, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.duplicate_window_seconds = 10.0
        self.rate_limit_records = defaultdict(list)
        self.duplicate_records = {}
        self.lock = Lock()

    def check_request(self, ip: str, endpoint: str, path: str) -> bool:
        """Returns whether a request satisfies rate and duplicate limits."""
        current_time = time.monotonic()
        duplicate_key = (ip, endpoint, path)

        with self.lock:
            timestamps = [
                timestamp
                for timestamp in self.rate_limit_records[ip]
                if current_time - timestamp < self.window_seconds
            ]
            self.rate_limit_records[ip] = timestamps
            self.duplicate_records = {
                key: timestamp
                for key, timestamp in self.duplicate_records.items()
                if current_time - timestamp < self.duplicate_window_seconds
            }

            if duplicate_key in self.duplicate_records:
                logger.warning("Blocked duplicate LLM request from %s.", ip)
                return False

            if len(timestamps) >= self.max_requests:
                logger.warning("Blocked LLM request rate limit from %s.", ip)
                return False

            timestamps.append(current_time)
            self.duplicate_records[duplicate_key] = current_time
            return True


security_shield = AISecurityShield()
