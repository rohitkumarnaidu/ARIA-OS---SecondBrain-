# Architecture

## System Overview

```mermaid
graph TD
    subgraph Frontend["Frontend (Next.js)"]
        direction LR
        D1[Dashboard] --> State[Zustand + React Query]
        T1[Tasks] --> State
        C1[Courses] --> State
        CH[Chat] --> State
    end

    State -->|API Calls| API

    subgraph Backend["Backend (FastAPI)"]
        API[API Layer<br/>/tasks, /courses, /goals, /chat]
        API --> SVC[Service Layer<br/>TaskService, CourseService, GoalService]
        SVC --> DB[Database Layer<br/>Supabase: PostgreSQL + RLS + Realtime]
    end

    DB --> AI

    subgraph AI["AI Layer (Dual Mode)"]
        O[Ollama<br/>(Local LLM - Llama 3.1)] -->|Fallback| C[Claude API<br/>(Cloud)]
    end

    AI --> SA

    subgraph SA["Scheduled Agents (Edge Functions)"]
        direction LR
        SB[Daily Briefing<br/>7 AM]
        MT[Missed Task Checker<br/>Every 15 min]
        OR[Opportunity Radar<br/>6 AM]
        RU[Roadmap Update<br/>Sunday 9 AM]
        WR[Weekly Review<br/>Sunday 8 PM]
        SR[Sleep Reminder<br/>9:30 PM]
        HM[Habit Miss Checker<br/>Midnight]
        CN[Course Nudge<br/>6 PM]
    end

    style Frontend fill:#1a1a2e,stroke:#6366F1,color:#F1F5F9
    style Backend fill:#1a1a2e,stroke:#00FFA3,color:#F1F5F9
    style AI fill:#1a1a2e,stroke:#818CF8,color:#F1F5F9
    style SA fill:#1a1a2e,stroke:#F59E0B,color:#F1F5F9
```

---

## Component Responsibilities

### Frontend (Next.js)

**Pages/Routes:**
- `/` — Dashboard with morning briefing and productivity score
- `/tasks` — Task list, kanban, and time tracker
- `/courses` — Course tracker with progress and deadlines
- `/youtube` — YouTube knowledge vault
- `/resources` — Resource library with search
- `/ideas` — Idea vault with AI market check
- `/goals` — Roadmap builder (React Flow canvas)
- `/opportunities` — Opportunity radar results
- `/income` — Income tracker and hourly rate analysis
- `/projects` — Project tracker with phases
- `/academics` — Academic planner and CGPA calculator
- `/habits` — Habit engine with streaks
- `/sleep` — Sleep monitor with score
- `/time` — Time tracker with deep work detection
- `/chat` — ARIA chat panel

**State Management:**
- Zustand for global UI state (sidebar, modals, theme)
- React Query (TanStack Query) for server state
- localStorage/IndexedDB persistence for offline

**Key Libraries:**
- `framer-motion` — page transitions, staggered reveals
- `reactflow` — roadmap drag-and-drop canvas
- `recharts` — analytics charts and heatmaps
- `@supabase/auth-helpers-nextjs` — auth integration
- `zustand` — lightweight state management

### Backend (FastAPI)

**API Routes:**
- RESTful CRUD endpoints for all 15 modules
- WebSocket endpoint for real-time ARIA chat
- Server-side AI prompt construction

**Services:**
- Business logic per module (TaskService, CourseService, GoalService)
- AI context builder (serializes user profile, tasks, goals, courses)
- Action executor (parses AI response for JSON action blocks)

### Database (Supabase)

**Tables:** 21 tables as documented in Database.md

**Features Used:**
- PostgreSQL for structured storage
- RLS for row-level security on every table
- Realtime subscriptions for live UI updates
- Edge Functions for 8 cron-based agent schedules
- pg_cron for database-level cron scheduling

### AI Layer

**Ollama (Primary — Rs. 0):**
- Runs locally on developer machine
- Used for: ARIA chat responses, video summaries, resource tagging, habit reports
- Model: `llama3.1` (8B parameters)

**Claude API (Fallback — $5 credits):**
- Used for: Daily Briefing, Weekly Review, Opportunity parsing, Roadmap analysis
- Model: `claude-sonnet-4-20250514`
- Called only for complex reasoning tasks that exceed local LLM capability

### Scheduled Agents (8 total)

| Agent | Schedule | Function |
|-------|----------|----------|
| Daily Briefing | 7 AM daily | Generates morning intelligence report |
| Missed Task Checker | Every 15 min | Detects overdue tasks, auto-reschedules, escalates |
| Opportunity Radar | 6 AM daily | Scans 8 opportunity sources via Brave Search |
| Roadmap Update | Sunday 9 AM | Checks roadmap node validity against current data |
| Weekly Review | Sunday 8 PM | Compiles week data, generates narrative review |
| Bedtime Reminder | 9:30 PM daily | Wind-down nudge with tomorrow's first task |
| Habit Miss Checker | Midnight daily | Detects 2+ day habit misses, resets streaks |
| Course Progress Nudge | 6 PM daily | Checks daily study targets, alerts if behind |

---

## Data Flow

### User Creates Task

```mermaid
sequenceDiagram
    actor U as User
    participant FE as Frontend
    participant API as FastAPI
    participant SVC as TaskService
    participant DB as Supabase
    participant RT as Realtime

    U->>FE: Fill task form
    FE->>API: POST /api/tasks
    API->>SVC: Validate + Create
    SVC->>DB: INSERT tasks
    DB-->>RT: Broadcast change
    RT-->>FE: Live update
    FE-->>U: Task appears in lists
    alt due_date <= 2h
        DB-->>U: Push notification
    end
```

### User Chats with ARIA

```mermaid
sequenceDiagram
    actor U as User
    participant FE as Frontend
    participant API as Next.js API Route
    participant CB as Context Builder
    participant OLL as Ollama (Primary)
    participant CLA as Claude API (Fallback)
    participant AE as Action Executor
    participant MW as Memory Writer
    participant DB as Supabase

    U->>FE: Type message in chat
    FE->>API: POST /api/chat {message}
    API->>CB: Serialize user context
    CB->>DB: Fetch profile, tasks, goals, courses, sleep, memory
    DB-->>CB: User data
    CB-->>API: Context assembled

    alt Ollama available
        API->>OLL: Generate response
        OLL-->>API: Response + action JSON
    else Fallback
        API->>CLA: Generate response
        CLA-->>API: Response + action JSON
    end

    API->>AE: Parse action blocks
    AE->>DB: add_task / update_course / save_idea
    API->>MW: Extract facts & preferences
    MW->>DB: Upsert to aria_memory
    API->>DB: Save to chat_messages
    API-->>FE: {response, action_taken}
    FE-->>U: Display response
```

### Morning Briefing Generation

```mermaid
sequenceDiagram
    participant PG as pg_cron
    participant EF as Edge Function
    participant DB as Supabase
    participant CLA as Claude API
    participant NOT as Notification System
    participant RES as Resend (Optional)

    PG->>EF: Trigger 01:30 UTC (7 AM IST)
    EF->>DB: Load tasks, courses, goals, sleep, opportunities
    DB-->>EF: User data
    EF->>CLA: Daily Briefing system prompt + context
    CLA-->>EF: 6-section briefing JSON
    EF->>DB: Save to daily_briefings
    EF->>NOT: Send push + in-app banner
    alt Email enabled
        EF->>RES: Send email digest
    end
```

### Opportunity Radar Scan

```mermaid
sequenceDiagram
    participant PG as pg_cron
    participant EF as Edge Function
    participant DB as Supabase
    participant CLA as Claude API
    participant BRAVE as Brave Search
    participant NOT as Push Notification

    PG->>EF: Trigger 00:30 UTC (6 AM IST)
    EF->>DB: Fetch user profiles + skills + preferences
    DB-->>EF: User profiles
    EF->>CLA: Generate 8 search queries
    CLA-->>EF: Query list

    loop For each query
        EF->>BRAVE: Execute search
        BRAVE-->>EF: Search results
        EF->>CLA: Parse opportunity data
        CLA-->>EF: Structured opportunity
        alt match_score >= 50
            EF->>DB: INSERT opportunity
            alt deadline < 48h
                EF->>NOT: Immediate push
            end
        end
    end
```

### Missed Task Auto-Reschedule

```mermaid
flowchart TD
    PG[pg_cron triggers every 15 min] --> CHECK{Find tasks where<br/>due_date < now()<br/>AND status NOT IN<br/>done, archived}

    CHECK -->|Missed task found| PROC[For each missed task]
    PROC --> INC[Increment missed_count]
    INC --> STATUS[Set status = missed<br/>Set rescheduled_from = original_due_date]
    STATUS --> RESCHED[Set scheduled_start = now + 2h]
    RESCHED --> NOTIFY[Send Push Notification]

    NOTIFY --> LEVEL2{missed_count >= 2?}
    LEVEL2 -->|Yes| EMAIL[Send Email via Resend]
    LEVEL2 -->|No| DONE

    EMAIL --> LEVEL3{missed_count >= 3<br/>AND priority = high?}
    LEVEL3 -->|Yes| SMS[Send SMS via Twilio]
    LEVEL3 -->|No| DONE

    DONE([End])
```

---

## Deployment Architecture

```mermaid
graph LR
    GH[GitHub Repo<br/>Source of Truth] -->|git push| V[Vercel<br/>Next.js App<br/>CDN + SSR + Serverless]

    UB[User Browser<br/>PWA + HTTPS<br/>Desktop / Mobile] <--> V
    V <--> S[Supabase<br/>DB + Auth + Edge Fn]

    V -->|AI Requests| O[Ollama<br/>Local LLM<br/>Dev Machine]
    V --> EA[External APIs<br/>Brave Search<br/>Google APIs<br/>Resend<br/>Twilio]

    S --> EA

    style GH fill:#13151A,stroke:#6366F1,color:#F1F5F9
    style UB fill:#13151A,stroke:#00FFA3,color:#F1F5F9
    style V fill:#13151A,stroke:#818CF8,color:#F1F5F9
    style S fill:#13151A,stroke:#F59E0B,color:#F1F5F9
    style O fill:#13151A,stroke:#EF4444,color:#F1F5F9
    style EA fill:#13151A,stroke:#94A3B8,color:#F1F5F9
```

**Hosting Strategy:**
- **Vercel**: Frontend Next.js app (static + serverless functions)
- **Supabase**: Managed PostgreSQL database, authentication, realtime, edge functions
- **Ollama**: Runs locally on developer's machine (no cloud hosting needed)
- **External APIs**: Called from server-side/edge functions only (API keys never in client)

---

## Offline Strategy

Second Brain OS is designed as an offline-first PWA. The system works without internet connectivity and syncs automatically when reconnected.

### Layer 1 — App Shell (Service Worker)

```
Offline → Workbox service worker serves cached app shell
Online  → Network-first strategy for API calls
```

- Workbox `StaleWhileRevalidate` for page routes
- Workbox `NetworkFirst` for `/api/*` requests
- Workbox `CacheFirst` for static assets (`_next/static`)

### Layer 2 — Local Data Store (IndexedDB)

```
Tables cached locally:
- tasks (recent 100 + today's)
- courses (active only)
- goals (active only)
- daily_briefings (current week)
- roadmaps (active only)
- habits (active only)
```

- Uses `idb` library for IndexedDB access
- Stores critical data needed for dashboard + task management
- Syncs on reconnect with background sync API

### Layer 3 — Background Sync

```
Offline action → Queued in IndexedDB → Online → Replay in order
```

- Queues: task creation, completion, course progress updates
- On reconnect: replays queued actions against Supabase
- Conflict resolution: last-write-wins with server timestamp

### Layer 4 — Optimistic Updates

```
UI update → Immediate (no wait for server)
Server response → Confirm or revert
```

- Tasks marked complete appear done immediately
- If server rejects, UI reverts with toast notification
- Used for: task status, habit completion, timer start/stop

---

## Security Architecture

### Authentication

```
Layer 1: Supabase Auth (Google OAuth primary)
Layer 2: Magic link (fallback)
Layer 3: JWT session (auto-refresh, 7-day expiry)
Layer 4: Force logout all devices (Settings page)
```

### Authorization

```
Every database query filtered by: auth.uid() = user_id
Enforced at 3 levels:
  1. RLS on all 21 tables (database level)
  2. API middleware validates JWT (application level)
  3. Service layer re-checks user_id (business logic level)
```

### Data Protection

| Area | Implementation |
|------|---------------|
| Data in transit | TLS 1.3 for all HTTP traffic |
| Data at rest | AES-256 encryption (Supabase managed) |
| API keys | Vercel env variables only, never in client code |
| AI queries | Claude calls go through server routes only |
| Browser extension | Only sends explicitly-saved URLs |
| File uploads | Type/size validation, max 10 MB |
| Rate limiting | AI: 10/min, Auth: 5 attempts then lockout, Uploads: 10/hour |

### Row Level Security

Every table has the standard policy:

```sql
ALTER TABLE table_name ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_own_data" ON table_name
  FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);
```

### API Key Safety Rules

1. `SUPABASE_SERVICE_ROLE_KEY` never in client code (server-only routes)
2. `ANTHROPIC_API_KEY` never in client code (Next.js API routes only)
3. `BRAVE_API_KEY` never in client code (Edge Functions only)
4. `.env.local` never committed to GitHub (in `.gitignore` from Day 1)
5. `NEXT_PUBLIC_*` variables are the only ones safe for client side

---

## Component Diagram

```mermaid
graph TD
    subgraph SBO["Second Brain OS"]
        subgraph PL["Presentation Layer"]
            P[Pages - 15 Modules]
            C[Components - Cards]
            L[Layout - Shell]
            N[NavBar]
            M[Modals]
            PR[Providers - Theme]
        end

        PL --> SL

        subgraph SL["State Layer"]
            Z[Zustand Stores<br/>Global UI State]
            RQ[React Query Cache<br/>Server State]
            IDB[IndexedDB<br/>Offline Persistence]
        end

        SL --> AL

        subgraph AL["API Layer"]
            REST[REST Routes - /api/*]
            WS[WebSocket - /ws/aria]
            AM[Auth Middleware]
            RS[Realtime Subs<br/>supabase-realtime]
        end

        AL --> SVL

        subgraph SVL["Service Layer"]
            TSK[TaskSvc]
            CRS[CourseSvc]
            GLS[GoalSvc]
            MMS[MemorySvc]
            PJS[ProjectSvc]
            IDS[IdeaSvc]
            SPS[SleepSvc]
            CTS[ChatSvc]
        end

        SVL --> AIL

        subgraph AIL["AI Layer"]
            CB[Context Builder]
            OC[Ollama Client<br/>Primary]
            CC[Claude Client<br/>Fallback]
            AE[Action Executor]
            MW[Memory Writer]
            LO[LangChain Orchestrator<br/>8 Agents]
        end

        AIL --> DL

        subgraph DL["Data Layer"]
            SDB[Supabase DB<br/>21 Tables - RLS - PostgreSQL]
            SA[Supabase Auth<br/>Google OAuth - JWT]
            EF[Edge Functions<br/>8 Cron Agents - Deno]
        end
    end

    style SBO fill:#0A0B0F,stroke:#334155,color:#F1F5F9
    style PL fill:#13151A,stroke:#6366F1,color:#F1F5F9
    style SL fill:#13151A,stroke:#818CF8,color:#F1F5F9
    style AL fill:#13151A,stroke:#00FFA3,color:#F1F5F9
    style SVL fill:#13151A,stroke:#F59E0B,color:#F1F5F9
    style AIL fill:#13151A,stroke:#EF4444,color:#F1F5F9
    style DL fill:#13151A,stroke:#94A3B8,color:#F1F5F9
```
