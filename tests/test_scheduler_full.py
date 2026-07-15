"""Comprehensive tests for scheduler modules — failure_tracker, alerting, all crons, main.py.

This file extends coverage across the full scheduler package by exercising:
  - failure_tracker: all async methods, global instance, edge cases
  - alerting: AlertRateLimiter, Alerting (console, logtail, webhook, rate-limiting)
  - health_check: all dependency checks, file I/O, circuit breaker alerts
  - deadline_alert: full CRUD flow, existing-alert dedup, urgency calculation
  - All 8 user-facing cron modules (daily_briefing, opportunity_radar, weekly_review,
    habit_checker, missed_task_checker, sleep_reminder, course_nudge, deadline_alert)
  - main.py: _wrap_cron (success/fast/slow/failure), _scheduler_listener, setup_cron_jobs,
    write_initial_health, HealthHandler (do_GET, _load_health), start_health_server, main()
"""

import asyncio
import json
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path

import pytest

pytestmark = pytest.mark.asyncio

# ── Import guard for APScheduler-dependent tests ──────────────────────────────
_HAVE_APSCHEDULER = False
try:
    import apscheduler  # noqa: F401
    _HAVE_APSCHEDULER = True
except ImportError:
    pass

NEED_APSCHEDULER = pytest.mark.skipif(
    not _HAVE_APSCHEDULER,
    reason="apscheduler not installed — skipping APScheduler-dependent tests",
)


# ═══════════════════════════════════════════════════════════════════════════════
# FailureTracker — unit coverage
# ═══════════════════════════════════════════════════════════════════════════════

class TestFailureTracker:
    """Cover every method of FailureTracker including global instance."""

    async def test_init_defaults(self):
        from failure_tracker import FailureTracker
        ft = FailureTracker()
        assert ft._consecutive_failures == {}
        assert ft._last_failure_time == {}
        assert ft._last_success_time == {}
        assert ft._daily_failures == {}
        assert ft._current_date == ""

    async def test_record_failure_first(self):
        from failure_tracker import FailureTracker
        ft = FailureTracker()
        await ft.record_failure("job_a", "first error")
        assert await ft.get_consecutive_failures("job_a") == 1
        assert ft._daily_failures["job_a"] == 1
        assert ft._current_date != ""

    async def test_record_failure_multiple(self):
        from failure_tracker import FailureTracker
        ft = FailureTracker()
        for i in range(3):
            await ft.record_failure("job_b", f"error {i}")
        assert await ft.get_consecutive_failures("job_b") == 3
        assert ft._daily_failures["job_b"] == 3

    async def test_record_failure_date_change(self):
        from failure_tracker import FailureTracker
        ft = FailureTracker()
        await ft.record_failure("job_x", "day1")
        assert await ft.get_daily_failure_count() == 1
        ft._current_date = "1999-01-01"
        await ft.record_failure("job_x", "day2")
        assert await ft.get_daily_failure_count() == 1

    async def test_record_success_resets(self):
        from failure_tracker import FailureTracker
        ft = FailureTracker()
        await ft.record_failure("job_c", "e1")
        await ft.record_failure("job_c", "e2")
        await ft.record_success("job_c")
        assert await ft.get_consecutive_failures("job_c") == 0
        assert "job_c" in ft._last_success_time

    async def test_record_success_unknown_job(self):
        from failure_tracker import FailureTracker
        ft = FailureTracker()
        await ft.record_success("never_failed")
        assert await ft.get_consecutive_failures("never_failed") == 0

    async def test_get_consecutive_failures_has(self):
        from failure_tracker import FailureTracker
        ft = FailureTracker()
        await ft.record_failure("j1", "e")
        assert await ft.get_consecutive_failures("j1") == 1

    async def test_get_consecutive_failures_none(self):
        from failure_tracker import FailureTracker
        ft = FailureTracker()
        assert await ft.get_consecutive_failures("nonexistent") == 0

    async def test_get_failing_jobs_above_threshold(self):
        from failure_tracker import FailureTracker
        ft = FailureTracker()
        for _ in range(5):
            await ft.record_failure("j_fail", "e")
        await ft.record_failure("j_ok", "e")
        failing = await ft.get_failing_jobs(threshold=3)
        assert len(failing) == 1
        assert failing[0]["job_name"] == "j_fail"

    async def test_get_failing_jobs_below_threshold(self):
        from failure_tracker import FailureTracker
        ft = FailureTracker()
        await ft.record_failure("j1", "e")
        assert await ft.get_failing_jobs(threshold=5) == []

    async def test_get_failing_jobs_empty(self):
        from failure_tracker import FailureTracker
        ft = FailureTracker()
        assert await ft.get_failing_jobs() == []

    async def test_get_daily_failure_count_sum(self):
        from failure_tracker import FailureTracker
        ft = FailureTracker()
        await ft.record_failure("a", "e")
        await ft.record_failure("b", "e")
        await ft.record_failure("a", "e")
        assert await ft.get_daily_failure_count() == 3

    async def test_get_daily_failure_count_zero(self):
        from failure_tracker import FailureTracker
        ft = FailureTracker()
        assert await ft.get_daily_failure_count() == 0

    async def test_is_circuit_open_closed(self):
        from failure_tracker import FailureTracker
        ft = FailureTracker()
        assert not await ft.is_circuit_open("any_job")

    async def test_is_circuit_open_open(self):
        from failure_tracker import FailureTracker
        ft = FailureTracker()
        for _ in range(5):
            await ft.record_failure("circuit_b", "e")
        assert await ft.is_circuit_open("circuit_b")

    async def test_is_circuit_open_four(self):
        from failure_tracker import FailureTracker
        ft = FailureTracker()
        for _ in range(4):
            await ft.record_failure("four", "e")
        assert not await ft.is_circuit_open("four")

    async def test_get_summary_empty(self):
        from failure_tracker import FailureTracker
        ft = FailureTracker()
        s = await ft.get_summary()
        assert s["total_daily_failures"] == 0
        assert s["failing_jobs"] == []
        assert s["open_circuits"] == []

    async def test_get_summary_with_failures(self):
        from failure_tracker import FailureTracker
        ft = FailureTracker()
        for _ in range(3):
            await ft.record_failure("j_a", "e")
        await ft.record_failure("j_b", "e")
        s = await ft.get_summary()
        assert s["consecutive_failures"] == {"j_a": 3, "j_b": 1}
        assert s["daily_failures"]["j_a"] == 3
        assert s["total_daily_failures"] == 4
        assert len(s["failing_jobs"]) == 2

    async def test_get_summary_open_circuits(self):
        from failure_tracker import FailureTracker
        ft = FailureTracker()
        for _ in range(5):
            await ft.record_failure("open_j", "e")
        s = await ft.get_summary()
        assert "open_j" in s["open_circuits"]

    async def test_global_instance(self):
        from failure_tracker import failure_tracker
        assert failure_tracker is not None
        assert hasattr(failure_tracker, "record_failure")
        assert hasattr(failure_tracker, "record_success")
        assert hasattr(failure_tracker, "get_summary")


# ═══════════════════════════════════════════════════════════════════════════════
# AlertRateLimiter
# ═══════════════════════════════════════════════════════════════════════════════

class TestAlertRateLimiter:

    async def test_can_alert_first_call(self):
        from alerting import AlertRateLimiter
        rl = AlertRateLimiter()
        assert await rl.can_alert("test_key", cooldown=300)

    async def test_can_alert_within_cooldown(self):
        from alerting import AlertRateLimiter
        rl = AlertRateLimiter()
        assert await rl.can_alert("key1", cooldown=300)
        assert not await rl.can_alert("key1", cooldown=300)

    async def test_can_alert_after_cooldown(self):
        from alerting import AlertRateLimiter
        rl = AlertRateLimiter()
        assert await rl.can_alert("key2", cooldown=0.05)
        await asyncio.sleep(0.06)
        assert await rl.can_alert("key2", cooldown=0.05)

    async def test_can_alert_different_keys(self):
        from alerting import AlertRateLimiter
        rl = AlertRateLimiter()
        assert await rl.can_alert("key_a", 300)
        assert await rl.can_alert("key_b", 300)

    async def test_can_alert_zero_cooldown(self):
        from alerting import AlertRateLimiter
        rl = AlertRateLimiter()
        assert await rl.can_alert("zero_key", 0)
        assert await rl.can_alert("zero_key", 0)


# ═══════════════════════════════════════════════════════════════════════════════
# Alerting
# ═══════════════════════════════════════════════════════════════════════════════

class TestAlerting:

    @pytest.fixture(autouse=True)
    def reset_alerting(self):
        from alerting import alerting
        alerting._http_client = None
        alerting._webhook_url = ""
        alerting._slack_channel = "#aria-alerts"
        alerting._logtail_token = ""
        # Save and restore env
        saved = {
            "ALERT_WEBHOOK_URL": os.environ.get("ALERT_WEBHOOK_URL"),
            "ALERT_SLACK_CHANNEL": os.environ.get("ALERT_SLACK_CHANNEL"),
            "ALERT_LOGTAIL_SOURCE_TOKEN": os.environ.get("ALERT_LOGTAIL_SOURCE_TOKEN"),
        }
        yield
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v
            else:
                os.environ.pop(k, None)

    async def test_init_loads_env_vars(self):
        os.environ["ALERT_WEBHOOK_URL"] = "https://hooks.example.com"
        os.environ["ALERT_SLACK_CHANNEL"] = "#custom"
        os.environ["ALERT_LOGTAIL_SOURCE_TOKEN"] = "tok_abc"
        from alerting import Alerting
        a = Alerting()
        assert a._webhook_url == "https://hooks.example.com"
        assert a._slack_channel == "#custom"
        assert a._logtail_token == "tok_abc"

    async def test_init_defaults_when_env_missing(self):
        for k in ("ALERT_WEBHOOK_URL", "ALERT_SLACK_CHANNEL", "ALERT_LOGTAIL_SOURCE_TOKEN"):
            os.environ.pop(k, None)
        from alerting import Alerting
        a = Alerting()
        assert a._webhook_url == ""
        assert a._slack_channel == "#aria-alerts"
        assert a._logtail_token == ""

    async def test_get_client_creates_and_reuses(self, mocker):
        from alerting import Alerting
        a = Alerting()
        assert a._http_client is None
        mock_instance = AsyncMock()
        mocker.patch("httpx.AsyncClient", return_value=mock_instance)
        c1 = await a._get_client()
        assert c1 is mock_instance
        assert a._http_client is mock_instance
        c2 = await a._get_client()
        assert c2 is mock_instance

    async def test_shutdown_closes_client(self, mocker):
        from alerting import Alerting
        a = Alerting()
        mock_client = AsyncMock()
        a._http_client = mock_client
        await a.shutdown()
        mock_client.aclose.assert_awaited_once()
        assert a._http_client is None

    async def test_shutdown_no_client(self):
        from alerting import Alerting
        a = Alerting()
        a._http_client = None
        await a.shutdown()

    async def test_flush_pending(self):
        from alerting import alerting
        await alerting.flush_pending()

    def test_log_console_critical(self, mocker):
        import alerting as alerting_mod
        from alerting import alerting
        mock_logger = mocker.patch.object(alerting_mod, "logger")
        alerting._log_console("CRITICAL", "crit msg", {"x": 1})
        mock_logger.error.assert_called_once_with("[CRITICAL] crit msg", **{"x": 1})

    def test_log_console_warning(self, mocker):
        import alerting as alerting_mod
        from alerting import alerting
        mock_logger = mocker.patch.object(alerting_mod, "logger")
        alerting._log_console("WARNING", "warn msg")
        mock_logger.warn.assert_called_once_with("[WARNING] warn msg")

    def test_log_console_info(self, mocker):
        import alerting as alerting_mod
        from alerting import alerting
        mock_logger = mocker.patch.object(alerting_mod, "logger")
        alerting._log_console("INFO", "info msg")
        mock_logger.info.assert_called_once_with("[INFO] info msg")

    def test_log_console_none_details(self, mocker):
        import alerting as alerting_mod
        from alerting import alerting
        mock_logger = mocker.patch.object(alerting_mod, "logger")
        alerting._log_console("INFO", "msg", None)
        mock_logger.info.assert_called_once()

    async def test_send_logtail_no_token(self, mocker):
        from alerting import alerting
        alerting._logtail_token = ""
        mock_get = AsyncMock()
        mocker.patch.object(alerting, "_get_client", mock_get)
        await alerting._send_logtail({"msg": "test"})
        mock_get.assert_not_called()

    async def test_send_logtail_success(self, mocker):
        from alerting import alerting
        alerting._logtail_token = "tok_valid"
        mock_client = AsyncMock()
        mock_client.post.return_value = MagicMock(status_code=200)
        mocker.patch.object(alerting, "_get_client", AsyncMock(return_value=mock_client))
        mock_logger = mocker.patch("alerting.logger")
        await alerting._send_logtail({"severity": "INFO"})
        mock_client.post.assert_awaited_once()
        assert "Bearer tok_valid" in mock_client.post.call_args[1]["headers"]["Authorization"]

    async def test_send_logtail_non_2xx(self, mocker):
        from alerting import alerting
        alerting._logtail_token = "tok"
        mock_client = AsyncMock()
        mock_client.post.return_value = MagicMock(status_code=401)
        mocker.patch.object(alerting, "_get_client", AsyncMock(return_value=mock_client))
        mock_logger = mocker.patch("alerting.logger")
        await alerting._send_logtail({"severity": "WARNING"})
        mock_logger.warn.assert_called_with("Logtail delivery failed", status_code=401)

    async def test_send_logtail_exception(self, mocker):
        from alerting import alerting
        alerting._logtail_token = "tok"
        mock_client = AsyncMock()
        mock_client.post.side_effect = Exception("Connection refused")
        mocker.patch.object(alerting, "_get_client", AsyncMock(return_value=mock_client))
        mock_logger = mocker.patch("alerting.logger")
        await alerting._send_logtail({"severity": "INFO"})
        mock_logger.warn.assert_called_with("Logtail unavailable", error="Connection refused")

    async def test_deliver_webhook_no_url(self, mocker):
        from alerting import alerting
        alerting._webhook_url = ""
        mock_get = AsyncMock()
        mocker.patch.object(alerting, "_get_client", mock_get)
        await alerting._deliver_webhook({"severity": "INFO"})
        mock_get.assert_not_called()

    async def test_deliver_webhook_success(self, mocker):
        from alerting import alerting
        alerting._webhook_url = "https://hooks.example.com"
        mock_client = AsyncMock()
        mock_client.post.return_value = MagicMock(status_code=200)
        mocker.patch.object(alerting, "_get_client", AsyncMock(return_value=mock_client))
        mock_logger = mocker.patch("alerting.logger")
        await alerting._deliver_webhook({"severity": "INFO", "message": "ok", "job_name": "j"})
        mock_client.post.assert_awaited_once()
        payload = mock_client.post.call_args[1]["json"]
        assert payload["attachments"][0]["color"] == "good"

    async def test_deliver_webhook_critical(self, mocker):
        from alerting import alerting
        alerting._webhook_url = "https://hooks.example.com"
        mock_client = AsyncMock()
        mock_client.post.return_value = MagicMock(status_code=200)
        mocker.patch.object(alerting, "_get_client", AsyncMock(return_value=mock_client))
        await alerting._deliver_webhook({"severity": "CRITICAL", "message": "down"})
        assert mock_client.post.call_args[1]["json"]["attachments"][0]["color"] == "danger"

    async def test_deliver_webhook_warning(self, mocker):
        from alerting import alerting
        alerting._webhook_url = "https://hooks.example.com"
        mock_client = AsyncMock()
        mock_client.post.return_value = MagicMock(status_code=200)
        mocker.patch.object(alerting, "_get_client", AsyncMock(return_value=mock_client))
        await alerting._deliver_webhook({"severity": "WARNING", "message": "warn"})
        assert mock_client.post.call_args[1]["json"]["attachments"][0]["color"] == "warning"

    async def test_deliver_webhook_non_2xx(self, mocker):
        from alerting import alerting
        alerting._webhook_url = "https://hooks.example.com"
        mock_client = AsyncMock()
        mock_client.post.return_value = MagicMock(status_code=500, text="Server Error")
        mocker.patch.object(alerting, "_get_client", AsyncMock(return_value=mock_client))
        mock_logger = mocker.patch("alerting.logger")
        await alerting._deliver_webhook({"severity": "INFO", "message": "m"})
        mock_logger.warn.assert_called()
        assert "Webhook delivery failed" in mock_logger.warn.call_args[0][0]

    async def test_deliver_webhook_exception(self, mocker):
        from alerting import alerting
        alerting._webhook_url = "https://hooks.example.com"
        mock_client = AsyncMock()
        mock_client.post.side_effect = Exception("Network timeout")
        mocker.patch.object(alerting, "_get_client", AsyncMock(return_value=mock_client))
        mock_logger = mocker.patch("alerting.logger")
        await alerting._deliver_webhook({"severity": "INFO", "message": "m"})
        mock_logger.warn.assert_called_with("Webhook unavailable", error="Network timeout")

    async def test_send_alert_assembles_payload(self, mocker):
        from alerting import alerting
        alerting._webhook_url = "https://hooks.example.com"
        mock_log = mocker.patch.object(alerting, "_log_console")
        mock_logtail = mocker.patch.object(alerting, "_send_logtail", AsyncMock())
        mock_webhook = mocker.patch.object(alerting, "_deliver_webhook", AsyncMock())
        await alerting.alert_critical("critical msg", {"job_name": "test_job"})
        mock_log.assert_called_once()
        mock_logtail.assert_awaited_once()
        assert mock_webhook.await_count >= 1

    async def test_send_alert_rate_limited(self, mocker):
        from alerting import alerting
        alerting._webhook_url = "https://hooks.example.com"
        mock_deliver = mocker.patch.object(alerting, "_deliver_webhook", AsyncMock())
        mocker.patch.object(alerting, "_send_logtail", AsyncMock())
        mocker.patch.object(alerting, "_log_console")
        mock_logger = mocker.patch("alerting.logger")

        await alerting.alert_warning("msg1", {"job_name": "myjob"})
        assert mock_deliver.call_count == 1

        await alerting.alert_warning("msg2", {"job_name": "myjob"})
        assert mock_deliver.call_count == 1
        mock_logger.info.assert_called_with(
            "Alert rate-limited (webhook skipped)", job_name="myjob", severity="WARNING"
        )

    async def test_send_alert_different_keys_not_rate_limited(self, mocker):
        from alerting import alerting
        alerting._webhook_url = "https://hooks.example.com"
        mock_deliver = mocker.patch.object(alerting, "_deliver_webhook", AsyncMock())
        mocker.patch.object(alerting, "_send_logtail", AsyncMock())
        mocker.patch.object(alerting, "_log_console")

        await alerting.alert_critical("c1", {"job_name": "j1"})
        await alerting.alert_critical("c2", {"job_name": "j2"})
        await alerting.alert_info("i1", {"job_name": "j1"})
        assert mock_deliver.call_count == 3

    async def test_send_alert_no_details(self, mocker):
        from alerting import alerting
        alerting._webhook_url = "https://hooks.example.com"
        mocker.patch.object(alerting, "_deliver_webhook", AsyncMock())
        mocker.patch.object(alerting, "_send_logtail", AsyncMock())
        mocker.patch.object(alerting, "_log_console")
        alerting._rate_limiter.can_alert = AsyncMock(return_value=True)
        await alerting.alert_info("bare", None)
        alerting._send_logtail.assert_awaited_once()

    async def test_alert_critical(self, mocker):
        from alerting import alerting
        mock_send = AsyncMock()
        mocker.patch.object(alerting, "_send_alert", mock_send)
        await alerting.alert_critical("crit", {"x": 1})
        mock_send.assert_awaited_once_with("CRITICAL", "crit", {"x": 1})

    async def test_alert_warning(self, mocker):
        from alerting import alerting
        mock_send = AsyncMock()
        mocker.patch.object(alerting, "_send_alert", mock_send)
        await alerting.alert_warning("warn", {"y": 2})
        mock_send.assert_awaited_once_with("WARNING", "warn", {"y": 2})

    async def test_alert_info(self, mocker):
        from alerting import alerting
        mock_send = AsyncMock()
        mocker.patch.object(alerting, "_send_alert", mock_send)
        await alerting.alert_info("info", {"z": 3})
        mock_send.assert_awaited_once_with("INFO", "info", {"z": 3})


# ═══════════════════════════════════════════════════════════════════════════════
# health_check — dependency checks, file I/O, alerts
# ═══════════════════════════════════════════════════════════════════════════════

class TestHealthCheck:

    @pytest.fixture(autouse=True)
    def preserve_env(self):
        old = {
            "USE_LOCAL_AI": os.environ.get("USE_LOCAL_AI", ""),
        }
        os.environ["USE_LOCAL_AI"] = "true"
        yield
        for k, v in old.items():
            if v:
                os.environ[k] = v
            else:
                os.environ.pop(k, None)

    @pytest.fixture(autouse=True)
    def mock_supabase(self, mocker):
        mock = mocker.patch("config.core.supabase.get_supabase_client")
        mock.return_value.from_.return_value.select.return_value.limit.return_value.execute.return_value = MagicMock()
        return mock

    async def test_healthy(self, mocker):
        mocker.patch(
            "crons.health_check.failure_tracker.get_summary",
            AsyncMock(return_value={
                "open_circuits": [], "failing_jobs": [],
                "total_daily_failures": 0, "consecutive_failures": {}, "daily_failures": {},
            }),
        )
        mock_client = AsyncMock()
        mock_client.get.return_value = MagicMock(status_code=200)
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)
        mocker.patch("crons.health_check.httpx.AsyncClient", return_value=mock_ctx)
        mock_open = mocker.patch("builtins.open", MagicMock())
        mocker.patch("crons.health_check.logger")
        from crons.health_check import run_health_check
        await run_health_check()
        mock_open.assert_called_once()

    async def test_supabase_fails(self, mocker, mock_supabase):
        mocker.patch(
            "crons.health_check.failure_tracker.get_summary",
            AsyncMock(return_value={
                "open_circuits": [], "failing_jobs": [],
                "total_daily_failures": 0, "consecutive_failures": {}, "daily_failures": {},
            }),
        )
        mock_supabase.side_effect = Exception("DB down")
        mock_logger = mocker.patch("crons.health_check.logger")
        mock_client = AsyncMock()
        mock_client.get.return_value = MagicMock(status_code=200)
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)
        mocker.patch("crons.health_check.httpx.AsyncClient", return_value=mock_ctx)
        mocker.patch("builtins.open", MagicMock())
        from crons.health_check import run_health_check
        await run_health_check()
        mock_logger.warn.assert_called_with("Health check: Supabase unavailable", error="DB down")

    async def test_ollama_available(self, mocker):
        mocker.patch(
            "crons.health_check.failure_tracker.get_summary",
            AsyncMock(return_value={
                "open_circuits": [], "failing_jobs": [],
                "total_daily_failures": 0, "consecutive_failures": {}, "daily_failures": {},
            }),
        )
        mock_client = AsyncMock()
        mock_client.get.return_value = MagicMock(status_code=200)
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)
        mocker.patch("crons.health_check.httpx.AsyncClient", return_value=mock_ctx)
        mock_open = mocker.patch("builtins.open", MagicMock())
        mocker.patch("crons.health_check.logger")
        from crons.health_check import run_health_check
        await run_health_check()
        mock_open.assert_called_once()

    async def test_ollama_unavailable(self, mocker):
        mocker.patch(
            "crons.health_check.failure_tracker.get_summary",
            AsyncMock(return_value={
                "open_circuits": [], "failing_jobs": [],
                "total_daily_failures": 0, "consecutive_failures": {}, "daily_failures": {},
            }),
        )
        mock_client = AsyncMock()
        mock_client.get.return_value = MagicMock(status_code=503)
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)
        mocker.patch("crons.health_check.httpx.AsyncClient", return_value=mock_ctx)
        mocker.patch("builtins.open", MagicMock())
        mocker.patch("crons.health_check.logger")
        from crons.health_check import run_health_check
        await run_health_check()

    async def test_ollama_not_configured(self, mocker):
        os.environ["USE_LOCAL_AI"] = "false"
        mocker.patch(
            "crons.health_check.failure_tracker.get_summary",
            AsyncMock(return_value={
                "open_circuits": [], "failing_jobs": [],
                "total_daily_failures": 0, "consecutive_failures": {}, "daily_failures": {},
            }),
        )
        mock_ctx = MagicMock()
        mocker.patch("crons.health_check.httpx.AsyncClient", return_value=mock_ctx)
        mocker.patch("builtins.open", MagicMock())
        mocker.patch("crons.health_check.logger")
        from crons.health_check import run_health_check
        await run_health_check()
        mock_ctx.__aenter__.assert_not_called()

    async def test_open_circuits_alert(self, mocker):
        mocker.patch(
            "crons.health_check.failure_tracker.get_summary",
            AsyncMock(return_value={
                "open_circuits": ["breaker_job"],
                "failing_jobs": [{"job_name": "breaker_job", "consecutive_failures": 5}],
                "total_daily_failures": 5, "consecutive_failures": {"breaker_job": 5},
                "daily_failures": {"breaker_job": 5},
            }),
        )
        mock_client = AsyncMock()
        mock_client.get.return_value = MagicMock(status_code=200)
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
        assert "circuit breakers open" in mock_alert.await_args[1]["message"]

    async def test_file_write_error(self, mocker):
        mocker.patch(
            "crons.health_check.failure_tracker.get_summary",
            AsyncMock(return_value={
                "open_circuits": [], "failing_jobs": [],
                "total_daily_failures": 0, "consecutive_failures": {}, "daily_failures": {},
            }),
        )
        mock_client = AsyncMock()
        mock_client.get.return_value = MagicMock(status_code=200)
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_client)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)
        mocker.patch("crons.health_check.httpx.AsyncClient", return_value=mock_ctx)
        mocker.patch("builtins.open", side_effect=OSError("Disk full"))
        mock_logger = mocker.patch("crons.health_check.logger")
        from crons.health_check import run_health_check
        await run_health_check()
        mock_logger.error.assert_called_with("Failed to write health status file", error="Disk full")


# ═══════════════════════════════════════════════════════════════════════════════
# deadline_alert — full coverage (previously untested)
# ═══════════════════════════════════════════════════════════════════════════════

class TestDeadlineAlert:

    async def test_supabase_query_exception(self, mocker):
        mock_supabase = mocker.patch("crons.deadline_alert.get_supabase_client")
        mock_supabase().from_().select().not_.is_().lte().execute.side_effect = Exception("DB error")
        mock_logger = mocker.patch("crons.deadline_alert.logger")
        from crons.deadline_alert import run_deadline_alert
        result = await run_deadline_alert()
        assert result == 0
        mock_logger.error.assert_called()

    async def test_no_opportunities(self, mocker):
        mock_supabase = mocker.patch("crons.deadline_alert.get_supabase_client")
        mock_supabase().from_().select().not_.is_().lte().execute.return_value = MagicMock(data=[])
        mock_logger = mocker.patch("crons.deadline_alert.logger")
        from crons.deadline_alert import run_deadline_alert
        result = await run_deadline_alert()
        assert result == 0
        mock_logger.info.assert_called_with("Deadline alert: no opportunities closing within 48h")

    async def test_all_deadlines_passed(self, mocker):
        mock_supabase = mocker.patch("crons.deadline_alert.get_supabase_client")
        past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        mock_supabase().from_().select().not_.is_().lte().execute.return_value = MagicMock(
            data=[{"id": "o1", "deadline": past, "title": "Old", "user_id": "u1"}]
        )
        mock_logger = mocker.patch("crons.deadline_alert.logger")
        from crons.deadline_alert import run_deadline_alert
        result = await run_deadline_alert()
        assert result == 0
        mock_logger.info.assert_called_with("Deadline alert: no upcoming deadlines within 48h")

    async def test_existing_alert_deduplicated(self, mocker):
        now = datetime.now(timezone.utc)
        future = (now + timedelta(hours=12)).isoformat()
        mocker.patch("crons.deadline_alert.datetime")
        from crons.deadline_alert import datetime as dt_fake
        dt_fake.now.return_value = now
        dt_fake.fromisoformat.side_effect = lambda s: datetime.fromisoformat(s)
        dt_fake.timedelta = timedelta
        dt_fake.timezone = timezone
        mock_supabase = mocker.patch("crons.deadline_alert.get_supabase_client")
        mock_supabase().from_().select().not_.is_().lte().execute.return_value = MagicMock(
            data=[{"id": "opp1", "deadline": future, "title": "Internship", "match_score": 92, "user_id": "u1"}]
        )
        mock_supabase().from_().select().eq().eq().execute.return_value = MagicMock(
            data=[{"id": "n1", "action_url": "/opportunities?id=opp1"}]
        )
        mock_logger = mocker.patch("crons.deadline_alert.logger")
        from crons.deadline_alert import run_deadline_alert
        result = await run_deadline_alert()
        assert result == 0
        mock_supabase().from_().insert.assert_not_called()

    async def test_creates_notification_critical_urgency(self, mocker):
        now = datetime.now(timezone.utc)
        future = (now + timedelta(hours=6)).isoformat()
        mock_supabase = mocker.patch("crons.deadline_alert.get_supabase_client")
        mock_supabase().from_().select().not_.is_().lte().execute.return_value = MagicMock(
            data=[{"id": "opp2", "deadline": future, "title": "Fast Track", "match_score": 88, "user_id": "u1"}]
        )
        mock_supabase().from_().select().eq().eq().execute.return_value = MagicMock(data=[])
        mock_supabase().from_().insert().execute.return_value = MagicMock(data=[{"id": "new_n"}])
        mock_logger = mocker.patch("crons.deadline_alert.logger")
        from crons.deadline_alert import run_deadline_alert
        result = await run_deadline_alert()
        assert result == 1
        insert_call = mock_supabase().from_().insert.call_args
        payload = insert_call[0][0]
        assert payload["priority"] == "high"
        assert payload["category"] == "deadline_alert"
        assert "Fast Track" in payload["title"]

    async def test_creates_notification_warning_urgency(self, mocker):
        now = datetime.now(timezone.utc)
        future = (now + timedelta(hours=36)).isoformat()
        mock_supabase = mocker.patch("crons.deadline_alert.get_supabase_client")
        mock_supabase().from_().select().not_.is_().lte().execute.return_value = MagicMock(
            data=[{"id": "opp3", "deadline": future, "title": "Scholarship", "match_score": 75, "user_id": "u2"}]
        )
        mock_supabase().from_().select().eq().eq().execute.return_value = MagicMock(data=[])
        mock_supabase().from_().insert().execute.return_value = MagicMock(data=[{"id": "new_n2"}])
        mock_logger = mocker.patch("crons.deadline_alert.logger")
        from crons.deadline_alert import run_deadline_alert
        result = await run_deadline_alert()
        assert result == 1
        payload = mock_supabase().from_().insert.call_args[0][0]
        assert payload["priority"] == "medium"

    async def test_exception_during_individual_opportunity(self, mocker):
        now = datetime.now(timezone.utc)
        future = (now + timedelta(hours=24)).isoformat()
        mock_supabase = mocker.patch("crons.deadline_alert.get_supabase_client")
        mock_supabase().from_().select().not_.is_().lte().execute.return_value = MagicMock(
            data=[
                {"id": "opp_a", "deadline": future, "title": "A", "match_score": 80, "user_id": "u1"},
                {"id": "opp_b", "deadline": future, "title": "B", "match_score": 85, "user_id": "u1"},
            ]
        )
        calls = [MagicMock(data=[]), Exception("Insert failed")]
        mock_supabase().from_().select().eq().eq().execute.side_effect = [MagicMock(data=[]), None]
        mock_supabase().from_().insert().execute.side_effect = [MagicMock(data=[{"id": "n1"}]), None]
        mock_supabase().from_().insert().execute.side_effect = [MagicMock(data=[{"id": "n1"}]), Exception("Insert err")]
        mock_logger = mocker.patch("crons.deadline_alert.logger")
        from crons.deadline_alert import run_deadline_alert
        result = await run_deadline_alert()
        assert result == 1
        mock_logger.error.assert_called()

    async def test_multiple_opportunities_partially_deduplicated(self, mocker):
        now = datetime.now(timezone.utc)
        future = (now + timedelta(hours=24)).isoformat()
        mock_supabase = mocker.patch("crons.deadline_alert.get_supabase_client")
        mock_supabase().from_().select().not_.is_().lte().execute.return_value = MagicMock(
            data=[
                {"id": "opp_x", "deadline": future, "title": "X", "match_score": 90, "user_id": "u1"},
                {"id": "opp_y", "deadline": future, "title": "Y", "match_score": 70, "user_id": "u1"},
            ]
        )
        mock_supabase().from_().select().eq().eq().execute.side_effect = [
            MagicMock(data=[{"id": "n1", "action_url": "/opportunities?id=opp_x"}]),
            MagicMock(data=[]),
        ]
        mock_supabase().from_().insert().execute.return_value = MagicMock(data=[{"id": "new_y"}])
        mock_logger = mocker.patch("crons.deadline_alert.logger")
        from crons.deadline_alert import run_deadline_alert
        result = await run_deadline_alert()
        assert result == 1
        inserted = mock_supabase().from_().insert.call_args[0][0]
        assert inserted["title"] == "Opportunity Closing Soon: Y"


# ═══════════════════════════════════════════════════════════════════════════════
# Cron modules — additional edge cases
# ═══════════════════════════════════════════════════════════════════════════════

class TestDailyBriefingCron:

    async def test_normal_flow(self, mocker):
        mock_supabase = mocker.patch("crons.daily_briefing.get_supabase_client")
        mock_supabase().from_().select().execute.return_value.data = [{"id": "u1"}]
        mock_gen = mocker.patch("crons.daily_briefing.generate_daily_briefing",
                                return_value={"productivity_score": 85})
        mocker.patch("crons.daily_briefing.sanitize_input", side_effect=lambda x: x)
        from crons.daily_briefing import run_daily_briefing
        await run_daily_briefing()
        mock_gen.assert_awaited_once_with("u1")

    async def test_empty_users(self, mocker):
        mock_supabase = mocker.patch("crons.daily_briefing.get_supabase_client")
        mock_supabase().from_().select().execute.return_value.data = []
        mock_gen = mocker.patch("crons.daily_briefing.generate_daily_briefing")
        from crons.daily_briefing import run_daily_briefing
        await run_daily_briefing()
        mock_gen.assert_not_called()

    async def test_user_exception(self, mocker):
        mock_supabase = mocker.patch("crons.daily_briefing.get_supabase_client")
        mock_supabase().from_().select().execute.return_value.data = [{"id": "u1"}, {"id": "u2"}]
        mock_gen = mocker.patch("crons.daily_briefing.generate_daily_briefing",
                                side_effect=[Exception("AI error"), {"productivity_score": 90}])
        mocker.patch("crons.daily_briefing.sanitize_input", side_effect=lambda x: x)
        from crons.daily_briefing import run_daily_briefing
        await run_daily_briefing()
        assert mock_gen.await_count == 2


class TestOpportunityRadarCron:

    async def test_normal_flow(self, mocker):
        mock_supabase = mocker.patch("crons.opportunity_radar.get_supabase_client")
        mock_supabase().from_().select().execute.return_value.data = [{"id": "u1"}]
        mock_radar = mocker.patch("crons.opportunity_radar.run_opportunity_radar",
                                  return_value=[{"title": "Opp1"}])
        mocker.patch("crons.opportunity_radar.sanitize_input", side_effect=lambda x: x)
        from crons.opportunity_radar import run_radar
        await run_radar()
        mock_radar.assert_awaited_once_with("u1")

    async def test_empty_users(self, mocker):
        mock_supabase = mocker.patch("crons.opportunity_radar.get_supabase_client")
        mock_supabase().from_().select().execute.return_value.data = []
        mock_radar = mocker.patch("crons.opportunity_radar.run_opportunity_radar")
        from crons.opportunity_radar import run_radar
        await run_radar()
        mock_radar.assert_not_called()


class TestWeeklyReviewCron:

    async def test_normal_flow(self, mocker):
        mock_supabase = mocker.patch("crons.weekly_review.get_supabase_client")
        mock_supabase().from_().select().execute.return_value.data = [{"id": "u1"}]
        mock_review = mocker.patch("crons.weekly_review.generate_weekly_review",
                                   return_value={"completion_rate": 0.8})
        mocker.patch("crons.weekly_review.sanitize_input", side_effect=lambda x: x)
        from crons.weekly_review import run_weekly_review
        await run_weekly_review()
        mock_review.assert_awaited_once_with("u1")

    async def test_error(self, mocker):
        mock_supabase = mocker.patch("crons.weekly_review.get_supabase_client")
        mock_supabase().from_().select().execute.return_value.data = [{"id": "u1"}]
        mock_review = mocker.patch("crons.weekly_review.generate_weekly_review",
                                   side_effect=Exception("Gen failed"))
        mocker.patch("crons.weekly_review.sanitize_input", side_effect=lambda x: x)
        from crons.weekly_review import run_weekly_review
        await run_weekly_review()
        mock_review.assert_awaited_once_with("u1")


class TestHabitCheckerCron:

    def _make_query_chain(self, execute_responses):
        """Build a mock chain where execute() iterates through responses."""
        it = iter(execute_responses)
        chain = MagicMock()
        chain.execute = MagicMock(side_effect=lambda: next(it))
        chain.select.return_value = chain
        chain.eq.return_value = chain
        chain.gte.return_value = chain
        return chain

    async def test_habit_logged_today(self, mocker):
        mock_supabase = mocker.patch("crons.habit_checker.get_supabase_client")
        mock_date_patch = mocker.patch("crons.habit_checker.date")
        mock_date_patch.today.return_value.isoformat.return_value = "2026-07-13"
        chain = self._make_query_chain([
            MagicMock(data=[{"id": "u1"}]),
            MagicMock(data=[{"id": "h1", "name": "Read"}]),
            MagicMock(data=[{"id": "log1"}]),
        ])
        mock_supabase().from_.return_value = chain
        mock_logger = mocker.patch("crons.habit_checker.logger")
        from crons.habit_checker import run_habit_checker
        await run_habit_checker()
        mock_logger.info.assert_not_called()

    async def test_habit_not_logged(self, mocker):
        mock_supabase = mocker.patch("crons.habit_checker.get_supabase_client")
        mock_date_patch = mocker.patch("crons.habit_checker.date")
        mock_date_patch.today.return_value.isoformat.return_value = "2026-07-13"
        chain = self._make_query_chain([
            MagicMock(data=[{"id": "u1"}]),
            MagicMock(data=[{"id": "h1", "name": "Exercise"}]),
            MagicMock(data=[]),
        ])
        mock_supabase().from_.return_value = chain
        mock_logger = mocker.patch("crons.habit_checker.logger")
        from crons.habit_checker import run_habit_checker
        await run_habit_checker()
        mock_logger.info.assert_called_with("Habit not logged today", user_id="u1", habit_name="Exercise")

    async def test_no_active_habits(self, mocker):
        mock_supabase = mocker.patch("crons.habit_checker.get_supabase_client")
        mock_date_patch = mocker.patch("crons.habit_checker.date")
        mock_date_patch.today.return_value.isoformat.return_value = "2026-07-13"
        chain = self._make_query_chain([
            MagicMock(data=[{"id": "u1"}]),
            MagicMock(data=[]),
        ])
        mock_supabase().from_.return_value = chain
        from crons.habit_checker import run_habit_checker
        await run_habit_checker()


class TestMissedTaskCheckerCron:

    async def test_marks_overdue_as_missed(self, mocker):
        from crons.missed_task_checker import run_missed_task_checker
        mock_supabase = mocker.patch("crons.missed_task_checker.get_supabase_client")
        mocker.patch("crons.missed_task_checker.datetime")
        it = iter([
            MagicMock(data=[{"id": "u1"}]),
            MagicMock(data=[{"id": "t1", "missed_count": 0}]),
        ])
        chain = MagicMock()
        chain.execute = MagicMock(side_effect=lambda: next(it))
        chain.eq.return_value = chain
        chain.lt.return_value = chain
        chain.select.return_value = chain
        chain.update.return_value = MagicMock(eq=lambda x: MagicMock(execute=MagicMock()))
        mock_supabase().from_.return_value = chain
        await run_missed_task_checker()
        chain.update.assert_called_once_with({"status": "missed", "missed_count": 1})

    async def test_no_overdue(self, mocker):
        from crons.missed_task_checker import run_missed_task_checker
        mock_supabase = mocker.patch("crons.missed_task_checker.get_supabase_client")
        mocker.patch("crons.missed_task_checker.datetime")
        it = iter([
            MagicMock(data=[{"id": "u1"}]),
            MagicMock(data=[]),
        ])
        chain = MagicMock()
        chain.execute = MagicMock(side_effect=lambda: next(it))
        chain.eq.return_value = chain
        chain.lt.return_value = chain
        chain.select.return_value = chain
        chain.update.return_value = chain
        mock_supabase().from_.return_value = chain
        await run_missed_task_checker()
        chain.update.assert_not_called()


class TestSleepReminderCron:

    async def test_already_logged(self, mocker):
        from crons.sleep_reminder import run_sleep_reminder
        mock_supabase = mocker.patch("crons.sleep_reminder.get_supabase_client")
        mocker.patch("crons.sleep_reminder.date")
        it = iter([
            MagicMock(data=[{"id": "u1", "sleep_goal_bedtime": "23:00"}]),
            MagicMock(data=[{"id": "log1"}]),
        ])
        chain = MagicMock()
        chain.execute = MagicMock(side_effect=lambda: next(it))
        chain.select.return_value = chain
        chain.eq.return_value = chain
        chain.gte.return_value = chain
        mock_supabase().from_.return_value = chain
        mock_suggest = mocker.patch("crons.sleep_reminder.suggest_bedtime")
        await run_sleep_reminder()
        mock_suggest.assert_not_called()

    async def test_not_logged_sends_nudge(self, mocker):
        from crons.sleep_reminder import run_sleep_reminder
        mock_supabase = mocker.patch("crons.sleep_reminder.get_supabase_client")
        mocker.patch("crons.sleep_reminder.date")
        it = iter([
            MagicMock(data=[{"id": "u1", "sleep_goal_bedtime": "23:00"}]),
            MagicMock(data=[]),
        ])
        chain = MagicMock()
        chain.execute = MagicMock(side_effect=lambda: next(it))
        chain.select.return_value = chain
        chain.eq.return_value = chain
        chain.gte.return_value = chain
        mock_supabase().from_.return_value = chain
        mock_suggest = mocker.patch("crons.sleep_reminder.suggest_bedtime",
                                    return_value={"suggested_bedtime": "22:30"})
        mocker.patch("crons.sleep_reminder.sanitize_input", side_effect=lambda x: x)
        await run_sleep_reminder()
        mock_suggest.assert_awaited_once_with("u1")


class TestCourseNudgeCron:

    async def test_normal_with_nudges(self, mocker):
        mock_supabase = mocker.patch("crons.course_nudge.get_supabase_client")
        mock_supabase().from_().select().execute.return_value.data = [{"id": "u1"}]
        mock_nudge = mocker.patch("crons.course_nudge.run_all_nudges",
                                  return_value={"total_nudges": 2, "course_nudges": [{}], "habit_nudges": [{}]})
        mocker.patch("crons.course_nudge.sanitize_input", side_effect=lambda x: x)
        from crons.course_nudge import run_course_nudges
        await run_course_nudges()
        mock_nudge.assert_awaited_once_with("u1")

    async def test_exception(self, mocker):
        mock_supabase = mocker.patch("crons.course_nudge.get_supabase_client")
        mock_supabase().from_().select().execute.return_value.data = [{"id": "u1"}, {"id": "u2"}]
        mock_nudge = mocker.patch("crons.course_nudge.run_all_nudges",
                                  side_effect=[Exception("fail"), {"total_nudges": 0, "course_nudges": [], "habit_nudges": []}])
        mocker.patch("crons.course_nudge.sanitize_input", side_effect=lambda x: x)
        from crons.course_nudge import run_course_nudges
        await run_course_nudges()
        assert mock_nudge.await_count == 2

    async def test_empty_users(self, mocker):
        mock_supabase = mocker.patch("crons.course_nudge.get_supabase_client")
        mock_supabase().from_().select().execute.return_value.data = []
        mock_nudge = mocker.patch("crons.course_nudge.run_all_nudges")
        from crons.course_nudge import run_course_nudges
        await run_course_nudges()
        mock_nudge.assert_not_called()


# ═══════════════════════════════════════════════════════════════════════════════
# main.py — _wrap_cron
# ═══════════════════════════════════════════════════════════════════════════════

@NEED_APSCHEDULER
class TestWrapCron:
    """Cover _wrap_cron success/fast/slow/failure paths."""

    async def test_success_fast(self, mocker):
        import main as main_module
        from main import _wrap_cron
        mocker.patch("main.time.time", side_effect=[100.0, 100.3])
        mocker.patch.object(main_module.failure_tracker, "record_success", AsyncMock())
        mock_logger = mocker.patch("main.logger")
        async def good(): return "ok"
        wrapped = _wrap_cron("fast_j", good)
        result = await wrapped()
        assert result == "ok"
        main_module.failure_tracker.record_success.assert_awaited_once_with("fast_j")
        mock_logger.info.assert_called_with("Cron job completed", job_name="fast_j", duration_ms=300.0)

    async def test_success_slow(self, mocker):
        import main as main_module
        from main import _wrap_cron
        mocker.patch("main.time.time", side_effect=[100.0, 106.5])
        mocker.patch.object(main_module.failure_tracker, "record_success", AsyncMock())
        mock_logger = mocker.patch("main.logger")
        async def slow(): return "done"
        wrapped = _wrap_cron("slow_j", slow)
        result = await wrapped()
        assert result == "done"
        mock_logger.info.assert_called_with("Cron job completed (slow)", job_name="slow_j", duration_ms=6500.0)

    async def test_failure(self, mocker):
        import main as main_module
        from main import _wrap_cron
        mocker.patch("main.time.time", side_effect=[100.0, 101.0])
        mocker.patch.object(main_module.failure_tracker, "record_failure", AsyncMock())
        mock_alert = mocker.patch.object(main_module.alerting, "alert_warning", AsyncMock())
        mocker.patch("main.logger")
        async def fail(): raise ValueError("broke")
        wrapped = _wrap_cron("fail_j", fail)
        result = await wrapped()
        assert result is None
        main_module.failure_tracker.record_failure.assert_awaited_once_with("fail_j", "broke")
        mock_alert.assert_awaited_once()

    async def test_failure_details(self, mocker):
        import main as main_module
        from main import _wrap_cron
        mocker.patch("main.time.time", side_effect=[200.0, 202.5])
        mocker.patch.object(main_module.failure_tracker, "record_failure", AsyncMock())
        mock_alert = mocker.patch.object(main_module.alerting, "alert_warning", AsyncMock())
        mocker.patch("main.logger")
        async def err(): raise RuntimeError("crash")
        wrapped = _wrap_cron("detail_j", err)
        await wrapped()
        kwargs = mock_alert.await_args[1]
        assert kwargs["details"]["job_name"] == "detail_j"
        assert kwargs["details"]["duration_ms"] == 2500.0
        assert kwargs["details"]["error_message"] == "crash"

    async def test_return_value_preserved(self, mocker):
        import main as main_module
        from main import _wrap_cron
        mocker.patch("main.time.time", side_effect=[1.0, 1.1])
        mocker.patch.object(main_module.failure_tracker, "record_success", AsyncMock())
        mocker.patch("main.logger")
        async def returns_dict(): return {"key": "val"}
        wrapped = _wrap_cron("dict_j", returns_dict)
        result = await wrapped()
        assert result == {"key": "val"}


# ═══════════════════════════════════════════════════════════════════════════════
# main.py — _scheduler_listener
# ═══════════════════════════════════════════════════════════════════════════════

@NEED_APSCHEDULER
class TestSchedulerListener:
    """Cover EVENT_JOB_ERROR, EVENT_JOB_MISSED, job found/not found, missing attrs."""

    async def test_job_error(self, mocker):
        import main as main_module
        from apscheduler.events import EVENT_JOB_ERROR
        mock_event = MagicMock()
        mock_event.job_id = "job1"
        mock_event.code = EVENT_JOB_ERROR
        mock_event.exception = ValueError("bad")
        main_module.scheduler = MagicMock()
        main_module.scheduler.get_job.return_value = MagicMock(name="Job One")
        mock_alert = mocker.patch.object(main_module.alerting, "alert_warning", AsyncMock())
        await main_module._scheduler_listener(mock_event)
        assert "Unhandled exception" in mock_alert.await_args[1]["message"]

    async def test_job_missed(self, mocker):
        import main as main_module
        from apscheduler.events import EVENT_JOB_MISSED
        mock_event = MagicMock()
        mock_event.job_id = "job2"
        mock_event.code = EVENT_JOB_MISSED
        mock_event.scheduled_run_time = "2026-07-13T00:00:00"
        main_module.scheduler = MagicMock()
        main_module.scheduler.get_job.return_value = MagicMock(name="Job Two")
        mock_alert = mocker.patch.object(main_module.alerting, "alert_warning", AsyncMock())
        await main_module._scheduler_listener(mock_event)
        assert "missed" in mock_alert.await_args[1]["message"].lower()

    async def test_job_not_found(self, mocker):
        import main as main_module
        from apscheduler.events import EVENT_JOB_ERROR
        mock_event = MagicMock()
        mock_event.job_id = "orphan"
        mock_event.code = EVENT_JOB_ERROR
        mock_event.exception = RuntimeError()
        main_module.scheduler = MagicMock()
        main_module.scheduler.get_job.return_value = None
        mock_alert = mocker.patch.object(main_module.alerting, "alert_warning", AsyncMock())
        await main_module._scheduler_listener(mock_event)
        assert "orphan" in mock_alert.await_args[1]["message"]

    async def test_missing_event_attributes(self, mocker):
        import main as main_module
        from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED
        main_module.scheduler = MagicMock()
        main_module.scheduler.get_job.return_value = MagicMock(name="anon")
        mock_alert = mocker.patch.object(main_module.alerting, "alert_warning", AsyncMock())
        event = MagicMock(spec=[])
        event.job_id = "j1"
        event.code = EVENT_JOB_ERROR
        await main_module._scheduler_listener(event)
        assert mock_alert.await_args[1]["details"]["error_message"] == "unknown"
        event2 = MagicMock(spec=[])
        event2.job_id = "j2"
        event2.code = EVENT_JOB_MISSED
        await main_module._scheduler_listener(event2)


# ═══════════════════════════════════════════════════════════════════════════════
# main.py — setup_cron_jobs & write_initial_health
# ═══════════════════════════════════════════════════════════════════════════════

@NEED_APSCHEDULER
class TestSetupCronJobs:

    def test_registers_all_jobs_and_listener(self, mocker):
        import main as main_module
        main_module.scheduler = MagicMock()
        mock_jobs = []
        for i in range(14):
            j = MagicMock(spec=["id", "name"])
            j.id = f"j{i}"
            j.name = f"Job {i}"
            mock_jobs.append(j)
        main_module.scheduler.get_jobs.return_value = mock_jobs
        mocker.patch.object(main_module, "_wrap_cron", side_effect=lambda jid, fn: fn)
        mock_add_listener = mocker.patch.object(main_module.scheduler, "add_listener")
        main_module.setup_cron_jobs()
        assert main_module.scheduler.add_job.call_count == 14
        mock_add_listener.assert_called_once()


@NEED_APSCHEDULER
class TestWriteInitialHealth:

    def test_success(self):
        from main import write_initial_health
        mock_open = MagicMock()
        with patch("builtins.open", mock_open):
            write_initial_health()
        mock_open.assert_called_once()

    def test_file_write_exception(self, mocker):
        from main import write_initial_health
        mocker.patch("builtins.open", side_effect=OSError("Permission denied"))
        mock_logger = mocker.patch("main.logger")
        write_initial_health()
        mock_logger.warn.assert_called_with(
            "Failed to write initial health status", error="Permission denied"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# main.py — HealthHandler
# ═══════════════════════════════════════════════════════════════════════════════

@NEED_APSCHEDULER
class TestHealthHandler:

    def test_health_returns_200(self, mocker):
        from main import HealthHandler
        mocker.patch.object(HealthHandler, "_load_health", return_value={"status": "healthy"})
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

    def test_health_ready_healthy(self, mocker):
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

    def test_health_ready_degraded(self, mocker):
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

    def test_unknown_path_404(self, mocker):
        from main import HealthHandler
        mocker.patch.object(HealthHandler, "send_response")
        mocker.patch.object(HealthHandler, "end_headers")
        handler = HealthHandler.__new__(HealthHandler)
        handler.path = "/unknown"
        handler.command = "GET"
        handler.do_GET()
        handler.send_response.assert_called_with(404)

    def test_load_health_file_exists(self, mocker):
        from main import HealthHandler
        import tempfile
        handler = HealthHandler.__new__(HealthHandler)
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump({"status": "custom"}, tmp)
        tmp.close()
        import main as main_module
        original = main_module.HEALTH_STATUS_FILE
        main_module.HEALTH_STATUS_FILE = Path(tmp.name)
        try:
            result = handler._load_health()
            assert result == {"status": "custom"}
        finally:
            main_module.HEALTH_STATUS_FILE = original
            os.unlink(tmp.name)

    def test_load_health_file_not_found(self, mocker):
        from main import HealthHandler
        import main as main_module
        handler = HealthHandler.__new__(HealthHandler)
        original = main_module.HEALTH_STATUS_FILE
        main_module.HEALTH_STATUS_FILE = Path("nonexistent_XXXX.json")
        try:
            result = handler._load_health()
            assert result == {"status": "healthy", "service": "scheduler"}
        finally:
            main_module.HEALTH_STATUS_FILE = original

    def test_load_health_read_exception(self, mocker):
        from main import HealthHandler
        import main as main_module
        handler = HealthHandler.__new__(HealthHandler)
        original = main_module.HEALTH_STATUS_FILE
        main_module.HEALTH_STATUS_FILE = Path(".")
        try:
            result = handler._load_health()
            assert result == {"status": "healthy", "service": "scheduler"}
        finally:
            main_module.HEALTH_STATUS_FILE = original

    def test_includes_job_count(self, mocker):
        from main import HealthHandler
        mocker.patch.object(HealthHandler, "_load_health", return_value={"status": "healthy"})
        mocker.patch.object(HealthHandler, "send_response")
        mocker.patch.object(HealthHandler, "send_header")
        mocker.patch.object(HealthHandler, "end_headers")
        mocker.patch("main.scheduler.get_jobs", return_value=[1, 2, 3])
        handler = HealthHandler.__new__(HealthHandler)
        handler.path = "/health"
        handler.command = "GET"
        handler.wfile = MagicMock()
        handler.do_GET()
        written = json.loads(handler.wfile.write.call_args[0][0])
        assert written["jobs"] == 3

    def test_log_message_silenced(self):
        from main import HealthHandler
        handler = HealthHandler.__new__(HealthHandler)
        handler.log_message("some format %s", "arg")


# ═══════════════════════════════════════════════════════════════════════════════
# main.py — start_health_server & main()
# ═══════════════════════════════════════════════════════════════════════════════

@NEED_APSCHEDULER
class TestStartHealthServer:

    def test_creates_server(self, mocker):
        from main import start_health_server
        mock_server = MagicMock()
        mock_server.serve_forever.side_effect = Exception("Stop")
        with patch("main.HTTPServer", return_value=mock_server):
            with pytest.raises(Exception, match="Stop"):
                start_health_server()
        assert mock_server.serve_forever.called


@NEED_APSCHEDULER
class TestMainFunction:
    """Cover main() setup path and KeyboardInterrupt/SystemExit shutdown."""

    async def test_keyboard_interrupt(self, mocker):
        import main as main_module
        import asyncio
        main_module.scheduler = MagicMock()
        main_module.scheduler.start = MagicMock()
        mocker.patch.object(main_module, "write_initial_health")
        mocker.patch.object(main_module, "setup_cron_jobs")
        mocker.patch.object(main_module.threading, "Thread")
        mocker.patch.object(asyncio, "sleep", side_effect=KeyboardInterrupt())
        mock_alert_info = mocker.patch.object(main_module.alerting, "alert_info", AsyncMock())
        mock_flush = mocker.patch.object(main_module.alerting, "flush_pending", AsyncMock())
        mock_shutdown = mocker.patch.object(main_module.alerting, "shutdown", AsyncMock())
        mock_sched_shutdown = mocker.patch.object(main_module.scheduler, "shutdown")
        await main_module.main()
        main_module.write_initial_health.assert_called_once()
        main_module.setup_cron_jobs.assert_called_once()
        main_module.scheduler.start.assert_called_once()
        assert mock_alert_info.await_count >= 2
        mock_flush.assert_awaited_once()
        mock_sched_shutdown.assert_called_once_with(wait=False)

    async def test_system_exit(self, mocker):
        import main as main_module
        import asyncio
        main_module.scheduler = MagicMock()
        mocker.patch.object(main_module, "write_initial_health")
        mocker.patch.object(main_module, "setup_cron_jobs")
        mocker.patch.object(main_module.threading, "Thread")
        mocker.patch.object(asyncio, "sleep", side_effect=SystemExit())
        mocker.patch.object(main_module.alerting, "alert_info", AsyncMock())
        mocker.patch.object(main_module.alerting, "flush_pending", AsyncMock())
        mocker.patch.object(main_module.alerting, "shutdown", AsyncMock())
        mock_sched_shutdown = mocker.patch.object(main_module.scheduler, "shutdown")
        await main_module.main()
        mock_sched_shutdown.assert_called_once_with(wait=False)


# ═══════════════════════════════════════════════════════════════════════════════
# JOB_DEFINITIONS validation
# ═══════════════════════════════════════════════════════════════════════════════

@NEED_APSCHEDULER
class TestJobDefinitions:

    def test_all_14_jobs_defined(self):
        from main import JOB_DEFINITIONS
        assert len(JOB_DEFINITIONS) == 14

    def test_all_have_callable_func(self):
        from main import JOB_DEFINITIONS
        from apscheduler.triggers.cron import CronTrigger
        for func, trigger, job_id, job_name in JOB_DEFINITIONS:
            assert callable(func), f"{job_id} not callable"
            assert isinstance(trigger, CronTrigger), f"{job_id} trigger not CronTrigger"
            assert isinstance(job_id, str) and len(job_id) > 0
            assert isinstance(job_name, str) and len(job_name) > 0

    def test_all_ids_unique(self):
        from main import JOB_DEFINITIONS
        ids = [j[2] for j in JOB_DEFINITIONS]
        assert len(ids) == len(set(ids))

    def test_expected_ids_present(self):
        from main import JOB_DEFINITIONS
        ids = {j[2] for j in JOB_DEFINITIONS}
        expected = {
            "daily_briefing", "opportunity_radar", "weekly_review",
            "habit_checker", "missed_task_checker", "sleep_reminder",
            "course_nudge", "skill_intelligence_refresh", "skill_evidence_expiry",
            "skill_analytics_snapshot", "skill_mv_refresh", "skill_retention_cleanup",
            "deadline_alert", "health_check",
        }
        assert ids == expected

    def test_health_check_trigger_every_5min(self):
        from main import JOB_DEFINITIONS
        from datetime import datetime
        hc = [j for j in JOB_DEFINITIONS if j[2] == "health_check"][0]
        trigger = hc[1]
        next_fire = trigger.get_next_fire_time(None, datetime(2026, 7, 13, 12, 0))
        assert next_fire is not None
        assert next_fire.minute in (5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 0)

    def test_deadline_alert_trigger_every_hour(self):
        from main import JOB_DEFINITIONS
        from datetime import datetime
        da = [j for j in JOB_DEFINITIONS if j[2] == "deadline_alert"][0]
        trigger = da[1]
        next_fire = trigger.get_next_fire_time(None, datetime(2026, 7, 13, 10, 15))
        assert next_fire is not None
        assert next_fire.minute == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Skill cron modules — additional edge case coverage
# ═══════════════════════════════════════════════════════════════════════════════

class TestSkillIntelligenceRefresh:

    async def test_insert_exception(self, mocker):
        mock_supabase = mocker.patch("crons.skill_intelligence_refresh.get_supabase_client")
        mock_supabase().from_().select().eq().execute.return_value = MagicMock(
            data=[{"skill_id": "s1"}, {"skill_id": "s2"}]
        )
        mock_supabase().from_().update().eq().execute.return_value = MagicMock(data=[{"skill_id": "s1"}])
        call_count = [0]
        def insert_side(*a, **kw):
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("Insert failed")
            return MagicMock(execute=MagicMock(return_value=MagicMock(data=[{"id": "h1"}])))
        mock_supabase().from_().insert.side_effect = insert_side
        mock_logger = mocker.patch("crons.skill_intelligence_refresh.logger")
        from crons.skill_intelligence_refresh import run_skill_intelligence_refresh
        await run_skill_intelligence_refresh()
        assert call_count[0] == 2

    async def test_no_stale_skills(self, mocker):
        mock_supabase = mocker.patch("crons.skill_intelligence_refresh.get_supabase_client")
        mock_supabase().from_().select().eq().execute.return_value = MagicMock(data=[])
        from crons.skill_intelligence_refresh import run_skill_intelligence_refresh
        await run_skill_intelligence_refresh()


class TestSkillEvidenceExpiry:

    async def test_no_expired(self, mocker):
        mock_supabase = mocker.patch("crons.skill_evidence_expiry.get_supabase_client")
        mock_supabase().from_().select().lt().neq().execute.return_value = MagicMock(data=[])
        from crons.skill_evidence_expiry import run_skill_evidence_expiry
        await run_skill_evidence_expiry()

    async def test_expired_found(self, mocker):
        mock_supabase = mocker.patch("crons.skill_evidence_expiry.get_supabase_client")
        mock_supabase().from_().select().lt().neq().execute.return_value = MagicMock(
            data=[{"evidence_id": "e1"}, {"evidence_id": "e2"}]
        )
        from crons.skill_evidence_expiry import run_skill_evidence_expiry
        await run_skill_evidence_expiry()
        mock_supabase().from_().update().in_().execute.assert_called_once()


class TestSkillAnalyticsSnapshot:

    async def test_empty_users(self, mocker):
        mock_supabase = mocker.patch("crons.skill_analytics_snapshot.get_supabase_client")
        mock_supabase().from_().select().execute.return_value = MagicMock(data=[])
        from crons.skill_analytics_snapshot import run_skill_analytics_snapshot
        await run_skill_analytics_snapshot()

    async def test_no_skills_skips_upsert(self, mocker):
        from crons.skill_analytics_snapshot import run_skill_analytics_snapshot
        mock_supabase = mocker.patch("crons.skill_analytics_snapshot.get_supabase_client")
        mock_supabase().from_().select().execute.return_value = MagicMock(data=[{"id": "u1"}])
        mock_supabase().from_().select().eq().execute.return_value = MagicMock(data=[])
        mock_logger = mocker.patch("crons.skill_analytics_snapshot.logger")
        await run_skill_analytics_snapshot()
        mock_supabase().from_().upsert.assert_not_called()

    async def test_user_exception(self, mocker):
        from crons.skill_analytics_snapshot import run_skill_analytics_snapshot
        mock_supabase = mocker.patch("crons.skill_analytics_snapshot.get_supabase_client")
        mock_supabase().from_().select().execute.return_value = MagicMock(data=[{"id": "u1"}, {"id": "u2"}])
        mock_supabase().from_().select().eq().execute.side_effect = [
            MagicMock(data=[{"level": 3, "state": "active"}]),
            Exception("DB error"),
        ]
        await run_skill_analytics_snapshot()


class TestSkillMVRefresh:

    async def test_supabase_unavailable(self, mocker):
        mocker.patch("config.core.supabase.get_supabase_client", side_effect=Exception("No conn"))
        from crons.skill_mv_refresh import run_skill_mv_refresh
        await run_skill_mv_refresh()

    async def test_success(self, mocker):
        mock_supabase = mocker.patch("config.core.supabase.get_supabase_client")
        mock_supabase().rpc().execute.return_value = MagicMock(data=[], error=None)
        from crons.skill_mv_refresh import run_skill_mv_refresh
        await run_skill_mv_refresh()

    async def test_rpc_error(self, mocker):
        mock_supabase = mocker.patch("config.core.supabase.get_supabase_client")
        mock_supabase().rpc().execute.return_value = MagicMock(data=[], error=MagicMock(message="RPC fail"))
        from crons.skill_mv_refresh import run_skill_mv_refresh
        await run_skill_mv_refresh()

    async def test_rpc_exception(self, mocker):
        mock_supabase = mocker.patch("config.core.supabase.get_supabase_client")
        mock_supabase().rpc.side_effect = Exception("Connection lost")
        from crons.skill_mv_refresh import run_skill_mv_refresh
        await run_skill_mv_refresh()


class TestSkillRetentionCleanup:

    async def test_supabase_unavailable(self, mocker):
        mocker.patch("config.core.supabase.get_supabase_client", side_effect=Exception("No conn"))
        from crons.skill_retention_cleanup import run_skill_retention_cleanup
        await run_skill_retention_cleanup()

    async def test_all_cleanups(self, mocker):
        mock_supabase = mocker.patch("config.core.supabase.get_supabase_client")
        dt_patch = mocker.patch("crons.skill_retention_cleanup.datetime")
        dt_patch.now.return_value.timestamp.return_value = 1_000_000_000
        dt_patch.now.return_value.isoformat.return_value = "2026-07-13"
        mock_supabase().table().delete().eq().lt().execute.return_value = MagicMock(data=[{"id": "ev1"}], error=None)
        mock_supabase().table().delete().lt().execute.return_value = MagicMock(data=[{"id": "al1"}], error=None)
        from crons.skill_retention_cleanup import run_skill_retention_cleanup
        await run_skill_retention_cleanup()
        assert mock_supabase().table().delete.call_count >= 3

    async def test_cleanup_errors(self, mocker):
        mock_supabase = mocker.patch("config.core.supabase.get_supabase_client")
        dt_patch = mocker.patch("crons.skill_retention_cleanup.datetime")
        dt_patch.now.return_value.timestamp.return_value = 1_000_000_000
        dt_patch.now.return_value.isoformat.return_value = "2026-07-13"
        mock_supabase().table().delete().eq().lt().execute.side_effect = Exception("Evidence error")
        mock_supabase().table().delete().lt().execute.side_effect = Exception("Activity error")
        from crons.skill_retention_cleanup import run_skill_retention_cleanup
        await run_skill_retention_cleanup()

    async def test_cleanup_error_results(self, mocker):
        mock_supabase = mocker.patch("config.core.supabase.get_supabase_client")
        dt_patch = mocker.patch("crons.skill_retention_cleanup.datetime")
        dt_patch.now.return_value.timestamp.return_value = 1_000_000_000
        dt_patch.now.return_value.isoformat.return_value = "2026-07-13"
        mock_supabase().table().delete().eq().lt().execute.return_value = MagicMock(data=[], error=MagicMock(message="Del err"))
        mock_supabase().table().delete().lt().execute.return_value = MagicMock(data=[], error=MagicMock(message="Del err"))
        from crons.skill_retention_cleanup import run_skill_retention_cleanup
        await run_skill_retention_cleanup()



