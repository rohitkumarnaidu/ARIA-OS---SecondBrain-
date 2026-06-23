# Architecture Update — Phase 4: Enterprise Hardening

| Field | Value |
|---|---|
| Document ID | SB-ARCH-UPDATE-046 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-06-21 |
| Classification | Internal — Engineering |
| Owner | Engineering Lead |

---

## 1. API Key Authentication System

Authenticate via `X-API-Key` header. Keys are SHA-256 hashed before storage (never stored in plaintext). Supports multiple keys per user with rotation and revocation.

```
Request: POST /api/v1/tasks
Headers: X-API-Key: sb_key_abc123...
         Content-Type: application/json

Flow: Key → SHA-256 hash → Compare against stored hash → Resolve user_id → Execute request
```

**Config:** `API_KEY_SALT` env var, key prefix `sb_key_`, stored in `api_keys` table.

## 2. GDPR Data Export

`GET /api/v1/gdpr/export` returns a JSON archive of all 18 user tables: tasks, courses, goals, habits, habit_logs, sleep_logs, income_entries, projects, ideas, resources, opportunities, time_entries, chat_messages, daily_briefings, weekly_reviews, memory, learning_progress, users. Packaged as a `data-export-{user_id}-{timestamp}.json` download.

## 3. Data Retention Policy

| Data Type | Retention | Cleanup |
|---|---|---|
| Chat messages | 90 days | APScheduler daily job |
| Analytics events | 90 days | APScheduler daily job |
| Habit logs | 365 days | APScheduler weekly job |
| Time entries | 365 days | APScheduler weekly job |
| Daily briefings | 90 days | APScheduler daily job |
| User profile | Until account deletion | Manual / GDPR delete |

**Env var:** `DATA_RETENTION_DAYS` (default: 90). Cleanup runs via scheduled cron in `services/scheduler/crons/data_retention.py`.

## 4. Rate Limiter with Headers

Per-IP rate limiter returns RFC 6585 standard headers on every response:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1687359600
Retry-After: 45  (only on 429 responses)
```

Configurable via `RATE_LIMIT_MAX` (default: 100) and `RATE_LIMIT_WINDOW` (default: 60s). Whitelist support for internal IPs. Per-endpoint overrides (e.g., `/api/v1/chat` limited to 30 req/min).

## 5. Audit Logging Middleware

Every data mutation (POST, PUT, DELETE) is logged to `audit_logs` table:

```json
{
  "timestamp": "2026-06-21T12:00:00Z",
  "user_id": "uuid",
  "action": "CREATE / UPDATE / DELETE",
  "table": "tasks",
  "record_id": "uuid",
  "old_values": { ... },
  "new_values": { ... },
  "ip_address": "203.0.113.1",
  "user_agent": "Mozilla/5.0..."
}
```

Controlled by `AUDIT_LOG_ENABLED` env var (default: True). Queries via `/api/v1/admin/audit-logs` (admin-only).

## 6. CSRF Protection

Double-submit cookie pattern:
1. Server sets `csrf_token` cookie (HttpOnly, Secure, SameSite=Strict)
2. Client reads cookie, sends `X-CSRF-Token` header
3. Server validates header matches cookie

Controlled by `CSRF_ENABLED` env var (default: True). Skipped for `GET`, `HEAD`, `OPTIONS` and API key-authenticated requests.

## 7. Graceful Shutdown

`app.add_event_handler("shutdown", graceful_shutdown)` performs:
- Drain active connections (max 30s wait)
- Cancel pending AI requests
- Flush audit log buffer
- Close Supabase connection pool
- Log shutdown event with duration

## 8. Input Sanitization & XSS Protection

All user input sanitized via `shared/utils/validators.py`:
- Strip HTML tags from text fields (`strip_tags`)
- Validate email format (`validate_email`)
- Sanitize file uploads (type + size check)
- Escape output in API responses (JSON serialization is safe)
- CSP headers on all frontend pages

## 9. Circuit Breaker & Retry Logic

All AI calls wrapped in `packages/shared/utils/retry.py`:

```
┌──────────┐    Success → ┌──────────┐
│  CLOSED  │─────────────▶│  CLOSED  │
│ (normal) │              │ (normal) │
└─────┬────┘              └──────────┘
      │ 5 failures
      ▼
┌──────────┐    Timeout → ┌──────────┐
│   OPEN   │─────────────▶│ HALF-OPEN│
│ (60s CD) │   (60s)     │ (testing)│
└──────────┘              └─────┬────┘
                               │ Success
                               ▼
                          ┌──────────┐
                          │  CLOSED  │
                          │ (normal) │
                          └──────────┘
```

- **Retry:** 3 attempts with exponential backoff (2s, 4s, 8s)
- **Circuit breaker:** Opens after 5 consecutive failures, 60s cooldown
- **Fallback:** Ollama → Claude → algorithmic fallback

## 10. Testing & Coverage

| Metric | Phase 3 | Phase 4 |
|---|---|---|
| Total tests | 477 | 1,450 |
| Coverage (overall) | 71% | 98.99% |
| Coverage (packages/ai/) | 93% | 100% |
| Coverage (packages/shared/) | 96% | 100% |
| Coverage (packages/config/) | 79% | 100% |
| Coverage (apps/api/) | 52% | 97% |
| E2E tests | 0 | 5 (Playwright) |

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-21 | Engineering Lead | Initial Phase 4 architecture update |
