# Error Budget Policy — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| **Document ID** | OPS-EBG-001 |
| **Version** | 1.0.0 |
| **Status** | Active |
| **Classification** | Internal — Operations |
| **Last Updated** | 2026-07-11 |
| **Next Review** | 2026-10-11 |
| **Review Cycle** | Quarterly |
| **Approved By** | Developer |
| **SLA Tier** | Tier 1 (Critical) |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [SLO Definitions](#2-slo-definitions)
3. [Error Budget Calculation](#3-error-budget-calculation)
4. [Budget Consumption Tracking](#4-budget-consumption-tracking)
5. [Consequences by Consumption Level](#5-consequences-by-consumption-level)
6. [Budget Restoration](#6-budget-restoration)
7. [Quarterly Review Process](#7-quarterly-review-process)
8. [Related Documents](#8-related-documents)

---

## 1. Introduction

### 1.1 What is an Error Budget?

An **error budget** is the maximum amount of downtime or degraded performance a service can tolerate over a given measurement window before violating its Service Level Objective (SLO). It is defined as:

```
Error Budget = 1 - SLO Target
```

For example, a service with a 99.5% SLO target has an error budget of 0.5% downtime over the measurement window — approximately 3.6 hours per 30-day month.

### 1.2 Why Error Budgets Matter

Error budgets bridge the gap between **velocity** and **reliability**:

- **When the budget is available:** Teams may deploy new features with confidence, accepting calculated risk.
- **When the budget is depleted:** All efforts shift to reliability — feature development freezes, incident response is prioritised, and root-cause fixes are mandatory.

This creates a data-driven mechanism that prevents burnout (endless reliability firefighting) and stagnation (fearing every deployment).

### 1.3 Scope

This policy applies to all production services of Second Brain OS: FastAPI backend, Next.js frontend, Supabase database, AI agent system, and the APScheduler cron subsystem.

---

## 2. SLO Definitions

| Service | SLO Target | Measurement Window | Error Budget (downtime) |
|---|---|---|---|
| API p95 latency | < 500ms | 30 days rolling | N/A |
| AI response time | < 30s | 30 days rolling | N/A |
| DB query time | < 200ms | 30 days rolling | N/A |
| Frontend TTI | < 3s | 30 days rolling | N/A |
| Frontend bundle size | < 300KB gzip | Per build | N/A |
| Uptime (API) | 99.5% | 30 days rolling | ~3.6 hours |
| Uptime (Frontend) | 99.9% | 30 days rolling | ~43 minutes |

### 2.1 SLO Definitions

| Term | Definition |
|---|---|
| **SLO Target** | The reliability target expressed as a percentage of successful events over total events. |
| **Measurement Window** | The rolling time period over which SLO compliance is evaluated. |
| **Error Budget** | The tolerated failure budget = (1 - SLO) × total possible good events in window. |
| **Burn Rate** | The rate at which the error budget is consumed. A burn rate > 1 indicates budget is being consumed faster than planned. |

### 2.2 Latency Budgets

Latency SLOs are measured as the percentage of requests completing under the threshold:

| Service | Threshold | Target | Window |
|---|---|---|---|
| API p95 latency | 500ms | ≥ 95% of requests | 30 days |
| AI response time | 30s | ≥ 90% of requests | 30 days |
| DB query time | 200ms | ≥ 98% of requests | 30 days |
| Frontend TTI | 3s | ≥ 95% of page loads | 30 days |

For latency SLOs, the error budget is based on the number of requests exceeding the threshold rather than absolute downtime. Each request that exceeds the threshold consumes a portion of the budget.

### 2.3 Bundle Size Budget

| SLO | Target | Window |
|---|---|---|
| Frontend bundle size | < 300KB gzip | Per build |

The bundle size budget is assessed at build time. A single build exceeding 300KB gzip is treated as a full budget exhaustion event for that SLO.

---

## 3. Error Budget Calculation

### 3.1 Formula

```
budget_remaining = ((total_budget - total_budget_consumed) / total_budget) × 100
```

Where:

- **total_budget** = total possible good events in the measurement window × (1 - SLO)
- **total_budget_consumed** = count of events that failed the SLO threshold
- **budget_remaining** = percentage of budget still available

### 3.2 Example: API Uptime

For a 30-day window (2,592,000 seconds) with a 99.5% SLO target:

```
total_budget = 2,592,000 × (1 - 0.995) = 12,960 seconds = 3.6 hours
```

If the API was down for 1 hour (3,600 seconds):

```
budget_consumed = 3,600 seconds
budget_remaining = ((12,960 - 3,600) / 12,960) × 100 = 72.2%
```

### 3.3 Example: API Latency

For 100,000 requests in a 30-day window with a 95th-percentile latency SLO of 500ms:

```
total_budget = 100,000 × (1 - 0.95) = 5,000 requests
```

If 2,000 requests exceeded 500ms:

```
budget_remaining = ((5,000 - 2,000) / 5,000) × 100 = 60%
```

---

## 3.4 Budget Consumption Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Healthy: Budget > 50%
    Healthy --> AtRisk: Budget 20–50%
    AtRisk --> Critical: Budget 0–20%
    Critical --> Exhausted: Budget = 0%
    
    Healthy --> Healthy: Normal operations<br/>Deploy freely
    AtRisk --> AtRisk: Reduce feature velocity<br/>CI + Manual QA required
    Critical --> Critical: Deploy freeze<br/>Daily reliability stand-ups
    Exhausted --> Exhausted: All hands on deck<br/>Incident response activated

    Exhausted --> AtRisk: Accelerated restoration<br/>(max 20% credit)
    Critical --> Healthy: Rollover to new<br/>measurement window

    note right of Healthy: Target: > 50% at all times
    note right of Exhausted: P0 incident declared
```

## 4. Budget Consumption Tracking

### 4.1 Tracking Sources

| Source | Tool | Data |
|---|---|---|
| API uptime | Railway health checks, custom `/health` | Uptime % per day |
| API latency | Custom metrics middleware, Logtail | p50/p95/p99 latency per endpoint |
| AI response time | LLM client timing in `packages/ai/client.py` | Duration per agent call |
| DB query time | Supabase dashboard, Logtail | Query duration |
| Frontend TTI | Lighthouse CI, Vercel Analytics | TTI percentiles |
| Bundle size | `next/bundle-analyzer`, CI artifact | Gzip size |

### 4.2 Consumption Events

An **SLO violation** (budget consumption event) is recorded when:

1. **Uptime:** Any 5-minute window where the API is unreachable (0% availability).
2. **Latency:** Any request whose duration exceeds the service's latency threshold.
3. **Bundle size:** Any production build whose main JS bundle exceeds 300KB gzip.
4. **AI response:** Any agent call whose total duration exceeds its SLO threshold.

### 4.3 Recording & Alerting

- Consumption events are logged via structured JSON logging with event type `slo_violation`.
- The RED metrics dashboard (see [monitoring-guide.md](./monitoring-guide.md)) tracks running budget consumption.
- At 50% consumption, a **WARN** alert fires to the operations channel.
- At 80% consumption, a **CRITICAL** alert fires with P1 severity.
- At 100% consumption, an **EMERGENCY** incident is declared with P0 severity.

---

## 5. Consequences by Consumption Level

### 5.1 Consumption Thresholds

| Budget Remaining | Status | Actions |
|---|---|---|
| > 50% | **Healthy** | Normal operations. Feature development continues. Deployments proceed normally. |
| 20% – 50% | **At Risk** | Reliability review required. Feature velocity reduced by 50%. Bug fixes prioritised over new features. All deployments require CI + manual QA approval. |
| 0% – 20% | **Critical** | Deploy freeze on all non-critical changes. Full team focus on SLO recovery. Daily reliability stand-ups. Any deployment requires CTO sign-off. |
| 0% (Exhausted) | **Emergency** | All hands on deck. Incident response activated per [40_IncidentResponse.md](./40_IncidentResponse.md). Root-cause analysis mandatory. Feature development frozen until budget is restored above 20%. |

### 5.2 Decision Matrix

| Scenario | Can deploy? | Can add features? | Must fix reliability? |
|---|---|---|---|
| Budget > 50% | Yes | Yes | No |
| Budget 20–50% | Yes (with approval) | Reduced | Yes |
| Budget < 20% | No (exceptions only) | No | Yes — full team |
| Budget exhausted | No | No | Yes — emergency |

### 5.3 Exceptions

The CTO / Tech Lead may grant a **reliability budget override** for:
- Security patches (critical/high severity CVEs)
- Data loss prevention fixes
- Legal or compliance-mandated changes

All overrides must be documented with a justification and an associated Jira ticket.

---

## 6. Budget Restoration

### 6.1 Automatic Restoration

Error budgets reset automatically at the start of each new measurement window (rolling 30 days). As time passes and old violations fall out of the window, the budget is restored proportionally.

### 6.2 Accelerated Restoration

Teams may accelerate budget restoration through **reliability improvement initiatives**:

| Activity | Budget Credit |
|---|---|
| Implement circuit breaker on a previously unprotected dependency | +5% of window budget |
| Reduce p95 latency by > 20% for any service | +10% of that service's budget |
| Achieve 100% test pass rate with > 90% coverage for 7 consecutive days | +5% of window budget |
| Complete a blameless postmortem with actionable follow-ups | +2% per postmortem |
| Deploy an SLO-monitoring improvement (new dashboard/alert) | +2% per improvement |

Accelerated restoration credits are capped at 30% of the total budget per window and are applied immediately.

### 6.3 Partial Restoration

When a budget is exhausted mid-window, reliability improvements can restore the budget to a maximum of 20% — sufficient to resume normal operations but maintaining a heightened reliability posture.

---

## 7. Quarterly Review Process

### 7.1 Review Cadence

| Review | Frequency | Participants | Agenda |
|---|---|---|---|
| SLO Tuning | Quarterly | CTO, SRE, Engineering Leads | Review SLO targets, adjust if needed |
| Budget Consumption | Monthly | On-Call Engineer, DevOps | Analyse consumption patterns, identify trends |
| Post-Incident | Per P0/P1 | Full incident response team | Blameless postmortem, action items |

### 7.2 Quarterly Review Agenda

1. **SLO Attainment:** Did each service meet its SLO target? Review burn rate charts.
2. **Budget Consumption Trends:** Which services consumed the most budget? Are there recurring patterns?
3. **Top Violations:** Identify the top 3 causes of budget consumption. Plan mitigations.
4. **SLO Target Adjustment:** Should any SLO targets be tightened or loosened based on data?
5. **Reliability Investments:** Review past reliability projects. Did they improve budget health?
6. **Policy Updates:** Update this document if process changes are required.

### 7.3 Review Outputs

Each quarterly review produces:
- Updated SLO targets (if needed) with version bump to this document
- A ranked list of top reliability risks
- Action items with owners and deadlines
- Updated error budget consumption forecasts

---

## 8. Related Documents

| Document | Relationship |
|---|---|
| [monitoring-guide.md](./monitoring-guide.md) | Defines the RED metrics, alerting rules, and dashboards used to measure SLO compliance. |
| [39_Runbooks.md](./39_Runbooks.md) | Operational runbooks for responding to incidents that consume error budgets. |
| [40_IncidentResponse.md](./40_IncidentResponse.md) | Incident severity definitions and escalation procedures triggered at budget exhaustion. |
| [31_Observability.md](./31_Observability.md) | Observability architecture that powers SLO tracking and alerting. |
| [AGENTS.md](../../AGENTS.md) | Project master reference — Section 18 (Cost & Performance) and Section 26 (Performance Benchmarks). |
| [openapi-reference.md](../engineering/api/openapi-reference.md) | API rate limiting and endpoint latency expectations. |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-07-11 | Developer | Initial error budget policy: SLO definitions, calculation formula, consumption tracking, consequences, restoration, and quarterly review process. |

