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
│  │   PostgreSQL + RLS + Realtime                            │   │
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
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Responsibilities

### Frontend (Next.js)

**Pages/Routes:**
- `/` - Dashboard with morning briefing
- `/tasks` - Task list and kanban
- `/courses` - Course tracker
- `/youtube` - YouTube vault
- `/resources` - Resource library
- `/ideas` - Idea vault
- `/goals` - Roadmap builder
- `/opportunities` - Opportunity radar
- `/income` - Income tracker
- `/projects` - Project tracker
- `/academics` - Academic planner
- `/habits` - Habit engine
- `/sleep` - Sleep monitor
- `/time` - Time tracker
- `/chat` - ARIA chat

**State Management:**
- Zustand for global state
- React Query for server state
- Persist to localStorage for offline

### Backend (FastAPI)

**API Routes:**
- RESTful endpoints for each module
- WebSocket for real-time chat

**Services:**
- Business logic for each feature
- AI prompt construction
- Context building for ARIA

### Database (Supabase)

**Tables:** 21 tables as documented in Database.md

**Features Used:**
- PostgreSQL for storage
- RLS for security
- Realtime for live updates
- Edge Functions for cron jobs

### AI Layer

**Ollama (Primary):**
- Runs locally on developer's machine
- Free, private, unlimited
- Used for: chat, summaries, suggestions

**Claude API (Fallback):**
- Used for complex tasks
- Weekly reviews
- Opportunity parsing
- Roadmap generation

### Scheduled Agents

**Daily Briefing (7 AM):**
- Reads all user data
- Generates personalized briefing
- Sends push + email

**Missed Task Checker (Every 15 min):**
- Finds overdue tasks
- Auto-reschedules
- Sends escalation notifications

**Opportunity Radar (6 AM):**
- Scrapes job boards
- Matches with user skills
- Stores opportunities

**Roadmap Update (Sunday 9 AM):**
- Checks if roadmap items are still valid
- Searches for syllabus changes
- Updates or alerts user

**Weekly Review (Sunday 8 PM):**
- Compiles week's data
- Generates narrative review
- Emails to user

**Sleep Reminder (9:30 PM):**
- Sends bedtime reminder
- Shows tomorrow's first task

---

## Data Flow

### User Creates Task
```
1. User fills form in frontend
2. POST /api/tasks
3. TaskService creates in Supabase
4. Realtime pushes to all clients
5. Task appears in lists
```

### User Chats with ARIA
```
1. User types message in chat
2. POST /api/chat
3. Backend builds context (tasks, goals, courses, etc.)
4. Calls Ollama with context + prompt
5. Returns response
6. Saves message to chat_messages table
7. If action requested, performs action
```

### Morning Briefing Generation
```
1. Cron triggers at 7 AM
2. Loads user's tasks, goals, opportunities
3. Calls Claude API
4. Generates briefing
5. Stores in database
6. Sends push notification
7. Sends email via Resend
```

---

## Deployment Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   User Browser  │────▶│   Vercel        │
│   (PWA)         │◀────│   (Frontend)    │
└─────────────────┘     └────────┬────────┘
                                 │
                                 │ API Calls
                                 ▼
┌─────────────────┐     ┌─────────────────┐
│   Ollama        │◀───▶│   Render/Railway│
│   (Local Dev)   │     │   (Backend)     │
└─────────────────┘     └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   Supabase      │
                        │   (DB + Auth)   │
                        └─────────────────┘
```

---

## Offline Strategy

1. **Service Worker:** Caches app shell and static assets
2. **IndexedDB:** Stores tasks, courses, goals locally
3. **Background Sync:** Queues actions when offline
4. **Optimistic Updates:** UI updates immediately, syncs later

---

## Security Architecture

1. **Authentication:** Supabase Auth (Google OAuth)
2. **Authorization:** RLS on every table
3. **API:** All endpoints require valid token
4. **Environment:** API keys never in client code
5. **HTTPS:** Enforced in production
