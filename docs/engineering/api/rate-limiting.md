# Rate Limiting Policy — Second Brain OS API

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ENG-RATE-001 |
| **Version** | 1.0.0 |
| **Status** | Active |
| **Date** | 2026-07-10 |
| **Classification** | Internal |
| **Owner** | Developer |

---

## 1. Architecture

The API implements a **two-layer rate limiting** system:

1. **Global middleware** (`RateLimiter`) — applies to all incoming requests
2. **Per-endpoint limiter** (`EndpointRateLimiter`) — applies to specific high-cost endpoints

Both are implemented in `packages/shared/utils/rate_limiter.py`.

---

## 2. Global Rate Limiter (`RateLimiter`)

### Algorithm: Sliding Window

The `RateLimiter` is a `BaseHTTPMiddleware` that uses an **in-memory sliding window** algorithm:

- Each client IP has a list of request timestamps
- On each request, timestamps older than `window_seconds` are pruned
- If the count of remaining timestamps ≥ `max_requests`, the request is rejected with HTTP 429
- The window slides continuously (not fixed clock-aligned buckets)

### Default Configuration (from `config.core.config.settings`)

| Setting | Env Var | Default | Description |
|---|---|---|---|
| `max_requests` | `RATE_LIMIT_MAX` | 100 | Maximum requests per window |
| `window_seconds` | `RATE_LIMIT_WINDOW` | 60 | Window duration in seconds |

### Thread Safety

Uses `asyncio.Lock` to protect the request tracking dictionary from concurrent access.

### Limitation

This is an **in-memory** rate limiter. It does NOT persist across server restarts and does NOT work correctly in multi-process deployments (e.g., multiple uvicorn workers). For production multi-worker deployments, consider a Redis-backed limiter.

---

## 3. Per-Endpoint Rate Limiter (`EndpointRateLimiter`)

### Algorithm: Per-Endpoint Sliding Window

The `EndpointRateLimiter` provides granular rate limits for specific endpoint paths. It tracks requests per `(endpoint, client_ip)` pair.

### Configured Limits

| Endpoint Pattern | Max Requests | Window | Notes |
|---|---|---|---|
| `/api/v1/chat` | 30 | 60s | AI chat is expensive — conservative limit |
| `/api/tasks` (legacy) | 60 | 60s | Legacy path, may not be actively used |
| `/api/courses` (legacy) | 60 | 60s | Legacy path |
| `/api/goals` (legacy) | 60 | 60s | Legacy path |
| `default` | 100 | 60s | Fallback for all other endpoints |

### Usage in Code

```python
from shared.utils.rate_limiter import endpoint_limiter

client_ip = request.client.host if request.client else "unknown"
if not endpoint_limiter.check(client_ip, "/api/v1/chat"):
    raise HTTPException(status_code=429, detail="Rate limit exceeded.")
```

Currently used by:
- `POST /api/v1/chat` (chat.py)
- `POST /api/v1/automation/trigger/briefing`
- `POST /api/v1/automation/trigger/radar`
- `POST /api/v1/automation/trigger/weekly-review`
- `POST /api/v1/automation/trigger/sleep-analysis`
- `POST /api/v1/automation/trigger/sleep-bedtime`
- `POST /api/v1/automation/trigger/nudges`
- `POST /api/v1/automation/trigger/cleanup`

---

## 4. Rate Limit Headers

Every response from the global rate limiter includes:

| Header | Type | Description |
|---|---|---|
| `X-RateLimit-Limit` | int | Maximum requests allowed per window |
| `X-RateLimit-Remaining` | int | Requests remaining in current window |
| `X-RateLimit-Reset` | int | Unix timestamp when the window resets |

**Example:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1720630000
```

---

## 5. 429 Response Format

When a request is rate-limited, the middleware raises an `HTTPException(429)`:

```json
{
  "detail": "Rate limit exceeded. Max 100 requests per 60s"
}
```

For per-endpoint rate limits:

```json
{
  "detail": "Rate limit exceeded. Max 30 requests per minute for chat."
}
```

---

## 6. Circuit Breaker (AI Endpoints)

While not strictly rate limiting, the AI client (`packages/ai/client.py`) implements a **circuit breaker** that complements the rate limiter:

| State | Condition | Behavior |
|---|---|---|
| **CLOSED** | Normal operation | Requests flow through |
| **OPEN** | 5 consecutive failures | Reject all requests for 60s cooldown |
| **HALF_OPEN** | After cooldown | Allow 1 test request |

### Circuit Breaker States

```
CLOSED → (5 failures) → OPEN → (60s timeout) → HALF_OPEN → (1 success) → CLOSED
                                                          → (1 failure) → OPEN
```

### AI Retry Policy

```python
# 3 attempts with exponential backoff
retry_attempts = 3
backoff = [2, 4, 8]  # seconds
```

### Provider Fallback Chain

1. Primary: Ollama (local, free) — `ollama/mistral:7b`
2. Fallback: Claude API (cloud, paid) — only if `USE_LOCAL_AI=False`
3. Algorithmic: If both providers fail, each agent has a keyword/regex fallback

---

## 7. How to Request Rate Limit Increases

Rate limits are configured via environment variables:

| Variable | Effect | File |
|---|---|---|
| `RATE_LIMIT_MAX` | Global max requests per window | `main.py:179` |
| `RATE_LIMIT_WINDOW` | Global window seconds | `main.py:180` |
| `EndpointRateLimiter.limits` dict | Per-endpoint overrides | `rate_limiter.py:55-61` |

To change defaults:

1. For global limits: update `.env` and restart the server
2. For per-endpoint limits: edit the `EndpointRateLimiter.limits` dict in `rate_limiter.py`
3. For production multi-worker: replace `RateLimiter` with a Redis-backed implementation

### Requesting Changes via PR

1. Create a branch with your limit changes
2. Update `packages/shared/utils/rate_limiter.py` with new limits
3. Add/update tests in `tests/test_config_core.py` or `tests/test_shared_utils.py`
4. Open PR with justification for the change
5. CI must pass (all rate limit tests)

---

## 8. Monitoring and Alerting

Rate limit events (429 responses) are logged via the structured logger:

```json
{
  "level": "WARN",
  "message": "Rate limit exceeded",
  "client_ip": "203.0.113.42",
  "endpoint": "/api/v1/chat",
  "request_id": "abc-123-def"
}
```

The monitoring endpoint `GET /monitoring/metrics` tracks overall request rates and error rates (including 429s) in the RED metrics dashboard.

---

## 9. Known Limitations and Future Work

| Limitation | Impact | Planned Fix |
|---|---|---|
| In-memory storage | Lost on restart, not shared across workers | Redis-backed limiter (Q4 2026) |
| IP-based only | Behind NAT, all users of same public IP share a bucket | User-ID-based + IP hybrid |
| No burst allowance | Strict sliding window, no burst tolerance | Token bucket algorithm |
| No distributed support | Multiple workers have independent counters | Redis-backed distributed limiter |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-07-10 | Developer | Initial policy document from `rate_limiter.py` source code. |
