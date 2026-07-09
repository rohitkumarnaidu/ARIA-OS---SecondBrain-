"""Integration tests for LLM-dependent API endpoints.

Tests the full HTTP request -> route handler -> agent -> LLM -> response pipeline
with LLM mocked at the transport layer (ai.client). Validates middleware chains,
dependency injection, error handling, response schemas, and security headers
across the entire request lifecycle.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from config.core.auth import get_current_user


class MockUser:
    class InnerUser:
        id = "test-integration-user-llm"

    user = InnerUser()


async def override_get_current_user():
    return MockUser()


def _build_supabase_mock():
    supabase = MagicMock()
    builder = MagicMock()
    builder.execute.return_value.data = []
    builder.execute.return_value.error = None
    builder.select.return_value = builder
    builder.eq.return_value = builder
    builder.neq.return_value = builder
    builder.order.return_value = builder
    builder.limit.return_value = builder
    builder.range.return_value = builder
    builder.gte.return_value = builder
    builder.insert.return_value = builder
    builder.update.return_value = builder
    builder.delete.return_value = builder
    supabase.from_.return_value = builder
    return supabase


@pytest.fixture(autouse=True)
def _mock_supabase():
    with patch("config.core.supabase.create_client") as mock_create:
        supabase = _build_supabase_mock()
        mock_create.return_value = supabase
        yield supabase


@pytest.fixture(autouse=True)
def _override_auth():
    from apps.api.main import app

    original = app.dependency_overrides.copy()
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original)


class TestChatIntegration:
    """Full-stack integration tests for POST /api/v1/chat/."""

    @pytest.fixture(autouse=True)
    def _configure_settings(self):
        from config.core.config import settings

        orig_url = settings.supabase_url
        orig_key = settings.supabase_key
        settings.supabase_url = "https://test.supabase.co"
        settings.supabase_key = "test-service-role-key"
        yield
        settings.supabase_url = orig_url
        settings.supabase_key = orig_key

    @pytest.fixture(autouse=True)
    def _patch_llm(self):
        with patch("ai.client.llm.generate", new_callable=AsyncMock) as gen:
            gen.return_value = "You have 3 pending tasks. Your top priority is the DB project."
            with patch("ai.client.llm.generate_json", new_callable=AsyncMock) as json_gen:
                json_gen.return_value = {
                    "summary": "Focused on DB project",
                    "preferences": {"preferred_category": "academic"},
                }
                with patch("ai.agents.memory_agent.get_memory_summary", new_callable=AsyncMock) as mem:
                    mem.return_value = {
                        "summary": "User is working on DB project",
                        "preferences": {"preferred_category": "academic"},
                    }
                    yield

    def _client(self):
        from apps.api.main import app

        return TestClient(app)

    def test_chat_success_returns_201(self):
        client = self._client()
        resp = client.post("/api/v1/chat/", json={"message": "What are my tasks today?"})
        assert resp.status_code == 201
        data = resp.json()
        assert "response" in data
        assert data["response"] == "You have 3 pending tasks. Your top priority is the DB project."
        assert "action_taken" in data

    def test_chat_with_context_override(self):
        client = self._client()
        resp = client.post(
            "/api/v1/chat/",
            json={
                "message": "Summarize my day",
                "context": "Focus on academic achievements",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["response"]

    def test_chat_returns_correct_headers(self):
        client = self._client()
        resp = client.post("/api/v1/chat/", json={"message": "Hello ARIA"})
        assert resp.status_code == 201
        assert "X-Request-ID" in resp.headers
        assert "X-Content-Type-Options" in resp.headers
        assert resp.headers["X-Content-Type-Options"] == "nosniff"
        assert "Cache-Control" in resp.headers
        assert "no-store" in resp.headers["Cache-Control"]

    def test_chat_missing_message_returns_422(self):
        client = self._client()
        resp = client.post("/api/v1/chat/", json={})
        assert resp.status_code == 422

    def test_chat_empty_message_returns_200(self):
        client = self._client()
        resp = client.post("/api/v1/chat/", json={"message": ""})
        assert resp.status_code == 201

    def test_chat_llm_fallback_keyword_tasks(self):
        with patch("ai.client.llm.generate", new_callable=AsyncMock) as gen:
            from ai.client import LLMProviderUnavailableError

            gen.side_effect = LLMProviderUnavailableError("Ollama not available")
            client = self._client()
            resp = client.post("/api/v1/chat/", json={"message": "show me my tasks"})
            assert resp.status_code == 201
            data = resp.json()
            assert "pending tasks" in data["response"].lower()

    def test_chat_llm_fallback_keyword_help(self):
        with patch("ai.client.llm.generate", new_callable=AsyncMock) as gen:
            from ai.client import LLMProviderUnavailableError

            gen.side_effect = LLMProviderUnavailableError("API down")
            client = self._client()
            resp = client.post("/api/v1/chat/", json={"message": "help me"})
            assert resp.status_code == 201
            data = resp.json()
            assert "help" in data["response"].lower()

    def test_chat_memory_summary_failure_graceful(self):
        with patch("ai.agents.memory_agent.get_memory_summary", new_callable=AsyncMock) as mem:
            mem.side_effect = RuntimeError("Memory service down")
            client = self._client()
            resp = client.post("/api/v1/chat/", json={"message": "Hi ARIA"})
            assert resp.status_code == 201
            data = resp.json()
            assert data["response"]


class TestBriefingsIntegration:
    """Integration tests for /api/v1/briefings/ endpoints."""

    @pytest.fixture(autouse=True)
    def _configure_settings(self):
        from config.core.config import settings

        orig_url = settings.supabase_url
        orig_key = settings.supabase_key
        settings.supabase_url = "https://test.supabase.co"
        settings.supabase_key = "test-service-role-key"
        yield
        settings.supabase_url = orig_url
        settings.supabase_key = orig_key

    def _client(self):
        from apps.api.main import app

        return TestClient(app)

    def test_list_briefings_returns_200(self):
        client = self._client()
        resp = client.get("/api/v1/briefings/?limit=10&offset=0")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_today_briefing_no_data_returns_null(self):
        client = self._client()
        resp = client.get("/api/v1/briefings/today")
        assert resp.status_code == 200
        assert resp.json() is None

    def test_get_briefing_by_id_not_found_returns_404(self):
        client = self._client()
        resp = client.get("/api/v1/briefings/nonexistent-id")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Briefing not found"


class TestAutomationIntegration:
    """Integration tests for /api/v1/automation/ endpoints."""

    @pytest.fixture(autouse=True)
    def _configure_settings(self):
        from config.core.config import settings

        orig_url = settings.supabase_url
        orig_key = settings.supabase_key
        settings.supabase_url = "https://test.supabase.co"
        settings.supabase_key = "test-service-role-key"
        yield
        settings.supabase_url = orig_url
        settings.supabase_key = orig_key

    def _client(self):
        from apps.api.main import app

        return TestClient(app)

    def test_trigger_briefing_success(self):
        import app.api.automation as am

        with patch.object(am, "generate_daily_briefing", new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = {"briefing": "Test briefing", "priorities": ["Study SQL"]}
            client = self._client()
            resp = client.post("/api/v1/automation/trigger/briefing")
            assert resp.status_code == 201
            data = resp.json()
            assert data["status"] == "success"
            assert "data" in data

    def test_trigger_radar_success(self):
        import app.api.automation as am

        with patch.object(am, "run_opportunity_radar", new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = [{"id": "opp1", "title": "Hackathon", "match_score": 92}]
            client = self._client()
            resp = client.post("/api/v1/automation/trigger/radar")
            assert resp.status_code == 201
            data = resp.json()
            assert data["status"] == "success"
            assert data["count"] == 1

    def test_trigger_weekly_review_success(self):
        import app.api.automation as am

        with patch.object(am, "generate_weekly_review", new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = {"summary": "Great week", "score": 88}
            client = self._client()
            resp = client.post("/api/v1/automation/trigger/weekly-review")
            assert resp.status_code == 201
            data = resp.json()
            assert data["status"] == "success"

    def test_trigger_sleep_analysis_success(self):
        import app.api.automation as am

        with patch.object(am, "analyze_sleep", new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = {"score": 82, "recommendation": "Sleep more"}
            client = self._client()
            resp = client.post("/api/v1/automation/trigger/sleep-analysis")
            assert resp.status_code == 201
            data = resp.json()
            assert data["status"] == "success"

    def test_trigger_nudges_success(self):
        import app.api.automation as am

        with patch.object(am, "run_all_nudges", new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = [{"type": "course", "message": "Complete DB assignment"}]
            client = self._client()
            resp = client.post("/api/v1/automation/trigger/nudges")
            assert resp.status_code == 201
            data = resp.json()
            assert data["status"] == "success"

    def test_trigger_briefing_server_error(self):
        import app.api.automation as am

        with patch.object(am, "generate_daily_briefing", new_callable=AsyncMock) as mock_fn:
            mock_fn.side_effect = RuntimeError("LLM provider chain exhausted")
            client = self._client()
            resp = client.post("/api/v1/automation/trigger/briefing")
            assert resp.status_code == 500
            data = resp.json()
            assert "detail" in data


class TestPlanExecuteIntegration:
    """Integration tests for /api/v1/automation/plan and /execute."""

    @pytest.fixture(autouse=True)
    def _configure_settings(self):
        from config.core.config import settings

        orig_url = settings.supabase_url
        orig_key = settings.supabase_key
        settings.supabase_url = "https://test.supabase.co"
        settings.supabase_key = "test-service-role-key"
        yield
        settings.supabase_url = orig_url
        settings.supabase_key = orig_key

    def _client(self):
        from apps.api.main import app

        return TestClient(app)

    def test_plan_success(self):
        import app.api.automation as am

        with patch.object(am, "orchestrate_plan", new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = {
                "plan_id": "plan-1",
                "steps": [{"action": "search", "target": "tasks"}],
                "summary": "Search tasks",
            }
            client = self._client()
            resp = client.post("/api/v1/automation/plan", json={"query": "find my tasks", "context": {}})
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"

    def test_plan_fallback_on_error(self):
        import app.api.automation as am

        with patch.object(am, "orchestrate_plan", new_callable=AsyncMock) as mock_fn:
            mock_fn.side_effect = RuntimeError("Planner failed")
            client = self._client()
            resp = client.post("/api/v1/automation/plan", json={"query": "find my tasks", "context": {}})
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert data["data"]["plan_id"] == "fallback"

    def test_execute_success(self):
        import app.api.automation as am

        with patch.object(am, "orchestrate_execute", new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = {"action": "query", "result": {"tasks": []}, "summary": "Found 0 tasks"}
            client = self._client()
            resp = client.post("/api/v1/automation/execute", json={"query": "list tasks", "context": {}})
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"

    def test_execute_fallback_on_error(self):
        import app.api.automation as am

        with patch.object(am, "orchestrate_execute", new_callable=AsyncMock) as mock_fn:
            mock_fn.side_effect = RuntimeError("Execution failed")
            client = self._client()
            resp = client.post("/api/v1/automation/execute", json={"query": "list tasks", "context": {}})
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "success"
            assert data["data"]["action"] == "noop"


class TestHealthIntegration:
    """Lightweight smoke tests verifying the app boots and middleware is intact."""

    def _client(self):
        from apps.api.main import app

        return TestClient(app)

    def test_health_returns_200(self):
        client = self._client()
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "endpoints_registered" in data

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

    def test_security_headers_on_all_responses(self):
        client = self._client()
        resp = client.get("/health")
        assert resp.headers.get("X-Content-Type-Options") == "nosniff"
        assert resp.headers.get("X-Frame-Options") == "DENY"
        assert resp.headers.get("X-XSS-Protection") == "1; mode=block"
        assert "X-Request-ID" in resp.headers

    def test_health_cache_control_no_store(self):
        client = self._client()
        resp = client.get("/health")
        assert "no-store" in resp.headers.get("Cache-Control", "")

    def test_unversioned_endpoint_returns_404(self):
        client = self._client()
        resp = client.get("/api/v1/nonexistent")
        assert resp.status_code == 404

    def test_cors_preflight_allows_localhost(self):
        client = self._client()
        resp = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert "access-control-allow-origin" in resp.headers

    def test_global_exception_handler_catches_errors(self):
        from apps.api.main import app

        @app.get("/api/v1/test-crash")
        async def crash():
            raise ValueError("Simulated crash")

        client = TestClient(app)
        resp = client.get("/api/v1/test-crash")
        assert resp.status_code == 500
        data = resp.json()
        assert data["detail"] == "Internal server error"
        assert data["error_code"] == "INTERNAL_ERROR"
        assert "X-Request-ID" in resp.headers

    def test_unauthenticated_endpoint_does_not_require_auth(self):
        client = self._client()
        resp = client.get("/health")
        assert resp.status_code == 200
