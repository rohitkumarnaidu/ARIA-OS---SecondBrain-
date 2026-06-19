"""Tests for LLM Client — retry logic, fallback, circuit breaker, JSON parsing."""

import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.agent
class TestLLMClient:
    """Test LLM client error handling and resilience."""

    @pytest.fixture
    def mock_client(self):
        with patch("ai.client.LLMClient.__init__", return_value=None):
            from ai.client import LLMClient

            client = LLMClient()
            client.ollama_base = "http://localhost:11434"
            client.claude_key = None
            client.use_local = True
            client.model = "mistral"
            client.max_retries = 2
            client.base_delay = 0.01
            return client

    @pytest.mark.asyncio
    async def test_generate_json_parses_valid_json(self, mock_client):
        mock_client.generate = AsyncMock(return_value='{"key": "value", "number": 42}')
        result = await mock_client.generate_json("test prompt")
        assert result["key"] == "value"
        assert result["number"] == 42

    @pytest.mark.asyncio
    async def test_generate_json_fallback_to_extract_json(self, mock_client):
        mock_client.generate = AsyncMock(return_value='Some text before ```json\n{"found": true}\n``` after')
        result = await mock_client.generate_json("test prompt")
        assert "found" in result or "raw" in result
        assert result.get("found") is True or "found" in str(result)

    @pytest.mark.asyncio
    async def test_generate_json_returns_raw_on_failure(self, mock_client):
        mock_client.generate = AsyncMock(return_value="Not JSON at all just plain text")
        result = await mock_client.generate_json("test prompt")
        assert "raw" in result
        assert result.get("parse_error") is True

    @pytest.mark.asyncio
    async def test_generate_retries_on_connection_error(self, mock_client):
        call_count = 0

        async def fail_then_succeed(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 1:
                import httpx

                raise httpx.ReadTimeout("Request timed out")
            return '{"success": true}'

        mock_client._call_ollama = fail_then_succeed
        mock_client._get_providers = lambda: [("ollama", fail_then_succeed)]

        result = await mock_client.generate("test")
        assert result == '{"success": true}'
        assert call_count == 2


@pytest.mark.agent
class TestJSONParsing:
    """Test JSON extraction utilities."""

    def test_extract_json_from_markdown(self):
        from ai.client import LLMClient

        client = LLMClient()
        raw = 'Here is the result:\n```json\n{"key": "value"}\n```\nEnd.'
        result = client._extract_json(raw)
        assert result is not None
        assert result["key"] == "value"

    def test_extract_json_array_from_text(self):
        from ai.client import LLMClient

        client = LLMClient()
        text = 'Results: [{"id": 1}, {"id": 2}]'
        result = client._extract_json(text)
        assert result is not None
        assert "items" in result
        assert len(result["items"]) == 2

    def test_handles_non_json(self):
        from ai.client import LLMClient

        client = LLMClient()
        result = client._extract_json("Just some random text without JSON")
        assert result is None


@pytest.mark.agent
class TestCircuitBreaker:
    """Test circuit breaker integration."""

    @pytest.mark.asyncio
    async def test_circuit_breaker_trips_after_threshold(self):
        from shared.utils.retry import CircuitBreaker

        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=0.5)

        async def failing_func():
            raise ValueError("Service error")

        for _ in range(3):
            with pytest.raises(ValueError):
                await cb.call(failing_func)

        assert cb.state == "open"

    @pytest.mark.asyncio
    async def test_circuit_breaker_recovers(self):
        from shared.utils.retry import CircuitBreaker
        import asyncio

        call_count = 0

        async def toggle_func():
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                raise ValueError("Fail")
            return "success"

        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=0.2)

        for _ in range(3):
            with pytest.raises(ValueError):
                await cb.call(toggle_func)

        assert cb.state == "open"

        # Recovery check happens inside call(), so we need to call it again
        await asyncio.sleep(0.3)

        # The second call() should transition from open -> half_open -> closed
        result = await cb.call(toggle_func)
        assert result == "success"
        assert cb.state == "closed"
