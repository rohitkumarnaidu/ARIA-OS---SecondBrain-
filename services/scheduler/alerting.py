"""Multi-channel alerting for the scheduler with rate limiting.

Supports:
  - Console logging (always on)
  - Logtail/Datadog via HTTP API (configurable via ALERT_LOGTAIL_SOURCE_TOKEN)
  - Webhook (Slack/Discord/Generic) via ALERT_WEBHOOK_URL
  - ALERT_SLACK_CHANNEL for Slack channel override
"""

import os
import asyncio
import time
from datetime import datetime, timezone
from typing import Optional

import httpx
from shared.utils.logger import logger


class AlertRateLimiter:
    """Prevents alert storms: max 1 alert per job per cooldown period."""

    def __init__(self):
        self._lock = asyncio.Lock()
        self._last_alert: dict[str, float] = {}

    async def can_alert(self, key: str, cooldown: float = 300.0) -> bool:
        async with self._lock:
            now = time.time()
            last = self._last_alert.get(key, 0.0)
            if now - last >= cooldown:
                self._last_alert[key] = now
                return True
            return False


class Alerting:
    """Multi-channel alerting with graceful fallback."""

    def __init__(self):
        self._rate_limiter = AlertRateLimiter()
        self._webhook_url = os.getenv("ALERT_WEBHOOK_URL", "")
        self._slack_channel = os.getenv("ALERT_SLACK_CHANNEL", "#aria-alerts")
        self._logtail_token = os.getenv("ALERT_LOGTAIL_SOURCE_TOKEN", "")
        self._http_client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=10.0)
        return self._http_client

    async def shutdown(self):
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def flush_pending(self):
        pass  # all alerts are sent immediately; placeholder for future batching

    # ── Console (always on) ──────────────────────────────────────────────────

    def _log_console(self, severity: str, message: str, details: Optional[dict] = None):
        safe = details or {}
        if severity == "CRITICAL":
            logger.error(f"[{severity}] {message}", **safe)
        elif severity == "WARNING":
            logger.warn(f"[{severity}] {message}", **safe)
        else:
            logger.info(f"[{severity}] {message}", **safe)

    # ── Logtail / Datadog ────────────────────────────────────────────────────

    async def _send_logtail(self, payload: dict):
        if not self._logtail_token:
            return
        try:
            client = await self._get_client()
            resp = await client.post(
                "https://in.logtail.com",
                headers={
                    "Authorization": f"Bearer {self._logtail_token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            if resp.status_code >= 400:
                logger.warn("Logtail delivery failed", status_code=resp.status_code)
        except Exception as e:
            logger.warn("Logtail unavailable", error=str(e))

    # ── Webhook (Slack / Discord / Generic) ─────────────────────────────────

    async def _deliver_webhook(self, payload: dict):
        if not self._webhook_url:
            return
        try:
            client = await self._get_client()
            severity = payload.get("severity", "INFO")
            color = "danger" if severity == "CRITICAL" else ("warning" if severity == "WARNING" else "good")
            fields = [{"title": k, "value": str(v), "short": True} for k, v in payload.items() if k not in ("severity", "message", "timestamp", "source")]
            webhook_payload = {
                "text": f"[{severity}] {payload.get('message', '')}",
                "channel": self._slack_channel,
                "attachments": [{"color": color, "fields": fields}],
            }
            resp = await client.post(self._webhook_url, json=webhook_payload)
            if resp.status_code >= 400:
                logger.warn("Webhook delivery failed", status_code=resp.status_code, response=resp.text[:200])
        except Exception as e:
            logger.warn("Webhook unavailable", error=str(e))

    # ── Send (assembly + delivery) ──────────────────────────────────────────

    async def _send_alert(self, severity: str, message: str, details: Optional[dict] = None):
        payload = {
            "severity": severity,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "scheduler",
            **(details or {}),
        }
        self._log_console(severity, message, details)
        await self._send_logtail(payload)

        job_name = details.get("job_name", "unknown") if details else "unknown"
        rate_key = f"{job_name}_{severity}"
        if await self._rate_limiter.can_alert(rate_key, cooldown=300.0):
            await self._deliver_webhook(payload)
        else:
            logger.info("Alert rate-limited (webhook skipped)", job_name=job_name, severity=severity)

    # ── Public API ───────────────────────────────────────────────────────────

    async def alert_critical(self, message: str, details: Optional[dict] = None):
        await self._send_alert("CRITICAL", message, details)

    async def alert_warning(self, message: str, details: Optional[dict] = None):
        await self._send_alert("WARNING", message, details)

    async def alert_info(self, message: str, details: Optional[dict] = None):
        await self._send_alert("INFO", message, details)


alerting = Alerting()
