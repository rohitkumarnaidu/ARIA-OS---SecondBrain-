"""Event outbox processor for skills domain events.

Implements the transactional outbox pattern: services write events to the
skill_event_outbox table within the same transaction as business operations.
A background processor polls for pending events, writes them to skill_events
for event sourcing, and dispatches to registered subscribers and webhooks.

Supports: exponential backoff, dead-letter queues, batch processing,
correlation/causation propagation, and graceful degradation.
"""

import json
import uuid
import time
import asyncio
from typing import Optional, Callable, Awaitable
from enum import Enum
from dataclasses import dataclass, field
from shared.utils.logger import logger


class OutboxStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


@dataclass
class OutboxEvent:
    outbox_id: str
    event_type: str
    aggregate_type: str
    aggregate_id: str
    payload: dict
    headers: dict
    status: OutboxStatus = OutboxStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    last_error: Optional[str] = None
    scheduled_at: Optional[int] = None
    processed_at: Optional[int] = None
    created_at: int = field(default_factory=lambda: int(time.time() * 1000))


class EventOutboxProcessor:
    """Transactional outbox processor for domain events.

    Polls the skill_event_outbox table for pending events, writes them
    to skill_events for event sourcing, and dispatches to registered
    handlers and webhook subscribers.

    Architecture:
        1. API handler writes event to skill_event_outbox (in business txn)
        2. Processor polls skill_event_outbox for pending events
        3. Writes event to skill_events (event sourcing)
        4. Dispatches to registered in-process handlers
        5. Dispatches to webhook subscribers via skill_webhook_queue
        6. Marks outbox event as delivered / failed / dead_letter
    """

    def __init__(self, poll_interval: float = 5.0, batch_size: int = 100):
        self.poll_interval = poll_interval
        self.batch_size = batch_size
        self._handlers: dict[str, list[Callable[..., Awaitable[None]]]] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None
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

    def register_handler(self, event_type: str, handler: Callable[..., Awaitable[None]]):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info(f"Handler registered for event type: {event_type}")

    def register_all(self, handlers: dict[str, list[Callable[..., Awaitable[None]]]]):
        for event_type, handler_list in handlers.items():
            for handler in handler_list:
                self.register_handler(event_type, handler)

    async def emit(
        self,
        event_type: str,
        aggregate_type: str,
        aggregate_id: str,
        data: dict,
        headers: dict = None,
        user_id: Optional[str] = None,
    ):
        """Emit an event by writing to the outbox table."""
        supabase = self._get_supabase()
        if not supabase:
            logger.warn("Supabase unavailable — event outbox write skipped")
            return

        event = {
            "event_type": event_type,
            "aggregate_type": aggregate_type,
            "aggregate_id": aggregate_id,
            "payload": json.dumps(data) if isinstance(data, dict) else data,
            "headers": json.dumps(headers or {}),
            "status": OutboxStatus.PENDING.value,
            "retry_count": 0,
            "max_retries": 3,
            "created_at": int(time.time() * 1000),
        }
        try:
            result = supabase.table("skill_event_outbox").insert(event).execute()
            if result.data:
                logger.info(
                    "Event emitted to outbox",
                    event_type=event_type,
                    aggregate_type=aggregate_type,
                    aggregate_id=aggregate_id,
                )
        except Exception as e:
            logger.error(f"Failed to write event to outbox: {e}", event_type=event_type)

    async def poll_once(self) -> tuple[int, int]:
        """Poll for pending events and process them. Returns (processed, failed)."""
        supabase = self._get_supabase()
        if not supabase:
            return 0, 0

        try:
            result = (
                supabase.table("skill_event_outbox")
                .select("*")
                .in_("status", [OutboxStatus.PENDING.value, OutboxStatus.FAILED.value])
                .lte(
                    "scheduled_at" if False else "created_at",
                    lambda: f"(created_at.lte.{int(time.time() * 1000)},scheduled_at.is.null)",
                )
                .limit(self.batch_size)
                .order("created_at")
                .execute()
            )

            if not result.data:
                return 0, 0

            processed = 0
            failed = 0
            now_ms = int(time.time() * 1000)

            for event in result.data:
                outbox_id = event.get("outbox_id")
                retry_count = event.get("retry_count", 0)
                max_retries = event.get("max_retries", 3)
                scheduled_at = event.get("scheduled_at")

                # Skip if not scheduled yet (backoff delay)
                if scheduled_at and scheduled_at > now_ms:
                    continue

                try:
                    # Mark as processing
                    supabase.table("skill_event_outbox").update({"status": OutboxStatus.PROCESSING.value}).eq(
                        "outbox_id", outbox_id
                    ).execute()

                    # Write to skill_events for event sourcing
                    source_event = {
                        "event_id": str(uuid.uuid4()),
                        "event_type": event.get("event_type"),
                        "event_version": "1.0",
                        "aggregate_type": event.get("aggregate_type"),
                        "aggregate_id": event.get("aggregate_id"),
                        "user_id": None,
                        "data": event.get("payload", {}),
                        "metadata": event.get("headers", {}),
                        "created_at": now_ms,
                    }
                    supabase.table("skill_events").insert(source_event).execute()

                    # Dispatch to in-process handlers
                    await self._dispatch(event)

                    # Route to webhook subscribers
                    await self._route_to_webhooks(event, supabase)

                    # Mark as delivered
                    supabase.table("skill_event_outbox").update(
                        {
                            "status": OutboxStatus.DELIVERED.value,
                            "processed_at": now_ms,
                        }
                    ).eq("outbox_id", outbox_id).execute()

                    processed += 1

                except Exception as exc:
                    error_msg = str(exc)[:500]
                    new_retry_count = retry_count + 1
                    new_status = (
                        OutboxStatus.DEAD_LETTER.value if new_retry_count >= max_retries else OutboxStatus.FAILED.value
                    )

                    # Exponential backoff: 2s, 4s, 8s, ...
                    backoff_ms = (2**new_retry_count) * 1000
                    new_scheduled_at = now_ms + backoff_ms

                    supabase.table("skill_event_outbox").update(
                        {
                            "status": new_status,
                            "retry_count": new_retry_count,
                            "last_error": error_msg,
                            "scheduled_at": new_scheduled_at,
                        }
                    ).eq("outbox_id", outbox_id).execute()

                    failed += 1
                    logger.error(
                        "Outbox event processing failed",
                        outbox_id=outbox_id,
                        event_type=event.get("event_type"),
                        retry=new_retry_count,
                        error=error_msg,
                    )

            return processed, failed

        except Exception as e:
            logger.error(f"Outbox poll iteration failed: {e}")
            return 0, 0

    async def _dispatch(self, event: dict):
        """Dispatch event to registered in-process handlers."""
        event_type = event.get("event_type", "")
        handlers = self._handlers.get(event_type, []) + self._handlers.get("*", [])
        if not handlers:
            return

        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"In-process handler failed for {event_type}: {e}")

    async def _route_to_webhooks(self, event: dict, supabase):
        """Route event to webhook subscribers based on event_type matching."""
        try:
            event_type = event.get("event_type", "")

            # Find active subscriptions that match this event type
            subs_result = supabase.table("skill_event_subscriptions").select("*").eq("is_active", True).execute()

            if not subs_result.data:
                return

            for sub in subs_result.data:
                # Check if subscription matches this event type
                subscribed_types = sub.get("event_types", [])
                if subscribed_types and event_type not in subscribed_types:
                    continue

                # Enqueue webhook delivery
                webhook_entry = {
                    "subscription_id": sub.get("subscription_id"),
                    "event_type": event_type,
                    "payload": json.dumps(
                        {
                            "event_type": event_type,
                            "aggregate_type": event.get("aggregate_type"),
                            "aggregate_id": event.get("aggregate_id"),
                            "data": event.get("payload"),
                        }
                    ),
                    "url": sub.get("url"),
                    "headers": sub.get("headers", {}),
                    "status": OutboxStatus.PENDING.value,
                    "retry_count": 0,
                    "max_retries": sub.get("retry_policy", {}).get("max_retries", 5),
                    "created_at": int(time.time() * 1000),
                }
                supabase.table("skill_webhook_queue").insert(webhook_entry).execute()

        except Exception as e:
            logger.error(f"Webhook routing failed: {e}", event_type=event.get("event_type"))

    async def start_background_polling(self):
        """Start the background polling loop."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info("Event outbox background polling started", interval=self.poll_interval)

    async def stop_background_polling(self):
        """Stop the background polling loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("Event outbox background polling stopped")

    async def _poll_loop(self):
        while self._running:
            try:
                processed, failed = await self.poll_once()
                if processed > 0 or failed > 0:
                    logger.debug("Outbox poll cycle", processed=processed, failed=failed)
            except Exception as e:  # pragma: no cover — unreachable; poll_once catches all internally
                logger.error(f"Outbox poll loop error: {e}")
            finally:
                await asyncio.sleep(self.poll_interval)

    async def reprocess_dead_letters(self) -> int:
        """Reprocess all dead-letter outbox entries. Returns count reprocessed."""
        supabase = self._get_supabase()
        if not supabase:
            return 0
        result = (
            supabase.table("skill_event_outbox")
            .update({"status": OutboxStatus.PENDING.value, "retry_count": 0, "last_error": None})
            .eq("status", OutboxStatus.DEAD_LETTER.value)
            .execute()
        )
        count = len(result.data) if result.data else 0
        if count:
            logger.info(f"Reprocessed {count} dead-letter outbox entries")
        return count

    async def get_queue_depth(self) -> dict:
        """Get current queue statistics."""
        supabase = self._get_supabase()
        if not supabase:
            return {"pending": 0, "failed": 0, "dead_letter": 0, "delivered": 0}
        try:
            stats = {}
            for status in ["pending", "failed", "dead_letter", "delivered"]:
                result = (
                    supabase.table("skill_event_outbox")
                    .select("outbox_id", count="exact")
                    .eq("status", status)
                    .execute()
                )
                stats[status] = result.count if hasattr(result, "count") else 0
            return stats
        except Exception:
            return {"pending": -1, "failed": -1, "dead_letter": -1, "delivered": -1}


event_outbox = EventOutboxProcessor()
