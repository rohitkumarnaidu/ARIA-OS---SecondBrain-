# Claude Integration

## Document Control

| Field | Value |
|---|---|
| Document ID | INT-CLD-005 |
| Version | 1.0.0 |
| Status | Approved |
| Date | 2026-07-10 |
| Classification | Internal |
| Owner | Developer |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Integration Overview](#2-integration-overview)
3. [API Configuration](#3-api-configuration)
4. [Supported Models](#4-supported-models)
5. [Architecture Diagram](#5-architecture-diagram)
6. [Request/Response Format](#6-requestresponse-format)
7. [Cost Per Request](#7-cost-per-request)
8. [Rate Limits & Quotas](#8-rate-limits--quotas)
9. [Fallback Chain Position](#9-fallback-chain-position)
10. [Circuit Breaker Integration](#10-circuit-breaker-integration)
11. [API Key Management](#11-api-key-management)
12. [Error Handling](#12-error-handling)
13. [Security Considerations](#13-security-considerations)
14. [Monitoring & Observability](#14-monitoring--observability)
15. [Token Usage Tracking](#15-token-usage-tracking)
16. [Testing Strategy](#16-testing-strategy)
17. [Edge Cases](#17-edge-cases)
18. [Failure Scenarios](#18-failure-scenarios)
19. [Configuration Reference](#19-configuration-reference)
20. [References](#20-references)

---

## 1. Executive Summary

Anthropic Claude is the primary fallback AI provider for Second Brain OS. When Ollama (local, default) is unavailable, the system automatically fails over to Claude. Claude handles complex agent tasks including daily briefings, weekly reviews, opportunity parsing, and roadmap analysis.

---

## 2. Integration Overview

| Property | Value |
|---|---|
| Provider | Anthropic |
| API Endpoint | `https://api.anthropic.com/v1/messages` |
| Auth Method | `x-api-key` header |
| Default Model | `claude-sonnet-4-20250514` |
| SDK | `anthropic` Python SDK (optional, can use `httpx` directly) |
| Cost | ~$0.003–$0.015 per request |
| API Version | `2023-06-01` |

---

## 3. API Configuration

```python
import httpx
import os

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
CLAUDE_API_VERSION = "2023-06-01"
CLAUDE_TIMEOUT = int(os.getenv("CLAUDE_TIMEOUT", "120"))
```

---

## 4. Supported Models

| Model | Use Case | Context Window | Cost (Input) | Cost (Output) |
|---|---|---|---|---|
| `claude-sonnet-4-20250514` | Primary fallback | 200K tokens | $3.00/1M tokens | $15.00/1M tokens |
| `claude-3-haiku-20240307` | Fast, cheap tasks | 200K tokens | $0.25/1M tokens | $1.25/1M tokens |
| `claude-3-opus-latest` | Complex reasoning (future) | 200K tokens | $15.00/1M tokens | $75.00/1M tokens |

---

## 5. Architecture Diagram

```mermaid
graph TD
    subgraph App["Second Brain OS"]
        LLMClient["LLMClient (client.py)"]
        Agents["Agent Modules"]
        Router["AI Provider Router"]
    end

    subgraph Fallback["Provider Chain"]
        Ollama["Ollama<br/>Local · Free · Default"]
        Claude["Claude API<br/>Cloud · ~$0.015/req<br/>Fallback #1"]
        OpenAI["OpenAI<br/>Cloud · Fallback #2<br/>(Planned)"]
    end

    Agents -->|generate() / generate_json()| LLMClient
    LLMClient --> Router
    Router -->|1st| Ollama
    Router -->|2nd| Claude
    Router -->|3rd| OpenAI

    Claude -->|Circuit Breaker| CB["3 failures → 120s cooldown"]
    CB -->|Pass| ClaudeSuccess["Return Response"]
    CB -->|Open| NextProvider["Skip to next provider"]

    style Claude fill:#1A1D24,stroke:#F59E0B,color:#F1F5F9
    style CB fill:#1A1D24,stroke:#EF4444,color:#F1F5F9
```

---

## 6. Request/Response Format

### Request

```json
{
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 4096,
  "temperature": 0.5,
  "system": "You are ARIA, the AI core of Second Brain OS...",
  "messages": [
    {"role": "user", "content": "Generate my daily briefing"}
  ]
}
```

### Response

```json
{
  "id": "msg_01ABC123",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Good morning! Here is your briefing..."
    }
  ],
  "model": "claude-sonnet-4-20250514",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 850,
    "output_tokens": 420
  }
}
```

---

## 7. Cost Per Request

| Agent | Avg Input Tokens | Avg Output Tokens | Est. Cost/Req | Frequency/Mo | Monthly Cost |
|---|---|---|---|---|---|
| Daily Briefing (A09) | 800 | 600 | ~$0.003 | 30 | ~$0.09 |
| Weekly Review (A10) | 1,500 | 800 | ~$0.006 | 4 | ~$0.02 |
| Opportunity Radar (A06) | 600 | 1,000 | ~$0.004 | 30 | ~$0.12 |
| Memory Agent (A02) | 400 | 200 | ~$0.001 | 90 | ~$0.09 |
| Learning Agent (A03) | 500 | 300 | ~$0.002 | 30 | ~$0.06 |
| Sleep Agent (A13) | 300 | 400 | ~$0.001 | 30 | ~$0.03 |
| Nudge Agent (A14) | 400 | 200 | ~$0.001 | 30 | ~$0.03 |
| Roadmap Agent (A08) | 500 | 300 | ~$0.002 | 8 | ~$0.02 |
| Opportunity Matching (A15) | 300 | 200 | ~$0.001 | 30 | ~$0.03 |
| **Total** | | | | | **~$0.49/mo** |

---

## 8. Rate Limits & Quotas

| Tier | Requests/Min | Tokens/Min | Max Tokens/Req |
|---|---|---|---|
| Developer (free credits) | 10 | 20,000 | 4,096 |
| Tier 1 ($5+ spend) | 50 | 100,000 | 8,192 |
| Tier 2 ($50+ spend) | 200 | 500,000 | 8,192 |

---

## 9. Fallback Chain Position

Claude is the **second position** in the provider chain:

| Position | Provider | Condition | Circuit Breaker | Timeout |
|---|---|---|---|---|
| 1 | Ollama | `USE_LOCAL_AI=True` | 5 failures → 60s cooldown | 60s |
| **2** | **Claude** | **Always enabled (API key present)** | **3 failures → 120s cooldown** | **120s** |
| 3 | OpenAI | `OPENAI_API_KEY` set | 3 failures → 120s cooldown | 60s |

---

## 10. Circuit Breaker Integration

```python
self.claude_circuit = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=120,
    expected_exception=(LLMRateLimitError, httpx.RequestError),
)
```

When the Claude circuit breaker opens:
1. All Claude requests are immediately rejected for 120 seconds
2. The system automatically proceeds to the next provider (OpenAI or raises error)
3. After cooldown, a single test request is allowed (half-open state)
4. If successful → circuit closes, normal operation resumes
5. If failed → circuit re-opens for another 120 seconds

---

## 11. API Key Management

| Practice | Implementation |
|---|---|
| Storage | Railway env var `CLAUDE_API_KEY` (encrypted) |
| Rotation | Every 90 days |
| Validation | Key prefix check (`sk-ant-...`) on startup |
| Monitoring | Usage dashboard via Anthropic Console |

---

## 12. Error Handling

| HTTP Status | Error | Action |
|---|---|---|
| 401 | Invalid API key | Log error, skip provider, alert developer |
| 429 | Rate limit exceeded | Read `retry-after` header, backoff + retry |
| 500 | Server error | Retry 3x (exponential: 2s, 4s, 8s) |
| 529 | Overloaded | Wait 30s, retry once, then fall back |
| Timeout | No response in 120s | Circuit breaker trip, fall back |

---

## 13. Security Considerations

- API key stored server-side only, never in client bundle
- All requests proxied through FastAPI backend
- User prompts sanitized before sending (XSS prevention)
- No PII or credentials included in prompts
- Anthropic does not train on API requests by default

---

## 14. Monitoring & Observability

| Metric | Source | Alert |
|---|---|---|
| Claude monthly cost | Token usage tracking | > $5/month |
| Error rate | Backend logs | > 5% |
| Latency p95 | Request timing | > 30s |
| Circuit breaker state | `/api/v1/monitoring/health` | OPEN state |
| Fallback activations | LLM client logs | > 10/day |
| Total tokens used | Token usage API | Monitor trend |

---

## 15. Token Usage Tracking

```python
async def record_token_usage(agent: str, model: str, provider: str, prompt_tokens: int, completion_tokens: int, duration_ms: int):
    if prompt_tokens == 0 and completion_tokens == 0:
        return
    async with httpx.AsyncClient(timeout=5) as client:
        await client.post(
            "http://localhost:8000/api/v1/monitoring/token-usage",
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
```

---

## 16. Testing Strategy

| Test Type | Scope |
|---|---|
| Unit | Request formatting, response parsing, cost calculation |
| Mock | Claude API responses with `responses` library |
| Integration | Full fallback chain (Ollama → Claude → error) |
| Circuit breaker | Verify state transitions (closed → open → half-open → closed) |

---

## 17. Edge Cases

- Empty response → Check `stop_reason` = `max_tokens` (truncated), retry with higher limit
- Content filter triggered → Check `stop_reason` = `end_turn` with filtered content, return safe fallback
- Streaming timeout → Fall back to non-streaming request with shorter timeout
- 200K context window exceeded → Truncate conversation history, summarize older messages

---

## 18. Failure Scenarios

| Scenario | Impact | Mitigation |
|---|---|---|
| Claude API outage | No Claude fallback | Use OpenAI fallback (if configured) or raise error |
| API key expired | Provider unavailable | Rotate key via Railway dashboard |
| Rate limit exceeded | Delayed responses | Queue requests, exponential backoff |
| Account suspended | Complete loss of cloud AI | Fall back to Ollama-only mode |

---

## 19. Configuration Reference

```env
CLAUDE_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-sonnet-4-20250514
CLAUDE_TIMEOUT=120
USE_LOCAL_AI=False  # Set to False to prefer Claude over Ollama
```

---

## 20. References

| Resource | URL |
|---|---|
| Anthropic API Reference | https://docs.anthropic.com/en/api |
| Anthropic Models | https://docs.anthropic.com/en/docs/about-claude/models |
| Anthropic Pricing | https://www.anthropic.com/pricing |
| Message API | https://docs.anthropic.com/en/api/messages |
| Integration Architecture | `docs/engineering/37_IntegrationArchitecture.md` |
| LLM Client | `packages/ai/client.py` |
