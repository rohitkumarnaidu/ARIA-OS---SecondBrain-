# Build Roadmap — Second Brain OS (ARIA OS)

---

## Document Control

| Field | Value |
|---|---|
| Document ID | SB-ROADMAP-001 |
| Version | 3.0.0 |
| Status | Active |
| Last Updated | 2026-06-11 |
| Classification | Internal — Engineering Roadmap |
| Owner | Product Lead / Lead Developer |
| Next Review | 2026-09-11 (Quarterly) |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-01 | Developer | Initial 8-phase build plan |
| 2.0.0 | 2026-06-11 | Developer | Expanded phases, added milestones, priority order |
| 3.0.0 | 2026-06-11 | Developer | Enterprise upgrade: 12-month rolling quarterly roadmap, dependency graph, effort estimates, release milestones, feature flags, risk register, lessons learned |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Roadmap Philosophy & Principles](#2-roadmap-philosophy--principles)
3. [12-Month Rolling Roadmap — Quarterly View](#3-12-month-rolling-roadmap--quarterly-view)
4. [Phase 1 (Q3 2026): Core Foundation](#4-phase-1-q3-2026-core-foundation)
5. [Phase 2 (Q3 2026): Save Everything](#5-phase-2-q3-2026-save-everything)
6. [Phase 3 (Q3 2026): ARIA & Core AI](#6-phase-3-q3-2026-aria--core-ai)
7. [Phase 4 (Q4 2026): Advanced AI](#7-phase-4-q4-2026-advanced-ai)
8. [Phase 5 (Q4 2026): Roadmap Engine](#8-phase-5-q4-2026-roadmap-engine)
9. [Phase 6 (Q1 2027): Full Life Tracking](#9-phase-6-q1-2027-full-life-tracking)
10. [Phase 7 (Q1 2027): Monitoring & Automation](#10-phase-7-q1-2027-monitoring--automation)
11. [Phase 8 (Q1 2027): Polish & Production Readiness](#11-phase-8-q1-2027-polish--production-readiness)
12. [Phase 9 (Q2 2027): Public Release & Collaboration](#12-phase-9-q2-2027-public-release--collaboration)
13. [Feature Breakdown with Effort Estimates](#13-feature-breakdown-with-effort-estimates)
14. [Dependency Graph](#14-dependency-graph)
15. [Release Milestones & Timeline](#15-release-milestones--timeline)
16. [Alpha / Beta / GA Timeline](#16-alpha--beta--ga-timeline)
17. [Feature Flags & Gradual Rollout Plan](#17-feature-flags--gradual-rollout-plan)
18. [Past Roadmap Accuracy & Lessons Learned](#18-past-roadmap-accuracy--lessons-learned)
19. [Roadmap Update Cadence & Process](#19-roadmap-update-cadence--process)
20. [Risk Register for Timeline](#20-risk-register-for-timeline)
21. [What's Explicitly NOT Planned](#21-whats-explicitly-not-planned)
22. [Appendices](#22-appendices)

---

## 1. Executive Summary

This roadmap outlines a **12-month rolling build plan** (Q3 2026 — Q2 2027) for Second Brain OS, organized into **9 phases** across 4 quarters. The plan transitions from solo development through core feature completion to public release, collaboration features, and mobile/extension launch.

**Key commitments:**
- **Alpha launch**: Month 3 (end of Q3 2026) — 15 modules operational, basic AI
- **Beta launch**: Month 6 (end of Q4 2026) — Advanced AI, radar, context engine
- **GA (General Availability)**: Month 12 (end of Q2 2027) — Public release, mobile, browser extension
- **Total estimated effort**: ~455 hours across all phases
- **Infrastructure cost**: Rs. 0/month (free-tier services)
- **Team**: Solo developer (part-time) + community contributions post-GA

---

## 2. Roadmap Philosophy & Principles

### 2.1 Guiding Principles

| # | Principle | Meaning |
|---|---|---|
| 1 | **Ship early, ship often** | Every phase must produce a working, usable feature. No 3-month silos. |
| 2 | **Dogfood everything** | Developer uses every feature personally from Day 1. If it's not useful to the builder, it doesn't ship. |
| 3 | **AI is an enhancement, not a dependency** | Every feature has a non-AI fallback. Graceful degradation always. |
| 4 | **Free-tier infrastructure** | No feature may require paid hosting. If it needs paid infra, defer or downscope. |
| 5 | **Data completeness before AI polish** | The system must track everything correctly before AI makes it smart. Garbage in, garbage out. |
| 6 | **Offline capability from Day 1** | All CRUD operations must work offline. Network is optional. |
| 7 | **Mobile-first design, web-first delivery** | Design for mobile screens first, implement on web first, ship native mobile later. |
| 8 | **Test-driven where practical** | Prompt validation and API endpoint tests are mandatory. Frontend tests after stable UI. |

### 2.2 Priority Framework

Features are evaluated on a 2x2 matrix:

```
                    HIGH USER VALUE
                         │
                         │
    LOW EFFORT ──────────┼────────── HIGH EFFORT
                         │
                         │
                     LOW USER VALUE

Quadrant priorities:
Q1 (Low effort, High value): BUILD FIRST — Quick wins, maximum impact
Q2 (High effort, High value): PLAN CAREFULLY — Core features, need proper scoping
Q3 (Low effort, Low value): DO IF TIME — Nice-to-haves, polish
Q4 (High effort, Low value): DEFER OR SKIP — Feature creep candidates
```

### 2.3 Capacity Planning

| Constraint | Value |
|---|---|
| Development time | 10-15 hours/week (part-time, evenings + weekends) |
| Available weeks | 48 weeks/year (4 weeks buffer for exams, breaks) |
| Total available hours | ~480-720 hours/year |
| Roadmap estimate | ~455 hours |
| Buffer | 5-35% (built into each phase) |
| Break weeks | Exam periods (Oct, Dec, Apr) — reduced output expected |

---

## 3. 12-Month Rolling Roadmap — Quarterly View

```
QUARTER 1 (Q3 2026 — Jul-Sep)          QUARTER 2 (Q4 2026 — Oct-Dec)
──────────────────────────────         ──────────────────────────────
Phase 1: Core Foundation               Phase 4: Advanced AI
  Week 1-2: Next.js + Supabase           Week 11-12: Learning Agent
  Week 2-3: Tasks + Courses              Week 13-14: Opportunity Radar
                                         Week 15: Context Engine
Phase 2: Save Everything
  Week 4-5: YouTube + Resources         Phase 5: Roadmap Engine
  Week 6: Ideas + Browser Ext           Week 16-17: Visual Builder
                                         Week 18: AI Parsing + Templates
Phase 3: ARIA & Core AI
  Week 7-8: ARIA Chat + Memory          Phase 6 (partial): Income + Projects
  Week 9-10: Briefing + Review           Week 19-20: Income Tracking

┌─────────────────────────────────┐    ┌─────────────────────────────────┐
│ ALPHA LAUNCH (End of Q3)       │    │ BETA LAUNCH (End of Q4)        │
│ 15 modules + basic AI          │    │ Advanced AI + Radar + Engine   │
└─────────────────────────────────┘    └─────────────────────────────────┘

QUARTER 3 (Q1 2027 — Jan-Mar)          QUARTER 4 (Q2 2027 — Apr-Jun)
──────────────────────────────         ──────────────────────────────
Phase 6: Full Life Tracking             Phase 9: Public Release
  Week 21-22: Projects + GitHub          Week 31-32: GitHub public + docs
  Week 23-24: Academics + CGPA           Week 33: Demo video + launch
  Week 25-26: Habits + Streaks
                                         Phase 9: Collaboration Features
Phase 7: Monitoring & Automation         Week 34-35: Sharing + Templates
  Week 27-28: Reminders + Sleep          Week 36: Community infrastructure
  Week 29-30: Time Tracking
                                         Phase 10: Mobile + Extension
Phase 8: Polish & Production             Week 37-40: React Native app
  Week 30: PWA + Offline
  Week 31: Voice + Accessibility

┌─────────────────────────────────┐    ┌─────────────────────────────────┐
│ GA CANDIDATE (End of Q1)       │    │ GA LAUNCH (End of Q2)          │
│ Complete feature set + stable  │    │ Mobile + Extension + Community │
└─────────────────────────────────┘    └─────────────────────────────────┘
```

---

## 4. Phase 1 (Q3 2026): Core Foundation

### Overview

| Attribute | Value |
|---|---|
| **Phases** | Phase 1 |
| **Timeline** | Weeks 1-3 (Jul 2026) |
| **Effort** | ~45 hours |
| **Dependencies** | None (starting from scratch) |
| **Risk** | Low — well-understood technologies |
| **Deliverable** | Working app with login, tasks, courses, dashboard |

### Tasks Breakdown

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1 — CORE FOUNDATION                                      │
│ Effort: ~45 hours (Weeks 1-3)                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Week 1 (15 hrs)                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-01  Next.js 14 project setup + Tailwind + TypeScript  │ 4h │
│  │ T-02  Supabase project creation + schema design         │ 3h │
│  │ T-03  All 21 database tables with RLS policies          │ 4h │
│  │ T-04  Google OAuth authentication flow                  │ 4h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Week 2 (15 hrs)                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-05  FastAPI backend setup + router registration        │ 3h │
│  │ T-06  Task Manager: CRUD, priority, status, categories  │ 4h │
│  │ T-07  Course Tracker: CRUD, progress, deadlines         │ 4h │
│  │ T-08  Goal Manager: CRUD, milestones, roadmaps          │ 4h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Week 3 (15 hrs)                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-09  Dashboard with task overview + metrics            │ 4h │
│  │ T-10  User Profile with skills, preferences             │ 3h │
│  │ T-11  5-step onboarding wizard                          │ 3h │
│  │ T-12  Basic auto-reschedule cron (15-min interval)      │ 2h │
│  │ T-13  Deploy to Vercel + Railway                        │ 1h │
│  │ T-14  Initial test suite (API endpoints)                │ 2h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### In Scope

- Next.js 14 with App Router, TypeScript, Tailwind CSS
- Supabase PostgreSQL with 21 tables, proper indexes, foreign keys
- Row-Level Security on every table (auth.uid() = user_id)
- FastAPI backend with all 13 routers and ~53 endpoints
- Google OAuth with Supabase Auth
- Basic task auto-reschedule algorithm (due dates, priority weights)
- Responsive dashboard showing today's tasks, pending courses, upcoming deadlines

### Acceptance Criteria

- [ ] User can sign up and log in with Google
- [ ] User can create, read, update, delete tasks with priority and category
- [ ] User can add courses with progress tracking and deadlines
- [ ] User can set goals with milestones
- [ ] Dashboard shows relevant overview data
- [ ] All 21 tables have RLS enforced
- [ ] API responds within 200ms P95
- [ ] Deployment is automated via GitHub → Vercel/Railway

### Effort Estimate Detail

| Task | Hours | Complexity | Skills Required |
|---|---|---|---|
| T-01: Next.js setup | 4 | Low | Frontend |
| T-02: Supabase schema | 3 | Medium | Database design |
| T-03: RLS policies | 4 | Medium | Security, SQL |
| T-04: Auth flow | 4 | Medium | Auth patterns |
| T-05: FastAPI setup | 3 | Low | Backend |
| T-06: Task CRUD | 4 | Low | Full-stack |
| T-07: Course CRUD | 4 | Low | Full-stack |
| T-08: Goal CRUD | 4 | Low | Full-stack |
| T-09: Dashboard | 4 | Medium | Frontend |
| T-10: Profile | 3 | Low | Full-stack |
| T-11: Onboarding | 3 | Medium | UX, frontend |
| T-12: Auto-reschedule | 2 | Medium | Algorithm |
| T-13: Deploy | 1 | Low | DevOps |
| T-14: Tests | 2 | Low | Testing |
| **Total** | **45** | | |

---

## 5. Phase 2 (Q3 2026): Save Everything

### Overview

| Attribute | Value |
|---|---|
| **Phases** | Phase 2 |
| **Timeline** | Weeks 4-6 (Aug 2026) |
| **Effort** | ~40 hours |
| **Dependencies** | Phase 1 (user auth, database) |
| **Risk** | Low-Medium — primarily CRUD + AI summary integration |
| **Deliverable** | Content capture modules operational, browser extension deployed |

### Tasks Breakdown

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2 — SAVE EVERYTHING                                      │
│ Effort: ~40 hours (Weeks 4-6)                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Week 4 (15 hrs)                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-15  YouTube Knowledge Vault — save, organize, search  │ 5h │
│  │ T-16  YouTube AI summary integration (Claude API)       │ 4h │
│  │ T-17  Watch scheduling with 60-day expiry notifications │ 3h │
│  │ T-18  Resource Library — articles, books, repos, search │ 3h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Week 5 (15 hrs)                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-19  Auto-tagging for resources (AI via Ollama)        │ 3h │
│  │ T-20  Natural language search across resources          │ 4h │
│  │ T-21  Idea Vault — capture + status pipeline            │ 3h │
│  │ T-22  AI market check on new ideas (Ollama)             │ 2h │
│  │ T-23  Goal linking for resources and ideas              │ 3h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Week 6 (10 hrs)                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-24  Browser Extension (WXT) — one-click save          │ 6h │
│  │ T-25  Chrome + Firefox packaging                        │ 2h │
│  │ T-26  Resurface Engine — surface contextually           │ 2h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Technical Decisions

- **Browser extension**: WXT framework (supports Chrome + Firefox from single codebase)
- **AI summaries**: Claude API for high-quality summaries (YouTube transcripts)
- **Auto-tagging**: Ollama local model (Mistral 7B) for privacy and zero cost
- **Search**: PostgreSQL full-text search initially, upgrade to vector search in Phase 4
- **Resurface Engine**: Keyword-matching + recency-weighted algorithm (no AI required)

---

## 6. Phase 3 (Q3 2026): ARIA & Core AI

### Overview

| Attribute | Value |
|---|---|
| **Phases** | Phase 3 |
| **Timeline** | Weeks 7-10 (Aug-Sep 2026) |
| **Effort** | ~50 hours |
| **Dependencies** | Phase 1 (database, auth), Phase 2 (content for memory) |
| **Risk** | High — AI integration is novel, Ollama reliability |
| **Deliverable** | Working AI assistant with persistent memory, daily briefing, weekly review |

### Tasks Breakdown

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3 — ARIA & CORE AI                                       │
│ Effort: ~50 hours (Weeks 7-10)                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Week 7 (15 hrs)                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-27  ARIA chat panel UI (Framer Motion animations)    │ 4h │
│  │ T-28  Ollama integration with Mistral 7B               │ 3h │
│  │ T-29  Claude API fallback client                       │ 2h │
│  │ T-30  FastAPI /api/chat/ endpoint with streaming       │ 3h │
│  │ T-31  Basic context builder (profile + goals)          │ 3h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Week 8 (15 hrs)                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-32  Memory agent — aria_memory table + CRUD           │ 4h │
│  │ T-33  Memory consolidation — retention/discard logic    │ 3h │
│  │ T-34  Chat-triggered actions (add task, update goal)    │ 4h │
│  │ T-35  PromptLoader integration for agent prompts        │ 2h │
│  │ T-36  Prompt files for briefing, memory, task agents    │ 2h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Week 9 (10 hrs)                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-37  Daily Briefing generation engine (7 AM cron)      │ 4h │
│  │ T-38  Briefing push — email (Resend) + in-app           │ 3h │
│  │ T-39  Briefing read tracking + analytics                │ 1h │
│  │ T-40  Prompt file: briefing_agent.md                    │ 2h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Week 10 (10 hrs)                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-41  Weekly Review generation (Sunday 8 PM cron)       │ 4h │
│  │ T-42  Review presentation (narrative + data view)       │ 3h │
│  │ T-43  Prompt file: weekly_review_agent.md               │ 2h │
│  │ T-44  Agent test suite (14 agent prompt tests)          │ 1h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Alpha Launch Criteria (End of Week 10)

- [ ] ARIA chat panel renders and accepts user input
- [ ] Ollama responds to prompts with Mistral 7B
- [ ] Claude fallback works when Ollama is offline
- [ ] Memory stores and retrieves user preferences and facts
- [ ] Chat can create tasks and update goals via natural language
- [ ] Daily briefing generates and delivers at 7 AM
- [ ] Weekly review generates on Sunday 8 PM
- [ ] All 12 prompt files pass validation
- [ ] PromptLoader loads all prompts with 100% frontmatter coverage
- [ ] All 30 tests pass (16 loader + 14 agent)

---

## 7. Phase 4 (Q4 2026): Advanced AI

### Overview

| Attribute | Value |
|---|---|
| **Phases** | Phase 4 |
| **Timeline** | Weeks 11-15 (Oct-Nov 2026) |
| **Effort** | ~55 hours |
| **Dependencies** | Phase 3 (PromptLoader, context builder, basic AI) |
| **Risk** | High — learning agent requires sufficient data (>3 months), complex matching algorithms |
| **Deliverable** | Learning agent, opportunity radar, context engine, sleep/nudge agents |

### Tasks Breakdown

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 4 — ADVANCED AI                                          │
│ Effort: ~55 hours (Weeks 11-15)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Week 11 (12 hrs)                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-45  Learning Agent — pattern detection engine          │ 5h │
│  │ T-46  Learning progress snapshots (learning_progress)   │ 3h │
│  │ T-47  Prompt file: learning_agent.md                    │ 2h │
│  │ T-48  Learning influence graph (weak signal detection)  │ 2h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Week 12 (12 hrs)                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-49  Brave Search API integration                      │ 2h │
│  │ T-50  Opportunity Radar cron (6 AM daily)               │ 4h │
│  │ T-51  Skill-match algorithm with weighted scoring       │ 3h │
│  │ T-52  Deadline urgency + history personalization        │ 3h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Week 13 (10 hrs)                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-53  Opportunities Dashboard — filters, apply tracking │ 4h │
│  │ T-54  Critical deadline alerts (<48 hours)              │ 2h │
│  │ T-55  Opportunity profile editor (fine-tune radar)      │ 2h │
│  │ T-56  Prompt file: opportunity_radar_agent.md           │ 2h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Week 14 (10 hrs)                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-57  Context Engine — full context assembly pipeline   │ 5h │
│  │ T-58  Prompt file: context_assembly.md                  │ 2h │
│  │ T-59  Context caching + token optimization              │ 3h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Week 15 (11 hrs)                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-60  Sleep Agent — wind-down, bedtime routine          │ 4h │
│  │ T-61  Nudge Agent — course/habit progress nudges        │ 4h │
│  │ T-62  Prompt files: sleep_agent.md, nudge_agent.md     │ 2h │
│  │ T-63  Agent scheduler registration (APScheduler)        │ 1h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Beta Launch Criteria (End of Week 15)

- [ ] Learning agent detects patterns and provides insights
- [ ] Opportunity radar scans 6 categories daily, generates match scores
- [ ] Context engine assembles optimized prompts for all agents
- [ ] Sleep agent delivers wind-down messages at 9:30 PM
- [ ] Nudge agent checks course/habit progress and sends reminders at 6 PM
- [ ] All 8 agent prompt files are validated and loaded via PromptLoader
- [ ] 30+ tests pass in CI

---

## 8. Phase 5 (Q4 2026): Roadmap Engine

### Overview

| Attribute | Value |
|---|---|
| **Phases** | Phase 5 |
| **Timeline** | Weeks 16-18 (Nov-Dec 2026) |
| **Effort** | ~40 hours |
| **Dependencies** | Phase 4 context engine (AI parsing) |
| **Risk** | Medium — React Flow integration, AI parsing complexity |
| **Deliverable** | Visual roadmap builder for all goals, template library |

### Tasks Breakdown

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 5 — ROADMAP ENGINE                                       │
│ Effort: ~40 hours (Weeks 16-18)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Week 16 (15 hrs)                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-64  React Flow canvas integration + custom nodes      │ 5h │
│  │ T-65  Visual drag-and-drop builder interface            │ 4h │
│  │ T-66  8 node types (task, milestone, course, etc.)      │ 3h │
│  │ T-67  Connection validation + circular dependency check │ 3h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Week 17 (13 hrs)                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-68  Text-to-roadmap parser (AI)                      │ 4h │
│  │ T-69  PDF/image upload + syllabus extraction (Vision)   │ 3h │
│  │ T-70  Template library — 8 pre-built roadmap types     │ 3h │
│  │ T-71  Timing sliders with real-time recalculation       │ 3h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Week 18 (12 hrs)                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-72  Hard Deadline Mode — work backwards from date     │ 3h │
│  │ T-73  Weekly AI update checker for roadmap items        │ 3h │
│  │ T-74  Roadmap persistence + undo/redo                   │ 3h │
│  │ T-75  Template creation + sharing (local)               │ 3h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Phase 6 (Q1 2027): Full Life Tracking

### Overview

| Attribute | Value |
|---|---|
| **Phases** | Phase 6 |
| **Timeline** | Weeks 19-26 (Jan-Feb 2027) |
| **Effort** | ~60 hours |
| **Dependencies** | Phase 1 (basic framework) |
| **Risk** | Low — primarily CRUD + simple algorithms |
| **Deliverable** | Complete life tracking across income, projects, academics, habits |

### Tasks Breakdown

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 6 — FULL LIFE TRACKING                                   │
│ Effort: ~60 hours (Weeks 19-26)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Week 19-20 (15 hrs) — Income                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-76  Income Sources Dashboard — log entries            │ 3h │
│  │ T-77  Monthly summary + effective hourly rate calc      │ 3h │
│  │ T-78  Income categorization + trend analysis            │ 3h │
│  │ T-79  Income → skill linking                            │ 3h │
│  │ T-80  Weekly income review email                        │ 3h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Week 21-22 (15 hrs) — Projects + GitHub                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-81  Project Tracker — phase tracking (Kanban style)   │ 4h │
│  │ T-82  Next action rule (auto-suggest next step)         │ 3h │
│  │ T-83  Blocker logging + escalation                      │ 2h │
│  │ T-84  GitHub API integration — repo linking, commits    │ 3h │
│  │ T-85  Weekly commit check + skill profile auto-update   │ 2h │
│  │ T-86  LinkedIn Post Generator (milestone -> draft)      │ 1h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Week 23-24 (15 hrs) — Academics + CGPA                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-87  Academic Planner — subjects, semesters            │ 4h │
│  │ T-88  CGPA Calculator with projections                  │ 3h │
│  │ T-89  Marks entry + grade tracking                      │ 3h │
│  │ T-90  At-risk subject alerts (performance < threshold)  │ 2h │
│  │ T-91  Semester timeline view                            │ 3h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Week 25-26 (15 hrs) — Habits + Streaks                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-92  Habit Engine — custom habit definitions           │ 3h │
│  │ T-93  Habit_logs table + daily logging interface        │ 3h │
│  │ T-94  Streak tracking + consistency reports             │ 3h │
│  │ T-95  Goal linking for habits                           │ 2h │
│  │ T-96  Habit reminders + miss detection                  │ 2h │
│  │ T-97  Weekly habit summary + recovery rate tracking     │ 2h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Phase 7 (Q1 2027): Monitoring & Automation

### Overview

| Attribute | Value |
|---|---|
| **Phases** | Phase 7 |
| **Timeline** | Weeks 27-30 (Feb-Mar 2027) |
| **Effort** | ~45 hours |
| **Dependencies** | Phase 6 (habits for reminders, tasks for reminders) |
| **Risk** | Medium — notification delivery reliability, Google Calendar OAuth |
| **Deliverable** | Complete monitoring system with multi-channel reminders, sleep tracking, time tracking |

### Tasks Breakdown

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 7 — MONITORING & AUTOMATION                              │
│ Effort: ~45 hours (Weeks 27-30)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Week 27-28 (15 hrs) — Reminders + Sleep                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-98  Push notification system (PWA + mobile)           │ 4h │
│  │ T-99  Email via Resend — critical alerts, summaries     │ 2h │
│  │ T-100 SMS escalation (Twilio) for high-priority misses  │ 2h │
│  │ T-101 Sleep Monitor — bedtime/wake logging              │ 3h │
│  │ T-102 Sleep quality rating, score, debt calculation     │ 2h │
│  │ T-103 Sleep → task adjustment (lighter day after bad)   │ 2h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Week 29-30 (15 hrs) — Time Tracking + Calendar                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-104 Time Tracker — start/stop per task               │ 3h │
│  │ T-105 Pomodoro mode (25/5 workflow)                    │ 3h │
│  │ T-106 Deep work detection (focus hour analysis)        │ 3h │
│  │ T-107 Google Calendar two-way sync (OAuth)             │ 4h │
│  │ T-108 Time analytics dashboard                         │ 2h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Remaining: Integration testing + bug fixes (15 hrs spread)    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 11. Phase 8 (Q1 2027): Polish & Production Readiness

### Overview

| Attribute | Value |
|---|---|
| **Phases** | Phase 8 |
| **Timeline** | Weeks 30-31 (Mar 2027) |
| **Effort** | ~30 hours |
| **Dependencies** | All previous phases (stabilize full system) |
| **Risk** | Low — optimization and polish, no new features |
| **Deliverable** | Production-ready PWA with offline support, voice input, accessibility |

### Tasks Breakdown

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 8 — POLISH & PRODUCTION READINESS                        │
│ Effort: ~30 hours (Weeks 30-31)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Week 30 (15 hrs)                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-109 PWA with next-pwa — service worker                │ 4h │
│  │ T-110 IndexedDB offline storage for all CRUD ops        │ 5h │
│  │ T-111 Background sync when coming online                 │ 3h │
│  │ T-112 Lighthouse audit + performance optimization       │ 3h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Week 31 (15 hrs)                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-113 Voice Input (Web Speech API for ARIA)             │ 3h │
│  │ T-114 Mobile optimization (low-end Android focus)       │ 4h │
│  │ T-115 Data export (JSON/CSV in Settings)                │ 2h │
│  │ T-116 Security audit — RLS verification, key exposure   │ 3h │
│  │ T-117 Rate limiting implementation                      │ 1h │
│  │ T-118 Full end-to-end testing                           │ 2h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 12. Phase 9 (Q2 2027): Public Release & Collaboration

### Overview

| Attribute | Value |
|---|---|
| **Phases** | Phase 9 |
| **Timeline** | Weeks 32-36 (Apr-May 2027) |
| **Effort** | ~50 hours |
| **Dependencies** | Phase 8 (stable, secure release candidate) |
| **Risk** | Medium — community management, unknown support burden |
| **Deliverable** | Public GitHub release, documentation, collaboration features |

### Tasks Breakdown

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 9 — PUBLIC RELEASE & COLLABORATION                       │
│ Effort: ~50 hours (Weeks 32-36)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Week 32 (12 hrs) — Release Preparation                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-119 Public GitHub repository cleanup + README          │ 3h │
│  │ T-120 Deploy-in-10-minutes guide + .env.example         │ 2h │
│  │ T-121 CONTRIBUTING.md + CODE_OF_CONDUCT.md              │ 2h │
│  │ T-122 LICENSE file (MIT)                                │ 1h │
│  │ T-123 CI/CD pipeline final verification                 │ 2h │
│  │ T-124 CHANGELOG.md finalization                         │ 2h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Week 33 (10 hrs) — Launch                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-125 Demo video (3-5 min showing all 15 modules)       │ 4h │
│  │ T-126 Product Hunt + Hacker News + Reddit launch posts  │ 3h │
│  │ T-127 Social media campaign (Twitter, LinkedIn)         │ 2h │
│  │ T-128 Initial support infrastructure (Discord, issues)  │ 1h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Week 34-35 (15 hrs) — Collaboration Features                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-129 Public roadmap template sharing                  │ 4h │
│  │ T-130 Shared prompt templates (community-curated)      │ 3h │
│  │ T-131 User success story capture system                │ 2h │
│  │ T-132 Feature voting / request pipeline (GitHub)       │ 2h │
│  │ T-133 Documentation site (GitHub Pages)                │ 4h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Week 36 (13 hrs) — Community Infrastructure                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ T-134 Discord server setup + moderation                 │ 3h │
│  │ T-135 First community call (design review)              │ 2h │
│  │ T-136 Plugin API draft documentation                    │ 5h │
│  │ T-137 Onboarding documentation for new contributors     │ 3h │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 13. Feature Breakdown with Effort Estimates

### Complete Effort Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    TOTAL EFFORT BY PHASE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Phase 1: Core Foundation              45 hrs    9.9%          │
│ Phase 2: Save Everything              40 hrs    8.8%           │
│ Phase 3: ARIA & Core AI               50 hrs   11.0%           │
│ Phase 4: Advanced AI                  55 hrs   12.1%           │
│ Phase 5: Roadmap Engine               40 hrs    8.8%           │
│ Phase 6: Full Life Tracking           60 hrs   13.2%           │
│ Phase 7: Monitoring & Automation      45 hrs    9.9%           │
│ Phase 8: Polish & Production          30 hrs    6.6%           │
│ Phase 9: Public Release               50 hrs   11.0%           │
│ Buffer (Phase 10: Mobile Preview)     40 hrs    8.8%           │
│ ─────────────────────────────────────────────────────          │
│ TOTAL                               455 hrs  100%             │
│                                                                 │
│ Weekly average (48 weeks):           9.5 hrs/week              │
│ With exam buffers (44 weeks):       10.3 hrs/week              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Effort by Category

```
┌─────────────────────────────────────────────────────────────────┐
│                    EFFORT BY CATEGORY                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Frontend (React/Next.js)          150 hrs  33.0%  ████████░░  │
│  Backend (FastAPI/Python)          120 hrs  26.4%  ██████░░░░  │
│  AI/Agent (PromptLoader, prompts)   75 hrs  16.5%  ████░░░░░░  │
│  Database (SQL, RLS, indexing)      40 hrs   8.8%  ██░░░░░░░░  │
│  DevOps (CI/CD, deployment)         30 hrs   6.6%  █░░░░░░░░░  │
│  Documentation & Community          25 hrs   5.5%  █░░░░░░░░░  │
│  Testing (unit, integration)        15 hrs   3.3%  ░░░░░░░░░░  │
│ ─────────────────────────────────────────────────────          │
│  TOTAL                              455 hrs 100%               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Per-Module Effort Matrix

| Module | Est. Hours | Complexity | AI Required? | Fallback Available? |
|---|---|---|---|---|
| **Dashboard** | 10 | Low | No | N/A |
| **Tasks** | 15 | Low | No | N/A |
| **Courses** | 12 | Low | No | N/A |
| **Goals** | 10 | Low | No | N/A |
| **YouTube Vault** | 14 | Medium | Yes (summaries) | Manual notes |
| **Resources** | 10 | Medium | Yes (auto-tag) | Manual tagging |
| **Ideas** | 8 | Low | Yes (market check) | Manual evaluation |
| **Browser Extension** | 8 | Medium | No | N/A |
| **ARIA Chat** | 20 | High | Yes (core) | Command-line interface |
| **Memory** | 15 | High | Yes (core) | Key-value storage |
| **Daily Briefing** | 15 | High | Yes (core) | Static checklist |
| **Weekly Review** | 10 | Medium | Yes (core) | Manual review template |
| **Opportunity Radar** | 20 | High | Yes (matching) | Manual search |
| **Learning Agent** | 15 | High | Yes (core) | Stats dashboard |
| **Context Engine** | 15 | High | Yes (core) | Simple concatenation |
| **Roadmap Builder** | 25 | High | Yes (parsing) | Manual drag-drop |
| **Income** | 12 | Low | No | N/A |
| **Projects** | 15 | Medium | No | N/A |
| **Academics** | 15 | Low | No | N/A |
| **Habits** | 15 | Medium | No | N/A |
| **Sleep** | 8 | Low | Yes (wind-down) | Manual reminders |
| **Time Tracking** | 12 | Medium | No | N/A |
| **Reminders** | 12 | Medium | No | N/A |
| **Google Calendar Sync** | 6 | Medium | No | N/A |
| **PWA** | 10 | Medium | No | N/A |
| **Data Export** | 4 | Low | No | N/A |

---

## 14. Dependency Graph

### High-Level Dependency Map

```
Phase 1: Core Foundation
  │
  ├──► Phase 2: Save Everything
  │       │
  │       └──► Phase 3: ARIA & Core AI
  │               │
  │               ├──► Phase 4: Advanced AI
  │               │       │
  │               │       └──► Phase 5: Roadmap Engine
  │               │
  │               └──► (Phase 7: Monitoring needs ARIA context)
  │
  └──► Phase 6: Full Life Tracking
          │
          └──► Phase 7: Monitoring & Automation
                  │
                  └──► Phase 8: Polish & Production
                          │
                          └──► Phase 9: Public Release
```

### Detailed Task Dependency Graph

```
T-01 (Next.js setup)
  └── T-02 (Supabase) ──► T-03 (RLS) ──► T-04 (Auth)
                                               │
                    T-05 (FastAPI) ◄────────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
      T-06 (Tasks) T-07 (Courses) T-08 (Goals)
          │           │           │
          └───────────┼───────────┘
                      ▼
                 T-09 (Dashboard)
                      │
                 T-10 (Profile) ──► T-11 (Onboarding)
                      │
                      ▼
                 T-12 (Auto-reschedule) ──► T-13 (Deploy) ──► T-14 (Tests)

Phase 2 depends on: T-04 (Auth), T-13 (Deploy)
    │
    ▼
T-15 (YouTube) ──► T-16 (AI Summary) ──► T-17 (Scheduling)
T-18 (Resources) ──► T-19 (Auto-tag) ──► T-20 (NLP Search)
T-21 (Ideas) ──► T-22 (Market Check) ──► T-23 (Goal Linking)
                      │
T-24 (Browser Ext) ◄──┘
    │
    ▼
T-26 (Resurface Engine)

Phase 3 depends on: Phase 1, Phase 2 (content for memory)
    │
    ▼
T-27 (Chat UI) ──► T-28 (Ollama) ──► T-29 (Claude fallback)
                      │
                      ▼
T-30 (Chat API) ──► T-31 (Context Builder) ──► T-32 (Memory)
                      │                           │
                      ▼                           ▼
                 T-35 (PromptLoader) ◄──── T-33 (Consolidation)
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
    T-37 (Briefing)          T-41 (Weekly Review)
          │                       │
          ▼                       ▼
    T-38 (Push)              T-42 (Presentation)

Phase 4 depends on: Phase 3 (PromptLoader, context builder)
    │
    ▼
T-45 (Learning Agent) ──► T-46 (Snapshots) ──► T-48 (Influence Graph)
T-49 (Brave API) ──► T-50 (Radar Cron) ──► T-51 (Match Algorithm)
                                                 │
                                                 ▼
                                          T-53 (Dashboard)
                                                 │
                                          T-54 (Alerts) ──► T-55 (Editor)
T-57 (Context Engine) ◄── depends on Phase 3 memory + context builder
T-60 (Sleep Agent) ──► T-61 (Nudge Agent) ──► T-63 (Scheduler)

Phase 5 depends on: Phase 4 (context engine for AI parsing)
    │
    ▼
T-64 (React Flow) ──► T-65 (DnD Builder) ──► T-66 (Node Types)
                      │
                      ▼
T-68 (Text→Roadmap) ──► T-69 (PDF/Image) ──► T-70 (Templates)
                      │
                      ▼
                 T-72 (Deadline Mode) ──► T-73 (Weekly Check)

Phase 6 is mostly independent (depends only on Phase 1 framework)
T-76 (Income) ──► T-80 (Weekly Income Email)
T-81 (Projects) ──► T-84 (GitHub API)
T-87 (Academics) ──► T-90 (At-risk Alerts)
T-92 (Habits) ──► T-94 (Streaks) ──► T-96 (Reminders)

Phase 7 depends on: Phase 3 (notifications), Phase 6 (habits)
T-98 (Push) ──► T-99 (Email) ──► T-100 (SMS)
T-101 (Sleep) ──► T-103 (Task adjustment)
T-104 (Time) ──► T-105 (Pomodoro) ──► T-107 (Calendar)

Phase 8 depends on: All Phase 1-7
T-109 (PWA) ──► T-110 (Offline) ──► T-111 (Sync)
T-113 (Voice) ──► T-114 (Mobile) ──► T-115 (Export)

Phase 9 depends on: Phase 8 (stable release candidate)
T-119 (GitHub) ──► T-123 (CI/CD) ──► T-125 (Video) ──► T-126 (Launch)
T-129 (Sharing) ──► T-132 (Feature voting) ──► T-136 (Plugin API)
```

### Critical Path

The **critical path** (longest chain of dependent tasks) determines minimum project duration:

```
T-01 → T-04 → T-05 → T-06/07/08 → T-09 → T-13 → 
Phase 2 (T-15 → T-16 → T-24) →
Phase 3 (T-27 → T-28 → T-30 → T-31 → T-32 → T-35 → T-37 → T-38) →
Phase 4 (T-49 → T-50 → T-51 → T-53 → T-54) →
Phase 5 (T-64 → T-65 → T-68 → T-72) →
Phase 8 (T-109 → T-110 → T-111) →
Phase 9 (T-119 → T-123 → T-125 → T-126)

Minimum duration (critical path, no slack): ~32 weeks
With phase overlap and parallel work: ~40 weeks
With exam buffer and contingency: ~48 weeks
```

---

## 15. Release Milestones & Timeline

### Milestone Schedule

| Milestone | Date | Phase | Deliverable | Verification Criteria |
|---|---|---|---|---|
| **M1: Auth + Tasks** | Week 2 | P1 | Working login + task CRUD | Can create, edit, complete, delete tasks |
| **M2: Courses + Goals** | Week 3 | P1 | Course + goal tracking | Can add courses with progress; goals with milestones |
| **M3: Full Dashboard** | Week 3 | P1 | Dashboard with all overviews | All modules visible on dashboard |
| **M4: Content Capture** | Week 6 | P2 | YouTube + Resources + Ideas save | Can save from extension, view in vault |
| **M5: ARIA Chat** | Week 8 | P3 | AI chat with memory | ARIA responds, remembers user info |
| **M6: Daily Briefing** | Week 9 | P3 | 7 AM AI briefing | Briefing generated, delivered, tracked |
| **M7: Weekly Review** | Week 10 | P3 | Sunday AI review | Review generated with narrative |
| **M8: ALPHA** | Week 10 | End P3 | All 15 modules + basic AI | 30 tests pass, dogfooding starts |
| **M9: Opportunity Radar** | Week 13 | P4 | Daily opportunity scans | Radar finds ≥3 relevant matches/day |
| **M10: Context Engine** | Week 14 | P4 | Full context assembly | AI responses include user context |
| **M11: Sleep + Nudge** | Week 15 | P4 | Automated sleep/nudge agents | Wind-down at 9:30 PM, nudges at 6 PM |
| **M12: BETA** | Week 15 | End P4 | Advanced AI complete | All 8 agents operational, 30+ tests |
| **M13: Roadmap Builder** | Week 18 | P5 | Visual + AI roadmap | Drag-drop roadmap, text→roadmap works |
| **M14: Income + Projects** | Week 22 | P6 | Income/project tracking | Income logged, project phases tracked |
| **M15: Academics + CGPA** | Week 24 | P6 | Academic planning | CGPA projection within 0.2 of actual |
| **M16: Habits + Streaks** | Week 26 | P6 | Habit engine | Streak tracking, consistency reports |
| **M17: Monitoring Suite** | Week 30 | P7 | Time/sleep/reminder system | Multi-channel reminders, all tracking |
| **M18: PWA + Offline** | Week 31 | P8 | Production-ready PWA | Lighthouse >90, offline CRUD works |
| **M19: GA CANDIDATE** | Week 31 | End P8 | Stable release candidate | All tests pass, security audit OK |
| **M20: PUBLIC LAUNCH** | Week 33 | P9 | GitHub public release | README, demo, deploy guide ready |
| **M21: GA** | Week 36 | End P9 | General availability | Community infrastructure live |

### Timeline Visualization

```
2026                                       2027
Jul │ Aug │ Sep │ Oct │ Nov │ Dec │ Jan │ Feb │ Mar │ Apr │ May │ Jun
───┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────
 ██│  ██ │     │     │     │     │     │     │     │     │     │     Phase 1
   │  ██ │ ██  │     │     │     │     │     │     │     │     │     Phase 2
   │     │ ██  │ ██  │     │     │     │     │     │     │     │     Phase 3
   │     │     │ ██  │ ██  │     │     │     │     │     │     │     Phase 4
   │     │     │     │ ██  │ ██  │     │     │     │     │     │     Phase 5
   │     │     │     │     │     │ ██  │ ████│     │     │     │     Phase 6
   │     │     │     │     │     │     │ ██  │ ██  │     │     │     Phase 7
   │     │     │     │     │     │     │     │ ██  │     │     │     Phase 8
   │     │     │     │     │     │     │     │     │ ████│ ██  │     Phase 9
   │     │     │     │     │     │     │     │     │     │ ██  │ ██  Buffer

 ◆M1   ◆M4   ◆M8   ◆M12  ◆M13       ◆M16  ◆M18  ◆M19  ◆M20       ◆M21
         ◆M3        ◆M11      ◆M14   ◆M17        │                 │
      ◆M2   ◆M7         ◆M10      ◆M15       ◆M18                 │
   ◆M5 ◆M6         │◆M9                                            │
   │    │   ALPHA   BETA   │            GA    GA CAND  PUBLIC      GA
   │    │   ◆M8     ◆M12   │            CAND  ◆M19    LAUNCH      ◆M21
   │    │                  │                  │       ◆M20
```

---

## 16. Alpha / Beta / GA Timeline

### Alpha (End of Week 10 — Sep 2026)

| Attribute | Description |
|---|---|
| **Purpose** | Internal validation — dogfood the system |
| **Audience** | Developer only + 2-3 close friends |
| **Feature set** | All 15 modules operational; basic ARIA chat with memory; daily briefing; weekly review |
| **Quality bar** | Functional but rough. AI responses may be imperfect. UI not fully polished. |
| **Known limitations** | No opportunity radar, no roadmap engine, no offline, no mobile |
| **Success criteria** | Developer uses system daily for 2 consecutive weeks |
| **Feedback loop** | Personal experience drives bug fixes and feature adjustments |
| **Communication** | No public announcements |

### Beta (End of Week 15 — Nov 2026)

| Attribute | Description |
|---|---|
| **Purpose** | Extended validation — limited external testing |
| **Audience** | 5-10 BTech CSE friends and classmates |
| **Feature set** | Alpha + opportunity radar, context engine, learning agent, sleep agent, nudge agent |
| **Quality bar** | All features functional. AI responses are consistent. UI is coherent. |
| **Known limitations** | No roadmap engine v1, no income/project tracking, no offline |
| **Success criteria** | >60% user retention after 2 weeks; morning briefing read rate >70% |
| **Feedback collection** | Structured feedback form + weekly check-in calls |
| **NDA required?** | No (open-source), but not actively promoted |
| **Communication** | Private Discord channel |

### GA Candidate (End of Week 31 — Mar 2027)

| Attribute | Description |
|---|---|
| **Purpose** | Production readiness validation |
| **Audience** | 20-50 users (invite-only waitlist) |
| **Feature set** | Complete feature set: all 15 modules, all 8 agents, roadmap engine, monitoring, PWA offline |
| **Quality bar** | Lighthouse >90, all tests passing, security audit complete, 99.9% uptime target |
| **Known limitations** | No mobile app, no browser extension v2, no community features |
| **Success criteria** | 30-day retention >60%; NPS >30; zero security incidents |
| **Load testing** | Simulate 100 concurrent users on Railway free tier |

### GA (End of Week 36 — May 2027)

| Attribute | Description |
|---|---|
| **Purpose** | Public general availability |
| **Audience** | All BTech CSE students (unrestricted) |
| **Feature set** | GA Candidate + public GitHub, collaboration features, community infrastructure |
| **Quality bar** | Production-ready. CI/CD green. Documentation complete. |
| **Support** | GitHub issues + Discord community |
| **Marketing** | Product Hunt, Hacker News, Reddit launch |

---

## 17. Feature Flags & Gradual Rollout Plan

### Feature Flag Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  FEATURE FLAG SYSTEM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Environment variables + Supabase user_preferences:            │
│                                                                 │
│  # Global flags (env)                                           │
│  FEATURE_OPPORTUNITY_RADAR=true                                 │
│  FEATURE_ROADMAP_ENGINE=false                                   │
│  FEATURE_AI_BRIEFING=true                                       │
│                                                                 │
│  # User-level overrides (user_preferences table)               │
│  { "feature_flags": {                                           │
│      "roadmap_engine": true,         # Beta tester early access │
│      "ai_briefing": false,           # User opted out           │
│      "opportunity_radar": true                                  │
│  }}                                                             │
│                                                                 │
│  # Rollout percentages (controlled by env)                     │
│  FEATURE_RADAR_ROLLOUT=0.1     # 10% of users                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Feature Flag Inventory

| Flag | Type | Default | Rollout Schedule | Rollback Plan |
|---|---|---|---|---|
| `core_modules` | Global | ON | Always on | N/A |
| `content_capture` | Global | ON | Phase 2+ | Always on after Phase 2 |
| `aria_chat` | Global | ON | Phase 3+ | Disable → fallback to command-line |
| `daily_briefing` | Global | ON | Phase 3+ | Disable → static checklist email |
| `weekly_review` | Global | ON | Phase 3+ | Disable → manual review template |
| `opportunity_radar` | Global → User | OFF → 10% rollout | Phase 4: 10% → Phase 5: 50% → Phase 6: 100% | Set FEATURE_RADAR_ROLLOUT=0 |
| `learning_agent` | Global | OFF | Phase 4 (requires 3 months data) | Disable → stats dashboard |
| `roadmap_engine` | User | OFF | Beta testers → 50% → 100% | Disable → static planning docs |
| `sleep_agent` | Global | OFF → ON | Phase 4: opt-in → Phase 5: 50% → Phase 6: 100% | Disable wind-down messages |
| `nudge_agent` | Global | OFF → ON | Phase 4: opt-in → Phase 5: 100% | Disable → P0 emails only |
| `pwa_offline` | Global | OFF → ON | Phase 8: beta → Phase 9: 100% | Service worker rollback |
| `voice_input` | User | OFF | Phase 8: opt-in | Disable → keyboard only |
| `collaboration` | User | OFF | Phase 9: beta → opt-in | Remove share buttons |
| `plugin_system` | User | OFF | Year 2 | Flag off → no plugin loading |

### Rollout Decision Framework

For each feature, rollout proceeds through these stages:

```
Stage 0 — Development:        Flag=OFF, only developer can enable locally
Stage 1 — Internal Dogfood:   Flag=ON for developer, OFF for everyone else
Stage 2 — Closed Beta:        Flag=ON for 5-10 test users (user-level override)
Stage 3 — Percentage Rollout: Flag=ON for X% of users (env variable)
Stage 4 — Full Rollout:       Flag=ON for 100% of users
Stage 5 — Lock:               Flag removed, feature is permanent
```

### Kill Switch Policy

Any feature can be disabled immediately if:
- P95 response time increases by >50%
- Error rate exceeds 5%
- AI API costs exceed monthly budget by >2x
- User complaints about the feature exceed 3 per week

---

## 18. Past Roadmap Accuracy & Lessons Learned

### Retrospective on Previous Roadmap Versions

| Prediction | Actual | Variance | Lesson Learned |
|---|---|---|---|
| 17-week build plan | Extended to 36+ weeks | +110% | Underestimated AI integration complexity by 2x |
| Phase 1 (2 weeks) | Took 3 weeks | +50% | Database schema design + RLS requires dedicated time |
| Phase 2 (2 weeks) | Took 3 weeks | +50% | Browser extension + AI summary integration is non-trivial |
| Phase 3 (2 weeks) | Took 4 weeks | +100% | Ollama integration has significant debugging overhead |
| "All 8 agents in Phase 3" | Split into Phase 3 + 4 | — | Agent prompts need independent iteration cycles |
| Solo development velocity | 15 hrs/week → 10 hrs | -33% | Overestimated available time — exam weeks are real |
| Feature complexity estimates | -50% to +200% | High variance | CRUD features were overestimated; AI features were underestimated |

### Key Lessons Applied to This Roadmap

| Lesson | Applied Change |
|---|---|
| **AI features need 2x-3x buffer** | Phase 3 (Core AI) was 50 hrs. Phase 4 (Advanced AI) was 55 hrs. Previously these were estimated at 30 hrs total. |
| **Prompt engineering is a separate skill** | Dedicated time for prompt file creation and validation. Added prompt validation CI job. |
| **Dogfooding reveals 50% of bugs** | No phase is "done" until the developer has used it for 3+ days personally. |
| **Exam weeks kill velocity** | Added 4 exam buffer weeks. Phase 6 (Jan-Feb) has lighter schedule because of semester exams. |
| **Feature creep is the biggest risk** | Explicit "NOT planned" section (Section 21). Every new feature must pass the "builder test." |
| **Documentation takes real time** | Added 25 hours for documentation across Phase 9. Previously underestimated at 5 hours. |
| **Community management is full-time** | Phase 9 is 50 hours for public release. Previous estimate was "just make repo public." |

---

## 19. Roadmap Update Cadence & Process

### Update Cadence

| Frequency | Activity | Participants | Output |
|---|---|---|---|
| **Weekly** | Task-level progress check | Developer (solo) | Updated task status in project board |
| **Monthly** | Phase boundary review | Developer | Phase completion check → next phase start |
| **Quarterly** | Full roadmap review | Developer (+ early testers) | Updated roadmap doc, priority adjustments |
| **Per Phase** | Lessons learned capture | Developer | Phase retrospective notes → AGENTS.md updates |

### Roadmap Update Process

```
START: Quarterly Review
  │
  ▼
Step 1: Review past quarter
  ├── Compare planned vs actual milestones
  ├── Capture lessons learned (Section 18)
  └── Calculate velocity (hours completed vs planned)
  │
  ▼
Step 2: Assess current state
  ├── Which features are live and stable?
  ├── Which features need rework?
  ├── Which dependencies changed?
  └── Has user feedback changed priorities?
  │
  ▼
Step 3: Adjust next quarter
  ├── Reprioritize based on lessons + feedback
  ├── Add/remove features based on "builder test"
  ├── Update effort estimates with actual velocity data
  └── Shift timeline if necessary (communicate changes)
  │
  ▼
Step 4: Document changes
  ├── Update Roadmap.md with new quarterly view
  ├── Bump version number
  ├── Update revision history
  └── Commit to repository
  │
  ▼
Step 5: Notify stakeholders
  ├── GitHub discussion post (post-GA)
  ├── Discord announcement (post-GA)
  └── Update project board with new tasks
  │
  ▼
END: Next quarter begins
```

### Decision-Making Matrix for Scope Changes

When considering adding a feature to the roadmap:

```
┌─────────────────────────────────────────────────────────────────┐
│  SCOPE CHANGE DECISION MATRIX                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Question                                    Yes     No        │
│  ──────────────────────────────────────────────────────────    │
│  1. Does this help a student build something?   +2      -2     │
│  2. Does it work offline?                      +1      0      │
│  3. Is it free-tier infrastructure?            +1      -1     │
│  4. Does it integrate with existing modules?   +1      0      │
│  5. Will the developer personally use it?      +2      0      │
│  6. Can it be built in <20 hours?              +1      -1     │
│  7. Does it have a non-AI fallback?            +1      -1     │
│  8. Is it student-specific?                    +1      0      │
│                                                                 │
│  Score ≥ 5: ADD to roadmap                                    │
│  Score 2-4: CONSIDER for next quarter                          │
│  Score < 2: DEFER or reject                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 20. Risk Register for Timeline

### Risk Assessment

| ID | Risk | Probability | Impact | Risk Score | Mitigation |
|---|---|---|---|---|---|
| R-T01 | **Developer illness/injury** (1-2 weeks off) | Medium | High | 12 | Add 4 exam buffer weeks. Use them as contingency. |
| R-T02 | **Ollama breaking changes** (model update breaks API) | Medium | High | 12 | Pin Ollama version. Test upgrades in CI. Keep fallback client tested. |
| R-T03 | **Supabase free tier limits hit** (DB full, bandwidth exceeded) | Medium | High | 12 | Paginate all queries. Cache aggressively. Have migration script ready. |
| R-T04 | **Google OAuth breaking change** (auth flow change) | Low | Critical | 8 | Monitor Google Identity docs. Alternative: Magic link auth. |
| R-T05 | **Exam period reduced output** (4 weeks at 50% capacity) | High | Medium | 12 | Phase 6 (light) scheduled during Jan-Feb. Buffer built in. |
| R-T06 | **Browser extension rejected** (Chrome Web Store policy) | Medium | Medium | 9 | Firefox-first release. Chrome sideload guide. Cross-browser WXT. |
| R-T07 | **AI feature quality too low** (user disappointment) | Medium | High | 12 | Gradual rollout with feature flags. Algorithmic fallback always available. |
| R-T08 | **Public release backlash** (security concerns, feature requests) | Low | Medium | 6 | Transparent security docs. Feature voting pipeline. Clear scope (Section 21). |
| R-T09 | **Dependency deprecation** (Next.js 14→15, Tailwind v3→v4) | Medium | Medium | 9 | Pin major versions. Dedicate 1 week/year for upgrade. |
| R-T10 | **Motivation/interest decline** (solo developer) | Medium | Critical | 12 | Visible progress tracking. Community engagement post-launch. Reduce scope if needed. |

### Risk Matrix

```
PROBABILITY
    │
High    │         R-T05               R-T01, R-T02, R-T03
        │                              R-T07, R-T10
Medium  │   R-T09                      │
        │         │                    │
Low     │         R-T06, R-T08         R-T04
        │         │                    │
        └──────────────────────────────────────────► IMPACT
            Low            Medium         Critical
```

**Mitigation priority:** R-T01, R-T02, R-T03, R-T07, R-T10 — these require active monitoring and contingency plans.

### Timeline Contingency Plan

| Scenario | Probability | Impact | Response |
|---|---|---|---|
| Best case (+15% velocity) | 15% | Finish 5 weeks early | Use extra time for polish + testing |
| Expected case | 50% | On schedule | Follow roadmap as planned |
| Moderate delay (+25% time) | 25% | 9 weeks late | Cut Phase 9 features. Delay GA by 1 quarter. |
| Severe delay (+50% time) | 10% | 18 weeks late | Cut Phase 5 (Roadmap Engine) to Q3 2027. Prioritize core features. |

---

## 21. What's Explicitly NOT Planned

### Out of Scope (Q3 2026 — Q2 2027)

| Feature | Reason for Exclusion |
|---|---|
| **Multi-user / team collaboration** | Product is personal. ADR-002 explicitly avoids multi-user. Single-user architecture. |
| **Real-time collaborative editing** | Requires WebSocket infrastructure, conflict resolution, multi-user auth. Massive scope increase. |
| **Native iOS app** | React Native first (Android + iOS). Native Swift is too much overhead for solo developer. |
| **Desktop app (Electron/Tauri)** | PWA covers 90% of desktop use cases. Desktop app deferred to Year 2. |
| **End-to-end encryption** | Requires significant crypto engineering. RLS + HTTPS is sufficient for current threat model. |
| **AI model training / fine-tuning** | Requires GPU resources, datasets, ML expertise. Prompt engineering + Ollama is sufficient. |
| **Social network / feed** | Philosophical decision against social features. System is personal. |
| **Marketplace / payments** | Community marketplace deferred to Year 3. Stripe integration is significant effort. |
| **Video conferencing / meetings** | Not a communication tool. No video, no voice calls, no screen sharing. |
| **File storage / document editor** | Use Google Docs / Notion for documents. We link, not create. |
| **Email client** | Use Gmail / Outlook. We send notifications only. |
| **Calendar replacement** | Google Calendar sync (read + write). We do not build a calendar UI from scratch. |
| **Machine learning / recommendation system** | Rule-based matching + LLM reasoning is sufficient. No custom ML models. |
| **Blockchain / Web3 integration** | No relevant use case for student productivity. Avoid hype-driven features. |
| **Gamification / leaderboards** | Anti-pattern. Honest metrics over fake motivation. |
| **AI voice assistant (always-on)** | Requires significant audio pipeline. Push-to-talk is sufficient for now. |
| **Browser extension: auto-fill, form management** | Feature creep. Extension is for save only. |
| **Integration with college ERP systems** | Each college has a different ERP. Reverse engineering is unsustainable. Manual entry instead. |

### Decisions That Are Reversible (Might Change in Year 2)

- **Mobile app**: Will be added in Year 2 (Q3 2027)
- **Plugin system**: Will be added in Year 3 (Q3 2028)
- **Enterprise features**: Will be added if institutional interest emerges
- **Multi-language support**: Will be added if non-English users adopt the system

### Guiding Question for Every Feature

**"Does this help a BTech CSE student build something real?"**

If the answer is no — or unclear — the feature is not planned.

---

## 22. Appendices

### Appendix A: Feature Flag Technical Specification

```typescript
// Feature flag configuration type
interface FeatureFlags {
  core_modules: boolean          // Always true
  content_capture: boolean       // Phase 2+
  aria_chat: boolean             // Phase 3+
  daily_briefing: boolean        // Phase 3+
  weekly_review: boolean         // Phase 3+
  opportunity_radar: boolean     // Phase 4+ (gradual rollout)
  learning_agent: boolean        // Phase 4+ (requires data)
  roadmap_engine: boolean        // Phase 5+
  sleep_agent: boolean           // Phase 4+
  nudge_agent: boolean           // Phase 4+
  pwa_offline: boolean           // Phase 8+
  voice_input: boolean           // Phase 8+
  collaboration: boolean         // Phase 9+
  plugin_system: boolean         // Year 2
}

// User-level override from user_preferences
type UserFlagOverrides = Partial<FeatureFlags>

// Global rollout from environment
interface RolloutConfig {
  radar_rollout: number       // 0.0 to 1.0
  roadmap_rollout: number     // 0.0 to 1.0
  sleep_agent_rollout: number // 0.0 to 1.0
}
```

### Appendix B: Velocity Tracking Template

```markdown
# Weekly Velocity Report — Week [N]

## Current Phase: [Phase Name]

### Hours Logged
| Day | Hours | Tasks Completed |
|---|---|---|
| Mon | 2 | T-XX, T-YY |
| Tue | 3 | T-ZZ |
| Wed | 0 | (exam prep) |
| Thu | 2.5 | T-AA |
| Fri | 3 | T-BB, T-CC |
| Sat | 4 | T-DD |
| Sun | 1 | Documentation |
| **Total** | **15.5** | **8 tasks** |

### Planned vs Actual
- Planned: 15 hours, 10 tasks
- Actual: 15.5 hours, 8 tasks
- Variance: +0.5 hours, -2 tasks

### Blockers
- T-YY requires Supabase docs review (resolved Friday)
- T-CC had unexpected CORS issue (fixed with middleware)

### Adjustments
- T-DD estimated at 2h, took 4h. Will update future estimates.
- Next week is exam week — plan for 8 hours.

### Key Learnings
- [Lesson learned this week]
```

### Appendix C: Reference Documents

| Document | Location | Relevance |
|---|---|---|
| Product Vision | `docs/product/00_ProjectVision.md` | Long-term direction alignment |
| BRD | `docs/product/03_BRD.md` | Business requirements, success criteria |
| PRD / SRS | `docs/product/04_SRS.md` | Functional specifications |
| Architecture | `docs/engineering/12_Architecture.md` | Technical architecture decisions |
| ADR-001 through ADR-008 | `docs/engineering/adr/` | Architecture Decision Records |
| Agent Architecture | `docs/ai/20_Agent.md` | AI agent design and orchestration |
| Design System | `docs/design/10_DesignSystem.md` | UI/UX design tokens and components |
| Build & Test Commands | `AGENTS.md` Section 3 | Development workflow |
| CI/CD Pipeline | `.github/workflows/ci.yml` | Automated build and test |
