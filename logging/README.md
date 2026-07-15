# Log Aggregation Configuration

## Overview

Second Brain OS logs structured JSON to stdout via `packages/shared/utils/logger.py`. This directory contains configs for optional log aggregation services.

## Options

### 1. Logtail (Better Stack) — Free Tier

Logtail is the recommended starting point: free 1GB/month, 7-day retention, search + alerting.

**Setup:**

1. Create a free account at https://betterstack.com/logtail
2. Create a **Log Source** → pick "Python / Django"
3. Copy the **Source Token**
4. Set env var: `LOGTAIL_SOURCE_TOKEN=your-token`

**The logger auto-detects this var and starts shipping logs in batches (every 5s or 10 logs).** No code changes needed beyond the env var.

**Config:** `logging/logtail-config.json`

### 2. Datadog — Paid

Full-featured observability: logs, metrics, traces, dashboards, SLOs, alerting.

**Setup:**

1. Sign up at https://www.datadoghq.com
2. Get an API key from **Organization Settings → API Keys**
3. Set env vars:
   - `DD_API_KEY=your-key`
   - `DD_SITE=datadoghq.com`
4. Install `ddtrace`: `pip install ddtrace`
5. Run with: `ddtrace-run python -m uvicorn main:app`

**Config:** `logging/datadog-config.json`

### 3. Local Loki + Grafana — Free, Self-Hosted

Run a local log stack with Docker for development or air-gapped environments.

**Setup:**

```bash
docker compose -f logging/docker-compose.logging.yml up -d
```

Then open Grafana at **http://localhost:3001** — no login required.

1. Go to **Connections → Data Sources → Add data source**
2. Pick **Loki**
3. Set URL to `http://loki:3100`
4. Click **Save & Test**
5. Go to **Explore**, select Loki, query `{service="secondbrain-api"}`

**Components:**

| Service | Port | Purpose |
|---------|------|---------|
| Loki | 3100 | Log storage and query engine |
| Promtail | 9080 | Log scraper (reads Docker container logs) |
| Grafana | 3001 | Dashboards and alerting |

## How Log Shipping Works

### Logtail Handler (`LogtailHandler` in `logger.py`)

- On first log, creates an `httpx.AsyncClient` pointed at `https://in.logtail.com`
- Log records are batched in-memory (thread-safe via `asyncio.Lock`)
- Flush triggers: **every 5 seconds** OR **every 10 logs**
- On failure: silently catches exceptions — the app never crashes from log shipping failures
- If `LOGTAIL_SOURCE_TOKEN` is not set: no-op (logs only go to stdout)

## Structured Log Schema

All logs (console + Logtail) follow the same schema:

```json
{
  "timestamp": "2026-07-09T23:00:00.000Z",
  "level": "INFO",
  "message": "API Request",
  "endpoint": "/api/v1/tasks",
  "method": "GET",
  "user_id": "uuid",
  "request_id": "uuid",
  "duration_ms": 42.5,
  "service": "secondbrain-api"
}
```

## Search Examples

**Logtail:** `level:ERROR` | `service:secondbrain-api` | `endpoint:"/api/v1/chat"`

**Grafana/Loki:** `{service="secondbrain-api"} |= "ERROR"` | `{container="secondbrain-api-1"}`

## Alerting Ideas

| Alert | Condition | Severity |
|-------|-----------|----------|
| High error rate | `level:ERROR` rate > 5/min over 5 min | Critical |
| Slow responses | `duration_ms > 2000` | Warning |
| Auth failures | `status_code:401` > 10/min | High |
| AI circuit breaker open | `message:"Circuit breaker OPEN"` | Critical |

## Pricing Comparison

| Service | Free Tier | Paid Starts At | Retention | Key Features |
|---------|-----------|----------------|-----------|--------------|
| **Logtail** | 1 GB/month | $15/mo (15 GB) | 7 days free, 30 days paid | Search, alerts, teams |
| **Datadog** | None | $15/host/mo (1M logs) | 7 days default | APM, traces, RUM, SLOs |
| **Loki + Grafana** | Unlimited (self-hosted) | Free | Configurable | Full control, air-gapped |

## Env Variables

See `.env.example`:

```
LOGTAIL_SOURCE_TOKEN=
DD_API_KEY=
DD_SITE=datadoghq.com
```