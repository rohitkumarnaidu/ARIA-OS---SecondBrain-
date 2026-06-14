# Performance Testing Strategy

## 1. Performance Testing Goals and Metrics

### 1.1 Objectives

Performance testing ensures Second Brain OS remains responsive, scalable, and reliable under all expected load conditions. The application has four primary goals:

| Goal | Target | Priority |
|---|---|---|
| **Responsiveness** | All API endpoints respond within 500ms P95 | P0 |
| **Throughput** | Handle 50 concurrent users with <1% error rate | P0 |
| **Stability** | Zero degradation over 8-hour soak test | P1 |
| **Efficiency** | CPU < 60%, memory < 512MB under peak load | P1 |

### 1.2 Key Performance Metrics

| Metric | Definition | Target P95 | Critical Threshold |
|---|---|---|---|
| **Response Time (P50)** | Median response time across all requests | < 200ms | < 500ms |
| **Response Time (P95)** | 95th percentile response time | < 400ms | < 1000ms |
| **Response Time (P99)** | 99th percentile (worst-case outliers) | < 800ms | < 2000ms |
| **Throughput (RPS)** | Requests per second handled successfully | > 50 RPS | > 20 RPS |
| **Error Rate** | Percentage of non-2xx responses | < 0.1% | < 1% |
| **CPU Usage** | Backend server CPU utilization | < 40% | < 80% |
| **Memory Usage** | Backend process RSS | < 200MB | < 512MB |
| **DB Query Time** | Supabase query execution time | < 50ms | < 200ms |
| **AI Inference** | Ollama/Claude response generation | < 3000ms | < 8000ms |

### 1.3 Performance Testing Types

| Test Type | What It Measures | When to Run |
|---|---|---|
| **Load Testing** | Behavior under expected concurrent users | Every PR |
| **Stress Testing** | Breaking point and failure mode | Weekly |
| **Soak Testing** | Memory leaks and degradation over time | Monthly |
| **Spike Testing** | Behavior under sudden traffic surges | Monthly |
| **Scalability Testing** | How performance changes with resources | Per release |

---

## 2. Load Testing Tools

### 2.1 Locust.io (Python)

**Locust** is the primary load testing tool for the Python/FastAPI backend. Test scenarios are written in Python -- the same language as the application.

**Installation:**
```
pip install locust
pip install locust[plugins]
```

**Basic test script (`performance/locustfile.py`):**

```python
from locust import HttpUser, task, between, tag
import random


class SecondBrainOSUser(HttpUser):
    \"\"\"Simulates a real user interacting with the API.\"\"\"

    wait_time = between(1, 5)

    def on_start(self):
        self.token = self.login()

    def login(self):
        response = self.client.post("/api/auth/login", json={
            "email": "perf-test-user@test.com",
            "password": "PerfTest123!",
        })
        return response.json().get("token")

    @task(5)
    @tag("tasks", "read")
    def list_tasks(self):
        self.client.get(
            "/api/tasks/",
            headers={"Authorization": f"Bearer {self.token}"},
        )

    @task(3)
    @tag("tasks", "write")
    def create_task(self):
        self.client.post(
            "/api/tasks/",
            json={
                "title": f"Perf test {random.randint(1, 10000)}",
                "priority": random.choice(["low", "medium", "high", "urgent"]),
            },
            headers={"Authorization": f"Bearer {self.token}"},
        )

    @task(2)
    @tag("tasks", "write")
    def complete_task(self):
        tasks = self.client.get(
            "/api/tasks/?status=pending",
            headers={"Authorization": f"Bearer {self.token}"},
        ).json()
        if tasks:
            task_id = random.choice(tasks)["id"]
            self.client.post(
                f"/api/tasks/{task_id}/complete",
                headers={"Authorization": f"Bearer {self.token}"},
            )

    @task(3)
    @tag("dashboard")
    def view_dashboard(self):
        self.client.get(
            "/api/dashboard/",
            headers={"Authorization": f"Bearer {self.token}"},
        )

    @task(2)
    @tag("courses")
    def list_courses(self):
        self.client.get(
            "/api/courses/",
            headers={"Authorization": f"Bearer {self.token}"},
        )

    @task(1)
    @tag("chat")
    def chat_with_aria(self):
        self.client.post(
            "/api/chat/",
            json={"message": "What is on my schedule today?"},
            headers={"Authorization": f"Bearer {self.token}"},
        )
```

**Running Locust:**
```
# Web UI mode (http://localhost:8089)
locust --host=http://localhost:8000 --users=50 --spawn-rate=5

# Headless mode (for CI)
locust --host=http://localhost:8000 ^
  --headless ^
  --users=50 ^
  --spawn-rate=10 ^
  --run-time=5m ^
  --html=performance/reports/locust-report.html ^
  --json=performance/reports/locust-results.json ^
  --csv=performance/reports/locust-stats

# Tag-specific runs
locust --host=http://localhost:8000 ^
  --headless ^
  --users=100 ^
  --tags "tasks" ^
  --run-time=3m
```

### 2.2 k6 (JavaScript/Go)

For advanced scripting and CI integration, **k6** is used as a secondary tool:

```javascript
// performance/k6-scripts/load-test-tasks.js
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const taskListDuration = new Trend('task_list_duration');
const taskCreateDuration = new Trend('task_create_duration');

export const options = {
  stages: [
    { duration: '2m', target: 20 },
    { duration: '5m', target: 50 },
    { duration: '2m', target: 100 },
    { duration: '3m', target: 100 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<2000'],
    http_req_failed: ['rate<0.01'],
    errors: ['rate<0.05'],
    task_list_duration: ['p(95)<300'],
    task_create_duration: ['p(95)<1000'],
  },
};

const BASE_URL = __ENV.API_URL || 'http://localhost:8000';

export function setup() {
  const loginRes = http.post(BASE_URL + '/api/auth/login', {
    email: 'perf-test-user@test.com',
    password: 'PerfTest123!',
  });
  return { token: loginRes.json('token') };
}

export default function (data) {
  const headers = {
    Authorization: 'Bearer ' + data.token,
    'Content-Type': 'application/json',
  };

  group('Task operations', () => {
    const listRes = http.get(BASE_URL + '/api/tasks/', { headers });
    taskListDuration.add(listRes.timings.duration);
    check(listRes, { 'tasks listed': (r) => r.status === 200 });
    errorRate.add(listRes.status !== 200);

    const createRes = http.post(
      BASE_URL + '/api/tasks/',
      JSON.stringify({ title: 'K6 task ' + Date.now(), priority: 'medium' }),
      { headers }
    );
    taskCreateDuration.add(createRes.timings.duration);
    check(createRes, { 'task created': (r) => r.status === 201 });
    errorRate.add(createRes.status !== 201);

    sleep(1);
  });
}
```

---

## 3. Test Scenarios

### 3.1 Scenario Matrix

| Scenario | Load (RPS) | Duration | Users | Purpose |
|---|---|---|---|---|
| **Baseline Load** | 10 RPS | 10 min | 10 | Establish performance baseline |
| **Expected Load** | 50 RPS | 30 min | 50 | Normal daily peak traffic |
| **Peak Load** | 200 RPS | 15 min | 200 | Maximum expected concurrent usage |
| **Stress Test** | 500 RPS | 5 min | 500 | Find breaking point |
| **Soak Test** | 50 RPS | 8 hours | 50 | Detect memory leaks and degradation |
| **Spike Test** | 10 to 200 RPS | 5 min | 10 to 200 | Sudden traffic surge behavior |

### 3.2 Baseline Load Test (10 RPS, 10 min)

```
locust --headless --users=10 --spawn-rate=2 --run-time=10m --host=http://localhost:8000 --csv=performance/reports/baseline
```

**Expected results:**

| Metric | Target | Warning | Critical |
|---|---|---|---|
| P50 Response | < 100ms | > 200ms | > 500ms |
| P95 Response | < 250ms | > 400ms | > 800ms |
| Error Rate | < 0.1% | > 0.5% | > 1% |
| CPU | < 20% | > 40% | > 60% |
| Memory | < 100MB | > 200MB | > 350MB |

### 3.3 Expected Load Test (50 RPS, 30 min)

```
locust --headless --users=50 --spawn-rate=5 --run-time=30m --host=http://localhost:8000 --csv=performance/reports/expected-load
```

**Expected results:**

| Metric | Target | Warning | Critical |
|---|---|---|---|
| P50 Response | < 200ms | > 300ms | > 500ms |
| P95 Response | < 400ms | > 600ms | > 1000ms |
| Error Rate | < 0.5% | > 1% | > 2% |
| CPU | < 40% | > 60% | > 80% |
| Memory | < 200MB | > 350MB | > 512MB |

### 3.4 Peak Load Test (200 RPS, 15 min)

```
locust --headless --users=200 --spawn-rate=20 --run-time=15m --host=http://localhost:8000 --csv=performance/reports/peak-load
```

**Expected results:**

| Metric | Target | Warning | Critical |
|---|---|---|---|
| P50 Response | < 400ms | > 600ms | > 1000ms |
| P95 Response | < 800ms | > 1200ms | > 2000ms |
| Error Rate | < 1% | > 2% | > 5% |
| CPU | < 60% | > 80% | > 95% |
| Memory | < 350MB | > 500MB | > 750MB |

### 3.5 Stress Test (500 RPS, find breaking point)

The stress test ramps up users until the error rate exceeds 5% or P95 exceeds 5000ms.

```python
# performance/locust-stress.py
from locust import HttpUser, task, between, events


class StressTestUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        resp = self.client.post("/api/auth/login", json={
            "email": "perf-stress-user@test.com",
            "password": "StressTest123!",
        })
        self.token = resp.json().get("token")

    @task
    def hit_endpoint(self):
        self.client.get(
            "/api/tasks/",
            headers={"Authorization": f"Bearer {self.token}"},
        )


@events.quitting.add_listener
def report_breakpoint(environment, **kw):
    stats = environment.runner.stats
    total = stats.num_requests
    failures = stats.num_failures
    error_rate = (failures / total * 100) if total > 0 else 0
    print(f"Total Requests: {total}")
    print(f"Total Failures: {failures}")
    print(f"Error Rate: {error_rate:.2f}%")
```

### 3.6 Soak Test (50 RPS, 8 hours)

**Monitoring script:**

```python
# performance/monitor_soak.py
import time
import psutil
import requests
import csv
from datetime import datetime

API_URL = "http://localhost:8000"
LOG_FILE = "performance/reports/soak-metrics.csv"
POLL_INTERVAL = 60

with open(LOG_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "timestamp", "cpu_pct", "memory_mb", "api_p50_ms",
        "api_p95_ms", "api_error_rate", "db_query_time_ms"
    ])
    while True:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.Process().memory_info().rss / 1024 / 1024
        try:
            health = requests.get(f"{API_URL}/health", timeout=5).json()
        except Exception:
            health = {"p50": -1, "p95": -1, "error_rate": -1}

        writer.writerow([
            datetime.utcnow().isoformat(),
            cpu, memory,
            health.get("p50", -1), health.get("p95", -1),
            health.get("error_rate", -1), health.get("db_query_time", -1),
        ])
        f.flush()
        time.sleep(POLL_INTERVAL)
```

---

## 4. API Endpoint Benchmarks

### 4.1 Endpoint Benchmarking Script

```python
# performance/benchmark_endpoints.py
import asyncio
import time
import statistics
import httpx
from dataclasses import dataclass, field
from typing import List

BASE_URL = "http://localhost:8000"
NUM_REQUESTS = 100
CONCURRENCY = 10


@dataclass
class EndpointBenchmark:
    method: str
    path: str
    p50_ms: float = 0
    p95_ms: float = 0
    p99_ms: float = 0
    avg_ms: float = 0
    min_ms: float = 0
    max_ms: float = 0
    error_rate: float = 0


async def benchmark_endpoint(method: str, path: str, json_data: dict = None):
    bench = EndpointBenchmark(method=method, path=path)
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        for _ in range(5):
            try:
                await client.request(method, path, json=json_data,
                    headers={"Authorization": "Bearer perf-test-token"})
            except Exception:
                pass

        sem = asyncio.Semaphore(CONCURRENCY)

        async def single_request():
            async with sem:
                start = time.perf_counter()
                try:
                    resp = await client.request(method, path, json=json_data,
                        headers={"Authorization": "Bearer perf-test-token"})
                    dur = (time.perf_counter() - start) * 1000
                    return dur, resp.status_code >= 400
                except Exception:
                    dur = (time.perf_counter() - start) * 1000
                    return dur, True

        tasks = [single_request() for _ in range(NUM_REQUESTS)]
        results = await asyncio.gather(*tasks)
        durations = sorted(r[0] for r in results)
        errors = sum(1 for r in results if r[1])

        bench.p50_ms = durations[len(durations) // 2]
        bench.p95_ms = durations[int(len(durations) * 0.95)]
        bench.p99_ms = durations[int(len(durations) * 0.99)]
        bench.avg_ms = statistics.mean(durations)
        bench.min_ms = durations[0]
        bench.max_ms = durations[-1]
        bench.error_rate = (errors / NUM_REQUESTS) * 100

    return bench


async def main():
    endpoints = [
        ("GET", "/api/tasks/"),
        ("POST", "/api/tasks/", {"title": "Benchmark", "priority": "medium"}),
        ("GET", "/api/courses/"),
        ("GET", "/api/goals/"),
        ("GET", "/api/habits/"),
        ("GET", "/api/sleep/"),
        ("GET", "/api/income/"),
        ("GET", "/api/projects/"),
        ("GET", "/api/ideas/"),
        ("GET", "/api/resources/"),
        ("GET", "/api/opportunities/"),
        ("GET", "/api/time/"),
        ("GET", "/api/dashboard/"),
        ("POST", "/api/chat/", {"message": "Hello"}),
    ]

    print(f"{'Endpoint':<40} {'P50':<8} {'P95':<8} {'P99':<8}")
    print("-" * 64)

    results = []
    for endpoint in endpoints:
        method = endpoint[0]
        path = endpoint[1]
        json_data = endpoint[2] if len(endpoint) > 2 else None
        b = await benchmark_endpoint(method, path, json_data)
        results.append(b)
        print(f"{method} {path:<35} {b.p50_ms:<8.1f} {b.p95_ms:<8.1f} {b.p99_ms:<8.1f}")

    results.sort(key=lambda r: r.p95_ms, reverse=True)
    print("\nSlowest endpoints (P95):")
    for r in results[:3]:
        print(f"  {r.method} {r.path} - P95: {r.p95_ms:.1f}ms")


if __name__ == "__main__":
    asyncio.run(main())
```

### 4.2 Expected Benchmark Results

| Endpoint | Method | P50 (ms) | P95 (ms) | P99 (ms) | Critical |
|---|---|---|---|---|---|
| /api/tasks/ | GET | 45 | 120 | 250 | P95 > 500ms |
| /api/tasks/ | POST | 65 | 180 | 350 | P95 > 500ms |
| /api/courses/ | GET | 50 | 140 | 280 | P95 > 500ms |
| /api/goals/ | GET | 40 | 110 | 220 | P95 > 500ms |
| /api/habits/ | GET | 35 | 100 | 200 | P95 > 500ms |
| /api/sleep/ | GET | 30 | 90 | 180 | P95 > 500ms |
| /api/dashboard/ | GET | 80 | 220 | 400 | P95 > 500ms |
| /api/chat/ | POST | 1500 | 3500 | 6000 | P95 > 8000ms |
| /api/auth/login | POST | 200 | 500 | 800 | P95 > 1000ms |

---

## 5. Database Query Performance

### 5.1 N+1 Query Detection

```python
# performance/detect_nplus1.py
from collections import defaultdict


class QueryMonitor:
    def __init__(self):
        self.reset()

    def reset(self):
        self.query_count = 0
        self.queries_by_table = defaultdict(int)
        self.queries_by_endpoint = defaultdict(int)

    def track_query(self, table: str):
        self.query_count += 1
        self.queries_by_table[table] += 1

    def check_nplus1(self, endpoint: str, item_count: int):
        expected = 1 + item_count
        actual = self.queries_by_endpoint[endpoint]
        if actual > expected:
            return {
                "endpoint": endpoint,
                "expected_queries": expected,
                "actual_queries": actual,
                "nplus1_ratio": round(actual / expected, 2),
                "severity": "high" if actual > expected * 2 else "medium",
            }
        return None
```

### 5.2 Slow Query Analysis

```sql
-- Identify slow queries in Supabase
SELECT
    query,
    mean_exec_time,
    calls,
    ROUND(mean_exec_time::numeric, 2) as avg_ms,
    ROUND(total_exec_time::numeric / 1000, 2) as total_seconds
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_%'
ORDER BY mean_exec_time DESC
LIMIT 20;
```

### 5.3 Index Effectiveness

| Table | Column(s) | Index Type | Query Pattern | Improvement |
|---|---|---|---|---|
| tasks | user_id | B-tree | WHERE user_id = ? | 50x |
| tasks | (user_id, status) | Composite B-tree | WHERE user_id = ? AND status = ? | 80x |
| tasks | due_date | B-tree | WHERE due_date < ? | 20x |
| courses | user_id | B-tree | WHERE user_id = ? | 45x |
| habit_logs | (user_id, date) | Composite B-tree | WHERE user_id = ? AND date = ? | 60x |
| chat_messages | (user_id, created_at) | Composite B-tree | ORDER BY created_at DESC LIMIT 50 | 30x |
| sleep_logs | (user_id, date) | Composite B-tree | WHERE user_id = ? ORDER BY date DESC | 40x |
| memory | user_id | B-tree | WHERE user_id = ? | 35x |

---

## 6. AI Inference Latency

### 6.1 Ollama vs Claude Response Times

| Model | Generation Mode | P50 | P95 | P99 | Cost/Req |
|---|---|---|---|---|---|
| Ollama (Mistral 7B) | Synchronous | 1200ms | 2500ms | 5000ms | Free (local) |
| Ollama (Mistral 7B) | Streaming (first token) | 200ms | 500ms | 1000ms | Free (local) |
| Claude Sonnet 4 | Synchronous | 800ms | 1500ms | 3000ms | ~$0.003 |
| Claude Sonnet 4 | Streaming | 300ms | 600ms | 1200ms | ~$0.003 |
| Claude Haiku 3.5 | Synchronous | 400ms | 800ms | 1500ms | ~$0.001 |

### 6.2 Streaming Latency Monitoring

```python
# performance/measure_ai_latency.py
import asyncio
import time
import statistics
from ai.client import LLMClient


async def measure_ai_latency(num_samples: int = 20):
    client = LLMClient()
    latencies = []
    ttft_latencies = []
    tokens_per_second = []

    for i in range(num_samples):
        start = time.perf_counter()
        response = await client.generate_json(
            "Generate a one-paragraph summary of task management best practices."
        )
        duration = (time.perf_counter() - start) * 1000
        latencies.append(duration)

    print(f"AI Inference Latency Report ({num_samples} samples):")
    latencies.sort()
    print(f"  P50: {statistics.median(latencies):.0f}ms")
    print(f"  P95: {latencies[int(len(latencies) * 0.95)]:.0f}ms")
    print(f"  P99: {latencies[int(len(latencies) * 0.99)]:.0f}ms")


if __name__ == "__main__":
    asyncio.run(measure_ai_latency())
```

### 6.3 Token Generation Speed

| Model | Tokens/Sec (avg) | Latency Variability | Best For |
|---|---|---|---|
| Ollama Mistral 7B (4-bit quantized) | 25 tok/s | High | Background agents (memory, learning) |
| Ollama Mistral 7B (FP16) | 15 tok/s | Medium | Briefing generation |
| Claude Sonnet 4 | 45 tok/s | Low | Real-time chat |
| Claude Haiku 3.5 | 60 tok/s | Very Low | Quick nudges, simple classifications |

---

## 7. Frontend Performance

### 7.1 Web Vitals Targets

| Metric | Target | Warning | Critical |
|---|---|---|---|
| **LCP** (Largest Contentful Paint) | < 1.5s | > 2.5s | > 4.0s |
| **FID** (First Input Delay) | < 50ms | > 100ms | > 300ms |
| **CLS** (Cumulative Layout Shift) | < 0.05 | > 0.1 | > 0.25 |
| **TTI** (Time to Interactive) | < 2.0s | > 3.5s | > 5.0s |
| **TBT** (Total Blocking Time) | < 100ms | > 200ms | > 500ms |
| **FCP** (First Contentful Paint) | < 1.0s | > 1.5s | > 3.0s |

### 7.2 Performance Measurement in E2E

```typescript
// e2e/performance.spec.ts
import { test, expect } from '@playwright/test'

test('dashboard meets Web Vitals targets', async ({ page }) => {
  await page.goto('/dashboard', { waitUntil: 'networkidle' })

  const metrics = await page.evaluate(() => {
    return new Promise((resolve) => {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        const result: Record<string, number> = {}
        entries.forEach((entry) => {
          result[entry.name] = entry.startTime
        })
        resolve(result)
      })
      observer.observe({ type: 'largest-contentful-paint', buffered: true })
    })
  })

  // @ts-ignore
  expect(metrics['largest-contentful-paint']).toBeLessThan(2500)
})
```

### 7.3 Bundle Size Budget

| Asset | Budget (gzipped) | Enforcement |
|---|---|---|
| Main JS bundle | < 300KB | webpack-bundle-analyzer in CI |
| Route chunks | < 50KB each | next/bundle-analyzer |
| CSS (Tailwind + custom) | < 30KB | CI size check |
| Fonts (Syne, DM Sans, JetBrains Mono) | < 100KB | Preloaded, self-hosted |
| Images per page | < 200KB | next/image optimization |
| Total page weight | < 750KB | Lighthouse CI |

### 7.4 Bundle Analysis CI

```yaml
# .github/workflows/bundle-size.yml
name: Bundle Size Check
on: [pull_request]

jobs:
  bundle-size:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
      - run: npm ci
      - run: npm run build

      - name: Check bundle size
        run: |
          npx next-bundle-analyzer
          node -e "
            const fs = require('fs');
            const stats = JSON.parse(fs.readFileSync('.next/stats.json'));
            const mainJs = stats.assets.find(a =>
              a.name.endsWith('.js') && a.name.includes('main'));
            const sizeKB = mainJs.size / 1024;
            console.log('Main JS bundle:', sizeKB.toFixed(1), 'KB');
            if (sizeKB > 300) {
              console.error('FAIL: Main JS exceeds 300KB budget');
              process.exit(1);
            }
            console.log('PASS: Bundle within budget');
          "
```

---

## 8. Lighthouse CI Thresholds and Regression Detection

### 8.1 Lighthouse Configuration

```json
{
  "ci": {
    "collect": {
      "startServerCommand": "npm run start -- --port 3000",
      "url": [
        "http://localhost:3000/",
        "http://localhost:3000/login",
        "http://localhost:3000/dashboard",
        "http://localhost:3000/tasks"
      ],
      "numberOfRuns": 3,
      "settings": {
        "preset": "desktop",
        "throttlingMethod": "simulate"
      }
    },
    "assert": {
      "preset": "lighthouse:recommended",
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "categories:accessibility": ["error", { "minScore": 0.95 }],
        "categories:best-practices": ["error", { "minScore": 0.95 }],
        "categories:seo": ["error", { "minScore": 0.95 }],
        "first-contentful-paint": ["error", { "maxNumericValue": 1500 }],
        "largest-contentful-paint": ["error", { "maxNumericValue": 2500 }],
        "cumulative-layout-shift": ["error", { "maxNumericValue": 0.1 }],
        "total-blocking-time": ["error", { "maxNumericValue": 200 }],
        "interactive": ["error", { "maxNumericValue": 3500 }]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

### 8.2 Regression Detection

```yaml
# .github/workflows/performance-regression.yml
name: Performance Regression Detection
on:
  pull_request:
    types: [opened, synchronize]
  schedule:
    - cron: '0 8 * * 1'

jobs:
  lighthouse-compare:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4

      - name: Build and run Lighthouse
        run: |
          npm ci
          npm run build
          npx lhci autorun --collect.url=http://localhost:3000/dashboard

      - name: Compare with baseline
        run: |
          node -e "
            const current = require('./lighthouse-report.json');
            const baseline = require('./baseline.json');
            const metrics = ['performance', 'accessibility', 'best-practices', 'seo'];
            let regressions = 0;
            for (const m of metrics) {
              const diff = current.categories[m].score - baseline.categories[m].score;
              if (diff < -0.05) {
                console.error('REGRESSION:', m, 'dropped by', (diff * 100).toFixed(1) + '%');
                regressions++;
              }
            }
            if (regressions > 0) process.exit(1);
          "
```

---

## 9. Performance Regression Test Suite

### 9.1 Running on Every PR

```yaml
name: Performance Regression
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  perf-regression:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4

      - name: Install and build
        run: |
          npm ci
          npm run build

      - name: Lighthouse check
        run: npx lhci autorun || echo "Lighthouse check completed"

      - name: API response time check
        run: |
          pip install -r apps/api/requirements.txt
          uvicorn main:app --host 0.0.0.0 --port 8000 &
          sleep 5
          python performance/benchmark_endpoints.py
```

### 9.2 Performance Pass/Fail Criteria

| Check | Threshold | Action |
|---|---|---|
| Lighthouse Performance score | < 85 | Block PR |
| Lighthouse Accessibility score | < 90 | Block PR |
| API P95 response time (any endpoint) | > 1000ms | Block PR |
| JS bundle size increase | > 10% | Block PR |
| New N+1 query pattern | Detected | Block PR |
| Chat endpoint P95 | > 5000ms | Warn (not block) |
| Lighthouse score decrease | > 5 points | Block PR |

---

## 10. Performance Budget

### 10.1 Budget Definition

```json
{
  "budgets": [
    {
      "path": "/dashboard",
      "resourceCounts": [
        { "resourceType": "script", "budget": 10 },
        { "resourceType": "stylesheet", "budget": 5 },
        { "resourceType": "image", "budget": 15 },
        { "resourceType": "font", "budget": 5 },
        { "resourceType": "total", "budget": 35 }
      ],
      "resourceSizes": [
        { "resourceType": "script", "budget": 300 },
        { "resourceType": "stylesheet", "budget": 30 },
        { "resourceType": "image", "budget": 300 },
        { "resourceType": "font", "budget": 100 },
        { "resourceType": "total", "budget": 750 }
      ],
      "timings": [
        { "metric": "interactive", "budget": 5000 },
        { "metric": "first-contentful-paint", "budget": 2000 }
      ]
    },
    {
      "path": "/tasks",
      "resourceSizes": [
        { "resourceType": "script", "budget": 280 },
        { "resourceType": "total", "budget": 650 }
      ]
    }
  ]
}
```

### 10.2 Remediation Strategies

| Issue | Remediation |
|---|---|
| Large JS bundle | Code splitting, dynamic imports, tree shaking |
| Slow API response | Database query optimization, caching, pagination |
| High LCP | Optimize images, preload hero, reduce server response time |
| High CLS | Set explicit dimensions on images, reserve space for dynamic content |
| High TBT | Break up long tasks, use web workers, code splitting |
| Slow AI inference | Use streaming, reduce prompt size, cache common responses |
| N+1 queries | Eager loading, batch queries, GraphQL-style resolvers |
| Memory leaks | Fix event listener cleanup, weak references, pool connections |

---

## 11. Performance Monitoring in Production

### 11.1 Real User Monitoring (RUM)

```typescript
// apps/web/app/lib/rum.ts
export function initRUM() {
  if (typeof window === 'undefined') return

  const observer = new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
      sendMetric({
        name: entry.name,
        value: entry.startTime,
        type: 'web-vital',
        url: window.location.pathname,
        timestamp: Date.now(),
      })
    }
  })

  observer.observe({ type: 'largest-contentful-paint', buffered: true })
  observer.observe({ type: 'first-input', buffered: true })
  observer.observe({ type: 'layout-shift', buffered: true })

  window.addEventListener('load', () => {
    const navigation = performance.getEntriesByType('navigation')[0]
    sendMetric({
      name: 'TTFB',
      value: navigation.responseStart - navigation.requestStart,
      type: 'navigation',
    })
  })
}

function sendMetric(metric: Record<string, unknown>) {
  const blob = new Blob([JSON.stringify(metric)], { type: 'application/json' })
  navigator.sendBeacon('/api/analytics/vitals', blob)
}
```

### 11.2 APM Integration

```python
# packages/shared/utils/apm.py
import os
import time
import functools
from dataclasses import dataclass, field
from typing import Optional

BACKEND = os.getenv("APM_BACKEND", "none")


@dataclass
class APMTrace:
    name: str
    start_ns: int = field(default_factory=time.perf_counter_ns)
    end_ns: Optional[int] = None
    tags: dict = field(default_factory=dict)
    error: Optional[str] = None

    @property
    def duration_ms(self) -> float:
        end = self.end_ns or time.perf_counter_ns()
        return (end - self.start_ns) / 1_000_000

    def finish(self, error: Optional[str] = None):
        self.end_ns = time.perf_counter_ns()
        self.error = error
        if BACKEND == "datadog":
            self._send_datadog()
        elif BACKEND == "newrelic":
            self._send_newrelic()

    def _send_datadog(self):
        pass

    def _send_newrelic(self):
        pass


def monitor(name: str, **default_tags):
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            trace = APMTrace(name=name, tags={**default_tags})
            try:
                result = await func(*args, **kwargs)
                trace.finish()
                return result
            except Exception as e:
                trace.finish(error=str(e))
                raise

        return async_wrapper

    return decorator
```

### 11.3 Custom Metrics Dashboard

| Metric | Source | Dashboard Panel |
|---|---|---|
| P50/P95/P99 API latency | Locust / APM | Latency heatmap |
| RPS per endpoint | Load balancer | Throughput chart |
| Error rate by status code | API middleware | Error rate gauge |
| CPU/Memory per service | Docker stats | Resource usage |
| DB query time | Supabase pg_stat_statements | Query performance |
| AI inference latency | APM monitor | AI response times |
| Web Vitals (LCP, FID, CLS) | RUM beacon | User experience |
| Bundle size | Build step | Bundle size trend |
| Lighthouse scores | CI | Score trend |
| Cache hit ratio | Cache middleware | Cache efficiency |

---

## 12. Reporting

### 12.1 Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Second Brain OS - Performance",
    "panels": [
      {
        "title": "API Latency (P95 by Endpoint)",
        "type": "graph",
        "targets": [
          {
            "measurement": "api_latency",
            "field": "p95",
            "groupBy": ["endpoint"]
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "singlestat",
        "targets": [{ "measurement": "api_errors", "field": "error_rate" }],
        "thresholds": "1,5",
        "colors": ["green", "yellow", "red"]
      },
      {
        "title": "Web Vitals - Last 7 Days",
        "type": "graph",
        "targets": [
          { "measurement": "web_vitals", "field": "LCP", "alias": "LCP" },
          { "measurement": "web_vitals", "field": "FID", "alias": "FID" },
          { "measurement": "web_vitals", "field": "CLS", "alias": "CLS" }
        ]
      },
      {
        "title": "Active Users",
        "type": "singlestat",
        "targets": [{ "measurement": "active_users", "field": "count" }]
      }
    ]
  }
}
```

### 12.2 Performance Scorecard (Per Release)

| Metric | Baseline | Current Release | Delta | Status |
|---|---|---|---|---|
| Tasks endpoint P95 | 120ms | 115ms | -5ms | Green |
| Dashboard P95 | 220ms | 245ms | +25ms | Yellow |
| Chat P95 | 3500ms | 3200ms | -300ms | Green |
| Lighthouse Performance | 92 | 91 | -1 | Green |
| JS Bundle | 245KB | 258KB | +13KB | Yellow |
| Error Rate | 0.05% | 0.08% | +0.03% | Green |
| Memory (peak) | 180MB | 195MB | +15MB | Green |

### 12.3 Performance Regression Report Template

```
PERFORMANCE REGRESSION REPORT
=============================
PR: #1234 - Add course progress tracking
Date: 2026-06-11
Author: @developer

RESULTS
-------
- Lighthouse: PASS (Performance: 91 vs baseline 92)
- Bundle size: WARN (258KB vs budget 300KB, +5% from baseline)
- API P95: PASS (all endpoints within thresholds)
- N+1 check: PASS (no pattern detected)

ACTION ITEMS
------------
1. Investigate bundle size increase (+13KB from date-fns import)
   Owner: @developer  Priority: Low

VERDICT: APPROVED with warnings
```

---

*Document ID: SB-QA-PERF-001 | Version: 1.0.0 | Status: Active | Last Updated: 2026-06-11*
