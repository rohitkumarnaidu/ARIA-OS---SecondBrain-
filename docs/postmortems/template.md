# Incident Postmortem: [Title]

## Document Control

| Field | Value |
|---|---|
| Document ID | PSM-[NNN] |
| Version | 1.0.0 |
| Status | Draft |
| Classification | Internal — Incident Analysis |

## Incident Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Normal: System operational
    Normal --> Detected: Alert / User report
    Detected --> Triaged: Severity assigned
    Triaged --> Contained: Mitigation applied
    Contained --> Eradicated: Root cause fixed
    Eradicated --> Resolved: Service restored
    Resolved --> Normal: Monitoring confirms

    Detected --> Escalated: Severity > capacity
    Escalated --> Triaged: Additional resources

    Resolved --> Postmortem: Within 48h (P0/P1)
    Postmortem --> [*]: Lessons learned

    note right of Normal: Target: 99.5% uptime
    note right of Contained: SLA: 15min-2hr depending on severity
```

## Summary

[2-3 sentences describing what happened, the impact on users, and the total duration of the incident.]

## Severity

P0 / P1 / P2 / P3

## Timeline

| Time (UTC) | Event |
|---|---|
| HH:MM | [Detection or start of incident] |
| HH:MM | [Triage started — who responded] |
| HH:MM | [Mitigation applied — what was done] |
| HH:MM | [Resolution confirmed — service restored] |
| HH:MM | [Post-incident review initiated] |

## Detection

How was this incident detected? (e.g., automated alert, user report, monitoring dashboard, manual check)

## Root Cause

A clear technical explanation of what caused the incident. Include relevant system context, component interactions, and the chain of events leading to the failure.

## Impact

| Metric | Value |
|---|---|
| Users affected | [# or description] |
| Service downtime | [HH:MM] |
| Data loss | [Yes / No — if yes, describe extent] |
| Financial impact | [if applicable] |
| Degraded experience | [if partial degradation] |

## Action Items

| Action | Owner | Tracked In | Status |
|---|---|---|---|
| [Fix root cause] | @person | Issue #NNN | Open |
| [Add monitoring/alerting] | @person | Issue #NNN | Open |
| [Update runbook] | @person | PR #NNN | Open |
| [Add regression test] | @person | PR #NNN | Open |
| [Document lesson learned] | @person | Issue #NNN | Open |

## Lessons Learned

### What Went Well
- [Item 1: What worked as expected during the incident]
- [Item 2: What tooling or process helped]
- [Item 3: What the team did right]

### What Went Wrong
- [Item 1: What should not have happened]
- [Item 2: What tooling or process was missing]
- [Item 3: What slowed down response time]

### What We'll Do Differently
- [Item 1: Specific process change to prevent recurrence]
- [Item 2: Tooling or monitoring improvements]
- [Item 3: Training or documentation updates]

## Related Documents

- [Incident Response Playbook](../operations/40_IncidentResponse.md) — Full incident lifecycle, severity definitions, escalation matrix
- [Operations Runbooks](../operations/39_Runbooks.md) — RB-001 through RB-013 runbooks (SDVRP format, decision trees)
- [Error Budget Policy](../operations/error-budget.md) — SLO definitions and budget consumption tracking
- [Security IR Playbook](../security/policies/incident-response.md) — Security-specific breach response and evidence collection
- [Monitoring Dashboard](../operations/31_Observability.md) — RED metrics, alerting rules, dashboard definitions

---

*Postmortem created: YYYY-MM-DD | Review date: YYYY-MM-DD*
