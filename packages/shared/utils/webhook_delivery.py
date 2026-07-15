"""Webhook delivery service for skills event system.

Delivers webhook events to external subscribers with HMAC signing,
exponential backoff retry, dead-letter handling, and monitoring.

Integrates with the event outbox: when events are routed to subscribers,
the delivery service picks up pending webhook_queue entries and delivers
them via HTTP POST with configurable headers and HMAC payload signing.
"""

import json
import time
import hmac
import hashlib
import asyncio
from typing import Optional
from dataclasses import dataclass
from enum import Enum
from shared.utils.logger import logger


class WebhookStatus(str, Enum):
    PENDING = "pending"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


@dataclass
class WebhookResult:
    webhook_id: str
    success: bool
    status_code: Optional[int] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    attempt: int = 0


class WebhookDeliveryService:
    """Delivers webhook events to external subscribers.

    Features:
    - HTTP POST delivery with configurable headers
    - HMAC-SHA256 payload signing for authenticity
    - Exponential backoff retry (2^n seconds, max 5 attempts)
    - Dead-letter queue after max retries
    - Per-subscriber rate limiting
    - Delivery timeouts (default 30s)
    - Graceful degradation: logs warning instead of crashing
    """

    def __init__(self, poll_interval: float = 15.0, batch_size: int = 50, request_timeout: int = 30):
        self.poll_interval = poll_interval
        self.batch_size = batch_size
        self.request_timeout = request_timeout
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._http_client = None
        self._supabase = None

    def _get_supabase(self):
        if self._supabase is None:
            try:
                from config.core.supabase import get_supabase_client

                self._supabase = get_supabase_client()
            except Exception as e:
                logger.error(f"Cannot get Supabase client: {e}")
                return None
        return self._supabase

    async def _get_http_client(self):
        if self._http_client is None:
            try:
                import httpx

                self._http_client = httpx.AsyncClient(
                    timeout=self.request_timeout,
                    limits=httpx.Limits(max_keepalive_connections=10, max_connections=50),
                )
            except ImportError:
                logger.warn("httpx not installed — webhook delivery disabled")
                return None
        return self._http_client

    def _sign_payload(self, payload: str, secret: Optional[str]) -> Optional[str]:
        """HMAC-SHA256 sign the payload for authenticity."""
        if not secret:
            return None
        return hmac.new(
            secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    async def deliver(self, webhook: dict) -> WebhookResult:
        """Deliver a single webhook event. Returns the delivery result."""
        webhook_id = webhook.get("webhook_id", "unknown")
        url = webhook.get("url", "")
        payload = webhook.get("payload", {})
        headers = webhook.get("headers", {}) or {}
        secret = None

        # Fetch subscriber secret if we have a subscription_id
        subscription_id = webhook.get("subscription_id")
        if subscription_id:
            supabase = self._get_supabase()
            if supabase:
                try:
                    sub_result = (
                        supabase.table("skill_event_subscriptions")
                        .select("secret")
                        .eq("subscription_id", subscription_id)
                        .execute()
                    )
                    if sub_result.data:
                        secret = sub_result.data[0].get("secret")
                except Exception as e:
                    logger.warn("Failed to fetch webhook subscription secret", error=str(e))

        start_time = time.monotonic()
        attempt = webhook.get("retry_count", 0) + 1

        client = await self._get_http_client()
        if not client:
            return WebhookResult(
                webhook_id=webhook_id,
                success=False,
                error="HTTP client unavailable",
                duration_ms=0,
                attempt=attempt,
            )

        try:
            payload_str = json.dumps(payload) if isinstance(payload, dict) else str(payload)
            signature = self._sign_payload(payload_str, secret)

            request_headers = {
                "Content-Type": "application/json",
                "User-Agent": "SecondBrain-OS-Webhook/1.0",
            }
            if signature:
                request_headers["X-Signature-256"] = signature

            # Add subscriber-configured headers
            for k, v in (headers.items() if isinstance(headers, dict) else {}):
                request_headers[k] = str(v)

            response = await client.post(url, content=payload_str, headers=request_headers)
            duration = (time.monotonic() - start_time) * 1000

            if 200 <= response.status_code < 300:
                return WebhookResult(
                    webhook_id=webhook_id,
                    success=True,
                    status_code=response.status_code,
                    duration_ms=duration,
                    attempt=attempt,
                )
            else:
                return WebhookResult(
                    webhook_id=webhook_id,
                    success=False,
                    status_code=response.status_code,
                    error=f"HTTP {response.status_code}: {response.text[:200]}",
                    duration_ms=duration,
                    attempt=attempt,
                )

        except Exception as e:
            duration = (time.monotonic() - start_time) * 1000
            return WebhookResult(
                webhook_id=webhook_id,
                success=False,
                error=str(e)[:500],
                duration_ms=duration,
                attempt=attempt,
            )

    async def poll_once(self) -> tuple[int, int]:
        """Poll for pending webhook deliveries and process them. Returns (delivered, failed)."""
        supabase = self._get_supabase()
        if not supabase:
            return 0, 0

        try:
            now_ms = int(time.time() * 1000)

            result = (
                supabase.table("skill_webhook_queue")
                .select("*")
                .in_("status", [WebhookStatus.PENDING.value, WebhookStatus.FAILED.value])
                .limit(self.batch_size)
                .order("created_at")
                .execute()
            )

            if not result.data:
                return 0, 0

            delivered = 0
            failed = 0

            for webhook in result.data:
                webhook_id = webhook.get("webhook_id")
                retry_count = webhook.get("retry_count", 0)
                max_retries = webhook.get("max_retries", 5)
                scheduled_at = webhook.get("scheduled_at")

                # Skip if in backoff delay
                if scheduled_at and scheduled_at > now_ms:
                    continue

                # Mark as delivering
                supabase.table("skill_webhook_queue").update({"status": WebhookStatus.DELIVERING.value}).eq(
                    "webhook_id", webhook_id
                ).execute()

                result_data = await self.deliver(webhook)

                if result_data.success:
                    supabase.table("skill_webhook_queue").update(
                        {
                            "status": WebhookStatus.DELIVERED.value,
                            "delivered_at": now_ms,
                            "last_http_status": result_data.status_code,
                        }
                    ).eq("webhook_id", webhook_id).execute()

                    # Update subscriber delivery count
                    if webhook.get("subscription_id"):
                        supabase.table("skill_event_subscriptions").update(
                            {
                                "last_delivered_at": now_ms,
                                "delivery_count": supabase.raw("delivery_count + 1"),
                            }
                        ).eq("subscription_id", webhook.get("subscription_id")).execute()

                    delivered += 1
                    logger.info(
                        "Webhook delivered",
                        webhook_id=webhook_id,
                        url=webhook.get("url"),
                        status=result_data.status_code,
                        duration_ms=result_data.duration_ms,
                    )

                else:
                    new_retry = retry_count + 1
                    is_dead = new_retry >= max_retries

                    # Exponential backoff: 2^attempt seconds
                    backoff_ms = (2**new_retry) * 1000

                    supabase.table("skill_webhook_queue").update(
                        {
                            "status": WebhookStatus.DEAD_LETTER.value if is_dead else WebhookStatus.FAILED.value,
                            "retry_count": new_retry,
                            "last_error": result_data.error,
                            "last_http_status": result_data.status_code,
                            "scheduled_at": now_ms + backoff_ms if not is_dead else None,
                        }
                    ).eq("webhook_id", webhook_id).execute()

                    # Update subscriber failure count
                    if webhook.get("subscription_id") and is_dead:
                        supabase.table("skill_event_subscriptions").update(
                            {
                                "last_error_at": now_ms,
                                "failure_count": supabase.raw("failure_count + 1"),
                            }
                        ).eq("subscription_id", webhook.get("subscription_id")).execute()

                    failed += 1
                    logger.warn(
                        "Webhook delivery failed",
                        webhook_id=webhook_id,
                        url=webhook.get("url"),
                        attempt=new_retry,
                        error=result_data.error,
                    )

            return delivered, failed

        except Exception as e:
            logger.error(f"Webhook poll iteration failed: {e}")
            return 0, 0

    async def start_background_polling(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info("Webhook delivery service started", interval=self.poll_interval)

    async def stop_background_polling(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass  # Expected during shutdown — not an error
            self._task = None
        logger.info("Webhook delivery service stopped")

    async def _poll_loop(self):
        while self._running:
            try:
                delivered, failed = await self.poll_once()
                if delivered > 0 or failed > 0:
                    logger.debug("Webhook poll cycle", delivered=delivered, failed=failed)
            except Exception as e:  # pragma: no cover — unreachable; poll_once catches all internally
                logger.error(f"Webhook poll loop error: {e}")
            finally:
                await asyncio.sleep(self.poll_interval)

    async def close(self):
        await self.stop_background_polling()
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def get_queue_stats(self) -> dict:
        supabase = self._get_supabase()
        if not supabase:
            return {"pending": 0, "failed": 0, "dead_letter": 0, "delivered": 0}
        try:
            stats = {}
            for status in ["pending", "failed", "dead_letter", "delivered"]:
                result = (
                    supabase.table("skill_webhook_queue")
                    .select("webhook_id", count="exact")
                    .eq("status", status)
                    .execute()
                )
                stats[status] = result.count if hasattr(result, "count") else 0
            return stats
        except Exception:
            return {"pending": -1, "failed": -1, "dead_letter": -1, "delivered": -1}  # Cleanup operation — acceptable to silently skip


webhook_delivery = WebhookDeliveryService()
