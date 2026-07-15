# Features Overview

## Document Control

| Field | Value |
|---|---|
| Document ID | UG-FEATURES-001 |
| Version | 2.0.0 |
| Status | Active |
| Classification | Public - User Documentation |
| Last Updated | 2026-07-14 |

---

## Feature Catalog

ARIA OS includes **16 functional modules**, **11 AI agents**, and **15 cron jobs** designed for BTech CSE students.

### Core Productivity Modules

| Feature | Description | Key Capabilities | Where to Start |
|---|---|---|---|
| **Tasks** | Full todo management with priorities, due dates, recurring tasks, dependencies, and status tracking (pending, in progress, completed, missed). Includes list, kanban, and calendar views. | AI task analysis, auto-reschedule missed tasks, priority-based sorting, bulk operations, keyboard shortcuts | [Tasks](tasks.md) |
| **Habits** | Streak-based habit tracking with daily check-in, consistency percentage, best streak tracking, and habit calendar. Missed habit recovery with AI nudges. | Streak counter, consistency %, missed habit detection, AI recovery suggestions | [Habits](habits.md) |
| **Sleep** | Sleep logging with bedtime/wake time, quality rating, automatic sleep score calculation (0-100), sleep debt tracking, and AI-generated wind-down routines after 6 PM. | Sleep score, debt tracking, wind-down routines, quality trends | [Sleep](sleep.md) |
| **Time Tracking** | Pomodoro and deep work session tracking. Log time entries by category with duration, start/end times, and deep work indicators. View daily stats and breakdowns. | Pomodoro timer, deep work detection, daily stats, category breakdown charts | [Time Tracking](time-tracking.md) |

### Academic & Learning Modules

| Feature | Description | Key Capabilities | Where to Start |
|---|---|---|---|
| **Courses** | Academic course tracking across platforms (Udemy, Coursera, NPTEL, YouTube). Track progress percentage, videos completed, and deadlines. | Platform badges, progress rings, deadline tracking, AI study nudges (6 PM daily) | [Courses](courses.md) |
| **Goals** | Long-term goal planning with interactive roadmap canvas, progress percentage, target dates, categories, and status tracking (active, completed, abandoned). | React Flow roadmap, milestone nodes, task linking, AI roadmap optimization | [Goals](goals.md) |
| **Resources** | Curated learning resource library with tags and categorization. Save links to useful articles, videos, tools, documentation, and books. | Tag filtering, type categorization, status tracking, full-text search | [Resources](resources.md) |
| **Roadmap** | Skill development roadmap optimizer. AI-powered suggestions for optimal learning path ordering, prerequisite identification, and gap analysis. | AI-powered optimization, prerequisite detection, gap analysis | [Chat & AI](chat-and-ai.md) |

### Creative & Planning Modules

| Feature | Description | Key Capabilities | Where to Start |
|---|---|---|---|
| **Ideas** | Idea pipeline management from raw concept through validating to building stage. Capture and develop ideas systematically. | 3-stage pipeline, promote to project, tag categorization | [Ideas](ideas.md) |
| **Projects** | Multi-phase project management with status tracking, blockers, repository URL linking, and next action tracking. | 6 phases, blocker logging, GitHub link, next action field | [Projects](projects.md) |

### Finance & Career Modules

| Feature | Description | Key Capabilities | Where to Start |
|---|---|---|---|
| **Income** | Track income entries with hourly rate calculations, category breakdown, and monthly totals. | Hourly rate auto-calc, category breakdown, monthly totals, project linking | [Income](income.md) |
| **Opportunity Radar** | AI-matched opportunities (internships, scholarships, hackathons, open-source projects, grants, competitions) scored by relevance (0-100). Daily scan at 6 AM. | 8 source categories, match scoring, urgency alerts (<48h), daily scan | [Opportunities](opportunities.md) |
| **Opportunity Matching** | On-demand scoring engine that evaluates specific opportunities against your profile and goals. Instant relevance assessment with reasoning. | Per-opportunity scoring, profile matching, instant results | [Chat & AI](chat-and-ai.md) |

### AI & Intelligence Modules

| Feature | Description | Key Capabilities | Where to Start |
|---|---|---|---|
| **AI Chat** | Natural language conversation with ARIA. Asks about tasks, goals, habits, courses, sleep, and more. Streaming responses and conversation history. | 3-panel layout, streaming responses, agent badges, thought process view, context panel | [Chat & AI](chat-and-ai.md) |
| **Daily Briefing** | Morning summary generated at 7 AM by agent A09. Covers pending tasks, sleep score, habit streaks, deadlines, and a focus suggestion. | 6-section briefing, push notification, email digest (optional) | [Chat & AI](chat-and-ai.md) |
| **Weekly Review** | Sunday 8 PM AI-generated review of your week. Tasks completed, habit consistency, sleep trends, goals progress, and improvement tips. | 9-section review, trend analysis, next week focus suggestion | [Weekly Review](weekly-review.md) |
| **Memory** | AI persistent memory that learns your preferences, work patterns, and common topics from your conversations. Resettable from settings. | Automatic fact extraction, preference learning, resettable | [Chat & AI](chat-and-ai.md) |
| **Analytics** | Productivity stats across all modules. Timeline view of your activity, trend charts, and performance metrics. | Per-module stats, timeline view, trend visualization | Analytics page |
| **Predictions** | AI predictions for sleep quality and productivity based on your historical data. Uses learning agent (A03) pattern detection. | Sleep prediction, productivity prediction, pattern-based | Predictions page |
| **Automation** | Trigger AI agents on demand -- generate briefing, run opportunity radar, create weekly review, get sleep analysis, receive nudges. | 6 on-demand triggers, agent status monitoring, manual override | Automation settings |

### System Modules

| Feature | Description | Key Capabilities |
|---|---|---|
| **Notifications** | In-app notification center for reminders, nudges, system messages, and agent outputs. | Read/unread tracking, category grouping, push notifications |
| **Data Export** | Download all your data in JSON format (GDPR-compliant). Complete archive of all modules. | GDPR-compliant, all modules, JSON format |

## Feature Matrix

| Feature | Create | Read | Update | Delete | AI-Powered | Pagination | Offline |
|---|---|---|---|---|---|---|---|
| Tasks | Yes | Yes | Yes | Yes | Task analysis | Yes (20/page) | Planned |
| Habits | Yes | Yes | Yes | Yes | Nudge agent | Yes (20/page) | Planned |
| Sleep | Yes | Yes | Yes | Yes | Wind-down AI | Yes (30/page) | Planned |
| Goals | Yes | Yes | Yes | Yes | Roadmap AI | Yes (20/page) | Planned |
| Projects | Yes | Yes | Yes | Yes | No | Yes (20/page) | Planned |
| Courses | Yes | Yes | Yes | Yes | Nudge agent | Yes (20/page) | Planned |
| Ideas | Yes | Yes | Yes | Yes | No | Yes (20/page) | Planned |
| Time | Yes | Yes | Yes | Yes | No | Yes (20/page) | Planned |
| Income | Yes | Yes | Yes | Yes | No | Yes (20/page) | Planned |
| Opportunities | Yes | Yes | Yes | Yes | Radar agent | Yes (20/page) | Planned |
| Resources | Yes | Yes | Yes | Yes | No | Yes (20/page) | Planned |
| Roadmap | Yes | Yes | Yes | Yes | Roadmap AI | No | No |
| Chat | Yes | Yes | -- | -- | Core AI | No | No |
| Memory | Yes | Yes | Yes | Yes | Memory agent | No | No |
| Analytics | No | Yes | No | No | Learning agent | Yes (30/page) | No |
| Notifications | No | Yes | Yes | No | System | Yes (20/page) | Yes |

## AI Agent Triggers

| Agent | Trigger | Schedule | AI Model |
|---|---|---|---|
| Daily Briefing (A09) | Automatic + On-demand | 7 AM daily | Ollama / Claude |
| Missed Task Checker (A11) | Automatic | Every 15 min | No (rule-based) |
| Opportunity Radar (A06) | Automatic + On-demand | 6 AM daily | Ollama / Claude |
| Roadmap Update (A08) | Automatic + On-demand | Sunday 9 AM | Ollama / Claude |
| Weekly Review (A10) | Automatic + On-demand | Sunday 8 PM | Ollama / Claude |
| Sleep Wind-Down (A13) | Automatic | 9:30 PM daily | Ollama / Claude |
| Habit Miss Checker (A12) | Automatic | Midnight daily | No (rule-based) |
| Course Nudge (A14) | Automatic | 6 PM daily | Ollama / Claude |
| Memory (A02) | Background (every chat) | On interaction | Ollama / Claude |
| Learning (A03) | Automatic + On-demand | Daily | Ollama / Claude |
| Opportunity Match (A15) | On-demand | Per request | Ollama / Claude |

## Key Properties

| Property | Supported Features |
|---|---|
| Pagination | All list endpoints (limit 1-100, offset) |
| Authentication | JWT-based, all endpoints except health |
| Rate Limiting | Global 100 req/min, Chat 30 req/min |
| AI Fallback | Keyword-based when AI unavailable |
| Data Privacy | Local AI by default, cloud optional |
| Offline | PWA with service worker, IndexedDB cache (Phase 2) |
| Realtime | Supabase Realtime for live updates |
| Export | GDPR-compliant JSON data export |
