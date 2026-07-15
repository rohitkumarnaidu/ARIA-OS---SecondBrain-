"""Comprehensive tests for shared utility modules — batch, ai_utils, date_utils, retention, logger, feature_flags."""

import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta
import json
import os
import logging

pytestmark = pytest.mark.asyncio

# =============================================================================
# batch.py
# =============================================================================


class TestBatchResult:
    def test_default_values(self):
        from shared.utils.batch import BatchResult

        r = BatchResult()
        assert r.results == {}
        assert r.errors == {}
        assert r.completed_at is None
        assert r.started_at is not None

    def test_duration_ms_without_completed_at(self):
        from shared.utils.batch import BatchResult

        r = BatchResult()
        ms = r.duration_ms
        assert isinstance(ms, float)
        assert ms >= 0

    def test_duration_ms_with_completed_at(self):
        from shared.utils.batch import BatchResult

        r = BatchResult()
        r.completed_at = r.started_at + timedelta(seconds=2)
        assert r.duration_ms == 2000.0

    def test_success_count(self):
        from shared.utils.batch import BatchResult

        r = BatchResult()
        assert r.success_count == 0
        r.ok("a", 1)
        r.ok("b", 2)
        assert r.success_count == 2

    def test_error_count(self):
        from shared.utils.batch import BatchResult

        r = BatchResult()
        assert r.error_count == 0
        r.fail("a", "err1")
        r.fail("b", "err2")
        assert r.error_count == 2

    def test_fail(self):
        from shared.utils.batch import BatchResult

        r = BatchResult()
        r.fail("x", "something went wrong")
        assert r.errors["x"] == "something went wrong"

    def test_ok(self):
        from shared.utils.batch import BatchResult

        r = BatchResult()
        r.ok("x", 42)
        assert r.results["x"] == 42

    def test_finish(self):
        from shared.utils.batch import BatchResult

        r = BatchResult()
        assert r.completed_at is None
        r.finish()
        assert r.completed_at is not None


class TestBatchExecutor:
    def test_init_default_concurrency(self):
        from shared.utils.batch import BatchExecutor

        e = BatchExecutor()
        assert e.concurrency == 5
        assert e._queries == []

    def test_add(self):
        from shared.utils.batch import BatchExecutor

        e = BatchExecutor()
        fn = lambda: None
        e.add("k1", fn, "arg1", extra="val")
        assert len(e._queries) == 1
        assert e._queries[0][0] == "k1"
        assert e._queries[0][1] is fn
        assert e._queries[0][2] == ("arg1",)
        assert e._queries[0][3] == {"extra": "val"}

    async def test_execute_all_succeed(self):
        from shared.utils.batch import BatchExecutor

        async def fetch_a():
            return "a_value"

        async def fetch_b():
            return "b_value"

        e = BatchExecutor()
        e.add("a", fetch_a)
        e.add("b", fetch_b)
        result = await e.execute()
        assert result.results == {"a": "a_value", "b": "b_value"}
        assert result.errors == {}
        assert result.completed_at is not None

    async def test_execute_some_fail(self):
        from shared.utils.batch import BatchExecutor

        async def good():
            return 42

        async def bad():
            raise ValueError("oops")

        e = BatchExecutor()
        e.add("good", good)
        e.add("bad", bad)
        result = await e.execute()
        assert result.results == {"good": 42}
        assert "oops" in result.errors["bad"]
        assert result.completed_at is not None

    async def test_execute_empty(self):
        from shared.utils.batch import BatchExecutor

        e = BatchExecutor()
        result = await e.execute()
        assert result.results == {}
        assert result.errors == {}
        assert result.completed_at is not None

    async def test_execute_mixed_sync_async(self):
        from shared.utils.batch import BatchExecutor

        async def async_fn():
            return "async"

        def sync_fn():
            return "sync"

        e = BatchExecutor()
        e.add("a", async_fn)
        e.add("b", sync_fn)
        result = await e.execute()
        assert result.results == {"a": "async", "b": "sync"}


class TestBatchSupabaseQueries:
    async def test_returns_correct_dict_structure(self):
        from shared.utils.batch import batch_supabase_queries

        async def fetch_one():
            return 1

        result = await batch_supabase_queries({"x": fetch_one})
        assert isinstance(result, dict)
        assert "data" in result
        assert "errors" in result
        assert "duration_ms" in result
        assert result["data"] == {"x": 1}
        assert result["errors"] == {}
        assert isinstance(result["duration_ms"], float)

    async def test_with_errors(self):
        from shared.utils.batch import batch_supabase_queries

        async def fail_fn():
            raise RuntimeError("failure")

        result = await batch_supabase_queries({"x": fail_fn})
        assert result["data"] == {}
        assert "failure" in result["errors"]["x"]


# =============================================================================
# ai_utils.py
# =============================================================================
# Note: httpx and anthropic are imported inside function bodies, not at module
# level. We patch them as top-level module references.


class TestGetAiResponse:
    @patch("shared.utils.ai_utils.get_ollama_response")
    @patch.dict(os.environ, {"USE_LOCAL_AI": "true"}, clear=False)
    def test_local_ai_true_calls_ollama(self, mock_ollama):
        from shared.utils.ai_utils import get_ai_response

        get_ai_response("hello")
        mock_ollama.assert_called_once_with("hello", None)

    @patch("shared.utils.ai_utils.get_claude_response")
    @patch.dict(os.environ, {"USE_LOCAL_AI": "false"}, clear=False)
    def test_local_ai_false_calls_claude(self, mock_claude):
        from shared.utils.ai_utils import get_ai_response

        get_ai_response("hello", context={"key": "val"})
        mock_claude.assert_called_once_with("hello", {"key": "val"})


class TestGetOllamaResponse:
    @patch("httpx.post")
    @patch("shared.utils.ai_utils.logger")
    def test_success(self, mock_logger, mock_post):
        from shared.utils.ai_utils import get_ollama_response

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Hello!"}
        mock_post.return_value = mock_response

        result = get_ollama_response("hi")
        assert result == "Hello!"

    @patch("httpx.post")
    @patch("shared.utils.ai_utils.logger")
    def test_non_200_status(self, mock_logger, mock_post):
        from shared.utils.ai_utils import get_ollama_response

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        result = get_ollama_response("hi")
        assert result == "AI response unavailable. Please try again later."

    @patch("httpx.post")
    @patch("shared.utils.ai_utils.logger")
    def test_exception(self, mock_logger, mock_post):
        from shared.utils.ai_utils import get_ollama_response

        mock_post.side_effect = Exception("connection failed")

        result = get_ollama_response("hi")
        assert result == "AI response unavailable. Please try again later."
        mock_logger.error.assert_called_once()

    @patch("httpx.post")
    @patch("shared.utils.ai_utils.logger")
    @patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://custom:11434"}, clear=False)
    def test_custom_url(self, mock_logger, mock_post):
        from shared.utils.ai_utils import get_ollama_response

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "ok"}
        mock_post.return_value = mock_response

        get_ollama_response("hi")
        mock_post.assert_called_once_with(
            "http://custom:11434/api/generate",
            json={"model": "llama2", "prompt": "hi", "stream": False},
            timeout=30,
        )


class TestGetClaudeResponse:
    from shared.utils.ai_utils import get_claude_response

    @patch("shared.utils.ai_utils.logger")
    @patch.dict(os.environ, {}, clear=False)
    def test_no_api_key(self, mock_logger):
        from shared.utils.ai_utils import get_claude_response

        if "CLAUDE_API_KEY" in os.environ:
            del os.environ["CLAUDE_API_KEY"]
        result = get_claude_response("hi")
        assert result == "Claude API key not configured."

    @patch("anthropic.Anthropic")
    @patch.dict(os.environ, {"CLAUDE_API_KEY": "sk-fake"}, clear=False)
    def test_success(self, mock_anthropic_cls):
        from shared.utils.ai_utils import get_claude_response

        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_message = MagicMock()
        mock_message.content[0].text = "Hello from Claude"
        mock_client.messages.create.return_value = mock_message

        result = get_claude_response("hi")
        assert result == "Hello from Claude"

    @patch("anthropic.Anthropic")
    @patch("shared.utils.ai_utils.logger")
    @patch.dict(os.environ, {"CLAUDE_API_KEY": "sk-fake"}, clear=False)
    def test_exception(self, mock_logger, mock_anthropic_cls):
        from shared.utils.ai_utils import get_claude_response

        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("api error")

        result = get_claude_response("hi")
        assert result == "AI response unavailable."
        mock_logger.error.assert_called_once()


class TestGenerateTaskSummary:
    def test_no_tasks(self):
        from shared.utils.ai_utils import generate_task_summary

        result = generate_task_summary([])
        assert result == "You have 0 pending tasks."

    def test_with_urgent(self):
        from shared.utils.ai_utils import generate_task_summary

        tasks = [
            {"priority": "urgent"},
            {"priority": "low"},
            {"priority": "urgent"},
        ]
        result = generate_task_summary(tasks)
        assert "2 are urgent" in result

    def test_with_high(self):
        from shared.utils.ai_utils import generate_task_summary

        tasks = [
            {"priority": "high"},
            {"priority": "urgent"},
            {"priority": "high"},
        ]
        result = generate_task_summary(tasks)
        assert "1 are urgent" in result
        assert "2 are high priority" in result

    def test_no_urgent_or_high(self):
        from shared.utils.ai_utils import generate_task_summary

        tasks = [{"priority": "low"}, {"priority": "medium"}]
        result = generate_task_summary(tasks)
        assert "You have 2 pending tasks." in result
        assert "urgent" not in result


class TestGenerateCourseRecommendation:
    def test_matching_skills(self):
        from shared.utils.ai_utils import generate_course_recommendation

        result = generate_course_recommendation(["python", "javascript"], [])
        assert len(result) <= 5
        assert "Python for Everybody" in result
        assert "JavaScript Fundamentals" in result

    def test_no_matching_skills(self):
        from shared.utils.ai_utils import generate_course_recommendation

        result = generate_course_recommendation(["rust", "c++"], [])
        assert result == []

    def test_limited_to_5(self):
        from shared.utils.ai_utils import generate_course_recommendation

        skills = ["python", "javascript", "react", "machine learning", "web development"]
        result = generate_course_recommendation(skills, [])
        assert len(result) <= 5


class TestSummarizeVideo:
    @patch("shared.utils.ai_utils.get_ai_response")
    def test_summarize_video(self, mock_get_ai):
        from shared.utils.ai_utils import summarize_video

        mock_get_ai.return_value = "Summary text"
        result = summarize_video("My Video", "Some long transcript content here")
        assert result == "Summary text"
        mock_get_ai.assert_called_once()
        call_arg = mock_get_ai.call_args[0][0]
        assert "My Video" in call_arg
        assert "Some long transcript" in call_arg


# =============================================================================
# date_utils.py
# =============================================================================


class TestGetCurrentIso:
    def test_returns_valid_iso(self):
        from shared.utils.date_utils import get_current_iso

        result = get_current_iso()
        assert isinstance(result, str)
        assert len(result) > 10


class TestParseDate:
    def test_valid_iso(self):
        from shared.utils.date_utils import parse_date

        result = parse_date("2026-06-15T10:00:00")
        assert result is not None
        assert result.year == 2026
        assert result.month == 6
        assert result.day == 15

    def test_valid_with_z(self):
        from shared.utils.date_utils import parse_date

        result = parse_date("2026-06-15T10:00:00Z")
        assert result is not None
        assert result.tzinfo is not None

    def test_invalid_returns_none(self):
        from shared.utils.date_utils import parse_date

        result = parse_date("not-a-date")
        assert result is None


class TestDaysUntil:
    @patch("shared.utils.date_utils.parse_date")
    def test_invalid_returns_0(self, mock_parse):
        from shared.utils.date_utils import days_until

        mock_parse.return_value = None
        assert days_until("bad") == 0

    @patch("shared.utils.date_utils.parse_date")
    def test_future_date(self, mock_parse):
        from shared.utils.date_utils import days_until

        target = datetime(2026, 6, 10)
        mock_parse.return_value = target

        with patch("shared.utils.date_utils.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 6, 1)
            result = days_until("2026-06-10")
            assert result == 9


class TestFormatRelativeTime:
    def test_months_ago(self):
        from shared.utils.date_utils import format_relative_time

        dt = datetime.now() - timedelta(days=150)
        assert "months ago" in format_relative_time(dt)

    def test_days_ago(self):
        from shared.utils.date_utils import format_relative_time

        dt = datetime.now() - timedelta(days=5)
        result = format_relative_time(dt)
        assert "days ago" in result

    def test_hours_ago(self):
        from shared.utils.date_utils import format_relative_time

        dt = datetime.now() - timedelta(hours=5)
        result = format_relative_time(dt)
        assert "hours ago" in result

    def test_minutes_ago(self):
        from shared.utils.date_utils import format_relative_time

        dt = datetime.now() - timedelta(minutes=5)
        result = format_relative_time(dt)
        assert "minutes ago" in result

    def test_just_now(self):
        from shared.utils.date_utils import format_relative_time

        dt = datetime.now() - timedelta(seconds=10)
        assert format_relative_time(dt) == "just now"

    def test_exact_boundaries(self):
        from shared.utils.date_utils import format_relative_time

        dt = datetime.now() - timedelta(days=31)
        assert "months ago" in format_relative_time(dt)
        dt = datetime.now() - timedelta(days=1, hours=1)
        assert "days ago" in format_relative_time(dt)
        dt = datetime.now() - timedelta(hours=1, minutes=1)
        assert "hours ago" in format_relative_time(dt)
        dt = datetime.now() - timedelta(minutes=1, seconds=1)
        assert "minutes ago" in format_relative_time(dt)


class TestGetWeekRange:
    def test_returns_tuple_of_dates(self):
        from shared.utils.date_utils import get_week_range

        start, end = get_week_range()
        assert isinstance(start, type(datetime.now().date()))
        assert isinstance(end, type(datetime.now().date()))
        assert start <= end
        assert start.weekday() == 0  # Always Monday


class TestGetMonthRange:
    def test_returns_tuple_of_dates(self):
        from shared.utils.date_utils import get_month_range

        start, end = get_month_range()
        assert isinstance(start, type(datetime.now().date()))
        assert isinstance(end, type(datetime.now().date()))
        assert start.day == 1
        assert start <= end

    @patch("shared.utils.date_utils.datetime")
    def test_december_branch(self, mock_datetime):
        from shared.utils.date_utils import get_month_range

        mock_datetime.now.return_value = datetime(2026, 12, 15)

        start, end = get_month_range()
        assert start.month == 12
        assert start.day == 1
        assert end.month == 12
        assert end.day == 31


class TestIsOverdue:
    def test_none_returns_false(self):
        from shared.utils.date_utils import is_overdue

        assert is_overdue(None) is False

    def test_overdue(self):
        from shared.utils.date_utils import is_overdue

        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        assert is_overdue(past_date) is True

    def test_not_overdue(self):
        from shared.utils.date_utils import is_overdue

        future_date = (datetime.now() + timedelta(days=1)).isoformat()
        assert is_overdue(future_date) is False

    def test_invalid_date_returns_false(self):
        from shared.utils.date_utils import is_overdue

        assert not is_overdue("not-a-date")


class TestGetNextOccurrence:
    def test_future_day_in_same_week(self):
        from shared.utils.date_utils import get_next_occurrence

        today_weekday = datetime.now().weekday()
        target = (today_weekday + 3) % 7
        result = get_next_occurrence(target)
        assert result.weekday() == target
        assert result > datetime.now()

    def test_past_day_goes_to_next_week(self):
        from shared.utils.date_utils import get_next_occurrence

        today_weekday = datetime.now().weekday()
        target = (today_weekday - 1) % 7
        result = get_next_occurrence(target)
        assert result.weekday() == target
        assert result > datetime.now()

    def test_same_day_goes_to_next_week(self):
        from shared.utils.date_utils import get_next_occurrence

        today_weekday = datetime.now().weekday()
        result = get_next_occurrence(today_weekday)
        assert result.weekday() == today_weekday
        assert result > datetime.now()
        # Should be 7 days ahead
        diff_days = (result - datetime.now()).days
        assert 6 <= diff_days <= 8


# =============================================================================
# retention.py
# =============================================================================


class TestCleanupOldAuditLogs:
    @patch("shared.utils.retention.get_supabase_client")
    @patch("shared.utils.retention.logger")
    async def test_with_data(self, mock_logger, mock_get_supabase):
        from shared.utils.retention import cleanup_old_audit_logs

        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        mock_result = MagicMock()
        mock_result.data = [{"id": 1}, {"id": 2}]
        mock_supabase.from_.return_value.delete.return_value.lt.return_value.execute.return_value = mock_result

        count = await cleanup_old_audit_logs(90)
        assert count == 2
        mock_logger.info.assert_called_once()

    @patch("shared.utils.retention.get_supabase_client")
    @patch("shared.utils.retention.logger")
    async def test_without_data(self, mock_logger, mock_get_supabase):
        from shared.utils.retention import cleanup_old_audit_logs

        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        mock_result = MagicMock()
        mock_result.data = []
        mock_supabase.from_.return_value.delete.return_value.lt.return_value.execute.return_value = mock_result

        count = await cleanup_old_audit_logs(90)
        assert count == 0
        mock_logger.info.assert_not_called()

    @patch("shared.utils.retention.get_supabase_client")
    @patch("shared.utils.retention.logger")
    async def test_none_data(self, mock_logger, mock_get_supabase):
        from shared.utils.retention import cleanup_old_audit_logs

        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        mock_result = MagicMock()
        mock_result.data = None
        mock_supabase.from_.return_value.delete.return_value.lt.return_value.execute.return_value = mock_result

        count = await cleanup_old_audit_logs(90)
        assert count == 0


class TestCleanupOldChatMessages:
    @patch("shared.utils.retention.get_supabase_client")
    @patch("shared.utils.retention.logger")
    async def test_with_data(self, mock_logger, mock_get_supabase):
        from shared.utils.retention import cleanup_old_chat_messages

        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        mock_result = MagicMock()
        mock_result.data = [{"id": 1}]
        mock_supabase.from_.return_value.delete.return_value.lt.return_value.execute.return_value = mock_result

        count = await cleanup_old_chat_messages(60)
        assert count == 1
        mock_logger.info.assert_called_once()

    @patch("shared.utils.retention.get_supabase_client")
    @patch("shared.utils.retention.logger")
    async def test_without_data(self, mock_logger, mock_get_supabase):
        from shared.utils.retention import cleanup_old_chat_messages

        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        mock_result = MagicMock()
        mock_result.data = []
        mock_supabase.from_.return_value.delete.return_value.lt.return_value.execute.return_value = mock_result

        count = await cleanup_old_chat_messages(90)
        assert count == 0


class TestCleanupOldNotifications:
    @patch("shared.utils.retention.get_supabase_client")
    @patch("shared.utils.retention.logger")
    async def test_with_data(self, mock_logger, mock_get_supabase):
        from shared.utils.retention import cleanup_old_notifications

        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        mock_result = MagicMock()
        mock_result.data = [{"id": 1}, {"id": 2}, {"id": 3}]
        mock_supabase.from_.return_value.delete.return_value.lt.return_value.execute.return_value = mock_result

        count = await cleanup_old_notifications(30)
        assert count == 3
        mock_logger.info.assert_called_once()

    @patch("shared.utils.retention.get_supabase_client")
    @patch("shared.utils.retention.logger")
    async def test_without_data(self, mock_logger, mock_get_supabase):
        from shared.utils.retention import cleanup_old_notifications

        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        mock_result = MagicMock()
        mock_result.data = []
        mock_supabase.from_.return_value.delete.return_value.lt.return_value.execute.return_value = mock_result

        count = await cleanup_old_notifications(30)
        assert count == 0


class TestRunDataRetentionCleanup:
    @patch("shared.utils.retention.cleanup_old_audit_logs", new_callable=AsyncMock)
    @patch("shared.utils.retention.cleanup_old_chat_messages", new_callable=AsyncMock)
    @patch("shared.utils.retention.cleanup_old_notifications", new_callable=AsyncMock)
    async def test_aggregate(self, mock_notif, mock_chat, mock_audit):
        from shared.utils.retention import run_data_retention_cleanup

        mock_audit.return_value = 5
        mock_chat.return_value = 3
        mock_notif.return_value = 1

        result = await run_data_retention_cleanup(audit_days=60, chat_days=30, notification_days=15)
        assert result == {
            "audit_logs_removed": 5,
            "chat_messages_removed": 3,
            "notifications_removed": 1,
        }
        mock_audit.assert_called_once_with(60)
        mock_chat.assert_called_once_with(30)
        mock_notif.assert_called_once_with(15)


# =============================================================================
# logger.py
# =============================================================================


class TestLogger:
    def test_init_creates_logger(self):
        from shared.utils.logger import Logger

        log = Logger("test-logger")
        assert log.logger.name == "test-logger"
        assert log.service == "secondbrain-api"

    @patch.dict(os.environ, {"LOGGER_SERVICE_NAME": "custom-service"}, clear=False)
    def test_init_custom_service(self):
        from shared.utils.logger import Logger

        log = Logger()
        assert log.service == "custom-service"

    @patch("shared.utils.logger.logging.getLogger")
    def test_init_no_existing_handlers(self, mock_get_logger):
        from shared.utils.logger import Logger

        mock_logger = MagicMock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger

        Logger("test")
        mock_logger.addHandler.assert_called_once()

    @patch("shared.utils.logger.logging.getLogger")
    def test_init_with_existing_handlers(self, mock_get_logger):
        from shared.utils.logger import Logger

        existing_handler = MagicMock()
        mock_logger = MagicMock()
        mock_logger.handlers = [existing_handler]
        mock_get_logger.return_value = mock_logger

        Logger("test")
        mock_logger.addHandler.assert_not_called()

    @patch("shared.utils.logger.logging.getLogger")
    def test_log_formats_correctly(self, mock_get_logger):
        from shared.utils.logger import Logger

        mock_logger = MagicMock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger

        log = Logger("test")

        with patch("shared.utils.logger._logtail_handler") as mock_lt:
            mock_lt.client = None
            log._log("INFO", "hello", extra_field="value")

        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.INFO
        logged_entry = json.loads(call_args[0][1])
        assert logged_entry["level"] == "INFO"
        assert logged_entry["message"] == "hello"
        assert logged_entry["extra_field"] == "value"
        assert logged_entry["service"] == "secondbrain-api"
        assert "timestamp" in logged_entry

    def test_info(self):
        from shared.utils.logger import Logger

        log = Logger("test-info")
        with patch.object(log, "_log") as mock_log:
            log.info("info msg", count=1)
            mock_log.assert_called_once_with("INFO", "info msg", count=1)

    def test_warn(self):
        from shared.utils.logger import Logger

        log = Logger("test-warn")
        with patch.object(log, "_log") as mock_log:
            log.warn("warn msg")
            mock_log.assert_called_once_with("WARN", "warn msg")

    def test_error(self):
        from shared.utils.logger import Logger

        log = Logger("test-err")
        with patch.object(log, "_log") as mock_log:
            log.error("err msg")
            mock_log.assert_called_once_with("ERROR", "err msg", error_message=None)

    def test_error_with_exception(self):
        from shared.utils.logger import Logger

        log = Logger("test-err-exc")
        with patch.object(log, "_log") as mock_log:
            log.error("err msg", error=ValueError("bad"))
            mock_log.assert_called_once_with("ERROR", "err msg", error_message="bad")

    def test_debug(self):
        from shared.utils.logger import Logger

        log = Logger("test-debug")
        with patch.object(log, "_log") as mock_log:
            log.debug("debug msg")
            mock_log.assert_called_once_with("DEBUG", "debug msg")

    @patch("shared.utils.logger._logtail_handler")
    def test_log_calls_emit(self, mock_lt):
        from shared.utils.logger import Logger

        mock_client = MagicMock()
        mock_client.aclose = AsyncMock()
        mock_lt.client = mock_client
        mock_lt.emit = MagicMock(return_value=asyncio.Future())
        log = Logger("test-lt-emit")
        with patch.object(log, "logger") as mock_std_logger:
            log.info("test")
        assert mock_lt.client is not None


class TestLogtailHandler:
    def test_init_without_token(self):
        with patch.dict(os.environ, {}, clear=True):
            from shared.utils.logger import LogtailHandler

            handler = LogtailHandler()
            assert handler.token is None
            assert handler.client is None
            assert handler.batch == []

    def test_init_with_token_and_httpx_available(self):
        from shared.utils.logger import LogtailHandler

        with patch.dict(os.environ, {"LOGTAIL_SOURCE_TOKEN": "test-token"}, clear=False):
            with patch("httpx.AsyncClient") as mock_client_cls:
                handler = LogtailHandler()
                assert handler.token == "test-token"
                assert handler.client is not None
                mock_client_cls.assert_called_once_with(
                    base_url="https://in.logtail.com",
                    timeout=5,
                    headers={"Authorization": "Bearer test-token"},
                )

    def test_setup_catches_importerror(self):
        from shared.utils.logger import LogtailHandler
        import builtins
        import sys

        handler = LogtailHandler.__new__(LogtailHandler)
        handler.token = "test-token"
        handler.client = None
        handler.batch = []
        handler.batch_lock = asyncio.Lock()
        handler._flush_task = None

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "httpx":
                raise ImportError("no httpx")
            return original_import(name, *args, **kwargs)

        saved = sys.modules.pop("httpx", None)
        try:
            with patch("builtins.__import__", side_effect=mock_import):
                handler._setup()
                assert handler.client is None
        finally:
            if saved:
                sys.modules["httpx"] = saved

    def test_start_background_flush_with_client(self):
        from shared.utils.logger import LogtailHandler

        handler = LogtailHandler.__new__(LogtailHandler)
        handler.token = "test"
        handler.client = MagicMock()
        handler.batch = []
        handler.batch_lock = asyncio.Lock()
        handler._flush_task = None

        with patch("asyncio.create_task") as mock_ct:
            handler.start_background_flush()
            assert handler._flush_task is not None
            mock_ct.assert_called_once()

    def test_start_background_flush_no_client(self):
        from shared.utils.logger import LogtailHandler

        handler = LogtailHandler.__new__(LogtailHandler)
        handler.token = None
        handler.client = None
        handler.batch = []
        handler.batch_lock = asyncio.Lock()
        handler._flush_task = None

        handler.start_background_flush()
        assert handler._flush_task is None

    def test_start_background_flush_already_running(self):
        from shared.utils.logger import LogtailHandler

        handler = LogtailHandler.__new__(LogtailHandler)
        handler.token = "test"
        handler.client = MagicMock()
        handler.batch = []
        handler.batch_lock = asyncio.Lock()
        existing_task = MagicMock()
        handler._flush_task = existing_task

        with patch("asyncio.create_task") as mock_ct:
            handler.start_background_flush()
            mock_ct.assert_not_called()
        assert handler._flush_task is existing_task

    async def test_stop_background_flush(self):
        from shared.utils.logger import LogtailHandler

        handler = LogtailHandler.__new__(LogtailHandler)
        handler.token = "test"
        client_mock = MagicMock()
        client_mock.aclose = AsyncMock()
        handler.client = client_mock
        handler.batch = []
        handler.batch_lock = asyncio.Lock()
        flush_task = MagicMock()
        flush_task.cancel = MagicMock()
        handler._flush_task = flush_task

        await handler.stop_background_flush()
        flush_task.cancel.assert_called_once()
        assert handler._flush_task is None
        client_mock.aclose.assert_called_once()
        assert handler.client is None

    async def test_stop_background_flush_no_task(self):
        from shared.utils.logger import LogtailHandler

        handler = LogtailHandler.__new__(LogtailHandler)
        handler.token = "test"
        client_mock = MagicMock()
        client_mock.aclose = AsyncMock()
        handler.client = client_mock
        handler.batch = []
        handler.batch_lock = asyncio.Lock()
        handler._flush_task = None

        await handler.stop_background_flush()
        client_mock.aclose.assert_called_once()
        assert handler.client is None

    async def test_emit_without_client(self):
        from shared.utils.logger import LogtailHandler

        handler = LogtailHandler.__new__(LogtailHandler)
        handler.token = None
        handler.client = None
        handler.batch = []
        handler.batch_lock = asyncio.Lock()

        await handler.emit({"level": "INFO"})
        assert handler.batch == []

    async def test_emit_adds_to_batch(self):
        from shared.utils.logger import LogtailHandler

        handler = LogtailHandler.__new__(LogtailHandler)
        handler.token = "test"
        handler.client = MagicMock()
        handler.batch = []
        handler.batch_lock = asyncio.Lock()

        await handler.emit({"level": "INFO"})
        assert len(handler.batch) == 1

    async def test_emit_triggers_flush_at_10(self):
        from shared.utils.logger import LogtailHandler

        handler = LogtailHandler.__new__(LogtailHandler)
        handler.token = "test"
        handler.client = MagicMock()
        handler.batch = list(range(9))
        handler.batch_lock = asyncio.Lock()

        with patch("asyncio.create_task") as mock_ct:
            await handler.emit({"level": "INFO"})
            assert mock_ct.called

    async def test_flush_with_batch(self):
        from shared.utils.logger import LogtailHandler

        handler = LogtailHandler.__new__(LogtailHandler)
        handler.token = "test"
        handler.client = MagicMock()
        handler.batch = [{"level": "INFO"}]
        handler.batch_lock = asyncio.Lock()

        await handler._flush()
        assert handler.batch == []
        handler.client.post.assert_called_once_with("/", json=[{"level": "INFO"}])

    async def test_flush_empty_batch(self):
        from shared.utils.logger import LogtailHandler

        handler = LogtailHandler.__new__(LogtailHandler)
        handler.token = "test"
        handler.client = MagicMock()
        handler.batch = []
        handler.batch_lock = asyncio.Lock()

        await handler._flush()
        handler.client.post.assert_not_called()

    async def test_flush_exception_silent(self):
        from shared.utils.logger import LogtailHandler

        handler = LogtailHandler.__new__(LogtailHandler)
        handler.token = "test"
        handler.client = MagicMock()
        handler.batch = [{"level": "INFO"}]
        handler.batch_lock = asyncio.Lock()
        handler.client.post.side_effect = Exception("network error")

        await handler._flush()

    async def test_flush_loop(self):
        from shared.utils.logger import LogtailHandler

        handler = LogtailHandler.__new__(LogtailHandler)
        handler.token = "test"
        handler.client = MagicMock()
        handler.batch = []
        handler.batch_lock = asyncio.Lock()

        with patch("asyncio.sleep", side_effect=[None, asyncio.CancelledError()]):
            with pytest.raises(asyncio.CancelledError):
                await handler._flush_loop()


class TestLogFunctions:
    @patch("shared.utils.logger.logger")
    def test_log_request(self, mock_logger):
        from shared.utils.logger import log_request

        log_request("/api/v1/tasks", "GET", user_id="user1", extra="val")
        mock_logger.info.assert_called_once_with(
            "API Request", endpoint="/api/v1/tasks", method="GET", user_id="user1", extra="val"
        )

    @patch("shared.utils.logger.logger")
    def test_log_request_no_user(self, mock_logger):
        from shared.utils.logger import log_request

        log_request("/api/v1/tasks", "GET", extra="val")
        mock_logger.info.assert_called_once_with(
            "API Request", endpoint="/api/v1/tasks", method="GET", user_id=None, extra="val"
        )

    @patch("shared.utils.logger.logger")
    def test_log_response(self, mock_logger):
        from shared.utils.logger import log_response

        log_response("/api/v1/tasks", "GET", 200, 42.123, extra="val")
        mock_logger.info.assert_called_once_with(
            "API Response",
            endpoint="/api/v1/tasks",
            method="GET",
            status_code=200,
            duration_ms=42.12,
            extra="val",
        )

    @patch("shared.utils.logger.logger")
    def test_log_error(self, mock_logger):
        from shared.utils.logger import log_error

        log_error("/api/v1/tasks", "GET", ValueError("bad input"), extra="val")
        mock_logger.error.assert_called_once_with(
            "API Error",
            endpoint="/api/v1/tasks",
            method="GET",
            error_type="ValueError",
            error_message="bad input",
            extra="val",
        )


# =============================================================================
# feature_flags.py
# =============================================================================


class TestFeatureFlag:
    def test_init_defaults(self):
        from shared.utils.feature_flags import FeatureFlag

        f = FeatureFlag("test.flag")
        assert f.key == "test.flag"
        assert f.enabled is False
        assert f.rollout_percentage == 0
        assert f.user_segments == []
        assert f.metadata == {}

    def test_init_clamps_percentage(self):
        from shared.utils.feature_flags import FeatureFlag

        f1 = FeatureFlag("f1", rollout_percentage=150)
        assert f1.rollout_percentage == 100

        f2 = FeatureFlag("f2", rollout_percentage=-10)
        assert f2.rollout_percentage == 0

    def test_init_with_values(self):
        from shared.utils.feature_flags import FeatureFlag

        f = FeatureFlag("f", enabled=True, rollout_percentage=50, user_segments=["u1"], metadata={"a": 1})
        assert f.enabled is True
        assert f.rollout_percentage == 50
        assert f.user_segments == ["u1"]
        assert f.metadata == {"a": 1}

    def test_to_dict(self):
        from shared.utils.feature_flags import FeatureFlag

        f = FeatureFlag("my.flag", enabled=True, rollout_percentage=75, user_segments=["u1"], metadata={"v": 2})
        d = f.to_dict()
        assert d["key"] == "my.flag"
        assert d["enabled"] is True
        assert d["rollout_percentage"] == 75
        assert d["user_segments"] == ["u1"]
        assert d["metadata"] == {"v": 2}
        assert "updated_at" in d

    def test_from_dict(self):
        from shared.utils.feature_flags import FeatureFlag

        data = {
            "key": "test.key",
            "enabled": True,
            "rollout_percentage": 50,
            "user_segments": ["u1", "u2"],
            "metadata": {"x": 1},
        }
        f = FeatureFlag.from_dict(data)
        assert f.key == "test.key"
        assert f.enabled is True
        assert f.rollout_percentage == 50
        assert f.user_segments == ["u1", "u2"]
        assert f.metadata == {"x": 1}

    def test_from_dict_partial(self):
        from shared.utils.feature_flags import FeatureFlag

        f = FeatureFlag.from_dict({"key": "k"})
        assert f.key == "k"
        assert f.enabled is False

    def test_updated_at_set_on_init(self):
        from shared.utils.feature_flags import FeatureFlag

        f = FeatureFlag("test")
        assert f.updated_at is not None


class TestFeatureFlagStoreLoadFromEnv:
    @patch.dict(os.environ, {"FF_NEW_FEATURE": "true", "FF_ANOTHER_FLAG": "false", "NORMAL_VAR": "x"}, clear=True)
    def test_loads_env_flags(self):
        from shared.utils.feature_flags import FeatureFlagStore

        store = FeatureFlagStore()
        assert "new.feature" in store._flags
        assert store._flags["new.feature"].enabled is True
        assert store._flags["new.feature"].rollout_percentage == 100

        assert "another.flag" in store._flags
        assert store._flags["another.flag"].enabled is False
        assert store._flags["another.flag"].rollout_percentage == 0

    @patch.dict(os.environ, {"FF_MY_FLAG": "1", "FF_OTHER": "yes"}, clear=True)
    def test_loads_with_non_normal_values(self):
        from shared.utils.feature_flags import FeatureFlagStore

        store = FeatureFlagStore()
        assert store._flags["my.flag"].enabled is True
        assert store._flags["other"].enabled is True


class TestFeatureFlagStoreGet:
    def test_flag_not_found_returns_default(self):
        from shared.utils.feature_flags import FeatureFlagStore

        store = FeatureFlagStore()
        store._flags = {}
        assert store.get("nonexistent") is False
        assert store.get("nonexistent", default=True) is True

    def test_flag_disabled_returns_false(self):
        from shared.utils.feature_flags import FeatureFlag, FeatureFlagStore

        store = FeatureFlagStore()
        store._flags = {"test": FeatureFlag("test", enabled=False)}
        assert store.get("test") is False

    def test_flag_100_percent_returns_true(self):
        from shared.utils.feature_flags import FeatureFlag, FeatureFlagStore

        store = FeatureFlagStore()
        store._flags = {"test": FeatureFlag("test", enabled=True, rollout_percentage=100)}
        assert store.get("test") is True

    def test_user_in_segment_returns_true(self):
        from shared.utils.feature_flags import FeatureFlag, FeatureFlagStore

        store = FeatureFlagStore()
        store._flags = {
            "test": FeatureFlag("test", enabled=True, rollout_percentage=0, user_segments=["user1"])
        }
        assert store.get("test", user_id="user1") is True
        assert store.get("test", user_id="user2") is False

    def test_user_bucket_under_threshold(self):
        from shared.utils.feature_flags import FeatureFlag, FeatureFlagStore

        store = FeatureFlagStore()

        with patch.object(store, "_user_bucket", return_value=5):
            flag = FeatureFlag("test", enabled=True, rollout_percentage=50)
            store._flags = {"test": flag}
            assert store.get("test", user_id="user-abc") is True

    def test_user_bucket_over_threshold(self):
        from shared.utils.feature_flags import FeatureFlag, FeatureFlagStore

        store = FeatureFlagStore()

        with patch.object(store, "_user_bucket", return_value=75):
            flag = FeatureFlag("test", enabled=True, rollout_percentage=50)
            store._flags = {"test": flag}
            assert store.get("test", user_id="user-abc") is False

    def test_no_user_id_and_nonzero_rollout(self):
        from shared.utils.feature_flags import FeatureFlag, FeatureFlagStore

        store = FeatureFlagStore()
        flag = FeatureFlag("test", enabled=True, rollout_percentage=50)
        store._flags = {"test": flag}
        assert store.get("test") is True


class TestFeatureFlagStoreGetVariant:
    def test_flag_none_or_disabled(self):
        from shared.utils.feature_flags import FeatureFlagStore

        store = FeatureFlagStore()
        store._flags = {}
        assert store.get_variant("nonexistent", "user1") == "control"

        from shared.utils.feature_flags import FeatureFlag

        store._flags = {"test": FeatureFlag("test", enabled=False)}
        assert store.get_variant("test", "user1") == "control"

    def test_100_percent_rollout(self):
        from shared.utils.feature_flags import FeatureFlag, FeatureFlagStore

        store = FeatureFlagStore()
        store._flags = {"test": FeatureFlag("test", enabled=True, rollout_percentage=100)}
        assert store.get_variant("test", "user1") == "treatment"

    def test_user_in_segment(self):
        from shared.utils.feature_flags import FeatureFlag, FeatureFlagStore

        store = FeatureFlagStore()
        store._flags = {
            "test": FeatureFlag("test", enabled=True, rollout_percentage=0, user_segments=["user1"])
        }
        assert store.get_variant("test", "user1") == "treatment"

    def test_bucket_under_threshold(self):
        from shared.utils.feature_flags import FeatureFlag, FeatureFlagStore

        store = FeatureFlagStore()
        store._flags = {"test": FeatureFlag("test", enabled=True, rollout_percentage=50)}
        with patch.object(store, "_user_bucket", return_value=20):
            assert store.get_variant("test", "user1") == "treatment"

    def test_bucket_over_threshold(self):
        from shared.utils.feature_flags import FeatureFlag, FeatureFlagStore

        store = FeatureFlagStore()
        store._flags = {"test": FeatureFlag("test", enabled=True, rollout_percentage=50)}
        with patch.object(store, "_user_bucket", return_value=80):
            assert store.get_variant("test", "user1") == "control"


class TestFeatureFlagStoreCRUD:
    def test_set_and_get_flag(self):
        from shared.utils.feature_flags import FeatureFlag, FeatureFlagStore

        store = FeatureFlagStore()
        flag = FeatureFlag("my.flag", enabled=True)
        store.set("my.flag", flag)

        retrieved = store.get_flag("my.flag")
        assert retrieved is not None
        assert retrieved.key == "my.flag"
        assert retrieved.enabled is True

    def test_get_flag_not_found(self):
        from shared.utils.feature_flags import FeatureFlagStore

        store = FeatureFlagStore()
        store._flags = {}
        assert store.get_flag("nope") is None

    def test_delete_existing(self):
        from shared.utils.feature_flags import FeatureFlag, FeatureFlagStore

        store = FeatureFlagStore()
        store._flags = {"test": FeatureFlag("test")}
        assert store.delete("test") is True
        assert "test" not in store._flags

    def test_delete_non_existing(self):
        from shared.utils.feature_flags import FeatureFlagStore

        store = FeatureFlagStore()
        store._flags = {}
        assert store.delete("nope") is False

    def test_all_flags(self):
        from shared.utils.feature_flags import FeatureFlag, FeatureFlagStore

        store = FeatureFlagStore()
        store._flags = {"a": FeatureFlag("a"), "b": FeatureFlag("b")}
        all_f = store.all_flags()
        assert set(all_f.keys()) == {"a", "b"}
        all_f["c"] = FeatureFlag("c")
        assert "c" not in store._flags


class TestFeatureFlagStoreRefresh:
    @patch("shared.utils.feature_flags.get_supabase_client")
    @patch("shared.utils.feature_flags.logger")
    async def test_skip_if_not_due(self, mock_logger, mock_get_supabase):
        from shared.utils.feature_flags import FeatureFlagStore

        store = FeatureFlagStore()
        store._last_refresh = datetime.utcnow().timestamp() + 3600
        await store.refresh()
        mock_get_supabase.assert_not_called()

    @patch("shared.utils.feature_flags.get_supabase_client")
    @patch("shared.utils.feature_flags.logger")
    async def test_successful_refresh(self, mock_logger, mock_get_supabase):
        from shared.utils.feature_flags import FeatureFlagStore

        store = FeatureFlagStore()
        store._last_refresh = 0
        store._refresh_interval = 0

        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        mock_result = MagicMock()
        mock_result.data = [
            {"key": "flag.a", "enabled": True, "rollout_percentage": 100, "user_segments": None, "metadata": {}},
            {"key": "flag.b", "enabled": False, "rollout_percentage": 0, "user_segments": ["admin"], "metadata": {"x": 1}},
        ]
        mock_supabase.from_.return_value.select.return_value.execute.return_value = mock_result

        await store.refresh()

        assert "flag.a" in store._flags
        assert store._flags["flag.a"].enabled is True
        assert "flag.b" in store._flags
        assert store._flags["flag.b"].user_segments == ["admin"]
        assert store._flags["flag.b"].metadata == {"x": 1}
        mock_logger.info.assert_called_once()

    @patch("shared.utils.feature_flags.get_supabase_client")
    @patch("shared.utils.feature_flags.logger")
    async def test_empty_data(self, mock_logger, mock_get_supabase):
        from shared.utils.feature_flags import FeatureFlagStore

        store = FeatureFlagStore()
        store._last_refresh = 0
        store._refresh_interval = 0

        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase
        mock_result = MagicMock()
        mock_result.data = []
        mock_supabase.from_.return_value.select.return_value.execute.return_value = mock_result

        await store.refresh()
        mock_logger.info.assert_not_called()

    @patch("shared.utils.feature_flags.get_supabase_client")
    @patch("shared.utils.feature_flags.logger")
    async def test_exception_handling(self, mock_logger, mock_get_supabase):
        from shared.utils.feature_flags import FeatureFlagStore

        store = FeatureFlagStore()
        store._last_refresh = 0
        store._refresh_interval = 0

        mock_get_supabase.side_effect = Exception("db down")

        await store.refresh()
        mock_logger.warn.assert_called_once()


class TestFeatureFlagStoreUserBucket:
    def test_deterministic(self):
        from shared.utils.feature_flags import FeatureFlagStore

        store = FeatureFlagStore()
        r1 = store._user_bucket("user1", "flag.a")
        r2 = store._user_bucket("user1", "flag.a")
        assert r1 == r2

    def test_different_users_different_keys(self):
        from shared.utils.feature_flags import FeatureFlagStore

        store = FeatureFlagStore()
        r1 = store._user_bucket("user1", "flag.a")
        r2 = store._user_bucket("user1", "flag.b")
        assert 0 <= r1 < 100
        assert 0 <= r2 < 100
        assert r1 != r2  # Very high probability


class TestFeatureFlagStoreThreadSafety:
    def test_set_under_lock(self):
        from shared.utils.feature_flags import FeatureFlag, FeatureFlagStore

        store = FeatureFlagStore()
        flag = FeatureFlag("test", enabled=True, rollout_percentage=100)
        store.set("test", flag)
        assert store.get("test") is True

    def test_delete_under_lock(self):
        from shared.utils.feature_flags import FeatureFlag, FeatureFlagStore

        store = FeatureFlagStore()
        store._flags = {"test": FeatureFlag("test", enabled=True, rollout_percentage=100)}
        assert store.delete("test") is True
        assert store.get("test") is False
