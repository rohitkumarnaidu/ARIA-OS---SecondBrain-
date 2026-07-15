"""Tests for shared/utils/webhook_delivery.py — WebhookDeliveryService."""

import asyncio
import time
from unittest.mock import MagicMock, AsyncMock, patch
import pytest
from shared.utils.webhook_delivery import WebhookDeliveryService


@pytest.fixture
def service():
    svc = WebhookDeliveryService(poll_interval=0.1, batch_size=10, request_timeout=5)
    svc._supabase = MagicMock()
    return svc


class TestWebhookDeliveryService:
    def test_init(self):
        svc = WebhookDeliveryService(poll_interval=5.0, batch_size=20, request_timeout=10)
        assert svc.poll_interval == 5.0
        assert svc.batch_size == 20
        assert svc.request_timeout == 10
        assert not svc._running
        assert svc._task is None

    def test_get_supabase_uses_cached(self, service):
        cached = service._supabase
        result = service._get_supabase()
        assert result is cached

    def test_get_supabase_creates_new(self):
        svc = WebhookDeliveryService()
        with patch("config.core.supabase.get_supabase_client", return_value=MagicMock()):
            result = svc._get_supabase()
            assert result is not None
            assert svc._supabase is result

    def test_get_supabase_error_returns_none(self):
        svc = WebhookDeliveryService()
        with patch("config.core.supabase.get_supabase_client", side_effect=Exception("DB down")):
            result = svc._get_supabase()
            assert result is None

    def test_sign_payload_with_secret(self, service):
        sig = service._sign_payload('{"key":"value"}', "mysecret")
        assert sig is not None
        assert isinstance(sig, str)
        assert len(sig) == 64

    def test_sign_payload_without_secret(self, service):
        sig = service._sign_payload('{"key":"value"}', None)
        assert sig is None

    @pytest.mark.asyncio
    async def test_get_http_client_creates(self, service):
        with patch("httpx.AsyncClient") as mock_cls:
            client = await service._get_http_client()
            assert client is not None
            mock_cls.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_http_client_cached(self, service):
        with patch("httpx.AsyncClient") as mock_cls:
            await service._get_http_client()
            await service._get_http_client()
            mock_cls.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_http_client_no_httpx(self, service):
        with patch.dict("sys.modules", {"httpx": None}):
            result = await service._get_http_client()
            assert result is None

    @pytest.mark.asyncio
    async def test_deliver_success(self, service):
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response
        service._http_client = mock_client

        result = await service.deliver({
            "webhook_id": "wh1",
            "url": "https://example.com/hook",
            "payload": {"event": "test"},
            "headers": {"X-Custom": "val1"},
        })
        assert result.success is True
        assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_deliver_http_error(self, service):
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_client.post.return_value = mock_response
        service._http_client = mock_client

        result = await service.deliver({
            "webhook_id": "wh2",
            "url": "https://example.com/hook",
            "payload": {},
        })
        assert result.success is False
        assert result.status_code == 500

    @pytest.mark.asyncio
    async def test_deliver_exception(self, service):
        mock_client = AsyncMock()
        mock_client.post.side_effect = Exception("Connection refused")
        service._http_client = mock_client

        result = await service.deliver({
            "webhook_id": "wh3",
            "url": "https://example.com/hook",
            "payload": {},
        })
        assert result.success is False
        assert "Connection refused" in result.error

    @pytest.mark.asyncio
    async def test_deliver_no_http_client(self, service):
        service._http_client = None
        with patch.object(service, "_get_http_client", AsyncMock(return_value=None)):
            result = await service.deliver({
                "webhook_id": "wh4",
                "url": "https://example.com/hook",
                "payload": {},
            })
            assert result.success is False
            assert "HTTP client unavailable" in result.error

    @pytest.mark.asyncio
    async def test_poll_once_no_data(self, service):
        service._supabase.table.return_value.select.return_value.in_.return_value.limit.return_value.order.return_value.execute.return_value = MagicMock(data=[])
        delivered, failed = await service.poll_once()
        assert delivered == 0
        assert failed == 0

    @pytest.mark.asyncio
    async def test_poll_once_no_supabase(self):
        svc = WebhookDeliveryService()
        delivered, failed = await svc.poll_once()
        assert delivered == 0
        assert failed == 0

    @pytest.mark.asyncio
    async def test_poll_once_delivers(self, service):
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response
        service._http_client = mock_client

        service._supabase.table.return_value.select.return_value.in_.return_value.limit.return_value.order.return_value.execute.return_value = MagicMock(
            data=[{"webhook_id": "wh1", "url": "https://example.com/hook", "payload": {"event": "t"}, "retry_count": 0, "max_retries": 5, "scheduled_at": 0}]
        )
        delivered, failed = await service.poll_once()
        assert delivered == 1
        assert failed == 0

    @pytest.mark.asyncio
    async def test_poll_once_exception(self, service):
        service._supabase.table.return_value.select.side_effect = Exception("DB error")
        delivered, failed = await service.poll_once()
        assert delivered == 0
        assert failed == 0

    @pytest.mark.asyncio
    async def test_start_background_polling(self, service):
        await service.start_background_polling()
        assert service._running is True
        assert service._task is not None
        await service.stop_background_polling()

    @pytest.mark.asyncio
    async def test_start_twice_does_nothing(self, service):
        service._running = True
        service._task = AsyncMock()
        await service.start_background_polling()

    @pytest.mark.asyncio
    async def test_stop_background_polling_not_running(self, service):
        await service.stop_background_polling()
        assert service._task is None

    @pytest.mark.asyncio
    async def test_stop_background_polling_cancels_task(self, service):
        service._running = True
        service._task = asyncio.create_task(asyncio.sleep(999))
        await service.stop_background_polling()
        assert service._task is None

    @pytest.mark.asyncio
    async def test_close(self, service):
        mock_client = AsyncMock()
        service._http_client = mock_client
        await service.close()
        mock_client.aclose.assert_awaited_once()
        assert service._http_client is None

    @pytest.mark.asyncio
    async def test_get_queue_stats(self, service):
        def select_side_effect(*args, **kwargs):
            m = MagicMock()
            m.count = 5
            m.data = []
            return m
        service._supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = select_side_effect
        stats = await service.get_queue_stats()
        assert stats["pending"] == 5

    @pytest.mark.asyncio
    async def test_get_queue_stats_no_supabase(self):
        svc = WebhookDeliveryService()
        svc._supabase = None
        with patch.object(svc, "_get_supabase", return_value=None):
            stats = await svc.get_queue_stats()
        assert stats["pending"] == 0

    @pytest.mark.asyncio
    async def test_get_queue_stats_exception(self, service):
        service._supabase.table.side_effect = Exception("error")
        stats = await service.get_queue_stats()
        assert stats["pending"] == -1

    @pytest.mark.asyncio
    async def test_deliver_with_subscription_secret(self, service):
        """Cover lines 108-118: subscription secret fetch sets secret for signing."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response
        service._http_client = mock_client

        sub_data = [{"secret": "test-secret-key"}]
        service._supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=sub_data)

        result = await service.deliver({
            "webhook_id": "wh-sec",
            "url": "https://example.com/hook",
            "payload": {"event": "test"},
            "headers": {"X-Custom": "val1"},
            "subscription_id": "sub-1",
        })
        assert result.success is True
        assert result.status_code == 200
        # Verify signature header was added (line 144)
        call_kwargs = mock_client.post.call_args[1]
        assert "X-Signature-256" in call_kwargs["headers"]

    @pytest.mark.asyncio
    async def test_deliver_with_subscription_secret_exception(self, service):
        """Cover lines 119-120: subscription fetch exception is caught."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response
        service._http_client = mock_client

        service._supabase.table.return_value.select.side_effect = Exception("DB error")

        result = await service.deliver({
            "webhook_id": "wh-sec2",
            "url": "https://example.com/hook",
            "payload": {},
            "subscription_id": "sub-err",
        })
        assert result.success is True  # Should still succeed, exception silently caught

    @pytest.mark.asyncio
    async def test_deliver_with_signature_header(self, service):
        """Cover line 144: signature added to request headers when secret present."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response
        service._http_client = mock_client

        sub_data = [{"secret": "mysecret"}]
        service._supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=sub_data)

        result = await service.deliver({
            "webhook_id": "wh-sig",
            "url": "https://example.com/hook",
            "payload": {"msg": "hello"},
            "subscription_id": "sub-sig",
        })
        assert result.success
        call_headers = mock_client.post.call_args[1]["headers"]
        assert "X-Signature-256" in call_headers
        assert len(call_headers["X-Signature-256"]) == 64

    @pytest.mark.asyncio
    async def test_poll_once_supabase_none(self, service):
        """Cover line 185: return 0,0 when supabase unavailable."""
        with patch.object(service, "_get_supabase", return_value=None):
            delivered, failed = await service.poll_once()
            assert delivered == 0
            assert failed == 0

    @pytest.mark.asyncio
    async def test_poll_once_skips_backoff(self, service):
        """Cover line 213: continue when scheduled_at > now_ms (backoff delay)."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response
        service._http_client = mock_client

        future_time = int(time.time() * 1000) + 3600000  # 1 hour in future
        service._supabase.table.return_value.select.return_value.in_.return_value.limit.return_value.order.return_value.execute.return_value = MagicMock(
            data=[{"webhook_id": "wh-backoff", "url": "https://example.com/hook", "payload": {}, "retry_count": 0, "max_retries": 5, "scheduled_at": future_time}]
        )
        delivered, failed = await service.poll_once()
        assert delivered == 0
        assert failed == 0

    @pytest.mark.asyncio
    async def test_poll_once_updates_subscriber_delivery_count(self, service):
        """Cover line 233: update subscriber delivery count on success."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response
        service._http_client = mock_client

        def table_side_effect(tbl):
            base = MagicMock()
            if tbl == "skill_webhook_queue":
                base.select.return_value.in_.return_value.limit.return_value.order.return_value.execute.return_value = MagicMock(
                    data=[{"webhook_id": "wh-sub1", "url": "https://example.com/hook", "payload": {}, "retry_count": 0, "max_retries": 5, "scheduled_at": 0, "subscription_id": "sub-1"}]
                )
            elif tbl == "skill_event_subscriptions":
                base.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"secret": "test-secret"}])
                base.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
            return base

        service._supabase.table.side_effect = table_side_effect

        delivered, failed = await service.poll_once()
        assert delivered == 1
        assert failed == 0

    @pytest.mark.asyncio
    async def test_poll_once_failed_retry_not_dead(self, service):
        """Cover line 250-264: failed delivery with retry (not dead letter)."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_client.post.return_value = mock_response
        service._http_client = mock_client

        service._supabase.table.return_value.select.return_value.in_.return_value.limit.return_value.order.return_value.execute.return_value = MagicMock(
            data=[{"webhook_id": "wh-fail1", "url": "https://example.com/hook", "payload": {}, "retry_count": 0, "max_retries": 5, "scheduled_at": 0}]
        )

        delivered, failed = await service.poll_once()
        assert delivered == 0
        assert failed == 1

    @pytest.mark.asyncio
    async def test_poll_once_failed_dead_letter(self, service):
        """Cover lines 250-264: failed delivery with dead letter (max retries reached)."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_client.post.return_value = mock_response
        service._http_client = mock_client

        service._supabase.table.return_value.select.return_value.in_.return_value.limit.return_value.order.return_value.execute.return_value = MagicMock(
            data=[{"webhook_id": "wh-dead", "url": "https://example.com/hook", "payload": {}, "retry_count": 5, "max_retries": 5, "scheduled_at": 0}]
        )

        delivered, failed = await service.poll_once()
        assert delivered == 0
        assert failed == 1

    @pytest.mark.asyncio
    async def test_poll_once_failed_dead_letter_updates_subscriber(self, service):
        """Cover lines 267-273: dead letter updates subscriber failure count."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_client.post.return_value = mock_response
        service._http_client = mock_client

        def table_side_effect(tbl):
            base = MagicMock()
            if tbl == "skill_webhook_queue":
                base.select.return_value.in_.return_value.limit.return_value.order.return_value.execute.return_value = MagicMock(
                    data=[{"webhook_id": "wh-dead2", "url": "https://example.com/hook", "payload": {}, "retry_count": 5, "max_retries": 5, "scheduled_at": 0, "subscription_id": "sub-2"}]
                )
            elif tbl == "skill_event_subscriptions":
                base.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
            return base

        service._supabase.table.side_effect = table_side_effect

        delivered, failed = await service.poll_once()
        assert delivered == 0
        assert failed == 1

    @pytest.mark.asyncio
    async def test_poll_loop_debug_logging(self, service):
        """Cover lines 313-315: poll loop debug logging when delivered/failed > 0."""
        service._running = True
        real_poll_once = service.poll_once

        call_count = 0

        async def controlled_poll():
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                service._running = False
            return (1, 0)

        service.poll_once = controlled_poll
        await service._poll_loop()
        assert call_count >= 1
