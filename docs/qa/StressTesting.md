# Stress Testing

## Document Control

| Field | Value |
|---|---|
| Document ID | QA-STR-011 |
| Version | 1.0.0 |
| Status | Draft |
| Date | 2026-07-10 |
| Classification | Internal |
| Owner | Developer |

---

## 1. Executive Summary

### Purpose
Define the stress testing strategy for Second Brain OS. Stress testing pushes the system beyond normal operating capacity to identify breaking points, failure modes, and recovery behavior. Unlike load testing (which tests expected traffic), stress testing answers "what breaks and how?"

### Scope
Covers stress testing for FastAPI backend (Railway free tier), Supabase database (free tier), AI providers, APScheduler, and frontend rendering.

---

## 2. Stress vs Load Testing

| Aspect | Load Testing | Stress Testing |
|---|---|---|
| **Goal** | Verify performance under expected load | Find breaking points |
| **Traffic** | Realistic (7-20 RPM) | Extreme (50-500+ RPM) |
| **Duration** | Sustained (minutes) | Short bursts (seconds) |
| **Outcome** | Performance metrics | Failure modes & recovery |
| **Frequency** | Weekly | Per major release |

---

## 3. Stress Test Scenarios

### 3.1 API Stress Test

```javascript
// tests/performance/stress-test-api.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 10 },   // Warm up
    { duration: '10s', target: 100 },  // Ramp up to 100 VUs
    { duration: '20s', target: 200 },  // Extreme load
    { duration: '10s', target: 0 },    // Cool down
  ],
  thresholds: {
    http_req_duration: ['p(95) < 10000'],  // Allow slow responses
    http_req_failed: ['rate < 0.5'],        // Allow 50% failures
  },
};
```

### 3.2 Concurrent AI Call Stress Test

```javascript
// tests/performance/stress-test-ai.js
export const options = {
  stages: [
    { duration: '5s', target: 1 },
    { duration: '10s', target: 10 },  // 10 concurrent AI calls
    { duration: '5s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95) < 60000'],
    'circuit_breaker_open': ['count < 3'],  // Expect some CB opens
    'fallback_used': ['count < 10'],
  },
};
```

### 3.3 Database Connection Stress Test

```javascript
// tests/performance/stress-test-db.js
export const options = {
  vus: 50,
  duration: '30s',
  thresholds: {
    'db_connection_errors': ['rate < 0.1'],
    http_req_duration: ['p(95) < 5000'],
  },
};

export default function () {
  // Simulate heavy read/write pattern
  const batchSize = 10;
  for (let i = 0; i < batchSize; i++) {
    http.get(`${BASE_URL}/tasks?limit=100`);
    http.post(`${BASE_URL}/tasks`, payload);
  }
}
```

---

## 4. Breaking Point Identification

| Component | Expected Breaking Point | Failure Mode |
|---|---|---|
| Railway Free RAM (512MB) | ~50 concurrent requests | OOM kill, 502 errors |
| Railway Free CPU | ~100 RPM (CRUD) | Latency > 10s |
| Supabase Free (2 conns) | ~3 concurrent queries | Connection timeout |
| Supabase Free (500MB) | ~10K+ records queried | Slow queries > 5s |
| Ollama (CPU inference) | ~3 concurrent requests | Queue time > 30s |
| Claude API (5 RPM) | 6th request in same minute | 429 rate limited |

---

## 5. Recovery Testing

### 5.1 Recovery Scenarios

| Scenario | Injection | Expected Recovery |
|---|---|---|
| Process crash | Kill API process | Railway auto-restart < 30s |
| Memory exhaustion | Trigger OOM | Restart, cold start < 10s |
| Circuit breaker open | 5 AI failures | Auto-recover after 60s cooldown |
| Database timeout | Slow query | Subsequent queries succeed |
| Rate limit hit | > 100 requests/min | 429 for 60s, then normal |

### 5.2 Recovery Verification

```python
# tests/performance/verify_recovery.py
async def test_circuit_breaker_recovery():
    """Verify CB opens after failures and recovers."""
    # Step 1: Trigger 5 AI failures
    for _ in range(5):
        await trigger_ai_failure()
    
    # Verify CB is open
    state = await get_circuit_breaker_state()
    assert state == "OPEN"
    
    # Step 2: Wait for recovery
    await asyncio.sleep(60)
    
    # Step 3: Verify CB has recovered
    state = await get_circuit_breaker_state()
    assert state == "HALF_OPEN"
    
    # Step 4: Successful request should close it
    response = await make_ai_request()
    assert response.status == 200
    state = await get_circuit_breaker_state()
    assert state == "CLOSED"
```

---

## 6. Metrics Collection

| Metric | Collection Point | What It Tells Us |
|---|---|---|
| HTTP 502/503 count | Railway logs | Backend overloaded |
| Memory usage | Railway dashboard | Leak or OOM risk |
| CPU usage | Railway dashboard | Computation bottleneck |
| Response time P99 | k6 output | Worse-case latency |
| Error rate | k6 output | System stability |
| Circuit breaker state | Application logs | AI provider health |
| Database connections | Supabase dashboard | Connection pool status |

---

## 7. Test Execution

```bash
# Run all stress tests
cd tests/performance
k6 run stress-test-api.js --out json=stress-report.json
k6 run stress-test-ai.js --out json=stress-ai-report.json
k6 run stress-test-db.js --out json=stress-db-report.json

# Combine reports
python scripts/combine-stress-reports.py
```

---

## 8. Success Criteria

| Criteria | Target |
|---|---|
| Graceful degradation under stress | No unhandled crashes |
| Recovery within 60s after stress ends | Full functionality restored |
| No data corruption | Verify record counts after test |
| Circuit breaker isolates failures | Failing provider doesn't crash system |
| Rate limiting protects resources | 429 before 500 |

---

## 9. Performance Targets

| Metric | Target |
|---|---|
| Peak RPM before 50% error rate | > 200 RPM (CRUD) |
| Recovery time after stress | < 30 seconds |
| Memory leak (30 min soak) | < 5% increase |
| Circuit breaker recovery | < 60 seconds |

---

## 10. Edge Cases

| Edge Case | Handling |
|---|---|
| Test exceeds free tier limits | Accept as finding, document limits |
| Railway auto-scales (unlikely on free) | Note in report |
| Database locks from concurrent writes | Supabase handles row-level locking |
| AI provider queues concurrent requests | Circuit breaker pattern handles it |

---

## 11. Failure Scenarios

| Scenario | Impact | Mitigation |
|---|---|---|
| Production degradation from test | Use staging only | Environment check in scripts |
| Data loss during stress test | Seed data loss | Refresh seed after test |
| Test script bug causing real load | Monitor and kill switch | `kill $(lsof -t -i:8000)` |

---

## 12. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Identifying low breaking points | High | Low | Document free tier limits |
| Over-engineering for scale | Low | Medium | Focus on single-user resilience |
| Production-like stress impossible | Medium | Low | Accept staging-only testing |

---

## 13. Related Documents

| Document | Relation |
|---|---|
| docs/qa/LoadTesting.md | Standard load testing |
| docs/qa/ChaosTesting.md | Fault injection testing |
| docs/qa/PerformanceTesting.md | Performance benchmarks |
| docs/operations/39_Runbooks.md | Recovery runbooks |

---

## 14. Appendices

### 14.1 Stress Test Report Template

```markdown
# Stress Test Report

**Date:** YYYY-MM-DD
**Test:** [API/AI/DB]
**Environment:** staging

## Summary
- Peak load: [N] VUs / [N] RPM
- Breaking point: [N] VUs / [N] RPM
- Failure mode: [description]
- Recovery time: [N] seconds

## Findings
1. [Finding 1]
2. [Finding 2]

## Actions
- [ ] Action item 1
- [ ] Action item 2
```

### 14.2 Required Tools

```bash
k6 version  # Must be >= 0.45
python --version  # >= 3.10
```
