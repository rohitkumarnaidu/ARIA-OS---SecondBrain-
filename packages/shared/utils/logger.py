import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any, Optional


class LogtailHandler:
    """Async log shipping to Logtail (Better Stack). Falls back gracefully."""

    def __init__(self):
        self.token = os.getenv("LOGTAIL_SOURCE_TOKEN")
        self.client = None
        self.batch: list[dict] = []
        self.batch_lock = asyncio.Lock()
        self._flush_task: Optional[asyncio.Task] = None
        self._setup()

    def _setup(self):
        if self.token:
            try:
                import httpx

                self.client = httpx.AsyncClient(
                    base_url="https://in.logtail.com",
                    timeout=5,
                    headers={"Authorization": f"Bearer {self.token}"},
                )
            except ImportError:
                self.client = None
                return

    def start_background_flush(self):
        if self.token and self.client and self._flush_task is None:
            self._flush_task = asyncio.create_task(self._flush_loop())

    async def stop_background_flush(self):
        if self._flush_task:
            self._flush_task.cancel()
            self._flush_task = None
        await self._flush()
        if self.client:
            await self.client.aclose()
            self.client = None

    async def emit(self, record: dict):
        if not self.client:
            return
        async with self.batch_lock:
            self.batch.append(record)
            if len(self.batch) >= 10:
                asyncio.create_task(self._flush())

    async def _flush(self):
        async with self.batch_lock:
            if not self.batch:
                return
            batch = self.batch.copy()
            self.batch.clear()
        try:
            await self.client.post("/", json=batch)
        except Exception:
            pass  # Logtail flush failure — acceptable to silently degrade

    async def _flush_loop(self):
        while True:
            await asyncio.sleep(5)
            await self._flush()


_logtail_handler = LogtailHandler()


class Logger:
    """Structured JSON logger for API requests"""

    def __init__(self, name: str = "second-brain-os"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.service = os.getenv("LOGGER_SERVICE_NAME", "secondbrain-api")

        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter("%(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _log(self, level: str, message: str, **kwargs: Any):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
            "service": self.service,
            **kwargs,
        }
        level_map = {"DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARN": logging.WARN, "ERROR": logging.ERROR}
        self.logger.log(level_map.get(level, logging.INFO), json.dumps(entry))
        if _logtail_handler.client:
            asyncio.ensure_future(_logtail_handler.emit(entry))

    def info(self, message: str, **kwargs: Any):
        self._log("INFO", message, **kwargs)

    def warn(self, message: str, **kwargs: Any):
        self._log("WARN", message, **kwargs)

    def error(self, message: str, error: Optional[Exception] = None, **kwargs: Any):
        self._log("ERROR", message, error_message=str(error) if error else None, **kwargs)

    def debug(self, message: str, **kwargs: Any):
        self._log("DEBUG", message, **kwargs)


logger = Logger()


def log_request(endpoint: str, method: str, user_id: Optional[str] = None, **kwargs: Any):
    """Log incoming API request"""
    logger.info("API Request", endpoint=endpoint, method=method, user_id=user_id, **kwargs)


def log_response(endpoint: str, method: str, status_code: int, duration_ms: float, **kwargs: Any):
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
