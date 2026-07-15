---
version: 2.0.0
status: active
description: Enterprise context assembly template for AI agent orchestration — token budgets, freshness rules, fallback strategies, assembly flow, and edge case handling for every Supabase context section
model: all
max_tokens: 8192
temperature: 0.0
tags: [context-assembly, template]
last_updated: 2026-06-11
approved_by: architecture-review
classification: internal
refresh_policy: per-request
assembly_time_budget_ms: 250
cache_ttl_seconds: 30
---

# Context Assembly Template v2.0.0

Defines how user context packets are assembled before injection into any agent prompt.

---

## 1. Context Packet Budget

Total budget: **7,800 tokens** (392 reserved for overhead). Hard cap: 8,192.

| # | Section                | Max Tokens |  %  | Prio | Order | Rationale                              |
|---|------------------------|------------|-----|------|-------|----------------------------------------|
| 1 | System Prompt          | 1,200      | 15% | Crit | 1     | Base persona, never truncated          |
| 2 | Guardrails             | 400        |  5% | Crit | 2     | Safety constraints, never truncated    |
| 3 | User Profile           | 350        |  5% | High | 3     | Identity, skills, time context         |
| 4 | Active Tasks           | 1,000      | 13% | High | 4     | Task context drives agent actions      |
| 5 | Active Goals           | 600        |  8% | High | 5     | Goal alignment for steering            |
| 6 | Course Status          | 400        |  5% | Med  | 6     | Academic context, omit if none         |
| 7 | Health & Sleep         | 300        |  4% | Med  | 7     | Wellness, 3-day avg if over budget     |
| 8 | Habit Streaks          | 300        |  4% | Med  | 8     | Consistency metrics, summarized        |
| 9 | Chat History           | 2,000      | 26% | High | 9     | Conversational continuity, oldest drop |
|10 | Agent Outputs          | 800        | 10% | Med  | 10    | Cross-agent awareness, max 5           |
|11 | Request Context        | 150        |  2% | High | 11    | Current query metadata                 |
|12 | Reserve / Padding      | 300        |  4% | -    | -     | Buffer for token expansion             |
|   | **Total**             | **7,800**  |100% |      |       |                                        |

---

## 2. Section Specifications

Each section defines: **Source** (Supabase query), **Max Tokens**, **Fallback** (if query fails), **Truncation** (if over budget).

### 2.1 System Prompt — Section 1
- **Source**: `prompts/system/aria_system.md` (loaded at start, cached, polled 30s)
- **Max**: 1,200 (hard, never truncated) | **Fallback**: Minimal prompt from `client.py` (log WARN)

### 2.2 Guardrails — Section 2
- **Source**: `prompts/system/guardrails.md` (cached, polled 30s)
- **Max**: 400 (hard, never truncated) | **Fallback**: Default safe-mode constant (log ALERT)

### 2.3 User Profile — Section 3
- **Source**: `SELECT id,name,skills,interests,timezone,preferences FROM users WHERE id=$1`
- **Fields**: `name`, `timezone`, `current_time`, `time_of_day`, `day_of_week`, `skills[]`, `interest[]`
- **Format**: Plain text
- **Max**: 350 | **Fallback**: user_id as name, empty arrays, UTC (log ERROR) | **Trunc**: Skills 15, Interests 10

### 2.4 Active Tasks — Section 4
- **Source**: `SELECT id,title,priority,due_date,status,goal_id FROM tasks WHERE user_id=$1 AND status IN ('pending','in_progress') ORDER BY priority DESC,due_date ASC LIMIT 25`
- **Format**: `| Title | P | Due | S | Goal |` markdown table
- **Max**: 1,000 | **Fallback**: "Unable to load tasks" (retry once 500ms) | **Trunc**: Drop P3 first, then oldest. Keep min 5 highest-priority.

### 2.5 Active Goals — Section 5
- **Source**: `SELECT id,title,progress_pct,target_date,intensity,category FROM goals WHERE user_id=$1 AND status='active' ORDER BY target_date ASC LIMIT 10`
- **Max**: 600 | **Fallback**: "No active goals set." | **Trunc**: Drop low-intensity; summarize to 1 line

### 2.6 Course Status — Section 6
- **Source**: `SELECT id,title,progress_pct,deadline,overdue FROM courses WHERE user_id=$1 AND status='enrolled' ORDER BY deadline ASC LIMIT 10`
- **Max**: 400 | **Fallback**: Omit section if no enrollments | **Trunc**: Omit 100% complete; if >5 show only <50% or overdue

### 2.7 Health & Sleep — Section 7
- **Source**: `SELECT date,score,duration_hours,quality FROM sleep_logs WHERE user_id=$1 ORDER BY date DESC LIMIT 7`
- **Fields**: `avg_score_3day`, `avg_duration_3day`, `last_night_score`, `trend`
- **Freshness**: Must be <24h old. Stale → omit with note.
- **Max**: 300 | **Fallback**: Omit if no data | **Trunc**: Aggregate to 7-day avg only

### 2.8 Habit Streaks — Section 8
- **Source**: `SELECT id,name,streak,consistency_pct,category FROM habits WHERE user_id=$1 AND active=true ORDER BY streak DESC LIMIT 15`
- **Max**: 300 | **Fallback**: Omit section | **Trunc**: Top 5 only, drop consistency column

### 2.9 Chat History — Section 9
- **Source**: `SELECT role,content,created_at FROM chat_history WHERE session_id=$1 ORDER BY created_at DESC LIMIT 20`
- **Fields**: Up to 20 exchanges (~250 tokens/pair), limited to 8 if over budget
- **Max**: 2,000 | **Fallback**: "No prior conversation." | **Trunc**: Drop oldest first. Summarize oldest 50% as "Earlier: {topic}"

### 2.10 Agent Outputs — Section 10
- **Source**: `SELECT agent_name,output_type,summary,generated_at FROM agent_outputs WHERE user_id=$1 AND generated_at > NOW() - INTERVAL '1 day' ORDER BY generated_at DESC LIMIT 10`
- **Max**: 800 | **Fallback**: Omit if none | **Trunc**: Deduplicate, max 5, summaries to 100 chars

### 2.11 Request Context — Section 11
- **Source**: API call parameters directly. Fields: `user_query`, `agent_name`, `request_id`, `session_id`, `client`
- **Max**: 150 | **Fallback**: "No query — trigger: {event_name}"

---

## 3. Freshness Rules

| Data              | Max Age | Refresh      | Stale Behavior                  |
|-------------------|---------|--------------|----------------------------------|
| User Profile      | 0s      | Per-request  | N/A (always fresh)               |
| Active Tasks      | 0s      | Per-request  | N/A                              |
| Active Goals      | 0s      | Per-request  | N/A                              |
| Course Status     | 0s      | Per-request  | N/A                              |
| Sleep Logs        | 24h     | Per-request  | Omit section                     |
| Habit Streaks     | 1h      | Per-request  | Omit section                     |
| Chat History      | 0s      | Per-request  | N/A                              |
| Agent Outputs     | 24h     | Per-request  | Omit section                     |
| System Prompt     | File change | Poll 30s | Use last known good (WARN)       |
| Guardrails        | File change | Poll 30s | Use last known good (ALERT)      |

---

## 4. Token Optimization

### Per-Section Truncation Order
1. Remove low-priority fields (`created_at`, `goal_id`)
2. Truncate text (titles to 120 chars, keep only summaries)
3. Remove footer rows from tables
4. Aggregate (per-item → summary stats)
5. Hard-cut at max with `[...truncated]`

### Cross-Section Emergency (total > 7800)
Drop in order: Agent Outputs → Chat History (to 4) → Course Status → Health & Sleep. Never drop: System, Guardrails, Profile, Request. Log all to monitoring.

### Compression
- Relative timestamps ("2d ago" not ISO)
- Single-char column headers (P, D, S)
- Remove whitespace-only table lines
- Merge empty sections → "No additional context"

---

## 5. Assembly Process Flow

```
ASSEMBLE(user_id, session_id, agent, query):
  1. LOAD system_prompt + guardrails from cache
  2. PARALLEL FETCH (8 queries, 200ms each): users, tasks, goals, courses, sleep, habits, chat, agents
  3. FOR section IN order (1-11):
     IF data exists AND fresh: FORMAT section
     ELSE: fallback; log warning
     IF tokens > max: truncate
     APPEND to packet
  4. IF total > 7800: emergency truncate lowest-priority non-critical
  5. RETURN packet, token_count, elapsed_ms
```

```python
async def assemble(user_id, session_id, agent, query=None):
    packet = ContextPacket()
    packet.add(load_system()), packet.add(load_guardrails())
    results = await parallel_fetch_all(user_id, session_id, timeout=0.2)
    for key, spec in ASSEMBLY_ORDER:
        data = results[key]
        section = spec.format(data) if data else spec.fallback()
        if estimate_tokens(section) > spec.max_tokens:
            section = spec.truncate(section)
        packet.add(section)
    return packet
```

---

## 6. Edge Cases

| Case               | Behavior                                                      |
|--------------------|---------------------------------------------------------------|
| Empty DB / New user| ~2,200 tokens: system + guardrails + minimal profile + "No data" placeholders. Agent detects "new user". |
| Offline mode       | System from local cache. Queries timeout gracefully. Uses last-known-good from `~/.second_brain/cache/context_cache.json`. Header: `mode: offline`. Cache refresh 30min. |
| Query timeout      | Single query >200ms abandoned. Section uses fallback. Header includes `warnings: [query timed out]`. |
| Token emergency    | Drop non-critical until total <= 7800. Log all drops. |

---

## 7. Performance & Caching

| Phase              | Max Time | Notes                   |
|--------------------|----------|-------------------------|
| DB queries (total) | 200ms    | Parallel, ~25ms each    |
| Section formatting | 30ms     | String ops              |
| Token estimation   | 10ms     | Regex counters          |
| **Total**          |**250ms** | P99 target              |

| Cache Layer        | Type       | TTL  | Invalidation            |
|--------------------|------------|------|-------------------------|
| System prompts     | In-memory  | 30s  | File change detection   |
| Sleep/Habits       | Short-lived| 60s  | Write-through on insert |
| Agent outputs      | Short-lived| 30s  | Write-through           |
| Tasks/Goals/Profile| No cache   | -    | Per-request             |

### Monitoring Metrics
- `context.assembly.time_ms` — alert if P99 > 300ms
- `context.assembly.token_total` — alert if > 7,800
- `context.section.{name}.fallback` — alert if rate > 5%
- `context.assembly.truncation_emergency` — page on-call

---

## 8. Version History

| Version | Date       | Author             | Changes                                      |
|---------|------------|--------------------|----------------------------------------------|
| 2.0.0   | 2026-06-11 | Architecture Team  | Budget mgmt, freshness rules, fallback specs, edge cases, performance SLA |
| 1.0.0   | 2026-01-15 | Initial            | Basic context structure                      |
