"""Tests for event_outbox, webhook_delivery, notifications, and neo4j_sync modules.

Achieves 100% coverage of:
  - packages/shared/utils/event_outbox.py
  - packages/shared/utils/webhook_delivery.py
  - packages/shared/utils/notifications.py
  - packages/shared/utils/neo4j_sync.py
"""

# ruff: noqa: E402

import pytest
import json
import time
import asyncio
import hmac
import hashlib
from unittest.mock import MagicMock, patch, AsyncMock

pytestmark = pytest.mark.asyncio


# ── Helpers ──


def _async_iter(*items):
    """Create an async iterator from items."""
    it = iter(items)

    class _AsyncIter:
        def __aiter__(self):
            return self

        async def __anext__(self):
            try:
                return next(it)
            except StopIteration:
                raise StopAsyncIteration

    return _AsyncIter()


def _make_async_run(records=None):
    """Return an async side_effect function for session.run that yields records."""
    records = records or []

    async def run_side_effect(query, params=None):
        return _async_iter(*records)

    return run_side_effect


# =============================================================================
#  event_outbox.py
# =============================================================================


class TestOutboxStatus:
    def test_members(self):
        from shared.utils.event_outbox import OutboxStatus

        assert OutboxStatus.PENDING.value == "pending"
        assert OutboxStatus.PROCESSING.value == "processing"
        assert OutboxStatus.DELIVERED.value == "delivered"
        assert OutboxStatus.FAILED.value == "failed"
        assert OutboxStatus.DEAD_LETTER.value == "dead_letter"


class TestOutboxEvent:
    def test_defaults(self):
        from shared.utils.event_outbox import OutboxEvent, OutboxStatus

        ev = OutboxEvent(
            outbox_id="o1",
            event_type="skill.created",
            aggregate_type="skill",
            aggregate_id="s1",
            payload={"name": "Python"},
            headers={"trace_id": "t1"},
        )
        assert ev.outbox_id == "o1"
        assert ev.status == OutboxStatus.PENDING
        assert ev.retry_count == 0
        assert ev.max_retries == 3
        assert ev.last_error is None
        assert ev.scheduled_at is None
        assert ev.processed_at is None
        assert ev.created_at > 0


class TestEventOutboxProcessor:
    """EventOutboxProcessor — init, supabase, handlers, emit, poll, dispatch, webhooks, lifecycle."""

    @pytest.fixture
    def processor(self):
        from shared.utils.event_outbox import EventOutboxProcessor

        p = EventOutboxProcessor(poll_interval=2.0, batch_size=50)
        yield p

    # ── __init__ ──

    def test_init_defaults(self):
        from shared.utils.event_outbox import EventOutboxProcessor

        p = EventOutboxProcessor()
        assert p.poll_interval == 5.0
        assert p.batch_size == 100
        assert p._handlers == {}
        assert p._running is False
        assert p._task is None
        assert p._supabase is None

    # ── _get_supabase ──

    async def test_get_supabase_success(self, processor):
        mock_client = MagicMock()
        with patch("config.core.supabase.get_supabase_client", return_value=mock_client):
            client = processor._get_supabase()
            assert client is mock_client
            assert processor._supabase is mock_client

    async def test_get_supabase_failure(self, processor):
        with patch("config.core.supabase.get_supabase_client", side_effect=ImportError("no module")):
            client = processor._get_supabase()
            assert client is None

    async def test_get_supabase_cached(self, processor):
        mock_client = MagicMock()
        processor._supabase = mock_client
        client = processor._get_supabase()
        assert client is mock_client

    # ── register_handler ──

    async def test_register_handler_new(self, processor):
        async def handler(event):
            pass

        processor.register_handler("skill.created", handler)
        assert "skill.created" in processor._handlers
        assert handler in processor._handlers["skill.created"]

    async def test_register_handler_existing(self, processor):
        async def h1(event):
            pass

        async def h2(event):
            pass

        processor.register_handler("skill.created", h1)
        processor.register_handler("skill.created", h2)
        assert len(processor._handlers["skill.created"]) == 2

    # ── register_all ──

    async def test_register_all(self, processor):
        async def h1(event):
            pass

        async def h2(event):
            pass

        processor.register_all({"skill.created": [h1], "skill.updated": [h2]})
        assert h1 in processor._handlers["skill.created"]
        assert h2 in processor._handlers["skill.updated"]

    # ── emit ──

    async def test_emit_success(self, processor):
        mock_supabase = MagicMock()
        mock_table = MagicMock()
        mock_table.insert.return_value.execute.return_value.data = [{"outbox_id": "o1"}]
        mock_supabase.table.return_value = mock_table
        processor._supabase = mock_supabase

        await processor.emit(
            event_type="skill.created",
            aggregate_type="skill",
            aggregate_id="s1",
            data={"name": "Python"},
            headers={"trace_id": "abc"},
            user_id="u1",
        )
        mock_table.insert.assert_called_once()
        args = mock_table.insert.call_args[0][0]
        assert args["event_type"] == "skill.created"
        assert args["aggregate_type"] == "skill"
        assert args["aggregate_id"] == "s1"
        assert json.loads(args["payload"]) == {"name": "Python"}

    async def test_emit_supabase_unavailable(self, processor):
        with patch.object(processor, "_get_supabase", return_value=None):
            await processor.emit(event_type="skill.created", aggregate_type="skill", aggregate_id="s1", data={})

    async def test_emit_exception(self, processor):
        mock_supabase = MagicMock()
        mock_supabase.table.side_effect = Exception("DB down")
        processor._supabase = mock_supabase

        await processor.emit(event_type="skill.created", aggregate_type="skill", aggregate_id="s1", data={})

    async def test_emit_data_not_dict(self, processor):
        mock_supabase = MagicMock()
        mock_table = MagicMock()
        mock_table.insert.return_value.execute.return_value.data = [{"outbox_id": "o1"}]
        mock_supabase.table.return_value = mock_table
        processor._supabase = mock_supabase

        await processor.emit(event_type="skill.created", aggregate_type="skill", aggregate_id="s1", data="raw_string")
        args = mock_table.insert.call_args[0][0]
        assert args["payload"] == "raw_string"

    async def test_emit_no_headers(self, processor):
        mock_supabase = MagicMock()
        mock_table = MagicMock()
        mock_table.insert.return_value.execute.return_value.data = [{"outbox_id": "o1"}]
        mock_supabase.table.return_value = mock_table
        processor._supabase = mock_supabase

        await processor.emit(event_type="skill.created", aggregate_type="skill", aggregate_id="s1", data={})
        args = mock_table.insert.call_args[0][0]
        assert json.loads(args["headers"]) == {}

    # ── poll_once ──

    async def test_poll_once_no_supabase(self, processor):
        with patch.object(processor, "_get_supabase", return_value=None):
            processed, failed = await processor.poll_once()
            assert processed == 0 and failed == 0

    async def test_poll_once_no_pending(self, processor):
        mock_supabase = MagicMock()
        outbox_table = MagicMock()
        outbox_table.select.return_value.in_.return_value.lte.return_value.limit.return_value.order.return_value.execute.return_value.data = []
        mock_supabase.table.return_value = outbox_table
        processor._supabase = mock_supabase

        processed, failed = await processor.poll_once()
        assert processed == 0 and failed == 0

    async def test_poll_once_processes_successfully(self, processor):
        mock_supabase = MagicMock()
        outbox_table = MagicMock()
        events_table = MagicMock()
        subs_table = MagicMock()
        queue_table = MagicMock()

        outbox_table.select.return_value.in_.return_value.lte.return_value.limit.return_value.order.return_value.execute.return_value.data = [
            {
                "outbox_id": "o1", "event_type": "skill.created",
                "aggregate_type": "skill", "aggregate_id": "s1",
                "payload": json.dumps({"name": "Python"}),
                "headers": json.dumps({"trace_id": "abc"}),
                "retry_count": 0, "max_retries": 3,
                "scheduled_at": None, "status": "pending",
            }
        ]

        update_calls = []
        processing_update = MagicMock()
        processing_update.eq.return_value.execute.return_value = MagicMock()
        delivered_update = MagicMock()
        delivered_update.eq.return_value.execute.return_value = MagicMock()
        update_calls = [processing_update, delivered_update]

        def update_side(*a, **kw):
            return update_calls.pop(0) if update_calls else MagicMock()

        outbox_table.update.side_effect = update_side
        events_table.insert.return_value.execute.return_value = MagicMock()
        subs_table.select.return_value.eq.return_value.execute.return_value.data = []
        queue_table.insert.return_value.execute.return_value = MagicMock()

        def table_side(name):
            return {
                "skill_event_outbox": outbox_table,
                "skill_events": events_table,
                "skill_event_subscriptions": subs_table,
                "skill_webhook_queue": queue_table,
            }.get(name, MagicMock())

        mock_supabase.table.side_effect = table_side
        processor._supabase = mock_supabase

        processed, failed = await processor.poll_once()
        assert processed == 1
        assert failed == 0
        processing_update.eq.assert_called_with("outbox_id", "o1")

    async def test_poll_once_skip_scheduled(self, processor):
        mock_supabase = MagicMock()
        future_ms = int(time.time() * 1000) + 60000
        outbox_table = MagicMock()
        outbox_table.select.return_value.in_.return_value.lte.return_value.limit.return_value.order.return_value.execute.return_value.data = [
            {
                "outbox_id": "o2", "event_type": "skill.created",
                "aggregate_type": "skill", "aggregate_id": "s2",
                "payload": "{}", "headers": "{}",
                "retry_count": 0, "max_retries": 3,
                "scheduled_at": future_ms, "status": "pending",
            }
        ]
        mock_supabase.table.return_value = outbox_table
        processor._supabase = mock_supabase

        processed, failed = await processor.poll_once()
        assert processed == 0 and failed == 0

    async def test_poll_once_dead_letter_after_max_retries(self, processor):
        mock_supabase = MagicMock()
        outbox_table = MagicMock()
        events_table = MagicMock()
        subs_table = MagicMock()
        queue_table = MagicMock()

        outbox_table.select.return_value.in_.return_value.lte.return_value.limit.return_value.order.return_value.execute.return_value.data = [
            {
                "outbox_id": "o_dead", "event_type": "skill.created",
                "aggregate_type": "skill", "aggregate_id": "s1",
                "payload": "{}", "headers": "{}",
                "retry_count": 2, "max_retries": 3,
                "scheduled_at": None, "status": "failed",
            }
        ]

        processing_update = MagicMock()
        processing_update.eq.return_value.execute.return_value = MagicMock()
        failed_update = MagicMock()
        failed_update.eq.return_value.execute.return_value = MagicMock()
        update_order = [processing_update, failed_update]

        def update_side(*a, **kw):
            return update_order.pop(0) if update_order else MagicMock()

        outbox_table.update.side_effect = update_side
        events_table.insert.side_effect = Exception("insert failure")
        subs_table.select.return_value.eq.return_value.execute.return_value.data = []
        queue_table.insert.return_value.execute.return_value = MagicMock()

        def table_side(name):
            return {
                "skill_event_outbox": outbox_table,
                "skill_events": events_table,
                "skill_event_subscriptions": subs_table,
                "skill_webhook_queue": queue_table,
            }.get(name, MagicMock())

        mock_supabase.table.side_effect = table_side
        processor._supabase = mock_supabase

        processed, failed = await processor.poll_once()
        assert processed == 0
        assert failed == 1
        status_call = outbox_table.update.call_args_list[1]
        assert status_call[0][0]["status"] == "dead_letter"
        assert status_call[0][0]["retry_count"] == 3

    async def test_poll_once_retry_failed_not_dead_letter(self, processor):
        mock_supabase = MagicMock()
        outbox_table = MagicMock()
        events_table = MagicMock()
        subs_table = MagicMock()
        queue_table = MagicMock()

        outbox_table.select.return_value.in_.return_value.lte.return_value.limit.return_value.order.return_value.execute.return_value.data = [
            {
                "outbox_id": "o_retry", "event_type": "skill.created",
                "aggregate_type": "skill", "aggregate_id": "s1",
                "payload": "{}", "headers": "{}",
                "retry_count": 0, "max_retries": 3,
                "scheduled_at": None, "status": "pending",
            }
        ]

        processing_update = MagicMock()
        processing_update.eq.return_value.execute.return_value = MagicMock()
        failed_update = MagicMock()
        failed_update.eq.return_value.execute.return_value = MagicMock()
        update_order = [processing_update, failed_update]

        def update_side(*a, **kw):
            return update_order.pop(0) if update_order else MagicMock()

        outbox_table.update.side_effect = update_side
        events_table.insert.side_effect = Exception("insert failure")
        subs_table.select.return_value.eq.return_value.execute.return_value.data = []
        queue_table.insert.return_value.execute.return_value = MagicMock()

        def table_side(name):
            return {
                "skill_event_outbox": outbox_table,
                "skill_events": events_table,
                "skill_event_subscriptions": subs_table,
                "skill_webhook_queue": queue_table,
            }.get(name, MagicMock())

        mock_supabase.table.side_effect = table_side
        processor._supabase = mock_supabase

        processed, failed = await processor.poll_once()
        assert processed == 0
        assert failed == 1
        status_call = outbox_table.update.call_args_list[1]
        assert status_call[0][0]["status"] == "failed"
        assert status_call[0][0]["retry_count"] == 1
        assert "scheduled_at" in status_call[0][0]

    async def test_poll_once_exception_during_poll(self, processor):
        mock_supabase = MagicMock()
        mock_supabase.table.side_effect = Exception("poll error")
        processor._supabase = mock_supabase

        processed, failed = await processor.poll_once()
        assert processed == 0 and failed == 0

    async def test_poll_once_dispatch_throws_still_handles(self, processor):
        mock_supabase = MagicMock()
        outbox_table = MagicMock()
        events_table = MagicMock()
        subs_table = MagicMock()
        queue_table = MagicMock()

        outbox_table.select.return_value.in_.return_value.lte.return_value.limit.return_value.order.return_value.execute.return_value.data = [
            {
                "outbox_id": "o_dispatch_fail", "event_type": "skill.created",
                "aggregate_type": "skill", "aggregate_id": "s1",
                "payload": "{}", "headers": "{}",
                "retry_count": 0, "max_retries": 3,
                "scheduled_at": None, "status": "pending",
            }
        ]

        processing_update = MagicMock()
        processing_update.eq.return_value.execute.return_value = MagicMock()
        failed_update = MagicMock()
        failed_update.eq.return_value.execute.return_value = MagicMock()
        update_order = [processing_update, failed_update]

        def update_side(*a, **kw):
            return update_order.pop(0) if update_order else MagicMock()

        outbox_table.update.side_effect = update_side
        events_table.insert.return_value.execute.return_value = MagicMock()

        def table_side(name):
            return {
                "skill_event_outbox": outbox_table,
                "skill_events": events_table,
                "skill_event_subscriptions": subs_table,
                "skill_webhook_queue": queue_table,
            }.get(name, MagicMock())

        mock_supabase.table.side_effect = table_side
        processor._supabase = mock_supabase

        with patch.object(processor, "_dispatch", side_effect=Exception("dispatch fail")):
            processed, failed = await processor.poll_once()
            assert processed == 0
            assert failed == 1

    # ── _dispatch ──

    async def test_dispatch_handlers_exist(self, processor):
        mock_handler = AsyncMock()
        processor.register_handler("skill.created", mock_handler)
        await processor._dispatch({"event_type": "skill.created", "data": {}})
        mock_handler.assert_awaited_once()

    async def test_dispatch_no_handlers(self, processor):
        await processor._dispatch({"event_type": "unknown", "data": {}})

    async def test_dispatch_wildcard_handler(self, processor):
        mock_handler = AsyncMock()
        processor.register_handler("*", mock_handler)
        await processor._dispatch({"event_type": "skill.created", "data": {}})
        mock_handler.assert_awaited_once()

    async def test_dispatch_handler_throws(self, processor):
        async def failing_handler(event):
            raise ValueError("oops")

        processor.register_handler("skill.created", failing_handler)
        await processor._dispatch({"event_type": "skill.created", "data": {}})

    # ── _route_to_webhooks ──

    async def test_route_to_webhooks_no_subscribers(self, processor):
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        await processor._route_to_webhooks({"event_type": "skill.created"}, mock_supabase)

    async def test_route_to_webhooks_subscriber_matches(self, processor):
        mock_supabase = MagicMock()
        subs_table = MagicMock()
        subs_table.select.return_value.eq.return_value.execute.return_value.data = [
            {
                "subscription_id": "sub1", "event_types": ["skill.created"],
                "url": "https://example.com/hook", "headers": {"X-Custom": "val"},
                "retry_policy": {"max_retries": 5},
            }
        ]
        queue_table = MagicMock()
        queue_table.insert.return_value.execute.return_value = MagicMock()

        def ts(name):
            return subs_table if name == "skill_event_subscriptions" else queue_table if name == "skill_webhook_queue" else MagicMock()

        mock_supabase.table.side_effect = ts

        await processor._route_to_webhooks(
            {"event_type": "skill.created", "aggregate_type": "skill", "aggregate_id": "s1", "payload": "{}"},
            mock_supabase,
        )
        queue_table.insert.assert_called_once()

    async def test_route_to_webhooks_subscriber_does_not_match(self, processor):
        mock_supabase = MagicMock()
        subs_table = MagicMock()
        subs_table.select.return_value.eq.return_value.execute.return_value.data = [
            {
                "subscription_id": "sub1", "event_types": ["skill.deleted"],
                "url": "https://example.com/hook", "headers": {}, "retry_policy": {},
            }
        ]
        mock_supabase.table.return_value = subs_table
        await processor._route_to_webhooks(
            {"event_type": "skill.created", "aggregate_type": "skill", "aggregate_id": "s1", "payload": "{}"},
            mock_supabase,
        )

    async def test_route_to_webhooks_exception(self, processor):
        mock_supabase = MagicMock()
        mock_supabase.table.side_effect = Exception("routing failure")
        await processor._route_to_webhooks({"event_type": "skill.created"}, mock_supabase)

    async def test_route_to_webhooks_empty_event_types(self, processor):
        mock_supabase = MagicMock()
        subs_table = MagicMock()
        subs_table.select.return_value.eq.return_value.execute.return_value.data = [
            {
                "subscription_id": "sub2", "event_types": [],
                "url": "https://example.com/hook", "headers": {},
                "retry_policy": {"max_retries": 3},
            }
        ]
        queue_table = MagicMock()
        queue_table.insert.return_value.execute.return_value = MagicMock()

        def ts(name):
            return subs_table if name == "skill_event_subscriptions" else queue_table if name == "skill_webhook_queue" else MagicMock()

        mock_supabase.table.side_effect = ts

        await processor._route_to_webhooks(
            {"event_type": "skill.created", "aggregate_type": "skill", "aggregate_id": "s1", "payload": "{}"},
            mock_supabase,
        )
        queue_table.insert.assert_called_once()

    # ── start_background_polling ──

    async def test_start_background_polling(self, processor):
        await processor.start_background_polling()
        assert processor._running is True
        assert processor._task is not None
        await processor.stop_background_polling()

    async def test_start_background_polling_already_running(self, processor):
        processor._running = True
        processor._task = asyncio.create_task(asyncio.sleep(999))
        await processor.start_background_polling()
        await processor.stop_background_polling()

    # ── stop_background_polling ──

    async def test_stop_background_polling(self, processor):
        await processor.start_background_polling()
        await processor.stop_background_polling()
        assert processor._running is False
        assert processor._task is None

    async def test_stop_background_polling_no_task(self, processor):
        await processor.stop_background_polling()
        assert processor._task is None

    # ── _poll_loop ──

    async def test_poll_loop_runs_and_sleeps(self, processor):
        processor.poll_interval = 0.01
        processor._running = True
        call_count = 0

        async def mock_poll_once():
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                processor._running = False
            return (1, 2)

        processor.poll_once = mock_poll_once
        await processor._poll_loop()
        assert call_count >= 2

    async def test_poll_loop_exception_handled(self, processor):
        processor.poll_interval = 0.01
        processor._running = True
        call_count = 0

        async def mock_poll_once():
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                processor._running = False
                return (0, 0)
            raise ValueError("poll error")

        processor.poll_once = mock_poll_once
        await processor._poll_loop()
        assert call_count >= 2

    # ── reprocess_dead_letters ──

    async def test_reprocess_dead_letters_success(self, processor):
        mock_supabase = MagicMock()
        mock_update = MagicMock()
        mock_update.eq.return_value.execute.return_value.data = [{"outbox_id": "d1"}, {"outbox_id": "d2"}]
        mock_supabase.table.return_value.update.return_value = mock_update
        processor._supabase = mock_supabase

        count = await processor.reprocess_dead_letters()
        assert count == 2

    async def test_reprocess_dead_letters_supabase_unavailable(self, processor):
        with patch.object(processor, "_get_supabase", return_value=None):
            count = await processor.reprocess_dead_letters()
            assert count == 0

    async def test_reprocess_dead_letters_no_data(self, processor):
        mock_supabase = MagicMock()
        mock_update = MagicMock()
        mock_update.eq.return_value.execute.return_value.data = []
        mock_supabase.table.return_value.update.return_value = mock_update
        processor._supabase = mock_supabase

        count = await processor.reprocess_dead_letters()
        assert count == 0

    # ── get_queue_depth ──

    async def test_get_queue_depth_success(self, processor):
        mock_supabase = MagicMock()
        mock_result = MagicMock()
        mock_result.count = 5

        def select_side_effect(col, **kwargs):
            m = MagicMock()
            m.eq.return_value.execute.return_value = mock_result
            return m

        mock_table = MagicMock()
        mock_table.select.side_effect = select_side_effect
        mock_supabase.table.return_value = mock_table
        processor._supabase = mock_supabase

        stats = await processor.get_queue_depth()
        assert stats == {"pending": 5, "failed": 5, "dead_letter": 5, "delivered": 5}

    async def test_get_queue_depth_no_count_attr(self, processor):
        mock_supabase = MagicMock()
        mock_result = MagicMock()
        del mock_result.count

        def select_side_effect(col, **kwargs):
            m = MagicMock()
            m.eq.return_value.execute.return_value = mock_result
            return m

        mock_table = MagicMock()
        mock_table.select.side_effect = select_side_effect
        mock_supabase.table.return_value = mock_table
        processor._supabase = mock_supabase

        stats = await processor.get_queue_depth()
        assert stats == {"pending": 0, "failed": 0, "dead_letter": 0, "delivered": 0}

    async def test_get_queue_depth_exception(self, processor):
        mock_supabase = MagicMock()
        mock_supabase.table.side_effect = Exception("stats error")
        processor._supabase = mock_supabase

        stats = await processor.get_queue_depth()
        assert stats == {"pending": -1, "failed": -1, "dead_letter": -1, "delivered": -1}

    async def test_get_queue_depth_supabase_unavailable(self, processor):
        with patch.object(processor, "_get_supabase", return_value=None):
            stats = await processor.get_queue_depth()
            assert stats == {"pending": 0, "failed": 0, "dead_letter": 0, "delivered": 0}

    # ── event_outbox global ──

    async def test_global_event_outbox_instance(self):
        from shared.utils.event_outbox import event_outbox

        assert event_outbox is not None
        assert isinstance(event_outbox.poll_interval, float)
        assert isinstance(event_outbox.batch_size, int)


# =============================================================================
#  webhook_delivery.py
# =============================================================================


class TestWebhookStatus:
    def test_members(self):
        from shared.utils.webhook_delivery import WebhookStatus

        assert WebhookStatus.PENDING.value == "pending"
        assert WebhookStatus.DELIVERING.value == "delivering"
        assert WebhookStatus.DELIVERED.value == "delivered"
        assert WebhookStatus.FAILED.value == "failed"
        assert WebhookStatus.DEAD_LETTER.value == "dead_letter"


class TestWebhookResult:
    def test_defaults(self):
        from shared.utils.webhook_delivery import WebhookResult

        r = WebhookResult(webhook_id="w1", success=True)
        assert r.webhook_id == "w1"
        assert r.success is True
        assert r.status_code is None
        assert r.error is None
        assert r.duration_ms == 0.0
        assert r.attempt == 0


class TestWebhookDeliveryService:
    """WebhookDeliveryService — init, supabase, http client, sign, deliver, poll, lifecycle."""

    @pytest.fixture
    def svc(self):
        from shared.utils.webhook_delivery import WebhookDeliveryService

        s = WebhookDeliveryService(poll_interval=3.0, batch_size=25, request_timeout=15)
        yield s

    # ── __init__ ──

    def test_init_defaults(self):
        from shared.utils.webhook_delivery import WebhookDeliveryService

        s = WebhookDeliveryService()
        assert s.poll_interval == 15.0
        assert s.batch_size == 50
        assert s.request_timeout == 30

    # ── _get_supabase ──

    async def test_wh_get_supabase_success(self, svc):
        mock_client = MagicMock()
        with patch("config.core.supabase.get_supabase_client", return_value=mock_client):
            client = svc._get_supabase()
            assert client is mock_client

    async def test_wh_get_supabase_failure(self, svc):
        with patch("config.core.supabase.get_supabase_client", side_effect=Exception("fail")):
            client = svc._get_supabase()
            assert client is None

    # ── _get_http_client ──

    async def test_get_http_client_success(self, svc):
        # httpx is available in this environment; just call the method directly
        client = await svc._get_http_client()
        assert client is not None
        assert svc._http_client is client

    async def test_get_http_client_not_installed(self, svc):
        import sys as _sys
        orig = _sys.modules.pop("httpx", None)
        _sys.modules["httpx"] = None
        try:
            client = await svc._get_http_client()
            assert client is None
        finally:
            if orig:
                _sys.modules["httpx"] = orig
            else:
                _sys.modules.pop("httpx", None)

    async def test_get_http_client_cached(self, svc):
        mock_client = AsyncMock()
        svc._http_client = mock_client
        client = await svc._get_http_client()
        assert client is mock_client

    # ── _sign_payload ──

    async def test_sign_payload_with_secret(self, svc):
        sig = svc._sign_payload('{"key":"val"}', "mysecret")
        expected = hmac.new(b"mysecret", b'{"key":"val"}', hashlib.sha256).hexdigest()
        assert sig == expected

    async def test_sign_payload_without_secret(self, svc):
        sig = svc._sign_payload("payload", None)
        assert sig is None

    async def test_sign_payload_empty_secret(self, svc):
        sig = svc._sign_payload("payload", "")
        assert sig is None

    # ── deliver ──

    async def test_deliver_success_2xx(self, svc):
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_client.post.return_value = mock_response
        svc._http_client = mock_client

        result = await svc.deliver({
            "webhook_id": "w1", "url": "https://example.com/hook",
            "payload": {"event": "test"}, "headers": {},
            "retry_count": 0, "subscription_id": None,
        })
        assert result.success is True
        assert result.status_code == 200
        assert result.webhook_id == "w1"

    async def test_deliver_failure_non_2xx(self, svc):
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_client.post.return_value = mock_response
        svc._http_client = mock_client

        result = await svc.deliver({
            "webhook_id": "w2", "url": "https://example.com/hook",
            "payload": {}, "headers": {},
            "retry_count": 0, "subscription_id": None,
        })
        assert result.success is False
        assert result.status_code == 500
        assert "HTTP 500" in result.error

    async def test_deliver_exception(self, svc):
        mock_client = AsyncMock()
        mock_client.post.side_effect = ConnectionError("network down")
        svc._http_client = mock_client

        result = await svc.deliver({
            "webhook_id": "w3", "url": "https://example.com/hook",
            "payload": {}, "headers": {},
            "retry_count": 0, "subscription_id": None,
        })
        assert result.success is False
        assert "network down" in result.error

    async def test_deliver_no_http_client(self, svc):
        svc._http_client = None
        with patch.object(svc, "_get_http_client", return_value=None):
            result = await svc.deliver({
                "webhook_id": "w4", "url": "https://example.com/hook",
                "payload": {}, "headers": {},
                "retry_count": 0, "subscription_id": None,
            })
            assert result.success is False
            assert result.error == "HTTP client unavailable"

    async def test_deliver_with_subscription_secret(self, svc):
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_client.post.return_value = mock_response
        svc._http_client = mock_client

        subs_table = MagicMock()
        subs_table.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"secret": "sub-secret"}])
        mock_supabase = MagicMock()
        mock_supabase.table.return_value = subs_table
        svc._supabase = mock_supabase

        result = await svc.deliver({
            "webhook_id": "w5", "url": "https://example.com/hook",
            "payload": {"event": "test"}, "headers": {"X-Custom": "val"},
            "retry_count": 0, "subscription_id": "sub1",
        })
        assert result.success is True
        call_kwargs = mock_client.post.call_args[1]
        assert "X-Signature-256" in call_kwargs["headers"]
        assert "X-Custom" in call_kwargs["headers"]

    async def test_deliver_subscription_secret_fetch_fails(self, svc):
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_client.post.return_value = mock_response
        svc._http_client = mock_client

        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("db fail")
        svc._supabase = mock_supabase

        result = await svc.deliver({
            "webhook_id": "w6", "url": "https://example.com/hook",
            "payload": {"event": "test"}, "headers": {},
            "retry_count": 0, "subscription_id": "sub1",
        })
        assert result.success is True

    async def test_deliver_subscription_no_supabase(self, svc):
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_client.post.return_value = mock_response
        svc._http_client = mock_client
        svc._supabase = None

        result = await svc.deliver({
            "webhook_id": "w7", "url": "https://example.com/hook",
            "payload": {"event": "test"}, "headers": {},
            "retry_count": 0, "subscription_id": "sub1",
        })
        assert result.success is True

    async def test_deliver_subscription_no_data(self, svc):
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_client.post.return_value = mock_response
        svc._http_client = mock_client

        subs_table = MagicMock()
        subs_table.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
        mock_supabase = MagicMock()
        mock_supabase.table.return_value = subs_table
        svc._supabase = mock_supabase

        result = await svc.deliver({
            "webhook_id": "w8", "url": "https://example.com/hook",
            "payload": {"event": "test"}, "headers": {},
            "retry_count": 0, "subscription_id": "sub1",
        })
        assert result.success is True

    async def test_deliver_string_payload(self, svc):
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_client.post.return_value = mock_response
        svc._http_client = mock_client

        result = await svc.deliver({
            "webhook_id": "w9", "url": "https://example.com/hook",
            "payload": "raw_string", "headers": {},
            "retry_count": 0, "subscription_id": None,
        })
        assert result.success is True

    async def test_deliver_headers_none(self, svc):
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_client.post.return_value = mock_response
        svc._http_client = mock_client

        result = await svc.deliver({
            "webhook_id": "w10", "url": "https://example.com/hook",
            "payload": {}, "headers": None,
            "retry_count": 0, "subscription_id": None,
        })
        assert result.success is True

    # ── poll_once ──

    async def test_wh_poll_once_no_supabase(self, svc):
        with patch.object(svc, "_get_supabase", return_value=None):
            d, f = await svc.poll_once()
            assert d == 0 and f == 0

    async def test_wh_poll_once_no_pending(self, svc):
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.in_.return_value.limit.return_value.order.return_value.execute.return_value.data = []
        svc._supabase = mock_supabase

        d, f = await svc.poll_once()
        assert d == 0 and f == 0

    async def test_wh_poll_once_delivers_successfully(self, svc):
        wq_table = MagicMock()
        wq_table.select.return_value.in_.return_value.limit.return_value.order.return_value.execute.return_value.data = [
            {
                "webhook_id": "wh1", "url": "https://example.com/hook",
                "payload": {"event": "test"}, "headers": {},
                "retry_count": 0, "max_retries": 5,
                "scheduled_at": None, "subscription_id": "sub1", "status": "pending",
            }
        ]

        delivering_update = MagicMock()
        delivering_update.eq.return_value.execute.return_value = MagicMock()
        delivered_update = MagicMock()
        delivered_update.eq.return_value.execute.return_value = MagicMock()
        wq_order = [delivering_update, delivered_update]

        def wq_upd_side(*a, **kw):
            return wq_order.pop(0) if wq_order else MagicMock()

        wq_table.update.side_effect = wq_upd_side

        subs_table = MagicMock()
        subs_table.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"secret": None}])
        subs_delivery_update = MagicMock()
        subs_delivery_update.eq.return_value.execute.return_value = MagicMock()
        subs_table.update.return_value = subs_delivery_update

        mock_supabase = MagicMock()

        def ts(name):
            return wq_table if name == "skill_webhook_queue" else subs_table if name == "skill_event_subscriptions" else MagicMock()

        mock_supabase.table.side_effect = ts
        svc._supabase = mock_supabase

        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_client.post.return_value = mock_response
        svc._http_client = mock_client

        d, f = await svc.poll_once()
        assert d == 1
        assert f == 0
        delivering_update.eq.assert_called_with("webhook_id", "wh1")

    async def test_wh_poll_once_delivery_failure_retry(self, svc):
        wq_table = MagicMock()
        wq_table.select.return_value.in_.return_value.limit.return_value.order.return_value.execute.return_value.data = [
            {
                "webhook_id": "wh_fail", "url": "https://example.com/hook",
                "payload": {}, "headers": {},
                "retry_count": 0, "max_retries": 5,
                "scheduled_at": None, "subscription_id": None, "status": "pending",
            }
        ]

        delivering_update = MagicMock()
        delivering_update.eq.return_value.execute.return_value = MagicMock()
        failure_update = MagicMock()
        failure_update.eq.return_value.execute.return_value = MagicMock()
        wq_order = [delivering_update, failure_update]

        def wq_upd_side(*a, **kw):
            return wq_order.pop(0) if wq_order else MagicMock()

        wq_table.update.side_effect = wq_upd_side

        mock_supabase = MagicMock()

        def ts(name):
            return wq_table if name == "skill_webhook_queue" else MagicMock()

        mock_supabase.table.side_effect = ts
        svc._supabase = mock_supabase

        svc._http_client = None
        with patch.object(svc, "_get_http_client", return_value=None):
            d, f = await svc.poll_once()
            assert d == 0
            assert f == 1

        status_call = wq_table.update.call_args_list[1]
        assert status_call[0][0]["status"] == "failed"

    async def test_wh_poll_once_dead_letter(self, svc):
        wq_table = MagicMock()
        wq_table.select.return_value.in_.return_value.limit.return_value.order.return_value.execute.return_value.data = [
            {
                "webhook_id": "wh_dead", "url": "https://example.com/hook",
                "payload": {}, "headers": {},
                "retry_count": 4, "max_retries": 5,
                "scheduled_at": None, "subscription_id": None, "status": "failed",
            }
        ]

        delivering_update = MagicMock()
        delivering_update.eq.return_value.execute.return_value = MagicMock()
        dead_letter_update = MagicMock()
        dead_letter_update.eq.return_value.execute.return_value = MagicMock()
        wq_order = [delivering_update, dead_letter_update]

        def wq_upd_side(*a, **kw):
            return wq_order.pop(0) if wq_order else MagicMock()

        wq_table.update.side_effect = wq_upd_side

        mock_supabase = MagicMock()

        def ts(name):
            return wq_table if name == "skill_webhook_queue" else MagicMock()

        mock_supabase.table.side_effect = ts
        svc._supabase = mock_supabase

        svc._http_client = None
        with patch.object(svc, "_get_http_client", return_value=None):
            d, f = await svc.poll_once()
            assert d == 0
            assert f == 1

        status_call = wq_table.update.call_args_list[1]
        assert status_call[0][0]["status"] == "dead_letter"

    async def test_wh_poll_once_skip_scheduled(self, svc):
        mock_supabase = MagicMock()
        future_ms = int(time.time() * 1000) + 60000
        wq_table = MagicMock()
        wq_table.select.return_value.in_.return_value.limit.return_value.order.return_value.execute.return_value.data = [
            {
                "webhook_id": "wh_skip", "url": "https://example.com/hook",
                "payload": {}, "headers": {},
                "retry_count": 0, "max_retries": 5,
                "scheduled_at": future_ms, "subscription_id": None, "status": "pending",
            }
        ]
        mock_supabase.table.return_value = wq_table
        svc._supabase = mock_supabase

        d, f = await svc.poll_once()
        assert d == 0 and f == 0

    async def test_wh_poll_once_exception(self, svc):
        mock_supabase = MagicMock()
        mock_supabase.table.side_effect = Exception("poll error")
        svc._supabase = mock_supabase

        d, f = await svc.poll_once()
        assert d == 0 and f == 0

    async def test_wh_poll_once_dead_letter_updates_subscriber_failures(self, svc):
        wq_table = MagicMock()
        wq_table.select.return_value.in_.return_value.limit.return_value.order.return_value.execute.return_value.data = [
            {
                "webhook_id": "wh_dead2", "url": "https://example.com/hook",
                "payload": {}, "headers": {},
                "retry_count": 4, "max_retries": 5,
                "scheduled_at": None, "subscription_id": "sub_dead2", "status": "failed",
            }
        ]

        delivering_update = MagicMock()
        delivering_update.eq.return_value.execute.return_value = MagicMock()
        dead_letter_update = MagicMock()
        dead_letter_update.eq.return_value.execute.return_value = MagicMock()
        wq_order = [delivering_update, dead_letter_update]

        def wq_upd_side(*a, **kw):
            return wq_order.pop(0) if wq_order else MagicMock()

        wq_table.update.side_effect = wq_upd_side

        subs_table = MagicMock()
        subs_failure_update = MagicMock()
        subs_failure_update.eq.return_value.execute.return_value = MagicMock()
        subs_table.update.return_value = subs_failure_update

        mock_supabase = MagicMock()

        def ts(name):
            return wq_table if name == "skill_webhook_queue" else subs_table if name == "skill_event_subscriptions" else MagicMock()

        mock_supabase.table.side_effect = ts
        svc._supabase = mock_supabase

        svc._http_client = None
        with patch.object(svc, "_get_http_client", return_value=None):
            d, f = await svc.poll_once()
            assert d == 0
            assert f == 1

        subs_failure_update.eq.assert_called_once_with("subscription_id", "sub_dead2")

    async def test_wh_poll_once_delivery_success_subscriber_count(self, svc):
        wq_table = MagicMock()
        wq_table.select.return_value.in_.return_value.limit.return_value.order.return_value.execute.return_value.data = [
            {
                "webhook_id": "wh_sub_cnt", "url": "https://example.com/hook",
                "payload": {}, "headers": {},
                "retry_count": 0, "max_retries": 5,
                "scheduled_at": None, "subscription_id": "sub_cnt", "status": "pending",
            }
        ]

        delivering_update = MagicMock()
        delivering_update.eq.return_value.execute.return_value = MagicMock()
        delivered_update = MagicMock()
        delivered_update.eq.return_value.execute.return_value = MagicMock()
        wq_order = [delivering_update, delivered_update]

        def wq_upd_side(*a, **kw):
            return wq_order.pop(0) if wq_order else MagicMock()

        wq_table.update.side_effect = wq_upd_side

        subs_table = MagicMock()
        subs_table.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"secret": None}])
        subs_delivery_update = MagicMock()
        subs_delivery_update.eq.return_value.execute.return_value = MagicMock()
        subs_table.update.return_value = subs_delivery_update

        mock_supabase = MagicMock()

        def ts(name):
            return wq_table if name == "skill_webhook_queue" else subs_table if name == "skill_event_subscriptions" else MagicMock()

        mock_supabase.table.side_effect = ts
        svc._supabase = mock_supabase

        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_client.post.return_value = mock_response
        svc._http_client = mock_client

        d, f = await svc.poll_once()
        assert d == 1
        assert f == 0
        subs_delivery_update.eq.assert_called_once_with("subscription_id", "sub_cnt")

    # ── start/stop background polling ──

    async def test_wh_start_background_polling(self, svc):
        await svc.start_background_polling()
        assert svc._running is True
        assert svc._task is not None
        await svc.stop_background_polling()

    async def test_wh_start_background_polling_already_running(self, svc):
        svc._running = True
        svc._task = asyncio.create_task(asyncio.sleep(999))
        await svc.start_background_polling()
        await svc.stop_background_polling()

    async def test_wh_stop_background_polling(self, svc):
        await svc.start_background_polling()
        await svc.stop_background_polling()
        assert svc._running is False
        assert svc._task is None

    # ── _poll_loop ──

    async def test_wh_poll_loop(self, svc):
        svc.poll_interval = 0.01
        svc._running = True
        call_count = 0

        async def mock_poll_once():
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                svc._running = False
            return (0, 0)

        svc.poll_once = mock_poll_once
        await svc._poll_loop()
        assert call_count >= 2

    async def test_wh_poll_loop_with_data(self, svc):
        svc.poll_interval = 0.01
        svc._running = True
        call_count = 0

        async def mock_poll_once():
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                svc._running = False
            return (2, 1)

        svc.poll_once = mock_poll_once
        await svc._poll_loop()

    async def test_wh_poll_loop_exception(self, svc):
        svc.poll_interval = 0.01
        svc._running = True
        call_count = 0

        async def mock_poll_once():
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                svc._running = False
                return (0, 0)
            raise ValueError("loop error")

        svc.poll_once = mock_poll_once
        await svc._poll_loop()

    # ── close ──

    async def test_close(self, svc):
        mock_client = AsyncMock()
        svc._http_client = mock_client
        await svc.close()
        assert svc._http_client is None
        assert svc._running is False

    async def test_close_no_client(self, svc):
        await svc.close()
        assert svc._running is False

    # ── get_queue_stats ──

    async def test_get_queue_stats(self, svc):
        mock_supabase = MagicMock()
        mock_result = MagicMock()
        mock_result.count = 3

        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_result
        mock_supabase.table.return_value = mock_table
        svc._supabase = mock_supabase

        stats = await svc.get_queue_stats()
        assert stats == {"pending": 3, "failed": 3, "dead_letter": 3, "delivered": 3}

    async def test_get_queue_stats_exception(self, svc):
        mock_supabase = MagicMock()
        mock_supabase.table.side_effect = Exception("error")
        svc._supabase = mock_supabase

        stats = await svc.get_queue_stats()
        assert stats == {"pending": -1, "failed": -1, "dead_letter": -1, "delivered": -1}

    async def test_get_queue_stats_no_supabase(self, svc):
        with patch.object(svc, "_get_supabase", return_value=None):
            stats = await svc.get_queue_stats()
            assert stats == {"pending": 0, "failed": 0, "dead_letter": 0, "delivered": 0}

    # ── global webhook_delivery ──

    async def test_global_webhook_delivery(self):
        from shared.utils.webhook_delivery import webhook_delivery

        assert webhook_delivery is not None


# =============================================================================
#  notifications.py
# =============================================================================


class TestSendEmail:
    def test_no_api_key_fallback(self):
        with patch("shared.utils.notifications.os.getenv", return_value=None):
            from shared.utils.notifications import send_email

            result = send_email("user@test.com", "Subject", "Body text")
            assert result["success"] is True
            assert result["message_id"] is None

    def test_success(self):
        mock_resp = MagicMock()
        mock_resp.is_success = True
        mock_resp.json.return_value = {"id": "email_123"}

        with patch("shared.utils.notifications.os.getenv", side_effect=lambda k, d=None: {
            "RESEND_API_KEY": "re_abc123",
            "RESEND_FROM_EMAIL": "test@test.com",
        }.get(k, d)):
            with patch("shared.utils.notifications.httpx.post", return_value=mock_resp):
                from shared.utils.notifications import send_email

                result = send_email("user@test.com", "Subject", "Body text", html_body="<p>HTML</p>")
                assert result["success"] is True
                assert result["message_id"] == "email_123"

    def test_api_error(self):
        mock_resp = MagicMock()
        mock_resp.is_success = False
        mock_resp.status_code = 400
        mock_resp.text = "Bad request"

        with patch("shared.utils.notifications.os.getenv", side_effect=lambda k, d=None: {
            "RESEND_API_KEY": "re_abc",
            "RESEND_FROM_EMAIL": "test@test.com",
        }.get(k, d)):
            with patch("shared.utils.notifications.httpx.post", return_value=mock_resp):
                from shared.utils.notifications import send_email

                result = send_email("user@test.com", "Subject", "Body")
                assert result["success"] is False
                assert "Resend API error 400" in result["error"]

    def test_timeout(self):
        from shared.utils.notifications import httpx

        with patch("shared.utils.notifications.os.getenv", side_effect=lambda k, d=None: {
            "RESEND_API_KEY": "re_abc",
            "RESEND_FROM_EMAIL": "test@test.com",
        }.get(k, d)):
            with patch("shared.utils.notifications.httpx.post", side_effect=httpx.TimeoutException("timeout")):
                from shared.utils.notifications import send_email

                result = send_email("user@test.com", "Subject", "Body")
                assert result["success"] is False
                assert "timed out" in result["error"]

    def test_generic_exception(self):
        with patch("shared.utils.notifications.os.getenv", side_effect=lambda k, d=None: {
            "RESEND_API_KEY": "re_abc",
            "RESEND_FROM_EMAIL": "test@test.com",
        }.get(k, d)):
            with patch("shared.utils.notifications.httpx.post", side_effect=ConnectionError("network fail")):
                from shared.utils.notifications import send_email

                result = send_email("user@test.com", "Subject", "Body")
                assert result["success"] is False
                assert result["error"] == "network fail"

    def test_html_body(self):
        mock_resp = MagicMock()
        mock_resp.is_success = True
        mock_resp.json.return_value = {"id": "e1"}

        with patch("shared.utils.notifications.os.getenv", side_effect=lambda k, d=None: {
            "RESEND_API_KEY": "re_abc",
            "RESEND_FROM_EMAIL": "test@test.com",
        }.get(k, d)):
            with patch("shared.utils.notifications.httpx.post", return_value=mock_resp) as mock_post:
                from shared.utils.notifications import send_email

                send_email("user@test.com", "Subject", "Body", html_body="<h1>HTML</h1>")
                call_args = mock_post.call_args[1]["json"]
                assert call_args["html"] == "<h1>HTML</h1>"
                assert call_args["text"] == "Body"


class TestSendPushNotification:
    def test_no_webhook_url_fallback(self):
        with patch("shared.utils.notifications.os.getenv", return_value=None):
            from shared.utils.notifications import send_push_notification

            result = send_push_notification("user1", "Title", "Body")
            assert result["success"] is True
            assert result["message_id"] is None

    def test_success(self):
        mock_resp = MagicMock()
        mock_resp.is_success = True
        mock_resp.json.return_value = {"id": "push_1"}

        with patch("shared.utils.notifications.os.getenv", return_value="https://push.example.com"):
            with patch("shared.utils.notifications.httpx.post", return_value=mock_resp):
                from shared.utils.notifications import send_push_notification

                result = send_push_notification("user1", "Title", "Body")
                assert result["success"] is True
                assert result["message_id"] == "push_1"

    def test_success_with_data(self):
        mock_resp = MagicMock()
        mock_resp.is_success = True
        mock_resp.json.return_value = {"id": "push_d1"}

        with patch("shared.utils.notifications.os.getenv", return_value="https://push.example.com"):
            with patch("shared.utils.notifications.httpx.post", return_value=mock_resp) as mock_post:
                from shared.utils.notifications import send_push_notification

                result = send_push_notification("user1", "Title", "Body", data={"type": "alert", "count": 3})
                assert result["success"] is True
                call_args = mock_post.call_args[1]["json"]
                assert call_args["data"] == {"type": "alert", "count": 3}

    def test_api_error(self):
        mock_resp = MagicMock()
        mock_resp.is_success = False
        mock_resp.status_code = 403
        mock_resp.text = "Forbidden"

        with patch("shared.utils.notifications.os.getenv", return_value="https://push.example.com"):
            with patch("shared.utils.notifications.httpx.post", return_value=mock_resp):
                from shared.utils.notifications import send_push_notification

                result = send_push_notification("user1", "Title", "Body")
                assert result["success"] is False
                assert "Push webhook error 403" in result["error"]

    def test_timeout(self):
        from shared.utils.notifications import httpx

        with patch("shared.utils.notifications.os.getenv", return_value="https://push.example.com"):
            with patch("shared.utils.notifications.httpx.post", side_effect=httpx.TimeoutException("timeout")):
                from shared.utils.notifications import send_push_notification

                result = send_push_notification("user1", "Title", "Body")
                assert result["success"] is False
                assert "timed out" in result["error"]

    def test_exception(self):
        with patch("shared.utils.notifications.os.getenv", return_value="https://push.example.com"):
            with patch("shared.utils.notifications.httpx.post", side_effect=ValueError("bad")):
                from shared.utils.notifications import send_push_notification

                result = send_push_notification("user1", "Title", "Body")
                assert result["success"] is False
                assert "bad" in result["error"]


class TestSendSms:
    def test_no_creds_fallback(self):
        with patch("shared.utils.notifications.os.getenv", return_value=None):
            from shared.utils.notifications import send_sms

            result = send_sms("+1234567890", "Hello")
            assert result["success"] is True
            assert result["message_id"] is None

    def test_success(self):
        mock_resp = MagicMock()
        mock_resp.is_success = True
        mock_resp.json.return_value = {"sid": "SM123"}

        with patch("shared.utils.notifications.os.getenv", side_effect=lambda k, d=None: {
            "TWILIO_ACCOUNT_SID": "ACxxx",
            "TWILIO_AUTH_TOKEN": "token123",
            "TWILIO_FROM_NUMBER": "+1555",
        }.get(k, d)):
            with patch("shared.utils.notifications.httpx.post", return_value=mock_resp):
                from shared.utils.notifications import send_sms

                result = send_sms("+1234567890", "Hello")
                assert result["success"] is True
                assert result["message_id"] == "SM123"

    def test_api_error(self):
        mock_resp = MagicMock()
        mock_resp.is_success = False
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized"

        with patch("shared.utils.notifications.os.getenv", side_effect=lambda k, d=None: {
            "TWILIO_ACCOUNT_SID": "ACxxx",
            "TWILIO_AUTH_TOKEN": "token123",
        }.get(k, d)):
            with patch("shared.utils.notifications.httpx.post", return_value=mock_resp):
                from shared.utils.notifications import send_sms

                result = send_sms("+1234567890", "Hello")
                assert result["success"] is False
                assert "Twilio API error 401" in result["error"]

    def test_timeout(self):
        from shared.utils.notifications import httpx

        with patch("shared.utils.notifications.os.getenv", side_effect=lambda k, d=None: {
            "TWILIO_ACCOUNT_SID": "ACxxx",
            "TWILIO_AUTH_TOKEN": "token123",
        }.get(k, d)):
            with patch("shared.utils.notifications.httpx.post", side_effect=httpx.TimeoutException("timeout")):
                from shared.utils.notifications import send_sms

                result = send_sms("+1234567890", "Hello")
                assert result["success"] is False
                assert "timed out" in result["error"]

    def test_exception(self):
        with patch("shared.utils.notifications.os.getenv", side_effect=lambda k, d=None: {
            "TWILIO_ACCOUNT_SID": "ACxxx",
            "TWILIO_AUTH_TOKEN": "token123",
        }.get(k, d)):
            with patch("shared.utils.notifications.httpx.post", side_effect=RuntimeError("fail")):
                from shared.utils.notifications import send_sms

                result = send_sms("+1234567890", "Hello")
                assert result["success"] is False
                assert "fail" in result["error"]


class TestSendNotification:
    def test_email_type(self):
        with patch("shared.utils.notifications.send_email", return_value={"done": True}) as mock_fn:
            from shared.utils.notifications import send_notification

            result = send_notification("email", "user@test.com", "Sub", "Body", html_body="<p>Hi</p>")
            assert result == {"done": True}
            mock_fn.assert_called_with("user@test.com", "Sub", "Body", html_body="<p>Hi</p>")

    def test_push_type(self):
        with patch("shared.utils.notifications.send_push_notification", return_value={"done": True}) as mock_fn:
            from shared.utils.notifications import send_notification

            result = send_notification("push", "user1", "Title", "Body", data={"key": "val"})
            assert result == {"done": True}
            mock_fn.assert_called_with("user1", "Title", "Body", data={"key": "val"})

    def test_sms_type(self):
        with patch("shared.utils.notifications.send_sms", return_value={"done": True}) as mock_fn:
            from shared.utils.notifications import send_notification

            result = send_notification("sms", "+1234", "Sub", "Hello")
            assert result == {"done": True}
            mock_fn.assert_called_with("+1234", "Hello")

    def test_unknown_type(self):
        from shared.utils.notifications import send_notification

        result = send_notification("fax", "recipient", "Sub", "Body")
        assert result["success"] is False
        assert "Unknown notification type: fax" in result["error"]


class TestNotificationDelegates:
    def test_send_email_notification(self):
        with patch("shared.utils.notifications.send_email", return_value={"sent": True}) as mock_fn:
            from shared.utils.notifications import send_email_notification

            result = send_email_notification("a@b.com", "Sub", "Body")
            assert result == {"sent": True}
            mock_fn.assert_called_with("a@b.com", "Sub", "Body")

    def test_send_sms_notification(self):
        with patch("shared.utils.notifications.send_sms", return_value={"sent": True}) as mock_fn:
            from shared.utils.notifications import send_sms_notification

            result = send_sms_notification("+1234", "Msg")
            assert result == {"sent": True}
            mock_fn.assert_called_with("+1234", "Msg")


class TestNotifyHelpers:
    def test_notify_task_overdue(self):
        with patch("shared.utils.notifications.send_email_notification") as mock_fn:
            from shared.utils.notifications import notify_task_overdue

            notify_task_overdue("Finish homework", "user@test.com")
            mock_fn.assert_called_with(
                "user@test.com",
                "Overdue Task: Finish homework",
                "Your task 'Finish homework' is overdue. Please complete or reschedule it.",
            )

    def test_notify_critical_alert(self):
        with patch("shared.utils.notifications.send_sms_notification") as mock_fn:
            from shared.utils.notifications import notify_critical_alert

            notify_critical_alert("Server down", "+1234567890")
            mock_fn.assert_called_with("+1234567890", "ALERT: Server down")

    def test_notify_habit_missed(self):
        with patch("shared.utils.notifications.send_email_notification") as mock_fn:
            from shared.utils.notifications import notify_habit_missed

            notify_habit_missed("Morning run", "user@test.com")
            mock_fn.assert_called_with(
                "user@test.com",
                "Habit Missed: Morning run",
                "You missed your habit 'Morning run' today. Don't worry, tomorrow is a new day!",
            )

    def test_notify_bedtime_reminder(self):
        with patch("shared.utils.notifications.send_email_notification") as mock_fn:
            from shared.utils.notifications import notify_bedtime_reminder

            notify_bedtime_reminder("user@test.com", "10:00 PM")
            mock_fn.assert_called_with(
                "user@test.com",
                "Bedtime Reminder",
                "It's 10:00 PM. Time to start winding down for a good night's sleep.",
            )


class TestNotificationTypes:
    def test_notification_types_dict(self):
        from shared.utils.notifications import NOTIFICATION_TYPES

        assert NOTIFICATION_TYPES["email"] == "email"
        assert NOTIFICATION_TYPES["push"] == "push"
        assert NOTIFICATION_TYPES["sms"] == "sms"
        assert len(NOTIFICATION_TYPES) == 3


# =============================================================================
#  neo4j_sync.py
# =============================================================================


class TestNeo4jConstants:
    def test_node_label_map(self):
        from shared.utils.neo4j_sync import NODE_LABEL_MAP

        assert "Skill" in NODE_LABEL_MAP
        assert NODE_LABEL_MAP["Skill"] == "skills"
        assert len(NODE_LABEL_MAP) == 13

    def test_relationship_type_map(self):
        from shared.utils.neo4j_sync import RELATIONSHIP_TYPE_MAP

        assert RELATIONSHIP_TYPE_MAP["prerequisite"] == "DEPENDS_ON"
        assert len(RELATIONSHIP_TYPE_MAP) == 8


class TestNeo4jSyncService:
    """Neo4jSyncService — init, initialize, close, _ensure_enabled, _run, sync, bulk, rebuild, queries."""

    @pytest.fixture
    def svc(self):
        from shared.utils.neo4j_sync import Neo4jSyncService

        return Neo4jSyncService()

    @pytest.fixture
    def enabled_svc(self, svc):
        """Service with _enabled=True and a working mock driver."""
        svc._enabled = True
        svc._driver = MagicMock()
        mock_session = MagicMock()
        svc._driver.session.return_value.__aenter__.return_value = mock_session
        svc._driver.session.return_value.__aexit__.return_value = None
        return svc

    def _set_run(self, enabled_svc, records=None):
        """Configure session.run with an async side_effect that returns the given records."""
        mock_session = enabled_svc._driver.session.return_value.__aenter__.return_value
        mock_session.run.side_effect = _make_async_run(records or [])
        return mock_session

    # ── __init__ ──

    def test_init(self):
        from shared.utils.neo4j_sync import Neo4jSyncService

        s = Neo4jSyncService()
        assert s._enabled is False
        assert s._driver is None
        assert s._retry_count == 0

    # ── initialize ──

    async def test_initialize_no_uri(self, svc):
        with patch("shared.utils.neo4j_sync.os.getenv", return_value=None):
            await svc.initialize()
            assert svc._enabled is False

    async def test_initialize_no_password(self, svc):
        with patch(
            "shared.utils.neo4j_sync.os.getenv",
            side_effect=lambda k, d=None: "bolt://localhost:7687" if k == "NEO4J_URI" else d,
        ):
            await svc.initialize()
            assert svc._enabled is False

    async def test_initialize_import_fails(self, svc):
        with patch("shared.utils.neo4j_sync.os.getenv", side_effect=lambda k, d=None: {
            "NEO4J_URI": "bolt://localhost:7687",
            "NEO4J_USER": "neo4j",
            "NEO4J_PASSWORD": "secret",
        }.get(k, d)):
            import sys as _sys
            orig = _sys.modules.pop("neo4j", None)
            _sys.modules["neo4j"] = None
            try:
                await svc.initialize()
                assert svc._enabled is False
            finally:
                if orig:
                    _sys.modules["neo4j"] = orig
                else:
                    _sys.modules.pop("neo4j", None)

    async def test_initialize_connection_succeeds(self, svc):
        mock_session = AsyncMock()
        mock_session.run = AsyncMock()
        mock_driver = MagicMock()
        mock_driver.session.return_value.__aenter__.return_value = mock_session
        mock_driver.session.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_gdb = MagicMock()
        mock_gdb.driver.return_value = mock_driver

        import sys as _sys
        _sys.modules["neo4j"] = MagicMock()
        _sys.modules["neo4j"].GraphDatabase = mock_gdb

        with patch("shared.utils.neo4j_sync.os.getenv", side_effect=lambda k, d=None: {
            "NEO4J_URI": "bolt://localhost:7687",
            "NEO4J_USER": "neo4j",
            "NEO4J_PASSWORD": "secret",
        }.get(k, d)):
            await svc.initialize()
            assert svc._enabled is True

    async def test_initialize_connection_fails(self, svc):
        mock_gdb = MagicMock()
        mock_gdb.driver.side_effect = Exception("connection refused")

        import sys as _sys
        _sys.modules["neo4j"] = MagicMock()
        _sys.modules["neo4j"].GraphDatabase = mock_gdb

        with patch("shared.utils.neo4j_sync.os.getenv", side_effect=lambda k, d=None: {
            "NEO4J_URI": "bolt://localhost:7687",
            "NEO4J_USER": "neo4j",
            "NEO4J_PASSWORD": "secret",
        }.get(k, d)):
            await svc.initialize()
            assert svc._enabled is False

    # ── close ──

    async def test_close_with_driver(self, svc):
        mock_driver = AsyncMock()
        svc._driver = mock_driver
        svc._enabled = True
        await svc.close()
        mock_driver.close.assert_awaited_once()
        assert svc._driver is None
        assert svc._enabled is False

    async def test_close_without_driver(self, svc):
        await svc.close()
        assert svc._driver is None

    # ── _ensure_enabled ──

    async def test_ensure_enabled_true(self, svc):
        svc._enabled = True
        assert svc._ensure_enabled() is True

    async def test_ensure_enabled_false(self, svc):
        assert svc._ensure_enabled() is False

    # ── _run ──

    async def test_run_disabled(self, svc):
        result = await svc._run("MATCH (n) RETURN n")
        assert result == []

    async def test_run_success(self, enabled_svc):
        records = [{"name": "Python", "id": "1"}, {"name": "JavaScript", "id": "2"}]
        self._set_run(enabled_svc, records)
        result = await enabled_svc._run("MATCH (n) RETURN n")
        assert result == records

    async def test_run_exception(self, enabled_svc):
        mock_session = enabled_svc._driver.session.return_value.__aenter__.return_value
        mock_session.run.side_effect = Exception("query failed")
        enabled_svc._retry_count = 0

        result = await enabled_svc._run("BAD QUERY")
        assert result == []
        assert enabled_svc._retry_count == 1

    async def test_run_five_retries_disables(self, enabled_svc):
        mock_session = enabled_svc._driver.session.return_value.__aenter__.return_value
        mock_session.run.side_effect = Exception("persistent failure")
        enabled_svc._retry_count = 5

        result = await enabled_svc._run("BAD QUERY")
        assert result == []
        assert enabled_svc._enabled is False

    # ── sync_skill_node ──

    async def test_sync_skill_node(self, enabled_svc):
        mock_session = self._set_run(enabled_svc)
        await enabled_svc.sync_skill_node({
            "skill_id": "s1", "name": "Python", "slug": "python",
            "category_id": "c1", "description": "Lang", "level_min": 1,
            "level_max": 5, "skill_health": 0.9, "is_deprecated": False,
            "updated_at": 1000,
        })
        mock_session.run.assert_called_once()

    # ── sync_category_node ──

    async def test_sync_category_node(self, enabled_svc):
        mock_session = self._set_run(enabled_svc)
        await enabled_svc.sync_category_node({
            "category_id": "c1", "name": "Backend", "slug": "backend",
            "description": "Backend skills", "parent_category_id": None,
            "level": 1, "is_active": True, "sort_order": 0,
        })
        mock_session.run.assert_called_once()

    # ── sync_user_node ──

    async def test_sync_user_node_with_email(self, enabled_svc):
        mock_session = self._set_run(enabled_svc)
        await enabled_svc.sync_user_node({
            "id": "u1", "org_id": "org1", "email": "user@test.com",
            "settings": {"theme": "dark"},
        })
        mock_session.run.assert_called_once()
        params = mock_session.run.call_args[0][1]
        assert params["email_hash"] is not None
        assert "settings" in params

    async def test_sync_user_node_no_email(self, enabled_svc):
        mock_session = self._set_run(enabled_svc)
        await enabled_svc.sync_user_node({
            "id": "u2", "org_id": "org2", "settings": {},
        })
        params = mock_session.run.call_args[0][1]
        assert params["email_hash"] is None

    # ── sync_user_skill_node ──

    async def test_sync_user_skill_node(self, enabled_svc):
        mock_session = self._set_run(enabled_svc)
        await enabled_svc.sync_user_skill_node({
            "user_skill_id": "us1", "user_id": "u1", "skill_id": "s1",
            "level": 3, "state": "active", "confidence_score": 0.8,
            "evidence_score": 0.7, "level_change_90d": 0.5,
            "is_emerging": False, "is_stale": False, "last_activity_at": 1000,
        })
        mock_session.run.assert_called_once()

    # ── sync_evidence_node ──

    async def test_sync_evidence_node(self, enabled_svc):
        mock_session = self._set_run(enabled_svc)
        await enabled_svc.sync_evidence_node({
            "evidence_id": "e1", "user_skill_id": "us1", "user_id": "u1",
            "source_type": "quiz", "state": "verified", "title": "Quiz 90%",
            "quality_score": 0.9, "trust_score": 0.8,
            "weight": 1.0, "collected_at": 1000,
        })
        mock_session.run.assert_called_once()

    # ── sync_target_node ──

    async def test_sync_target_node(self, enabled_svc):
        mock_session = self._set_run(enabled_svc)
        await enabled_svc.sync_target_node({
            "target_id": "t1", "user_skill_id": "us1", "user_id": "u1",
            "target_level": 5, "current_level": 2, "priority": "high",
            "status": "active", "gap_size": 3, "progress_pct": 40.0,
        })
        mock_session.run.assert_called_once()

    # ── sync_assessment_node ──

    async def test_sync_assessment_node(self, enabled_svc):
        mock_session = self._set_run(enabled_svc)
        await enabled_svc.sync_assessment_node({
            "assessment_id": "a1", "user_skill_id": "us1", "user_id": "u1",
            "assessment_type": "quiz", "score": 85, "level_achieved": 3,
            "confidence": 0.9, "status": "completed",
        })
        mock_session.run.assert_called_once()

    # ── sync_belongs_to ──

    async def test_sync_belongs_to(self, enabled_svc):
        mock_session = self._set_run(enabled_svc)
        await enabled_svc.sync_belongs_to({"skill_id": "s1", "category_id": "c1"})
        mock_session.run.assert_called_once()

    async def test_sync_belongs_to_no_category(self, enabled_svc):
        mock_session = self._set_run(enabled_svc)
        await enabled_svc.sync_belongs_to({"skill_id": "s1", "category_id": None})
        mock_session.run.assert_not_called()

    # ── sync_user_skill_edges ──

    async def test_sync_user_skill_edges(self, enabled_svc):
        mock_session = self._set_run(enabled_svc)
        await enabled_svc.sync_user_skill_edges({"user_id": "u1", "skill_id": "s1", "user_skill_id": "us1"})
        mock_session.run.assert_called_once()

    # ── sync_evidence_edges ──

    async def test_sync_evidence_edges(self, enabled_svc):
        mock_session = self._set_run(enabled_svc)
        await enabled_svc.sync_evidence_edges({"user_skill_id": "us1", "evidence_id": "e1"})
        mock_session.run.assert_called_once()

    # ── sync_target_edges ──

    async def test_sync_target_edges(self, enabled_svc):
        mock_session = self._set_run(enabled_svc)
        await enabled_svc.sync_target_edges({"user_skill_id": "us1", "target_id": "t1"})
        mock_session.run.assert_called_once()

    # ── sync_assessment_edges ──

    async def test_sync_assessment_edges(self, enabled_svc):
        mock_session = self._set_run(enabled_svc)
        await enabled_svc.sync_assessment_edges({"user_skill_id": "us1", "assessment_id": "a1"})
        mock_session.run.assert_called_once()

    # ── sync_relationship_edge ──

    async def test_sync_relationship_edge(self, enabled_svc):
        mock_session = self._set_run(enabled_svc)
        await enabled_svc.sync_relationship_edge({
            "relationship_type": "prerequisite", "from_skill_id": "s1", "to_skill_id": "s2",
            "weight": 0.8, "min_level_from": 1, "min_level_to": 2, "is_directed": True,
        })
        query = mock_session.run.call_args[0][0]
        assert "DEPENDS_ON" in query

    async def test_sync_relationship_edge_default_type(self, enabled_svc):
        mock_session = self._set_run(enabled_svc)
        await enabled_svc.sync_relationship_edge({
            "relationship_type": "unknown_type", "from_skill_id": "s1", "to_skill_id": "s2",
            "weight": 1.0, "is_directed": True,
        })
        query = mock_session.run.call_args[0][0]
        assert "RELATED_TO" in query

    # ── delete_node ──

    async def test_delete_node(self, enabled_svc):
        mock_session = self._set_run(enabled_svc)
        await enabled_svc.delete_node("Skill", "skill_id", "s1")
        mock_session.run.assert_called_once()
        query = mock_session.run.call_args[0][0]
        assert "DETACH DELETE" in query
        params = mock_session.run.call_args[0][1]
        assert params["node_id"] == "s1"

    # ── bulk_sync_skills ──

    async def test_bulk_sync_skills(self, enabled_svc):
        mock_session = self._set_run(enabled_svc)
        await enabled_svc.bulk_sync_skills([
            {"skill_id": "s1", "category_id": "c1"},
            {"skill_id": "s2", "category_id": "c2"},
        ])
        assert mock_session.run.call_count == 4

    # ── bulk_sync_relationships ──

    async def test_bulk_sync_relationships(self, enabled_svc):
        mock_session = self._set_run(enabled_svc)
        await enabled_svc.bulk_sync_relationships([
            {"relationship_type": "prerequisite", "from_skill_id": "s1", "to_skill_id": "s2"},
        ])
        assert mock_session.run.call_count == 1

    # ── bulk_sync_user_skills ──

    async def test_bulk_sync_user_skills(self, enabled_svc):
        mock_session = self._set_run(enabled_svc)
        await enabled_svc.bulk_sync_user_skills([
            {"user_skill_id": "us1", "user_id": "u1", "skill_id": "s1"},
        ])
        assert mock_session.run.call_count == 2

    # ── full_rebuild ──

    async def test_full_rebuild(self, enabled_svc):
        mock_session = self._set_run(enabled_svc)
        await enabled_svc.full_rebuild(
            skills=[{"skill_id": "s1", "category_id": "c1"}],
            categories=[{"category_id": "c1"}],
            relationships=[{"from_skill_id": "s1", "to_skill_id": "s2"}],
            user_skills=[{"user_skill_id": "us1", "user_id": "u1", "skill_id": "s1"}],
            evidence=[{"evidence_id": "e1", "user_skill_id": "us1"}],
            targets=[{"target_id": "t1", "user_skill_id": "us1"}],
            assessments=[{"assessment_id": "a1", "user_skill_id": "us1"}],
        )
        assert mock_session.run.call_count == 13

    # ── find_related_skills ──

    async def test_find_related_skills(self, enabled_svc):
        records = [{"skill_id": "s2", "name": "JS", "depth": 1, "rel_types": ["RELATED_TO"], "cumulative_weight": 0.8}]
        self._set_run(enabled_svc, records)
        results = await enabled_svc.find_related_skills("s1", max_depth=3)
        assert len(results) == 1
        mock_session = enabled_svc._driver.session.return_value.__aenter__.return_value
        params = mock_session.run.call_args[0][1]
        assert params["skill_id"] == "s1"
        assert params["max_depth"] == 3

    # ── recommend_skills ──

    async def test_recommend_skills(self, enabled_svc):
        records = [{"skill_id": "s3", "name": "React", "connection_strength": 5, "avg_weight": 0.9, "skill_health": 0.95}]
        self._set_run(enabled_svc, records)
        results = await enabled_svc.recommend_skills("u1", limit=10)
        assert len(results) == 1
        mock_session = enabled_svc._driver.session.return_value.__aenter__.return_value
        params = mock_session.run.call_args[0][1]
        assert params["user_id"] == "u1"
        assert params["limit"] == 10

    # ── find_learning_path ──

    async def test_find_learning_path(self, enabled_svc):
        records = [{"skill_names": ["A", "B"], "skill_ids": ["s1", "s2"], "steps": 1}]
        self._set_run(enabled_svc, records)
        results = await enabled_svc.find_learning_path("u1", "s2")
        assert len(results) == 1

    # ── find_similar_users ──

    async def test_find_similar_users(self, enabled_svc):
        records = [{"similar_user_id": "u2", "common_skills": 3, "avg_level": 2.5}]
        self._set_run(enabled_svc, records)
        results = await enabled_svc.find_similar_users("u1", limit=20)
        assert len(results) == 1

    # ── get_graph_statistics ──

    async def test_get_graph_statistics(self, enabled_svc):
        mock_session = enabled_svc._driver.session.return_value.__aenter__.return_value
        calls = {
            "total_nodes": [{"total_nodes": 50}],
            "total_relationships": [{"total_relationships": 120}],
            "labels": [{"labels": ["Skill"], "count": 30}, {"labels": ["Category"], "count": 10}],
        }

        async def run_side(query, params=None):
            for key, value in calls.items():
                if key in query:
                    return _async_iter(*value)
            return _async_iter()

        mock_session.run.side_effect = run_side

        stats = await enabled_svc.get_graph_statistics()
        assert stats["total_nodes"] == 50
        assert stats["total_relationships"] == 120
        assert stats["node_distribution"]["Skill"] == 30

    async def test_get_graph_statistics_empty(self, enabled_svc):
        mock_session = enabled_svc._driver.session.return_value.__aenter__.return_value
        mock_session.run.side_effect = _make_async_run([])
        stats = await enabled_svc.get_graph_statistics()
        assert stats["total_nodes"] == 0
        assert stats["total_relationships"] == 0
        assert stats["node_distribution"] == {}

    # ── global neo4j_sync ──

    async def test_global_neo4j_sync(self):
        from shared.utils.neo4j_sync import graph_sync

        assert graph_sync is not None
        assert graph_sync._enabled is False
