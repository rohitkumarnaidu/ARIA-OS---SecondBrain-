# Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                       │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │Dashboard│  │ Tasks   │  │ Courses │  │  Chat   │            │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘            │
│       │            │            │            │                  │
│  ┌────┴────────────┴────────────┴────────────┴────┐            │
│  │              State (Zustand + React Query)    │            │
│  └─────────────────────┬────────────────────────┘            │
└────────────────────────┼───────────────────────────────────────┘
                         │ API Calls
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    API Layer                             │   │
│  │   /tasks, /courses, /goals, /projects, /chat, etc.      │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                            │                                    │
│  ┌─────────────────────────┴───────────────────────────────┐   │
│  │                 Service Layer                            │   │
│  │   TaskService, CourseService, GoalService, etc.         │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                            │                                    │
│  ┌─────────────────────────┴───────────────────────────────┐   │
│  │                 Database Layer (Supabase)                │   │
│  │   PostgreSQL + RLS + Realtime + Edge Functions          │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI Layer (Dual Mode)                        │
│                                                                 │
│   ┌──────────────────┐        ┌──────────────────┐            │
│   │    Ollama        │        │  Claude API      │            │
│   │  (Local LLM)     │───────▶│  (Cloud Fallback)│            │
│   │  Llama 3.1      │        │                  │            │
│   └──────────────────┘        └──────────────────┘            │
│                                                                 │
│   Used for: Chat, Summaries, Weekly Reviews, Opportunity      │
│   parsing, Roadmap generation                                   │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                Scheduled Agents (Edge Functions)              │
│                                                                 │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│   │ Daily        │  │ Missed Task  │  │ Opportunity  │        │
│   │ Briefing    │  │ Checker      │  │ Radar        │        │
│   │ 7 AM        │  │ Every 15 min │  │ 6 AM         │        │
│   └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│   │ Roadmap      │  │ Weekly       │  │ Sleep        │        │
│   │ Update      │  │ Review       │  │ Reminder     │        │
│   │ Sunday 9 AM │  │ Sunday 8 PM  │  │ 9:30 PM      │        │
│   └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
│   ┌──────────────┐  ┌──────────────┐                           │
│   │ Habit Miss   │  │ Course Nudge │                           │
│   │ Midnight     │  │ 6 PM         │                           │
│   └──────────────┘  └──────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
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

```
1. User fills form in frontend
2. POST /api/tasks
3. TaskService validates + creates in Supabase
4. Realtime pushes to all connected clients
5. Task appears in all lists instantly
6. If due_date <= 2h away → push notification
```

### User Chats with ARIA

```
1. User types message in chat
2. POST /api/chat
3. Context Builder serializes: profile, tasks, goals, courses, sleep, memory
4. Routes to Ollama (primary) or Claude API (fallback)
5. AI returns response + optional action JSON blocks
6. Action executor processes: add_task, update_course, save_idea, etc.
7. Memory writer extracts facts/preferences from conversation
8. Response sent to user, message saved to chat_messages
```

### Morning Briefing Generation

```
1. pg_cron triggers daily-briefing Edge Function at 01:30 UTC (7 AM IST)
2. Loads: tasks due today, overdue tasks, active courses, goals, sleep, opportunities
3. Calls Claude API with Daily Briefing system prompt
4. Generates 6-section briefing: Focus, Opportunities, Course Target, Roadmap, Top Pick, Skip
5. Saves to daily_briefings table
6. Sends push notification + in-app banner
7. (Optional) Sends email via Resend
```

### Opportunity Radar Scan

```
1. pg_cron triggers opp-radar Edge Function at 00:30 UTC (6 AM IST)
2. Fetches all user profiles with skills and preferences
3. Calls Query Generator (Claude) → produces 8 search queries
4. For each query: calls Brave Search API
5. For each result: calls Opportunity Parser (Claude) → extracts structured data
6. Filters: only saves if match_score >= 50
7. Inserts to opportunities table
8. If deadline < 48h away → immediate push notification
```

### Missed Task Auto-Reschedule

```
1. pg_cron triggers task-checker every 15 minutes
2. Finds: due_date < now() AND status NOT IN ('done','archived')
3. For each missed task:
   a. Increment missed_count
   b. Set status='missed', rescheduled_from=original_due_date
   c. Set scheduled_start = now() + 2 hours
   d. Send push notification
   e. If missed_count >= 2 → send email via Resend
   f. If missed_count >= 3 AND priority='high' → send SMS via Twilio
```

---

## Deployment Architecture

```
                          ┌─────────────────┐
                          │   GitHub Repo   │
                          │  (Source of     │
                          │   Truth)        │
                          └────────┬────────┘
                                   │ git push
                                   ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User Browser  │────▶│     Vercel      │◀────│   Supabase      │
│   (PWA + HTTPS) │◀────│  (Next.js App)  │────▶│  (DB + Auth +   │
│   Desktop/Mobile│     │  CDN + SSR +    │     │   Edge Fn)      │
└─────────────────┘     │  Serverless     │     └────────┬────────┘
                        └─────────────────┘              │
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │    Ollama       │     │  External APIs  │
                        │  (Local LLM)    │     │  Brave Search   │
                        │  Dev machine    │     │  Google APIs    │
                        └─────────────────┘     │  Resend         │
                                                 │  Twilio         │
                                                 └─────────────────┘
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

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Second Brain OS                             │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     Presentation Layer                       │   │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌─────────┐ │   │
│  │  │Pages │ │Compts│ │Layout│ │Nav   │ │Modals│ │Providers│ │   │
│  │  │15    │ │Cards │ │Shell │ │Bar   │ │      │ │Theme    │ │   │
│  │  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └─────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  ┌──────────────────────────┴──────────────────────────────────┐   │
│  │                     State Layer                              │   │
│  │  ┌───────────────────────────────────────────────────────┐  │   │
│  │  │   Zustand Stores (global UI state)                    │  │   │
│  │  │   React Query Cache (server state)                    │  │   │
│  │  │   IndexedDB (offline persistence)                     │  │   │
│  │  └───────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  ┌──────────────────────────┴──────────────────────────────────┐   │
│  │                     API Layer                                │   │
│  │  ┌───────────┐ ┌──────────┐ ┌─────────┐ ┌────────────────┐ │   │
│  │  │REST Routes│ │WebSocket │ │Auth     │ │Realtime Subs  │ │   │
│  │  │/api/*     │ │/ws/aria  │ │Middleware│ │supabase-realtime│ │   │
│  │  └───────────┘ └──────────┘ └─────────┘ └────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  ┌──────────────────────────┴──────────────────────────────────┐   │
│  │                   Service Layer                              │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │   │
│  │  │TaskSvc   │ │CourseSvc │ │GoalSvc   │ │MemorySvc │      │   │
│  │  │ProjectSvc│ │IdeaSvc   │ │SleepSvc  │ │ChatSvc   │      │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  ┌──────────────────────────┴──────────────────────────────────┐   │
│  │                   AI Layer                                   │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐│   │
│  │  │Context       │ │Ollama Client │ │Claude Client         ││   │
│  │  │Builder       │ │(primary)     │ │(fallback)            ││   │
│  │  └──────────────┘ └──────────────┘ └──────────────────────┘│   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐│   │
│  │  │Action        │ │Memory Writer │ │LangChain Orchestrator││   │
│  │  │Executor      │ │              │ │(8 agents)            ││   │
│  │  └──────────────┘ └──────────────┘ └──────────────────────┘│   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  ┌──────────────────────────┴──────────────────────────────────┐   │
│  │                   Data Layer                                 │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐│   │
│  │  │Supabase DB   │ │Supabase Auth │ │Edge Functions (8)    ││   │
│  │  │21 tables, RLS│ │Google OAuth  │ │Cron-based agents     ││   │
│  │  │PostgreSQL    │ │JWT sessions  │ │Deno runtime          ││   │
│  │  └──────────────┘ └──────────────┘ └──────────────────────┘│   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```
