"""Tests for /api/v1/monitoring/ endpoints."""

import pytest
from unittest.mock import MagicMock, patch


@pytest.mark.api
class TestMonitoringRoutes:
    """Test token usage recording and summary endpoints."""

    @patch("app.api.monitoring.uuid4")
    @patch("app.api.monitoring.get_supabase_client")
    @pytest.mark.asyncio
    async def test_record_token_usage_success(self, mock_supabase_cli, mock_uuid):
        mock_uuid.return_value = "tok-uuid"
        mock_client = MagicMock()
        mock_supabase_cli.return_value = mock_client
        mock_client.from_.return_value.insert.return_value.execute.return_value.data = [{"id": "tok-uuid"}]
        from app.api.monitoring import record_token_usage

        current_user = MagicMock(user=MagicMock(id="test-user"))
        req = {
            "agent": "briefing_agent",
            "model": "ollama/mistral:7b",
            "prompt_tokens": 500,
            "completion_tokens": 300,
            "duration_ms": 1200,
            "endpoint": "/api/v1/automation/trigger/briefing",
        }
        result = await record_token_usage(req=req, current_user=current_user)
        assert result["status"] == "ok"

    @patch("app.api.monitoring.uuid4")
    @patch("app.api.monitoring.get_supabase_client")
    @pytest.mark.asyncio
    async def test_record_token_usage_handles_db_error(self, mock_supabase_cli, mock_uuid):
        mock_uuid.return_value = "tok-uuid"
        mock_client = MagicMock()
        mock_supabase_cli.return_value = mock_client
        mock_client.from_.return_value.insert.return_value.execute.side_effect = Exception("DB error")
        from app.api.monitoring import record_token_usage

        current_user = MagicMock(user=MagicMock(id="test-user"))
        req = {"agent": "test", "prompt_tokens": 100, "completion_tokens": 50}
        result = await record_token_usage(req=req, current_user=current_user)
        assert result["status"] == "ok"

    @patch("app.api.monitoring.get_supabase_client")
    @pytest.mark.asyncio
    async def test_token_usage_summary_with_data(self, mock_supabase_cli):
        mock_client = MagicMock()
        mock_supabase_cli.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"agent": "briefing", "total_tokens": 1000, "duration_ms": 500},
            {"agent": "briefing", "total_tokens": 2000, "duration_ms": 1500},
            {"agent": "memory", "total_tokens": 500, "duration_ms": 200},
        ]
        from app.api.monitoring import token_usage_summary

        current_user = MagicMock(user=MagicMock(id="test-user"))
        result = await token_usage_summary(current_user=current_user)
        assert result["total_tokens"] == 3500
        assert result["total_calls"] == 3
        assert result["by_agent"] == {"briefing": 3000, "memory": 500}
        assert result["avg_duration_ms"] == 733.3
        assert result["p50_ms"] == 500

    @patch("app.api.monitoring.get_supabase_client")
    @pytest.mark.asyncio
    async def test_token_usage_summary_empty(self, mock_supabase_cli):
        mock_client = MagicMock()
        mock_supabase_cli.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        from app.api.monitoring import token_usage_summary

        current_user = MagicMock(user=MagicMock(id="test-user"))
        result = await token_usage_summary(current_user=current_user)
        assert result["total_tokens"] == 0
        assert result["total_calls"] == 0
        assert result["by_agent"] == {}
        assert result["avg_duration_ms"] == 0

    def test_compute_cost_ollama_returns_zero(self):
        from app.api.monitoring import _compute_cost

        assert _compute_cost("ollama/mistral:7b", 1000, 500) == 0.0

    def test_compute_cost_opus_model(self):
        from app.api.monitoring import _compute_cost

        cost = _compute_cost("claude-opus-4", 1_000_000, 500_000)
        assert cost == (15 + 37.5)

    def test_compute_cost_sonnet_model(self):
        from app.api.monitoring import _compute_cost

        cost = _compute_cost("claude-sonnet-4-20250514", 1_000_000, 500_000)
        assert cost == (3 + 7.5)

    def test_compute_cost_haiku_model(self):
        from app.api.monitoring import _compute_cost

        cost = _compute_cost("claude-haiku-3", 1_000_000, 500_000)
        assert cost == (0.25 + 0.625)

    def test_compute_cost_unknown_model_uses_default(self):
        from app.api.monitoring import _compute_cost

        cost = _compute_cost("unknown-model", 1_000_000, 500_000)
        assert cost == (1_500_000 / 1_000_000 * 3)

    @patch("app.api.monitoring.get_supabase_client")
    @pytest.mark.asyncio
    async def test_token_usage_summary_db_error(self, mock_supabase_cli):
        mock_client = MagicMock()
        mock_supabase_cli.return_value = mock_client
        mock_client.from_.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("DB error")
        from app.api.monitoring import token_usage_summary

        current_user = MagicMock(user=MagicMock(id="test-user"))
        result = await token_usage_summary(current_user=current_user)
        assert result["total_tokens"] == 0
        assert result["total_calls"] == 0
