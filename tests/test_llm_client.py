"""Tests for LLM Client — retry logic, fallback, circuit breaker, JSON parsing."""

import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.agent
class TestLLMClientInitialization:
    """Test LLMClient.__init__ reads settings correctly."""

    def test_init_reads_settings(self):
        with patch("ai.client.settings") as mock_settings:
            mock_settings.ollama_base_url = "http://custom:11434"
            mock_settings.claude_api_key = "sk-test-123"
            mock_settings.use_local_ai = False
            mock_settings.ollama_model = "llama3"
            mock_settings.claude_model = "claude-sonnet-4-20250514"
            mock_settings.ollama_timeout = 120
            mock_settings.claude_timeout = 90
            mock_settings.circuit_breaker_threshold = 3
            mock_settings.circuit_breaker_cooldown = 30

            from ai.client import LLMClient

            client = LLMClient()
            assert client.ollama_base == "http://custom:11434"
            assert client.claude_key == "sk-test-123"
            assert client.use_local is False
            assert client.model == "llama3"
            assert client.claude_model == "claude-sonnet-4-20250514"
            assert client.ollama_timeout == 120
            assert client.claude_timeout == 90
            assert client.max_retries == 3
            assert client.base_delay == 2.0
            assert client.ollama_circuit.failure_threshold == 3
            assert client.claude_circuit.recovery_timeout == 120


@pytest.mark.agent
class TestGetProviders:
    """Test _get_providers returns correct provider list."""

    @pytest.fixture
    def client(self):
        with patch("ai.client.LLMClient.__init__", return_value=None):
            from ai.client import LLMClient

            c = LLMClient()
            c.ollama_base = "http://localhost:11434"
            c.claude_key = None
            c.use_local = True
            c.model = "mistral"
            c.max_retries = 2
            c.base_delay = 0.01
            return c

    def test_local_only(self, client):
        client.use_local = True
        client.claude_key = None
        providers = client._get_providers()
        assert len(providers) == 1
        assert providers[0][0] == "ollama"

    def test_claude_only(self, client):
        client.use_local = False
        client.claude_key = "sk-test"
        providers = client._get_providers()
        assert len(providers) == 1
        assert providers[0][0] == "claude"

    def test_both_providers(self, client):
        client.use_local = True
        client.claude_key = "sk-test"
        providers = client._get_providers()
        assert len(providers) == 2
        assert providers[0][0] == "ollama"
        assert providers[1][0] == "claude"

    def test_fallback_to_ollama_when_none_configured(self, client):
        client.use_local = False
        client.claude_key = None
        providers = client._get_providers()
        assert len(providers) == 1
        assert providers[0][0] == "ollama"


@pytest.mark.agent
class TestLLMClientGenerate:
    """Test LLMClient.generate full flow."""

    @pytest.fixture
    def client(self):
        with patch("ai.client.LLMClient.__init__", return_value=None):
            from ai.client import LLMClient

            c = LLMClient()
            c.ollama_base = "http://localhost:11434"
            c.claude_key = "sk-test"
            c.use_local = True
            c.model = "mistral"
            c.claude_model = "claude-sonnet-4-20250514"
            c.max_retries = 2
            c.base_delay = 0.01
            c.ollama_timeout = 30
            c.claude_timeout = 30
            c.ollama_circuit = MagicMock()
            c.claude_circuit = MagicMock()
            c.ollama_circuit.call = AsyncMock(side_effect=lambda fn, *a, **kw: fn(*a, **kw))
            c.claude_circuit.call = AsyncMock(side_effect=lambda fn, *a, **kw: fn(*a, **kw))
            return c

    @pytest.fixture
    def client_ollama_only(self):
        """Client with only ollama (no claude_key) to avoid fallback interference."""
        with patch("ai.client.LLMClient.__init__", return_value=None):
            from ai.client import LLMClient

            c = LLMClient()
            c.ollama_base = "http://localhost:11434"
            c.claude_key = None
            c.use_local = True
            c.model = "mistral"
            c.max_retries = 2
            c.base_delay = 0.01
            c.ollama_timeout = 30
            c.claude_timeout = 30
            c.ollama_circuit = MagicMock()
            c.claude_circuit = MagicMock()
            c.ollama_circuit.call = AsyncMock(side_effect=lambda fn, *a, **kw: fn(*a, **kw))
            c.claude_circuit.call = AsyncMock(side_effect=lambda fn, *a, **kw: fn(*a, **kw))
            return c

    @pytest.mark.asyncio
    async def test_generate_calls_provider_and_returns_result(self, client_ollama_only):
        client_ollama_only._call_ollama = AsyncMock(return_value="response text")
        with patch("ai.client.cache") as mock_cache:
            mock_cache.get = AsyncMock(return_value=None)
            mock_cache.set = AsyncMock()
            result = await client_ollama_only.generate("test prompt")
        assert result == "response text"
        client_ollama_only._call_ollama.assert_awaited_once_with("test prompt", None, 1024, None)

    @pytest.mark.asyncio
    async def test_generate_passes_system_and_params(self, client_ollama_only):
        client_ollama_only._call_ollama = AsyncMock(return_value="resp")
        with patch("ai.client.cache") as mock_cache:
            mock_cache.get = AsyncMock(return_value=None)
            mock_cache.set = AsyncMock()
            result = await client_ollama_only.generate("prompt", system="sys", max_tokens=512, temperature=0.5)
        assert result == "resp"
        client_ollama_only._call_ollama.assert_awaited_once_with("prompt", "sys", 512, 0.5)

    @pytest.mark.asyncio
    async def test_provider_fallback_when_primary_fails(self, client):
        client._call_ollama = AsyncMock(side_effect=httpx.ReadTimeout("timeout"))
        client._call_claude = AsyncMock(return_value="claude response")
        with patch("ai.client.cache") as mock_cache:
            mock_cache.get = AsyncMock(return_value=None)
            mock_cache.set = AsyncMock()
            result = await client.generate("test")
        assert result == "claude response"
        client._call_claude.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_retries_on_timeout(self, client_ollama_only):
        call_count = 0

        async def fail_once(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise httpx.ReadTimeout("timed out")
            return "final response"

        client_ollama_only._call_ollama = fail_once
        with patch("ai.client.cache") as mock_cache:
            mock_cache.get = AsyncMock(return_value=None)
            mock_cache.set = AsyncMock()
            result = await client_ollama_only.generate("test")
        assert result == "final response"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_retries_on_http_status_error(self, client_ollama_only):
        call_count = 0

        async def fail_once(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 1:
                mock_resp = MagicMock(spec=httpx.Response)
                mock_resp.status_code = 500
                raise httpx.HTTPStatusError("Server error", request=MagicMock(spec=httpx.Request), response=mock_resp)
            return "recovered"

        client_ollama_only._call_ollama = fail_once
        with patch("ai.client.cache") as mock_cache:
            mock_cache.get = AsyncMock(return_value=None)
            mock_cache.set = AsyncMock()
            result = await client_ollama_only.generate("test")
        assert result == "recovered"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_all_retries_exhausted_raises_provider_unavailable(self, client_ollama_only):
        client_ollama_only._call_ollama = AsyncMock(side_effect=httpx.ReadTimeout("always timeout"))
        from ai.client import LLMProviderUnavailableError

        with patch("ai.client.cache") as mock_cache:
            mock_cache.get = AsyncMock(return_value=None)
            with pytest.raises(LLMProviderUnavailableError, match="All AI providers failed"):
                await client_ollama_only.generate("test")

    @pytest.mark.asyncio
    async def test_unexpected_error_retries(self, client_ollama_only):
        call_count = 0

        async def fail_then_ok(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 1:
                raise RuntimeError("unexpected")
            return "ok"

        client_ollama_only._call_ollama = fail_then_ok
        with patch("ai.client.cache") as mock_cache:
            mock_cache.get = AsyncMock(return_value=None)
            mock_cache.set = AsyncMock()
            result = await client_ollama_only.generate("test")
        assert result == "ok"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_rate_limit_retries_after_delay(self, client_ollama_only):
        call_count = 0

        from ai.client import LLMRateLimitError

        async def rate_limit_then_ok(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 1:
                raise LLMRateLimitError("rate limited", retry_after=1)
            return "ok"

        client_ollama_only._call_ollama = rate_limit_then_ok
        with patch("ai.client.cache") as mock_cache:
            mock_cache.get = AsyncMock(return_value=None)
            mock_cache.set = AsyncMock()
            result = await client_ollama_only.generate("test")
        assert result == "ok"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_circuit_breaker_open_breaks_to_next_provider(self, client):
        from shared.utils.retry import CircuitBreakerOpenError

        client._call_ollama = AsyncMock(side_effect=CircuitBreakerOpenError("OPEN"))
        client._call_claude = AsyncMock(return_value="claude rescued")
        with patch("ai.client.cache") as mock_cache:
            mock_cache.get = AsyncMock(return_value=None)
            mock_cache.set = AsyncMock()
            result = await client.generate("test")
        assert result == "claude rescued"

    @pytest.mark.asyncio
    async def test_provider_unavailable_breaks_to_next_provider(self, client):
        from ai.client import LLMProviderUnavailableError

        client._call_ollama = AsyncMock(side_effect=LLMProviderUnavailableError("down"))
        client._call_claude = AsyncMock(return_value="claude fallback")
        with patch("ai.client.cache") as mock_cache:
            mock_cache.get = AsyncMock(return_value=None)
            mock_cache.set = AsyncMock()
            result = await client.generate("test")
        assert result == "claude fallback"

    @pytest.mark.asyncio
    async def test_generate_with_system_prompt(self, client_ollama_only):
        client_ollama_only._call_ollama = AsyncMock(return_value="response")
        with patch("ai.client.cache") as mock_cache:
            mock_cache.get = AsyncMock(return_value=None)
            mock_cache.set = AsyncMock()
            result = await client_ollama_only.generate("hello", system="Be concise")
        assert result == "response"
        client_ollama_only._call_ollama.assert_awaited_once_with("hello", "Be concise", 1024, None)

    @pytest.mark.asyncio
    async def test_generate_with_temperature(self, client_ollama_only):
        client_ollama_only._call_ollama = AsyncMock(return_value="resp")
        with patch("ai.client.cache") as mock_cache:
            mock_cache.get = AsyncMock(return_value=None)
            mock_cache.set = AsyncMock()
            result = await client_ollama_only.generate("hi", temperature=0.9)
        assert result == "resp"
        client_ollama_only._call_ollama.assert_awaited_once_with("hi", None, 1024, 0.9)


@pytest.mark.agent
class TestLLMClientCache:
    """Test LLMClient.generate cache interaction."""

    @pytest.fixture
    def client(self):
        with patch("ai.client.LLMClient.__init__", return_value=None):
            from ai.client import LLMClient

            c = LLMClient()
            c.ollama_base = "http://localhost:11434"
            c.claude_key = None
            c.use_local = True
            c.model = "mistral"
            c.max_retries = 2
            c.base_delay = 0.01
            c.ollama_circuit = MagicMock()
            c.ollama_circuit.call = AsyncMock(side_effect=lambda fn, *a, **kw: fn(*a, **kw))
            return c

    @pytest.mark.asyncio
    async def test_cache_hit_returns_cached(self, client):
        with patch("ai.client.cache") as mock_cache:
            mock_cache.get = AsyncMock(return_value="cached response")
            client._call_ollama = AsyncMock(return_value="fresh response")
            result = await client.generate("test prompt")
            assert result == "cached response"
            client._call_ollama.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_cache_miss_calls_provider_and_caches(self, client):
        with patch("ai.client.cache") as mock_cache:
            mock_cache.get = AsyncMock(return_value=None)
            mock_cache.set = AsyncMock()
            client._call_ollama = AsyncMock(return_value="fresh response")
            result = await client.generate("test prompt")
            assert result == "fresh response"
            mock_cache.set.assert_awaited_once()


@pytest.mark.agent
class TestJSONParsingEdgeCases:
    """Test JSON extraction from LLM output edge cases."""

    @pytest.fixture
    def client(self):
        with patch("ai.client.LLMClient.__init__", return_value=None):
            from ai.client import LLMClient

            return LLMClient()

    def test_partial_json_still_extracts(self, client):
        text = 'Here is: {"key": "value", "nested": {"inner": 42}} trailing'
        result = client._extract_json(text)
        assert result is not None
        assert result["key"] == "value"
        assert result["nested"]["inner"] == 42

    def test_json_with_extra_chars_after_brace(self, client):
        text = '{"valid": true} and some text after'
        result = client._extract_json(text)
        assert result is not None
        assert result["valid"] is True

    def test_nested_json_objects(self, client):
        text = '{"outer": {"inner": [1, 2, 3]}, "status": "ok"}'
        result = client._extract_json(text)
        assert result["outer"]["inner"] == [1, 2, 3]

    def test_json_array_at_top_level(self, client):
        text = '[{"a": 1}, {"b": 2}]'
        result = client._extract_json(text)
        assert result is not None
        assert "items" in result
        assert len(result["items"]) == 2

    def test_json_with_text_after_closing_brace(self, client):
        text = '{"valid": "data"} and then some trailing text'
        result = client._extract_json(text)
        assert result is not None
        assert result["valid"] == "data"

    def test_empty_json_object(self, client):
        result = client._extract_json("{}")
        assert result == {}

    def test_markdown_code_block_no_language(self, client):
        text = '```\n{"key": "value"}\n```'
        result = client._extract_json(text)
        assert result is not None
        assert result["key"] == "value"

    @pytest.mark.asyncio
    async def test_generate_json_handles_list_result(self, client):
        client.generate = AsyncMock(return_value='[{"task": "write"}, {"task": "test"}]')
        result = await client.generate_json("list me")
        assert isinstance(result, dict)
        assert "items" in result
        assert len(result["items"]) == 2

    @pytest.mark.asyncio
    async def test_generate_json_handles_plain_string(self, client):
        client.generate = AsyncMock(return_value='"just a string"')
        result = await client.generate_json("say something")
        assert "raw" in result

    @pytest.mark.asyncio
    async def test_generate_json_with_multiline_markdown(self, client):
        client.generate = AsyncMock(
            return_value='Here is the result:\n\n```json\n{\n  "items": [\n    {"id": 1}\n  ]\n}\n```'
        )
        result = await client.generate_json("test")
        assert result["items"][0]["id"] == 1

    def test_extract_empty_square_brackets(self, client):
        result = client._extract_json("[]")
        assert result == {"items": []}

    def test_extract_non_json_with_brackets(self, client):
        result = client._extract_json("This {has brackets} but is not json")
        assert result is None

    def test_extract_with_escaped_quotes(self, client):
        text = '{"key": "value with \\"escaped\\" quotes"}'
        result = client._extract_json(text)
        assert result is not None
        assert "escaped" in result["key"]


@pytest.mark.agent
class TestCallOllama:
    """Test _call_ollama HTTP behavior."""

    @pytest.fixture
    def client(self):
        with patch("ai.client.LLMClient.__init__", return_value=None):
            from ai.client import LLMClient

            c = LLMClient()
            c.ollama_base = "http://localhost:11434"
            c.model = "mistral"
            c.ollama_timeout = 30
            c.use_local = True
            c.ollama_circuit = MagicMock()

            # circuit.call must actually await the wrapped function
            async def circuit_call(fn, *a, **kw):
                return await fn(*a, **kw)

            c.ollama_circuit.call = AsyncMock(side_effect=circuit_call)
            return c

    @pytest.mark.asyncio
    async def test_call_ollama_success(self, client):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"response": "ollama reply"}
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_http:
            mock_http.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_resp)
            result = await client._call_ollama("test prompt", system="Be helpful", max_tokens=512, temperature=0.7)
            assert result == "ollama reply"

    @pytest.mark.asyncio
    async def test_call_ollama_no_system_no_temp(self, client):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"response": "simple"}
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_http:
            mock_http.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_resp)
            result = await client._call_ollama("hello")
            assert result == "simple"

    @pytest.mark.asyncio
    async def test_call_ollama_empty_response(self, client):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {}
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_http:
            mock_http.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_resp)
            result = await client._call_ollama("test")
            assert result == ""


@pytest.mark.agent
class TestCallClaude:
    """Test _call_claude HTTP behavior."""

    @pytest.fixture
    def client(self):
        with patch("ai.client.LLMClient.__init__", return_value=None):
            from ai.client import LLMClient

            c = LLMClient()
            c.claude_key = "sk-ant-test"
            c.claude_model = "claude-sonnet-4-20250514"
            c.claude_timeout = 60
            c.use_local = False
            c.claude_circuit = MagicMock()

            async def circuit_call(fn, *a, **kw):
                return await fn(*a, **kw)

            c.claude_circuit.call = AsyncMock(side_effect=circuit_call)
            return c

    @pytest.mark.asyncio
    async def test_call_claude_success(self, client):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"content": [{"text": "claude response"}]}
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_http:
            mock_http.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_resp)
            result = await client._call_claude("prompt", system="sys", max_tokens=2048, temperature=0.5)
            assert result == "claude response"

    @pytest.mark.asyncio
    async def test_call_claude_rate_limited(self, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_resp.headers = {"retry-after": "30"}
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_http:
            mock_http.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_resp)
            from ai.client import LLMRateLimitError

            with pytest.raises(LLMRateLimitError, match="Claude rate limited"):
                await client._call_claude("test")

    @pytest.mark.asyncio
    async def test_call_claude_with_system_and_temp(self, client):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"content": [{"text": "resp"}]}
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_http:
            mock_http.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_resp)
            result = await client._call_claude("hi", system="You are helpful", max_tokens=1024, temperature=0.8)
            assert result == "resp"


@pytest.mark.agent
class TestLLMClientCircuitBreakerTransitions:
    """Test circuit breaker state transitions within LLMClient context."""

    @pytest.mark.asyncio
    async def test_client_circuit_breaker_tracks_ollama_failures(self):
        with patch("ai.client.settings") as mock_settings:
            mock_settings.ollama_base_url = "http://localhost:11434"
            mock_settings.claude_api_key = None
            mock_settings.use_local_ai = True
            mock_settings.ollama_model = "mistral"
            mock_settings.claude_model = "claude-sonnet-4-20250514"
            mock_settings.ollama_timeout = 1
            mock_settings.claude_timeout = 1
            mock_settings.circuit_breaker_threshold = 2
            mock_settings.circuit_breaker_cooldown = 60

            from ai.client import LLMClient

            client = LLMClient()
            assert client.ollama_circuit.state == "closed"
            assert client.ollama_circuit.failure_count == 0
            assert client.ollama_circuit.failure_threshold == 2

    @pytest.mark.asyncio
    async def test_circuit_transitions_closed_to_open(self):
        from shared.utils.retry import CircuitBreaker
        import httpx

        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=60, expected_exception=(httpx.RequestError,))

        async def fail():
            raise httpx.ReadTimeout("fail")

        assert cb.state == "closed"
        with pytest.raises(httpx.ReadTimeout):
            await cb.call(fail)
        assert cb.state == "closed"
        assert cb.failure_count == 1

        with pytest.raises(httpx.ReadTimeout):
            await cb.call(fail)
        assert cb.state == "open"
        assert cb.failure_count == 2

    @pytest.mark.asyncio
    async def test_circuit_open_to_half_open_to_closed(self):
        from shared.utils.retry import CircuitBreaker
        import asyncio
        import httpx

        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1, expected_exception=(httpx.RequestError,))

        async def fail():
            raise httpx.ReadTimeout("fail")

        with pytest.raises(httpx.RequestError):
            await cb.call(fail)
        with pytest.raises(httpx.RequestError):
            await cb.call(fail)
        assert cb.state == "open"

        await asyncio.sleep(0.15)

        async def succeed():
            return "ok"

        result = await cb.call(succeed)
        assert result == "ok"
        assert cb.state == "closed"

    @pytest.mark.asyncio
    async def test_circuit_open_rejects_fast(self):
        from shared.utils.retry import CircuitBreaker, CircuitBreakerOpenError
        import httpx

        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=3600, expected_exception=(httpx.RequestError,))

        async def fail():
            raise httpx.ReadTimeout("fail")

        with pytest.raises(httpx.RequestError):
            await cb.call(fail)
        assert cb.state == "open"

        with pytest.raises(CircuitBreakerOpenError, match="Circuit breaker is OPEN"):
            await cb.call(lambda: "should not run")

    @pytest.mark.asyncio
    async def test_circuit_half_open_failure_goes_back_to_open(self):
        from shared.utils.retry import CircuitBreaker
        import asyncio
        import httpx

        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1, expected_exception=(httpx.RequestError,))

        async def fail():
            raise httpx.ReadTimeout("fail")

        with pytest.raises(httpx.RequestError):
            await cb.call(fail)
        with pytest.raises(httpx.RequestError):
            await cb.call(fail)
        assert cb.state == "open"

        await asyncio.sleep(0.15)

        # half-open, but fails again
        with pytest.raises(httpx.RequestError):
            await cb.call(fail)
        assert cb.state == "open"


@pytest.mark.agent
class TestLLMErrorClasses:
    """Test custom LLM error classes."""

    def test_llm_error_base(self):
        from ai.client import LLMError

        err = LLMError("base error")
        assert str(err) == "base error"

    def test_llm_timeout_error(self):
        from ai.client import LLMTimeoutError

        err = LLMTimeoutError("timed out")
        assert isinstance(err, Exception)

    def test_llm_rate_limit_error(self):
        from ai.client import LLMRateLimitError

        err = LLMRateLimitError("rate limited", retry_after=120)
        assert err.retry_after == 120

    def test_llm_provider_unavailable_error(self):
        from ai.client import LLMProviderUnavailableError

        err = LLMProviderUnavailableError("down")
        assert isinstance(err, Exception)

    def test_rate_limit_error_default_retry_after(self):
        from ai.client import LLMRateLimitError

        err = LLMRateLimitError("limited")
        assert err.retry_after == 60


@pytest.mark.agent
class TestLLMClientEdgeCases:
    """Test edge cases in generate_json and related methods."""

    @pytest.fixture
    def client(self):
        with patch("ai.client.LLMClient.__init__", return_value=None):
            from ai.client import LLMClient

            return LLMClient()

    @pytest.mark.asyncio
    async def test_generate_json_handles_partial_extracted(self, client):
        client.generate = AsyncMock(return_value='Some prefix {"partial": true} and suffix')
        result = await client.generate_json("test")
        assert result["partial"] is True

    @pytest.mark.asyncio
    async def test_generate_json_handles_broken_json_with_extract(self, client):
        client.generate = AsyncMock(return_value='```json\n{\n  "broken": true\n}\n```')
        result = await client.generate_json("test")
        assert result["broken"] is True

    @pytest.mark.asyncio
    async def test_generate_json_list_with_items(self, client):
        client.generate = AsyncMock(return_value='[{"x": 1}, {"x": 2}]')
        result = await client.generate_json("test")
        assert result["items"][0]["x"] == 1
        assert result["items"][1]["x"] == 2

    @pytest.mark.asyncio
    async def test_generate_json_dict_result(self, client):
        client.generate = AsyncMock(return_value='{"key": "value"}')
        result = await client.generate_json("test")
        assert result["key"] == "value"

    @pytest.mark.asyncio
    async def test_generate_json_total_parse_failure(self, client):
        client.generate = AsyncMock(return_value="some random text")
        result = await client.generate_json("test")
        assert result["parse_error"] is True

    @pytest.mark.asyncio
    async def test_record_usage_httpx_error(self, client):
        client._api_base = "http://localhost:8000"
        with patch("httpx.AsyncClient.post", side_effect=Exception("Connection refused")):
            await client._record_usage(
                agent="test_agent",
                model="ollama/mistral:7b",
                provider="ollama",
                prompt_tokens=100,
                completion_tokens=50,
                duration_ms=500,
            )

    @pytest.mark.asyncio
    async def test_record_usage_zero_tokens_skips(self, client):
        client._api_base = "http://localhost:8000"
        with patch("httpx.AsyncClient.post") as mock_post:
            await client._record_usage(
                agent="test_agent",
                model="ollama/mistral:7b",
                provider="ollama",
                prompt_tokens=0,
                completion_tokens=0,
                duration_ms=0,
            )
            mock_post.assert_not_called()
