import logging
import json
from datetime import datetime
from typing import Any, Optional
import sys


class Logger:
    """Structured JSON logger for API requests"""

    def __init__(self, name: str = "second-brain-os"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter("%(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _log(self, level: str, message: str, **kwargs: Any):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            **kwargs,
        }
        self.logger.info(json.dumps(entry))

    def info(self, message: str, **kwargs: Any):
        self._log("INFO", message, **kwargs)

    def warn(self, message: str, **kwargs: Any):
        self._log("WARN", message, **kwargs)

    def error(self, message: str, error: Optional[Exception] = None, **kwargs: Any):
        self._log(
            "ERROR", message, error_message=str(error) if error else None, **kwargs
        )

    def debug(self, message: str, **kwargs: Any):
        self._log("DEBUG", message, **kwargs)


logger = Logger()


def log_request(
    endpoint: str, method: str, user_id: Optional[str] = None, **kwargs: Any
):
    """Log incoming API request"""
    logger.info(
        "API Request", endpoint=endpoint, method=method, user_id=user_id, **kwargs
    )


def log_response(
    endpoint: str, method: str, status_code: int, duration_ms: float, **kwargs: Any
):
    """Log API response"""
    logger.info(
        "API Response",
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        duration_ms=round(duration_ms, 2),
        **kwargs,
    )


def log_error(endpoint: str, method: str, error: Exception, **kwargs: Any):
    """Log API error"""
    logger.error(
        "API Error",
        endpoint=endpoint,
        method=method,
        error_type=type(error).__name__,
        error_message=str(error),
        **kwargs,
    )
