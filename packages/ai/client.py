import json
import asyncio
import hashlib
import time as _time
from typing import Optional, Dict, Any, List, Tuple, Callable
import httpx
from config.core.config import settings
from shared.utils.logger import logger
from shared.utils.retry import CircuitBreaker, CircuitBreakerOpenError
from shared.utils.cache import cache


class LLMError(Exception):
    pass


class LLMTimeoutError(LLMError):
    pass


class LLMRateLimitError(LLMError):
    def __init__(self, message: str, retry_after: int = 60):
        super().__init__(message)
        self.retry_after = retry_after


class LLMProviderUnavailableError(LLMError):
    pass


class LLMClient:
    def __init__(self):
        self.ollama_base = settings.ollama_base_url
        self.claude_key = settings.claude_api_key
        self.use_local = settings.use_local_ai
        self.model = settings.ollama_model
        self.claude_model = settings.claude_model

        self.ollama_timeout = settings.ollama_timeout
        self.claude_timeout = settings.claude_timeout

        self.max_retries = 3
        self.base_delay = 2.0

        self.ollama_circuit = CircuitBreaker(
            failure_threshold=settings.circuit_breaker_threshold,
            recovery_timeout=settings.circuit_breaker_cooldown,
            expected_exception=(LLMTimeoutError, httpx.RequestError),
        )
        self.claude_circuit = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=120,
            expected_exception=(LLMRateLimitError, httpx.RequestError),
        )

        self._last_token_usage = {}
        self._api_base = f"http://localhost:{settings.api_port if hasattr(settings, 'api_port') else 8000}"

    def _get_providers(self) -> List[Tuple[str, Callable]]:
        providers = []
        if self.use_local:
            providers.append(("ollama", self._call_ollama))
        if self.claude_key:
            providers.append(("claude", self._call_claude))
        if not providers:
            providers.append(("ollama", self._call_ollama))
        return providers

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: Optional[float] = None,
        agent_name: str = "unknown",
    ) -> str:
        raw_key = f"{prompt}||{system}||{max_tokens}||{temperature}"
        cache_key = "llm:" + hashlib.sha256(raw_key.encode()).hexdigest()
        cached_result = await cache.get(cache_key)
        if cached_result is not None:
            logger.info("LLM cache hit", length=len(cached_result))
            return cached_result

        last_error = None
        providers = self._get_providers()
        start_time = _time.time()

        for name, provider_fn in providers:
            for attempt in range(1, self.max_retries + 1):
                try:
                    logger.debug(
                        "LLM request",
                        provider=name,
                        attempt=attempt,
                        max_tokens=max_tokens,
                    )
                    result = await provider_fn(prompt, system, max_tokens, temperature)
                    duration_ms = int((_time.time() - start_time) * 1000)
                    logger.info(
                        "LLM success",
                        provider=name,
                        attempt=attempt,
                        tokens=len(result.split()),
                    )
                    await cache.set(cache_key, result, ttl=300)

                    token_usage = getattr(self, "_last_token_usage", {})
                    asyncio.create_task(
                        self._record_usage(
                            agent=agent_name,
                            model=self.model if name == "ollama" else self.claude_model,
                            provider=name,
                            prompt_tokens=token_usage.get("prompt_tokens", 0),
                            completion_tokens=token_usage.get("completion_tokens", 0),
                            duration_ms=duration_ms,
                        )
                    )
                    return result
                except (LLMProviderUnavailableError, CircuitBreakerOpenError) as e:
                    logger.warn(
                        "Provider unavailable",
                        provider=name,
                        error=str(e),
                    )
                    last_error = e
                    break
                except LLMRateLimitError as e:
                    logger.warn(
                        "Rate limited by provider",
                        provider=name,
                        retry_after=e.retry_after,
                    )
                    last_error = e
                    await asyncio.sleep(min(e.retry_after, 30))
                except (LLMTimeoutError, httpx.RequestError, httpx.HTTPStatusError) as e:
                    last_error = e
                    delay = self.base_delay * (2 ** (attempt - 1))
                    logger.warn(
                        "LLM provider error",
                        provider=name,
                        attempt=attempt,
                        error=str(e),
                        next_retry_delay=delay,
                    )
                    if attempt < self.max_retries:
                        await asyncio.sleep(delay)
                except Exception as e:
                    last_error = e
                    logger.error(
                        "LLM unexpected error",
                        provider=name,
                        error_type=type(e).__name__,
                    )
                    if attempt < self.max_retries:
                        await asyncio.sleep(self.base_delay)

        logger.error("All LLM providers exhausted", last_error=str(last_error))
        raise LLMProviderUnavailableError(f"All AI providers failed. Last error: {last_error}") from last_error

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        for opener, closer in [("{", "}"), ("[", "]")]:
            try:
                start = text.index(opener)
                end = text.rindex(closer) + 1
                parsed = json.loads(text[start:end])
                if isinstance(parsed, dict):
                    return parsed
                if isinstance(parsed, list):
                    return {"items": parsed}
            except (ValueError, json.JSONDecodeError):
                continue
        return None

    async def _call_ollama(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: Optional[float] = None,
    ) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": max_tokens},
        }
        if temperature is not None:
            payload["options"]["temperature"] = temperature
        if system:
            payload["system"] = system

        async def do_call():
            async with httpx.AsyncClient(timeout=self.ollama_timeout) as client:
                resp = await client.post(f"{self.ollama_base}/api/generate", json=payload)
                resp.raise_for_status()
                data = resp.json()
                self._last_token_usage = {
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                }
                return data.get("response", "")

        return await self.ollama_circuit.call(do_call)

    async def _call_claude(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: Optional[float] = None,
    ) -> str:
        headers = {
            "x-api-key": self.claude_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": self.claude_model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if temperature is not None:
            payload["temperature"] = temperature
        if system:
            payload["system"] = system

        async def do_call():
            async with httpx.AsyncClient(timeout=self.claude_timeout) as client:
                resp = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    json=payload,
                    headers=headers,
                )
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("retry-after", 60))
                    raise LLMRateLimitError("Claude rate limited", retry_after=retry_after)
                resp.raise_for_status()
                data = resp.json()
                usage = data.get("usage", {})
                self._last_token_usage = {
                    "prompt_tokens": usage.get("input_tokens", 0),
                    "completion_tokens": usage.get("output_tokens", 0),
                }
                return data["content"][0]["text"]

        return await self.claude_circuit.call(do_call)

    async def _record_usage(
        self,
        agent: str,
        model: str,
        provider: str,
        prompt_tokens: int,
        completion_tokens: int,
        duration_ms: int,
    ):
        if prompt_tokens == 0 and completion_tokens == 0:
            return
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                await client.post(
                    f"{self._api_base}/api/v1/monitoring/token-usage",
                    json={
                        "agent": agent,
                        "model": model,
                        "provider": provider,
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "duration_ms": duration_ms,
                        "endpoint": f"llm:{provider}",
                    },
                )
        except Exception:
            pass

    async def generate_json(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: Optional[float] = None,
        agent_name: str = "unknown",
    ) -> Dict[str, Any]:
        raw = await self.generate(prompt, system, max_tokens, temperature, agent_name=agent_name)
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
            if isinstance(parsed, list):
                return {"items": parsed}
            return {"raw": raw}
        except json.JSONDecodeError:
            extracted = self._extract_json(raw)
            if extracted is not None:
                return extracted
            logger.warn("Failed to parse LLM output as JSON", preview=raw[:200])
            return {"raw": raw, "parse_error": True}


llm = LLMClient()
