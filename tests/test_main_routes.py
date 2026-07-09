"""Tests for main.py — health endpoints, middleware, lifespan, exception handlers."""

import importlib.util
import sys
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Load apps/api/main.py explicitly (avoids clash with services/scheduler/main.py)
_API_MAIN_FILE = str(Path(__file__).resolve().parent.parent / "apps" / "api" / "main.py")
_spec = importlib.util.spec_from_file_location("api_main_module", _API_MAIN_FILE)
api_main = importlib.util.module_from_spec(_spec)
sys.modules["api_main_module"] = api_main
_spec.loader.exec_module(api_main)


# ===========================================================================
# Health endpoints — tested via the real main app
# ===========================================================================


class TestHealthEndpoints:
    """Test /, /health, /health/live, /health/ready using the real app."""

    def test_root(self):
        with TestClient(api_main.app) as client:
            resp = client.get("/")
            assert resp.status_code == 200
            body = resp.json()
            assert body["message"] == "Second Brain OS API is running"
            assert "version" in body
            assert "environment" in body
            assert "docs" in body

    def test_health_check(self):
        with TestClient(api_main.app) as client:
            resp = client.get("/health")
            assert resp.status_code == 200
            body = resp.json()
            assert body["status"] == "healthy"
            assert body["uptime_secs"] >= -0.1
            assert body["endpoints_registered"] > 0

    def test_health_live(self):
        with TestClient(api_main.app) as client:
            resp = client.get("/health/live")
            assert resp.status_code == 200
            assert resp.json()["status"] == "alive"

    def test_health_ready_supabase_ollama_ok(self):
        with patch("config.core.supabase.get_supabase_client") as mock_get_sb:
            mock_sb = MagicMock()
            mock_sb.from_.return_value.select.return_value.limit.return_value.execute.return_value.data = []
            mock_get_sb.return_value = mock_sb
            with patch("httpx.AsyncClient") as mock_httpx_cls:
                mock_client = AsyncMock()
                mock_httpx_cls.return_value = mock_client
                mock_client.__aenter__.return_value = mock_client
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_client.get.return_value = mock_response

                with TestClient(api_main.app) as client:
                    resp = client.get("/health/ready")
                    assert resp.status_code == 200
                    body = resp.json()
                    assert body["status"] in ("healthy", "degraded")
                    assert body["dependencies"]["supabase"]["status"] == "ok"
                    assert body["dependencies"]["ollama"]["status"] == "ok"

    def test_health_ready_supabase_error(self):
        with patch("config.core.supabase.get_supabase_client") as mock_get_sb:
            mock_get_sb.side_effect = Exception("Supabase down")
            with patch("httpx.AsyncClient") as mock_httpx_cls:
                mock_client = AsyncMock()
                mock_httpx_cls.return_value = mock_client
                mock_client.__aenter__.return_value = mock_client
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_client.get.return_value = mock_response

                with TestClient(api_main.app) as client:
                    resp = client.get("/health/ready")
                    assert resp.status_code == 200
                    body = resp.json()
                    assert body["status"] == "degraded"
                    assert body["dependencies"]["supabase"]["status"] == "error"

    def test_health_ready_ollama_unavailable(self):
        with patch("config.core.supabase.get_supabase_client") as mock_get_sb:
            mock_sb = MagicMock()
            mock_sb.from_.return_value.select.return_value.limit.return_value.execute.return_value.data = []
            mock_get_sb.return_value = mock_sb
            with patch("httpx.AsyncClient") as mock_httpx_cls:
                mock_client = AsyncMock()
                mock_httpx_cls.return_value = mock_client
                mock_client.__aenter__.return_value = mock_client
                mock_client.get.side_effect = Exception("Ollama not running")

                with TestClient(api_main.app) as client:
                    resp = client.get("/health/ready")
                    assert resp.status_code == 200
                    body = resp.json()
                    assert body["dependencies"]["ollama"]["status"] == "unavailable"

    def test_health_ready_ollama_degraded(self):
        with patch("config.core.supabase.get_supabase_client") as mock_get_sb:
            mock_sb = MagicMock()
            mock_sb.from_.return_value.select.return_value.limit.return_value.execute.return_value.data = []
            mock_get_sb.return_value = mock_sb
            with patch("httpx.AsyncClient") as mock_httpx_cls:
                mock_client = AsyncMock()
                mock_httpx_cls.return_value = mock_client
                mock_client.__aenter__.return_value = mock_client
                mock_response = MagicMock()
                mock_response.status_code = 500
                mock_client.get.return_value = mock_response

                with TestClient(api_main.app) as client:
                    resp = client.get("/health/ready")
                    assert resp.status_code == 200
                    body = resp.json()
                    assert body["dependencies"]["ollama"]["status"] == "degraded"

    def test_health_ready_claude_mode_configured(self):
        with patch("api_main_module.settings") as mock_settings:
            mock_settings.app_version = "1.0.0"
            mock_settings.environment = "test"
            mock_settings.debug = False
            mock_settings.sentry_dsn = None
            mock_settings.use_local_ai = False
            mock_settings.ollama_base_url = "http://localhost:11434"
            mock_settings.claude_api_key = "sk-test-123"
            mock_settings.rate_limit_max = 100
            mock_settings.rate_limit_window = 60
            mock_settings.cors_origins = ""

            with TestClient(api_main.app) as client:
                resp = client.get("/health/ready")
                assert resp.status_code == 200
                body = resp.json()
                assert "claude_api" in body["dependencies"]
                assert body["dependencies"]["claude_api"]["status"] == "configured"

    def test_health_ready_claude_not_configured(self):
        with patch("api_main_module.settings") as mock_settings:
            mock_settings.app_version = "1.0.0"
            mock_settings.environment = "test"
            mock_settings.debug = False
            mock_settings.sentry_dsn = None
            mock_settings.use_local_ai = False
            mock_settings.ollama_base_url = "http://localhost:11434"
            mock_settings.claude_api_key = ""
            mock_settings.rate_limit_max = 100
            mock_settings.rate_limit_window = 60
            mock_settings.cors_origins = ""

            with TestClient(api_main.app) as client:
                resp = client.get("/health/ready")
                assert resp.status_code == 200
                body = resp.json()
                assert body["dependencies"]["claude_api"]["status"] == "not_configured"

    def test_security_headers_present(self):
        with TestClient(api_main.app) as client:
            resp = client.get("/health")
            assert resp.headers.get("X-Content-Type-Options") == "nosniff"
            assert resp.headers.get("X-Frame-Options") == "DENY"
            assert resp.headers.get("X-XSS-Protection") == "1; mode=block"

    def test_request_id_added_to_response(self):
        with TestClient(api_main.app) as client:
            resp = client.get("/health")
            assert "X-Request-ID" in resp.headers
            assert len(resp.headers["X-Request-ID"]) > 0

    def test_request_id_passthrough(self):
        with TestClient(api_main.app) as client:
            custom_id = "my-custom-request-id-abc"
            resp = client.get("/health", headers={"X-Request-ID": custom_id})
            assert resp.headers.get("X-Request-ID") == custom_id


# ===========================================================================
# Cache-Control middleware — tested via minimal test apps
# ===========================================================================


class TestCacheControlMiddleware:
    """Test cache_control_middleware behaviors separate from real app."""

    def _make_app(self, method="GET", path="/api/v1/data"):
        app = FastAPI()
        if method == "GET":

            @app.get(path)
            async def handler():
                return {"ok": True}

        else:

            @app.post(path)
            async def handler():
                return {"ok": True}

        app.middleware("http")(api_main.cache_control_middleware)
        return app

    def test_static_assets_immutable(self):
        app = self._make_app(path="/static/js/app.js")
        with TestClient(app) as client:
            resp = client.get("/static/js/app.js")
            assert resp.headers.get("Cache-Control") == "public, max-age=31536000, immutable"

    def test_assets_immutable(self):
        app = self._make_app(path="/assets/images/logo.png")
        with TestClient(app) as client:
            resp = client.get("/assets/images/logo.png")
            assert resp.headers.get("Cache-Control") == "public, max-age=31536000, immutable"

    def test_health_no_cache(self):
        app = self._make_app(path="/health")
        with TestClient(app) as client:
            resp = client.get("/health")
            assert resp.headers.get("Cache-Control") == "no-store, no-cache, must-revalidate"

    def test_get_private_cache(self):
        app = self._make_app(path="/api/v1/tasks")
        with TestClient(app) as client:
            resp = client.get("/api/v1/tasks")
            cc = resp.headers.get("Cache-Control", "")
            assert "private" in cc
            assert "max-age=60" in cc

    def test_post_no_store(self):
        app = self._make_app(method="POST", path="/api/v1/data")
        with TestClient(app) as client:
            resp = client.post("/api/v1/data", json={"test": True})
            assert resp.headers.get("Cache-Control") == "no-store, must-revalidate"


# ===========================================================================
# Lifespan — tested directly as a context manager
# ===========================================================================


class TestLifespan:
    """Test the lifespan context manager directly."""

    @pytest.mark.asyncio
    async def test_startup_sets_start_time(self):
        app = FastAPI()
        async with api_main.lifespan(app):
            assert hasattr(app.state, "start_time")
            assert app.state.start_time > 0

    @pytest.mark.asyncio
    async def test_sentry_init_when_dsn_set(self):
        app = FastAPI()
        with patch.object(api_main.settings, "sentry_dsn", "https://key@o0.ingest.sentry.io/0"):
            with patch("api_main_module.sentry_sdk.init") as mock_init:
                async with api_main.lifespan(app):
                    pass
                mock_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_sentry_when_dsn_none(self):
        app = FastAPI()
        with patch.object(api_main.settings, "sentry_dsn", None):
            with patch("api_main_module.sentry_sdk.init") as mock_init:
                async with api_main.lifespan(app):
                    pass
                mock_init.assert_not_called()

    @pytest.mark.asyncio
    async def test_shutdown_clears_cache(self):
        app = FastAPI()
        with patch("api_main_module.cache.clear", new=AsyncMock()) as mock_clear:
            async with api_main.lifespan(app):
                pass
            mock_clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_shutdown_with_no_pending_tasks(self):
        app = FastAPI()
        app.state.pending_ai_tasks = []
        with patch("api_main_module.cache.clear", new=AsyncMock()) as mock_clear:
            async with api_main.lifespan(app):
                pass
            mock_clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_startup_event_services_failure(self):
        app = FastAPI()
        with patch("shared.utils.event_outbox.event_outbox.start_background_polling", side_effect=Exception("Failed")):
            with patch("shared.utils.webhook_delivery.webhook_delivery.start_background_polling", side_effect=Exception("Failed")):
                async with api_main.lifespan(app):
                    assert hasattr(app.state, "start_time")

    @pytest.mark.asyncio
    async def test_shutdown_event_services_failure(self):
        app = FastAPI()
        with patch("shared.utils.event_outbox.event_outbox.stop_background_polling", side_effect=Exception("Failed")):
            with patch("shared.utils.webhook_delivery.webhook_delivery.stop_background_polling", side_effect=Exception("Failed")):
                async with api_main.lifespan(app):
                    pass

    @pytest.mark.asyncio
    async def test_shutdown_with_pending_tasks(self):
        app = FastAPI()
        mock_task = AsyncMock()
        app.state.pending_ai_tasks = [mock_task()]
        with patch("api_main_module.cache.clear", new=AsyncMock()):
            async with api_main.lifespan(app):
                pass

    @pytest.mark.asyncio
    async def test_shutdown_pending_tasks_timeout(self):
        app = FastAPI()

        async def never_complete():
            import asyncio

            await asyncio.Event().wait()

        app.state.pending_ai_tasks = [never_complete()]
        import asyncio as _asyncio

        with patch("asyncio.wait_for", side_effect=_asyncio.TimeoutError("timed out")):
            with patch("api_main_module.cache.clear", new=AsyncMock()):
                async with api_main.lifespan(app):
                    pass


# ===========================================================================
# Global exception handler — tested via minimal app
# ===========================================================================


class TestGlobalExceptionHandler:
    """Test the global exception handler on a minimal app."""

    def test_global_handler_returns_500_json(self):
        app = FastAPI()

        @app.get("/error")
        async def error_route():
            raise ValueError("Something went wrong")

        app.exception_handler(Exception)(api_main.global_exception_handler)

        with TestClient(app, raise_server_exceptions=False) as client:
            resp = client.get("/error")
            assert resp.status_code == 500
            body = resp.json()
            assert body["detail"] == "An unexpected error occurred"
            assert body["error_code"] == "INTERNAL_ERROR"
            assert "request_id" in body


# ===========================================================================
# Request ID middleware exception path — tested via minimal app
# ===========================================================================


class TestRequestIdMiddleware:
    """Test request_id_middleware exception handling path."""

    def test_middleware_catches_route_exception(self):
        app = FastAPI()

        @app.get("/error")
        async def error_route():
            raise ValueError("Something broke")

        app.middleware("http")(api_main.request_id_middleware)

        with TestClient(app) as client:
            resp = client.get("/error")
            assert resp.status_code == 500
            body = resp.json()
            assert body["error_code"] == "INTERNAL_ERROR"
            assert "request_id" in body
            assert "X-Request-ID" in resp.headers


# ===========================================================================
# Audit dispatch — tested via minimal app with user state
# ===========================================================================


class TestAuditDispatch:
    """Test the audit logging path for mutation methods."""

    def test_mutation_audit_fires(self):
        app = FastAPI()

        @app.post("/api/v1/test")
        async def create():
            return {"id": "new"}

        app.middleware("http")(api_main.request_id_middleware)

        @app.middleware("http")
        async def set_user_state(request, call_next):
            request.state.user = type("User", (), {"id": "test-user"})()
            return await call_next(request)

        with patch("api_main_module.audit_middleware_dispatch", new=AsyncMock()) as mock_audit:
            with TestClient(app) as client:
                resp = client.post("/api/v1/test", json={"name": "test"})
                assert resp.status_code == 200
                mock_audit.assert_called_once()

    def test_mutation_audit_no_user_does_nothing(self):
        app = FastAPI()

        @app.post("/api/v1/test")
        async def create():
            return {"id": "new"}

        app.middleware("http")(api_main.request_id_middleware)

        with patch("api_main_module.audit_middleware_dispatch", new=AsyncMock()) as mock_audit:
            with TestClient(app) as client:
                resp = client.post("/api/v1/test", json={"name": "test"})
                assert resp.status_code == 200
                mock_audit.assert_not_called()
