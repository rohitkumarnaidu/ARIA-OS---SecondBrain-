# System Architecture (10,000ft View)

## Architectural Philosophy

Second Brain OS is built on 7 core principles that drive every architectural decision:

1. **Offline-first** — Works without internet via PWA + IndexedDB + background sync
2. **Mobile-first** — 44px minimum touch targets, bottom nav, swipe gestures
3. **Agent-orchestrated** — 8 AI agents run automatically on schedules
4. **Privacy-first** — Data stays in user's Supabase instance, AI runs locally (Ollama)
5. **Modular** — All 15 features independently toggleable
6. **Real-time** — Supabase Realtime pushes live updates; no page refresh needed
7. **Predictive** — System learns patterns and anticipates needs after 3 months

---

## Monorepo Layout

```
ARIA OS - SecondBrain/
│
├── apps/                              # Deployable applications
│   ├── web/                           # Next.js 14 frontend
│   │   ├── app/                       # App Router pages (15 modules)
│   │   │   ├── (auth)/               # Login, auth callback
│   │   │   ├── dashboard/            # Morning briefing, productivity score
│   │   │   ├── tasks/                # Task manager with kanban
│   │   │   ├── courses/              # Course tracker
│   │   │   ├── youtube/              # YouTube knowledge vault
│   │   │   ├── resources/            # Resource library
│   │   │   ├── ideas/                # Idea vault
│   │   │   ├── goals/                # Roadmap builder (React Flow)
│   │   │   ├── opportunities/        # Opportunity radar
│   │   │   ├── income/               # Income tracker
│   │   │   ├── projects/             # Project tracker
│   │   │   ├── academics/            # Academic planner
│   │   │   ├── habits/               # Habit engine
│   │   │   ├── sleep/                # Sleep monitor
│   │   │   ├── time/                 # Time tracker
│   │   │   └── chat/                 # ARIA chat panel
│   │   ├── components/               # Shared UI components
│   │   ├── lib/                      # Zustand stores, utilities
│   │   ├── hooks/                    # Custom React hooks
│   │   └── public/                   # Static assets, manifest.json, sw.js
│   │
│   ├── api/                          # FastAPI backend
│   │   └── app/
│   │       ├── api/                  # REST routes per module
│   │       ├── services/             # Business logic layer
│   │       └── ai/                   # Context builder, action executor
│   │
│   ├── admin/                        # Admin panel (WIP)
│   └── mobile/                       # React Native mobile (WIP)
│
├── packages/                         # Shared libraries
│   ├── ai/agents/                    # AI agent modules (8 agents)
│   │   ├── orchestrator.ts           # Master coordinator agent
│   │   ├── planner.ts                # Daily/weekly scheduling
│   │   ├── reminder.ts               # Missed task detection + escalation
│   │   ├── sleep.ts                  # Sleep scoring + task adjustment
│   │   ├── analytics.ts              # Productivity scores + insights
│   │   ├── learning.ts               # Course tracking + spaced repetition
│   │   ├── career.ts                 # GitHub monitoring + opportunity matching
│   │   └── memory.ts                 # Long-term preference/pattern storage
│   ├── config/core/                  # FastAPI config, auth middleware, Supabase client
│   ├── database/schemas/             # Pydantic models for all 21 tables
│   ├── shared/utils/                 # Logging, cache, rate limiter, retry, security
│   ├── types/                        # Shared TypeScript/Pydantic type definitions
│   └── ui/                           # Shared React components (Button, Card, Input, Modal)
│
├── services/                         # Background services
│   └── scheduler/                    # APScheduler + cron job orchestration
│       ├── main.py                   # Scheduler entry point
│       └── jobs/                     # Individual job definitions
│
├── docs/                             # Documentation
│   ├── product/                      # PRD, Features, Roadmap
│   ├── design/                       # UI/UX design system
│   ├── engineering/                  # Architecture, API, Database (this directory)
│   ├── ai/                           # Agents, AI_Instructions, Prompts
│   ├── security/                     # Security policies
│   ├── devops/                       # Deployment guides
│   └── operations/                   # Implementation status, Tech stack
│
├── infrastructure/                   # Infrastructure-as-Code (WIP)
│   ├── docker/                       # Docker Compose for local dev
│   ├── terraform/                    # Cloud provisioning
│   └── k8s/                          # Kubernetes manifests (future)
│
├── tests/                            # Test suites
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   └── e2e/                          # End-to-end tests (Playwright)
│
├── scripts/                          # Build/deployment scripts
│   ├── setup.sh                      # First-time environment setup
│   └── seed.ts                       # Database seeding
│
├── analytics/                        # Analytics configuration
├── monitoring/                       # Monitoring config (Sentry, uptime)
│
├── package.json                      # Root workspace config (npm workspaces)
├── turbo.json                        # Turborepo pipeline config
├── AGENTS.md                         # AI developer guide
└── README.md                         # Project overview
```

---

## Module Dependency Graph

```
                    ┌─────────────────────────────┐
                    │       Dashboard             │
                    │  (Aggregates all modules)   │
                    └──────┬──────┬──────┬───────┘
                           │      │      │
           ┌───────────────┘      │      └───────────────┐
           ▼                      ▼                      ▼
   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
   │  Task Manager│◄────►│ Course       │◄────►│ YouTube      │
   │  (Core)      │      │ Tracker      │      │ Vault        │
   └──┬───┬───┬───┘      └──────┬───────┘      └──────┬───────┘
      │   │   │                 │                      │
      │   │   │        ┌────────┴────────┐     ┌───────┴───────┐
      │   │   │        │  Study Sessions │     │  Resource     │
      │   │   │        │                 │     │  Library      │
      │   │   │        └─────────────────┘     └───────────────┘
      │   │   │
      │   │   └──────────────┐
      │   │                  │
  ┌───┴───┴────────┐  ┌─────┴──────┐
  │  Time Tracker  │  │  Habit     │
  │  (Pomodoro)    │  │  Engine    │
  └───────┬────────┘  └─────┬──────┘
          │                 │
          ▼                 ▼
  ┌──────────────┐  ┌──────────────┐
  │  Sleep       │  │  Weekly      │
  │  Monitor     │  │  Review      │
  └──────┬───────┘  └──────┬───────┘
         │                 │
         ▼                 ▼
  ┌──────────────┐  ┌──────────────┐
  │  Goal &      │  │  Academic    │
  │  Roadmap     │  │  Planner     │
  └──────┬───────┘  └──────┬───────┘
         │                 │
         ▼                 ▼
  ┌──────────────┐  ┌──────────────┐
  │  Opportunity │  │  Income      │
  │  Radar       │  │  Tracker     │
  └──────┬───────┘  └──────┬───────┘
         │                 │
         ▼                 ▼
  ┌──────────────┐  ┌──────────────┐
  │  Project     │  │  Idea Vault  │
  │  Tracker     │  │              │
  └──────────────┘  └──────────────┘

Data Flow Between Modules:
─────────────────────────────────

Task → Time:   Every timer session links to a task
Task → Goal:   Tasks optionally link to goals for progress tracking
Course → Task: Course generates daily study tasks automatically
Course → Goal: Courses link to learning goals
Sleep → Task:  Low sleep score → heavy tasks moved to tomorrow
Sleep → Habit: Sleep consistency tracked as a habit
Habit → Goal:  Habit completion contributes to goal progress
Goal → Roadmap: Goals link to roadmap nodes for timeline tracking
Project → Task: Project next_action generates tasks
Project → Income: Projects link to income sources
Idea → Project: Validated ideas become projects
Opportunity → Goal: Opportunities can trigger new roadmap creation
Income → Project: Income sources link to their generating projects
Weekly → All:   Weekly review aggregates all modules
```

---

## Request Lifecycle

### Typical API Request (Frontend → Supabase)

```
User Action (click, form submit)
       │
       ▼
React Component Event Handler
       │
       ▼
Zustand Store Action (optimistic update)
       │
       ▼
Supabase Client (`supabase.from('tasks').insert(...)`)
       │
       ├── RLS Policy Check (auth.uid() = user_id)
       │      │
       │      ├── Pass → Query Executes
       │      └── Fail → 401 Unauthorized
       │
       ▼
Supabase Realtime (broadcasts change to all clients)
       │
       ▼
React Query Cache Invalidation (refetch affected queries)
       │
       ▼
UI Re-renders with new data
```

### AI Chat Request

```
User types message in ARIA chat
       │
       ▼
Frontend sends POST /api/chat { message }
       │
       ▼
Next.js API Route (/api/chat/route.ts)
       │
       ├── 1. Context Builder fetches:
       │       - User profile + skills
       │       - Active courses with progress
       │       - Active goals with progress
       │       - Today's tasks + overdue tasks
       │       - Last 10 aria_memory entries
       │       - Last sleep log
       │
       ├── 2. Select AI provider:
       │       - Ollama (if USE_LOCAL_AI=true): localhost:11434/api/generate
       │       - Claude API (fallback): POST anthropic.com/v1/messages
       │
       ├── 3. AI processes context + prompt
       │       - Returns text response + optional action JSON blocks
       │
       ├── 4. Action Executor parses JSON:
       │       - { action: 'add_task', title, priority, due_date }
       │       - { action: 'update_course', name, progress_percent }
       │       - { action: 'save_idea', title, description, type }
       │       - { action: 'update_goal', title, progress_percent }
       │       Each action → Supabase CRUD operation
       │
       ├── 5. Memory Writer:
       │       - Sends conversation to AI for fact extraction
       │       - Inserts extracted facts to aria_memory table
       │
       ├── 6. Save to chat_messages table
       │
       └── 7. Return { response, action_taken } to frontend
```

### Edge Function Execution (Cron Agent)

```
pg_cron triggers Edge Function (e.g., daily-briefing at 01:30 UTC)
       │
       ▼
Supabase Edge Function (Deno runtime)
       │
       ├── 1. Authenticate with service_role key
       │
       ├── 2. Fetch user data from Supabase
       │       - SELECT * FROM tasks WHERE due_date = today
       │       - SELECT * FROM courses WHERE status = 'active'
       │       - SELECT * FROM opportunities WHERE found_at > yesterday
       │       - etc.
       │
       ├── 3. Call external API (Claude, Brave Search, Resend, etc.)
       │
       ├── 4. Process response (parse, filter, transform)
       │
       ├── 5. Write results back to Supabase
       │       - INSERT/UPDATE into appropriate tables
       │
       ├── 6. Send notifications (push, email, SMS)
       │       - Push: sendPushNotification(userId, title, body)
       │       - Email: POST resend.com/emails
       │       - SMS: POST twilio.com/2010-04-01/Accounts/{sid}/Messages
       │
       └── 7. Log execution result
```

---

## Integration Points

### Internal Integrations (within the system)

| Integration | Mechanism | Data Flow |
|-------------|-----------|-----------|
| Frontend ↔ Supabase | `@supabase/supabase-js` (Direct from client with RLS) | All CRUD operations |
| Frontend ↔ AI | Next.js API Routes (`/api/chat`) | Chat messages, context |
| Supabase ↔ Frontend | Supabase Realtime (WebSocket) | Live task/chat updates |
| Supabase ↔ External APIs | Edge Functions (Deno) | Cron agents calling Brave, Claude, Resend |
| Supabase ↔ Calendar | Next.js API Routes | OAuth2 + Google Calendar API |

### External Integrations

| Integration | Direction | Protocol | Auth Method |
|-------------|-----------|----------|-------------|
| **Ollama** | Backend → Localhost | HTTP POST `localhost:11434/api/generate` | None (localhost only) |
| **Claude API** | Backend → Cloud | HTTPS REST (`api.anthropic.com`) | API key header |
| **Brave Search** | Edge Fn → Cloud | HTTPS REST (`api.search.brave.com`) | API key header |
| **Google Calendar** | Backend ↔ Cloud | HTTPS REST (`www.googleapis.com/calendar/v3`) | OAuth2 (user token) |
| **Google Fit** | Backend → Cloud | HTTPS REST (`www.googleapis.com/fitness/v1`) | OAuth2 (user token) |
| **GitHub API** | Backend → Cloud | HTTPS REST (`api.github.com`) | OAuth2 (user token) |
| **Resend** | Backend → Cloud | HTTPS REST (`api.resend.com`) | API key header |
| **Twilio** | Backend → Cloud | HTTPS REST (`api.twilio.com`) | Account SID + Auth Token |
| **Web Push** | Backend → Browser | Web Push Protocol (VAPID) | VAPID keys |
| **YouTube oEmbed** | Backend → Cloud | HTTPS GET (`youtube.com/oembed`) | None (public API) |

### Integration Security Rules

1. All external API calls go through server-side routes (Next.js API routes, Edge Functions, or FastAPI)
2. No API keys or secrets ever appear in client-side JavaScript
3. OAuth tokens are stored in Supabase (users_profile table) encrypted at rest
4. Rate limits enforced per integration:
   - Brave Search: 50 queries/day across all users
   - Claude API: 10 requests/minute per user
   - GitHub API: 60 requests/hour (unauthenticated), 5,000/hour (authenticated)
   - Google APIs: per-user OAuth quota

---

## Tech Stack Summary

| Layer | Technology | Free Tier |
|-------|-----------|-----------|
| Frontend | Next.js 14 + Tailwind CSS + TypeScript | Free |
| State | Zustand + React Query | Free |
| Charts | Recharts | Free |
| Canvas | React Flow | Free (MIT) |
| Backend | FastAPI (Python) + Next.js API Routes | Free |
| Database | Supabase PostgreSQL | 500 MB free |
| Auth | Supabase Auth (Google OAuth) | Free |
| Realtime | Supabase Realtime | Free |
| AI (Primary) | Ollama + Llama 3.1 (local) | Free |
| AI (Fallback) | Claude API (Anthropic) | $5 credits |
| Email | Resend | 3,000/month free |
| SMS | Twilio | $15 credits |
| Push | Web Push + VAPID | Free |
| Voice | Web Speech API | Free |
| Search | Brave Search API | 2,000 queries/month |
| Hosting | Vercel | Free |
| Extension | WXT Framework | Free |
| Monitoring | Sentry | 5,000 errors/month |
| Offline | Workbox + IndexedDB | Free |
| OCR | Tesseract.js | Free |
| PDF | pdf-parse | Free |

---

## Build Phases Overview

| Phase | Weeks | Modules |
|-------|-------|---------|
| 1. Core Foundation | 1-2 | Auth, Tasks, Courses, Dashboard, Profile |
| 2. Save Everything | 3-4 | YouTube Vault, Resources, Ideas, Browser Extension |
| 3. ARIA + Memory | 5-6 | Chat, Memory, Daily Briefing, Weekly Review |
| 4. Opportunity Radar | 7-9 | Brave Search, Opportunity parser, Notifications |
| 5. Roadmap Engine | 10-11 | React Flow, Text/Image/PDF-to-roadmap, AI updates |
| 6. Income + Projects | 12-13 | Income, Projects, Academics, Habits, Sleep |
| 7. Reminders + Time | 14-15 | Push/Email/SMS, Time tracking, Calendar sync |
| 8. PWA + Polish | 16-17 | Offline support, Voice input, Onboarding, Data export |

Total build time: 17 weeks. Each phase is independently useful and deployable.
