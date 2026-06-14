---
version: 2.0.0
status: active
classification: Internal — Engineering
author: AI Agent System
last_updated: 2026-06-11
review_cycle: monthly
document_id: SB-OPS-MON-001
related_docs:
  - docs/operations/30_Analytics.md
  - docs/operations/31_Observability.md
  - docs/engineering/45_PerformanceScalability.md
  - docs/operations/39_Runbooks.md
  - docs/operations/40_IncidentResponse.md
---

# Monitoring & Observability

## Document Control

| Field | Value |
|---|---|
| Document ID | SB-OPS-MON-001 |
| Version | 2.0.0 |
| Status | Active |
| Classification | Internal — Engineering |
| Last Updated | 2026-06-11 |
| Review Cycle | Monthly |
| Owner | Engineering Team |
| Related Docs | Analytics, Observability, Performance & Scalability, Runbooks, Incident Response |

---

## Executive Summary

This document defines the complete monitoring and observability strategy for Second Brain OS. The system uses lightweight, free-tier tools exclusively to maintain the Rs. 0 / $0 budget commitment while providing adequate coverage across five pillars: **system health**, **application performance**, **user experience**, **AI reliability**, and **cost tracking**.

**Monitoring Philosophy:**
- **Alert on symptoms, not causes** — Notify when users are impacted, not when internal metrics fluctuate
- **Free-tier first** — Every tool must have a viable free tier; paid upgrades are justified only by proven need
- **Self-healing over paging** — Automate recovery before alerting humans
- **Progressive escalation** — Warn → Alert → Critical → Page with increasing urgency

**Coverage Summary:**

| Pillar | Coverage | Tools |
|---|---|---|
| System Health | API, DB, Auth, Cache, Scheduler | Health endpoint, Better Uptime |
| Application Performance | Response times, error rates, throughput | Metrics middleware, Supabase Insights |
| User Experience | Core Web Vitals, page load, navigation | Frontend PerfMonitor, Browser DevTools |
| AI Reliability | Ollama status, Claude API, prompt latency | Health checks, prompt validation script |
| Cost Tracking | DB storage, bandwidth, email, API costs | Cost monitor cron, budget alerts |
| Security | Auth failures, rate limit violations, audit log | Rate limiter, audit events |

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [System Health Monitoring](#2-system-health-monitoring)
3. [Application Performance Monitoring](#3-application-performance-monitoring)
4. [User Experience Monitoring](#4-user-experience-monitoring)
5. [AI Reliability Monitoring](#5-ai-reliability-monitoring)
6. [Cost Tracking & Budget Alerts](#6-cost-tracking--budget-alerts)
7. [Logging Strategy](#7-logging-strategy)
8. [Alerting & Escalation](#8-alerting--escalation)
9. [Dashboard Implementation](#9-dashboard-implementation)
10. [Error Tracking](#10-error-tracking)
11. [Distributed Tracing](#11-distributed-tracing)
12. [Security Monitoring](#12-security-monitoring)
13. [SLO / SLI / SLA Framework](#13-slo--sli--sla-framework)
14. [Incident Response Integration](#14-incident-response-integration)
15. [Tool Reference & Setup](#15-tool-reference--setup)
16. [Implementation Roadmap](#16-implementation-roadmap)
17. [Appendices](#17-appendices)

---

## 1. Architecture Overview

### 1.1 Monitoring Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    MONITORING LAYER                          │
│                                                              │
│  ┌──────────────────┐   ┌──────────────────┐                │
│  │  External Probes   │   │  Built-in Health  │              │
│  │  (Better Uptime)   │   │  (FastAPI Endpoint)│             │
│  └────────┬─────────┘   └────────┬─────────┘                │
│           │                      │                          │
│  ┌────────▼──────────────────────▼─────────┐                │
│  │         Alert Manager                    │                │
│  │  (Email / SMS / Slack Webhook)           │                │
│  └────────────────┬────────────────────────┘                │
│                   │                                          │
│  ┌────────────────▼────────────────────────┐                │
│  │      Data Storage Layer                  │                │
│  │  ┌──────────┐  ┌──────────┐  ┌───────┐  │               │
│  │  │Supabase  │  │ Logs     │  │Analytics│  │             │
│  │  │Metrics   │  │(Logger)  │  │Events   │  │              │
│  │  └──────────┘  └──────────┘  └───────┘  │               │
│  └──────────────────────────────────────────┘               │
│                                                              │
│  ┌──────────────────────────────────────────┐                │
│  │         Visualization Layer               │               │
│  │  ┌────────────┐  ┌────────────┐          │              │
│  │  │Status Page │  │Supabase    │          │               │
│  │  │(Built-in)  │  │Dashboard   │          │               │
│  │  └────────────┘  └────────────┘          │               │
│  └──────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow

```
User Request → API Gateway → Metrics Middleware → Route Handler
                                    │
                            ┌───────┴───────┐
                            │               │
                     Performance         Business
                     Metrics              Events
                            │               │
                            └───────┬───────┘
                                    │
                            Alert Manager
                                    │
                          ┌─────────┴────────┐
                          │                  │
                    Auto-Recovery        Human
                    (Retry, Failover)    Alert
```

### 1.3 Tool Selection Criteria

| Requirement | Chosen Tool | Free Tier | Alternative |
|---|---|---|---|
| Uptime monitoring | Better Uptime | 3 URLs, 1-min checks | UptimeRobot (50 URLs, 5-min) |
| API metrics | Custom middleware | Unlimited | New Relic (100GB/mo free) |
| Error tracking | Custom logger | Unlimited | Sentry (5k events/mo free) |
| Logging | Custom structured logger | Unlimited | Logtail (1GB/mo free) |
| Cost tracking | Custom cron | Unlimited | — |
| Performance | Supabase Insights | Built-in | — |
| Alerting | Custom AlertManager | Unlimited | PagerDuty (5 users free) |
| Dashboards | Built-in status page | Unlimited | Grafana (free tier) |

---

## 2. System Health Monitoring

### 2.1 Health Endpoint

A dedicated `/api/health` endpoint provides a comprehensive system health check. It is polled by external uptime monitors and internal cron jobs.

**Endpoint:** `GET /api/health`

**Response Schema:**
```json
{
  "status": "healthy" | "degraded" | "unhealthy",
  "timestamp": "2026-06-11T09:15:30Z",
  "version": "2.4.1",
  "uptime_seconds": 864000,
  "checks": {
    "database": {
      "status": "healthy" | "degraded" | "unhealthy",
      "latency_ms": 12,
      "details": "Connected to supabase. 18 tables accessible."
    },
    "supabase_auth": {
      "status": "healthy",
      "latency_ms": 45,
      "details": "Auth service responsive."
    },
    "ollama": {
      "status": "degraded",
      "latency_ms": null,
      "error": "Ollama not running. Claude fallback active.",
      "details": "AI service running in degraded mode."
    },
    "cache": {
      "status": "healthy",
      "entry_count": 127,
      "hit_rate_pct": 68.3,
      "details": "In-memory cache operational."
    },
    "scheduler": {
      "status": "healthy",
      "last_tick": "2026-06-11T09:14:00Z",
      "details": "APScheduler running. 6 jobs registered."
    },
    "disk": {
      "status": "healthy",
      "usage_pct": 42.5,
      "details": "Disk usage within limits."
    }
  }
}
```

**Implementation:**
```python
# apps/api/app/api/health.py
import time
from datetime import datetime, timedelta
from fastapi import APIRouter
from config.core.supabase import get_supabase_client
from shared.utils.cache import cache

router = APIRouter(prefix="/api", tags=["health"])

class HealthCheckService:
    def __init__(self):
        self.start_time = time.time()
        self.check_history = []

    async def check_database(self) -> dict:
        start = time.time()
        try:
            supabase = get_supabase_client()
            result = supabase.from_("users").select("count", count="exact").execute()
            latency = round((time.time() - start) * 1000)
            return {
                "status": "healthy" if latency < 500 else "degraded",
                "latency_ms": latency,
                "details": f"Connected. Query returned {result.count if hasattr(result, 'count') else 'N/A'} rows."
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "latency_ms": round((time.time() - start) * 1000),
                "error": str(e)[:200],
                "details": "Database connection failed."
            }

    async def check_auth(self) -> dict:
        start = time.time()
        try:
            supabase = get_supabase_client()
            # Lightweight auth check - ping the auth endpoint
            supabase.auth.get_user("health-check")
            latency = round((time.time() - start) * 1000)
            return {
                "status": "healthy" if latency < 1000 else "degraded",
                "latency_ms": latency,
                "details": "Auth service responsive."
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "latency_ms": round((time.time() - start) * 1000),
                "error": str(e)[:200],
                "details": "Auth service unreachable."
            }

    async def check_ollama(self) -> dict:
        start = time.time()
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get("http://localhost:11434/api/tags")
                if resp.status_code == 200:
                    models = resp.json().get("models", [])
                    return {
                        "status": "healthy",
                        "latency_ms": round((time.time() - start) * 1000),
                        "details": f"Ollama running. {len(models)} models available."
                    }
                return {
                    "status": "degraded",
                    "latency_ms": round((time.time() - start) * 1000),
                    "details": "Ollama responded but with unexpected status.",
                    "error": f"HTTP {resp.status_code}"
                }
        except Exception:
            return {
                "status": "degraded",
                "latency_ms": None,
                "error": "Ollama not running.",
                "details": "AI service will use Claude API fallback."
            }

    async def check_cache(self) -> dict:
        try:
            stats = cache.get_stats()
            return {
                "status": "healthy",
                "entry_count": stats.get("entry_count", 0),
                "hit_rate_pct": round(stats.get("hit_rate", 0) * 100, 1),
                "details": f"{stats.get('entry_count', 0)} entries cached."
            }
        except Exception as e:
            return {
                "status": "degraded",
                "error": str(e)[:200],
                "details": "Cache check failed."
            }

    def get_uptime(self) -> int:
        return int(time.time() - self.start_time)

health_service = HealthCheckService()


@router.get("/health")
async def health_check():
    checks = {
        "database": await health_service.check_database(),
        "supabase_auth": await health_service.check_auth(),
        "ollama": await health_service.check_ollama(),
        "cache": await health_service.check_cache(),
    }

    # Determine overall status
    statuses = [c.get("status") for c in checks.values()]
    if "unhealthy" in statuses:
        overall = "unhealthy"
    elif "degraded" in statuses:
        overall = "degraded"
    else:
        overall = "healthy"

    return {
        "status": overall,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.4.1",
        "uptime_seconds": health_service.get_uptime(),
        "checks": checks,
    }
```

### 2.2 Auto-Recovery Actions

When a health check fails, the system attempts automatic recovery before alerting:

| Component | Failure Symptom | Auto-Recovery | Fallback |
|---|---|---|---|
| Database | Timeout > 5s | Retry with backoff (3 attempts, 1s/2s/4s) | Return cached data |
| Auth | HTTP 401/403 | Refresh JWT, re-authenticate | Use cached session |
| Ollama | Connection refused | Retry 1x after 2s | Route to Claude API |
| Ollama | Timeout > 30s | Abort, mark degraded | Route to Claude API |
| Cache | Corruption detected | Clear and rebuild | Bypass cache |
| Scheduler | Job timeout > 60s | Restart job with backoff | Skip tick, log warning |

### 2.3 External Uptime Monitoring

**Primary: Better Uptime** (Free Tier)
- 3 monitored URLs: `https://api.ariaos.app/api/health`, `https://ariaos.app`, `https://scheduler.ariaos.app/health`
- 1-minute check intervals
- Email + Slack notifications on downtime
- Public status page: `https://status.ariaos.app`

**Backup: UptimeRobot** (Free Tier)
- 50 monitored URLs (for future expansion)
- 5-minute check intervals
- Email notifications only

**Heartbeat Monitoring:**
```python
# services/scheduler/crons/heartbeat.py
async def send_heartbeat():
    """Send a heartbeat signal to Better Uptime every 5 minutes."""
    heartbeat_url = os.getenv("BETTER_UPTIME_HEARTBEAT_URL")
    if not heartbeat_url:
        return
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            await client.get(heartbeat_url)
            logger.info("Heartbeat sent successfully")
        except Exception as e:
            logger.error("Heartbeat failed", error=str(e))
```

---

## 3. Application Performance Monitoring

### 3.1 Metrics Collector Middleware

A lightweight in-memory metrics collector tracks API response times, error rates, and throughput. Data is stored in memory (last 1000 measurements per endpoint) and periodically persisted to Supabase for historical analysis.

```python
# apps/api/middleware/metrics.py
import time
from collections import defaultdict, deque
from datetime import datetime
from typing import Dict, List, Optional

class MetricsCollector:
    """Collects and stores API performance metrics in memory."""

    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self.endpoints: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_samples)
        )
        self.errors: Dict[str, int] = defaultdict(int)
        self.status_codes: Dict[str, Dict[int, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self.last_flush: Optional[datetime] = None

    def record(
        self,
        endpoint: str,
        method: str,
        duration_ms: float,
        status_code: int,
        error: bool = False,
    ):
        key = f"{method} {endpoint}"
        self.endpoints[key].append({
            "duration_ms": duration_ms,
            "timestamp": time.time(),
            "status_code": status_code,
        })
        self.status_codes[key][status_code] += 1
        if error:
            self.errors[key] += 1

    def get_stats(self, endpoint: Optional[str] = None) -> dict:
        """Get aggregated statistics for one or all endpoints."""
        if endpoint:
            keys = [endpoint]
        else:
            keys = list(self.endpoints.keys())

        result = {}
        for key in keys:
            samples = list(self.endpoints.get(key, []))
            if not samples:
                result[key] = {"count": 0}
                continue

            times = [s["duration_ms"] for s in samples]
            sorted_times = sorted(times)
            n = len(sorted_times)

            # Count errors in last 5 minutes
            recent_cutoff = time.time() - 300
            recent_errors = sum(
                1 for s in samples
                if s["timestamp"] > recent_cutoff and s.get("error", False)
            )
            recent_total = sum(1 for s in samples if s["timestamp"] > recent_cutoff)

            result[key] = {
                "count": n,
                "p50": sorted_times[n // 2],
                "p95": sorted_times[int(n * 0.95)],
                "p99": sorted_times[int(n * 0.99)],
                "max": max(times),
                "min": min(times),
                "avg": sum(times) / n,
                "error_rate_pct": round(recent_errors / max(recent_total, 1) * 100, 2),
                "status_codes": dict(self.status_codes.get(key, {})),
            }
        return result.get(endpoint, result) if endpoint else result

    def flush_to_db(self, supabase):
        """Periodically persist metrics to Supabase analytics_events table."""
        timestamp = datetime.utcnow().isoformat()
        for endpoint, stats in self.get_stats().items():
            if stats.get("count", 0) == 0:
                continue
            event = {
                "event_name": "api_metrics_snapshot",
                "timestamp": timestamp,
                "properties": {
                    "endpoint": endpoint,
                    **stats,
                },
            }
            supabase.table("analytics_events").insert(event).execute()
        self.last_flush = datetime.utcnow()

metrics = MetricsCollector()


# Middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
        duration = (time.time() - start) * 1000
        metrics.record(
            endpoint=request.url.path,
            method=request.method,
            duration_ms=duration,
            status_code=response.status_code,
            error=response.status_code >= 500,
        )
        return response
    except Exception as e:
        duration = (time.time() - start) * 1000
        metrics.record(
            endpoint=request.url.path,
            method=request.method,
            duration_ms=duration,
            status_code=500,
            error=True,
        )
        raise
```

### 3.2 Database Query Performance

**Supabase Query Performance Insights** (built-in):
- Navigate to: Supabase Dashboard → Database → Query Performance
- Shows: slowest queries, most frequent queries, query plans
- Retention: 24 hours of query history

**Application-Level Tracking:**
```python
class QueryTracker:
    """Tracks database query performance at the application level."""

    def __init__(self, threshold_ms: int = 500):
        self.queries: deque = deque(maxlen=1000)
        self.threshold_ms = threshold_ms

    async def track(
        self,
        table: str,
        operation: str,
        duration_ms: float,
        row_count: int = 0,
        query_preview: str = "",
    ):
        entry = {
            "table": table,
            "operation": operation,
            "duration_ms": duration_ms,
            "row_count": row_count,
            "timestamp": datetime.utcnow().isoformat(),
            "query_preview": query_preview[:100],  # Truncate for privacy
        }
        self.queries.append(entry)

        if duration_ms > self.threshold_ms:
            logger.warning("Slow query detected", **entry)

    def get_slow_queries(self, min_duration_ms: int = 200) -> List[dict]:
        return [
            q for q in self.queries
            if q["duration_ms"] >= min_duration_ms
        ][-50:]  # Last 50 slow queries

query_tracker = QueryTracker()
```

### 3.3 Performance Thresholds

| Metric | Warning | Critical | Action |
|---|---|---|---|
| API p95 response time | > 500ms | > 1000ms | Investigate endpoint, add caching |
| API p99 response time | > 1000ms | > 2000ms | Profile and optimize |
| API error rate | > 1% | > 5% | Rollback or hotfix |
| Database query latency | > 200ms | > 500ms | Add index or optimize query |
| Database connection pool | > 80% | > 95% | Scale connection pool |
| AI prompt latency (Ollama) | > 10s | > 30s | Fallback to Claude or retry |
| Cache hit rate | < 50% | < 20% | Review caching strategy |
| Frontend page load | > 3s | > 5s | Optimize bundles, lazy load |

---

## 4. User Experience Monitoring

### 4.1 Frontend Performance Monitor

```typescript
// apps/web/lib/performance.ts
interface PerfMetric {
  label: string
  duration: number
  timestamp: number
}

class FrontendPerfMonitor {
  private marks: Map<string, number> = new Map()
  private metrics: PerfMetric[] = []
  private readonly maxMetrics = 500
  private isReporting = false

  start(label: string): void {
    this.marks.set(label, performance.now())
  }

  end(label: string): number | null {
    const start = this.marks.get(label)
    if (!start) return null
    const duration = performance.now() - start
    this.marks.delete(label)

    const metric: PerfMetric = {
      label,
      duration,
      timestamp: Date.now(),
    }
    this.metrics.push(metric)

    // Trim if needed
    if (this.metrics.length > this.maxMetrics) {
      this.metrics = this.metrics.slice(-this.maxMetrics)
    }

    // Report slow operations immediately
    if (label === 'page_load' && duration > 3000) {
      this.reportSlowPageLoad(metric)
    }

    // Report Core Web Vitals
    if (label.startsWith('web_vital_')) {
      this.reportWebVital(metric)
    }

    return duration
  }

  private async reportSlowPageLoad(metric: PerfMetric): Promise<void> {
    try {
      await fetch('/api/analytics/event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event: 'slow_page_load',
          properties: {
            path: window.location.pathname,
            load_time_ms: Math.round(metric.duration),
            user_agent: navigator.userAgent?.substring(0, 128),
          },
        }),
      })
    } catch {
      // Best-effort reporting, don't block UX
    }
  }

  private async reportWebVital(metric: PerfMetric): Promise<void> {
    const vitalName = metric.label.replace('web_vital_', '')
    // Classify as good / needs-improvement / poor
    let rating: 'good' | 'needs-improvement' | 'poor'
    if (vitalName === 'LCP') {
      rating = metric.duration <= 2500 ? 'good' : metric.duration <= 4000 ? 'needs-improvement' : 'poor'
    } else if (vitalName === 'FID') {
      rating = metric.duration <= 100 ? 'good' : metric.duration <= 300 ? 'needs-improvement' : 'poor'
    } else if (vitalName === 'CLS') {
      rating = metric.duration <= 0.1 ? 'good' : metric.duration <= 0.25 ? 'needs-improvement' : 'poor'
    } else {
      rating = 'good'
    }

    logger.info('Web Vital', { metric: vitalName, value: Math.round(metric.duration), rating })
  }

  getMetrics(): PerfMetric[] {
    return [...this.metrics]
  }

  getAverageByLabel(label: string): number | null {
    const matching = this.metrics.filter(m => m.label === label)
    if (matching.length === 0) return null
    return matching.reduce((sum, m) => sum + m.duration, 0) / matching.length
  }
}

export const perfMonitor = new FrontendPerfMonitor()
```

### 4.2 Core Web Vitals Tracking

The application monitors three Core Web Vitals metrics:

| Metric | Good | Needs Improvement | Poor | Measurement |
|---|---|---|---|---|
| **LCP** (Largest Contentful Paint) | ≤ 2.5s | 2.5s – 4.0s | > 4.0s | Page load speed |
| **FID** (First Input Delay) | ≤ 100ms | 100ms – 300ms | > 300ms | Interactivity |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | 0.1 – 0.25 | > 0.25 | Visual stability |

**Implementation via `next/web-vitals`:**
```typescript
// apps/web/app/layout.tsx
'use client'
import { useReportWebVitals } from 'next/web-vitals'

export function WebVitals() {
  useReportWebVitals((metric) => {
    perfMonitor.start(`web_vital_${metric.name}`)
    perfMonitor.end(`web_vital_${metric.name}`)
  })
  return null
}
```

### 4.3 Frontend Error Boundary

```typescript
// apps/web/components/error-boundary.tsx
'use client'
import React from 'react'

interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    logger.error('React component error', {
      error: error.message,
      stack: error.stack?.substring(0, 500),
      componentStack: errorInfo.componentStack?.substring(0, 500),
      url: window.location.href,
    })

    // Report to analytics
    fetch('/api/analytics/event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        event: 'frontend_error',
        properties: { error: error.message, url: window.location.href },
      }),
    }).catch(() => {})
  }

  render(): React.ReactNode {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="card p-8 text-center max-w-md">
            <h2 className="text-xl font-semibold mb-2">Something went wrong</h2>
            <p className="text-text-secondary mb-4">
              An unexpected error occurred. Please try refreshing the page.
            </p>
            <button
              className="btn btn-primary"
              onClick={() => window.location.reload()}
            >
              Refresh Page
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
```

---

## 5. AI Reliability Monitoring

### 5.1 AI Service Health Checks

The health endpoint tracks two AI services separately:

| Service | Health Check | Latency Budget | Fallback |
|---|---|---|---|
| **Ollama** (local) | `GET http://localhost:11434/api/tags` | 5s | → Claude API |
| **Claude API** (cloud) | `POST https://api.anthropic.com/v1/messages` (ping) | 10s | → Algorithmic fallback |
| **Prompt validation** | `python scripts/validate_prompts.py` | 30s (cron) | Skip, log warning |

### 5.2 Prompt Validation as Monitoring

Run `scripts/validate_prompts.py` as a scheduled monitor:

```python
# services/scheduler/crons/prompt_validator.py
import subprocess
import json
from datetime import datetime

async def validate_prompts():
    """Validates all prompt YAML frontmatter. Runs daily."""
    result = subprocess.run(
        ["python", "scripts/validate_prompts.py", "--json"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    if result.returncode != 0:
        logger.error("Prompt validation failed", output=result.stderr[:500])
        return {"status": "failed", "errors": result.stderr[:1000]}

    try:
        data = json.loads(result.stdout)
        logger.info("Prompt validation passed", count=len(data.get("validated", [])))
        return {"status": "passed", "validated_count": len(data.get("validated", []))}
    except json.JSONDecodeError:
        logger.warning("Prompt validation output not JSON", output=result.stdout[:200])
        return {"status": "passed", "note": "Non-JSON output"}
```

### 5.3 AI Latency & Token Tracking

```python
# packages/ai/monitoring.py
from dataclasses import dataclass, asdict
from datetime import datetime
import json

@dataclass
class AICallRecord:
    agent: str
    prompt_name: str
    provider: str  # "ollama" | "claude" | "algorihmic"
    model: str
    input_tokens: int
    output_tokens: int
    duration_ms: int
    success: bool
    error: str = ""
    timestamp: str = ""

class AITracker:
    def __init__(self, max_records: int = 10000):
        self.records: list = []
        self.max_records = max_records

    def record_call(self, **kwargs):
        record = AICallRecord(
            timestamp=datetime.utcnow().isoformat(),
            **kwargs,
        )
        self.records.append(asdict(record))
        if len(self.records) > self.max_records:
            self.records = self.records[-self.max_records:]

        # Alert on failure
        if not kwargs.get("success", True):
            logger.error("AI call failed", **asdict(record))

        # Alert on slow calls
        if kwargs.get("duration_ms", 0) > 30000:
            logger.warning("Slow AI call detected", **asdict(record))

    def get_stats(self, hours: int = 24) -> dict:
        cutoff = datetime.utcnow().timestamp() - hours * 3600
        recent = [
            r for r in self.records
            if datetime.fromisoformat(r["timestamp"]).timestamp() > cutoff
        ]
        if not recent:
            return {"total_calls": 0}

        total = len(recent)
        success = sum(1 for r in recent if r["success"])
        total_duration = sum(r["duration_ms"] for r in recent)
        total_tokens = sum(r["input_tokens"] + r["output_tokens"] for r in recent)

        return {
            "total_calls": total,
            "success_rate_pct": round(success / total * 100, 1),
            "avg_duration_ms": round(total_duration / max(total, 1)),
            "total_tokens": total_tokens,
            "avg_tokens_per_call": round(total_tokens / max(total, 1)),
            "by_agent": {
                agent: sum(1 for r in recent if r["agent"] == agent)
                for agent in set(r["agent"] for r in recent)
            },
            "by_provider": {
                provider: sum(1 for r in recent if r["provider"] == provider)
                for provider in set(r["provider"] for r in recent)
            },
            "failures": [r for r in recent if not r["success"]][-10:],
        }

ai_tracker = AITracker()
```

---

## 6. Cost Tracking & Budget Alerts

### 6.1 Cost Monitor Cron Job

```python
# services/scheduler/crons/cost_monitor.py
import os
from datetime import datetime
from dataclasses import dataclass, asdict

@dataclass
class CostReport:
    date: str
    ai: dict
    infrastructure: dict
    budget_utilization: dict
    alerts: list

class CostMonitor:
    BUDGET_LIMITS = {
        "db_size_mb": {"free": 500, "warn_at": 400, "critical_at": 475},
        "bandwidth_gb": {"free": 100, "warn_at": 80, "critical_at": 95},
        "emails_monthly": {"free": 3000, "warn_at": 2400, "critical_at": 2800},
        "claude_cost_usd": {"free": 5.0, "warn_at": 3.0, "critical_at": 4.5},
        "vercel_bandwidth_gb": {"free": 100, "warn_at": 80, "critical_at": 95},
        "supabase_reads_day": {"free": 50000, "warn_at": 40000, "critical_at": 47500},
    }

    async def generate_report(self) -> CostReport:
        today = datetime.now().date()

        # Collect metrics from various sources
        ai_calls = await self._count_ai_calls()
        db_stats = await self._get_db_stats()
        bandwidth = await self._estimate_bandwidth()
        emails = await self._count_emails()

        # Calculate budget utilization
        budget_util = {}
        alerts = []

        for metric, limits in self.BUDGET_LIMITS.items():
            value = locals().get(metric.split("_")[0], {}).get(metric, 0)
            pct = round(value / limits["free"] * 100, 1)
            budget_util[metric] = {
                "value": value,
                "limit": limits["free"],
                "usage_pct": pct,
            }
            if pct >= limits["critical_at"] / limits["free"] * 100:
                alerts.append({
                    "severity": "critical",
                    "metric": metric,
                    "message": f"{metric} at {pct}% of free limit ({value}/{limits['free']})",
                })
            elif pct >= limits["warn_at"] / limits["free"] * 100:
                alerts.append({
                    "severity": "warning",
                    "metric": metric,
                    "message": f"{metric} at {pct}% of free limit ({value}/{limits['free']})",
                })

        return CostReport(
            date=today.isoformat(),
            ai={
                "ollama_calls": ai_calls.get("ollama", 0),
                "claude_calls": ai_calls.get("claude", 0),
                "total_tokens": ai_calls.get("tokens", 0),
                "estimated_cost_usd": ai_calls.get("cost", 0),
            },
            infrastructure={
                "db_size_mb": db_stats.get("size_mb", 0),
                "bandwidth_gb": bandwidth.get("gb", 0),
                "emails_sent": emails,
            },
            budget_utilization=budget_util,
            alerts=alerts,
        )

    async def _count_ai_calls(self) -> dict:
        # Count from AI tracker or Supabase analytics_events
        # Simplified implementation:
        return {"ollama": 0, "claude": 0, "tokens": 0, "cost": 0.0}

    async def _get_db_stats(self) -> dict:
        # Query Supabase for database size
        return {"size_mb": 0}

    async def _estimate_bandwidth(self) -> dict:
        # Estimate from request counts
        return {"gb": 0}

    async def _count_emails(self) -> int:
        # Count from Resend API or local tracking
        return 0

cost_monitor = CostMonitor()


async def track_costs():
    """Daily cost tracking cron job."""
    report = await cost_monitor.generate_report()
    logger.info("Daily cost report", report=asdict(report))

    # Send alert if critical
    critical_alerts = [a for a in report.alerts if a["severity"] == "critical"]
    if critical_alerts:
        alert_manager.send_alert(
            severity="critical",
            title="Budget Alert: Critical threshold reached",
            message="\n".join(a["message"] for a in critical_alerts),
            metadata=asdict(report),
        )

    return asdict(report)
```

### 6.2 Budget Alert Thresholds

| Metric | Free Limit | Warn (80%) | Critical (95%) | Action |
|---|---|---|---|---|
| DB Storage | 500 MB | 400 MB | 475 MB | Archive old data, optimize schema |
| Bandwidth | 100 GB/mo | 80 GB | 95 GB | Enable CDN, compress assets |
| Emails (Resend) | 3,000/mo | 2,400 | 2,800 | Review email frequency |
| Claude API (fallback) | $5 credit | $3.00 | $4.50 | Optimize prompts, cache responses |
| Vercel Bandwidth | 100 GB | 80 GB | 95 GB | Optimize images, enable ISR |
| Supabase Reads | 50K/day | 40K/day | 47.5K/day | Add caching, optimize queries |

---

## 7. Logging Strategy

### 7.1 Structured Logging

All logs use structured JSON format for machine-parseability and correlation:

```python
# packages/shared/utils/logger.py
import json
import logging
import sys
from datetime import datetime
from typing import Optional

class StructuredFormatter(logging.Formatter):
    """Formats log records as JSON objects for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields from record
        if hasattr(record, "extra"):
            log_entry.update(record.extra)

        # Add exception info
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
            }

        return json.dumps(log_entry)


def setup_logging(level: str = "INFO", json_output: bool = True):
    """Configure application-wide logging."""
    handler = logging.StreamHandler(sys.stdout)
    if json_output:
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Set third-party loggers to WARNING
    for logger_name in ["httpx", "urllib3", "asyncio"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str, extra: Optional[dict] = None) -> logging.Logger:
    """Get a logger with optional extra context fields."""
    logger = logging.getLogger(name)
    if extra:
        logger = logging.LoggerAdapter(logger, {"extra": extra})
    return logger


logger = get_logger("secondbrain")
```

### 7.2 Log Levels & Usage

| Level | Usage | Example |
|---|---|---|
| DEBUG | Development details | SQL queries, variable values |
| INFO | Normal operations | Request completed, cron job ran |
| WARNING | Unexpected but handled | Slow query, retry attempt, degraded mode |
| ERROR | Failure requiring attention | Database connection lost, API call failed |
| CRITICAL | System-impacting failure | Auth service down, data corruption |

### 7.3 Log Correlation with Request IDs

```python
# apps/api/middleware/request_id.py
import uuid
from fastapi import Request

@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id

    # Add to response headers
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    # Log request
    logger.info("Request started", extra={
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "query": str(request.url.query)[:200],
        "user_agent": request.headers.get("user-agent", "")[:100],
    })

    return response
```

---

## 8. Alerting & Escalation

### 8.1 Alert Severity Levels

| Severity | Color | Response Time | Notification | Example |
|---|---|---|---|---|
| **INFO** | Blue | None | Dashboard only | Cost report generated |
| **WARNING** | Yellow | < 24h | Email | DB at 80% capacity |
| **ERROR** | Orange | < 2h | Email + Slack | API error rate > 1% |
| **CRITICAL** | Red | < 30 min | Email + SMS | Service unavailable |

### 8.2 Alert Manager Implementation

```python
# packages/shared/utils/alerting.py
import os
import json
from datetime import datetime
from enum import Enum
from typing import Optional

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertManager:
    def __init__(self):
        self.admin_email = os.getenv("ADMIN_EMAIL", "admin@ariaos.app")
        self.admin_phone = os.getenv("ADMIN_PHONE", "")
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL", "")
        self.alert_history: list = []

    async def send_alert(
        self,
        severity: AlertSeverity,
        title: str,
        message: str,
        metadata: Optional[dict] = None,
    ):
        alert = {
            "id": str(uuid.uuid4())[:8],
            "severity": severity.value,
            "title": title,
            "message": message,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat(),
            "acknowledged": False,
        }
        self.alert_history.append(alert)

        # Email alert (all severities except INFO)
        if severity.value in ("warning", "error", "critical"):
            await self._send_email(alert)

        # Slack alert (ERROR and CRITICAL)
        if severity.value in ("error", "critical") and self.slack_webhook:
            await self._send_slack(alert)

        # SMS alert (CRITICAL only)
        if severity.value == "critical" and self.admin_phone:
            await self._send_sms(alert)

        # Log the alert
        log_fn = logger.error if severity.value in ("error", "critical") else logger.warning
        log_fn(f"Alert [{severity.value.upper()}]: {title}", alert=alert)

        return alert

    async def _send_email(self, alert: dict):
        """Send email via Resend API."""
        try:
            send_email_notification(
                to=self.admin_email,
                subject=f"[{alert['severity'].upper()}] {alert['title']}",
                body=f"""
Severity: {alert['severity'].upper()}
Time: {alert['timestamp']}
Title: {alert['title']}
Message: {alert['message']}
Metadata: {json.dumps(alert['metadata'], indent=2) if alert['metadata'] else 'None'}
Alert ID: {alert['id']}
                """.strip(),
            )
        except Exception as e:
            logger.error("Failed to send email alert", error=str(e))

    async def _send_slack(self, alert: dict):
        """Send Slack notification via webhook."""
        try:
            color = {"warning": "#F59E0B", "error": "#EF4444", "critical": "#DC2626"}
            blocks = [
                {"type": "header", "text": {"type": "plain_text", "text": f"🚨 {alert['title']}"}},
                {"type": "section", "text": {"type": "mrkdwn", "text": alert['message']}},
                {"type": "context", "elements": [
                    {"type": "mrkdwn", "text": f"*Severity:* {alert['severity'].upper()} | *Alert ID:* `{alert['id']}` | *Time:* {alert['timestamp']}"}
                ]},
            ]
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(self.slack_webhook, json={"attachments": [{"color": color.get(alert['severity'], "#6366F1"), "blocks": blocks}]})
        except Exception as e:
            logger.error("Failed to send Slack alert", error=str(e))

    async def _send_sms(self, alert: dict):
        """Send SMS via Twilio or similar service."""
        logger.info("SMS alert would be sent", phone=self.admin_phone[:4] + "****", alert_id=alert['id'])

    def get_recent_alerts(self, hours: int = 24) -> list:
        cutoff = datetime.utcnow().timestamp() - hours * 3600
        return [
            a for a in self.alert_history
            if datetime.fromisoformat(a["timestamp"]).timestamp() > cutoff
        ]

alert_manager = AlertManager()
```

### 8.3 Alert Rules

| Rule | Condition | Severity | Action |
|---|---|---|---|
| Service down | Health check fails 3 consecutive times | CRITICAL | Alert + auto-restart |
| High error rate | API error rate > 5% in 5 min | ERROR | Rollback deployment |
| Slow responses | p95 > 1s for 5 min | WARNING | Investigate endpoint |
| Budget threshold | Any metric exceeds warn_at | WARNING | Review usage |
| Budget critical | Any metric exceeds critical_at | ERROR | Take corrective action |
| Auth failures | > 10 auth failures in 5 min | CRITICAL | Possible attack, investigate |
| AI fallback active | Ollama degraded > 30 min | WARNING | Restart Ollama |
| Scheduler missed | No tick in 15 min | ERROR | Restart scheduler |

---

## 9. Dashboard Implementation

### 9.1 Built-In Status Page

A `/status` route provides a real-time operational dashboard:

```
┌─────────────────────────────────────────────────────────────────┐
│  SECOND BRAIN OS — STATUS DASHBOARD                [Refresh]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  OVERALL STATUS: HEALTHY          Uptime: 10d 3h 42m       ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ API          │  │ Database     │  │ AI Service   │          │
│  │ ● Healthy    │  │ ● Healthy    │  │ ● Degraded   │          │
│  │ 142ms avg    │  │ 12ms latency │  │ Ollama down  │          │
│  │ 847 req/24h  │  │ 18 tables    │  │ Claude active│          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Cache        │  │ Auth         │  │ Scheduler    │          │
│  │ ● Healthy    │  │ ● Healthy    │  │ ● Healthy    │          │
│  │ 127 entries  │  │ 45ms latency │  │ Last tick: 2m│          │
│  │ 68% hit rate │  │ JWT valid    │  │ 6 jobs active│          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  PERFORMANCE (Last 24h)                                      ││
│  │  ┌──────────────────────────────────────────────────────────┐││
│  │  │ Requests:  2,847                                         │││
│  │  │ Errors:    23    (0.8%)                                  │││
│  │  │ Avg Resp:  142ms                                         │││
│  │  │ p95 Resp:  389ms                                         │││
│  │  │ p99 Resp:  1,234ms                                       │││
│  │  └──────────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  CRON JOBS                                                   ││
│  │  ● Daily Briefing    OK      Last: 7:00 AM                   ││
│  │  ● Opportunity Radar OK      Last: 6:00 AM                   ││
│  │  ● Weekly Review     OK      Last: Sun 8:00 PM               ││
│  │  ● Uptime Check      OK      Last: 2 min ago                 ││
│  │  ● Cost Monitor      OK      Last: 12:00 AM                  ││
│  │  ● Prompt Validator  OK      Last: 12:00 AM                  ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  COST STATUS (This Month)                                    ││
│  │  DB Storage:    123MB / 500MB     ████████░░░  24.6%         ││
│  │  Bandwidth:     12.4GB / 100GB    ██░░░░░░░░░  12.4%         ││
│  │  Emails:        156 / 3,000       █░░░░░░░░░░   5.2%         ││
│  │  Claude API:    $0.00 / $5.00     ░░░░░░░░░░░   0.0%         ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  RECENT ALERTS (Last 24h)                                    ││
│  │  09:15:23  WARN  AI service degraded (Ollama not running)    ││
│  │  08:30:01  INFO  Daily cost report generated                  ││
│  │  07:00:00  INFO  Daily briefing generated successfully        ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 Supabase Dashboard (For Ad-hoc Analysis)

Use Supabase's built-in SQL editor for custom queries:

```sql
-- API response time distribution in last 24h
SELECT
    endpoint,
    COUNT(*) as requests,
    ROUND(AVG(p95)::numeric, 2) as avg_p95_ms,
    ROUND(AVG(error_rate)::numeric, 2) as avg_error_rate_pct
FROM (
    SELECT
        properties->>'endpoint' as endpoint,
        (properties->>'p95')::float as p95,
        (properties->>'error_rate_pct')::float as error_rate
    FROM analytics_events
    WHERE event_name = 'api_metrics_snapshot'
      AND timestamp > NOW() - INTERVAL '24 hours'
) sub
GROUP BY endpoint
ORDER BY avg_p95_ms DESC;

-- Top errors in last 24h
SELECT
    properties->>'error_type' as error_type,
    properties->>'endpoint' as endpoint,
    COUNT(*) as occurrences
FROM analytics_events
WHERE event_name = 'error_occurred'
  AND timestamp > NOW() - INTERVAL '24 hours'
GROUP BY error_type, endpoint
ORDER BY occurrences DESC
LIMIT 20;
```

---

## 10. Error Tracking

### 10.1 Global Error Handler

```python
# apps/api/middleware/error_handler.py
import traceback
from fastapi import Request, Response
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    user_id = getattr(request.state, "user_id", None)

    # Categorize error
    error_type = categorize_error(exc)

    # Log full error details
    logger.error("Unhandled exception", extra={
        "request_id": request_id,
        "user_id": user_id,
        "error_type": error_type,
        "error": str(exc),
        "traceback": traceback.format_exc()[-1000:],
        "endpoint": request.url.path,
        "method": request.method,
    })

    # Track in metrics
    metrics.record(
        endpoint=request.url.path,
        method=request.method,
        duration_ms=0,
        status_code=500,
        error=True,
    )

    # Return safe error response
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred",
            "request_id": request_id,
            "error_type": error_type,
        },
    )


def categorize_error(exc: Exception) -> str:
    """Categorize exception into known error types."""
    exc_name = type(exc).__name__
    exc_module = type(exc).__module__

    if "supabase" in exc_module or "db" in exc_module:
        return "database"
    if "auth" in exc_module or "jwt" in exc_module:
        return "auth"
    if "httpx" in exc_module or "request" in exc_module:
        return "external_api"
    if "validation" in exc_module or "pydantic" in exc_module:
        return "validation"
    if "rate" in exc_module:
        return "rate_limit"
    return "internal"
```

### 10.2 Error Categories

| Category | Code | Description | Handling |
|---|---|---|---|
| `database` | DB_ERR | Supabase query failures | Retry with backoff, return cached data |
| `auth` | AUTH_ERR | Authentication/authorization | Refresh token, re-authenticate |
| `ai_service` | AI_ERR | Ollama/Claude failures | Fallback chain, retry |
| `validation` | VAL_ERR | Pydantic validation errors | Return 422 with field details |
| `external_api` | EXT_ERR | Brave/Resend/GitHub failures | Retry, cache, graceful degradation |
| `rate_limit` | RATE_ERR | 429 rate limit violations | Retry-After header, backoff |
| `internal` | INT_ERR | Unexpected exceptions | Log full traceback, alert |

---

## 11. Distributed Tracing

Second Brain OS is a monolithic FastAPI application, so distributed tracing across services is limited. However, request correlation is achieved through:

### 11.1 Request ID Propagation

Each incoming request gets a unique `request_id` that is:
- Set in `request.state.request_id` via middleware
- Returned in response header `X-Request-ID`
- Included in all log entries
- Passed to Supabase queries via `pgmq` or comment headers

### 11.2 Trace Across AI Calls

```python
# packages/ai/tracing.py
from contextvars import ContextVar
import uuid

trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")

def get_trace_id() -> str:
    try:
        return trace_id_var.get()
    except LookupError:
        trace_id = str(uuid.uuid4())[:8]
        trace_id_var.set(trace_id)
        return trace_id

def set_trace_id(trace_id: str):
    trace_id_var.set(trace_id)

class TraceContext:
    """Context manager for tracing across AI agent calls."""

    def __init__(self, trace_id: Optional[str] = None):
        self.trace_id = trace_id or str(uuid.uuid4())[:8]
        self.parent_id = get_trace_id()

    def __enter__(self):
        self.token = trace_id_var.set(self.trace_id)
        return self

    def __exit__(self, *args):
        trace_id_var.reset(self.token)

# Usage in agents:
async def briefing_agent(user_id: str):
    with TraceContext() as trace:
        logger.info("Briefing agent started", trace_id=trace.trace_id)
        # ... agent logic ...
        logger.info("Briefing agent completed", trace_id=trace.trace_id)
```

---

## 12. Security Monitoring

### 12.1 Rate Limit Violation Tracking

```python
# Track rate limit violations in analytics
class RateLimitMonitor:
    def __init__(self):
        self.violations: deque = deque(maxlen=1000)

    def record_violation(self, ip: str, endpoint: str, user_id: Optional[str] = None):
        entry = {
            "ip": ip,
            "endpoint": endpoint,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.violations.append(entry)

        # Alert on abuse patterns
        recent = [v for v in self.violations if v["ip"] == ip][-10:]
        if len(recent) >= 10:
            time_span = (
                datetime.fromisoformat(recent[-1]["timestamp"]) -
                datetime.fromisoformat(recent[0]["timestamp"])
            ).total_seconds()
            if time_span < 60:  # 10 violations in 60 seconds
                alert_manager.send_alert(
                    severity="warning",
                    title=f"Possible abuse from IP {ip}",
                    message=f"10 rate limit violations in {time_span}s on endpoint {endpoint}",
                    metadata={"ip": ip, "endpoint": endpoint, "violations": len(recent)},
                )

rate_limit_monitor = RateLimitMonitor()
```

### 12.2 Auth Failure Monitoring

```python
@router.post("/auth/login")
async def login(credentials: LoginRequest):
    try:
        result = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password,
        })
        return {"access_token": result.session.access_token}
    except Exception as e:
        # Track auth failures
        auth_failure_counter[credentials.email] += 1
        failures = auth_failure_counter[credentials.email]

        if failures >= 5:
            alert_manager.send_alert(
                severity="warning",
                title=f"Multiple auth failures for {credentials.email}",
                message=f"{failures} failed login attempts",
                metadata={"email": credentials.email, "attempts": failures},
            )

        raise HTTPException(status_code=401, detail="Invalid credentials")
```

---

## 13. SLO / SLI / SLA Framework

### 13.1 Service Level Objectives

| Service | SLI | SLO Target | Measurement |
|---|---|---|---|
| API Gateway | Availability | 99.5% (monthly) | Health check success rate |
| API Gateway | Latency (p95) | < 500ms | Metrics middleware |
| API Gateway | Error rate | < 1% | Metrics middleware |
| Database | Availability | 99.9% | Supabase SLA |
| Database | Query latency (p95) | < 200ms | Query tracker |
| Auth | Login success rate | > 98% | Auth events |
| AI (Ollama) | Response time | < 15s | AI tracker |
| AI (Claude fallback) | Response time | < 10s | AI tracker |
| Scheduler | Tick reliability | > 99% | Health check timestamps |
| Frontend | Page load | < 3s (p95) | Web Vitals |
| Frontend | Uptime | 99.9% | Vercel SLA |

### 13.2 Error Budget

| SLO Target | Monthly Error Budget | Daily Error Budget |
|---|---|---|
| 99.5% | 3.65 hours | 7.2 minutes |
| 99.9% | 43.8 minutes | 1.4 minutes |
| 99.99% | 4.4 minutes | 8.6 seconds |

**Error Budget Policy:** If error budget is consumed before month-end:
- Freeze all non-critical deployments
- Focus exclusively on reliability improvements
- Require approval for any new features

---

## 14. Incident Response Integration

When monitoring detects a critical issue, it triggers the incident response process:

1. **Detection** → AlertManager sends CRITICAL alert
2. **Diagnosis** → Runbook consulted (see `docs/operations/39_Runbooks.md`)
3. **Mitigation** → Auto-recovery or manual intervention
4. **Resolution** → Service restored, incident logged
5. **Post-mortem** → RCA documented (see `docs/operations/40_IncidentResponse.md`)

**Alert → Runbook Mapping:**

| Alert Title | Runbook Section |
|---|---|
| Service unavailable (API down) | Runbook: API Recovery |
| Database connection failed | Runbook: Database Recovery |
| AI service degraded | Runbook: AI Fallback |
| High error rate | Runbook: Error Spike Investigation |
| Budget critical reached | Runbook: Cost Optimization |
| Auth spike detected | Runbook: Security Incident |

---

## 15. Tool Reference & Setup

### 15.1 Tool Configuration

| Tool | Configuration | Verification |
|---|---|---|
| Better Uptime | Add URLs in dashboard, configure heartbeat | Check status page |
| Supabase Insights | Built-in, no setup needed | Open Dashboard → Database → Query Performance |
| Metrics Middleware | Added to `apps/api/main.py` | `/api/health` returns metrics |
| Cost Monitor | `services/scheduler/crons/cost_monitor.py` | Check logs for daily report |
| Alert Manager | Set env vars: `ADMIN_EMAIL`, `SLACK_WEBHOOK_URL` | `python -c "from shared.utils.alerting import alert_manager; print(alert_manager.admin_email)"` |

### 15.2 Quick Reference

```bash
# Check health endpoint
curl http://localhost:8000/api/health | python -m json.tool

# View metrics (human-readable)
curl http://localhost:8000/api/metrics

# Test alert
python -c "
from shared.utils.alerting import alert_manager
import asyncio
asyncio.run(alert_manager.send_alert('test', 'Test alert', 'This is a test'))
"

# Check AI tracker stats
python -c "
from ai.monitoring import ai_tracker
import json
print(json.dumps(ai_tracker.get_stats(24), indent=2))
"
```

---

## 16. Implementation Roadmap

| Phase | Features | Priority | Timeline |
|---|---|---|---|
| **Phase 1** (Current) | Health endpoint, Metrics middleware, Error handler, Structured logging | P0 | Implemented |
| **Phase 2** (Next) | Status page, Frontend PerfMonitor, Uptime cron, Cost monitor | P1 | Within 2 weeks |
| **Phase 3** | Alert Manager (Email + Slack), Auth failure monitoring, Rate limit tracking | P1 | Within 1 month |
| **Phase 4** | Dashboard visualizations, Historical metrics, Trend analysis | P2 | Within 2 months |
| **Phase 5** | AI Tracker, Prompt validation monitor, Web Vitals dashboard | P2 | Within 3 months |
| **Phase 6** | SLO tracking, Error budget calculation, Automated runbook triggers | P3 | Future |

---

## 17. Appendices

### Appendix A: Environment Variables

| Variable | Description | Required |
|---|---|---|
| `ADMIN_EMAIL` | Alert recipient email | Yes |
| `ADMIN_PHONE` | SMS alert phone number | No |
| `SLACK_WEBHOOK_URL` | Slack incoming webhook URL | No |
| `BETTER_UPTIME_HEARTBEAT_URL` | Heartbeat URL for uptime monitor | No |
| `SENTRY_DSN` | Sentry error tracking DSN (future) | No |

### Appendix B: Testing Monitoring

```bash
# Test health endpoint
curl -s http://localhost:8000/api/health | python -c "import sys,json; d=json.load(sys.stdin); assert d['status'] in ('healthy','degraded'), 'Health check failed'"

# Test alert manager
python -c "
from shared.utils.alerting import alert_manager
import asyncio
r = asyncio.run(alert_manager.send_alert('info', 'Test', 'Diagnostic test'))
print(f'Alert sent: {r[\"id\"]}')
"

# Test metrics recording
python -c "
from middleware.metrics import metrics
metrics.record('/api/test', 'GET', 150, 200, False)
stats = metrics.get_stats('GET /api/test')
assert stats['count'] > 0, 'Metrics not recording'
print(f'Metrics OK: {stats}')
"

# Test log format
python -c "
from shared.utils.logger import get_logger
l = get_logger('test')
l.info('Diagnostic message', extra={'test': True})
print('Logging OK')
"
```

### Appendix C: Monitoring Checklist

**Daily:**
- [ ] Check status dashboard for any degraded components
- [ ] Review error rate trends
- [ ] Verify cron jobs executed successfully

**Weekly:**
- [ ] Review cost report and budget utilization
- [ ] Check database query performance (slow queries)
- [ ] Review AI call statistics and failure rates

**Monthly:**
- [ ] Full SLO/SLI review against targets
- [ ] Alert threshold review and tuning
- [ ] Tool usage review (are we within free tiers?)
- [ ] Update monitoring documentation

**Per-Release:**
- [ ] Verify health endpoint returns correct status
- [ ] Confirm metrics middleware not causing overhead
- [ ] Test alert delivery (email/Slack)
- [ ] Update dashboard with any new endpoints/services

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-01 | Developer | Initial monitoring documentation |
| 2.0.0 | 2026-06-11 | AI Agent System | Enterprise upgrade: full architecture, APM, UX monitoring, AI reliability, cost tracking, alerting, dashboards, error tracking, distributed tracing, security monitoring, SLO/SLI/SLA, incident integration, tool reference, roadmap, checklists |
