"""Tests for AIObservability — token tracking, latency, errors, metrics, dashboard."""

from datetime import datetime, timedelta, timezone

import pytest

from ai.observability import AIObservability


@pytest.fixture
def obs() -> AIObservability:
    return AIObservability()


class TestRecordUsage:
    """Tests for token usage tracking."""

    def test_record_and_get_usage(self, obs: AIObservability):
        obs.record_usage("briefing", 500, 200, "mistral", 3200, True, provider="ollama")
        result = obs.get_agent_usage("briefing")
        assert result["total_calls"] == 1
        assert result["total_input_tokens"] == 500
        assert result["total_output_tokens"] == 200
        assert result["total_tokens"] == 700
        assert result["avg_duration_ms"] == 3200.0
        assert result["error_rate"] == 0.0

    def test_usage_with_errors(self, obs: AIObservability):
        obs.record_usage("task", 100, 50, "mistral", 1000, True, provider="ollama")
        obs.record_usage("task", 200, 100, "claude", 2000, False, provider="claude")
        obs.record_usage("task", 150, 75, "mistral", 1500, True, provider="ollama")
        result = obs.get_agent_usage("task")
        assert result["total_calls"] == 3
        assert result["error_count"] == 1
        assert result["error_rate"] == pytest.approx(1.0 / 3.0, 0.01)

    def test_usage_time_filtering(self, obs: AIObservability):
        obs.record_usage("briefing", 100, 50, "mistral", 1000, True, provider="ollama")
        since = datetime.now(timezone.utc) + timedelta(hours=1)
        result = obs.get_agent_usage("briefing", since=since)
        assert result["total_calls"] == 0

    def test_unknown_agent_usage(self, obs: AIObservability):
        result = obs.get_agent_usage("nonexistent")
        assert result["total_calls"] == 0
        assert result["agent"] == "nonexistent"

    def test_record_with_zero_tokens(self, obs: AIObservability):
        obs.record_usage("briefing", 0, 0, "mistral", 100, True, provider="ollama")
        result = obs.get_agent_usage("briefing")
        assert result["total_calls"] == 1
        assert result["total_tokens"] == 0


class TestGetProviderUsage:
    """Tests for provider-level usage stats."""

    def test_provider_usage(self, obs: AIObservability):
        obs.record_usage("briefing", 500, 200, "mistral", 3200, True, provider="ollama")
        obs.record_usage("task", 300, 150, "mistral", 2000, True, provider="ollama")
        obs.record_usage("briefing", 1000, 500, "claude-sonnet-4", 5000, True, provider="claude")
        result = obs.get_provider_usage("ollama")
        assert result["total_calls"] == 2
        assert result["total_input_tokens"] == 800
        assert result["total_output_tokens"] == 350
        assert result["success_count"] == 2
        result_claude = obs.get_provider_usage("claude")
        assert result_claude["total_calls"] == 1

    def test_unknown_provider(self, obs: AIObservability):
        result = obs.get_provider_usage("nonexistent")
        assert result["total_calls"] == 0


class TestCostReport:
    """Tests for cost estimation."""

    def test_cost_report_basic(self, obs: AIObservability):
        obs.record_usage("briefing", 1000, 500, "mistral", 3000, True, provider="ollama")
        obs.record_usage("briefing", 500, 200, "claude-sonnet-4", 2000, True, provider="claude")
        report = obs.get_cost_report()
        assert report["total_calls"] == 2
        assert report["by_provider"]["ollama"]["calls"] == 1
        assert report["by_provider"]["claude"]["calls"] == 1
        assert report["by_agent"]["briefing"]["calls"] == 2

    def test_cost_report_with_time_range(self, obs: AIObservability):
        obs.record_usage("briefing", 100, 50, "mistral", 1000, True, provider="ollama")
        since = datetime.now(timezone.utc) + timedelta(hours=1)
        report = obs.get_cost_report(since=since)
        assert report["total_calls"] == 0

    def test_cost_calculation_ollama_free(self, obs: AIObservability):
        obs.record_usage("briefing", 1000, 500, "mistral", 3000, True, provider="ollama")
        report = obs.get_cost_report()
        assert report["by_provider"]["ollama"]["cost"] == 0.0

    def test_cost_calculation_claude(self, obs: AIObservability):
        obs.record_usage("briefing", 1000000, 500000, "claude-sonnet-4", 5000, True, provider="claude")
        report = obs.get_cost_report()
        claude_cost = report["by_provider"]["claude"]["cost"]
        assert claude_cost > 0
        expected = (1000000 * 3.0 / 1_000_000) + (500000 * 15.0 / 1_000_000)
        assert claude_cost == pytest.approx(expected, 0.01)

    def test_cost_report_empty(self, obs: AIObservability):
        report = obs.get_cost_report()
        assert report["total_calls"] == 0
        assert report["total_cost"] == 0.0


class TestLatencyTracking:
    """Tests for latency recording and querying."""

    def test_record_and_get_latency(self, obs: AIObservability):
        obs.record_latency("briefing", 100, endpoint="generate")
        obs.record_latency("briefing", 200, endpoint="generate")
        obs.record_latency("briefing", 300, endpoint="generate")
        result = obs.get_latency_percentiles("briefing", [50, 95, 99])
        assert result["samples"] == 3
        assert result["p50"] == 200.0
        assert result["p95"] == 300.0
        assert result["p99"] == 300.0

    def test_latency_unknown_agent(self, obs: AIObservability):
        result = obs.get_latency_percentiles("nonexistent")
        assert result["samples"] == 0
        assert result["p50"] == 0.0

    def test_slowest_agents(self, obs: AIObservability):
        obs.record_latency("agent_a", 1000, endpoint="generate")
        obs.record_latency("agent_b", 500, endpoint="generate")
        obs.record_latency("agent_c", 2000, endpoint="generate")
        slowest = obs.get_slowest_agents(top_n=2)
        assert len(slowest) == 2
        assert slowest[0]["agent"] == "agent_c"
        assert slowest[1]["agent"] == "agent_a"


class TestErrorTracking:
    """Tests for error tracking."""

    def test_record_and_get_errors(self, obs: AIObservability):
        obs.record_error("briefing", "LLMTimeoutError", "Request timed out", provider="ollama")
        obs.record_error("briefing", "LLMRateLimitError", "Rate limited", provider="ollama")
        obs.record_usage("briefing", 100, 50, "mistral", 1000, True, provider="ollama")
        error_rate = obs.get_error_rate("briefing", window_minutes=60)
        assert error_rate > 0

    def test_error_rate_no_calls(self, obs: AIObservability):
        obs.record_error("briefing", "LLMTimeoutError", "timeout", provider="ollama")
        error_rate = obs.get_error_rate("nonexistent")
        assert error_rate == 0.0

    def test_most_common_errors(self, obs: AIObservability):
        obs.record_error("agent_a", "Timeout", "timed out", provider="ollama")
        obs.record_error("agent_a", "Timeout", "timed out", provider="ollama")
        obs.record_error("agent_a", "RateLimit", "rate limited", provider="ollama")
        obs.record_error("agent_b", "Timeout", "timed out", provider="ollama")
        common = obs.get_most_common_errors(top_n=5)
        assert len(common) >= 2
        assert common[0]["error_type"] == "Timeout"
        assert common[0]["count"] == 3


class TestPrometheusMetrics:
    """Tests for Prometheus metrics formatting."""

    def test_metrics_format(self, obs: AIObservability):
        obs.record_usage("briefing", 500, 200, "mistral", 3200, True, provider="ollama")
        obs.record_error("briefing", "LLMTimeoutError", "timeout", provider="ollama")
        metrics = obs.get_prometheus_metrics()
        assert "# HELP ai_requests_total" in metrics
        assert "# TYPE ai_requests_total counter" in metrics
        assert "ai_requests_total{" in metrics
        assert "ai_errors_total{" in metrics
        assert "ai_tokens_total{" in metrics
        assert "ai_circuit_breaker_state{" in metrics

    def test_metrics_contains_labels(self, obs: AIObservability):
        obs.record_usage("briefing", 100, 50, "mistral", 1000, True, provider="ollama")
        obs.record_usage("task_agent", 200, 100, "claude", 2000, True, provider="claude")
        metrics = obs.get_prometheus_metrics()
        assert 'agent="briefing"' in metrics
        assert 'provider="ollama"' in metrics
        assert 'agent="task_agent"' in metrics
        assert 'provider="claude"' in metrics
        assert 'type="input"' in metrics
        assert 'type="output"' in metrics

    def test_metrics_agent_name_sanitization(self, obs: AIObservability):
        obs.record_usage("my-cool-agent!", 100, 50, "mistral", 1000, True, provider="ollama")
        metrics = obs.get_prometheus_metrics()
        assert "my-cool-agent!" not in metrics
        assert "my_cool_agent_" in metrics

    def test_metrics_empty(self, obs: AIObservability):
        metrics = obs.get_prometheus_metrics()
        assert "# HELP ai_requests_total" in metrics
        assert "ai_circuit_breaker_state{" in metrics


class TestDashboardSummary:
    """Tests for dashboard summary data."""

    def test_dashboard_summary_with_data(self, obs: AIObservability):
        obs.record_usage("briefing", 500, 200, "mistral", 3200, True, provider="ollama")
        obs.record_usage("task", 300, 150, "mistral", 1000, True, provider="ollama")
        obs.record_usage("sleep", 100, 50, "claude", 500, False, provider="claude")
        summary = obs.get_dashboard_summary()
        assert summary["total_agents"] >= 3
        assert summary["total_calls_last_24h"] >= 3
        assert summary["total_tokens_last_24h"] >= 1300
        assert summary["errors_last_24h"] >= 0

    def test_dashboard_summary_empty(self, obs: AIObservability):
        summary = obs.get_dashboard_summary()
        assert summary["total_agents"] == 0
        assert summary["total_calls_last_24h"] == 0
        assert summary["errors_last_24h"] == 0


class TestAgentHealth:
    """Tests for agent health status."""

    def test_agent_healthy(self, obs: AIObservability):
        obs.record_usage("briefing", 500, 200, "mistral", 3000, True, provider="ollama")
        obs.record_latency("briefing", 3000, endpoint="generate")
        health = obs.get_agent_health("briefing")
        assert health["agent"] == "briefing"
        assert health["status"] == "healthy"
        assert health["total_calls"] == 1
        assert health["last_call_success"] is True

    def test_agent_degraded(self, obs: AIObservability):
        for _ in range(5):
            obs.record_usage("briefing", 100, 50, "mistral", 1000, True, provider="ollama")
        for _ in range(2):
            obs.record_usage("briefing", 100, 50, "mistral", 1000, False, provider="ollama")
            obs.record_error("briefing", "LLMTimeoutError", "timeout", provider="ollama")
        health = obs.get_agent_health("briefing")
        assert health["status"] in ("degraded", "unhealthy")

    def test_agent_unknown(self, obs: AIObservability):
        health = obs.get_agent_health("nonexistent")
        assert health["status"] == "unknown"
        assert health["total_calls"] == 0

    def test_agent_avg_latency(self, obs: AIObservability):
        obs.record_usage("briefing", 100, 50, "mistral", 1000, True, provider="ollama")
        obs.record_latency("briefing", 1000, endpoint="generate")
        obs.record_usage("briefing", 100, 50, "mistral", 2000, True, provider="ollama")
        obs.record_latency("briefing", 2000, endpoint="generate")
        health = obs.get_agent_health("briefing")
        assert health["avg_latency_ms"] == pytest.approx(1500.0, 0.1)


class TestTrackDecorator:
    """Tests for the @observability.track decorator."""

    @pytest.mark.asyncio
    async def test_track_decorator_success(self, obs: AIObservability):
        @obs.track(agent_name="test_agent", model="mistral", provider="ollama")
        async def my_function(input_tokens: int = 0):
            return "success"

        result = await my_function(input_tokens=100)
        assert result == "success"
        usage = obs.get_agent_usage("test_agent")
        assert usage["total_calls"] == 1
        assert usage["total_input_tokens"] == 100

    @pytest.mark.asyncio
    async def test_track_decorator_error(self, obs: AIObservability):
        @obs.track(agent_name="failing_agent", model="mistral", provider="ollama")
        async def failing_function():
            raise ValueError("Something went wrong")

        with pytest.raises(ValueError):
            await failing_function()

        errors = obs.get_most_common_errors()
        assert any(e["error_type"] == "ValueError" for e in errors)


class TestEdgeCases:
    """Edge case tests for observability."""

    def test_very_high_tokens(self, obs: AIObservability):
        obs.record_usage("briefing", 100000, 50000, "mistral", 30000, True, provider="ollama")
        result = obs.get_agent_usage("briefing")
        assert result["total_input_tokens"] == 100000
        assert result["total_output_tokens"] == 50000

    def test_empty_error_log(self, obs: AIObservability):
        common = obs.get_most_common_errors()
        assert common == []

    def test_no_records_latency_percentile(self, obs: AIObservability):
        result = obs.get_latency_percentiles("missing", [50, 99])
        assert result["samples"] == 0
        assert result["p50"] == 0.0
        assert result["p99"] == 0.0

    def test_no_records_slowest_agents(self, obs: AIObservability):
        slowest = obs.get_slowest_agents()
        assert slowest == []

    def test_errors_with_long_message_truncated(self, obs: AIObservability):
        long_msg = "x" * 1000
        obs.record_error("briefing", "Error", long_msg, provider="ollama")
        errors = list(obs._errors.get("briefing", []))
        assert len(errors[0]["error_message"]) <= 500
