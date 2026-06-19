# ADR-002: Supabase over Custom Backend DB

## Status
Accepted

## Date
2024-06-01

## Context
The project requires a relational database (PostgreSQL) for 12+ tables (tasks, courses, goals, ideas, projects, resources, opportunities, income, habits, sleep_logs, time_entries, users), user authentication, and real-time subscriptions for live UI updates. Options considered: Supabase (managed PostgreSQL + Auth + Realtime), Firebase (NoSQL + Auth), and a custom PostgreSQL instance with a separate auth solution.

## Decision

```mermaid
graph LR
    subgraph SUPABASE["Supabase (Chosen)"]
        DB[(PostgreSQL<br/>21 Tables + RLS)]
        AUTH[Supabase Auth<br/>Google OAuth + JWT]
        RT[Supabase Realtime<br/>WebSocket Subscriptions]
        EF[Edge Functions<br/>8 Cron Agents]
    end

    subgraph CUSTOM["Custom Stack (Rejected)"]
        P[(PostgreSQL)]
        A[Auth0 / Firebase Auth]
        WS[Custom WebSocket Server]
        CR[OS-level Cron]
    end

    FE[Frontend - Next.js] -->|@supabase/supabase-js| SUPABASE
    BE[Backend - FastAPI] -->|supabase-py| SUPABASE

    style SUPABASE fill:#0A0B0F,stroke:#00FFA3,color:#F1F5F9
    style CUSTOM fill:#0A0B0F,stroke:#EF4444,color:#F1F5F9
```

Use Supabase as the sole backend-as-a-service, providing managed PostgreSQL for persistence, built-in authentication (email/password + OAuth), and real-time subscriptions over WebSockets. The `@supabase/supabase-js` client is used on the frontend and the `supabase-py` library on the backend. All queries filter by `user_id` with Row-Level Security enabled.

## Consequences

### Positive
- Single service for DB, auth, and realtime — no stitching together Postgres + Auth0 + WebSocket server
- Generous free tier (500MB database, 50,000 monthly active users, 2GB bandwidth) covers alpha and beta
- RLS policies enforce data isolation at the database level — every query is scoped by `user_id` regardless of client
- Real-time subscriptions enable live UI updates (e.g., task completed → habit streak updates immediately)
- Built-in dashboard (Supabase Studio) for ad-hoc queries and table browsing

### Negative
- Vendor lock-in — migrating off Supabase requires reimplementing auth, RLS policies, and real-time channels
- No offline-local database — the development environment always requires internet connectivity to Supabase
- Free tier limits (500MB DB, 5GB bandwidth) will eventually require a paid plan
- Supabase Realtime has a 200-concurrent-connection limit on free tier

### Neutral
- Local development uses the same Supabase project (not a local Supabase instance), which simplifies setup but creates coupling to the live service
- Supabase's Postgres is standard PostgreSQL — raw `psql` access is available if needed
