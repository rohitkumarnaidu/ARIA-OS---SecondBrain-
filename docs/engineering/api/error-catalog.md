# Error Catalog — Second Brain OS API

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ENG-EC-001 |
| **Version** | 1.0.0 |
| **Status** | Active |
| **Date** | 2026-07-11 |
| **Classification** | Internal |
| **Owner** | Developer |
| **Related Docs** | Error Response Schema (`database/schemas/error_response.py`), Rate Limiting Policy (`rate-limiting.md`) |

---

## Table of Contents

1. [Error Response Format](#1-error-response-format)
2. [HTTP 4xx — Client Errors](#2-http-4xx--client-errors)
3. [HTTP 5xx — Server Errors](#3-http-5xx--server-errors)
4. [Recovery & Retry Strategies](#4-recovery--retry-strategies)
5. [How to Report New Errors](#5-how-to-report-new-errors)

---

## 1. Error Response Format

The API uses a standardized error response schema defined in `packages/database/schemas/error_response.py`.

### Response Shape

```json
{
  "detail": "Human-readable error message",
  "error_code": "ERROR_CODE",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2026-07-11T12:00:00Z",
  "retry_after": 60
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `detail` | `string` | ✅ | Human-readable description of the error |
| `error_code` | `string` | ✅ | Machine-readable error code (UPPER_SNAKE_CASE) |
| `request_id` | `string` | ✅ | UUID v4 — correlates to `X-Request-ID` response header |
| `timestamp` | `string` (ISO 8601) | ✅ | UTC timestamp of when the error occurred |
| `retry_after` | `integer` | ❌ | Seconds to wait before retrying (only on 429 and 503) |

### HTTP Status Code Conventions

| Status | Usage |
|---|---|
| `200 OK` | Successful GET, PUT, PATCH |
| `201 Created` | Successful POST (resource created) |
| `204 No Content` | Successful DELETE |
| `400 Bad Request` | Malformed request, business logic violation |
| `401 Unauthorized` | Missing or invalid authentication |
| `403 Forbidden` | Authenticated but not authorized |
| `404 Not Found` | Resource does not exist |
| `409 Conflict` | Dependency conflict, duplicate resource |
| `422 Unprocessable Entity` | Pydantic validation failure |
| `429 Too Many Requests` | Rate limit exceeded |
| `500 Internal Server Error` | Unexpected server failure |
| `503 Service Unavailable` | AI provider down, database unreachable |
| `504 Gateway Timeout` | AI response timeout |

---

## 2. HTTP 4xx — Client Errors

### AUTH_INVALID (401)

| Field | Value |
|---|---|
| **Error Code** | `AUTH_INVALID` |
| **HTTP Status** | 401 Unauthorized |
| **Description** | Invalid or expired authentication token |
| **Common Causes** | Token expired, wrong JWT secret, malformed token, tampered token |
| **Recovery Steps** | 1. Call `supabase.auth.refreshSession()` to obtain new token<br>2. Re-authenticate via Google OAuth<br>3. Verify `JWT_SECRET` env var matches Supabase JWT secret<br>4. Check `SUPABASE_JWT_SECRET` in Supabase Dashboard → Settings → API |

**Source:** `packages/config/core/auth.py:32` — `get_current_user()`

```python
# Thrown when:
# - Token is expired (exp claim exceeded)
# - Signature validation fails (wrong secret)
# - Token is malformed or tampered with
```

### AUTH_INSUFFICIENT (403)

| Field | Value |
|---|---|
| **Error Code** | `AUTH_INSUFFICIENT` |
| **HTTP Status** | 403 Forbidden |
| **Description** | Authenticated but not authorized for this operation |
| **Common Causes** | Wrong `user_id` in request, RLS policy blocks access, API key lacks permissions |
| **Recovery Steps** | 1. Verify `user_id` matches the authenticated user<br>2. Check RLS policies on the target table<br>3. If using API key, verify it has required scope<br>4. Check Supabase Dashboard → Authentication → Policies |

**Source:** RLS policy layer in Supabase + `get_current_user()` filtering

### AUTH_EXPIRED (401)

| Field | Value |
|---|---|
| **Error Code** | `AUTH_EXPIRED` |
| **HTTP Status** | 401 Unauthorized |
| **Description** | Token has expired and refresh failed |
| **Common Causes** | User inactive > refresh token expiry, session revoked |
| **Recovery Steps** | 1. Re-authenticate via Google OAuth<br>2. `supabase.auth.signOut()` then `signInWithOAuth()` |

### RATE_LIMITED (429)

| Field | Value |
|---|---|
| **Error Code** | `RATE_LIMITED` |
| **HTTP Status** | 429 Too Many Requests |
| **Description** | Request rate exceeded the allowed limit |
| **Common Causes** | Client sending requests too fast, abuse, misconfigured polling interval |
| **Recovery Steps** | 1. Read `Retry-After` response header (seconds to wait)<br>2. Implement exponential backoff in client<br>3. Reduce polling frequency for status endpoints<br>4. If legitimate traffic increase, adjust `RATE_LIMIT_MAX` in env |

**Source:** `packages/shared/utils/rate_limiter.py` — `RateLimiter.dispatch()`

**Configuration:**
| Setting | Default | Env Var |
|---|---|---|
| Global limit | 100 req/min | `RATE_LIMIT_MAX` / `RATE_LIMIT_WINDOW` |
| Chat endpoint | 30 req/min | Hardcoded in `EndpointRateLimiter` |
| AI automation | 10 req/min | Per-endpoint in `automation.py` |

```json
// 429 Response
{
  "detail": "Rate limit exceeded. Try again in 42 seconds.",
  "error_code": "RATE_LIMITED",
  "request_id": "uuid",
  "timestamp": "2026-07-11T12:00:00Z",
  "retry_after": 42
}
```

### RESOURCE_NOT_FOUND (404)

| Field | Value |
|---|---|
| **Error Code** | `RESOURCE_NOT_FOUND` |
| **HTTP Status** | 404 Not Found |
| **Description** | The requested resource does not exist |
| **Common Causes** | Wrong resource ID, resource already deleted, user_id mismatch, wrong endpoint path |
| **Recovery Steps** | 1. Verify the resource ID is correct<br>2. Check that the resource belongs to the authenticated user<br>3. Check if the resource was recently deleted (soft-delete not used)<br>4. Confirm the correct API version prefix (`/api/v1/`) |

**Source:** All 31 router `GET /{id}`, `PUT /{id}`, `DELETE /{id}` endpoints

```python
# Pattern used across all route files
data = supabase.table("tasks").select("*").eq("id", task_id).eq("user_id", user_id).execute()
if not data.data:
    raise HTTPException(status_code=404, detail="Task not found")
```

### VALIDATION_ERROR (422)

| Field | Value |
|---|---|
| **Error Code** | `VALIDATION_ERROR` |
| **HTTP Status** | 422 Unprocessable Entity |
| **Description** | Request body failed Pydantic validation |
| **Common Causes** | Missing required fields, wrong data types, string too long/short, invalid enum value |
| **Recovery Steps** | 1. Check error detail for specific field that failed<br>2. Validate request body against the schema at `database/schemas/`<br>3. Check OpenAPI spec at `/docs` for correct field types<br>4. Ensure required fields are present |

**Source:** FastAPI Pydantic validation layer + manual schema checks

```json
// 422 Response
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ],
  "error_code": "VALIDATION_ERROR",
  "request_id": "uuid",
  "timestamp": "2026-07-11T12:00:00Z"
}
```

### DEPENDENCY_ERROR (409)

| Field | Value |
|---|---|
| **Error Code** | `DEPENDENCY_ERROR` |
| **HTTP Status** | 409 Conflict |
| **Description** | Operation conflicts with current resource state |
| **Common Causes** | Circular task dependency, trying to complete already-completed task, duplicate resource creation |
| **Recovery Steps** | 1. Review dependency chain (tasks, projects, etc.)<br>2. Resolve circular dependencies before retrying<br>3. Check current resource status before mutation |

**Source:** Task completion (POST `/{id}/complete`), project dependency checks

### VALIDATION_BUSINESS (400)

| Field | Value |
|---|---|
| **Error Code** | `VALIDATION_BUSINESS` |
| **HTTP Status** | 400 Bad Request |
| **Description** | Valid JSON + valid types, but business logic rejects the value |
| **Common Causes** | End date before start date, duplicate title, invalid state transition |
| **Recovery Steps** | 1. Check the error `detail` for the specific business rule violated<br>2. Adjust input values to satisfy business constraints |

---

## 3. HTTP 5xx — Server Errors

### INTERNAL_ERROR (500)

| Field | Value |
|---|---|
| **Error Code** | `INTERNAL_ERROR` |
| **HTTP Status** | 500 Internal Server Error |
| **Description** | An unexpected error occurred on the server |
| **Common Causes** | Database query timeout, unhandled exception in route handler, Python runtime error, Sentry DSN misconfiguration |
| **Recovery Steps** | 1. Check server logs (Railway Dashboard or terminal)<br>2. Search for the `request_id` in logs to correlate<br>3. Retry the request (may be transient)<br>4. Report with reproduction steps and `request_id` |

**IMPORTANT:** Internal error details are NEVER exposed to the client. All 500 responses contain the generic `detail` message. Full stack traces are sent to Sentry.

### AI_PROVIDER_UNAVAILABLE (503)

| Field | Value |
|---|---|
| **Error Code** | `AI_PROVIDER_UNAVAILABLE` |
| **HTTP Status** | 503 Service Unavailable |
| **Description** | All AI providers (Ollama + Claude) are currently unavailable |
| **Common Causes** | Ollama service not running, circuit breaker OPEN, Claude API key invalid/missing, Claude API quota exceeded |
| **Recovery Steps** | 1. Check `GET /health/ready` endpoint for AI provider status<br>2. Verify Ollama is running: `ollama ps`<br>3. Check circuit breaker state: `python -c "from ai.client import llm; print(llm.ollama_circuit.state)"`<br>4. If circuit OPEN: wait for cooldown (default 60s)<br>5. If Claude unavailable: verify `CLAUDE_API_KEY` in `.env`<br>6. Restart FastAPI service to reset circuit breaker |

**Source:** `packages/ai/client.py` — `LLMClient.generate()` + `CircuitBreaker`

```python
# Error chain
LLMTimeoutError → httpx.RequestError → CircuitBreaker (OPEN) → LLMProviderUnavailableError
```

**Agent fallback behavior:**

| Agent | Fallback Result |
|---|---|
| BriefingAgent | Plain-text summary of today's tasks + habits |
| WeeklyReviewAgent | Calculated stats (completion rates, streaks) |
| OpportunityAgent | Sorted list of user's skills vs. available opportunities |
| SleepAgent | Static wind-down message |
| MemoryAgent | Skip memory consolidation (no-op) |
| TaskAgent | No breakdown — return task as-is |

### AI_TIMEOUT (504)

| Field | Value |
|---|---|
| **Error Code** | `AI_TIMEOUT` |
| **HTTP Status** | 504 Gateway Timeout |
| **Description** | AI provider did not respond within the configured timeout |
| **Common Causes** | Large prompt (exceeds token budget), model overloaded (Ollama), slow network (Claude API) |
| **Recovery Steps** | 1. Check AI response times: <br>   `python -c "from ai.client import llm; import asyncio; print(asyncio.run(llm.generate_json('test', system='test')))"`<br>2. Reduce prompt size if possible<br>3. Check Ollama model load: `ollama ps` — consider smaller model<br>4. Increase timeout: `OLLAMA_TIMEOUT` / `CLAUDE_TIMEOUT` env vars |

### DB_CONNECTION_ERROR (503)

| Field | Value |
|---|---|
| **Error Code** | `DB_CONNECTION_ERROR` |
| **HTTP Status** | 503 Service Unavailable |
| **Description** | Cannot connect to Supabase PostgreSQL database |
| **Common Causes** | Supabase project paused (free tier), network restriction blocking IP, service key expired, database maintenance |
| **Recovery Steps** | 1. Check Supabase Dashboard → Database → Status<br>2. Verify project is not paused (free tier pauses after 7 days inactive)<br>3. Check network restrictions in Supabase Dashboard<br>4. Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`<br>5. Restart the API service |

---

## 4. Recovery & Retry Strategies

### 4.1 Error Recovery Decision Tree

`mermaid
flowchart TD
    subgraph ERROR["Error Occurred"]
        E["HTTP 4xx or 5xx<br/>returned to client"]
    end

    subgraph DECISION["Recovery Decision"]
        D1{"Status Code Range"}
    end

    subgraph CLIENT["Client Errors (4xx)"]
        direction TB
        C1{"Which 4xx?"}
        C2["400 Bad Request<br/>Fix request payload"]
        C3["401/403 Auth<br/>Refresh token / re-authenticate"]
        C4["404 Not Found<br/>Verify resource ID"]
        C5["409 Conflict<br/>Retry with updated state"]
        C6["422 Validation<br/>Fix input fields"]
        C7["429 Rate Limited<br/>Exponential backoff retry"]
    end

    subgraph SERVER["Server Errors (5xx)"]
        direction TB
        S1{"Which 5xx?"}
        S2["500 Internal<br/>Retry with backoff<br/>Max 3 attempts"]
        S3["502 Bad Gateway<br/>Retry with backoff<br/>Circuit breaker"]
        S4["503 Unavailable<br/>Wait + retry<br/>Check status page"]
        S5["504 Gateway Timeout<br/>Retry with longer timeout"]
    end

    E --> D1
    D1 -->|"4xx"| C1
    D1 -->|"5xx"| S1

    C1 --> C2
    C1 --> C3
    C1 --> C4
    C1 --> C5
    C1 --> C6
    C1 --> C7

    S1 --> S2
    S1 --> S3
    S1 --> S4
    S1 --> S5

    style ERROR fill:#13151A,stroke:#EF4444,color:#F1F5F9,stroke-width:3px
    style DECISION fill:#0A0B0F,stroke:#334155,color:#F1F5F9
    style CLIENT fill:#13151A,stroke:#F59E0B,color:#F1F5F9
    style SERVER fill:#13151A,stroke:#EF4444,color:#F1F5F9
    style C7 fill:#13151A,stroke:#818CF8,color:#F1F5F9
    style S2 fill:#13151A,stroke:#00FFA3,color:#F1F5F9
    style S3 fill:#13151A,stroke:#00FFA3,color:#F1F5F9
    style S4 fill:#13151A,stroke:#F59E0B,color:#F1F5F9
    style S5 fill:#13151A,stroke:#818CF8,color:#F1F5F9
`

### By Error Code

| Error Code | Retryable | Strategy | Max Retries | Backoff |
|---|---|---|---|---|
| `AUTH_INVALID` | ❌ No | Re-authenticate | — | — |
| `AUTH_INSUFFICIENT` | ❌ No | Check permissions | — | — |
| `AUTH_EXPIRED` | ❌ No | Re-authenticate | — | — |
| `RATE_LIMITED` | ✅ Yes | Wait for `Retry-After` + exponential backoff | 3 | Linear (retry-after × attempt) |
| `RESOURCE_NOT_FOUND` | ❌ No | Verify resource ID | — | — |
| `VALIDATION_ERROR` | ❌ No | Fix request body | — | — |
| `DEPENDENCY_ERROR` | ⚠️ Conditional | Resolve dependency conflict | 1 | Manual |
| `VALIDATION_BUSINESS` | ❌ No | Fix business logic | — | — |
| `INTERNAL_ERROR` | ✅ Yes | Exponential backoff | 3 | 1s, 4s, 16s |
| `AI_PROVIDER_UNAVAILABLE` | ✅ Yes | Wait + check health | 3 (circuit breaker) | 2s, 4s, 8s + 60s cooldown |
| `AI_TIMEOUT` | ✅ Yes | Exponential backoff | 2 | 1s, 3s |
| `DB_CONNECTION_ERROR` | ✅ Yes | Exponential backoff | 3 | 1s, 5s, 25s |

### Global Retry Policy (AI Calls)

Implemented in `LLMClient` (`packages/ai/client.py`):

```python
# Retry configuration
max_retries = 3
base_delay = 2.0  # seconds

# Backoff sequence: 2s, 4s, 8s
# Circuit breaker: 5 failures → 60s cooldown
# Fallback: Ollama → Claude → algorithmic
```

### Client-Side Retry Guidance

```typescript
// Recommended client-side pattern for API calls
async function fetchWithRetry(url: string, options: RequestInit, retries = 3): Promise<Response> {
  for (let i = 0; i < retries; i++) {
    const response = await fetch(url, options);

    if (response.ok) return response;

    if (response.status === 429) {
      const retryAfter = parseInt(response.headers.get('Retry-After') || '60');
      await sleep(retryAfter * 1000);
      continue;
    }

    if (response.status >= 500 && response.status < 600) {
      await sleep(Math.pow(2, i) * 1000);  // 1s, 2s, 4s
      continue;
    }

    // Non-retryable error (400, 401, 403, 404, 422)
    throw new ApiError(await response.json());
  }
  throw new Error('Max retries exceeded');
}
```

---

## 5. How to Report New Errors

### Adding a New Error Code

1. **Add the error code** to this catalog in the appropriate section (4xx or 5xx)
2. **Update the schema** in `packages/database/schemas/error_response.py` if new fields needed
3. **Implement the error** in the route handler:
   ```python
   raise HTTPException(
       status_code=409,
       detail={
           "detail": "Human-readable explanation",
           "error_code": "NEW_ERROR_CODE",
           "request_id": request.state.request_id,
           "timestamp": datetime.now(timezone.utc).isoformat(),
       }
   )
   ```
4. **Log the error** with the request ID: `logger.error("NEW_ERROR_CODE: ...", extra={"request_id": request_id})`
5. **Update Sentry** severity if it's a recurring/predictable error (not `logging.ERROR` by default)

### Error Registration Checklist

- [ ] Error code follows `UPPER_SNAKE_CASE` convention
- [ ] Appropriate HTTP status code selected
- [ ] Error message is user-friendly (not technical)
- [ ] Retry strategy documented
- [ ] Recovery steps documented
- [ ] Error is logged with structured logger
- [ ] Tests added for the error path (200 + 400 + 404 model)
- [ ] This catalog updated with new error entry

---

## Appendix: Quick Reference

### Common Error Codes by Endpoint

| Endpoint | Most Common Error |
|---|---|
| `GET /api/v1/tasks` | `AUTH_INVALID` (401) |
| `POST /api/v1/tasks` | `VALIDATION_ERROR` (422) |
| `GET /api/v1/tasks/{id}` | `RESOURCE_NOT_FOUND` (404) |
| `POST /api/v1/tasks/{id}/complete` | `DEPENDENCY_ERROR` (409) |
| `POST /api/v1/chat` | `AI_PROVIDER_UNAVAILABLE` (503) |
| `POST /api/v1/automation/*` | `RATE_LIMITED` (429) |
| `DELETE /api/v1/*/{id}` | `RESOURCE_NOT_FOUND` (404) |

### Error Code Prefixes

| Prefix | Category |
|---|---|
| `AUTH_*` | Authentication & Authorization |
| `RATE_LIMITED` | Rate Limiting |
| `RESOURCE_*` | Resource Operations |
| `VALIDATION_*` | Input Validation |
| `DEPENDENCY_*` | Dependency & Conflict |
| `AI_*` | AI Provider & Timeout |
| `DB_*` | Database Connectivity |
| `INTERNAL_*` | Unexpected Errors |

---

## Related Documents

| Document | Purpose |
|---|---|
| [API Documentation](../17_API.md) | Full API endpoint reference — all 31 routers |
| [Webhook Guide](webhook-guide.md) | Real-time event notifications via webhooks |
| [Migration v1 to v2](migration-v1-to-v2.md) | Breaking changes and migration steps |
| [Error Budget](../../operations/error-budget.md) | SLO definitions and error budget policy |
| [OpenAPI Reference](openapi-reference.md) | Interactive API specification |
| [Rate Limiting](rate-limiting.md) | API rate limit policies and configuration |
| [AGENTS.md](../../../AGENTS.md) | Master project reference — Section 8 (API Endpoint Reference), Section 24 (API Versioning) |
