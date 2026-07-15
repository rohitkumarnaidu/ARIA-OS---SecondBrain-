import asyncio
import functools
import re
import time as _time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Callable

import httpx

from config.core.config import settings


_OLLAMA_PRICE_PER_INPUT_TOKEN: float = 0.0
_OLLAMA_PRICE_PER_OUTPUT_TOKEN: float = 0.0
_CLAUDE_PRICE_PER_INPUT_TOKEN: float = 3.0 / 1_000_000
_CLAUDE_PRICE_PER_OUTPUT_TOKEN: float = 15.0 / 1_000_000

_PROVIDER_PRICES: dict[str, tuple[float, float]] = {
    "ollama": (_OLLAMA_PRICE_PER_INPUT_TOKEN, _OLLAMA_PRICE_PER_OUTPUT_TOKEN),
    "claude": (_CLAUDE_PRICE_PER_INPUT_TOKEN, _CLAUDE_PRICE_PER_OUTPUT_TOKEN),
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AIObservability:
    """Observability for AI agent calls — token usage, latency, errors, and metrics."""

    def __init__(self):
        self._usage: dict[str, deque[dict]] = defaultdict(
            lambda: deque(maxlen=10000)
        )
        self._latency: dict[str, deque[dict]] = defaultdict(
            lambda: deque(maxlen=10000)
        )
        self._errors: dict[str, deque[dict]] = defaultdict(
            lambda: deque(maxlen=5000)
        )
        self._agent_usage: dict[str, deque[dict]] = defaultdict(
            lambda: deque(maxlen=10000)
        )
        self._provider_usage: dict[str, deque[dict]] = defaultdict(
            lambda: deque(maxlen=10000)
        )
        self._api_base = f"http://localhost:{settings.api_port if hasattr(settings, 'api_port') else 8000}"

    # ── Token tracking ────────────────────────────────────────────────────────

    def record_usage(
        self,
        agent_name: str,
        input_tokens: int,
        output_tokens: int,
        model: str,
        duration_ms: int,
        success: bool,
        provider: str = "unknown",
    ) -> None:
        """Record token usage for an agent call."""
        timestamp = _now_iso()
        record = {
            "timestamp": timestamp,
            "agent": agent_name,
            "model": model,
            "provider": provider,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "duration_ms": duration_ms,
            "success": success,
        }
        self._usage[agent_name].append(record)
        self._agent_usage[agent_name].append(record)
        self._provider_usage[provider].append(record)

        if input_tokens > 0 or output_tokens > 0:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._persist_usage(record))
            except RuntimeError:
                pass

    def get_agent_usage(
        self,
        agent_name: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> dict:
        """Get aggregated usage stats for a specific agent."""
        records = list(self._usage.get(agent_name, []))
        if since:
            records = [r for r in records if r["timestamp"] >= since.isoformat()]
        if until:
            records = [r for r in records if r["timestamp"] <= until.isoformat()]

        if not records:
            return {
                "agent": agent_name,
                "total_calls": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_tokens": 0,
                "avg_duration_ms": 0.0,
                "error_count": 0,
                "error_rate": 0.0,
            }

        total_calls = len(records)
        total_input = sum(r["input_tokens"] for r in records)
        total_output = sum(r["output_tokens"] for r in records)
        total_duration = sum(r["duration_ms"] for r in records)
        errors = sum(1 for r in records if not r["success"])

        return {
            "agent": agent_name,
            "total_calls": total_calls,
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "avg_duration_ms": round(total_duration / total_calls, 2) if total_calls else 0.0,
            "error_count": errors,
            "error_rate": round(errors / total_calls, 4) if total_calls else 0.0,
        }

    def get_provider_usage(self, provider_name: str) -> dict:
        """Get aggregated usage stats for a specific provider."""
        records = list(self._provider_usage.get(provider_name, []))
        if not records:
            return {
                "provider": provider_name,
                "total_calls": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_tokens": 0,
                "avg_duration_ms": 0.0,
                "success_count": 0,
                "error_count": 0,
            }

        total_calls = len(records)
        total_input = sum(r["input_tokens"] for r in records)
        total_output = sum(r["output_tokens"] for r in records)
        total_duration = sum(r["duration_ms"] for r in records)
        successes = sum(1 for r in records if r["success"])
        errors = total_calls - successes

        return {
            "provider": provider_name,
            "total_calls": total_calls,
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "avg_duration_ms": round(total_duration / total_calls, 2) if total_calls else 0.0,
            "success_count": successes,
            "error_count": errors,
            "success_rate": round(successes / total_calls, 4) if total_calls else 0.0,
        }

    def get_cost_report(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> dict:
        """Get estimated cost breakdown by provider and agent."""
        all_records: list[dict] = []
        for records in self._usage.values():
            all_records.extend(records)

        if since:
            all_records = [r for r in all_records if r["timestamp"] >= since.isoformat()]
        if until:
            all_records = [r for r in all_records if r["timestamp"] <= until.isoformat()]

        by_provider: dict[str, dict] = {}
        by_agent: dict[str, dict] = {}
        total_cost: float = 0.0

        for record in all_records:
            provider = record.get("provider", "unknown")
            agent = record.get("agent", "unknown")
            input_tokens = record.get("input_tokens", 0)
            output_tokens = record.get("output_tokens", 0)
            inp_price, out_price = _PROVIDER_PRICES.get(provider, (0.0, 0.0))
            cost = (input_tokens * inp_price) + (output_tokens * out_price)
            total_cost += cost

            if provider not in by_provider:
                by_provider[provider] = {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0}
            by_provider[provider]["calls"] += 1
            by_provider[provider]["input_tokens"] += input_tokens
            by_provider[provider]["output_tokens"] += output_tokens
            by_provider[provider]["cost"] += cost

            if agent not in by_agent:
                by_agent[agent] = {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0}
            by_agent[agent]["calls"] += 1
            by_agent[agent]["input_tokens"] += input_tokens
            by_agent[agent]["output_tokens"] += output_tokens
            by_agent[agent]["cost"] += cost

        for p in by_provider:
            by_provider[p]["cost"] = round(by_provider[p]["cost"], 6)
        for a in by_agent:
            by_agent[a]["cost"] = round(by_agent[a]["cost"], 6)

        return {
            "total_calls": len(all_records),
            "total_cost": round(total_cost, 6),
            "by_provider": by_provider,
            "by_agent": by_agent,
            "period": {
                "since": since.isoformat() if since else None,
                "until": until.isoformat() if until else None,
            },
        }

    # ── Latency tracking ──────────────────────────────────────────────────────

    def record_latency(self, agent_name: str, duration_ms: int, endpoint: str = "unknown") -> None:
        """Record latency for an agent call."""
        self._latency[agent_name].append({
            "timestamp": _now_iso(),
            "agent": agent_name,
            "duration_ms": duration_ms,
            "endpoint": endpoint,
        })

    def get_latency_percentiles(
        self,
        agent_name: str,
        percentiles: Optional[list[int]] = None,
    ) -> dict:
        """Get latency percentiles for an agent."""
        if percentiles is None:
            percentiles = [50, 95, 99]
        records = list(self._latency.get(agent_name, []))
        if not records:
            result: dict = {"agent": agent_name, "samples": 0}
            for p in percentiles:
                result[f"p{p}"] = 0.0
            return result

        durations = sorted(r["duration_ms"] for r in records)
        n = len(durations)
        result = {"agent": agent_name, "samples": n}
        for p in percentiles:
            idx = max(0, min(n - 1, int(n * p / 100)))
            result[f"p{p}"] = round(durations[idx], 2)
        return result

    def get_slowest_agents(self, top_n: int = 5) -> list[dict]:
        """Get agents with highest average latency."""
        agent_avgs: list[tuple[str, float, int]] = []
        for agent_name, records in self._latency.items():
            if not records:
                continue
            durations = [r["duration_ms"] for r in records]
            avg = sum(durations) / len(durations)
            agent_avgs.append((agent_name, round(avg, 2), len(durations)))

        agent_avgs.sort(key=lambda x: x[1], reverse=True)
        return [
            {"agent": name, "avg_latency_ms": avg, "samples": count}
            for name, avg, count in agent_avgs[:top_n]
        ]

    # ── Error tracking ────────────────────────────────────────────────────────

    def record_error(
        self,
        agent_name: str,
        error_type: str,
        error_message: str,
        provider: str = "unknown",
    ) -> None:
        """Record an error for an agent call."""
        self._errors[agent_name].append({
            "timestamp": _now_iso(),
            "agent": agent_name,
            "error_type": error_type,
            "error_message": error_message[:500],
            "provider": provider,
        })

    def get_error_rate(self, agent_name: str, window_minutes: int = 60) -> float:
        """Get error rate for an agent over a rolling time window."""
        cutoff = (datetime.now(timezone.utc) - timedelta(minutes=window_minutes)).isoformat()
        errors = [r for r in self._errors.get(agent_name, []) if r["timestamp"] >= cutoff]
        total_calls = len([r for r in self._usage.get(agent_name, []) if r["timestamp"] >= cutoff])
        if total_calls == 0:
            return 0.0
        return round(len(errors) / total_calls, 4)

    def get_most_common_errors(self, top_n: int = 10) -> list[dict]:
        """Get the most common error types."""
        error_counts: dict[str, int] = defaultdict(int)
        for records in self._errors.values():
            for r in records:
                error_counts[r["error_type"]] += 1

        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        return [
            {"error_type": etype, "count": count}
            for etype, count in sorted_errors[:top_n]
        ]

    # ── Prometheus metrics ────────────────────────────────────────────────────

    def get_prometheus_metrics(self) -> str:
        """Format metrics for Prometheus scraping."""
        lines: list[str] = [
            "# HELP ai_requests_total Total number of AI requests",
            "# TYPE ai_requests_total counter",
        ]

        all_usage: list[dict] = []
        for records in self._usage.values():
            all_usage.extend(records)

        request_counts: dict[tuple[str, str, str], int] = defaultdict(int)
        for r in all_usage:
            key = (r.get("agent", "unknown"), r.get("provider", "unknown"), "ok" if r.get("success", True) else "error")
            request_counts[key] += 1

        for (agent, provider, status), count in sorted(request_counts.items()):
            agent_sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", agent)
            provider_sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", provider)
            lines.append(
                f'ai_requests_total{{agent="{agent_sanitized}",provider="{provider_sanitized}",'
                f'status="{status}"}} {count}'
            )

        lines.extend([
            "",
            "# HELP ai_latency_seconds AI request latency in seconds",
            "# TYPE ai_latency_seconds histogram",
            "# HELP ai_tokens_total Total tokens processed by AI",
            "# TYPE ai_tokens_total counter",
        ])

        token_counts: dict[tuple[str, str], int] = defaultdict(int)
        token_types: dict[tuple[str, str, str], int] = defaultdict(int)
        for r in all_usage:
            agent = r.get("agent", "unknown")
            provider = r.get("provider", "unknown")
            agent_s = re.sub(r"[^a-zA-Z0-9_]", "_", agent)
            provider_s = re.sub(r"[^a-zA-Z0-9_]", "_", provider)
            key = (agent_s, provider_s)
            token_counts[key] += r.get("input_tokens", 0) + r.get("output_tokens", 0)
            token_types[(agent_s, provider_s, "input")] += r.get("input_tokens", 0)
            token_types[(agent_s, provider_s, "output")] += r.get("output_tokens", 0)

        for (agent, provider, ttype), count in sorted(token_types.items()):
            lines.append(
                f'ai_tokens_total{{agent="{agent}",provider="{provider}",'
                f'type="{ttype}"}} {count}'
            )

        lines.extend([
            "",
            "# HELP ai_errors_total Total number of AI errors",
            "# TYPE ai_errors_total counter",
        ])

        error_counts: dict[tuple[str, str], int] = defaultdict(int)
        for records in self._errors.values():
            for r in records:
                agent_s = re.sub(r"[^a-zA-Z0-9_]", "_", r.get("agent", "unknown"))
                etype_s = re.sub(r"[^a-zA-Z0-9_]", "_", r.get("error_type", "unknown"))
                error_counts[(agent_s, etype_s)] += 1

        for (agent, etype), count in sorted(error_counts.items()):
            lines.append(f'ai_errors_total{{agent="{agent}",error_type="{etype}"}} {count}')

        lines.extend([
            "",
            "# HELP ai_circuit_breaker_state Circuit breaker state per provider (1=closed, 0=open)",
            "# TYPE ai_circuit_breaker_state gauge",
        ])

        from ai.client import llm as _llm_client
        for provider_name, cb in [("ollama", _llm_client.ollama_circuit), ("claude", _llm_client.claude_circuit)]:
            state_val = 1.0 if cb.state == "closed" else 0.0
            lines.append(f'ai_circuit_breaker_state{{provider="{provider_name}"}} {state_val}')

        lines.append("")
        return "\n".join(lines)

    # ── Dashboard data ────────────────────────────────────────────────────────

    def get_dashboard_summary(self) -> dict:
        """Get a summary for the frontend dashboard."""
        now = datetime.now(timezone.utc)
        last_hour = now - timedelta(hours=1)
        last_day = now - timedelta(days=1)

        all_usage: list[dict] = []
        for records in self._usage.values():
            all_usage.extend(records)

        hour_usage = [r for r in all_usage if r["timestamp"] >= last_hour.isoformat()]
        day_usage = [r for r in all_usage if r["timestamp"] >= last_day.isoformat()]

        all_errors: list[dict] = []
        for records in self._errors.values():
            all_errors.extend(records)
        hour_errors = [r for r in all_errors if r["timestamp"] >= last_hour.isoformat()]
        day_errors = [r for r in all_errors if r["timestamp"] >= last_day.isoformat()]

        total_agents = len(set(r.get("agent", "") for r in all_usage))
        active_agents_hour = len(set(r.get("agent", "") for r in hour_usage))

        total_tokens_hour = sum(r.get("input_tokens", 0) + r.get("output_tokens", 0) for r in hour_usage)
        total_tokens_day = sum(r.get("input_tokens", 0) + r.get("output_tokens", 0) for r in day_usage)

        hour_latencies = [r.get("duration_ms", 0) for r in hour_usage]
        avg_latency_hour = round(sum(hour_latencies) / len(hour_latencies), 2) if hour_latencies else 0.0

        return {
            "time_range": "last_24h",
            "total_agents": total_agents,
            "active_agents_last_hour": active_agents_hour,
            "total_calls_last_hour": len(hour_usage),
            "total_calls_last_24h": len(day_usage),
            "total_tokens_last_hour": total_tokens_hour,
            "total_tokens_last_24h": total_tokens_day,
            "avg_latency_ms_last_hour": avg_latency_hour,
            "errors_last_hour": len(hour_errors),
            "errors_last_24h": len(day_errors),
            "error_rate_last_hour": round(len(hour_errors) / len(hour_usage), 4) if hour_usage else 0.0,
            "error_rate_last_24h": round(len(day_errors) / len(day_usage), 4) if day_usage else 0.0,
        }

    def get_agent_health(self, agent_name: str) -> dict:
        """Get health status for a specific agent."""
        records = list(self._usage.get(agent_name, []))
        errors = list(self._errors.get(agent_name, []))
        latencies = list(self._latency.get(agent_name, []))

        if not records:
            return {
                "agent": agent_name,
                "status": "unknown",
                "total_calls": 0,
                "error_rate": 0.0,
                "avg_latency_ms": 0.0,
                "last_call_at": None,
                "last_call_success": None,
            }

        total_calls = len(records)
        error_count = len(errors)
        error_rate = round(error_count / total_calls, 4) if total_calls else 0.0

        avg_latency = 0.0
        if latencies:
            avg_latency = round(sum(r["duration_ms"] for r in latencies) / len(latencies), 2)

        last_call = records[-1] if records else {}
        last_success = last_call.get("success", True) if last_call else None

        status = "healthy"
        if error_rate > 0.1:
            status = "degraded"
        if error_rate > 0.3:
            status = "unhealthy"
        if not records:
            status = "inactive"

        return {
            "agent": agent_name,
            "status": status,
            "total_calls": total_calls,
            "error_count": error_count,
            "error_rate": error_rate,
            "avg_latency_ms": avg_latency,
            "last_call_at": last_call.get("timestamp") if last_call else None,
            "last_call_success": last_success,
        }

    # ── Track decorator ───────────────────────────────────────────────────────

    def track(
        self,
        agent_name: str = "unknown",
        model: str = "unknown",
        provider: str = "unknown",
    ) -> Callable:
        """Decorator to automatically track agent calls with observability."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                start = _time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration_ms = int((_time.time() - start) * 1000)
                    self.record_latency(agent_name, duration_ms, endpoint=func.__name__)
                    self.record_usage(
                        agent_name=agent_name,
                        input_tokens=kwargs.get("input_tokens", 0),
                        output_tokens=len(str(result)) // 4,
                        model=model,
                        duration_ms=duration_ms,
                        success=True,
                        provider=provider,
                    )
                    return result
                except Exception as e:
                    duration_ms = int((_time.time() - start) * 1000)
                    self.record_error(
                        agent_name=agent_name,
                        error_type=type(e).__name__,
                        error_message=str(e),
                        provider=provider,
                    )
                    self.record_latency(agent_name, duration_ms, endpoint=func.__name__)
                    raise
            return wrapper
        return decorator

    # ── Persistence ───────────────────────────────────────────────────────────

    async def _persist_usage(self, record: dict) -> None:
        """Persist usage record to the monitoring API (best-effort)."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                await client.post(
                    f"{self._api_base}/api/v1/monitoring/token-usage",
                    json={
                        "agent": record["agent"],
                        "model": record["model"],
                        "provider": record["provider"],
                        "prompt_tokens": record["input_tokens"],
                        "completion_tokens": record["output_tokens"],
                        "duration_ms": record["duration_ms"],
                        "endpoint": f"llm:{record.get('provider', 'unknown')}",
                    },
                )
        except Exception:
            pass


observability = AIObservability()
