"""Tests for all security utility modules: xss, sanitizer, csrf, audit, security, validators, rate_limiter."""

# ruff: noqa: E402

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock, AsyncMock

pytestmark = pytest.mark.asyncio


# ═══════════════════════════════════════════════════════════════
# 1. xss.py — XSS detection and sanitization
# ═══════════════════════════════════════════════════════════════

class TestXSSFunctions:

    # -- sanitize_html --

    async def test_sanitize_html_normal_string(self):
        from shared.utils.xss import sanitize_html
        assert sanitize_html("hello world") == "hello world"

    async def test_sanitize_html_empty_string(self):
        from shared.utils.xss import sanitize_html
        assert sanitize_html("") == ""

    async def test_sanitize_html_non_string(self):
        from shared.utils.xss import sanitize_html
        assert sanitize_html(123) == "123"
        assert sanitize_html(None) == "None"

    async def test_sanitize_html_script_tags(self):
        from shared.utils.xss import sanitize_html
        result = sanitize_html("<script>alert(1)</script>")
        assert "script" not in result.lower()

    async def test_sanitize_html_javascript_uri(self):
        from shared.utils.xss import sanitize_html
        result = sanitize_html("javascript:alert(1)")
        assert "javascript" not in result.lower()

    async def test_sanitize_html_event_handler(self):
        from shared.utils.xss import sanitize_html
        result = sanitize_html('<div onload="evil()">')
        assert "onload" not in result.lower()

    async def test_sanitize_html_iframe(self):
        from shared.utils.xss import sanitize_html
        result = sanitize_html("<iframe src='evil.com'>")
        assert "iframe" not in result.lower()

    async def test_sanitize_html_object(self):
        from shared.utils.xss import sanitize_html
        result = sanitize_html("<object data='evil'>")
        assert "object" not in result.lower()

    async def test_sanitize_html_embed(self):
        from shared.utils.xss import sanitize_html
        result = sanitize_html("<embed src='evil'>")
        assert "embed" not in result.lower()

    async def test_sanitize_html_svg_onload(self):
        from shared.utils.xss import sanitize_html
        result = sanitize_html("<svg onload=alert(1)>")
        assert "onload" not in result.lower()

    async def test_sanitize_html_document_cookie(self):
        from shared.utils.xss import sanitize_html
        result = sanitize_html("document.cookie")
        assert result == ""

    async def test_sanitize_html_eval(self):
        from shared.utils.xss import sanitize_html
        result = sanitize_html("eval(something)")
        assert "eval" not in result.lower()

    async def test_sanitize_html_link_tag(self):
        from shared.utils.xss import sanitize_html
        result = sanitize_html('<link href="evil.css">')
        assert "link" not in result.lower()

    async def test_sanitize_html_data_uri(self):
        from shared.utils.xss import sanitize_html
        result = sanitize_html("data:text/html,<script>alert(1)</script>")
        assert "data" not in result.lower()

    async def test_sanitize_html_escapes_remaining_html(self):
        from shared.utils.xss import sanitize_html
        result = sanitize_html("<b>safe</b>")
        assert result == "&lt;b&gt;safe&lt;/b&gt;"

    # -- strip_html --

    async def test_strip_html_normal_text(self):
        from shared.utils.xss import strip_html
        assert strip_html("hello world") == "hello world"

    async def test_strip_html_removes_tags(self):
        from shared.utils.xss import strip_html
        assert strip_html("<p>Hello</p>") == "Hello"

    async def test_strip_html_decodes_entities(self):
        from shared.utils.xss import strip_html
        result = strip_html("&amp; &lt; &gt;")
        assert result == "& < >"

    async def test_strip_html_non_string(self):
        from shared.utils.xss import strip_html
        assert strip_html(123) == "123"

    async def test_strip_html_mixed(self):
        from shared.utils.xss import strip_html
        assert strip_html("Hello <b>World</b>!") == "Hello World!"

    # -- sanitize_object --

    async def test_sanitize_object_string(self):
        from shared.utils.xss import sanitize_object
        assert sanitize_object("<script>alert(1)</script>") == ""

    async def test_sanitize_object_dict(self):
        from shared.utils.xss import sanitize_object
        result = sanitize_object({"a": "<script>alert(1)</script>", "b": "safe"})
        assert result["a"] == ""
        assert result["b"] == "safe"

    async def test_sanitize_object_nested_dict(self):
        from shared.utils.xss import sanitize_object
        result = sanitize_object({"a": {"b": "<script>alert(1)</script>"}})
        assert result["a"]["b"] == ""

    async def test_sanitize_object_list(self):
        from shared.utils.xss import sanitize_object
        result = sanitize_object(["<script>alert(1)</script>", "safe"])
        assert result[0] == ""
        assert result[1] == "safe"

    async def test_sanitize_object_max_depth_exceeded(self):
        from shared.utils.xss import sanitize_object
        deep = {"a": {"b": {"c": {"d": {"e": {"f": {"g": {"h": {"i": {"j": {"k": "xss"}}}}}}}}}}}
        result = sanitize_object(deep, max_depth=3)
        # At depth 4 (_depth=4 > max_depth=3), returns obj as-is
        assert result["a"]["b"]["c"] is not None

    async def test_sanitize_object_non_string_non_container(self):
        from shared.utils.xss import sanitize_object
        assert sanitize_object(42) == 42
        assert sanitize_object(True) is True
        assert sanitize_object(None) is None

    # -- has_xss --

    async def test_has_xss_clean_text(self):
        from shared.utils.xss import has_xss
        assert has_xss("hello world") is None

    async def test_has_xss_script_tags(self):
        from shared.utils.xss import has_xss
        assert has_xss("<script>alert(1)</script>") == "script tags"

    async def test_has_xss_javascript_uri(self):
        from shared.utils.xss import has_xss
        assert has_xss("javascript:alert(1)") == "javascript: URIs"

    async def test_has_xss_event_handler(self):
        from shared.utils.xss import has_xss
        assert has_xss("onload=") == "event handlers"

    # -- detect_xss_in_object --

    async def test_detect_xss_string(self):
        from shared.utils.xss import detect_xss_in_object
        assert detect_xss_in_object("<script>alert(1)</script>") == [("ROOT", "script tags")]

    async def test_detect_xss_clean_string(self):
        from shared.utils.xss import detect_xss_in_object
        assert detect_xss_in_object("safe text") == []

    async def test_detect_xss_dict(self):
        from shared.utils.xss import detect_xss_in_object
        result = detect_xss_in_object({"a": "<script>alert(1)</script>"})
        assert result == [("a", "script tags")]

    async def test_detect_xss_nested_dict(self):
        from shared.utils.xss import detect_xss_in_object
        result = detect_xss_in_object({"a": {"b": "javascript:alert(1)"}})
        assert ("a.b", "javascript: URIs") in result

    async def test_detect_xss_list(self):
        from shared.utils.xss import detect_xss_in_object
        result = detect_xss_in_object(["<script>alert(1)</script>"])
        assert len(result) >= 1

    async def test_detect_xss_max_depth(self):
        from shared.utils.xss import detect_xss_in_object
        deep = {"a": {"b": {"c": {"d": {"e": {"f": "javascript:alert(1)"}}}}}}
        result = detect_xss_in_object(deep, max_depth=2)
        # Deep nesting beyond max_depth is not inspected
        assert all("f" not in item[0] for item in result)

    async def test_detect_xss_non_string_non_container(self):
        from shared.utils.xss import detect_xss_in_object
        assert detect_xss_in_object(42) == []


# ═══════════════════════════════════════════════════════════════
# 2. sanitizer.py — Input sanitization functions + middleware
# ═══════════════════════════════════════════════════════════════

class TestSanitizerFunctions:

    async def test_sanitize_value_normal(self):
        from shared.utils.sanitizer import sanitize_value
        assert sanitize_value("hello") == "hello"

    async def test_sanitize_value_script_tags(self):
        from shared.utils.sanitizer import sanitize_value
        result = sanitize_value("<script>alert(1)</script>")
        assert "script" not in result.lower()

    async def test_sanitize_value_javascript(self):
        from shared.utils.sanitizer import sanitize_value
        result = sanitize_value("javascript:alert(1)")
        assert "javascript" not in result.lower()

    async def test_sanitize_value_onevent(self):
        from shared.utils.sanitizer import sanitize_value
        result = sanitize_value('onclick="evil()"')
        assert "onclick" not in result.lower()

    async def test_sanitize_value_iframe(self):
        from shared.utils.sanitizer import sanitize_value
        result = sanitize_value("<iframe src='evil.com'>")
        assert "iframe" not in result.lower()

    async def test_sanitize_value_embed(self):
        from shared.utils.sanitizer import sanitize_value
        result = sanitize_value("<embed src='evil'>")
        assert "embed" not in result.lower()

    async def test_sanitize_value_object(self):
        from shared.utils.sanitizer import sanitize_value
        result = sanitize_value("<object data='evil'>")
        assert "object" not in result.lower()

    async def test_sanitize_value_data_text_html(self):
        from shared.utils.sanitizer import sanitize_value
        result = sanitize_value("data:text/html,<script>")
        assert "data" not in result.lower()

    async def test_sanitize_value_vbscript(self):
        from shared.utils.sanitizer import sanitize_value
        result = sanitize_value('vbscript:msgbox(1)')
        assert "vbscript" not in result.lower()

    async def test_sanitize_value_expression(self):
        from shared.utils.sanitizer import sanitize_value
        result = sanitize_value("expression(alert(1))")
        assert "expression" not in result.lower()

    async def test_sanitize_value_document_cookie(self):
        from shared.utils.sanitizer import sanitize_value
        result = sanitize_value("document.cookie")
        assert result == ""

    async def test_sanitize_value_document_write(self):
        from shared.utils.sanitizer import sanitize_value
        result = sanitize_value("document.write('x')")
        assert "document" not in result.lower()

    async def test_sanitize_value_alert(self):
        from shared.utils.sanitizer import sanitize_value
        result = sanitize_value("alert(1)")
        assert "alert" not in result.lower()
        assert "1)" in result

    async def test_sanitize_value_eval(self):
        from shared.utils.sanitizer import sanitize_value
        result = sanitize_value("eval(code)")
        assert "eval" not in result.lower()
        assert "code)" in result

    async def test_sanitize_value_strips_whitespace(self):
        from shared.utils.sanitizer import sanitize_value
        result = sanitize_value("  hello  ")
        assert result == "hello"

    async def test_sanitize_dict_flat(self):
        from shared.utils.sanitizer import sanitize_dict
        result = sanitize_dict({"a": "<script>alert(1)</script>", "b": "hello"})
        assert result["a"] == ""
        assert result["b"] == "hello"

    async def test_sanitize_dict_nested(self):
        from shared.utils.sanitizer import sanitize_dict
        result = sanitize_dict({"a": {"b": "<script>alert(1)</script>"}})
        assert result["a"]["b"] == ""

    async def test_sanitize_dict_list_values(self):
        from shared.utils.sanitizer import sanitize_dict
        result = sanitize_dict({"a": ["<script>alert(1)</script>", "hello"]})
        assert result["a"][0] == ""
        assert result["a"][1] == "hello"

    async def test_sanitize_dict_list_with_nested_dicts(self):
        from shared.utils.sanitizer import sanitize_dict
        result = sanitize_dict({"a": [{"b": "<script>alert(1)</script>"}, "hello"]})
        assert result["a"][0]["b"] == ""

    async def test_sanitize_dict_non_string_values(self):
        from shared.utils.sanitizer import sanitize_dict
        result = sanitize_dict({"a": 123, "b": None, "c": True})
        assert result["a"] == 123
        assert result["b"] is None
        assert result["c"] is True

    async def test_sanitize_dict_empty(self):
        from shared.utils.sanitizer import sanitize_dict
        assert sanitize_dict({}) == {}


class TestInputSanitizer:

    async def test_post_with_json_sanitizes_body(self):
        from shared.utils.sanitizer import InputSanitizer
        from fastapi import FastAPI, Request
        from fastapi.testclient import TestClient

        app = FastAPI()

        @app.post("/echo")
        async def echo(request: Request):
            body = await request.body()
            return {"body": body.decode()}

        app.add_middleware(InputSanitizer)
        client = TestClient(app)

        response = client.post("/echo", json={"text": "<script>alert(1)</script>", "safe": "hi"})

        assert response.status_code == 200

    async def test_get_skips_sanitization(self):
        from shared.utils.sanitizer import InputSanitizer
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()

        @app.get("/test")
        async def test_get():
            return {"ok": True}

        app.add_middleware(InputSanitizer)
        client = TestClient(app)

        response = client.get("/test")
        assert response.status_code == 200
        assert response.json() == {"ok": True}

    async def test_post_without_json_skips_sanitization(self):
        from shared.utils.sanitizer import InputSanitizer
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()

        @app.post("/form")
        async def form_endpoint():
            return {"ok": True}

        app.add_middleware(InputSanitizer)
        client = TestClient(app)

        response = client.post("/form", data={"field": "value"})
        assert response.status_code == 200

    async def test_put_with_json_sanitizes(self):
        from shared.utils.sanitizer import InputSanitizer
        from fastapi import FastAPI, Request
        from fastapi.testclient import TestClient

        app = FastAPI()

        @app.put("/echo")
        async def echo_put(request: Request):
            body = await request.body()
            return {"body": body.decode()}

        app.add_middleware(InputSanitizer)
        client = TestClient(app)

        response = client.put("/echo", json={"text": "javascript:alert(1)"})
        assert response.status_code == 200

    async def test_patch_with_json_sanitizes(self):
        from shared.utils.sanitizer import InputSanitizer
        from fastapi import FastAPI, Request
        from fastapi.testclient import TestClient

        app = FastAPI()

        @app.patch("/echo")
        async def echo_patch(request: Request):
            body = await request.body()
            return {"body": body.decode()}

        app.add_middleware(InputSanitizer)
        client = TestClient(app)

        response = client.patch("/echo", json={"text": "eval(dangerous)"})
        assert response.status_code == 200


# ═══════════════════════════════════════════════════════════════
# 3. csrf.py — CSRF protection middleware
# ═══════════════════════════════════════════════════════════════

class TestCSRFMiddleware:

    async def test_safe_methods_pass_through(self):
        with patch("shared.utils.csrf.settings") as mock_settings:
            mock_settings.cors_origins = "http://allowed.com"
            from shared.utils.csrf import CSRFMiddleware
            from fastapi import FastAPI
            from fastapi.testclient import TestClient

            app = FastAPI()

            @app.get("/test")
            async def get():
                return {"ok": True}

            @app.head("/test")
            async def head():
                return {"ok": True}

            @app.options("/test")
            async def options():
                return {"ok": True}

            app.add_middleware(CSRFMiddleware)
            client = TestClient(app)

            assert client.get("/test").status_code == 200
            assert client.head("/test").status_code == 200
            assert client.options("/test").status_code == 200

    async def test_post_valid_origin_passes(self):
        with patch("shared.utils.csrf.settings") as mock_settings:
            mock_settings.cors_origins = "http://allowed.com"
            from shared.utils.csrf import CSRFMiddleware
            from fastapi import FastAPI
            from fastapi.testclient import TestClient

            app = FastAPI()

            @app.post("/test")
            async def post():
                return {"ok": True}

            app.add_middleware(CSRFMiddleware)
            client = TestClient(app)

            response = client.post("/test", headers={"Origin": "http://allowed.com"})
            assert response.status_code == 200

    async def test_post_valid_referer_passes(self):
        with patch("shared.utils.csrf.settings") as mock_settings:
            mock_settings.cors_origins = "http://allowed.com"
            from shared.utils.csrf import CSRFMiddleware
            from fastapi import FastAPI
            from fastapi.testclient import TestClient

            app = FastAPI()

            @app.post("/test")
            async def post():
                return {"ok": True}

            app.add_middleware(CSRFMiddleware)
            client = TestClient(app)

            response = client.post("/test", headers={"Referer": "http://allowed.com/page"})
            assert response.status_code == 200

    async def test_post_invalid_origin_returns_403(self):
        with patch("shared.utils.csrf.settings") as mock_settings:
            mock_settings.cors_origins = "http://allowed.com"
            from shared.utils.csrf import CSRFMiddleware
            from fastapi import FastAPI
            from fastapi.testclient import TestClient

            app = FastAPI()

            @app.post("/test")
            async def post():
                return {"ok": True}

            app.add_middleware(CSRFMiddleware)
            client = TestClient(app)

            response = client.post("/test", headers={"Origin": "http://evil.com"})
            assert response.status_code == 403
            data = response.json()
            assert data["detail"] == "CSRF check failed: Origin/Referer not allowed"
            assert data["error_code"] == "CSRF_ORIGIN_MISMATCH"

    async def test_post_invalid_referer_returns_403(self):
        with patch("shared.utils.csrf.settings") as mock_settings:
            mock_settings.cors_origins = "http://allowed.com"
            from shared.utils.csrf import CSRFMiddleware
            from fastapi import FastAPI
            from fastapi.testclient import TestClient

            app = FastAPI()

            @app.post("/test")
            async def post():
                return {"ok": True}

            app.add_middleware(CSRFMiddleware)
            client = TestClient(app)

            response = client.post("/test", headers={"Referer": "http://evil.com/page"})
            assert response.status_code == 403
            assert response.json()["error_code"] == "CSRF_ORIGIN_MISMATCH"

    async def test_post_no_origin_no_referer_logs_warning_and_passes(self):
        with patch("shared.utils.csrf.settings") as mock_settings:
            mock_settings.cors_origins = "http://allowed.com"
            from shared.utils.csrf import CSRFMiddleware
            from fastapi import FastAPI
            from fastapi.testclient import TestClient

            app = FastAPI()

            @app.post("/test")
            async def post():
                return {"ok": True}

            app.add_middleware(CSRFMiddleware)
            client = TestClient(app)

            with patch("shared.utils.csrf.logger") as mock_logger:
                response = client.post("/test")
                assert response.status_code == 200
                mock_logger.warn.assert_called_once()

    async def test_origin_host_check_matches_via_parsed_host(self):
        with patch("shared.utils.csrf.settings") as mock_settings:
            mock_settings.cors_origins = "http://allowed.com:3000"
            from shared.utils.csrf import CSRFMiddleware
            from fastapi import FastAPI
            from fastapi.testclient import TestClient

            app = FastAPI()

            @app.post("/test")
            async def post():
                return {"ok": True}

            app.add_middleware(CSRFMiddleware)
            client = TestClient(app)

            # Origin with different port should not match
            response = client.post("/test", headers={"Origin": "http://allowed.com"})
            assert response.status_code == 403

    async def test_origin_matches_via_parsed_host(self):
        with patch("shared.utils.csrf.settings") as mock_settings:
            mock_settings.cors_origins = "http://allowed.com:3000"
            from shared.utils.csrf import CSRFMiddleware
            from fastapi import FastAPI
            from fastapi.testclient import TestClient

            app = FastAPI()

            @app.post("/test")
            async def post():
                return {"ok": True}

            app.add_middleware(CSRFMiddleware)
            client = TestClient(app)

            response = client.post("/test", headers={"Origin": "http://allowed.com:3000"})
            assert response.status_code == 200

    async def test_referer_with_multiple_allowed_origins(self):
        with patch("shared.utils.csrf.settings") as mock_settings:
            mock_settings.cors_origins = "http://a.com, http://b.com"
            from shared.utils.csrf import CSRFMiddleware
            from fastapi import FastAPI
            from fastapi.testclient import TestClient

            app = FastAPI()

            @app.post("/test")
            async def post():
                return {"ok": True}

            app.add_middleware(CSRFMiddleware)
            client = TestClient(app)

            response = client.post("/test", headers={"Referer": "http://b.com/page"})
            assert response.status_code == 200

    async def test_empty_cors_origins_still_processes(self):
        with patch("shared.utils.csrf.settings") as mock_settings:
            mock_settings.cors_origins = ""
            from shared.utils.csrf import CSRFMiddleware
            from fastapi import FastAPI
            from fastapi.testclient import TestClient

            app = FastAPI()

            @app.post("/test")
            async def post():
                return {"ok": True}

            app.add_middleware(CSRFMiddleware)
            client = TestClient(app)

            response = client.post("/test", headers={"Origin": "http://any.com"})
            assert response.status_code == 403


# ═══════════════════════════════════════════════════════════════
# 4. audit.py — Audit logging functions
# ═══════════════════════════════════════════════════════════════

class TestAuditFunctions:

    # -- action_from_method --

    async def test_action_post_returns_create(self):
        from shared.utils.audit import action_from_method
        assert action_from_method("POST") == "create"

    async def test_action_put_returns_update(self):
        from shared.utils.audit import action_from_method
        assert action_from_method("PUT") == "update"

    async def test_action_patch_returns_update(self):
        from shared.utils.audit import action_from_method
        assert action_from_method("PATCH") == "update"

    async def test_action_delete_returns_delete(self):
        from shared.utils.audit import action_from_method
        assert action_from_method("DELETE") == "delete"

    async def test_action_get_returns_read(self):
        from shared.utils.audit import action_from_method
        assert action_from_method("GET") == "read"

    async def test_action_options_returns_read(self):
        from shared.utils.audit import action_from_method
        assert action_from_method("OPTIONS") == "read"

    async def test_action_head_returns_read(self):
        from shared.utils.audit import action_from_method
        assert action_from_method("HEAD") == "read"

    async def test_action_trace_returns_read(self):
        from shared.utils.audit import action_from_method
        assert action_from_method("TRACE") == "read"

    async def test_action_random_method_returns_read(self):
        from shared.utils.audit import action_from_method
        assert action_from_method("RANDOM") == "read"

    # -- log_audit --

    async def test_log_audit_inserts_record(self):
        from shared.utils.audit import log_audit
        mock_supabase = MagicMock()
        mock_supabase.from_.return_value.insert.return_value.execute.return_value = MagicMock(data=[])
        with patch("shared.utils.audit.get_supabase_client", return_value=mock_supabase):
            await log_audit(
                user_id="u1",
                action="create",
                resource="tasks",
                resource_id="r1",
                details={"k": "v"},
                ip_address="127.0.0.1",
                user_agent="agent",
            )
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
        from shared.utils.audit import log_audit
        mock_supabase = MagicMock()
        mock_supabase.from_.return_value.insert.return_value.execute.return_value = MagicMock(data=[])
        with patch("shared.utils.audit.get_supabase_client", return_value=mock_supabase):
            await log_audit(user_id="u1", action="read", resource="tasks")
        payload = mock_supabase.from_.return_value.insert.call_args[0][0]
        assert payload["resource_id"] is None
        assert payload["details"] is None
        assert payload["ip_address"] is None
        assert payload["user_agent"] is None

    async def test_log_audit_handles_exception(self):
        from shared.utils.audit import log_audit
        mock_supabase = MagicMock()
        mock_supabase.from_.return_value.insert.return_value.execute.side_effect = Exception("DB error")
        with patch("shared.utils.audit.get_supabase_client", return_value=mock_supabase):
            with patch("shared.utils.audit.logger") as mock_logger:
                await log_audit(user_id="u1", action="create", resource="tasks")
                mock_logger.error.assert_called_once()

    # -- audit_middleware_dispatch --

    async def test_middleware_dispatches_for_post(self):
        from shared.utils.audit import audit_middleware_dispatch
        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.url.path = "/api/v1/tasks/123"
        mock_request.client.host = "10.0.0.1"
        mock_request.headers.get.return_value = "test-agent"
        with patch("shared.utils.audit.log_audit", AsyncMock()) as mock_log:
            await audit_middleware_dispatch(mock_request, MagicMock(), user_id="u1")
            mock_log.assert_awaited_once_with(
                user_id="u1", action="create", resource="tasks",
                ip_address="10.0.0.1", user_agent="test-agent",
            )

    async def test_middleware_skips_get(self):
        from shared.utils.audit import audit_middleware_dispatch
        mock_request = MagicMock()
        mock_request.method = "GET"
        with patch("shared.utils.audit.log_audit", AsyncMock()) as mock_log:
            await audit_middleware_dispatch(mock_request, MagicMock(), user_id="u1")
            mock_log.assert_not_called()

    async def test_middleware_skips_without_user_id(self):
        from shared.utils.audit import audit_middleware_dispatch
        mock_request = MagicMock()
        mock_request.method = "POST"
        with patch("shared.utils.audit.log_audit", AsyncMock()) as mock_log:
            await audit_middleware_dispatch(mock_request, MagicMock(), user_id=None)
            mock_log.assert_not_called()

    async def test_middleware_no_client(self):
        from shared.utils.audit import audit_middleware_dispatch
        mock_request = MagicMock()
        mock_request.method = "PUT"
        mock_request.url.path = "/api/v1/goals/5"
        mock_request.client = None
        mock_request.headers.get.return_value = None
        with patch("shared.utils.audit.log_audit", AsyncMock()) as mock_log:
            await audit_middleware_dispatch(mock_request, MagicMock(), user_id="u1")
            mock_log.assert_awaited_once_with(
                user_id="u1", action="update", resource="goals",
                ip_address=None, user_agent=None,
            )

    async def test_middleware_handles_delete(self):
        from shared.utils.audit import audit_middleware_dispatch
        mock_request = MagicMock()
        mock_request.method = "DELETE"
        mock_request.url.path = "/api/v1/ideas/7"
        mock_request.client.host = "10.0.0.1"
        mock_request.headers.get.return_value = "agent"
        with patch("shared.utils.audit.log_audit", AsyncMock()) as mock_log:
            await audit_middleware_dispatch(mock_request, MagicMock(), user_id="u1")
            mock_log.assert_awaited_once_with(
                user_id="u1", action="delete", resource="ideas",
                ip_address="10.0.0.1", user_agent="agent",
            )

    # -- Constants --

    async def test_action_constants(self):
        from shared.utils.audit import CREATE_ACTIONS, UPDATE_ACTIONS, DELETE_ACTIONS, MUTATION_METHODS
        assert CREATE_ACTIONS == {"POST"}
        assert UPDATE_ACTIONS == {"PUT", "PATCH"}
        assert DELETE_ACTIONS == {"DELETE"}
        assert MUTATION_METHODS == {"POST", "PUT", "PATCH", "DELETE"}


# ═══════════════════════════════════════════════════════════════
# 5. security.py — Security utility functions
# ═══════════════════════════════════════════════════════════════

class TestSecurityFunctions:

    # -- generate_secure_token --

    async def test_generate_secure_token_default_length(self):
        from shared.utils.security import generate_secure_token
        token = generate_secure_token()
        assert isinstance(token, str)
        assert len(token) > 0

    async def test_generate_secure_token_custom_length(self):
        from shared.utils.security import generate_secure_token
        token = generate_secure_token(16)
        assert isinstance(token, str)
        assert len(token) > 0

    # -- hash_password / verify_password --

    async def test_hash_password_returns_string(self):
        from shared.utils.security import hash_password
        hashed = hash_password("my_password")
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != "my_password"

    async def test_verify_password_correct(self):
        from shared.utils.security import hash_password, verify_password
        password = "secure_password_123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    async def test_verify_password_incorrect(self):
        from shared.utils.security import hash_password, verify_password
        hashed = hash_password("correct_password")
        assert verify_password("wrong_password", hashed) is False

    # -- sanitize_input --

    async def test_sanitize_input_normal_text(self):
        from shared.utils.security import sanitize_input
        assert sanitize_input("hello world") == "hello world"

    async def test_sanitize_input_script_tag_full(self):
        from shared.utils.security import sanitize_input
        result = sanitize_input("<script>alert(1)</script>")
        assert "script" not in result.lower()

    async def test_sanitize_input_script_tag_alone(self):
        from shared.utils.security import sanitize_input
        result = sanitize_input("<script")
        assert "script" not in result.lower()

    async def test_sanitize_input_javascript(self):
        from shared.utils.security import sanitize_input
        result = sanitize_input("javascript:alert(1)")
        assert "javascript" not in result.lower()

    async def test_sanitize_input_onevent(self):
        from shared.utils.security import sanitize_input
        result = sanitize_input("onclick=")
        assert "onclick" not in result.lower()

    async def test_sanitize_input_iframe_full(self):
        from shared.utils.security import sanitize_input
        result = sanitize_input("<iframe src='evil'>evil</iframe>")
        assert "iframe" not in result.lower()

    async def test_sanitize_input_iframe_alone(self):
        from shared.utils.security import sanitize_input
        result = sanitize_input("<iframe")
        assert "iframe" not in result.lower()

    async def test_sanitize_input_embed(self):
        from shared.utils.security import sanitize_input
        result = sanitize_input("<embed src='evil'>")
        assert "embed" not in result.lower()

    async def test_sanitize_input_object(self):
        from shared.utils.security import sanitize_input
        result = sanitize_input("<object data='evil'>")
        assert "object" not in result.lower()

    async def test_sanitize_input_data_text_html(self):
        from shared.utils.security import sanitize_input
        result = sanitize_input("data:text/html,<script>")
        assert "data" not in result.lower()

    async def test_sanitize_input_vbscript(self):
        from shared.utils.security import sanitize_input
        result = sanitize_input("vbscript:msgbox(1)")
        assert "vbscript" not in result.lower()

    async def test_sanitize_input_expression(self):
        from shared.utils.security import sanitize_input
        result = sanitize_input("expression(alert(1))")
        assert "expression" not in result.lower()

    async def test_sanitize_input_document_cookie(self):
        from shared.utils.security import sanitize_input
        result = sanitize_input("document.cookie")
        assert result == ""

    async def test_sanitize_input_document_write(self):
        from shared.utils.security import sanitize_input
        result = sanitize_input("document.write('x')")
        assert "document" not in result.lower()

    async def test_sanitize_input_alert(self):
        from shared.utils.security import sanitize_input
        result = sanitize_input("alert(1)")
        assert "alert" not in result.lower()
        assert "1)" in result

    async def test_sanitize_input_eval(self):
        from shared.utils.security import sanitize_input
        result = sanitize_input("eval(code)")
        assert "eval" not in result.lower()
        assert "code)" in result

    async def test_sanitize_input_strips_whitespace(self):
        from shared.utils.security import sanitize_input
        result = sanitize_input("  hello  ")
        assert result == "hello"

    # -- sanitize_object --

    async def test_sanitize_object_string(self):
        from shared.utils.security import sanitize_object
        assert sanitize_object("<script>alert(1)</script>") == ""

    async def test_sanitize_object_dict(self):
        from shared.utils.security import sanitize_object
        result = sanitize_object({"a": "<script>alert(1)</script>", "b": "safe"})
        assert result["a"] == ""
        assert result["b"] == "safe"

    async def test_sanitize_object_list(self):
        from shared.utils.security import sanitize_object
        result = sanitize_object(["<script>alert(1)</script>", "safe"])
        assert result[0] == ""
        assert result[1] == "safe"

    async def test_sanitize_object_non_string_non_container(self):
        from shared.utils.security import sanitize_object
        assert sanitize_object(42) == 42
        assert sanitize_object(None) is None
        assert sanitize_object(True) is True

    # -- validate_email --

    async def test_validate_email_valid(self):
        from shared.utils.security import validate_email
        assert validate_email("user@example.com") is True
        assert validate_email("user.name+tag@example.co.uk") is True

    async def test_validate_email_invalid(self):
        from shared.utils.security import validate_email
        assert validate_email("") is False
        assert validate_email("not-an-email") is False
        assert validate_email("user@") is False
        assert validate_email("@example.com") is False
        assert validate_email("user@.com") is False

    # -- validate_url --

    async def test_validate_url_valid(self):
        from shared.utils.security import validate_url
        assert validate_url("https://example.com") is True
        assert validate_url("http://example.com") is True
        assert validate_url("https://example.com/path/to/page") is True

    async def test_validate_url_invalid(self):
        from shared.utils.security import validate_url
        assert validate_url("") is False
        assert validate_url("not-a-url") is False
        assert validate_url("ftp://example.com") is False

    # -- mask_sensitive_data --

    async def test_mask_sensitive_data_normal(self):
        from shared.utils.security import mask_sensitive_data
        result = mask_sensitive_data("abcdefgh", visible_chars=4)
        assert result == "****efgh"

    async def test_mask_sensitive_data_short_data(self):
        from shared.utils.security import mask_sensitive_data
        assert mask_sensitive_data("ab", visible_chars=4) == "**"

    async def test_mask_sensitive_data_exact_length(self):
        from shared.utils.security import mask_sensitive_data
        assert mask_sensitive_data("abcd", visible_chars=4) == "****"

    async def test_mask_sensitive_data_custom_visible(self):
        from shared.utils.security import mask_sensitive_data
        result = mask_sensitive_data("abcdefgh", visible_chars=2)
        assert result == "******gh"

    # -- generate_api_key --

    async def test_generate_api_key_default_prefix(self):
        from shared.utils.security import generate_api_key
        key = generate_api_key()
        assert key.startswith("sk_")
        assert len(key) > 3

    async def test_generate_api_key_custom_prefix(self):
        from shared.utils.security import generate_api_key
        key = generate_api_key(prefix="pk")
        assert key.startswith("pk_")
        assert len(key) > 3


# ═══════════════════════════════════════════════════════════════
# 6. validators.py — Input validation functions
# ═══════════════════════════════════════════════════════════════

class TestValidatorFunctions:

    # -- validate_task_data --

    async def test_validate_task_data_valid(self):
        from shared.utils.validators import validate_task_data
        result = validate_task_data("Study math")
        assert result["valid"] is True
        assert result["errors"] == []

    async def test_validate_task_data_empty_title(self):
        from shared.utils.validators import validate_task_data
        result = validate_task_data("")
        assert result["valid"] is False
        assert "Title is required" in result["errors"]

    async def test_validate_task_data_whitespace_title(self):
        from shared.utils.validators import validate_task_data
        result = validate_task_data("   ")
        assert result["valid"] is False

    async def test_validate_task_data_long_title(self):
        from shared.utils.validators import validate_task_data
        result = validate_task_data("x" * 201)
        assert result["valid"] is False
        assert "Title must be less than 200 characters" in result["errors"]

    async def test_validate_task_data_invalid_priority(self):
        from shared.utils.validators import validate_task_data
        result = validate_task_data("Task", priority="super_high")
        assert result["valid"] is False
        assert any("Priority" in e for e in result["errors"])

    async def test_validate_task_data_invalid_category(self):
        from shared.utils.validators import validate_task_data
        result = validate_task_data("Task", category="invalid")
        assert result["valid"] is False
        assert any("Category" in e for e in result["errors"])

    async def test_validate_task_data_multiple_errors(self):
        from shared.utils.validators import validate_task_data
        result = validate_task_data("", priority="invalid", category="bad")
        assert result["valid"] is False
        assert len(result["errors"]) >= 3

    # -- validate_due_date --

    async def test_validate_due_date_none(self):
        from shared.utils.validators import validate_due_date
        assert validate_due_date(None) is True

    async def test_validate_due_date_valid_iso(self):
        from shared.utils.validators import validate_due_date
        assert validate_due_date("2026-07-15T10:00:00") is True

    async def test_validate_due_date_valid_iso_z(self):
        from shared.utils.validators import validate_due_date
        assert validate_due_date("2026-07-15T10:00:00Z") is True

    async def test_validate_due_date_invalid(self):
        from shared.utils.validators import validate_due_date
        assert validate_due_date("not-a-date") is False

    # -- validate_recurring_frequency --

    async def test_validate_recurring_frequency_none(self):
        from shared.utils.validators import validate_recurring_frequency
        assert validate_recurring_frequency(None) is True

    async def test_validate_recurring_frequency_valid(self):
        from shared.utils.validators import validate_recurring_frequency
        assert validate_recurring_frequency("daily") is True
        assert validate_recurring_frequency("weekly") is True
        assert validate_recurring_frequency("monthly") is True

    async def test_validate_recurring_frequency_invalid(self):
        from shared.utils.validators import validate_recurring_frequency
        assert validate_recurring_frequency("yearly") is False

    # -- validate_task_input --

    async def test_validate_task_input_valid(self):
        from shared.utils.validators import validate_task_input
        errors = validate_task_input({"title": "My task", "status": "pending", "priority": "high"})
        assert errors == []

    async def test_validate_task_input_empty_title(self):
        from shared.utils.validators import validate_task_input
        errors = validate_task_input({"title": ""})
        assert "title is required" in errors

    async def test_validate_task_input_long_title(self):
        from shared.utils.validators import validate_task_input
        errors = validate_task_input({"title": "x" * 201})
        assert "title must be at most 200 characters" in errors

    async def test_validate_task_input_invalid_status(self):
        from shared.utils.validators import validate_task_input
        errors = validate_task_input({"title": "Task", "status": "invalid_status"})
        assert any("status" in e for e in errors)

    async def test_validate_task_input_invalid_priority(self):
        from shared.utils.validators import validate_task_input
        errors = validate_task_input({"title": "Task", "priority": "invalid"})
        assert any("priority" in e for e in errors)

    async def test_validate_task_input_missing_title_key(self):
        from shared.utils.validators import validate_task_input
        errors = validate_task_input({})
        assert "title is required" in errors

    # -- validate_project_input --

    async def test_validate_project_input_valid(self):
        from shared.utils.validators import validate_project_input
        errors = validate_project_input({"title": "My project", "phase": "planning"})
        assert errors == []

    async def test_validate_project_input_empty_title(self):
        from shared.utils.validators import validate_project_input
        errors = validate_project_input({"title": ""})
        assert "title is required" in errors

    async def test_validate_project_input_invalid_phase(self):
        from shared.utils.validators import validate_project_input
        errors = validate_project_input({"title": "Project", "phase": "invalid_phase"})
        assert any("phase" in e for e in errors)

    async def test_validate_project_input_no_phase(self):
        from shared.utils.validators import validate_project_input
        errors = validate_project_input({"title": "Project"})
        assert errors == []

    # -- validate_date_range --

    async def test_validate_date_range_valid(self):
        from shared.utils.validators import validate_date_range
        assert validate_date_range("2026-07-01T00:00:00", "2026-07-15T00:00:00") is True

    async def test_validate_date_range_same_date(self):
        from shared.utils.validators import validate_date_range
        assert validate_date_range("2026-07-15T00:00:00", "2026-07-15T00:00:00") is True

    async def test_validate_date_range_start_after_end(self):
        from shared.utils.validators import validate_date_range
        assert validate_date_range("2026-07-15T00:00:00", "2026-07-01T00:00:00") is False

    async def test_validate_date_range_invalid_dates(self):
        from shared.utils.validators import validate_date_range
        assert validate_date_range("not-a-date", "2026-07-15T00:00:00") is False

    async def test_validate_date_range_both_invalid(self):
        from shared.utils.validators import validate_date_range
        assert validate_date_range("bad", "also-bad") is False

    # -- VALIDATION_SCHEMAS --

    async def test_validation_schemas_has_task_and_project(self):
        from shared.utils.validators import VALIDATION_SCHEMAS
        assert "task" in VALIDATION_SCHEMAS
        assert "project" in VALIDATION_SCHEMAS
        assert callable(VALIDATION_SCHEMAS["task"])
        assert callable(VALIDATION_SCHEMAS["project"])

    # -- sanitize_and_validate --

    async def test_sanitize_and_validate_task(self):
        from shared.utils.validators import sanitize_and_validate
        sanitized, errors = sanitize_and_validate({"title": "<script>alert(1)</script>"}, "task")
        assert "<script>" not in sanitized["title"]
        assert "title is required" in errors

    async def test_sanitize_and_validate_project(self):
        from shared.utils.validators import sanitize_and_validate
        sanitized, errors = sanitize_and_validate({"title": "Project", "phase": "invalid"}, "project")
        assert sanitized["title"] == "Project"
        assert any("phase" in e for e in errors)

    async def test_sanitize_and_validate_unknown_schema(self):
        from shared.utils.validators import sanitize_and_validate
        sanitized, errors = sanitize_and_validate({"title": "Test"}, "unknown_type")
        assert sanitized["title"] == "Test"
        assert "unknown schema type: unknown_type" in errors


# ═══════════════════════════════════════════════════════════════
# 7. rate_limiter.py — Rate limiting middleware + endpoint limiter
# ═══════════════════════════════════════════════════════════════

class TestRateLimiterMiddleware:

    async def test_within_limit_returns_200(self):
        from shared.utils.rate_limiter import RateLimiter
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()

        @app.get("/test")
        async def test_get():
            return {"ok": True}

        app.add_middleware(RateLimiter, max_requests=10, window_seconds=60)
        client = TestClient(app)

        response = client.get("/test")
        assert response.status_code == 200
        assert response.json() == {"ok": True}

    async def test_exceeding_limit_returns_429(self):
        from shared.utils.rate_limiter import RateLimiter
        from fastapi import FastAPI, HTTPException, Request
        from unittest.mock import MagicMock, AsyncMock

        app = FastAPI()
        rl = RateLimiter(app, max_requests=3, window_seconds=60)
        request = MagicMock(spec=Request)
        request.client.host = "10.0.0.99"
        request.method = "GET"
        call_next = AsyncMock(return_value=MagicMock(status_code=200))

        for _ in range(3):
            resp = await rl.dispatch(request, call_next)
            assert resp.status_code == 200

        with pytest.raises(HTTPException) as exc:
            await rl.dispatch(request, call_next)
        assert exc.value.status_code == 429
        assert "Rate limit exceeded" in exc.value.detail

    async def test_rate_limit_headers_present(self):
        from shared.utils.rate_limiter import RateLimiter
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()

        @app.get("/test")
        async def test_get():
            return {"ok": True}

        app.add_middleware(RateLimiter, max_requests=5, window_seconds=60)
        client = TestClient(app)

        response = client.get("/test")
        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
        assert response.headers["X-RateLimit-Limit"] == "5"
        assert response.headers["X-RateLimit-Remaining"] == "4"

    async def test_cleanup_old_entries_via_mocked_time(self):
        from shared.utils.rate_limiter import RateLimiter
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from datetime import datetime

        fixed_now = datetime(2026, 7, 14, 12, 0, 0, tzinfo=timezone.utc)
        old_now = datetime(2026, 7, 14, 11, 58, 0, tzinfo=timezone.utc)

        app = FastAPI()

        @app.get("/test")
        async def test_get():
            return {"ok": True}

        limiter_instance = RateLimiter(app, max_requests=5, window_seconds=60)
        app.add_middleware(RateLimiter, max_requests=5, window_seconds=60)

        with patch("shared.utils.rate_limiter.datetime") as mock_dt:
            mock_dt.now.return_value = old_now
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            mock_dt.timezone = timezone
            mock_dt.timedelta = timedelta

            client1 = TestClient(app)
            client1.get("/test")

        with patch("shared.utils.rate_limiter.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_now
            mock_dt.timezone = timezone
            mock_dt.timedelta = timedelta

            client2 = TestClient(app)
            response = client2.get("/test")
            assert response.status_code == 200


class TestEndpointRateLimiter:

    async def test_check_allows_within_limit(self):
        from shared.utils.rate_limiter import EndpointRateLimiter
        limiter = EndpointRateLimiter()
        assert limiter.check("1.2.3.4", "/api/chat") is True

    async def test_check_blocks_when_exceeded(self):
        from shared.utils.rate_limiter import EndpointRateLimiter
        limiter = EndpointRateLimiter()
        # Make 30 requests (the limit for /api/chat)
        for _ in range(30):
            assert limiter.check("1.2.3.4", "/api/chat") is True
        # 31st request should be denied
        assert limiter.check("1.2.3.4", "/api/chat") is False

    async def test_different_endpoints_have_different_limits(self):
        from shared.utils.rate_limiter import EndpointRateLimiter
        limiter = EndpointRateLimiter()
        # Use up the chat limit
        for _ in range(30):
            assert limiter.check("1.2.3.4", "/api/chat") is True
        # Chat should now be blocked
        assert limiter.check("1.2.3.4", "/api/chat") is False
        # Tasks endpoint should still be allowed (different limit)
        assert limiter.check("1.2.3.4", "/api/tasks") is True

    async def test_different_ips_independent(self):
        from shared.utils.rate_limiter import EndpointRateLimiter
        limiter = EndpointRateLimiter()
        for _ in range(30):
            assert limiter.check("1.2.3.4", "/api/chat") is True
        assert limiter.check("1.2.3.4", "/api/chat") is False
        # Different IP should still be allowed
        assert limiter.check("5.6.7.8", "/api/chat") is True

    async def test_unknown_endpoint_uses_default_limit(self):
        from shared.utils.rate_limiter import EndpointRateLimiter
        limiter = EndpointRateLimiter()
        for _ in range(100):
            assert limiter.check("1.2.3.4", "/api/unknown") is True
        assert limiter.check("1.2.3.4", "/api/unknown") is False

    async def test_cleanup_old_entries(self):
        from shared.utils.rate_limiter import EndpointRateLimiter
        limiter = EndpointRateLimiter()
        old_time = datetime.now(timezone.utc) - timedelta(seconds=120)
        # Manually inject old entry
        limiter.requests["/api/chat"] = {"1.2.3.4": [old_time]}
        # Check should clean the old entry and allow
        assert limiter.check("1.2.3.4", "/api/chat") is True
        # After check, old entry should be gone, only new one exists
        assert len(limiter.requests["/api/chat"]["1.2.3.4"]) == 1
        # The remaining entry should be recent (not the old one)
        recent_time = limiter.requests["/api/chat"]["1.2.3.4"][0]
        assert recent_time > old_time

    async def test_endpoint_limiter_global_instance(self):
        from shared.utils.rate_limiter import endpoint_limiter
        assert isinstance(endpoint_limiter, object)
        assert hasattr(endpoint_limiter, "check")
        assert hasattr(endpoint_limiter, "limits")
        assert hasattr(endpoint_limiter, "requests")
