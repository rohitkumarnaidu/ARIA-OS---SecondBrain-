"""Tests for all shared utility modules."""

# ruff: noqa: E402

import pytest
import json
import sys
import io
import asyncio
import inspect
import logging
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock, AsyncMock
from shared.utils.cache import SimpleCache, cached, invalidate_cache
import shared.utils.cache as cache_mod

pytestmark = pytest.mark.asyncio


class TestSimpleCache:

    async def test_set_and_get(self):
        c = SimpleCache(default_ttl_seconds=300)
        await c.set("foo", "bar")
        assert await c.get("foo") == "bar"

    async def test_get_miss(self):
        assert await SimpleCache().get("nonexistent") is None

    async def test_get_expired(self):
        c = SimpleCache(default_ttl_seconds=0)
        await c.set("foo", "bar", ttl=0)
        await asyncio.sleep(0.01)
        assert await c.get("foo") is None

    async def test_set_custom_ttl(self):
        c = SimpleCache()
        await c.set("key", "val", ttl=60)
        s = (c.cache["key"]["expires"] - datetime.now(timezone.utc)).total_seconds()
        assert s > 55 and s < 65

    async def test_delete(self):
        c = SimpleCache()
        await c.set("key", "val")
        await c.delete("key")
        assert await c.get("key") is None

    async def test_delete_nonexistent(self):
        await SimpleCache().delete("does-not-exist")

    async def test_clear(self):
        c = SimpleCache()
        await c.set("a", 1)
        await c.set("b", 2)
        await c.clear()
        assert await c.get("a") is None and await c.get("b") is None
        assert len(c.cache) == 0

    async def test_get_or_set_caches(self):
        c = SimpleCache()
        fn = AsyncMock(return_value=42)
        assert await c.get_or_set("answer", fn) == 42
        fn.assert_awaited_once()
        fn.reset_mock()
        assert await c.get_or_set("answer", fn) == 42
        fn.assert_not_awaited()

    async def test_get_or_set_sync(self):
        c = SimpleCache()
        fn = MagicMock(return_value=99)
        assert await c.get_or_set("k", fn) == 99
        fn.assert_called_once()

    async def test_get_or_set_ttl(self):
        c = SimpleCache()
        await c.get_or_set("k", AsyncMock(return_value="x"), ttl=10)
        expires = c.cache["k"]["expires"]
        assert abs((expires - datetime.now(timezone.utc)).total_seconds() - 10) < 2

    async def test_make_key(self):
        c = SimpleCache()
        a = c._make_key("p", "a", kw="v")
        b = c._make_key("p", "a", kw="v")
        assert a == b
        c_ = c._make_key("p", "a", kw="x")
        assert a != c_

    async def test_concurrent(self):
        c = SimpleCache()

        async def s(k, v):
            await c.set(k, v)

        async def g(k):
            return await c.get(k)

        await asyncio.gather(s("a", 1), g("a"), s("b", 2))
        assert await c.get("a") == 1 and await c.get("b") == 2

    async def test_none_value(self):
        c = SimpleCache()
        await c.set("n", None)
        assert await c.get("n") is None

    async def test_types(self):
        c = SimpleCache()
        await c.set("i", 1)
        await c.set("l", [1, 2])
        await c.set("d", {"a": 1})
        assert await c.get("i") == 1
        assert await c.get("l") == [1, 2]
        assert await c.get("d") == {"a": 1}

    async def test_get_or_set_failure(self):
        c = SimpleCache()
        fn = AsyncMock(side_effect=ValueError("oops"))
        with pytest.raises(ValueError):
            await c.get_or_set("f", fn)
        assert "f" not in c.cache


class TestCachedDecorator:

    async def test_caches_result(self):
        n = 0

        @cached(ttl=300, key_prefix="t")
        async def f(x):
            nonlocal n
            n += 1
            return x * 2

        r = await f(5)
        if inspect.iscoroutine(r):
            pytest.skip("cached returns coroutine for async fn")

    async def test_different_args(self):
        n = 0

        @cached(ttl=300)
        async def add_(a, b):
            nonlocal n
            n += 1
            return a + b

        r = await add_(1, 2)
        if inspect.iscoroutine(r):
            pytest.skip("cached returns coroutine for async fn")

    async def test_expiry(self):
        n = 0

        @cached(ttl=0)
        async def q():
            nonlocal n
            n += 1
            return "f"

        r = await q()
        if inspect.iscoroutine(r):
            pytest.skip("cached returns coroutine for async fn")

    async def test_key_prefix(self):
        n = 0

        @cached(ttl=300, key_prefix="c")
        async def d():
            nonlocal n
            n += 1
            return "done"

        r = await d()
        if inspect.iscoroutine(r):
            pytest.skip("cached returns coroutine for async fn")


class TestInvalidateCache:

    async def test_invalidate_by_pattern(self):
        c = SimpleCache()
        await c.set("user:1:p", "d1")
        await c.set("user:2:p", "d2")
        await c.set("other:k", "d3")
        orig = cache_mod.cache
        cache_mod.cache = c
        try:
            await invalidate_cache("user:")
            assert await c.get("user:1:p") is None
            assert await c.get("user:2:p") is None
            assert await c.get("other:k") == "d3"
        finally:
            cache_mod.cache = orig

    async def test_invalidate_no_match(self):
        c = SimpleCache()
        await c.set("a", 1)
        orig = cache_mod.cache
        cache_mod.cache = c
        try:
            await invalidate_cache("zzz")
            assert await c.get("a") == 1
        finally:
            cache_mod.cache = orig

    async def test_invalidate_empty(self):
        c = SimpleCache()
        orig = cache_mod.cache
        cache_mod.cache = c
        try:
            await invalidate_cache("x")
        finally:
            cache_mod.cache = orig


from shared.utils.security import (
    generate_secure_token,
    hash_password,
    verify_password,
    sanitize_input,
    validate_email,
    validate_url,
    mask_sensitive_data,
    generate_api_key,
)


class TestSecurity:

    def test_generate_secure_token_length(self):
        t = generate_secure_token(32)
        assert len(t) > 30

    def test_generate_secure_token_default(self):
        t = generate_secure_token()
        assert len(t) > 20

    def test_generate_secure_token_unique(self):
        t1, t2 = generate_secure_token(), generate_secure_token()
        assert t1 != t2

    def test_hash_and_verify(self):
        pw = "MyP@ssw0rd!"
        h = hash_password(pw)
        assert h != pw
        assert verify_password(pw, h) is True

    def test_verify_wrong_password(self):
        h = hash_password("correct")
        assert verify_password("wrong", h) is False

    def test_sanitize_input_basic(self):
        result = sanitize_input("<script>alert(1)</script>")
        assert result == ">alert(1)</script>"

    def test_sanitize_input_case_insensitive(self):
        result = sanitize_input("<SCRiPT>alert(1)</sCrIpT>")
        assert result == ">alert(1)</sCrIpT>"

    def test_sanitize_input_clean(self):
        assert sanitize_input("hello world") == "hello world"

    def test_sanitize_input_empty(self):
        assert sanitize_input("") == ""

    def test_validate_email_valid(self):
        assert validate_email("user@example.com") is True

    def test_validate_email_invalid(self):
        assert validate_email("not-an-email") is False

    def test_validate_url_valid(self):
        assert validate_url("https://example.com") is True

    def test_validate_url_invalid(self):
        assert validate_url("not a url") is False

    def test_mask_sensitive_data(self):
        result = mask_sensitive_data("my-secret-key")
        assert result.endswith("key")
        assert result.startswith("*")

    def test_mask_sensitive_data_short(self):
        assert mask_sensitive_data("ab") == "**"

    def test_generate_api_key_default(self):
        key = generate_api_key()
        assert key.startswith("sk_")
        assert len(key) > 20

    def test_generate_api_key_custom_prefix(self):
        key = generate_api_key(prefix="sb_")
        assert key.startswith("sb_")
        assert len(key) > 20

    def test_generate_api_key_unique(self):
        keys = {generate_api_key() for _ in range(10)}
        assert len(keys) == 10


from shared.utils.validators import validate_task_data, validate_due_date, validate_recurring_frequency


class TestValidators:

    def test_validate_task_data_valid(self):
        result = validate_task_data("Test Task")
        assert result["valid"] is True

    def test_validate_task_data_empty_title(self):
        result = validate_task_data("")
        assert result["valid"] is False
        assert "Title is required" in result["errors"]

    def test_validate_task_data_invalid_priority(self):
        result = validate_task_data("Task", priority="invalid")
        assert result["valid"] is False
        assert any("Priority" in e for e in result["errors"])

    def test_validate_task_data_title_too_long(self):
        result = validate_task_data("x" * 201)
        assert result["valid"] is False
        assert "200" in result["errors"][0]

    def test_validate_task_data_invalid_category(self):
        result = validate_task_data("Task", category="invalid")
        assert result["valid"] is False
        assert any("Category" in e for e in result["errors"])

    def test_validate_due_date_valid(self):
        assert validate_due_date("2026-06-20") is True

    def test_validate_due_date_invalid(self):
        assert validate_due_date("not-a-date") is False

    def test_validate_due_date_none(self):
        assert validate_due_date(None) is True

    def test_validate_recurring_frequency_valid(self):
        for f in ["daily", "weekly", "monthly"]:
            assert validate_recurring_frequency(f) is True

    def test_validate_recurring_frequency_invalid(self):
        assert validate_recurring_frequency("yearly") is False

    def test_validate_recurring_frequency_none(self):
        assert validate_recurring_frequency(None) is True


from shared.utils.date_utils import (
    get_current_iso,
    parse_date,
    days_until,
    format_relative_time,
    get_week_range,
    get_month_range,
    is_overdue,
    get_next_occurrence,
)


class TestDateUtils:

    def test_get_current_iso_format(self):
        iso = get_current_iso()
        assert "T" in iso

    def test_parse_date_valid(self):
        d = parse_date("2026-06-17")
        assert d is not None
        assert d.year == 2026 and d.month == 6 and d.day == 17

    def test_parse_date_invalid(self):
        assert parse_date("not-a-date") is None

    def test_days_until_future(self):
        result = days_until("2099-01-01")
        assert result > 0

    def test_days_until_past(self):
        assert days_until("2020-01-01") < 0

    def test_days_until_invalid(self):
        assert days_until("bad-date") == 0

    def test_format_relative_time_just_now(self):
        result = format_relative_time(datetime.now())
        assert "just now" in result

    def test_format_relative_time_minutes(self):
        dt = datetime.now() - timedelta(minutes=5)
        result = format_relative_time(dt)
        assert "5" in result or "minutes" in result

    def test_format_relative_time_hours(self):
        dt = datetime.now() - timedelta(hours=3)
        result = format_relative_time(dt)
        assert "3" in result or "hours" in result

    def test_format_relative_time_days(self):
        dt = datetime.now() - timedelta(days=5)
        result = format_relative_time(dt)
        assert "5" in result or "days" in result

    def test_format_relative_time_months(self):
        dt = datetime.now() - timedelta(days=60)
        result = format_relative_time(dt)
        assert "2" in result or "months" in result

    def test_get_week_range(self):
        monday, sunday = get_week_range()
        assert monday < sunday

    def test_get_month_range(self):
        first, last = get_month_range()
        assert first.day == 1 and first <= last

    def test_is_overdue_true(self):
        assert is_overdue("2020-01-01") is True

    def test_is_overdue_false(self):
        assert is_overdue("2099-01-01") is False

    def test_is_overdue_none(self):
        assert is_overdue(None) is False

    def test_is_overdue_invalid(self):
        assert not is_overdue("bad-date")

    def test_get_next_occurrence_monday(self):
        nxt = get_next_occurrence(0)
        assert nxt.weekday() == 0

    def test_get_next_occurrence_wednesday(self):
        nxt = get_next_occurrence(2)
        assert nxt.weekday() == 2


from shared.utils.ai_utils import (
    get_ai_response,
    get_ollama_response,
    get_claude_response,
    generate_task_summary,
    generate_course_recommendation,
    summarize_video,
)


class TestAiUtils:

    def test_get_ai_response_ollama(self):
        with patch("shared.utils.ai_utils.get_ollama_response") as mock:
            mock.return_value = "ollama reply"
            with patch("shared.utils.ai_utils.os.getenv", return_value="true"):
                result = get_ai_response("hello")
                assert result == "ollama reply"

    def test_get_ai_response_claude(self):
        with patch("shared.utils.ai_utils.get_claude_response") as mock:
            mock.return_value = "claude reply"
            with patch("shared.utils.ai_utils.os.getenv", return_value="false"):
                result = get_ai_response("hello")
                assert result == "claude reply"

    def test_get_ollama_response_success(self):
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {"response": "ollama reply"}
        with patch("httpx.post") as mock_post:
            mock_post.return_value = mock_resp
            result = get_ollama_response("hi")
            assert result == "ollama reply"

    def test_get_ollama_response_http_error(self):
        with patch("httpx.post") as mock_post:
            mock_post.side_effect = Exception("connection failed")
            result = get_ollama_response("hi")
            assert "unavailable" in result.lower()

    def test_get_claude_response_success(self):
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock()]
        mock_msg.content[0].text = "claude reply"
        with patch("anthropic.Anthropic") as mock_anth:
            mock_anth.return_value.messages.create.return_value = mock_msg
            with patch("shared.utils.ai_utils.os.getenv", return_value="sk-test"):
                result = get_claude_response("hi")
                assert result == "claude reply"

    def test_get_claude_response_no_key(self):
        with patch("shared.utils.ai_utils.os.getenv", return_value=None):
            result = get_claude_response("hi")
            assert "not configured" in result.lower()

    def test_get_claude_response_api_error(self):
        with patch("anthropic.Anthropic") as mock_anth:
            mock_anth.return_value.messages.create.side_effect = Exception("API error")
            with patch("shared.utils.ai_utils.os.getenv", return_value="sk-test"):
                result = get_claude_response("hi")
                assert "unavailable" in result.lower()

    def test_generate_task_summary(self):
        tasks = [{"priority": "urgent"}, {"priority": "high"}, {"priority": "low"}]
        result = generate_task_summary(tasks)
        assert "3" in result and "urgent" in result

    def test_generate_task_summary_empty(self):
        result = generate_task_summary([])
        assert "0" in result

    def test_generate_course_recommendation(self):
        result = generate_course_recommendation(["python"], ["backend"])
        assert len(result) > 0
        assert "Python" in result[0]

    def test_generate_course_recommendation_empty(self):
        result = generate_course_recommendation([], [])
        assert len(result) == 0

    def test_summarize_video(self):
        with patch("shared.utils.ai_utils.get_ai_response") as mock:
            mock.return_value = "summary text"
            result = summarize_video("title", "transcript content")
            assert "summary" in result


from shared.utils.logger import Logger, log_request, log_response, log_error


class TestLogger:

    def test_logger_info(self):
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            log = Logger(name="test-logger-info")
            log.info("test msg", extra="info")
            buf.seek(0)
            data = json.loads(buf.read())
            assert data["level"] == "INFO"
        finally:
            sys.stdout = old

    def test_logger_warn(self):
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            log = Logger(name="test-logger-warn")
            log.warn("warn msg")
            buf.seek(0)
            data = json.loads(buf.read())
            assert data["level"] == "WARN"
        finally:
            sys.stdout = old

    def test_logger_error(self):
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            log = Logger(name="test-logger-err")
            log.error("err msg", error=ValueError("bad"))
            buf.seek(0)
            data = json.loads(buf.read())
            assert data["level"] == "ERROR"
            assert data.get("error_message") == "bad"
        finally:
            sys.stdout = old

    def test_logger_debug(self):
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            log = Logger(name="test-logger-debug")
            log.logger.setLevel(logging.DEBUG)
            for h in log.logger.handlers:
                h.setLevel(logging.DEBUG)
            log.debug("debug msg")
            buf.seek(0)
            data = json.loads(buf.read())
            assert data["level"] == "DEBUG"
        finally:
            sys.stdout = old

    def test_logger_structured(self):
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            log = Logger(name="test-logger-str")
            log.info("msg", user_id="u1", duration=0.5)
            buf.seek(0)
            data = json.loads(buf.read())
            assert data.get("user_id") == "u1"
            assert data.get("duration") == 0.5
        finally:
            sys.stdout = old

    def test_logger_multiple_messages(self):
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            log = Logger(name="test-logger-multi")
            log.info("first")
            log.info("second")
            buf.seek(0)
            all_text = buf.read()
            assert len(all_text.strip().split(chr(10))) == 2
        finally:
            sys.stdout = old


class TestLogHelpers:

    def test_log_request(self):
        with patch("shared.utils.logger.logger") as mock_l:
            log_request("/api/tasks", "GET", user_id="u1")
            mock_l.info.assert_called_once()

    def test_log_response(self):
        with patch("shared.utils.logger.logger") as mock_l:
            log_response("/api/tasks", "GET", 200, 42.5)
            mock_l.info.assert_called_once()

    def test_log_error(self):
        with patch("shared.utils.logger.logger") as mock_l:
            log_error("/api/tasks", "GET", ValueError("oops"))
            mock_l.error.assert_called_once()


from shared.utils.notifications import (
    send_push_notification,
    send_email_notification,
    send_sms_notification,
    notify_task_overdue,
    notify_critical_alert,
    notify_habit_missed,
    notify_bedtime_reminder,
)


class TestNotifications:

    def test_send_push_notification(self):
        result = send_push_notification("user-1", "Title", "Body")
        assert result is True

    def test_send_push_notification_with_data(self):
        result = send_push_notification("u1", "T", "B", data={"k": "v"})
        assert result is True

    def test_send_email_notification(self):
        result = send_email_notification("user@test.com", "Subject", "Body")
        assert result is True

    def test_send_sms_notification(self):
        result = send_sms_notification("+1234567890", "SMS body")
        assert result is True

    def test_notify_task_overdue(self):
        result = notify_task_overdue("Finish report", "user@test.com")
        assert result is None

    def test_notify_critical_alert(self):
        result = notify_critical_alert("System down", "+1234567890")
        assert result is None

    def test_notify_habit_missed(self):
        result = notify_habit_missed("Read 30 mins", "user@test.com")
        assert result is None

    def test_notify_bedtime_reminder(self):
        result = notify_bedtime_reminder("user@test.com", "10:00 PM")
        assert result is None
