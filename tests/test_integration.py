"""Integration tests — FastAPI app health, CORS, and root endpoints."""

import importlib.util
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

API_MAIN = str(Path(__file__).resolve().parent.parent / "apps" / "api" / "main.py")


@pytest.mark.integration
class TestHealthEndpoints:
    """Test health check endpoints on the real app instance."""

    @pytest.fixture(autouse=True)
    def _mock_supabase(self):
        """Mock supabase to prevent real DB calls in readiness check."""
        patcher = patch("config.core.supabase.create_client")
        mock_create = patcher.start()
        mock_supabase = MagicMock()
        mock_supabase.from_.return_value.select.return_value.limit.return_value.execute.return_value.data = []
        mock_create.return_value = mock_supabase
        yield
        patcher.stop()

    def _load_app(self):
        spec = importlib.util.spec_from_file_location("apps_api_main", API_MAIN)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.app

    def _client(self):
        from fastapi.testclient import TestClient
        return TestClient(self._load_app())

    def test_health_returns_200(self):
        client = self._client()
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    def test_health_ready_returns_dependencies(self):
        from config.core.config import settings
        settings.use_local_ai = False
        client = self._client()
        resp = client.get("/health/ready")
        assert resp.status_code == 200
        data = resp.json()
        assert "dependencies" in data
        assert data["status"] in ("healthy", "degraded")

    def test_health_live_returns_alive(self):
        client = self._client()
        resp = client.get("/health/live")
        assert resp.status_code == 200
        assert resp.json()["status"] == "alive"

    def test_root_returns_api_info(self):
        client = self._client()
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data

    def test_cors_headers_present(self):
        client = self._client()
        resp = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert "access-control-allow-origin" in resp.headers
