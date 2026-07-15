# Performance Benchmarks & SLOs

## Document Control

| Metadata | Value |
|---|---|
| **Document ID** | ENG-BEN-001 |
| **Version** | 1.0.0 |
| **Author** | ARIA OS Engineering |
| **Status** | Active |
| **Last Updated** | 2026-06-23 |
| **Applies To** | Second Brain OS (all modules) |
| **Review Cycle** | Monthly |
| **SLO Tier** | Tier 1 (Critical) |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [API Latency SLOs](#2-api-latency-slos)
3. [AI Response Budgets](#3-ai-response-budgets)
4. [Bundle Size Budgets](#4-bundle-size-budgets)
5. [Database Query Benchmarks](#5-database-query-benchmarks)
6. [k6 Load Test Results Template](#6-k6-load-test-results-template)
7. [Profiling Methodology](#7-profiling-methodology)
8. [Regression Testing](#8-regression-testing)
9. [Alert Thresholds](#9-alert-thresholds)
10. [Benchmark Results Archive](#10-benchmark-results-archive)
11. [Appendix A: Script Usage](#appendix-a-script-usage)

---

## 1. Executive Summary

This document defines the performance benchmarks, SLOs (Service Level Objectives), and measurement methodology for Second Brain OS. It is the operational companion to `docs/engineering/45_PerformanceScalability.md` â€” translating aspirational targets into measurable, testable assertions enforced by CI and manual profiling.

**Key principles:**

- All benchmarks are measured via the automated script at `scripts/benchmark_api.py`
- k6 load tests provide multi-user scenario coverage in `tests/performance/`
- SLO violations in CI (`--ci` flag) block deployment
- Historical results are stored in `docs/engineering/benchmark-results.json`

---

## 1.1 SLO Target vs Current Status

`mermaid
graph LR
    subgraph TARGET["SLO Targets"]
        direction LR
        T1["API p95 latency<br/>Target: < 500ms"]
        T2["AI response<br/>Target: < 30s"]
        T3["DB query<br/>Target: < 200ms"]
        T4["Frontend TTI<br/>Target: < 3s"]
        T5["Bundle size<br/>Target: < 300KB"]
    end

    subgraph BUDGET["Current Status"]
        B1["✅ On track<br/>p50: 120ms"]
        B2["⚠️ Monitoring<br/>p50: 8.5s"]
        B3["✅ On track<br/>p50: 45ms"]
        B4["❌ Needs audit<br/>no data"]
        B5["✅ On track<br/>gzip: 245KB"]
    end

    T1 --> B1
    T2 --> B2
    T3 --> B3
    T4 --> B4
    T5 --> B5

    style TARGET fill:#0A0B0F,stroke:#334155,color:#F1F5F9
    style BUDGET fill:#0A0B0F,stroke:#334155,color:#F1F5F9
    style T1 fill:#13151A,stroke:#6366F1,color:#F1F5F9
    style T2 fill:#13151A,stroke:#818CF8,color:#F1F5F9
    style T3 fill:#13151A,stroke:#00FFA3,color:#F1F5F9
    style T4 fill:#13151A,stroke:#F59E0B,color:#F1F5F9
    style T5 fill:#13151A,stroke:#EF4444,color:#F1F5F9
    style B1 fill:#13151A,stroke:#00FFA3,color:#F1F5F9
    style B2 fill:#13151A,stroke:#F59E0B,color:#F1F5F9
    style B3 fill:#13151A,stroke:#00FFA3,color:#F1F5F9
    style B4 fill:#13151A,stroke:#EF4444,color:#F1F5F9,stroke-width:2px
    style B5 fill:#13151A,stroke:#00FFA3,color:#F1F5F9
`

## 2. API Latency SLOs

| Endpoint Category | p50 Target | p95 Target | p99 Target | Example Endpoints |
|---|---|---|---|---|
| **Simple CRUD** | < 100ms | < 300ms | < 1,000ms | `GET /api/v1/tasks/`, `POST /api/v1/habits/` |
| **AI-powered** | < 10,000ms | < 30,000ms | < 60,000ms | `POST /api/v1/chat/`, automation triggers |
| **Aggregations** | < 500ms | < 2,000ms | < 5,000ms | `GET /api/v1/analytics/stats` |
| **Health checks** | < 50ms | < 100ms | < 200ms | `GET /health`, `GET /health/ready` |
| **Auth (login)** | < 500ms | < 1,000ms | < 3,000ms | `POST /api/v1/auth/login` |

### 2.1 Per-Endpoint Benchmarks (CI-Enforced)

| Endpoint | Method | Iterations | SLO (p95) | Checked by Script |
|---|---|---|---|---|
| `/health` | GET | 50 | < 200ms | âœ… |
| `/api/v1/tasks/` | GET | 50 | < 500ms | âœ… |
| `/api/v1/habits/` | GET | 50 | < 500ms | âœ… |
| `/api/v1/chat/` | POST | 50 | < 30,000ms | âœ… (AI endpoint) |

### 2.2 SLO Violation Actions

| Category | p95 Exceeded By | Action |
|---|---|---|
| CRUD | < 2x SLO | Log warning, auto-investigate |
| CRUD | 2xâ€“5x SLO | Raise P2 incident, block CI |
| CRUD | > 5x SLO | Raise P1 incident, rollback if deployed |
| AI | < 2x SLO | Log warning, review prompt changes |
| AI | > 2x SLO | Raise P2 incident, check LLM provider |
| Health | Any violation | Raise P0 incident (infrastructure issue) |

---

## 3. AI Response Budgets

| Agent | Target | Hard Limit | Prompt File |
|---|---|---|---|
| A09 â€” Daily Briefing | < 15,000ms | 30,000ms | `prompts/agents/briefing_agent.md` |
| A10 â€” Weekly Review | < 20,000ms | 45,000ms | `prompts/agents/weekly_review_agent.md` |
| A06 â€” Opportunity Radar | < 15,000ms | 30,000ms | `prompts/agents/opportunity_radar_agent.md` |
| A02 â€” Memory | < 5,000ms | 15,000ms | `prompts/agents/memory_agent.md` |
| A03 â€” Learning | < 10,000ms | 20,000ms | `prompts/agents/learning_agent.md` |
| A13 â€” Sleep & Bedtime | < 10,000ms | 20,000ms | `prompts/agents/sleep_agent.md` |
| A14 â€” Course Nudge | < 5,000ms | 15,000ms | `prompts/agents/nudge_agent.md` |
| A08 â€” Roadmap | < 15,000ms | 30,000ms | `prompts/agents/roadmap_agent.md` |
| A15 â€” Opportunity Matching | < 10,000ms | 20,000ms | `prompts/agents/opportunity_matching_agent.md` |

### 3.1 AI Error Budgets

| Provider | Success Rate Target | Measurement |
|---|---|---|
| Ollama (default) | > 95% | `llm.ollama_circuit.state` + HTTP 2xx |
| Claude (fallback) | > 98% | API 2xx count / total calls |

---

## 4. Bundle Size Budgets

| Asset | Budget (gzip) | Current Estimated | Measurement Tool |
|---|---|---|---|
| Main JS bundle | < 300 KB | ~150 KB | `next-bundle-analyzer` |
| Initial CSS | < 50 KB | ~30 KB | `next-bundle-analyzer` |
| Fonts (Syne, DM Sans, JetBrains Mono) | < 100 KB | ~50 KB | File size check |
| Images (per page) | < 200 KB | â€” | Chrome DevTools |
| **Total page weight** | **< 500 KB** | **~350 KB** | Lighthouse |
| Three.js (lazy) | < 150 KB | ~120 KB | `next-bundle-analyzer` |
| React Flow (lazy) | < 100 KB | ~80 KB | `next-bundle-analyzer` |
| Framer Motion | < 40 KB | ~35 KB | `next-bundle-analyzer` |

### 4.1 Bundle CI Check

```bash
# Run in CI to check bundle size
cd apps/web && npx next/bundle-analyzer 2>&1 | grep -E "(Total|Route)"
```

If any budget is exceeded by > 10%, CI should warn. If > 25%, CI should fail.

---

## 5. Database Query Benchmarks

| Query Type | Expected (p95) | Index Strategy |
|---|---|---|
| **PK lookup** (`SELECT ... WHERE id = ?`) | < 50ms | Primary key index (auto) |
| **User-scoped filter** (`WHERE user_id = ?`) | < 100ms | B-tree on `user_id` |
| **Filter + sort** (`WHERE user_id = ? ORDER BY created_at DESC`) | < 200ms | Composite index on `(user_id, created_at)` |
| **Filter + status** (`WHERE user_id = ? AND status = ?`) | < 150ms | Composite index on `(user_id, status)` |
| **Aggregation** (`COUNT`, `SUM` with filter) | < 500ms | Partial indexes + cached counts |
| **Full-text search** (`to_tsvector` on resources) | < 500ms | GIN index on tsvector |
| **JOIN with RLS** (two tables, user_id filter) | < 500ms | FK + user_id composite indexes |
| **INSERT single row** | < 100ms | Primary key index |
| **UPDATE by PK** | < 100ms | Primary key index |
| **DELETE by PK** | < 100ms | Primary key index |

### 5.1 Connection Pool Benchmarks

| Metric | Expected | Alert Threshold |
|---|---|---|
| Pool hit rate | > 95% | < 90% |
| Active connections (idle) | 1-2 | > 10 |
| Query timeout rate | < 0.1% | > 1% |

---

## 6. k6 Load Test Results Template

When running k6 load tests, record results using this template:

```markdown
## Load Test: [Test Name]

| Field | Value |
|---|---|
| **Date** | YYYY-MM-DD HH:MM |
| **Script** | `tests/performance/load-test-<name>.js` |
| **Target** | `http://localhost:8000` or production URL |
| **k6 Version** | x.y.z |
| **Run By** | @person |
| **Notes** | Any anomalies observed |

### Results

| Metric | Value | SLO | Pass/Fail |
|---|---|---|---|
| http_req_duration p50 | xxx ms | â€” | â€” |
| http_req_duration p95 | xxx ms | < xxx ms | âœ… / âŒ |
| http_req_duration p99 | xxx ms | < xxx ms | âœ… / âŒ |
| http_req_failed rate | x.xx% | < x% | âœ… / âŒ |
| VUs max | xxx | â€” | â€” |

### Endpoint Breakdown

| Endpoint | Count | p50 | p95 | p99 | Fail % |
|---|---|---|---|---|---|
| GET /api/v1/tasks/ | xxx | xxx | xxx | xxx | x% |
| POST /api/v1/tasks/ | xxx | xxx | xxx | xxx | x% |
| ... | ... | ... | ... | ... | ... |

### Threshold Violations

- None (or list each violation with details)
```

### 6.1 Baseline Results Archive

Past results are stored in `docs/engineering/benchmark-results.json`. Each entry:

```json
{
  "timestamp": "2026-06-23T12:00:00Z",
  "script": "scripts/benchmark_api.py",
  "target": "http://localhost:8000",
  "endpoints": {
    "/health": {
      "p50_ms": 2.34,
      "p75_ms": 3.12,
      "p90_ms": 4.56,
      "p95_ms": 5.89,
      "p99_ms": 8.12,
      "iterations": 50,
      "errors": 0,
      "slo_ms": 200,
      "passed": true
    }
  }
}
```

---

## 7. Profiling Methodology

### 7.1 API Endpoint Profiling with cProfile

```bash
# Profile a single request to find bottlenecks
python -m cProfile -s cumulative \
  -o /tmp/profile_output.prof \
  -m uvicorn apps.api.main:app --workers 1

# Then send a request:
curl http://localhost:8000/api/v1/tasks/

# Analyze the profile:
python -c "
import pstats
p = pstats.Stats('/tmp/profile_output.prof')
p.sort_stats('cumtime').print_stats(30)  # Top 30 by cumulative time
p.sort_stats('tottime').print_stats(20)  # Top 20 by total time
"
```

### 7.2 Manual Timing Wrapper

For ad-hoc profiling of specific functions, use the timing context manager from `packages/shared/utils/logger.py`:

```python
from shared.utils.logger import logger
import time

start = time.perf_counter()
result = await expensive_function()
elapsed = time.perf_counter() - start
logger.info("Function profile", extra={
    "function": "expensive_function",
    "duration_ms": round(elapsed * 1000, 2),
})
```

### 7.3 AI Call Timing

Every AI call is automatically timed by the LLM client in `packages/ai/client.py`. Durations are logged at INFO level with the key `ai_duration_ms`.

### 7.4 Benchmark Script

The canonical benchmarking tool is `scripts/benchmark_api.py`. Usage:

```bash
# Default: runs 50 iterations per endpoint, reports table
python scripts/benchmark_api.py

# CI mode: exits non-zero if any SLO is exceeded
python scripts/benchmark_api.py --ci

# Custom target
python scripts/benchmark_api.py --url http://production.example.com

# Custom iterations
python scripts/benchmark_api.py --iterations 100

# Save results to custom path
python scripts/benchmark_api.py --output /tmp/results.json

# Skip AI endpoints (faster, avoids LLM latency)
python scripts/benchmark_api.py --skip-ai
```

---

## 8. Regression Testing

### 8.1 Benchmark Comparison

Run the benchmark script against two targets (e.g., old deploy vs. new deploy) and compare:

```bash
# Baseline
python scripts/benchmark_api.py --url http://old-deploy.example.com --output /tmp/baseline.json

# New version
python scripts/benchmark_api.py --url http://new-deploy.example.com --output /tmp/new.json

# Compare (manual until automated comparison exists)
python -c "
import json
with open('/tmp/baseline.json') as f: b = json.load(f)
with open('/tmp/new.json') as f: n = json.load(f)
for ep in b['endpoints']:
    bp95 = b['endpoints'][ep]['p95_ms']
    np95 = n['endpoints'][ep]['p95_ms']
    change = ((np95 - bp95) / bp95) * 100
    status = 'âš ï¸ REGRESSION' if change > 20 else 'âœ…'
    print(f'{ep}: baseline={bp95}ms new={np95}ms change={change:+.1f}% {status}')
"
```

### 8.2 CI Integration

```yaml
# .github/workflows/ci.yml excerpt
- name: Performance Benchmarks
  run: |
    # Start server in background
    uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 &
    sleep 3
    # Run benchmarks with CI flag (exits non-zero if SLOs violated)
    python scripts/benchmark_api.py --ci --skip-ai
```

### 8.3 When to Re-Benchmark

| Event | Action |
|---|---|
| New API endpoint added | Add to benchmark script |
| Database schema change | Run full benchmark suite |
| New AI agent added | Run AI-specific benchmarks |
| Dependency upgrade (FastAPI, etc.) | Run CRUD benchmarks |
| Before production deployment | Run full benchmark suite |
| After incident with performance impact | Run affected benchmarks |

---

## 9. Alert Thresholds

### 9.1 API Latency Alerts

| Condition | Severity | Action |
|---|---|---|
| Any endpoint p95 > 2x SLO for 5 min | **P1** | Page on-call, investigate slow queries |
| CRUD endpoint p95 > SLO for 15 min | **P2** | Create ticket, review in daily standup |
| AI endpoint p95 > SLO for 30 min | **P2** | Check LLM provider status, optimize prompts |
| Health endpoint p95 > SLO | **P0** | Infrastructure issue, immediate investigation |

### 9.2 Error Rate Alerts

| Condition | Severity | Action |
|---|---|---|
| Error rate > 5% for 5 min | **P1** | Page on-call, check logs |
| Error rate > 1% for 1 hour | **P2** | Create ticket, investigate next session |
| Any 5xx on health endpoint | **P0** | Immediate investigation |

### 9.3 Bundle Size Alerts

| Condition | Severity | Action |
|---|---|---|
| Main JS bundle > 400 KB | **P2** | Code split, tree-shake, investigate |
| Total page weight > 500 KB | **P2** | Run bundle analysis |
| Any module increased by > 20% in PR | **P3** | Flag in code review |

### 9.4 Database Alerts

| Condition | Severity | Action |
|---|---|---|
| Any query consistently > 500ms p95 | **P2** | Add index, rewrite query |
| Connection pool exhaustion | **P1** | Immediate investigation, scale if needed |
| Storage > 80% of quota (400 MB) | **P3** | Plan archival, verify growth projection |

---

## 10. Benchmark Results Archive

Results from each benchmark run are saved to `docs/engineering/benchmark-results.json`. The file contains an array of result objects (see Section 6.1 for schema).

### 10.1 Latest Baseline

| Date | Branch | Target | CRUD p95 | AI p95 | Health p95 |
|---|---|---|---|---|---|
| 2026-06-23 | main | localhost:8000 | â€” | â€” | â€” |
| â€” | â€” | â€” | (first baseline pending) | â€” | â€” |

---

## 11. Appendix A: Script Usage

```bash
# Quick benchmark (default)
python scripts/benchmark_api.py

# CI mode with SLO enforcement
python scripts/benchmark_api.py --ci

# Custom URL and iterations
python scripts/benchmark_api.py --url http://localhost:8000 --iterations 100

# Skip AI endpoints
python scripts/benchmark_api.py --skip-ai

# Custom output path
python scripts/benchmark_api.py --output custom/path/results.json
```

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-23 | Developer | Initial document â€” API SLOs, AI budgets, bundle budgets, DB benchmarks, profiling methodology, regression testing, alert thresholds |
