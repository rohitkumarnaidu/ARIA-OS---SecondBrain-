import json
import asyncio
import hashlib
import time as _time
from typing import Optional, Dict, Any, List, Tuple, Callable, AsyncGenerator
import httpx
from config.core.config import settings
from shared.utils.logger import logger
from shared.utils.retry import CircuitBreaker, CircuitBreakerOpenError
from shared.utils.cache import cache
from shared.utils.ai_cache import ai_cache
from ai.guardrails import guardrails
from ai.observability import observability


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
        model = self.model
        system_prompt = system or ""

        # Check AI semantic cache (L1)
        cached = ai_cache.get(system_prompt, prompt, model)
        if cached is not None:
            logger.debug("AI cache HIT", model=model, prompt_len=len(prompt))
            return cached

        # Check existing SimpleCache (L2 - fast exact match)
        raw_key = f"{prompt}||{system}||{max_tokens}||{temperature}"
        cache_key = "llm:" + hashlib.sha256(raw_key.encode()).hexdigest()
        cached_result = await cache.get(cache_key)
        if cached_result is not None:
            logger.info("LLM cache hit", length=len(cached_result))
            return cached_result

        guard_result = guardrails.validate_input(prompt)
        if not guard_result["safe"]:
            logger.warn(
                "Input validation failed",
                agent=agent_name,
                issues=guard_result["issues"],
                risk_score=guard_result["risk_score"],
            )
            return f"I'm unable to process that request. Reason: {guard_result['issues'][0] if guard_result['issues'] else 'Content policy violation.'}"

        sanitized_prompt = guardrails.sanitize_input(prompt)
        sanitized_system = guardrails.sanitize_input(system_prompt) if system_prompt else ""

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
                    result = await provider_fn(sanitized_prompt, sanitized_system, max_tokens, temperature)
                    duration_ms = int((_time.time() - start_time) * 1000)

                    safe_output = guardrails.sanitize_output(result)
                    output_validation = guardrails.validate_output(safe_output, input_text=sanitized_prompt)
                    if not output_validation["safe"]:
                        logger.warn(
                            "Output validation flagged",
                            agent=agent_name,
                            provider=name,
                            issues=output_validation["issues"],
                            risk_score=output_validation["risk_score"],
                        )

                    logger.info(
                        "LLM success",
                        provider=name,
                        attempt=attempt,
                        tokens=len(result.split()),
                    )

                    estimated_tokens = len(sanitized_prompt) // 4 + len(safe_output) // 4
                    ai_cache.set(system_prompt, prompt, model, safe_output, estimated_tokens)
                    await cache.set(cache_key, safe_output, ttl=300)

                    token_usage = getattr(self, "_last_token_usage", {})
                    prompt_tokens = token_usage.get("prompt_tokens", 0)
                    completion_tokens = token_usage.get("completion_tokens", 0)
                    asyncio.create_task(
                        self._record_usage(
                            agent=agent_name,
                            model=self.model if name == "ollama" else self.claude_model,
                            provider=name,
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                            duration_ms=duration_ms,
                        )
                    )
                    observability.record_usage(
                        agent_name=agent_name,
                        input_tokens=prompt_tokens or len(sanitized_prompt) // 4,
                        output_tokens=completion_tokens or len(safe_output) // 4,
                        model=self.model if name == "ollama" else self.claude_model,
                        duration_ms=duration_ms,
                        success=True,
                        provider=name,
                    )
                    observability.record_latency(agent_name, duration_ms, endpoint="generate")
                    return safe_output
                except (LLMProviderUnavailableError, CircuitBreakerOpenError) as e:
                    logger.warn(
                        "Provider unavailable",
                        provider=name,
                        error=str(e),
                    )
                    observability.record_error(agent_name, type(e).__name__, str(e), provider=name)
                    last_error = e
                    break
                except LLMRateLimitError as e:
                    logger.warn(
                        "Rate limited by provider",
                        provider=name,
                        retry_after=e.retry_after,
                    )
                    observability.record_error(agent_name, "LLMRateLimitError", str(e), provider=name)
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
                    observability.record_error(agent_name, type(e).__name__, str(e), provider=name)
                    if attempt < self.max_retries:
                        await asyncio.sleep(delay)
                except Exception as e:
                    last_error = e
                    logger.error(
                        "LLM unexpected error",
                        provider=name,
                        error_type=type(e).__name__,
                    )
                    observability.record_error(agent_name, type(e).__name__, str(e), provider=name)
                    if attempt < self.max_retries:
                        await asyncio.sleep(self.base_delay)

        observability.record_error(agent_name, "LLMProviderUnavailableError", f"All providers failed: {last_error}", provider="all")
        logger.error("All LLM providers exhausted", last_error=str(last_error))
        raise LLMProviderUnavailableError(f"All AI providers failed. Last error: {last_error}") from last_error

    async def generate_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: Optional[float] = None,
        agent_name: str = "unknown",
        on_token: Optional[Callable[[str], Any]] = None,
        signal: Optional[asyncio.Event] = None,
    ) -> AsyncGenerator[str, None]:
        guard_result = guardrails.validate_input(prompt)
        if not guard_result["safe"]:
            logger.warn(
                "Input validation failed for stream",
                agent=agent_name,
                issues=guard_result["issues"],
                risk_score=guard_result["risk_score"],
            )
            yield f"I'm unable to process that request. Reason: {guard_result['issues'][0] if guard_result['issues'] else 'Content policy violation.'}"
            return

        sanitized_prompt = guardrails.sanitize_input(prompt)
        sanitized_system = guardrails.sanitize_input(system) if system else ""

        last_error = None
        providers = self._get_providers()
        start_time = _time.time()
        full_text_parts: List[str] = []

        for name, _ in providers:
            for attempt in range(1, self.max_retries + 1):
                try:
                    if signal and signal.is_set():
                        return

                    logger.debug("LLM stream request", provider=name, attempt=attempt, max_tokens=max_tokens)

                    if name == "ollama":
                        gen = self._call_ollama_stream(sanitized_prompt, sanitized_system, max_tokens, temperature, signal)
                    else:
                        gen = self._call_claude_stream(sanitized_prompt, sanitized_system, max_tokens, temperature, signal)

                    async for token in gen:
                        if signal and signal.is_set():
                            return
                        safe_token = guardrails.sanitize_output(token)
                        if on_token:
                            maybe = on_token(safe_token)
                            if asyncio.iscoroutine(maybe):
                                await maybe
                        full_text_parts.append(safe_token)
                        yield safe_token

                    duration_ms = int((_time.time() - start_time) * 1000)
                    full_text = "".join(full_text_parts)

                    output_validation = guardrails.validate_output(full_text, input_text=sanitized_prompt)
                    if not output_validation["safe"]:
                        logger.warn(
                            "Output validation flagged in stream",
                            agent=agent_name,
                            provider=name,
                            issues=output_validation["issues"],
                        )

                    token_usage = getattr(self, "_last_token_usage", {})
                    prompt_tokens = token_usage.get("prompt_tokens", 0)
                    completion_tokens = token_usage.get("completion_tokens", 0)
                    asyncio.create_task(
                        self._record_usage(
                            agent=agent_name,
                            model=self.model if name == "ollama" else self.claude_model,
                            provider=name,
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                            duration_ms=duration_ms,
                        )
                    )
                    observability.record_usage(
                        agent_name=agent_name,
                        input_tokens=prompt_tokens or len(sanitized_prompt) // 4,
                        output_tokens=completion_tokens or len(full_text) // 4,
                        model=self.model if name == "ollama" else self.claude_model,
                        duration_ms=duration_ms,
                        success=True,
                        provider=name,
                    )
                    observability.record_latency(agent_name, duration_ms, endpoint="generate_stream")
                    return

                except (LLMProviderUnavailableError, CircuitBreakerOpenError) as e:
                    logger.warn("Provider unavailable for stream", provider=name, error=str(e))
                    observability.record_error(agent_name, type(e).__name__, str(e), provider=name)
                    last_error = e
                    break
                except LLMRateLimitError as e:
                    logger.warn("Rate limited during stream", provider=name, retry_after=e.retry_after)
                    observability.record_error(agent_name, "LLMRateLimitError", str(e), provider=name)
                    last_error = e
                    await asyncio.sleep(min(e.retry_after, 30))
                except (LLMTimeoutError, httpx.RequestError, httpx.HTTPStatusError) as e:
                    last_error = e
                    delay = self.base_delay * (2 ** (attempt - 1))
                    logger.warn("LLM stream error", provider=name, attempt=attempt, error=str(e), next_retry_delay=delay)
                    observability.record_error(agent_name, type(e).__name__, str(e), provider=name)
                    if attempt < self.max_retries:
                        await asyncio.sleep(delay)
                except Exception as e:
                    last_error = e
                    logger.error("LLM stream unexpected error", provider=name, error_type=type(e).__name__)
                    observability.record_error(agent_name, type(e).__name__, str(e), provider=name)
                    if attempt < self.max_retries:
                        await asyncio.sleep(self.base_delay)

        observability.record_error(agent_name, "LLMProviderUnavailableError", f"All providers failed for stream: {last_error}", provider="all")
        logger.error("All LLM providers exhausted for stream", last_error=str(last_error))
        raise LLMProviderUnavailableError(f"All AI providers failed. Last error: {last_error}")

    async def _call_ollama_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: Optional[float] = None,
        signal: Optional[asyncio.Event] = None,
    ) -> AsyncGenerator[str, None]:
        if self.ollama_circuit.state == "open":
            if _time.time() - self.ollama_circuit.last_failure_time >= self.ollama_circuit.recovery_timeout:
                self.ollama_circuit.state = "half_open"
            else:
                raise CircuitBreakerOpenError("Ollama circuit breaker is OPEN for stream")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {"num_predict": max_tokens},
        }
        if temperature is not None:
            payload["options"]["temperature"] = temperature
        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self.ollama_timeout) as client:
                async with client.stream("POST", f"{self.ollama_base}/api/generate", json=payload) as resp:
                    resp.raise_for_status()
                    buffer = ""
                    async for chunk in resp.aiter_bytes():
                        if signal and signal.is_set():
                            return
                        buffer += chunk.decode("utf-8", errors="replace")
                        while "\n" in buffer:
                            line, buffer = buffer.split("\n", 1)
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                data = json.loads(line)
                                token = data.get("response", "")
                                if token:
                                    yield token
                                if data.get("done", False):
                                    self._last_token_usage = {
                                        "prompt_tokens": data.get("prompt_eval_count", 0),
                                        "completion_tokens": data.get("eval_count", 0),
                                    }
                                    self.ollama_circuit.failure_count = 0
                                    if self.ollama_circuit.state == "half_open":
                                        self.ollama_circuit.state = "closed"
                            except json.JSONDecodeError:
                                continue
        except (LLMTimeoutError, httpx.RequestError, httpx.HTTPStatusError):
            self.ollama_circuit.failure_count += 1
            self.ollama_circuit.last_failure_time = _time.time()
            if self.ollama_circuit.failure_count >= self.ollama_circuit.failure_threshold:
                self.ollama_circuit.state = "open"
                logger.error("Ollama circuit breaker OPENED during stream")
            raise

    async def _call_claude_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: Optional[float] = None,
        signal: Optional[asyncio.Event] = None,
    ) -> AsyncGenerator[str, None]:
        if self.claude_circuit.state == "open":
            if _time.time() - self.claude_circuit.last_failure_time >= self.claude_circuit.recovery_timeout:
                self.claude_circuit.state = "half_open"
            else:
                raise CircuitBreakerOpenError("Claude circuit breaker is OPEN for stream")

        headers = {
            "x-api-key": self.claude_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": self.claude_model,
            "max_tokens": max_tokens,
            "stream": True,
            "messages": [{"role": "user", "content": prompt}],
        }
        if temperature is not None:
            payload["temperature"] = temperature
        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self.claude_timeout) as client:
                async with client.stream("POST", "https://api.anthropic.com/v1/messages", json=payload, headers=headers) as resp:
                    if resp.status_code == 429:
                        retry_after = int(resp.headers.get("retry-after", 60))
                        raise LLMRateLimitError("Claude rate limited during stream", retry_after=retry_after)
                    resp.raise_for_status()
                    buffer = ""
                    async for chunk in resp.aiter_bytes():
                        if signal and signal.is_set():
                            return
                        buffer += chunk.decode("utf-8", errors="replace")
                        while "\n" in buffer:
                            line, buffer = buffer.split("\n", 1)
                            line = line.strip()
                            if not line:
                                continue
                            if line.startswith("event: "):
                                continue
                            if line.startswith("data: "):
                                data_str = line[6:].strip()
                                if data_str == "[DONE]":
                                    self.claude_circuit.failure_count = 0
                                    if self.claude_circuit.state == "half_open":
                                        self.claude_circuit.state = "closed"
                                    continue
                                try:
                                    data = json.loads(data_str)
                                    if data.get("type") == "content_block_delta":
                                        delta = data.get("delta", {})
                                        token = delta.get("text", "")
                                        if token:
                                            yield token
                                    elif data.get("type") == "message_delta":
                                        usage = data.get("usage", {})
                                        self._last_token_usage = {
                                            "prompt_tokens": usage.get("input_tokens", 0),
                                            "completion_tokens": usage.get("output_tokens", 0),
                                        }
                                except json.JSONDecodeError:
                                    continue
        except LLMRateLimitError:
            raise
        except (LLMTimeoutError, httpx.RequestError, httpx.HTTPStatusError):
            self.claude_circuit.failure_count += 1
            self.claude_circuit.last_failure_time = _time.time()
            if self.claude_circuit.failure_count >= self.claude_circuit.failure_threshold:
                self.claude_circuit.state = "open"
                logger.error("Claude circuit breaker OPENED during stream")
            raise

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
            pass  # Token usage recording is best-effort; failures are non-critical

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

    def format_tools(self, tools: list[dict[str, Any]]) -> str:
        if not tools:
            return ""
        lines: list[str] = ["\n\n## Available Tools\n"]
        for tool in tools:
            name = tool.get("name", tool.get("function", {}).get("name", "unknown"))
            desc = tool.get("description", tool.get("function", {}).get("description", ""))
            params = tool.get("parameters", tool.get("function", {}).get("parameters", {}))
            lines.append(f"- **{name}**: {desc}")
            if params:
                props = params.get("properties", {})
                required = params.get("required", [])
                for pname, pinfo in props.items():
                    req_mark = " (required)" if pname in required else ""
                    ptype = pinfo.get("type", "string")
                    lines.append(f"  - `{pname}` ({ptype}){req_mark}: {pinfo.get('description', '')}")
        return "\n".join(lines)

    def format_tools_for_openai(self, tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        formatted: list[dict[str, Any]] = []
        for tool in tools:
            entry: dict[str, Any] = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {"type": "object", "properties": {}}),
                },
            }
            formatted.append(entry)
        return formatted

    def format_tools_for_claude(self, tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        formatted: list[dict[str, Any]] = []
        for tool in tools:
            entry: dict[str, Any] = {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "input_schema": tool.get("parameters", {"type": "object", "properties": {}}),
            }
            formatted.append(entry)
        return formatted

    def parse_tool_calls_from_response(self, response: dict[str, Any], provider: str = "ollama") -> list[dict[str, Any]]:
        if provider == "openai":
            return self._parse_openai_tool_calls(response)
        elif provider == "claude":
            return self._parse_claude_tool_calls(response)
        return self._parse_generic_tool_calls(response)

    def _parse_openai_tool_calls(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        calls: list[dict[str, Any]] = []
        choices = response.get("choices", [])
        for choice in choices:
            message = choice.get("message", {})
            tool_calls = message.get("tool_calls", [])
            for tc in tool_calls:
                function = tc.get("function", {})
                try:
                    arguments = json.loads(function.get("arguments", "{}"))
                except (json.JSONDecodeError, TypeError):
                    arguments = {}
                calls.append({
                    "tool_name": function.get("name", ""),
                    "parameters": arguments,
                    "request_id": tc.get("id"),
                })
        return calls

    def _parse_claude_tool_calls(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        calls: list[dict[str, Any]] = []
        content = response.get("content", [])
        for block in content:
            if block.get("type") == "tool_use":
                calls.append({
                    "tool_name": block.get("name", ""),
                    "parameters": block.get("input", {}),
                    "request_id": block.get("id"),
                })
        return calls

    def _parse_generic_tool_calls(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        calls: list[dict[str, Any]] = []
        raw = response.get("response", response.get("text", ""))
        if isinstance(raw, str):
            extracted = self._extract_json(raw)
            if extracted:
                tc_list = extracted.get("tool_calls", extracted.get("calls", [extracted]))
                if isinstance(tc_list, dict):
                    tc_list = [tc_list]
                for tc in tc_list:
                    calls.append({
                        "tool_name": tc.get("tool_name", tc.get("name", "")),
                        "parameters": tc.get("parameters", tc.get("arguments", {})),
                        "request_id": tc.get("request_id", tc.get("id")),
                    })
        return calls


llm = LLMClient()
