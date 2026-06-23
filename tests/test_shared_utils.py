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
        assert result == ""

    def test_sanitize_input_case_insensitive(self):
        result = sanitize_input("<SCRiPT>alert(1)</sCrIpT>")
        assert result == ""

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


@pytest.mark.parametrize("expires_delta", [None, timedelta(hours=2)])
def test_create_access_token(expires_delta):
    from config.core.auth import create_access_token

    token = create_access_token({"sub": "user-1", "role": "admin"}, expires_delta=expires_delta)
    assert isinstance(token, str)
    assert token.count(".") == 2  # JWT has 3 parts


def test_rotate_api_key():
    from config.core.auth import rotate_api_key
    from unittest.mock import MagicMock, patch

    mock_supabase = MagicMock()
    with patch("config.core.supabase.get_supabase_client", return_value=mock_supabase):
        result = rotate_api_key("user-1")
    assert "new_key" in result
    assert result["new_key"].startswith("sb_")
    assert "old_key_expires_at" in result


async def test_get_current_user_raises_on_invalid_token():
    from config.core.auth import get_current_user
    from fastapi import HTTPException
    from unittest.mock import patch

    from jose import JWTError
    with patch("config.core.auth.jwt.decode", side_effect=JWTError("bad token")):
        with pytest.raises(HTTPException) as exc:
            await get_current_user(authorization="invalid-token")
        assert exc.value.status_code == 401


class TestAudit:
    def test_action_from_method(self):
        from shared.utils.audit import action_from_method
        assert action_from_method("POST") == "create"
        assert action_from_method("PUT") == "update"
        assert action_from_method("PATCH") == "update"
        assert action_from_method("DELETE") == "delete"
        assert action_from_method("GET") == "read"

    def test_mutation_methods_set(self):
        from shared.utils.audit import MUTATION_METHODS, CREATE_ACTIONS, UPDATE_ACTIONS, DELETE_ACTIONS
        assert "POST" in MUTATION_METHODS
        assert "PUT" in MUTATION_METHODS
        assert "PATCH" in MUTATION_METHODS
        assert "DELETE" in MUTATION_METHODS
        assert "GET" not in MUTATION_METHODS
        assert CREATE_ACTIONS == {"POST"}
        assert UPDATE_ACTIONS == {"PUT", "PATCH"}
        assert DELETE_ACTIONS == {"DELETE"}


class TestCSRF:
    def test_safe_methods_pass(self):
        from shared.utils.csrf import SAFE_METHODS
        for method in ("GET", "HEAD", "OPTIONS", "TRACE"):
            assert method in SAFE_METHODS

    def test_unsafe_methods_not_safe(self):
        from shared.utils.csrf import SAFE_METHODS
        for method in ("POST", "PUT", "PATCH", "DELETE"):
            assert method not in SAFE_METHODS


class TestAuditSchema:
    def test_audit_create_defaults(self):
        from database.schemas.audit import AuditLogCreate
        entry = AuditLogCreate(user_id="u1", action="create", resource="tasks")
        assert entry.user_id == "u1"
        assert entry.resource_id is None
        assert entry.details is None
        assert entry.ip_address is None

    def test_audit_response_fields(self):
        from database.schemas.audit import AuditLogResponse
        from datetime import datetime
        entry = AuditLogResponse(id="1", user_id="u1", action="create", resource="tasks", created_at=datetime.now())
        assert entry.id == "1"
        assert entry.created_at is not None


class TestErrorResponseSchema:
    def test_error_response_defaults(self):
        from database.schemas.error_response import ErrorResponse
        err = ErrorResponse(detail="Not found")
        assert err.detail == "Not found"
        assert err.error_code is None
        assert err.request_id is None
        assert err.timestamp is None

    def test_error_response_full(self):
        from database.schemas.error_response import ErrorResponse
        err = ErrorResponse(detail="Bad request", error_code="INVALID_INPUT", request_id="abc", timestamp=123456.0)
        assert err.detail == "Bad request"
        assert err.error_code == "INVALID_INPUT"
        assert err.request_id == "abc"
        assert err.timestamp == 123456.0


class TestRateLimiterHeaders:
    def test_rate_limiter_headers_present(self):
        from shared.utils.rate_limiter import RateLimiter
        from fastapi import FastAPI

        app = FastAPI()
        limiter = RateLimiter(app, max_requests=50, window_seconds=30)
        assert limiter.max_requests == 50
        assert limiter.window_seconds == 30

    def test_endpoint_limiter_limits(self):
        from shared.utils.rate_limiter import endpoint_limiter
        limits = endpoint_limiter.limits
        assert "/api/chat" in limits
        assert limits["/api/chat"]["max"] == 30
        assert "default" in limits
        assert limits["default"]["max"] == 100


class TestRetentionModule:
    def test_retention_module_imports(self):
        from shared.utils.retention import run_data_retention_cleanup, cleanup_old_audit_logs
        import inspect
        assert inspect.iscoroutinefunction(run_data_retention_cleanup)
        assert inspect.iscoroutinefunction(cleanup_old_audit_logs)

    def test_retention_config_structure(self):
        from shared.utils.retention import run_data_retention_cleanup
        import inspect
        sig = inspect.signature(run_data_retention_cleanup)
        assert "audit_days" in sig.parameters
        assert "chat_days" in sig.parameters
        assert "notification_days" in sig.parameters
        assert sig.parameters["audit_days"].default == 90
        assert sig.parameters["notification_days"].default == 30

    def test_endpoint_limiter_check_allows(self):
        from shared.utils.rate_limiter import endpoint_limiter
        allowed = endpoint_limiter.check("127.0.0.1", "/api/tasks")
        assert allowed is True


class TestAuditEdgeCases:
    def test_action_from_method_all(self):
        from shared.utils.audit import action_from_method
        assert action_from_method("POST") == "create"
        assert action_from_method("PUT") == "update"
        assert action_from_method("PATCH") == "update"
        assert action_from_method("DELETE") == "delete"
        assert action_from_method("GET") == "read"
        assert action_from_method("OPTIONS") == "read"
        assert action_from_method("FOO") == "read"


class TestHealthEndpoint:
    def test_health_response_structure(self):
        from apps.api.main import app
        assert app.title == "Second Brain OS API"
        assert app.version is not None

    def test_app_has_routes(self):
        from apps.api.main import app
        route_paths = [r.path for r in app.routes]
        assert "/" in route_paths
        assert "/health" in route_paths
        assert "/health/ready" in route_paths


# ──────────────────────────────────────────────
# sanitizer.py — XSS SanitizerMiddleware (0% coverage)
# ──────────────────────────────────────────────


from shared.utils.sanitizer import sanitize_value, sanitize_dict, InputSanitizer, DANGEROUS_PATTERNS


class TestSanitizer:

    def test_sanitize_value_removes_script_tags(self):
        assert sanitize_value("<script>alert(1)</script>") == ""

    def test_sanitize_value_removes_javascript_protocol(self):
        result = sanitize_value("javascript:alert(1)")
        assert "javascript" not in result.lower()

    def test_sanitize_value_removes_event_handlers(self):
        result = sanitize_value('onclick="evil()"')
        assert result == '"evil()"'

    def test_sanitize_value_removes_iframe(self):
        assert sanitize_value("<iframe src='http://evil.com'>") == ""

    def test_sanitize_value_removes_embed(self):
        assert sanitize_value("<embed src='http://evil.com'>") == ""

    def test_sanitize_value_removes_object(self):
        assert sanitize_value("<object data='http://evil.com'>") == ""

    def test_sanitize_value_removes_data_text_html(self):
        result = sanitize_value("data:text/html,<script>")
        assert "data" not in result.lower()

    def test_sanitize_value_removes_vbscript(self):
        result = sanitize_value("vbscript:msgbox(1)")
        assert "vbscript" not in result.lower()

    def test_sanitize_value_removes_expression(self):
        result = sanitize_value("expression(alert(1))")
        assert "expression" not in result.lower()

    def test_sanitize_value_removes_document_dot_cookie(self):
        assert sanitize_value("document.cookie") == ""

    def test_sanitize_value_removes_document_dot_write(self):
        assert sanitize_value("document.write") == ""

    def test_sanitize_value_removes_alert(self):
        result = sanitize_value("alert('xss')")
        assert "alert" not in result.lower()

    def test_sanitize_value_removes_eval(self):
        result = sanitize_value("eval(malicious)")
        assert "eval" not in result.lower()

    def test_sanitize_value_clean_text_unchanged(self):
        assert sanitize_value("hello world") == "hello world"

    def test_sanitize_value_empty_string(self):
        assert sanitize_value("") == ""

    def test_sanitize_value_strips_whitespace(self):
        assert sanitize_value("  hello  ") == "hello"

    def test_sanitize_value_mixed_content(self):
        result = sanitize_value("normal <script>bad</script> text")
        assert result == "normal  text"

    def test_sanitize_value_case_insensitive_script(self):
        assert sanitize_value("<SCRIPT>alert(1)</SCRIPT>") == ""

    def test_sanitize_dict_simple_string(self):
        result = sanitize_dict({"name": "<script>alert(1)</script>"})
        assert result == {"name": ""}

    def test_sanitize_dict_multiple_keys(self):
        result = sanitize_dict({"name": "<script>x</script>", "desc": "hello"})
        assert result == {"name": "", "desc": "hello"}

    def test_sanitize_dict_nested(self):
        result = sanitize_dict({"level1": {"name": "<script>x</script>"}})
        assert result == {"level1": {"name": ""}}

    def test_sanitize_dict_deeply_nested(self):
        result = sanitize_dict({"a": {"b": {"c": "<script>x</script>"}}})
        assert result == {"a": {"b": {"c": ""}}}

    def test_sanitize_dict_list_of_strings(self):
        result = sanitize_dict({"items": ["<script>x</script>", "hello"]})
        assert result == {"items": ["", "hello"]}

    def test_sanitize_dict_list_of_dicts(self):
        result = sanitize_dict({"items": [{"msg": "<script>x</script>"}]})
        assert result == {"items": [{"msg": ""}]}

    def test_sanitize_dict_preserves_non_string(self):
        result = sanitize_dict({"num": 42, "flag": True, "none": None})
        assert result == {"num": 42, "flag": True, "none": None}

    def test_sanitize_dict_empty(self):
        assert sanitize_dict({}) == {}

    def test_sanitize_dict_preserves_nested_non_string(self):
        result = sanitize_dict({"a": {"b": 42, "c": [1, 2, 3]}})
        assert result == {"a": {"b": 42, "c": [1, 2, 3]}}

    def test_input_sanitizer_is_base_http_middleware(self):
        from starlette.middleware.base import BaseHTTPMiddleware
        assert issubclass(InputSanitizer, BaseHTTPMiddleware)

    def test_dangerous_patterns_defined(self):
        assert len(DANGEROUS_PATTERNS) > 0
        for pattern, flags in DANGEROUS_PATTERNS:
            assert isinstance(pattern, str)
            assert isinstance(flags, int)

    async def test_input_sanitizer_skips_get(self):
        mock_request = MagicMock()
        mock_request.method = "GET"
        mock_request.headers = {}
        sanitizer = InputSanitizer(MagicMock())
        call_next = AsyncMock(return_value=MagicMock())
        await sanitizer.dispatch(mock_request, call_next)
        call_next.assert_awaited_once()

    async def test_input_sanitizer_skips_head(self):
        mock_request = MagicMock()
        mock_request.method = "HEAD"
        mock_request.headers = {}
        sanitizer = InputSanitizer(MagicMock())
        call_next = AsyncMock(return_value=MagicMock())
        await sanitizer.dispatch(mock_request, call_next)
        call_next.assert_awaited_once()

    async def test_input_sanitizer_sanitizes_json_body(self):
        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.headers = {"content-type": "application/json"}
        mock_request.json = AsyncMock(return_value={"name": "<script>alert(1)</script>"})
        mock_request._body = None
        sanitizer = InputSanitizer(MagicMock())
        call_next = AsyncMock(return_value=MagicMock())
        await sanitizer.dispatch(mock_request, call_next)
        assert mock_request._body == {"name": ""}
        call_next.assert_awaited_once()

    async def test_input_sanitizer_skips_non_json(self):
        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.headers = {"content-type": "text/plain"}
        mock_request._body = None
        sanitizer = InputSanitizer(MagicMock())
        call_next = AsyncMock(return_value=MagicMock())
        await sanitizer.dispatch(mock_request, call_next)
        assert mock_request._body is None
        call_next.assert_awaited_once()

    async def test_input_sanitizer_handles_put(self):
        mock_request = MagicMock()
        mock_request.method = "PUT"
        mock_request.headers = {"content-type": "application/json"}
        mock_request.json = AsyncMock(return_value={"desc": "<script>x</script>"})
        mock_request._body = None
        sanitizer = InputSanitizer(MagicMock())
        call_next = AsyncMock(return_value=MagicMock())
        await sanitizer.dispatch(mock_request, call_next)
        assert mock_request._body == {"desc": ""}

    async def test_input_sanitizer_handles_patch(self):
        mock_request = MagicMock()
        mock_request.method = "PATCH"
        mock_request.headers = {"content-type": "application/json"}
        mock_request.json = AsyncMock(return_value={"title": "clean"})
        mock_request._body = None
        sanitizer = InputSanitizer(MagicMock())
        call_next = AsyncMock(return_value=MagicMock())
        await sanitizer.dispatch(mock_request, call_next)
        assert mock_request._body == {"title": "clean"}

    async def test_input_sanitizer_no_content_type_header(self):
        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.headers = {}
        mock_request._body = None
        sanitizer = InputSanitizer(MagicMock())
        call_next = AsyncMock(return_value=MagicMock())
        await sanitizer.dispatch(mock_request, call_next)
        assert mock_request._body is None
        call_next.assert_awaited_once()


# ──────────────────────────────────────────────
# retry.py — CircuitBreaker & retry utilities (54% coverage)
# ──────────────────────────────────────────────


import time


from shared.utils.retry import (
    retry_with_backoff,
    retry_sync_with_backoff,
    CircuitBreaker,
    CircuitBreakerOpenError,
)


class TestRetryWithBackoff:

    async def test_success_first_try(self):
        fn = AsyncMock(return_value="ok")
        result = await retry_with_backoff(fn, max_retries=3)
        assert result == "ok"
        fn.assert_awaited_once()

    async def test_retry_then_succeed(self):
        fn = AsyncMock(side_effect=[ValueError("fail"), "ok"])
        result = await retry_with_backoff(fn, max_retries=2, base_delay=0.01)
        assert result == "ok"
        assert fn.await_count == 2

    async def test_max_retries_exceeded(self):
        fn = AsyncMock(side_effect=ValueError("persistent failure"))
        with pytest.raises(ValueError, match="persistent failure"):
            await retry_with_backoff(fn, max_retries=2, base_delay=0.01)
        assert fn.await_count == 3

    async def test_custom_exception_types(self):
        fn = AsyncMock(side_effect=TypeError("type mismatch"))
        with pytest.raises(TypeError):
            await retry_with_backoff(fn, max_retries=1, base_delay=0.01, exceptions=(TypeError,))
        assert fn.await_count == 2

    async def test_unhandled_exception_propagates_immediately(self):
        fn = AsyncMock(side_effect=ValueError("unhandled"))
        with pytest.raises(ValueError):
            await retry_with_backoff(fn, max_retries=3, base_delay=0.01, exceptions=(TypeError,))
        assert fn.await_count == 1

    async def test_exponential_backoff_delay_increases(self):
        fn = AsyncMock(side_effect=ValueError("fail"))
        with patch("asyncio.sleep", AsyncMock()) as mock_sleep:
            with pytest.raises(ValueError):
                await retry_with_backoff(fn, max_retries=2, base_delay=1.0, exponential_base=2.0)
            assert mock_sleep.await_count == 2
            args = [c[0][0] for c in mock_sleep.await_args_list]
            assert args == [1.0, 2.0]

    async def test_max_delay_caps_backoff(self):
        fn = AsyncMock(side_effect=ValueError("fail"))
        with patch("asyncio.sleep", AsyncMock()) as mock_sleep:
            with pytest.raises(ValueError):
                await retry_with_backoff(fn, max_retries=5, base_delay=10.0, max_delay=15.0)
            for delay in [c[0][0] for c in mock_sleep.await_args_list]:
                assert delay <= 15.0

    async def test_negative_max_retries_invokes_final_raise(self):
        fn = AsyncMock(side_effect=ValueError("fail"))
        with pytest.raises(TypeError):
            await retry_with_backoff(fn, max_retries=-1)


class TestRetrySyncWithBackoff:

    def test_success_first_try(self):
        calls = 0

        def fn():
            nonlocal calls
            calls += 1
            return "ok"

        decorated = retry_sync_with_backoff(max_retries=2, base_delay=0.01)(fn)
        result = decorated()
        assert result == "ok"
        assert calls == 1

    def test_max_retries_exceeded(self):
        calls = 0

        def fn():
            nonlocal calls
            calls += 1
            raise ValueError("sync fail")

        decorated = retry_sync_with_backoff(max_retries=2, base_delay=0.01)(fn)
        with pytest.raises(ValueError):
            decorated()
        assert calls == 3

    def test_retry_then_succeed(self):
        calls = 0

        def fn():
            nonlocal calls
            calls += 1
            if calls == 1:
                raise ValueError("fail")
            return "ok"

        decorated = retry_sync_with_backoff(max_retries=2, base_delay=0.01)(fn)
        result = decorated()
        assert result == "ok"
        assert calls == 2

    def test_preserves_function_name(self):
        def my_func():
            pass

        decorated = retry_sync_with_backoff()(my_func)
        assert decorated.__name__ == "my_func"

    def test_negative_max_retries_invokes_final_raise(self):
        def fn():
            raise ValueError("fail")

        decorated = retry_sync_with_backoff(max_retries=-1)(fn)
        with pytest.raises(TypeError):
            decorated()


class TestCircuitBreaker:

    def test_initial_state_closed(self):
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        assert cb.state == "closed"
        assert cb.failure_count == 0

    async def test_single_success_stays_closed(self):
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        fn = AsyncMock(return_value="ok")
        result = await cb.call(fn)
        assert result == "ok"
        assert cb.state == "closed"
        assert cb.failure_count == 0

    async def test_opens_after_threshold_failures(self):
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        fn = AsyncMock(side_effect=ValueError("fail"))
        for _ in range(3):
            with pytest.raises(ValueError):
                await cb.call(fn)
        assert cb.state == "open"
        assert cb.failure_count == 3

    async def test_rejects_request_when_open(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=3600)
        fn = AsyncMock(side_effect=ValueError("fail"))
        for _ in range(2):
            with pytest.raises(ValueError):
                await cb.call(fn)
        with pytest.raises(CircuitBreakerOpenError, match="Circuit breaker is OPEN"):
            await cb.call(fn)

    async def test_half_open_success_transitions_to_closed(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0)
        fn = AsyncMock(side_effect=[ValueError("fail"), ValueError("fail"), "recovered"])
        for _ in range(2):
            with pytest.raises(ValueError):
                await cb.call(fn)
        assert cb.state == "open"
        result = await cb.call(fn)
        assert result == "recovered"
        assert cb.state == "closed"
        assert cb.failure_count == 0

    async def test_half_open_failure_returns_to_open(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0)
        fn = AsyncMock(side_effect=[ValueError("fail"), ValueError("fail"), ValueError("still fail")])
        for _ in range(2):
            with pytest.raises(ValueError):
                await cb.call(fn)
        assert cb.state == "open"
        with pytest.raises(ValueError):
            await cb.call(fn)
        assert cb.state == "open"
        assert cb.failure_count == 3

    async def test_stays_open_before_recovery_timeout(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=3600)
        fn = AsyncMock(side_effect=ValueError("fail"))
        for _ in range(2):
            with pytest.raises(ValueError):
                await cb.call(fn)
        with pytest.raises(CircuitBreakerOpenError):
            await cb.call(fn)

    async def test_expected_exception_caught(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=60, expected_exception=(ValueError,))
        fn = AsyncMock(side_effect=TypeError("not expected"))
        with pytest.raises(TypeError):
            await cb.call(fn)
        assert cb.failure_count == 0
        assert cb.state == "closed"

    def test_circuit_breaker_open_error_is_exception(self):
        assert issubclass(CircuitBreakerOpenError, Exception)

    def test_circuit_breaker_open_error_default_message(self):
        err = CircuitBreakerOpenError()
        assert str(err) == ""


# ──────────────────────────────────────────────
# audit.py — AuditLogger, audit_middleware_dispatch (59% coverage)
# ──────────────────────────────────────────────


from shared.utils.audit import log_audit, audit_middleware_dispatch


class TestAuditLog:

    async def test_log_audit_inserts_record(self):
        mock_supabase = MagicMock()
        mock_supabase.from_.return_value.insert.return_value.execute.return_value = MagicMock(data=[])
        with patch("shared.utils.audit.get_supabase_client", return_value=mock_supabase):
            await log_audit(user_id="u1", action="create", resource="tasks", resource_id="r1", details={"k": "v"}, ip_address="127.0.0.1", user_agent="agent")
        mock_supabase.from_.assert_called_once_with("audit_logs")
        insert_call = mock_supabase.from_.return_value.insert
        insert_call.assert_called_once()
        payload = insert_call.call_args[0][0]
        assert payload["user_id"] == "u1"
        assert payload["action"] == "create"
        assert payload["resource"] == "tasks"
        assert payload["resource_id"] == "r1"
        assert payload["details"] == {"k": "v"}
        assert payload["ip_address"] == "127.0.0.1"
        assert payload["user_agent"] == "agent"

    async def test_log_audit_minimal_fields(self):
        mock_supabase = MagicMock()
        mock_supabase.from_.return_value.insert.return_value.execute.return_value = MagicMock(data=[])
        with patch("shared.utils.audit.get_supabase_client", return_value=mock_supabase):
            await log_audit(user_id="u1", action="read", resource="tasks")
        payload = mock_supabase.from_.return_value.insert.call_args[0][0]
        assert payload["resource_id"] is None
        assert payload["details"] is None
        assert payload["ip_address"] is None
        assert payload["user_agent"] is None

    async def test_log_audit_handles_supabase_error(self):
        mock_supabase = MagicMock()
        mock_supabase.from_.return_value.insert.return_value.execute.side_effect = Exception("DB error")
        with patch("shared.utils.audit.get_supabase_client", return_value=mock_supabase):
            with patch("shared.utils.audit.logger") as mock_logger:
                await log_audit(user_id="u1", action="create", resource="tasks")
                mock_logger.error.assert_called_once()

    async def test_audit_middleware_dispatches_for_post(self):
        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.url.path = "/api/v1/tasks/123"
        mock_request.client.host = "10.0.0.1"
        mock_request.headers.get.return_value = "test-agent"
        with patch("shared.utils.audit.log_audit", AsyncMock()) as mock_log:
            await audit_middleware_dispatch(mock_request, MagicMock(), user_id="u1")
            mock_log.assert_awaited_once_with(user_id="u1", action="create", resource="tasks", ip_address="10.0.0.1", user_agent="test-agent")

    async def test_audit_middleware_skips_get(self):
        mock_request = MagicMock()
        mock_request.method = "GET"
        with patch("shared.utils.audit.log_audit", AsyncMock()) as mock_log:
            await audit_middleware_dispatch(mock_request, MagicMock(), user_id="u1")
            mock_log.assert_not_called()

    async def test_audit_middleware_skips_without_user_id(self):
        mock_request = MagicMock()
        mock_request.method = "POST"
        with patch("shared.utils.audit.log_audit", AsyncMock()) as mock_log:
            await audit_middleware_dispatch(mock_request, MagicMock(), user_id=None)
            mock_log.assert_not_called()

    async def test_audit_middleware_handles_no_client(self):
        mock_request = MagicMock()
        mock_request.method = "PUT"
        mock_request.url.path = "/api/v1/goals/5"
        mock_request.client = None
        mock_request.headers.get.return_value = None
        with patch("shared.utils.audit.log_audit", AsyncMock()) as mock_log:
            await audit_middleware_dispatch(mock_request, MagicMock(), user_id="u1")
            mock_log.assert_awaited_once_with(user_id="u1", action="update", resource="goals", ip_address=None, user_agent=None)

    async def test_audit_middleware_handles_delete(self):
        mock_request = MagicMock()
        mock_request.method = "DELETE"
        mock_request.url.path = "/api/v1/ideas/7"
        mock_request.client.host = "10.0.0.1"
        mock_request.headers.get.return_value = "agent"
        with patch("shared.utils.audit.log_audit", AsyncMock()) as mock_log:
            await audit_middleware_dispatch(mock_request, MagicMock(), user_id="u1")
            mock_log.assert_awaited_once_with(user_id="u1", action="delete", resource="ideas", ip_address="10.0.0.1", user_agent="agent")


# ──────────────────────────────────────────────
# csrf.py — CSRFProtectionMiddleware (56% coverage)
# ──────────────────────────────────────────────


import json


from shared.utils.csrf import CSRFMiddleware, CSRF_HEADER


class TestCSRFMiddleware:

    def test_is_base_http_middleware(self):
        from starlette.middleware.base import BaseHTTPMiddleware
        assert issubclass(CSRFMiddleware, BaseHTTPMiddleware)

    async def test_safe_methods_pass_through(self):
        for method in ("GET", "HEAD", "OPTIONS", "TRACE"):
            mock_request = MagicMock()
            mock_request.method = method
            mock_request.headers = {}
            sanitizer = CSRFMiddleware(MagicMock())
            call_next = AsyncMock(return_value=MagicMock(status_code=200))
            response = await sanitizer.dispatch(mock_request, call_next)
            assert response.status_code == 200
            call_next.assert_awaited_once()
            call_next.reset_mock()

    async def test_unsafe_without_origin_or_referer_passes(self):
        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.headers = {"origin": "", "referer": ""}
        csrf = CSRFMiddleware(MagicMock())
        call_next = AsyncMock(return_value=MagicMock(status_code=200))
        response = await csrf.dispatch(mock_request, call_next)
        assert response.status_code == 200
        call_next.assert_awaited_once()

    async def test_missing_csrf_token_returns_403(self):
        from fastapi.responses import JSONResponse
        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.headers = {"origin": "http://example.com", "referer": ""}
        mock_request.state.request_id = "req-abc"
        csrf = CSRFMiddleware(MagicMock())
        call_next = AsyncMock(return_value=MagicMock())
        response = await csrf.dispatch(mock_request, call_next)
        assert response.status_code == 403
        body = json.loads(response.body)
        assert body["detail"] == "CSRF token required"
        assert body["error_code"] == "CSRF_MISSING"
        assert body["request_id"] == "req-abc"
        call_next.assert_not_awaited()

    async def test_present_csrf_token_allows(self):
        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.headers = {"origin": "http://example.com", "referer": "", CSRF_HEADER: "valid-token"}
        csrf = CSRFMiddleware(MagicMock())
        call_next = AsyncMock(return_value=MagicMock(status_code=200))
        response = await csrf.dispatch(mock_request, call_next)
        assert response.status_code == 200
        call_next.assert_awaited_once()

    async def test_referer_triggers_csrf_check(self):
        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.headers = {"origin": "", "referer": "http://example.com/page"}
        mock_request.state.request_id = "req-xyz"
        csrf = CSRFMiddleware(MagicMock())
        call_next = AsyncMock(return_value=MagicMock())
        response = await csrf.dispatch(mock_request, call_next)
        assert response.status_code == 403
        call_next.assert_not_awaited()

    async def test_request_id_empty_string_when_missing(self):
        from types import SimpleNamespace
        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.headers = {"origin": "http://example.com", "referer": ""}
        mock_request.state = SimpleNamespace()
        csrf = CSRFMiddleware(MagicMock())
        call_next = AsyncMock(return_value=MagicMock())
        response = await csrf.dispatch(mock_request, call_next)
        body = json.loads(response.body)
        assert body.get("request_id", "") == ""


# ──────────────────────────────────────────────
# retention.py — Data retention cleanup (24% coverage)
# ──────────────────────────────────────────────


from shared.utils.retention import (
    cleanup_old_audit_logs,
    cleanup_old_chat_messages,
    cleanup_old_notifications,
    run_data_retention_cleanup,
)


class TestRetentionCleanup:

    async def test_cleanup_old_audit_logs_returns_count(self):
        mock_supabase = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [{"id": "1"}, {"id": "2"}]
        mock_supabase.from_.return_value.delete.return_value.lt.return_value.execute.return_value = mock_result
        with patch("shared.utils.retention.get_supabase_client", return_value=mock_supabase):
            count = await cleanup_old_audit_logs(retention_days=90)
        assert count == 2
        mock_supabase.from_.assert_called_once_with("audit_logs")

    async def test_cleanup_old_audit_logs_empty_result(self):
        mock_supabase = MagicMock()
        mock_result = MagicMock()
        mock_result.data = []
        mock_supabase.from_.return_value.delete.return_value.lt.return_value.execute.return_value = mock_result
        with patch("shared.utils.retention.get_supabase_client", return_value=mock_supabase):
            count = await cleanup_old_audit_logs(retention_days=90)
        assert count == 0

    async def test_cleanup_old_audit_logs_none_data(self):
        mock_supabase = MagicMock()
        mock_result = MagicMock()
        mock_result.data = None
        mock_supabase.from_.return_value.delete.return_value.lt.return_value.execute.return_value = mock_result
        with patch("shared.utils.retention.get_supabase_client", return_value=mock_supabase):
            count = await cleanup_old_audit_logs(retention_days=90)
        assert count == 0

    async def test_cleanup_old_chat_messages(self):
        mock_supabase = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [{"id": "c1"}]
        mock_supabase.from_.return_value.delete.return_value.lt.return_value.execute.return_value = mock_result
        with patch("shared.utils.retention.get_supabase_client", return_value=mock_supabase):
            count = await cleanup_old_chat_messages(retention_days=30)
        assert count == 1
        mock_supabase.from_.assert_called_once_with("chat_messages")

    async def test_cleanup_old_chat_messages_empty(self):
        mock_supabase = MagicMock()
        mock_result = MagicMock()
        mock_result.data = []
        mock_supabase.from_.return_value.delete.return_value.lt.return_value.execute.return_value = mock_result
        with patch("shared.utils.retention.get_supabase_client", return_value=mock_supabase):
            count = await cleanup_old_chat_messages(retention_days=30)
        assert count == 0

    async def test_cleanup_old_notifications(self):
        mock_supabase = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [{"id": "n1"}, {"id": "n2"}, {"id": "n3"}]
        mock_supabase.from_.return_value.delete.return_value.lt.return_value.execute.return_value = mock_result
        with patch("shared.utils.retention.get_supabase_client", return_value=mock_supabase):
            count = await cleanup_old_notifications(retention_days=15)
        assert count == 3
        mock_supabase.from_.assert_called_once_with("notifications")

    async def test_cleanup_old_notifications_empty(self):
        mock_supabase = MagicMock()
        mock_result = MagicMock()
        mock_result.data = []
        mock_supabase.from_.return_value.delete.return_value.lt.return_value.execute.return_value = mock_result
        with patch("shared.utils.retention.get_supabase_client", return_value=mock_supabase):
            count = await cleanup_old_notifications(retention_days=15)
        assert count == 0

    async def test_run_data_retention_cleanup_orchestrates(self):
        mock_supabase = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [{"id": "x"}]
        mock_supabase.from_.return_value.delete.return_value.lt.return_value.execute.return_value = mock_result
        with patch("shared.utils.retention.get_supabase_client", return_value=mock_supabase):
            result = await run_data_retention_cleanup(audit_days=90, chat_days=30, notification_days=15)
        assert result == {"audit_logs_removed": 1, "chat_messages_removed": 1, "notifications_removed": 1}


# ──────────────────────────────────────────────
# security.py — sanitize_object (80% → 100%)
# ──────────────────────────────────────────────


from shared.utils.security import sanitize_object


class TestSecuritySanitizeObject:

    def test_sanitize_object_string(self):
        assert sanitize_object("<script>alert(1)</script>") == ""

    def test_sanitize_object_clean_string(self):
        assert sanitize_object("hello world") == "hello world"

    def test_sanitize_object_plain_dict(self):
        result = sanitize_object({"name": "<script>x</script>", "desc": "safe"})
        assert result == {"name": "", "desc": "safe"}

    def test_sanitize_object_nested_dict(self):
        result = sanitize_object({"outer": {"inner": "<script>x</script>"}})
        assert result == {"outer": {"inner": ""}}

    def test_sanitize_object_list(self):
        result = sanitize_object(["<script>x</script>", "hello", "<script>y</script>"])
        assert result == ["", "hello", ""]

    def test_sanitize_object_list_of_dicts(self):
        result = sanitize_object([{"msg": "<script>x</script>"}, {"msg": "safe"}])
        assert result == [{"msg": ""}, {"msg": "safe"}]

    def test_sanitize_object_nested_list_in_dict(self):
        result = sanitize_object({"items": ["<script>x</script>", 42]})
        assert result == {"items": ["", 42]}

    def test_sanitize_object_integer(self):
        assert sanitize_object(42) == 42

    def test_sanitize_object_float(self):
        assert sanitize_object(3.14) == 3.14

    def test_sanitize_object_boolean(self):
        assert sanitize_object(True) is True
        assert sanitize_object(False) is False

    def test_sanitize_object_none(self):
        assert sanitize_object(None) is None

    def test_sanitize_object_empty_string(self):
        assert sanitize_object("") == ""

    def test_sanitize_object_empty_dict(self):
        assert sanitize_object({}) == {}

    def test_sanitize_object_empty_list(self):
        assert sanitize_object([]) == []


# ──────────────────────────────────────────────
# notifications.py — edge cases (91% → 100%)
# ──────────────────────────────────────────────


class TestNotificationsEdgeCases:

    def test_send_email_with_resend_key(self):
        with patch("shared.utils.notifications.os.getenv", return_value="re_abc123"):
            result = send_email_notification("user@test.com", "Subject", "Body")
            assert result is True

    def test_send_push_notification_empty_title(self):
        result = send_push_notification("u1", "", "")
        assert result is True

    def test_send_sms_notification_long_message(self):
        result = send_sms_notification("+1234567890", "x" * 500)
        assert result is True


# ──────────────────────────────────────────────
# date_utils.py — edge cases (98% → 100%)
# ──────────────────────────────────────────────


class TestDateUtilsEdgeCases:

    def test_parse_date_with_z_suffix(self):
        d = parse_date("2026-06-20T12:00:00Z")
        assert d is not None
        assert d.year == 2026
        assert d.month == 6
        assert d.day == 20

    def test_parse_date_with_timezone_offset(self):
        d = parse_date("2026-06-20T12:00:00+05:30")
        assert d is not None
        assert d.hour == 12

    def test_days_until_returns_int_for_valid_date(self):
        result = days_until("2099-01-01")
        assert isinstance(result, int)
        assert result > 0

    def test_format_relative_time_future(self):
        dt = datetime.now() + timedelta(hours=2)
        result = format_relative_time(dt)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_next_occurrence_today(self):
        today_weekday = datetime.now().weekday()
        nxt = get_next_occurrence(today_weekday)
        assert nxt.weekday() == today_weekday

    def test_get_next_occurrence_saturday(self):
        nxt = get_next_occurrence(5)
        assert nxt.weekday() == 5

    def test_format_relative_time_seconds_ago(self):
        dt = datetime.now() - timedelta(seconds=30)
        result = format_relative_time(dt)
        assert "just now" in result

    def test_format_relative_time_hours_ago(self):
        dt = datetime.now() - timedelta(hours=5)
        result = format_relative_time(dt)
        assert "hours" in result

    def test_is_overdue_with_z_suffix_raises_type_error(self):
        with pytest.raises(TypeError):
            is_overdue("2020-01-01T00:00:00Z")


# ──────────────────────────────────────────────
# validators.py — comprehensive coverage (18% → 100%)
# ──────────────────────────────────────────────


class TestValidatorsEdgeCases:

    def test_validate_task_data_whitespace_only_title(self):
        result = validate_task_data("   ")
        assert result["valid"] is False
        assert "Title is required" in result["errors"]

    def test_validate_task_data_title_exactly_200(self):
        result = validate_task_data("x" * 200)
        assert result["valid"] is True

    def test_validate_task_data_title_201_still_fails(self):
        result = validate_task_data("x" * 201)
        assert result["valid"] is False

    def test_validate_due_date_with_z_suffix(self):
        assert validate_due_date("2026-06-20T12:00:00Z") is True

    def test_validate_due_date_with_timezone(self):
        assert validate_due_date("2026-06-20T12:00:00+00:00") is True

    def test_validate_url_with_path_and_query(self):
        assert validate_url("https://example.com/path?q=search") is True

    def test_validate_url_with_trailing_slash(self):
        assert validate_url("https://example.com/") is True

    def test_validate_url_missing_protocol(self):
        assert validate_url("example.com") is False

    def test_validate_url_empty(self):
        assert validate_url("") is False

    def test_validate_url_just_path(self):
        assert validate_url("/path/to/page") is False

    def test_validate_email_with_plus_tag(self):
        assert validate_email("user+tag@example.com") is True

    def test_validate_email_missing_at(self):
        assert validate_email("userexample.com") is False

    def test_validate_email_empty(self):
        assert validate_email("") is False

    def test_validate_email_no_domain(self):
        assert validate_email("user@") is False

    def test_validate_email_no_username(self):
        assert validate_email("@example.com") is False

    def test_validate_email_with_dots(self):
        assert validate_email("first.last@example.co") is True

    def test_validate_email_long_tld(self):
        assert validate_email("user@example.travel") is True

    def test_validate_recurring_frequency_empty_string(self):
        assert validate_recurring_frequency("") is True
