## Document Control

| Field | Value |
|---|---|
| Document ID | ENG-ADR08-001 |
| Version | 1.0.0 |
| Status | Accepted |
| Last Updated | 2026-07-11 |

# ADR-008: No Event Bus in Alpha

## Status
Accepted

## Date
2024-06-01

## Context
Various system events need handling: a task is completed (check habit streaks, update goal progress, log to history), a habit is missed (send encouragement, adjust streak counter), a briefing is generated (notify the user), a new idea is captured (trigger opportunity radar scan). The options were to deploy an event bus (RabbitMQ, Redis Pub/Sub, or Supabase Realtime channels) or to handle events through direct function calls and polling.

## Decision

```mermaid
graph TD
    subgraph CURRENT["Current Approach (Alpha) - No Event Bus"]
        API_HANDLER[Task Completed Handler]
        API_HANDLER -->|1. Sync call| HABIT[update_habit_streaks()]
        API_HANDLER -->|2. Sync call| GOAL[recalculate_goal_progress()]
        API_HANDLER -->|3. Sync call| LOG[log_event()]

        DB[(Supabase)]
        API_HANDLER -->|INSERT| DB
        DB -->|4. Realtime| FE[Frontend Live Update]

        CRON[APScheduler - 15 min] -->|5. Poll| DB
        CRON -->|6. Check conditions| ACT[Handle Missed Habits /<br/>Overdue Tasks]
    end

    subgraph FUTURE["Future State - Event Bus"]
        PRODUCER[Event Producers]
        BUS[Event Bus<br/>RabbitMQ / Supabase Channels]
        CONSUMER1[Habit Consumer]
        CONSUMER2[Goal Consumer]
        CONSUMER3[Log Consumer]
        PRODUCER -->|publish| BUS
        BUS -->|subscribe| CONSUMER1
        BUS -->|subscribe| CONSUMER2
        BUS -->|subscribe| CONSUMER3
    end

    style CURRENT fill:#0A0B0F,stroke:#00FFA3,color:#F1F5F9
    style FUTURE fill:#0A0B0F,stroke:#818CF8,color:#F1F5F9
```

For the alpha phase, events are handled through three mechanisms:
1. **Synchronous function calls** â€” completing a task in the API handler directly calls `update_habit_streaks()`, `recalculate_goal_progress()`, and `log_event()` in sequence
2. **Supabase Realtime** â€” Postgres changes (INSERT, UPDATE, DELETE) are subscribed to by the frontend for live UI updates
3. **Cron-based polling** â€” APScheduler jobs run every 15 minutes to check for conditions (missed habits, overdue tasks, stale opportunities)

No dedicated event bus or message queue is deployed.

## Consequences

### Positive
- Zero infrastructure to set up and maintain â€” no RabbitMQ cluster, no Redis instance, no Kafka broker
- Fewer failure points â€” no broker crash, no connection drops, no message replay logic
- Faster development velocity â€” calling `update_habit_streaks()` directly is faster than publishing an event and writing a consumer
- Easier debugging â€” the entire call stack is visible in a single trace, no chasing messages across consumers
- Lower memory footprint â€” no persistent TCP connections to a message broker

### Negative
- Tight coupling â€” the task completion endpoint directly imports and calls habit, goal, and logging functions; changing one may affect the others
- No retry logic â€” if `update_goal_progress()` throws a transient DB error, the entire task-completion request fails (no DLQ, no retry)
- Polling latency â€” 15-minute intervals mean missed habits are detected up to 15 minutes late, stale opportunities linger
- No event replay capability â€” if a bug causes events to be missed, there is no audit log of events to replay from

### Neutral
- The in-process function calls follow clean interface boundaries â€” each handler imports from `packages/ai/agents/` or `packages/database/schemas/`, not from `apps/api/`
- Adding an event bus later (Supabase Realtime channels as a lightweight bus, or RabbitMQ for production) is possible without changing event producers â€” only the dispatch mechanism changes
- The 15-minute polling interval is configurable per job and can be tightened to 1 minute if latency becomes an issue
