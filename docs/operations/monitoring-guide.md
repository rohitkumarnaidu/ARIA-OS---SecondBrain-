# Monitoring & Observability Guide â€” Second Brain OS

## Document Control

| Property | Value |
|---|---|
| **Document ID** | OPS-MNG-001 |
| **Version** | 1.0.0 |
| **Status** | Active |
| **Classification** | Internal â€” Operations |
| **Last Updated** | 2026-07-11 |
| **Review Cycle** | Monthly |

---

## Table of Contents

1. [Observability Pillars](#1-observability-pillars)
2. [Structured Logging](#2-structured-logging)
3. [Log Levels](#3-log-levels)
4. [RED Metrics](#4-red-metrics)
5. [Health Check Endpoints](#5-health-check-endpoints)
6. [Alerting Rules](#6-alerting-rules)
7. [Dashboard Definitions](#7-dashboard-definitions)
8. [Service Level Objectives (SLOs)](#8-service-level-objectives-slos)
9. [Log Retention Policy](#9-log-retention-policy)
10. [Monitoring Stack](#10-monitoring-stack)
11. [Runbook for Common Alerts](#11-runbook-for-common-alerts)
12. [Measuring RED Metrics](#12-measuring-red-metrics)

---

## 1. Observability Pillars

The monitoring strategy is built on four pillars:

| Pillar | What It Answers | Implementation | Tools |
|---|---|---|---|
| **Logging** | What happened? | Structured JSON logs, stdout + Logtail | `shared/utils/logger.py`, Logtail |
| **Metrics** | What is happening right now? | In-memory counters, Supabase snapshots, Prometheus textfile | Custom metrics middleware, `/health` |
| **Tracing** | Why did it happen? | X-Request-ID correlation across services | W3C Trace Context via HTTP headers |
| **Alerting** | When should I care? | Threshold evaluation, severity escalation | Scheduler alerting, Sentry, health checks |

### Data Flow

```
Request â†’ RateLimiter â†’ MIDDLEWARE [Request ID, Cache Control, CSRF]
                                  â†“
                       Route Handler (logs start/end with duration)
                                  â†“
                       Response (logs status, duration_ms, request_id)
                                  â†“
                       [Sentry] â† Exceptions
                       [Logtail] â† JSON logs
                       [Supabase] â† Token usage, agent activity
```

---

## 2. Structured Logging

Every log entry is a single-line JSON object written to stdout. The schema follows AGENTS.md Sec 25.2:

```json
{
  "timestamp": "2026-06-14T12:00:00.000Z",
  "level": "INFO",
  "message": "API Request",
  "endpoint": "/api/v1/tasks",
  "method": "GET",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "duration_ms": 42.5,
  "status_code": 200,
  "user_id": "user-uuid-here"
}
```

### Log Entry Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `timestamp` | ISO 8601 | Yes | When the event occurred |
| `level` | string | Yes | ERROR, WARN, INFO, DEBUG |
| `message` | string | Yes | Human-readable summary |
| `service` | string | Yes | Service name (api, scheduler, health-check) |
| `request_id` | UUID | For requests | Correlation ID for tracing |
| `endpoint` | string | For requests | URL path |
| `method` | string | For requests | HTTP method |
| `status_code` | int | For responses | HTTP status code |
| `duration_ms` | float | For timed ops | Duration in milliseconds |
| `user_id` | string | When available | Authenticated user ID |
| `error` | string | On errors | Error message / stack trace |
| `error_type` | string | On errors | Exception class name |

### Implementation

All logging goes through `packages/shared/utils/logger.py` (146 lines):

```python
from shared.utils.logger import logger, log_request, log_response

logger.info("Briefing generated", agent="briefing_agent", duration_ms=1234)
logger.error("Supabase query failed", error=exc, table="tasks")
logger.warn("Circuit breaker opened", provider="ollama", failures=5)

log_request(endpoint="/api/v1/tasks", method="GET", request_id=rid)
log_response(endpoint="/api/v1/tasks", method="GET", status_code=200, duration_ms=42.5, request_id=rid)
```

---

## 3. Log Levels

| Level | Usage | Example |
|---|---|---|
| **ERROR** | Failures requiring immediate attention | DB connection failed, AI provider down, unhandled exception |
| **WARN** | Degraded but functioning | Circuit breaker opened, retry attempt, fallback active, cron job slow (>5s) |
| **INFO** | Normal operations | Request completed, briefing generated, scheduler started, health check passed |
| **DEBUG** | Detailed troubleshooting | LLM prompt sent, cache hit/miss, query parameters |

### Log Level Configuration

The logger level is set via environment variable `LOG_LEVEL` (default: `INFO`). DEBUG level is automatically enabled when `DEBUG=true` in settings.

```bash
LOG_LEVEL=DEBUG  # Enables DEBUG-level logging
```

---

## 4. RED Metrics

The RED method (Rate, Errors, Duration) covers every endpoint and service.

### Rate â€” Requests per second

| Metric | Source | How to Measure |
|---|---|---|
| API request rate | Request ID middleware | Count of `log_request()` calls per time bucket |
| Requests per endpoint | Route path in logs | Group by `endpoint` field |
| AI calls per agent | Token usage table | Count rows in `token_usage` grouped by `agent` |
| Scheduler job executions | Cron job wrapper | Count `"Cron job completed"` log entries per job |

**Current measurement:** Backend counts token usage per time bucket in `GET /api/v1/monitoring/metrics`. The `rate.current` field returns requests/sec averaged over the selected period.

### Errors â€” Failed request rate

| Metric | Source | How to Measure |
|---|---|---|
| HTTP 5xx rate | Response status code | Count of `status_code >= 500` / total requests |
| HTTP 4xx rate | Response status code | Count of `status_code >= 400` / total requests |
| Agent failure rate | Agent activity log | Count of `status == "failed"` / total agent runs |
| Scheduler job failure rate | Failure tracker | Count of `record_failure()` calls per job |

**Current measurement:** Via `GET /api/v1/monitoring/metrics`. The `errors.current` field returns failure rate as percentage. The `agent_activity_log` table tracks per-agent success/failure.

### Duration â€” Response time percentiles

| Metric | Source | How to Measure |
|---|---|---|
| API p50/p95/p99 latency | Request ID middleware timing | Sort all `duration_ms` values, pick percentiles |
| AI response time | Token usage duration_ms | `duration_ms` field in `token_usage` table |
| Scheduler job duration | Cron job wrapper timing | `duration_ms` in log entries |
| DB query latency | Health check timing | `latency_ms` in health check response |

**Current measurement:** Via `GET /api/v1/monitoring/metrics`. Returns `duration.p50`, `duration.p95`, `duration.p99` with sparkline data and trend direction.

### Dashboard Endpoint

```bash
curl http://localhost:8000/api/v1/monitoring/metrics?period=24h
```

Response structure:
```json
{
  "rate": { "current": 0.05, "sparkline": [...], "trend": "up", "changePercent": 12.3 },
  "errors": { "current": 1.2, "sparkline": [...], "trend": "down", "changePercent": -5.1 },
  "duration": {
    "p50": { "current": 145, "sparkline": [...], "trend": "stable", "changePercent": 0.5 },
    "p95": { "current": 890, "sparkline": [...], "trend": "up", "changePercent": 8.2 },
    "p99": { "current": 2300, "sparkline": [...], "trend": "up", "changePercent": 15.0 }
  },
  "agents": [
    { "name": "briefing_agent", "calls": 30, "tokens": 45000, "avg_duration_ms": 12300, "error_rate": 0.0, "cost_usd": 0.0 }
  ],
  "services": {
    "api": { "status": "ok", "uptime": 99.9, "last_checked": "...", "latency_ms": 0 },
    "supabase": { "status": "ok", "uptime": 99.8, "last_checked": "...", "latency_ms": 12 },
    "ai": { "status": "ok", "uptime": 99.5, "last_checked": "...", "latency_ms": 45 }
  }
}
```

---

## 5. Health Check Endpoints

### `/health` â€” Overall Status

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "healthy",
  "version": "2.4.1",
  "environment": "development",
  "timestamp": 1720710000.0,
  "uptime_secs": 864000.0,
  "endpoints_registered": 214
}
```

**Checks:** None (returns process-level info only). Always returns 200 if the process is alive.

### `/health/live` â€” Liveness Probe

```bash
curl http://localhost:8000/health/live
```

```json
{ "status": "alive" }
```

**Use case:** Kubernetes/container liveness check. Always returns 200 if the process is running. No dependencies checked.

### `/health/ready` â€” Readiness Probe

```bash
curl http://localhost:8000/health/ready
```

```json
{
  "status": "healthy",
  "version": "2.4.1",
  "dependencies": {
    "api": { "status": "ok" },
    "supabase": { "status": "ok" },
    "ollama": { "status": "ok" }
  }
}
```

**Checks:**
1. **Supabase** â€” Executes `SELECT count(*) FROM users LIMIT 1`. Status: `ok`, `error`, or `degraded`.
2. **AI Provider** â€” If `USE_LOCAL_AI=true`: pings Ollama `/api/tags`. If `USE_LOCAL_AI=false`: checks `CLAUDE_API_KEY` is configured.
3. **Overall** â€” `healthy` if all deps pass, `degraded` otherwise.

**Cache-Control:** All `/health*` endpoints return `Cache-Control: no-store, no-cache, must-revalidate` (set by `cache_control_middleware` at line 370 of `main.py`).

### Scheduler Health

The scheduler runs its own health endpoint on port **8001**:

```bash
curl http://localhost:8001/health
curl http://localhost:8001/health/ready
```

The scheduler health status is written to a file (`health_status.json`) every 5 minutes by the health check cron job. The HTTP handler reads this file on each request. Response includes:
- `status`: healthy / degraded
- `service`: "scheduler"
- `scheduler.open_circuits`: List of circuits in OPEN state
- `scheduler.failing_jobs_count`: Jobs with consecutive failures
- `scheduler.total_daily_failures`: Cumulative failure count
- `jobs`: Current number of registered jobs

---

## 6. Alerting Rules

### Severity Framework

| Level | Label | Response SLA | Description |
|---|---|---|---|
| **P0** | Critical | 15 min response, 1 hr fix | Complete outage, data loss, security breach |
| **P1** | High | 30 min response, 4 hr fix | Major feature unavailable, >25% degradation |
| **P2** | Medium | 2 hr response, 24 hr fix | Partial degradation, <25% affected |
| **P3** | Low | 24 hr response, next sprint | Non-critical, cosmetic |

### Alert Rules

| ID | Alert | Condition | Severity | Channel | Action |
|---|---|---|---|---|---|
| ALR-001 | API Down | `/health` returns non-200 | **P0** | Log + Sentry + Email | Check Railway logs, verify deployment |
| ALR-002 | DB Connection Failed | `/health/ready` supabase status != ok | **P0** | Log + Sentry + Email | Check Supabase dashboard, verify IP allowlist |
| ALR-003 | Auth Broken | 401 errors > 20% of requests in 5 min | **P0** | Log + Sentry | Check JWT_SECRET, Supabase auth config |
| ALR-004 | High Error Rate | 5xx responses > 5% of total in 5 min | **P1** | Log + Sentry | Check recent deployments, rollback if needed |
| ALR-005 | AI Provider Failover | Ollama down + Claude API active | **P1** | Log + Sentry | Check Ollama service, restart if down |
| ALR-006 | p95 Latency > 2s | p95 response time exceeds 2s for 5 min | **P2** | Log + Sentry | Check for slow queries, AI call timeouts |
| ALR-007 | Circuit Breaker Open | Circuit breaker transitions to OPEN | **P1` | Log + Sentry | Check AI provider, wait for cooldown or reset |
| ALR-008 | Health Check Fail | `/health/ready` returns degraded | **P1** | Log + Sentry | Investigate failing dependency |
| ALR-009 | Rate Limit Threshold | 429 responses > 10% of requests in 5 min | **P2** | Log | Check for abusive traffic, adjust limits |
| ALR-010 | Scheduler Job Fail | Same cron job fails 3 consecutive times | **P2** | Log + Email | Check scheduler logs, restart service |
| ALR-011 | Sentence Job Missed | APScheduler detects missed run | **P2** | Log | Check scheduler load, adjust intervals |
| ALR-012 | Token Usage Spike | Daily tokens exceed 200% of 7-day avg | **P3` | Log | Review agent usage patterns, optimize prompts |
| ALR-013 | Sentry Event Quota | Monthly events > 80% of 5000 limit | **P3** | Log | Review error frequency, adjust sample rate |

### Alert Channels

| Channel | Configuration | Reliability | P0 Ready? |
|---|---|---|---|
| **Console log** (Railway/Vercel) | Always on | High | âœ… |
| **Sentry email alerts** | `SENTRY_DSN` env var | High | âœ… |
| **Logtail** | `LOGTAIL_SOURCE_TOKEN` env var | Medium | âš ï¸ |
| **Webhook (Slack/Discord)** | `ALERT_WEBHOOK_URL` env var | Medium | âš ï¸ |
| **Resend email** | Scheduler alerting module | Medium | âœ… |

### Suppression Rules

- **Dedup window**: Same alert type + same service suppressed for 30 minutes
- **Flapping detection**: Alert fires only after 3 consecutive positive checks
- **Cooldown**: 5-minute minimum interval between same alert type
- **Maintenance mode**: All alerts suppressed via feature flag `system.maintenance_mode`
- **Noise threshold**: If same alert fires 10+ times in 1 hour, reduce frequency automatically

---

## 7. Dashboard Definitions

### 7.1 API Overview Dashboard

**Purpose:** Quick health check â€” is the API serving requests normally?

| Panel | Metric | Query / Source |
|---|---|---|
| Request Rate | req/min | `GET /api/v1/monitoring/metrics` â†’ `rate.current` |
| Error Rate | % of 5xx | `GET /api/v1/monitoring/metrics` â†’ `errors.current` |
| p95 Latency | ms | `GET /api/v1/monitoring/metrics` â†’ `duration.p95.current` |
| Requests by Endpoint | Top-N endpoints | Parse log entries grouped by `endpoint` |
| HTTP Status Breakdown | 2xx vs 4xx vs 5xx | Grouped log entries |
| Health Status | healthy / degraded | `GET /health/ready` â†’ `status` |
| Service Uptime | % uptime this week | `GET /health` â†’ `uptime_secs` |

### 7.2 AI Performance Dashboard

**Purpose:** Monitor AI agent latency, token usage, and cost.

| Panel | Metric | Query / Source |
|---|---|---|
| Agent Calls | per agent per day | `token_usage` table grouped by `agent` |
| Avg Response Time | per agent | `token_usage.duration_ms` averaged |
| Total Tokens | prompt + completion | `token_usage.total_tokens` summed |
| Estimated Cost | USD | `token_usage.cost_usd` summed |
| Error Rate by Agent | % failed | `agent_activity_log` filtered by `status == "failed"` |
| AI Provider Status | ok / degraded | `GET /health/ready` â†’ `dependencies.ollama` / `claude_api` |
| Cache Hit Rate | % hits | `GET /api/v1/monitoring/ai-cache` â†’ `cache.hit_rate` |

### 7.3 System Health Dashboard

**Purpose:** Infrastructure-level view of all services.

| Panel | Metric | Query / Source |
|---|---|---|
| API Status | up / down | `GET /health` â†’ 200 check |
| Supabase Status | latency + reachable | `GET /health/ready` â†’ `dependencies.supabase` |
| AI Provider | ollama / claude status | `GET /health/ready` â†’ `dependencies.ollama` or `claude_api` |
| Scheduler Status | last tick + jobs count | `GET http://scheduler:8001/health` |
| Redis/Memory Cache | entry count | `cache.stats()` or `/health` cache check |
| Request ID Errors | failed requests tracked | Log entries with `level == "ERROR"` |

### 7.4 Business Metrics Dashboard

**Purpose:** Usage trends and user activity.

| Panel | Metric | Query / Source |
|---|---|---|
| Active Users | daily active users | `chat_messages` or `tasks` by `user_id` per day |
| Tasks Created | per day | `tasks` table count by `created_at` |
| Briefings Generated | per day | `daily_briefings` table count |
| Agent Activities | per agent per day | `agent_activity_log` count by `agent_name` |
| Total Token Usage | cumulative | `token_usage.total_tokens` summed over time |

### Grafana Dashboard

A pre-built Grafana dashboard is available at `monitoring/grafana-dashboard.json` with the following panels:
- Request Rate (stat, with threshold at 80/100 req/min)
- Error Rate % (stat, with threshold at 1%/5%)
- p95 Latency ms (stat, with threshold at 500ms/2000ms)
- Requests by Endpoint (bar gauge)
- HTTP Status Codes (pie chart)
- AI Response Time (time series, avg + max)

---

## 8. Service Level Objectives (SLOs)

| SLO | Target | Measurement | Window | Alert Severity |
|---|---|---|---|---|
| API Availability | **99.9%** uptime | Health check response rate | Rolling 30 days | P0 |
| API p95 Latency | **< 500ms** | Request duration percentiles | Rolling 5 min | P2 |
| AI Response p95 | **< 30s** | Token usage duration_ms | Rolling 1 hour | P2 |
| Error Rate | **< 1%** of all requests | 5xx / total requests | Rolling 5 min | P1 |
| Scheduler Job Success | **> 95%** of scheduled runs | Failure tracker stats | Rolling 7 days | P2 |
| AI Provider Uptime | **> 99%** (Ollama) | Health check /ready | Rolling 30 days | P1 |
| DB Query Latency | **< 200ms** p95 | Health check latency_ms | Rolling 5 min | P2 |
| Prompt Validation | **100%** pass rate | validate_prompts.py | Per commit | P3 |

### Error Budget

Monthly error budget = (1 - SLO) Ã— total requests. For API availability at 99.9%:
- ~7,000 requests/month â†’ max 7 failed requests before budget exhausted
- If budget exhausted: freeze non-critical deployments, focus on reliability

---

## 9. Log Retention Policy

| Log Type | Storage | Retention | Action After Retention |
|---|---|---|---|
| **API JSON logs** (stdout) | Railway console | 30 days | Automatically rotated by Railway |
| **API logs â†’ Logtail** | Logtail cloud | 30 days (free tier: 1 GB) | Auto-deleted by Logtail |
| **Scheduler logs** (stdout) | Railway console | 30 days | Automatically rotated |
| **Security events** (auth, audit) | Supabase `audit_log` table | 90 days | Manual archival, then cleanup |
| **Token usage** | Supabase `token_usage` table | 90 days | Cron job cleanup > 90 days |
| **Agent activity logs** | Supabase `agent_activity_log` | 90 days | Cron job cleanup > 90 days |
| **Sentry errors** | Sentry cloud | 90 days | Auto-deleted by Sentry free tier |
| **Health check history** | Scheduler health file | 7 days | Overwritten every 5 minutes |
| **Scheduler health status** | File on disk | Current only | Overwritten each check |
| **Frontend console logs** | Browser | Session only | Cleared on tab close |
| **Vercel logs** | Vercel dashboard | 7 days (free tier) | Auto-deleted by Vercel |

### Cleanup Implementation

The `skill_retention_cleanup` cron job runs daily at 2:30 AM and handles data retention for skill-related tables. For general log cleanup, extend this cron or create a dedicated cleanup job in `services/scheduler/crons/`.

---

## 10. Monitoring Stack

| Category | Tool | Free Tier | Configuration | Notes |
|---|---|---|---|---|
| **Error Tracking** | Sentry | 5k events/month | `SENTRY_DSN` env var (configured in `main.py` lines 143-155) | Frontend + backend both instrumented |
| **Log Aggregation** | Logtail (Better Stack) | 1 GB/month | `LOGTAIL_SOURCE_TOKEN` via `LogtailHandler` in `logger.py` | Async batch shipping every 5s |
| **Infrastructure** | Railway | Free starter plan | Railway dashboard | Logs, deploy history, resource usage |
| **Database** | Supabase | Free tier | Supabase dashboard | Query perf, table sizes, auth events |
| **Frontend Performance** | Lighthouse CI | Free | `.github/workflows/lighthouse.yml` | Run on every PR to main |
| **Uptime Monitoring** | UptimeRobot | 50 monitors, 5-min | `monitoring/uptimerobot-config.json` | Polls `/health`, `/health/ready`, frontend, scheduler |
| **Health Script** | Custom Python | Unlimited | `scripts/health-check.py` | Can output Prometheus format, Slack notifications |
| **RED Metrics** | Custom API | Unlimited | `GET /api/v1/monitoring/metrics` | Returns rate, errors, duration with sparklines |
| **Token Usage** | Custom API | Unlimited | `GET /api/v1/monitoring/token-usage/summary` | Tracks AI costs per agent |
| **Alerting** | Scheduler alerting module | Unlimited | `services/scheduler/alerting.py` | Multi-channel with rate limiting |
| **CI Security** | Trivy + npm audit | Unlimited | `.github/workflows/ci.yml` | Vulnerability scanning per commit |
| **Pen Testing** | OWASP ZAP + custom scripts | Unlimited | `scripts/zap-pentest.sh`, `scripts/attack-scenarios.py` | DAST + custom attack scenarios |

---

## 11. Runbook for Common Alerts

### ALR-001: API Down

**Symptoms:** `/health` returns non-200 or connection refused. UptimeRobot shows RED.

**Steps:**
1. Check Railway dashboard: `https://railway.app/project/...`
2. View recent deployments â€” did a deploy just happen?
3. Check logs for crash/startup errors
4. `curl http://localhost:8000/health` (if local) or `curl https://api.secondbrain-os.com/health`
5. **If deploy caused it:** Rollback to previous stable deploy:
   - Railway: Dashboard â†’ Deployments â†’ Previous â†’ Redeploy
6. **If OOM/crash:** Increase Railway plan or reduce memory usage
7. **If unknown:** Restart the service from Railway dashboard

### ALR-002: DB Connection Failed

**Symptoms:** `/health/ready` shows supabase status as `error`. API returns 500 on DB queries.

**Steps:**
1. Check Supabase dashboard: `https://supabase.com/dashboard/project/...`
2. Verify database is not in "Pausing" state (free tier pauses after 7 days inactivity)
3. Check if IP allowlist includes Railway's IP range
4. Verify `SUPABASE_URL` and `SUPABASE_KEY` environment variables
5. Try direct connection: `SELECT 1` in Supabase SQL Editor
6. **If paused:** Resume via Supabase dashboard (may take 30-60s)
7. **If credentials wrong:** Update env vars in Railway dashboard

### ALR-004: High Error Rate (>5%)

**Symptoms:** Error rate dashboard shows > 5% 5xx responses.

**Steps:**
1. Identify the failing endpoint: check `GET /api/v1/monitoring/metrics` â†’ endpoint breakdown
2. Check recent code changes: `git log --oneline -10`
3. Identify error pattern in logs: `grep "ERROR"` in Railway logs
4. Check Sentry for grouped exceptions
5. **If new deployment:** Rollback
6. **If DB issue:** Check Supabase query performance
7. **If AI provider:** Check Ollama status, verify fallback works

### ALR-005: AI Provider Failover Active

**Symptoms:** Ollama circuit breaker OPEN. Claude API being used as fallback.

**Steps:**
1. Check Ollama process: `ollama ps` (is model loaded? is the daemon running?)
2. Check Ollama logs: terminal running `ollama serve`
3. Check circuit breaker state: `python -c "from ai.client import llm; print(llm.ollama_circuit.state)"`
4. **If Ollama stopped:** `ollama serve` to restart
5. **If out of memory:** Kill other processes, `ollama stop` then restart
6. **If circuit breaker OPEN:** Wait 60s for auto-reset, or restart API service
7. Verify fallback is working: check Claude API key is valid, no rate limits

### ALR-007: Circuit Breaker Open

**Symptoms:** AI calls failing repeatedly. Logs show "Circuit breaker OPEN".

**Steps:**
1. Check which provider's circuit is open: `llm.ollama_circuit.state` or `llm.claude_circuit.state`
2. If Ollama: check Ollama service (see ALR-005)
3. If Claude: check `CLAUDE_API_KEY` is valid and has credits
4. Circuit will auto-reset after 60s cooldown
5. To force reset: restart the API service
6. Check for recent provider outages or API changes

### ALR-008: Health Check Fails (Degraded)

**Symptoms:** UptimeRobot reports degraded. `/health/ready` shows at least one dependency failing.

**Steps:**
1. Check `/health/ready` response to see which dependency failed
2. **If supabase error:** See ALR-002
3. **If ollama error:** See ALR-005
4. **If claude_api not_configured:** Set `CLAUDE_API_KEY` if fallback needed
5. If minor degradation (e.g., higher latency but still responding), no immediate action needed â€” monitor
6. Verify the health check itself isn't buggy: check `main.py` lines 480-517

### ALR-009: Rate Limit Threshold Exceeded

**Symptoms:** 429 responses > 10% of requests. Users getting "Too Many Requests".

**Steps:**
1. Check if legitimate traffic spike or abuse
2. Review IP-level rate limiting: `RATE_LIMIT_MAX` and `RATE_LIMIT_WINDOW` in settings
3. **If abuse:** Consider adding API key auth or stricter limits
4. **If legitimate:** Increase `RATE_LIMIT_MAX` (default: 100/min)
5. Check for misbehaving clients (e.g., polling too frequently)

### ALR-010: Scheduler Job Fails

**Symptoms:** Same cron job fails 3 times consecutively. Alert from scheduler alerting module.

**Steps:**
1. Check scheduler health: `curl http://localhost:8001/health`
2. View scheduler logs in Railway for the failing job
3. Check `failure_tracker` state for the job
4. **If API dependency:** Check API is healthy
5. **If AI agent fails:** Check AI provider (see ALR-005)
6. **If Supabase error:** Check DB (see ALR-002)
7. Restart scheduler: Railway dashboard â†’ Scheduler service â†’ Restart
8. If recurring, disable the job temporarily and investigate the root cause

---

## 12. Measuring RED Metrics

### Manual Measurement

```bash
# Get current RED metrics for the past 24 hours
curl http://localhost:8000/api/v1/monitoring/metrics?period=24h | python -m json.tool

# Check token usage summary
curl http://localhost:8000/api/v1/monitoring/token-usage/summary | python -m json.tool

# Check AI cache stats
curl http://localhost:8000/api/v1/monitoring/ai-cache | python -m json.tool

# Health check endpoints
curl http://localhost:8000/health
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
```

### Prometheus-Style Measurement (via health-check.py)

```bash
python scripts/health-check.py --prometheus
```

Output:
```
# HELP health_check_status Endpoint health status (1=up, 0=down)
# TYPE health_check_status gauge
health_check_status{endpoint="aria_os_api_health",url="https://api.secondbrain-os.com/health"} 1 1720710000
health_check_duration_ms{endpoint="aria_os_api_health",url="https://api.secondbrain-os.com/health"} 42.5 1720710000
```

### Grafana Dashboard Import

Import `monitoring/grafana-dashboard.json` into Grafana:
1. Grafana â†’ Dashboards â†’ New â†’ Import
2. Upload `monitoring/grafana-dashboard.json`
3. Configure Prometheus data source
4. The dashboard will show: Request Rate, Error Rate %, p95 Latency, Requests by Endpoint, HTTP Status Codes, AI Response Time

### Log-Based Measurement (no Prometheus)

If running without Prometheus, RED metrics can be derived from logs:

**Rate:**
```bash
# Count requests in the last hour
grep '"API Request"' railway.log | grep "$(date -u +'%Y-%m-%dT%H')" | wc -l
```

**Errors:**
```bash
# Count 5xx responses
grep '"API Response"' railway.log | grep '"status_code": 5' | wc -l
```

**Duration:**
```bash
# Extract all durations, sort, pick 95th percentile
grep '"API Response"' railway.log | grep -oP '"duration_ms": \K[0-9.]+' | sort -n | awk '{a[i++]=$1} END {print a[int(i*0.95)]}'
```

---

## References

| Document | Description |
|---|---|
| [AGENTS.md](../../AGENTS.md) | Master reference â€” Sec 25 Observability & Monitoring |
| [32_Monitoring.md](./32_Monitoring.md) | Original monitoring architecture document |
| [31_Observability.md](./31_Observability.md) | Observability strategy and three pillars |
| [Alerts.md](./Alerts.md) | Alerting system specification |
| [Sentry.md](./Sentry.md) | Sentry error tracking setup |
| [39_Runbooks.md](./39_Runbooks.md) | General operations runbooks |
| [40_IncidentResponse.md](./40_IncidentResponse.md) | Incident response procedures |
| [43_SLA.md](./43_SLA.md) | Service level agreement definitions |
| [monitoring/grafana-dashboard.json](../../monitoring/grafana-dashboard.json) | Pre-built Grafana RED metrics dashboard |
| [monitoring/uptimerobot-config.json](../../monitoring/uptimerobot-config.json) | UptimeRobot monitor configuration |
| [scripts/health-check.py](../../scripts/health-check.py) | External health check script |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-07-11 | AI Agent | Initial monitoring guide: pillars, logging, RED metrics, health checks, alerting, dashboards, SLOs, retention, stack, runbooks |
