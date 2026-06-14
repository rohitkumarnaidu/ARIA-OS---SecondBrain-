# ADR-008: No Event Bus in Alpha

## Status
Accepted

## Date
2024-06-01

## Context
Various system events need handling: a task is completed (check habit streaks, update goal progress, log to history), a habit is missed (send encouragement, adjust streak counter), a briefing is generated (notify the user), a new idea is captured (trigger opportunity radar scan). The options were to deploy an event bus (RabbitMQ, Redis Pub/Sub, or Supabase Realtime channels) or to handle events through direct function calls and polling.

## Decision
For the alpha phase, events are handled through three mechanisms:
1. **Synchronous function calls** — completing a task in the API handler directly calls `update_habit_streaks()`, `recalculate_goal_progress()`, and `log_event()` in sequence
2. **Supabase Realtime** — Postgres changes (INSERT, UPDATE, DELETE) are subscribed to by the frontend for live UI updates
3. **Cron-based polling** — APScheduler jobs run every 15 minutes to check for conditions (missed habits, overdue tasks, stale opportunities)

No dedicated event bus or message queue is deployed.

## Consequences

### Positive
- Zero infrastructure to set up and maintain — no RabbitMQ cluster, no Redis instance, no Kafka broker
- Fewer failure points — no broker crash, no connection drops, no message replay logic
- Faster development velocity — calling `update_habit_streaks()` directly is faster than publishing an event and writing a consumer
- Easier debugging — the entire call stack is visible in a single trace, no chasing messages across consumers
- Lower memory footprint — no persistent TCP connections to a message broker

### Negative
- Tight coupling — the task completion endpoint directly imports and calls habit, goal, and logging functions; changing one may affect the others
- No retry logic — if `update_goal_progress()` throws a transient DB error, the entire task-completion request fails (no DLQ, no retry)
- Polling latency — 15-minute intervals mean missed habits are detected up to 15 minutes late, stale opportunities linger
- No event replay capability — if a bug causes events to be missed, there is no audit log of events to replay from

### Neutral
- The in-process function calls follow clean interface boundaries — each handler imports from `packages/ai/agents/` or `packages/database/schemas/`, not from `apps/api/`
- Adding an event bus later (Supabase Realtime channels as a lightweight bus, or RabbitMQ for production) is possible without changing event producers — only the dispatch mechanism changes
- The 15-minute polling interval is configurable per job and can be tightened to 1 minute if latency becomes an issue
