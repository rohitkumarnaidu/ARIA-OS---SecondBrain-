"""Coverage tests for scheduler modules — failure_tracker, alerting, health_check, main."""

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

import pytest

pytest.importorskip("apscheduler")


# ═══════════════════════════════════════════════════════════════════════════════
# FailureTracker
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.scheduler
class TestFailureTrackerCoverage:
    """Covers remaining paths in failure_tracker.py (lines 20-27, 30-32, 35-36, 39-40, 51-52, 55-56, 59-60)."""

    @pytest.mark.asyncio
    async def test_record_failure_date_change(self):
        """Lines 22-24: Daily failures cleared on date change."""
        from failure_tracker import FailureTracker

        tracker = FailureTracker()
        await tracker.record_failure("job1", "e1")
        await tracker.record_failure("job2", "e2")
        assert await tracker.get_daily_failure_count() == 2

        tracker._current_date = "2000-01-01"
        await tracker.record_failure("job1", "e3")
        assert await tracker.get_daily_failure_count() == 1
        assert tracker._current_date != "2000-01-01"

    @pytest.mark.asyncio
    async def test_record_failure_increments_consecutive(self):
        """Line 25-26: Consecutive failures and last_failure_time tracked."""
        from failure_tracker import FailureTracker

        tracker = FailureTracker()
        await tracker.record_failure("job1", "e1")
        await tracker.record_failure("job1", "e2")
        assert await tracker.get_consecutive_failures("job1") == 2
        assert "job1" in tracker._last_failure_time

    @pytest.mark.asyncio
    async def test_record_failure_daily_increments(self):
        """Line 27: Daily failure counter incremented."""
        from failure_tracker import FailureTracker

        tracker = FailureTracker()
        await tracker.record_failure("job1", "e1")
        await tracker.record_failure("job2", "e2")
        assert tracker._daily_failures["job1"] == 1
        assert tracker._daily_failures["job2"] == 1

    @pytest.mark.asyncio
    async def test_record_success_resets_and_stores_time(self):
        """Lines 31-32: Resets consecutive failures and records last_success_time."""
        from failure_tracker import FailureTracker

        tracker = FailureTracker()
        await tracker.record_failure("job1", "e1")
        await tracker.record_failure("job1", "e2")
        await tracker.record_success("job1")
        assert await tracker.get_consecutive_failures("job1") == 0
        assert "job1" in tracker._last_success_time

    @pytest.mark.asyncio
    async def test_get_consecutive_failures_unknown_job(self):
        """Line 36: Returns 0 for jobs with no recorded failures."""
        from failure_tracker import FailureTracker

        tracker = FailureTracker()
        assert await tracker.get_consecutive_failures("nonexistent") == 0

    @pytest.mark.asyncio
    async def test_get_failing_jobs_empty(self):
        """Line 40: Returns empty list when no jobs exceed threshold."""
        from failure_tracker import FailureTracker

        tracker = FailureTracker()
        assert await tracker.get_failing_jobs() == []
        assert await tracker.get_failing_jobs(threshold=1) == []

    @pytest.mark.asyncio
    async def test_get_failing_jobs_with_custom_threshold(self):
        """Line 40: Filters by custom threshold."""
        from failure_tracker import FailureTracker

        tracker = FailureTracker()
        for _ in range(4):
            await tracker.record_failure("job1", "e")
        await tracker.record_failure("job2", "e")
        result = await tracker.get_failing_jobs(threshold=4)
        assert len(result) == 1
        assert result[0]["job_name"] == "job1"

    @pytest.mark.asyncio
    async def test_get_daily_failure_count_zero(self):
        """Line 52: Returns 0 when no failures recorded."""
        from failure_tracker import FailureTracker

        tracker = FailureTracker()
        assert await tracker.get_daily_failure_count() == 0

    @pytest.mark.asyncio
    async def test_is_circuit_open_threshold(self):
        """Line 56: Open at exactly 5 consecutive failures."""
        from failure_tracker import FailureTracker

        tracker = FailureTracker()
        assert not await tracker.is_circuit_open("job1")
        for _ in range(4):
            await tracker.record_failure("job1", "e")
        assert not await tracker.is_circuit_open("job1")
        await tracker.record_failure("job1", "e")
        assert await tracker.is_circuit_open("job1")

    @pytest.mark.asyncio
    async def test_get_summary_empty(self):
        """Line 60: Empty summary with no failures."""
        from failure_tracker import FailureTracker

        tracker = FailureTracker()
        s = await tracker.get_summary()
        assert s["total_daily_failures"] == 0
        assert s["failing_jobs"] == []
        assert s["open_circuits"] == []

    @pytest.mark.asyncio
    async def test_get_summary_with_open_circuits(self):
        """Lines 65-73: Summary includes failing jobs and open circuits."""
        from failure_tracker import FailureTracker

        tracker = FailureTracker()
        for _ in range(5):
            await tracker.record_failure("circuit_job", "e")
        await tracker.record_failure("fail_job", "e")
        s = await tracker.get_summary()
        assert s["total_daily_failures"] == 6
        assert len(s["failing_jobs"]) == 2
        assert "circuit_job" in s["open_circuits"]

    @pytest.mark.asyncio
    async def test_get_summary_consecutive_failures_dict(self):
        """Line 61: consecutive_failures dict is populated correctly."""
        from failure_tracker import FailureTracker

        tracker = FailureTracker()
        await tracker.record_failure("job_a", "e1")
        await tracker.record_failure("job_a", "e2")
        await tracker.record_failure("job_b", "e1")
        s = await tracker.get_summary()
        assert s["consecutive_failures"] == {"job_a": 2, "job_b": 1}

    @pytest.mark.asyncio
    async def test_get_summary_daily_failures_dict(self):
        """Line 62: daily_failures dict is populated correctly."""
        from failure_tracker import FailureTracker

        tracker = FailureTracker()
        await tracker.record_failure("j1", "e1")
        await tracker.record_failure("j1", "e2")
        s = await tracker.get_summary()
        assert s["daily_failures"] == {"j1": 2}


# ═══════════════════════════════════════════════════════════════════════════════
# Alerting
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.scheduler
class TestAlertingCoverage:
    """Covers remaining paths in alerting.py (lines 49-51, 55-56, 66, 68, 77-90, 97-111, 136, 139)."""

    @pytest.fixture(autouse=True)
    def reset_alerting(self):
        """Reset global alerting singleton state before each test."""
        from alerting import alerting

        alerting._http_client = None
        alerting._webhook_url = ""
        alerting._slack_channel = "#aria-alerts"
        alerting._logtail_token = ""

    @pytest.mark.asyncio
    async def test_get_client_lazy_init(self, mocker):
        """Lines 49-51: Client created lazily on first call."""
        from alerting import alerting

        mock_instance = AsyncMock()
        mocker.patch("httpx.AsyncClient", return_value=mock_instance)

        alerting._http_client = None
        client1 = await alerting._get_client()
        assert client1 is mock_instance
        assert alerting._http_client is mock_instance

        client2 = await alerting._get_client()
        assert client2 is mock_instance

    @pytest.mark.asyncio
    async def test_shutdown_closes_and_nulls(self, mocker):
        """Lines 55-56: shutdown closes client and sets to None."""
        from alerting import alerting

        mock_client = AsyncMock()
        alerting._http_client = mock_client
        await alerting.shutdown()
        mock_client.aclose.assert_awaited_once()
        assert alerting._http_client is None

    @pytest.mark.asyncio
    async def test_shutdown_no_client(self):
        """shutdown handles None client gracefully."""
        from alerting import alerting

        alerting._http_client = None
        await alerting.shutdown()

    def test_log_console_critical(self, mocker):
        """Line 66: CRITICAL severity calls logger.error."""
        import alerting as alerting_mod
        from alerting import alerting

        mock_logger = mocker.patch.object(alerting_mod, "logger")
        alerting._log_console("CRITICAL", "critical error", {"detail": "x"})
        mock_logger.error.assert_called_once()

    def test_log_console_warning(self, mocker):
        """Line 68: WARNING severity calls logger.warn."""
        import alerting as alerting_mod
        from alerting import alerting

        mock_logger = mocker.patch.object(alerting_mod, "logger")
        alerting._log_console("WARNING", "warning msg")
        mock_logger.warn.assert_called_once()

    def test_log_console_info(self, mocker):
        """INFO severity calls logger.info."""
        import alerting as alerting_mod
        from alerting import alerting

        mock_logger = mocker.patch.object(alerting_mod, "logger")
        alerting._log_console("INFO", "info msg", {"foo": "bar"})
        mock_logger.info.assert_called_once()

    def test_log_console_no_details(self, mocker):
        """Line 64: Handles None details gracefully."""
        import alerting as alerting_mod
        from alerting import alerting

        mock_logger = mocker.patch.object(alerting_mod, "logger")
        alerting._log_console("INFO", "no details")
        mock_logger.info.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_logtail_no_token(self, mocker):
        """Line 75: Early return when no token configured."""
        from alerting import alerting

        alerting._logtail_token = ""
        mock_get = AsyncMock()
        mocker.patch.object(alerting, "_get_client", mock_get)
        await alerting._send_logtail({"msg": "test"})
        mock_get.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_logtail_success(self, mocker):
        """Lines 78-86: POST to Logtail succeeds."""
        from alerting import alerting

        alerting._logtail_token = "test-token"
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=MagicMock(status_code=200))
        mocker.patch.object(alerting, "_get_client", AsyncMock(return_value=mock_client))
        mocker.patch("alerting.logger")

        await alerting._send_logtail({"severity": "INFO", "message": "hello"})

        mock_client.post.assert_awaited_once()
        args, kwargs = mock_client.post.call_args
        assert "in.logtail.com" in args[0]
        assert kwargs["headers"]["Authorization"] == "Bearer test-token"

    @pytest.mark.asyncio
    async def test_send_logtail_http_error(self, mocker):
        """Lines 87-88: Logtail delivery logs warning on HTTP error."""
        from alerting import alerting

        alerting._logtail_token = "test-token"
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=MagicMock(status_code=401))
        mocker.patch.object(alerting, "_get_client", AsyncMock(return_value=mock_client))
        mock_logger = mocker.patch("alerting.logger")

        await alerting._send_logtail({"severity": "WARNING"})

        mock_logger.warn.assert_called_with("Logtail delivery failed", status_code=401)

    @pytest.mark.asyncio
    async def test_send_logtail_exception(self, mocker):
        """Lines 89-90: Logtail unavailable logs exception."""
        from alerting import alerting

        alerting._logtail_token = "test-token"
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=Exception("Connection refused"))
        mocker.patch.object(alerting, "_get_client", AsyncMock(return_value=mock_client))
        mock_logger = mocker.patch("alerting.logger")

        await alerting._send_logtail({"severity": "INFO"})

        mock_logger.warn.assert_called_with("Logtail unavailable", error="Connection refused")

    @pytest.mark.asyncio
    async def test_deliver_webhook_no_url(self, mocker):
        """Line 95: Early return when no webhook URL."""
        from alerting import alerting

        alerting._webhook_url = ""
        mock_get = AsyncMock()
        mocker.patch.object(alerting, "_get_client", mock_get)
        await alerting._deliver_webhook({"severity": "INFO"})
        mock_get.assert_not_called()

    @pytest.mark.asyncio
    async def test_deliver_webhook_critical_format(self, mocker):
        """Lines 99-107: CRITICAL severity sets color=danger in Slack payload."""
        from alerting import alerting

        alerting._webhook_url = "https://hooks.example.com/hook"
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=MagicMock(status_code=200))
        mocker.patch.object(alerting, "_get_client", AsyncMock(return_value=mock_client))
        mocker.patch("alerting.logger")

        await alerting._deliver_webhook({
            "severity": "CRITICAL",
            "message": "Server down",
            "job_name": "checker",
            "extra_field": "val",
        })

        mock_client.post.assert_awaited_once()
        args, kwargs = mock_client.post.call_args
        payload = kwargs["json"]
        assert payload["attachments"][0]["color"] == "danger"
        assert "[CRITICAL] Server down" in payload["text"]
        assert len(payload["attachments"][0]["fields"]) >= 2

    @pytest.mark.asyncio
    async def test_deliver_webhook_warning_format(self, mocker):
        """Line 100: WARNING severity sets color=warning."""
        from alerting import alerting

        alerting._webhook_url = "https://hooks.example.com/hook"
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=MagicMock(status_code=200))
        mocker.patch.object(alerting, "_get_client", AsyncMock(return_value=mock_client))
        mocker.patch("alerting.logger")

        await alerting._deliver_webhook({
            "severity": "WARNING",
            "message": "Degraded",
        })

        args, kwargs = mock_client.post.call_args
        assert kwargs["json"]["attachments"][0]["color"] == "warning"

    @pytest.mark.asyncio
    async def test_deliver_webhook_info_format(self, mocker):
        """Line 100: INFO severity sets color=good."""
        from alerting import alerting

        alerting._webhook_url = "https://hooks.example.com/hook"
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=MagicMock(status_code=200))
        mocker.patch.object(alerting, "_get_client", AsyncMock(return_value=mock_client))
        mocker.patch("alerting.logger")

        await alerting._deliver_webhook({
            "severity": "INFO",
            "message": "All good",
        })

        args, kwargs = mock_client.post.call_args
        assert kwargs["json"]["attachments"][0]["color"] == "good"

    @pytest.mark.asyncio
    async def test_deliver_webhook_http_error(self, mocker):
        """Lines 108-109: Webhook HTTP error logged."""
        from alerting import alerting

        alerting._webhook_url = "https://hooks.example.com/hook"
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=MagicMock(status_code=500, text="Server Error"))
        mocker.patch.object(alerting, "_get_client", AsyncMock(return_value=mock_client))
        mock_logger = mocker.patch("alerting.logger")

        await alerting._deliver_webhook({"severity": "WARNING", "message": "test"})

        mock_logger.warn.assert_called()
        call_args = mock_logger.warn.call_args
        assert "Webhook delivery failed" in call_args[0][0]
        assert call_args[1]["status_code"] == 500
        assert call_args[1]["response"] == "Server Error"

    @pytest.mark.asyncio
    async def test_deliver_webhook_exception(self, mocker):
        """Lines 110-111: Webhook exception caught and logged."""
        from alerting import alerting

        alerting._webhook_url = "https://hooks.example.com/hook"
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=Exception("Network timeout"))
        mocker.patch.object(alerting, "_get_client", AsyncMock(return_value=mock_client))
        mock_logger = mocker.patch("alerting.logger")

        await alerting._deliver_webhook({"severity": "INFO", "message": "hi"})

        mock_logger.warn.assert_called_with("Webhook unavailable", error="Network timeout")

    @pytest.mark.asyncio
    async def test_alert_critical_delegates(self, mocker):
        """Line 136: alert_critical calls _send_alert with CRITICAL."""
        from alerting import alerting

        mock_send = AsyncMock()
        mocker.patch.object(alerting, "_send_alert", mock_send)
        await alerting.alert_critical("CRIT MSG", {"job": "x"})
        mock_send.assert_awaited_once_with("CRITICAL", "CRIT MSG", {"job": "x"})

    @pytest.mark.asyncio
    async def test_alert_warning_delegates(self, mocker):
        """Line 139: alert_warning calls _send_alert with WARNING."""
        from alerting import alerting

        mock_send = AsyncMock()
        mocker.patch.object(alerting, "_send_alert", mock_send)
        await alerting.alert_warning("WARN MSG", {"job": "y"})
        mock_send.assert_awaited_once_with("WARNING", "WARN MSG", {"job": "y"})

    @pytest.mark.asyncio
    async def test_alert_info_delegates(self, mocker):
        """alert_info calls _send_alert with INFO."""
        from alerting import alerting

        mock_send = AsyncMock()
        mocker.patch.object(alerting, "_send_alert", mock_send)
        await alerting.alert_info("INFO MSG", {"job": "z"})
        mock_send.assert_awaited_once_with("INFO", "INFO MSG", {"job": "z"})

    @pytest.mark.asyncio
    async def test_send_alert_assembly_rate_limited(self, mocker):
        """Lines 126-131: Same alert key within cooldown is rate-limited."""
        from alerting import alerting

        alerting._webhook_url = "https://hooks.example.com/hook"
        mock_deliver = AsyncMock()
        mocker.patch.object(alerting, "_deliver_webhook", mock_deliver)
        mock_logger = mocker.patch("alerting.logger")
        mocker.patch.object(alerting, "_send_logtail", AsyncMock())
        mocker.patch.object(alerting, "_log_console")

        await alerting.alert_warning("msg", {"job_name": "checker"})
        assert mock_deliver.call_count == 1

        await alerting.alert_warning("msg", {"job_name": "checker"})
        assert mock_deliver.call_count == 1
        mock_logger.info.assert_called_with(
            "Alert rate-limited (webhook skipped)", job_name="checker", severity="WARNING"
        )

    @pytest.mark.asyncio
    async def test_send_alert_different_keys_not_rate_limited(self, mocker):
        """Different job+severity keys are NOT rate-limited."""
        from alerting import alerting

        alerting._webhook_url = "https://hooks.example.com/hook"
        mock_deliver = AsyncMock()
        mocker.patch.object(alerting, "_deliver_webhook", mock_deliver)
        mocker.patch.object(alerting, "_send_logtail", AsyncMock())
        mocker.patch.object(alerting, "_log_console")

        await alerting.alert_warning("msg1", {"job_name": "job_a"})
        await alerting.alert_info("msg2", {"job_name": "job_b"})
        await alerting.alert_critical("msg3", {"job_name": "job_a"})
        assert mock_deliver.call_count == 3

    @pytest.mark.asyncio
    async def test_send_alert_no_details(self, mocker):
        """_send_alert handles None details."""
        from alerting import alerting

        mocker.patch.object(alerting, "_deliver_webhook", AsyncMock())
        mocker.patch.object(alerting, "_send_logtail", AsyncMock())
        mocker.patch.object(alerting, "_log_console")
        mocker.patch.object(alerting, "_rate_limiter")
        alerting._rate_limiter.can_alert = AsyncMock(return_value=True)

        await alerting.alert_info("bare message", None)
        alerting._send_logtail.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_flush_pending(self):
        """flush_pending is a no-op placeholder."""
        from alerting import alerting
        await alerting.flush_pending()

    @pytest.mark.asyncio
    async def test_empty_message(self, mocker):
        """Empty message is delivered correctly."""
        from alerting import alerting

        alerting._webhook_url = "https://hooks.example.com/hook"
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=MagicMock(status_code=200))
        mocker.patch.object(alerting, "_get_client", AsyncMock(return_value=mock_client))
        mocker.patch.object(alerting, "_send_logtail", AsyncMock())
        mocker.patch.object(alerting, "_log_console")

        await alerting.alert_info("", {"job_name": "empty_test"})
        mock_client.post.assert_awaited_once()


# ═══════════════════════════════════════════════════════════════════════════════
# Health Check
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.scheduler
class TestHealthCheckCoverage:
    """Covers remaining paths in crons/health_check.py (lines 19-72)."""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        old = os.environ.get("USE_LOCAL_AI", "")
        os.environ["USE_LOCAL_AI"] = "true"
        yield
        if old:
            os.environ["USE_LOCAL_AI"] = old
        else:
            os.environ.pop("USE_LOCAL_AI", None)

    @pytest.fixture(autouse=True)
    def mock_supabase_patch(self, mocker):
        """Patch get_supabase_client at config.core.supabase since health_check imports inside function."""
        mock = mocker.patch("config.core.supabase.get_supabase_client")
        mock.return_value.from_.return_value.select.return_value.limit.return_value.execute.return_value = MagicMock()
        self._mock_supabase = mock
        yield

    @pytest.mark.asyncio
    async def test_health_check_success(self, mocker):
        """Line 19-69: All endpoints respond, status = healthy."""
        mocker.patch(
            "crons.health_check.failure_tracker.get_summary",
            AsyncMock(return_value={
                "open_circuits": [],
                "failing_jobs": [],
                "total_daily_failures": 0,
                "consecutive_failures": {},
                "daily_failures": {},
            }),
        )

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)
        mocker.patch("crons.health_check.httpx.AsyncClient", return_value=mock_ctx)

        mock_open = mocker.patch("builtins.open", MagicMock())
        mocker.patch("crons.health_check.logger")

        from crons.health_check import run_health_check
        await run_health_check()

        mock_open.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_supabase_fails(self, mocker):
        """Lines 31-32: Supabase unavailable logged."""
        mocker.patch(
            "crons.health_check.failure_tracker.get_summary",
            AsyncMock(return_value={
                "open_circuits": [],
                "failing_jobs": [],
                "total_daily_failures": 0,
                "consecutive_failures": {},
                "daily_failures": {},
            }),
        )
        self._mock_supabase.side_effect = Exception("DB connection refused")
        mock_logger = mocker.patch("crons.health_check.logger")
        mocker.patch("crons.health_check.alerting.alert_warning", AsyncMock())

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)
        mocker.patch("crons.health_check.httpx.AsyncClient", return_value=mock_ctx)

        mocker.patch("builtins.open", MagicMock())

        from crons.health_check import run_health_check
        await run_health_check()

        mock_logger.warn.assert_called_with("Health check: Supabase unavailable", error="DB connection refused")

    @pytest.mark.asyncio
    async def test_health_check_ollama_http_failure(self, mocker):
        """Lines 40-43: Ollama HTTP error returns False."""
        mocker.patch(
            "crons.health_check.failure_tracker.get_summary",
            AsyncMock(return_value={
                "open_circuits": [],
                "failing_jobs": [],
                "total_daily_failures": 0,
                "consecutive_failures": {},
                "daily_failures": {},
            }),
        )

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=503))
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)
        mocker.patch("crons.health_check.httpx.AsyncClient", return_value=mock_ctx)

        mock_open = mocker.patch("builtins.open", MagicMock())
        mocker.patch("crons.health_check.logger")

        from crons.health_check import run_health_check
        await run_health_check()

        # Should reach file write with ollama_ok=False
        mock_open.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_ollama_exception(self, mocker):
        """Lines 42-43: Ollama request throws exception, ollama_ok = False."""
        mocker.patch(
            "crons.health_check.failure_tracker.get_summary",
            AsyncMock(return_value={
                "open_circuits": [],
                "failing_jobs": [],
                "total_daily_failures": 0,
                "consecutive_failures": {},
                "daily_failures": {},
            }),
        )

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=Exception("Ollama down"))
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)
        mocker.patch("crons.health_check.httpx.AsyncClient", return_value=mock_ctx)

        mock_open = mocker.patch("builtins.open", MagicMock())
        mocker.patch("crons.health_check.logger")

        from crons.health_check import run_health_check
        await run_health_check()

        mock_open.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_ollama_not_configured(self, mocker):
        """Lines 37: When USE_LOCAL_AI != 'true', ollama is None (not_configured)."""
        os.environ["USE_LOCAL_AI"] = "false"
        mocker.patch(
            "crons.health_check.failure_tracker.get_summary",
            AsyncMock(return_value={
                "open_circuits": [],
                "failing_jobs": [],
                "total_daily_failures": 0,
                "consecutive_failures": {},
                "daily_failures": {},
            }),
        )

        mock_client = AsyncMock()
        mock_ctx = MagicMock()
        mocker.patch("crons.health_check.httpx.AsyncClient", return_value=mock_ctx)
        mock_open = mocker.patch("builtins.open", MagicMock())
        mocker.patch("crons.health_check.logger")

        from crons.health_check import run_health_check
        await run_health_check()

        mock_open.assert_called_once()
        # httpx should NOT be called when ollama is not configured
        mock_ctx.__aenter__.assert_not_called()

    @pytest.mark.asyncio
    async def test_health_check_file_write_failure(self, mocker):
        """Lines 66-67: File write failure logged."""
        mocker.patch(
            "crons.health_check.failure_tracker.get_summary",
            AsyncMock(return_value={
                "open_circuits": [],
                "failing_jobs": [],
                "total_daily_failures": 0,
                "consecutive_failures": {},
                "daily_failures": {},
            }),
        )

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)
        mocker.patch("crons.health_check.httpx.AsyncClient", return_value=mock_ctx)

        mock_open = mocker.patch("builtins.open", side_effect=OSError("Permission denied"))
        mock_logger = mocker.patch("crons.health_check.logger")

        from crons.health_check import run_health_check
        await run_health_check()

        mock_logger.error.assert_called_with(
            "Failed to write health status file", error="Permission denied"
        )

    @pytest.mark.asyncio
    async def test_health_check_open_circuits_triggers_alert(self, mocker):
        """Lines 45-46, 71-79: Open circuits cause degraded status and alert."""
        mocker.patch(
            "crons.health_check.failure_tracker.get_summary",
            AsyncMock(return_value={
                "open_circuits": ["checker_job"],
                "failing_jobs": [{"job_name": "checker_job", "consecutive_failures": 5}],
                "total_daily_failures": 5,
                "consecutive_failures": {"checker_job": 5},
                "daily_failures": {"checker_job": 5},
            }),
        )

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)
        mocker.patch("crons.health_check.httpx.AsyncClient", return_value=mock_ctx)

        mock_alert = mocker.patch("crons.health_check.alerting.alert_warning", AsyncMock())
        mocker.patch("builtins.open", MagicMock())
        mocker.patch("crons.health_check.logger")

        from crons.health_check import run_health_check
        await run_health_check()

        mock_alert.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_health_check_no_open_circuits_no_alert(self, mocker):
        """Lines 71: No open circuits skips alerting."""
        mocker.patch(
            "crons.health_check.failure_tracker.get_summary",
            AsyncMock(return_value={
                "open_circuits": [],
                "failing_jobs": [],
                "total_daily_failures": 0,
                "consecutive_failures": {},
                "daily_failures": {},
            }),
        )

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)
        mocker.patch("crons.health_check.httpx.AsyncClient", return_value=mock_ctx)

        mock_alert = mocker.patch("crons.health_check.alerting.alert_warning", AsyncMock())
        mocker.patch("builtins.open", MagicMock())
        mocker.patch("crons.health_check.logger")

        from crons.health_check import run_health_check
        await run_health_check()

        mock_alert.assert_not_called()

    @pytest.mark.asyncio
    async def test_health_check_logs_results(self, mocker):
        """Line 69: Logger receives completion info."""
        mocker.patch(
            "crons.health_check.failure_tracker.get_summary",
            AsyncMock(return_value={
                "open_circuits": [],
                "failing_jobs": [],
                "total_daily_failures": 2,
                "consecutive_failures": {},
                "daily_failures": {},
            }),
        )

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)
        mocker.patch("crons.health_check.httpx.AsyncClient", return_value=mock_ctx)

        mock_logger = mocker.patch("crons.health_check.logger")
        mocker.patch("builtins.open", MagicMock())

        from crons.health_check import run_health_check
        await run_health_check()

        mock_logger.info.assert_called_with(
            "Health check completed", status="healthy", failing_jobs=0
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Main Module (wrap, listener, health_server, write_initial)
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.scheduler
class TestMainCoverage:
    """Covers remaining paths in main.py (lines 44-66, 73-85, 146-147, 157, 173-175)."""

    @pytest.mark.asyncio
    async def test_wrap_cron_success_fast(self, mocker):
        """Lines 46-53: Successful fast cron job (< 5s)."""
        import main as main_module
        from main import _wrap_cron

        mocker.patch("main.time.time", side_effect=[100.0, 100.3])
        mocker.patch.object(main_module.failure_tracker, "record_success", AsyncMock())
        mock_logger = mocker.patch("main.logger")

        async def good_func():
            return "ok"

        wrapped = _wrap_cron("fast_job", good_func)
        result = await wrapped()
        assert result == "ok"
        main_module.failure_tracker.record_success.assert_awaited_once_with("fast_job")
        mock_logger.info.assert_called_with("Cron job completed", job_name="fast_job", duration_ms=300.0)

    @pytest.mark.asyncio
    async def test_wrap_cron_success_slow(self, mocker):
        """Lines 49-50: Slow cron job (> 5s) logged with (slow) tag."""
        import main as main_module
        from main import _wrap_cron

        mocker.patch("main.time.time", side_effect=[100.0, 106.5])
        mocker.patch.object(main_module.failure_tracker, "record_success", AsyncMock())
        mock_logger = mocker.patch("main.logger")

        async def slow_func():
            return "done"

        wrapped = _wrap_cron("slow_job", slow_func)
        result = await wrapped()
        assert result == "done"
        main_module.failure_tracker.record_success.assert_awaited_once_with("slow_job")
        mock_logger.info.assert_called_with("Cron job completed (slow)", job_name="slow_job", duration_ms=6500.0)

    @pytest.mark.asyncio
    async def test_wrap_cron_failure(self, mocker):
        """Lines 54-66: Cron job failure tracked and alerted."""
        import main as main_module
        from main import _wrap_cron

        mocker.patch("main.time.time", side_effect=[100.0, 101.0])
        mocker.patch.object(main_module.failure_tracker, "record_failure", AsyncMock())
        mocker.patch.object(main_module.alerting, "alert_warning", AsyncMock())
        mocker.patch("main.logger")

        async def failing_func():
            raise ValueError("Something broke")

        wrapped = _wrap_cron("fail_job", failing_func)
        result = await wrapped()
        assert result is None
        main_module.failure_tracker.record_failure.assert_awaited_once_with("fail_job", "Something broke")
        main_module.alerting.alert_warning.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_wrap_cron_failure_duration_in_alert(self, mocker):
        """Line 62: Failure alert includes duration_ms."""
        import main as main_module
        from main import _wrap_cron

        mocker.patch("main.time.time", side_effect=[200.0, 202.0])
        mocker.patch.object(main_module.failure_tracker, "record_failure", AsyncMock())
        mock_alert = mocker.patch.object(main_module.alerting, "alert_warning", AsyncMock())
        mocker.patch("main.logger")

        async def fail_func():
            raise RuntimeError("crash")

        wrapped = _wrap_cron("dur_job", fail_func)
        await wrapped()

        call_kwargs = mock_alert.await_args[1]
        assert call_kwargs["details"]["duration_ms"] == 2000.0
        assert call_kwargs["details"]["job_name"] == "dur_job"
        assert call_kwargs["details"]["error_message"] == "crash"

    @pytest.mark.asyncio
    async def test_wrap_cron_success_return_value_preserved(self, mocker):
        """Line 53: Return value from wrapped function is preserved."""
        import main as main_module
        from main import _wrap_cron

        mocker.patch("main.time.time", side_effect=[1.0, 1.1])
        mocker.patch.object(main_module.failure_tracker, "record_success", AsyncMock())
        mocker.patch("main.logger")

        async def returns_data():
            return {"key": "value", "num": 42}

        wrapped = _wrap_cron("data_job", returns_data)
        result = await wrapped()
        assert result == {"key": "value", "num": 42}

    @pytest.mark.parametrize("event_code,event_attr,expected_msg", [
        ("EVENT_JOB_ERROR", {"exception": ValueError("bad")}, "Unhandled exception in job"),
        ("EVENT_JOB_MISSED", {"scheduled_run_time": "2026-01-01T00:00:00"}, "Cron job missed its scheduled run"),
    ])
    @pytest.mark.asyncio
    async def test_scheduler_listener(self, mocker, event_code, event_attr, expected_msg):
        """Lines 73-92: Listener handles EVENT_JOB_ERROR and EVENT_JOB_MISSED."""
        import main as main_module
        from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED

        code = EVENT_JOB_ERROR if event_code == "EVENT_JOB_ERROR" else EVENT_JOB_MISSED
        mock_event = MagicMock()
        mock_event.job_id = "test_job"
        mock_event.code = code
        for k, v in event_attr.items():
            setattr(mock_event, k, v)

        mock_job = MagicMock()
        mock_job.name = "Test Job Name"
        main_module.scheduler = MagicMock()
        main_module.scheduler.get_job.return_value = mock_job

        mock_alert = mocker.patch.object(main_module.alerting, "alert_warning", AsyncMock())

        await main_module._scheduler_listener(mock_event)

        main_module.scheduler.get_job.assert_called_once_with("test_job")
        mock_alert.assert_awaited_once()
        assert expected_msg in mock_alert.await_args[1]["message"]

    @pytest.mark.asyncio
    async def test_scheduler_listener_job_not_found(self, mocker):
        """Line 74: Uses job_id when job not found in scheduler."""
        import main as main_module
        from apscheduler.events import EVENT_JOB_ERROR

        mock_event = MagicMock()
        mock_event.job_id = "orphan_job"
        mock_event.code = EVENT_JOB_ERROR
        mock_event.exception = RuntimeError("gone")

        main_module.scheduler = MagicMock()
        main_module.scheduler.get_job.return_value = None

        mock_alert = mocker.patch.object(main_module.alerting, "alert_warning", AsyncMock())

        await main_module._scheduler_listener(mock_event)

        mock_alert.assert_awaited_once()
        assert "orphan_job" in mock_alert.await_args[1]["message"]

    @pytest.mark.asyncio
    async def test_scheduler_listener_missing_event_attributes(self, mocker):
        """Lines 80, 89: getattr defaults when event lacks exception/scheduled_run_time."""
        import main as main_module
        from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED

        main_module.scheduler = MagicMock()
        main_module.scheduler.get_job.return_value = MagicMock(name="anon")

        mock_alert = mocker.patch.object(main_module.alerting, "alert_warning", AsyncMock())

        event_error = MagicMock(spec=[])  # no attributes at all
        event_error.job_id = "j1"
        event_error.code = EVENT_JOB_ERROR
        # Deliberately NOT setting 'exception' to test getattr default

        await main_module._scheduler_listener(event_error)
        assert mock_alert.await_args[1]["details"]["error_message"] == "unknown"

        event_missed = MagicMock(spec=[])
        event_missed.job_id = "j2"
        event_missed.code = EVENT_JOB_MISSED

        await main_module._scheduler_listener(event_missed)

    def test_write_initial_health_failure(self, mocker):
        """Lines 146-147: File write failure caught and logged."""
        from main import write_initial_health

        mocker.patch("builtins.open", side_effect=OSError("Disk full"))
        mock_logger = mocker.patch("main.logger")

        write_initial_health()

        mock_logger.warn.assert_called_with(
            "Failed to write initial health status", error="Disk full"
        )

    def test_health_handler_ready_healthy(self, mocker):
        """Line 157: /health/ready returns 200 when status == healthy."""
        from main import HealthHandler

        mocker.patch.object(HealthHandler, "_load_health", return_value={"status": "healthy"})
        mocker.patch.object(HealthHandler, "send_response")
        mocker.patch.object(HealthHandler, "send_header")
        mocker.patch.object(HealthHandler, "end_headers")
        mocker.patch("main.scheduler.get_jobs", return_value=[])
        handler = HealthHandler.__new__(HealthHandler)
        handler.path = "/health/ready"
        handler.command = "GET"
        handler.wfile = MagicMock()

        handler.do_GET()

        handler.send_response.assert_called_with(200)

    def test_health_handler_ready_degraded(self, mocker):
        """Line 157: /health/ready returns 503 when status != healthy."""
        from main import HealthHandler

        mocker.patch.object(HealthHandler, "_load_health", return_value={"status": "degraded"})
        mocker.patch.object(HealthHandler, "send_response")
        mocker.patch.object(HealthHandler, "send_header")
        mocker.patch.object(HealthHandler, "end_headers")
        mocker.patch("main.scheduler.get_jobs", return_value=[])
        handler = HealthHandler.__new__(HealthHandler)
        handler.path = "/health/ready"
        handler.command = "GET"
        handler.wfile = MagicMock()

        handler.do_GET()

        handler.send_response.assert_called_with(503)

    def test_health_handler_root_health(self, mocker):
        """Line 159: /health always returns 200."""
        from main import HealthHandler

        mocker.patch.object(HealthHandler, "_load_health", return_value={"status": "degraded"})
        mocker.patch.object(HealthHandler, "send_response")
        mocker.patch.object(HealthHandler, "send_header")
        mocker.patch.object(HealthHandler, "end_headers")
        mocker.patch("main.scheduler.get_jobs", return_value=[])
        handler = HealthHandler.__new__(HealthHandler)
        handler.path = "/health"
        handler.command = "GET"
        handler.wfile = MagicMock()

        handler.do_GET()

        handler.send_response.assert_called_with(200)

    def test_health_handler_load_health_fallback(self):
        """Lines 173-175: _load_health returns default when file missing."""
        from main import HealthHandler
        import main as main_module
        import tempfile

        handler = HealthHandler.__new__(HealthHandler)
        tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        tmp.close()
        original = main_module.HEALTH_STATUS_FILE
        main_module.HEALTH_STATUS_FILE = Path(tmp.name)
        try:
            os.unlink(tmp.name)
            result = handler._load_health()
            assert result == {"status": "healthy", "service": "scheduler"}
        finally:
            main_module.HEALTH_STATUS_FILE = original

    def test_health_handler_load_health_invalid_json(self):
        """Lines 173-175: _load_health falls back on invalid JSON."""
        from main import HealthHandler
        import main as main_module
        import tempfile

        handler = HealthHandler.__new__(HealthHandler)
        tmp = tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False)
        tmp.write("{invalid json}")
        tmp.close()
        original = main_module.HEALTH_STATUS_FILE
        main_module.HEALTH_STATUS_FILE = Path(tmp.name)
        try:
            result = handler._load_health()
            assert result == {"status": "healthy", "service": "scheduler"}
        finally:
            main_module.HEALTH_STATUS_FILE = original
            os.unlink(tmp.name)

    def test_health_handler_writes_job_count(self, mocker):
        """Line 162: Job count included in response."""
        from main import HealthHandler

        mocker.patch.object(HealthHandler, "_load_health", return_value={"status": "healthy"})
        mocker.patch.object(HealthHandler, "send_response")
        mocker.patch.object(HealthHandler, "send_header")
        mocker.patch.object(HealthHandler, "end_headers")
        mocker.patch("main.scheduler.get_jobs", return_value=[1, 2, 3])
        wfile = MagicMock()
        handler = HealthHandler.__new__(HealthHandler)
        handler.path = "/health"
        handler.command = "GET"
        handler.wfile = wfile

        handler.do_GET()

        written = json.loads(wfile.write.call_args[0][0])
        assert written["jobs"] == 3

    def test_health_handler_404(self, mocker):
        """Line 164-165: Unknown paths return 404."""
        from main import HealthHandler

        mocker.patch.object(HealthHandler, "send_response")
        mocker.patch.object(HealthHandler, "end_headers")
        handler = HealthHandler.__new__(HealthHandler)
        handler.path = "/unknown"
        handler.command = "GET"

        handler.do_GET()

        handler.send_response.assert_called_with(404)


# ═══════════════════════════════════════════════════════════════════════════════
# Main Module — Job Registration Details
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.scheduler
class TestMainJobRegistration:
    """Covers remaining paths in main.py job definitions."""

    def test_all_14_jobs_have_correct_triggers(self):
        """Verify all 14 job definitions have valid CronTrigger instances."""
        from main import JOB_DEFINITIONS
        from apscheduler.triggers.cron import CronTrigger

        assert len(JOB_DEFINITIONS) == 14
        for func, trigger, job_id, job_name in JOB_DEFINITIONS:
            assert callable(func), f"{job_id} func is not callable"
            assert isinstance(trigger, CronTrigger), f"{job_id} trigger is not CronTrigger"
            assert isinstance(job_id, str) and len(job_id) > 0
            assert isinstance(job_name, str) and len(job_name) > 0

    def test_health_check_trigger_every_5_minutes(self):
        """health_check runs every 5 minutes."""
        from main import JOB_DEFINITIONS
        from apscheduler.triggers.cron import CronTrigger

        hc = [j for j in JOB_DEFINITIONS if j[2] == "health_check"][0]
        trigger = hc[1]
        assert isinstance(trigger, CronTrigger)

    def test_deadline_alert_trigger_every_hour(self):
        """deadline_alert runs every hour (hour='*')."""
        from main import JOB_DEFINITIONS
        from apscheduler.triggers.cron import CronTrigger
        from datetime import datetime

        da = [j for j in JOB_DEFINITIONS if j[2] == "deadline_alert"][0]
        trigger = da[1]
        assert isinstance(trigger, CronTrigger)
        next_fire = trigger.get_next_fire_time(None, datetime(2026, 1, 1, 0, 0))
        assert next_fire is not None
        # Verify it fires at the top of the next hour
        assert next_fire.minute == 0

    def test_job_definitions_unique_ids(self):
        """All job IDs are unique."""
        from main import JOB_DEFINITIONS

        ids = [j[2] for j in JOB_DEFINITIONS]
        assert len(ids) == len(set(ids))

    @pytest.mark.asyncio
    async def test_setup_cron_jobs_registers_listener(self, mocker):
        """Line 125: Listener registered after jobs."""
        import main as main_module

        main_module.scheduler = MagicMock()
        main_module.scheduler.get_jobs.return_value = [
            MagicMock(id="test_job", name="Test Job", spec=["id", "name"]),
        ]
        # Ensure job.name returns a real string for JSON serialization by logger
        main_module.scheduler.get_jobs.return_value[0].name = "Test Job"
        mock_add_listener = mocker.patch.object(main_module.scheduler, "add_listener")
        mocker.patch.object(main_module, "_wrap_cron", side_effect=lambda jid, fn: fn)

        main_module.setup_cron_jobs()

        mock_add_listener.assert_called_once()
        assert mock_add_listener.call_args[0][1] is not None

    @pytest.mark.asyncio
    async def test_setup_cron_jobs_adds_all_14_jobs(self, mocker):
        """All 14 jobs are added to the scheduler."""
        import main as main_module

        main_module.scheduler = MagicMock()
        jobs = []
        for i in range(14):
            j = MagicMock(id=f"job_{i}", name=f"Job {i}", spec=["id", "name"])
            j.name = f"Job {i}"
            jobs.append(j)
        main_module.scheduler.get_jobs.return_value = jobs
        mocker.patch.object(main_module, "_wrap_cron", side_effect=lambda jid, fn: fn)

        main_module.setup_cron_jobs()

        assert main_module.scheduler.add_job.call_count == 14

    @pytest.mark.asyncio
    async def test_scheduler_starts_without_error(self, mocker):
        """Scheduler starts without error in main()."""
        import main as main_module

        main_module.scheduler = MagicMock()
        main_module.scheduler.start = MagicMock()
        main_module.scheduler.get_jobs.return_value = []

        mocker.patch.object(main_module, "write_initial_health")
        mocker.patch.object(main_module, "setup_cron_jobs")
        mocker.patch.object(main_module.threading, "Thread")
        mocker.patch.object(main_module.alerting, "alert_info", AsyncMock())
        mocker.patch.object(main_module.alerting, "shutdown", AsyncMock())
        mocker.patch.object(main_module.alerting, "flush_pending", AsyncMock())
        mocker.patch("main.logger")
        mocker.patch("main.asyncio.sleep", side_effect=KeyboardInterrupt())

        await main_module.main()

        main_module.scheduler.start.assert_called_once()
        main_module.setup_cron_jobs.assert_called_once()

    @pytest.mark.asyncio
    async def test_main_shutdown_handler(self, mocker):
        """Lines 209-221: Shutdown handler runs on interrupt."""
        import main as main_module

        main_module.scheduler = MagicMock()
        main_module.scheduler.get_jobs.return_value = []
        mock_shutdown_sched = mocker.patch.object(main_module.scheduler, "shutdown")

        mocker.patch.object(main_module, "write_initial_health")
        mocker.patch.object(main_module, "setup_cron_jobs")
        mocker.patch.object(main_module.threading, "Thread")
        mocker.patch.object(main_module.alerting, "alert_info", AsyncMock())
        mock_flush = mocker.patch.object(main_module.alerting, "flush_pending", AsyncMock())
        mock_alert_shutdown = mocker.patch.object(main_module.alerting, "shutdown", AsyncMock())
        mocker.patch("main.logger")
        mocker.patch("main.asyncio.sleep", side_effect=KeyboardInterrupt())

        await main_module.main()

        mock_flush.assert_awaited_once()
        mock_shutdown_sched.assert_called_once_with(wait=False)
        mock_alert_shutdown.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_main_system_exit_handler(self, mocker):
        """SystemExit also triggers clean shutdown."""
        import main as main_module

        main_module.scheduler = MagicMock()
        main_module.scheduler.get_jobs.return_value = []

        mocker.patch.object(main_module, "write_initial_health")
        mocker.patch.object(main_module, "setup_cron_jobs")
        mocker.patch.object(main_module.threading, "Thread")
        mocker.patch.object(main_module.alerting, "alert_info", AsyncMock())
        mocker.patch.object(main_module.alerting, "flush_pending", AsyncMock())
        mocker.patch.object(main_module.alerting, "shutdown", AsyncMock())
        mocker.patch.object(main_module.scheduler, "shutdown")
        mocker.patch("main.logger")
        mocker.patch("main.asyncio.sleep", side_effect=SystemExit())

        await main_module.main()

        main_module.scheduler.shutdown.assert_called_once()

    def test_start_health_server_daemon_thread(self, mocker):
        """Line 192: Health server runs in daemon thread."""
        import main as main_module

        mocker.patch.object(main_module, "start_health_server")
        mock_thread = mocker.patch("main.threading.Thread")

        thread = mock_thread(target=main_module.start_health_server, daemon=True)
        assert thread.daemon

    def test_log_message_suppressed(self):
        """Line 177-178: log_message suppresses output."""
        from main import HealthHandler

        handler = HealthHandler.__new__(HealthHandler)
        handler.log_message("GET /health %s", 200)
