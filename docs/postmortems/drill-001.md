# Incident Postmortem: AI Provider Failure During Peak Hours

## Document Control

| Field | Value |
|---|---|
| Document ID | PSM-001 |
| Version | 1.0.0 |
| Status | Draft |
| Classification | Internal — Incident Analysis |

## Summary

At 08:55 UTC on 2026-07-10, the local Ollama instance serving Mistral 7B became unresponsive due to OOM (out-of-memory) exhaustion, occurring 5 minutes before the scheduled daily briefing generation for all users. The circuit breaker opened after 5 consecutive failures, and the Claude Sonnet 4 fallback activated successfully. All daily briefings were generated with an average latency increase of 12 seconds. No users experienced missing briefings, and the incident was resolved after the Ollama process was restarted at 09:07 UTC.

## Severity

P2 — Partial degradation (AI generation slowed, all briefings delivered successfully)

## Timeline

| Time (UTC) | Event |
|---|---|
| 08:55 | Ollama process becomes unresponsive (OOM) |
| 08:56 | First briefing cron job fires, LLM call fails with connection timeout |
| 08:56 | Circuit breaker records failure #1 (state: CLOSED) |
| 08:56 | Retry #1 fails (2s backoff), Retry #2 fails (4s backoff), Retry #3 fails (8s backoff) |
| 08:57 | Circuit breaker transitions to OPEN after 5th failure (60s cooldown starts) |
| 08:57 | Fallback to Claude Sonnet 4 activated |
| 08:57 | First Claude fallback call succeeds — briefing generated with 14s latency |
| 08:57–09:02 | All ~85 scheduled briefings generated via Claude fallback |
| 09:02 | Circuit breaker cooldown expires (state transitions to HALF_OPEN) |
| 09:02 | HALF_OPEN probe call to Ollama fails immediately |
| 09:02 | Circuit breaker returns to OPEN (new 60s cooldown) |
| 09:03 | Monitoring check identifies Ollama process as unresponsive |
| 09:04 | On-call developer paged via Slack |
| 09:05 | Developer runs `ollama ps` — confirms process is hung |
| 09:06 | Developer runs `ollama serve` to restart — previous process still holding port |
| 09:07 | Developer kills hung process (`taskkill /F /IM ollama.exe`) |
| 09:07 | `ollama serve` starts successfully — service restored |
| 09:08 | Circuit breaker transitions to HALF_OPEN after cooldown |
| 09:08 | HALF_OPEN probe succeeds — circuit breaker returns to CLOSED |
| 09:10 | Developer verifies next LLM call succeeds via Ollama |
| 09:12 | Post-incident review initiated |

## Detection

The incident was detected via two independent sources:
1. **Slack alert** from scheduler error logging at 09:03 UTC (8 minutes after first failure)
2. **Circuit breaker state change** logged at 08:57 UTC (visible in backend logs)

Notable: No PagerDuty or automated phone alert was triggered. The Slack alert was the only real-time notification.

## Root Cause

The local Ollama process exhausted available system memory (OOM) due to accumulated memory fragmentation. Analysis revealed:

- The Ollama process had been running continuously for 14 days without restart
- Mistral 7B's context window had gradually accumulated cached sessions from repeated agent calls
- Available system RAM dropped from 4.2 GB to 0.3 GB over the 14-day period
- When the 8:55 AM briefing batch (the largest daily batch of LLM calls) started, Ollama could not allocate memory for new inference requests

The underlying issue is the absence of a memory cap or periodic restart policy for the local Ollama instance.

## Impact

| Metric | Value |
|---|---|
| Users affected | 0 (all briefings delivered) |
| Service downtime | 0 min (fallback handled transparently) |
| Latency degradation | +12 seconds average (2.1s → 14.3s per briefing) |
| Data loss | None |
| Extra AI cost | ~$1.28 (85 briefings × $0.015 via Claude fallback) |
| Briefings delivered late | 0 (cron job completed within 90s of schedule) |

## Action Items

| Action | Owner | Tracked In | Status |
|---|---|---|---|
| Add OOM monitoring for Ollama process (memory usage alert > 80%) | @ops | Issue #847 | Open |
| Implement weekly Ollama restart via scheduler cron job | @devops | Issue #848 | Open |
| Set Ollama memory limit via `OLLAMA_NUM_PARALLEL` and `OLLAMA_MAX_LOADED_MODELS` env vars | @devops | PR #312 | Open |
| Add PagerDuty/webhook alert on circuit breaker OPEN state | @backend | Issue #849 | Open |
| Extend circuit breaker cooldown from 60s to 180s | @ai-team | Issue #850 | Open |
| Add incident runbook for AI provider failures | @docs | PR #313 | Open |
| Add regression test for OOM recovery scenario | @qa | Issue #851 | Open |

## Lessons Learned

### What Went Well
- **Circuit breaker pattern worked correctly** — After 5 failures, the circuit opened and prevented further calls to the dead Ollama instance
- **Claude fallback activated transparently** — No user-facing impact; all 85 briefings were generated without errors
- **Retry with exponential backoff** prevented a thundering herd against the failing provider
- **System designed for graceful degradation** — The algorithmic fallback briefings we have as a backup were available, though Claude was used first
- **Logging captured the full chain of events** — Every retry, circuit transition, and fallback was recorded with structured JSON logs

### What Went Wrong
- **No alert on Ollama failure** — The first notification came 8 minutes after the incident via Slack, not immediately via PagerDuty or phone
- **Circuit breaker cooldown too short** — The 60s cooldown expired while Ollama was still down, causing a second OPEN transition. A longer cooldown would have reduced log noise and unnecessary HALF_OPEN probes
- **No memory monitoring for Ollama** — Process had been running for 14 days with no health checks or memory usage tracking
- **No automated restart policy** — A weekly or memory-threshold-based restart would have prevented the OOM condition entirely
- **Developer had to manually kill the process** — There was no graceful restart script or health check endpoint for Ollama

### What We'll Do Differently
1. **Add memory usage alerting** for the Ollama process with a threshold of 80% system RAM
2. **Implement weekly Ollama restart** as a cron job (Sunday 4 AM, lowest usage period)
3. **Set Ollama environment variables** to limit parallelism and max loaded models: `OLLAMA_NUM_PARALLEL=1` and `OLLAMA_MAX_LOADED_MODELS=1`
4. **Extend circuit breaker cooldown** from 60s to 180s to reduce probe frequency during extended outages
5. **Create a restart script** (`scripts/restart-ollama.sh`) that gracefully stops and restarts the Ollama process with health verification
6. **Add a health check endpoint** that tests AI provider connectivity and surfaces provider status in `/health/ready`

## Related Documents

- [Incident Response Playbook](../security/policies/incident-response.md)
- [LLM Client Implementation](../../packages/ai/client.py)
- [Circuit Breaker Configuration](../../packages/shared/utils/retry.py)
- [Scheduler Cron Jobs](../../services/scheduler/main.py)
- [Agent Architecture Reference](../ai/20_Agent.md)
- PR #312: Ollama environment variable limits
- PR #313: AI provider failure runbook
- Issue #847: OOM monitoring
- Issue #848: Weekly Ollama restart cron
- Issue #849: Circuit breaker alerting
- Issue #850: Extend cooldown
- Issue #851: OOM recovery regression test

---

*Postmortem created: 2026-07-10 | Review date: 2026-07-17*
