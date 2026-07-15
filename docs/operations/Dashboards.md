# Monitoring Dashboards — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| Document ID | OPS-DSH-002 |
| Version | 1.0.0 |
| Status | Approved |
| Date | 2026-07-10 |
| Classification | Internal |
| Owner | Developer |

---

## Table of Contents

- [1. Executive Summary](#1-executive-summary)
- [2. Purpose](#2-purpose)
- [3. Scope](#3-scope)
- [4. Business Context](#4-business-context)
- [5. Functional Specification](#5-functional-specification)
- [6. Non-Functional Requirements](#6-non-functional-requirements)
- [7. Architecture](#7-architecture)
- [8. Diagrams](#8-diagrams)
- [9. Data Models](#9-data-models)
- [10. APIs](#10-apis)
- [11. Security](#11-security)
- [12. Performance Targets](#12-performance-targets)
- [13. Edge Cases](#13-edge-cases)
- [14. Failure Scenarios](#14-failure-scenarios)
- [15. Risks & Mitigations](#15-risks--mitigations)
- [16. Acceptance Criteria](#16-acceptance-criteria)
- [17. Traceability](#17-traceability)
- [18. Implementation Notes](#18-implementation-notes)
- [19. Testing Strategy](#19-testing-strategy)
- [20. References](#20-references)

---

## 1. Executive Summary

Second Brain OS currently implements monitoring dashboards using structured JSON logs viewed through Railway/Vercel console logs and custom API endpoints. There is no dedicated dashboarding platform (Grafana or similar) due to free-tier hosting constraints. Instead, monitoring data is exposed via the `/api/v1/monitoring/` endpoints, health check APIs, and log aggregation from hosting providers. A future phase will introduce Grafana dashboards once infrastructure budget permits.

---

## 2. Purpose

Dashboards provide at-a-glance visibility into system health, performance trends, error rates, and business metrics. They enable rapid incident detection, capacity planning, and data-driven decision-making. Until a dedicated graphing platform is available, dashboards exist as structured data endpoints designed for easy ingestion into eventual visualisation tools.

---

## 3. Scope

This document covers:

- Six dashboard categories: health, API performance, AI performance, scheduler health, error rate, business metrics
- Metrics definitions and collection methods
- Refresh rate and data retention policies
- Grafana migration plan
- Self-service query endpoints

Out of scope: product analytics dashboards (covered in [Analytics](./30_Analytics.md)), user-facing analytics, real-time streaming dashboards.

---

## 4. Business Context

As a personal productivity system with free-tier hosting, Second Brain OS cannot justify the cost of Grafana Cloud or similar SaaS monitoring. The current approach maximises observability within the free tier: structured logs on Railway/Vercel, health check endpoints, and monitoring API routes. When the project migrates to paid infrastructure (target Q1 2027), Grafana will be deployed alongside Prometheus for metric storage.

---

## 5. Functional Specification

### 5.1 Dashboard Types

| Dashboard | Purpose | Refresh | Data Source |
|---|---|---|---|
| Health Check | Service up/down, dependency status | 30s | `/health/ready` endpoint |
| API Performance | Endpoint latency, throughput, error rate | 1min | Log aggregation + `/api/v1/monitoring/token-usage` |
| AI Performance | Agent latency, token usage, provider availability | 1min | LLM client metrics + monitoring API |
| Scheduler Health | Cron job status, last run, failure count | 5min | Scheduler log parsing |
| Error Rate | 4xx/5xx breakdown, top error types, circuit breaker states | 1min | Log aggregation |
| Business Metrics | User activity, module adoption, engagement trends | 1hr | Analytics events table |

### 5.2 Health Check Dashboard

Displayed metrics:

- Backend status (up/down/ degraded)
- Supabase connectivity (ok / error)
- Ollama service status (running / stopped / circuit breaker open)
- Claude API configuration (configured / missing key)
- Last restart timestamp
- Uptime in hours
- Active request count
- Memory usage (estimated via Railway logs)

### 5.3 API Performance Dashboard

Displayed metrics:

- Requests per minute (by endpoint)
- p50 / p95 / p99 latency by endpoint
- Error rate by endpoint (4xx vs 5xx)
- Top 5 slowest endpoints
- Status code distribution (2xx, 3xx, 4xx, 5xx)
- Request size distribution
- Response size distribution

### 5.4 AI Performance Dashboard

Displayed metrics:

- Agent invocation count (per agent)
- Average response time per agent
- Token usage per agent (input + output)
- Provider distribution (Ollama vs Claude)
- Circuit breaker state per provider
- Cache hit rate (future: semantic cache)
- Error rate per agent
- Queue depth (future: request queuing)

### 5.5 Scheduler Health Dashboard

Displayed metrics:

- All 15 cron jobs with last run timestamp
- Job duration (average, max)
- Success/failure count per job
- Missed runs (expected vs actual)
- Next scheduled run
- Overlap count (jobs still running when next trigger fires)

### 5.6 Error Rate Dashboard

Displayed metrics:

- Error rate over time (5-minute buckets)
- Error breakdown by module
- Top 10 error messages
- 4xx vs 5xx ratio
- Circuit breaker states (ollama, claude)
- Rate limit hit count
- Unhandled exception count

### 5.7 Business Metrics Dashboard

Displayed metrics:

- Active users (daily, weekly, monthly)
- Tasks created / completed per day
- Habits logged per day
- Courses with activity in last 7 days
- AI interactions per user per day
- Briefings generated per day
- Module adoption (users with at least 1 action in module)

---

## 6. Non-Functional Requirements

| ID | Requirement | Target |
|---|---|---|
| DSH-NFR-001 | Dashboard endpoint response time | < 200ms |
| DSH-NFR-002 | Metric collection overhead | < 1% CPU |
| DSH-NFR-003 | Data retention (raw metrics) | 90 days |
| DSH-NFR-004 | Data retention (aggregated metrics) | 12 months |
| DSH-NFR-005 | Maximum metric cardinality | 1000 unique time series |
| DSH-NFR-006 | Dashboard refresh rate (health) | 30 seconds |

---

## 7. Architecture

```mermaid
graph TD
    subgraph Data_Sources["Data Sources"]
        API[FastAPI Requests] --> Logs[Structured Logs]
        Sched[APScheduler Jobs] --> Logs
        Health[Health Endpoints] --> Metrics[In-Memory Metrics]
        LLM[LLM Client] --> Metrics
    end

    subgraph Collection["Collection Layer"]
        Logs --> LogAgg[Log Aggregation<br/>(Railway Console / Vercel)]
        Metrics --> MetricsAPI[Metrics Endpoint<br/> /api/v1/monitoring/token-usage]
        DB[(Supabase)] --> DBAgg[SQL Aggregation<br/>Views & Queries]
    end

    subgraph Dashboard["Dashboard Layer"]
        LogAgg --> Console[Railway / Vercel Console]
        MetricsAPI --> CustomUI[Custom /api/v1/monitoring Endpoints]
        DBAgg --> CustomUI
        CustomUI --> FutureGrafana[Future: Grafana<br/>(Q1 2027)]
    end

    subgraph Consumers["Consumers"]
        Console --> Developer
        CustomUI --> Developer
        CustomUI --> Alerts[Alert System]
        CustomUI --> Reports[Reporting System]
    end
```

---

## 8. Diagrams

### 8.1 Dashboard Layout Mockup

```mermaid
graph TD
    subgraph Dashboard["Health Dashboard (//health/ready)"]
        direction LR
        S1[Status: OK<br/>Supabase: OK<br/>Ollama: OK<br/>Claude: Configured]
        S2[Uptime: 72h<br/>Last Restart: 2026-07-07<br/>Active Reqs: 3]
    end

    subgraph API_Perf["API Performance"]
        direction TB
        A1[Requests/min: 45]
        A2[p95 Latency: 120ms]
        A3[Error Rate: 1.2%]
        A4[Top Slow: /api/v1/chat - 2.3s]
    end

    subgraph AI_Perf["AI Performance"]
        direction TB
        AI1[Briefings: 12 today<br/>Avg: 8.3s]
        AI2[Memory: 45 today<br/>Avg: 1.2s]
        AI3[Tokens: 45K in / 28K out]
        AI4[Ollama CB: CLOSED]
    end

    subgraph Errors["Error Rate"]
        direction TB
        E1[5xx: 0.3% | 4xx: 2.1%]
        E2[Top: RateLimit - 8 hits]
    end
```

---

## 9. Data Models

### 9.1 Health Check Response

```python
class HealthCheckResponse(BaseModel):
    status: str  # healthy, degraded, unhealthy
    version: str
    uptime_seconds: float
    dependencies: dict[str, DependencyStatus]
    active_requests: int

class DependencyStatus(BaseModel):
    status: str  # ok, error, not_configured
    latency_ms: Optional[float] = None
    error: Optional[str] = None
```

### 9.2 Metrics Snapshot

```python
class MetricsSnapshot(BaseModel):
    timestamp: datetime
    dashboard_type: str  # health, api_perf, ai_perf, scheduler, errors, business
    metrics: dict[str, float | str | int]
    period_seconds: int
```

---

## 10. APIs

| Endpoint | Description | Data Source |
|---|---|---|
| `GET /health` | Simple alive check | Application |
| `GET /health/live` | Liveness probe | Application |
| `GET /health/ready` | Readiness + dependencies | Application + Supabase + Ollama |
| `GET /api/v1/monitoring/token-usage` | Token usage summary | Monitoring table |
| `GET /api/v1/monitoring/summary` | Aggregate metrics | Monitoring table |

---

## 11. Security

- Health endpoints reveal internal dependency status; should not be publicly exposed in production
- Metric endpoints require authentication (`Depends(get_current_user)`)
- No PII is included in metric data
- Error messages in metrics are sanitised (no stack traces)
- Dashboard API responses include only aggregated, de-identified data

---

## 12. Performance Targets

| Metric | Target |
|---|---|
| Health check endpoint p95 | < 50ms |
| Monitoring API endpoint p95 | < 200ms |
| Metric collection overhead per request | < 0.5ms |
| Dashboard data refresh interval | < 60s for all panels |

---

## 13. Edge Cases

| Edge Case | Handling |
|---|---|
| No metrics available yet | Return empty dataset with `"status": "no_data"` |
| Dependency check times out | Mark dependency as `"error"` with `"timeout"` detail |
| Metric collection queue backpressure | Drop oldest metrics; log warning |
| Dashboard accessed with no data | Return 200 with empty `metrics` object |
| Supabase query for metrics fails | Return cached last-known metrics with staleness indicator |

---

## 14. Failure Scenarios

| Scenario | Impact | Mitigation |
|---|---|---|
| All dependencies unhealthy | False alarms | Require 3 consecutive failures before alerting |
| Metric collection blocks request | Slowed responses | Run metric collection as background task |
| Retention cleanup fails | Storage growth | Auto-cleanup on write (check table size, delete oldest) |
| Grafana still not deployed (Q1 2027) | Manual log inspection | Extend custom endpoint approach |

---

## 15. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| No visual dashboard until Grafana | High | Medium | Expose structured JSON for easy future ingestion |
| Railway log retention is limited | High | Low | Export critical metrics to Supabase monitoring table |
| Metric cardinality explosion | Low | Medium | Set hard limits on tag combinations |
| Health check endpoint overload | Low | Medium | Cache health check for 10s |

---

## 16. Acceptance Criteria

- [ ] Health check endpoints return accurate dependency status
- [ ] Monitoring API returns aggregated token usage
- [ ] All six dashboard categories have defined metrics and data sources
- [ ] Metrics are queryable via REST endpoints
- [ ] Data retention policies are enforced
- [ ] Dashboard data refreshes within defined intervals

---

## 17. Traceability

| Requirement | Covered By | Verified By |
|---|---|---|
| DSH-NFR-001 | Health endpoint benchmark | `tests/test_main_routes.py` |
| DSH-NFR-002 | Metric collection profiling | Manual profiling |
| DSH-NFR-003 | Retention SQL scripts | `scripts/` review |

---

## 18. Implementation Notes

### 18.1 Current Dashboarding

Dashboards exist as structured data without a visual frontend. Developers inspect:
- Railway console logs for API/backend metrics
- Vercel analytics for frontend performance
- `curl` or browser requests to `/health/ready` and `/api/v1/monitoring/` endpoints

### 18.2 Grafana Migration Plan

| Phase | Timeline | Details |
|---|---|---|
| Phase 1 | Q4 2026 | Export metrics to structured JSON format compatible with Grafana |
| Phase 2 | Q1 2027 | Deploy Grafana Cloud free tier or self-hosted |
| Phase 3 | Q2 2027 | Connect Supabase as Grafana data source |
| Phase 4 | Q3 2027 | Build 6 production dashboards with alert rules |

### 18.3 Metric Collection Implementation

Metrics are collected using:
- FastAPI middleware hooks for request/response timing (middleware.py)
- LLM client callbacks for token counting (client.py)
- Scheduler job decorators for cron run tracking (crons/)
- Database triggers for business metrics (Supabase)

---

## 19. Testing Strategy

| Test Type | Scope | Location |
|---|---|---|
| Unit | Health check response schema | `tests/test_main_routes.py` |
| Unit | Metrics aggregation logic | `tests/test_shared_utils.py` |
| Integration | Monitoring API endpoints | `tests/test_api_endpoints.py` |
| Integration | Health dependency checks | `tests/test_api_routes_advanced.py` |
| E2E | Dashboard data correctness | Manual verification |

---

## 20. References

| Reference | Description |
|---|---|
| [Observability](./31_Observability.md) | Observability architecture overview |
| [Monitoring](./32_Monitoring.md) | Monitoring infrastructure |
| [Alerts](./Alerts.md) | Alert rules derived from dashboard metrics |
| [Tracing](./Tracing.md) | Distributed tracing for request correlation |
| [Analytics](./30_Analytics.md) | Product analytics and user metrics |
| [KPIs](./KPIs.md) | KPI framework for business metrics |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-07-10 | Developer | Initial dashboards document |
