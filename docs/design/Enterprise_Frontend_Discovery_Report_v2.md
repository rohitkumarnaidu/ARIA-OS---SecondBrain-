# Enterprise Frontend Discovery Report v2.0 — Second Brain OS (ARIA OS)

---

## Document Control

| Field | Value |
|---|---|
| Document ID | SB-DISCOVERY-002 |
| Version | 2.0.0 |
| Status | Active |
| Classification | Internal — Design & Engineering Reference |
| Target Audience | Designers, Frontend Engineers, AI Engineers, Product Team, QA, DevOps |
| Last Updated | 2026-06-11 |
| Review Cycle | Quarterly |
| Total Sections | 47 |
| Total Pages Est. | 85+ |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Product Understanding Report](#2-product-understanding-report)
3. [Core Product Vision](#3-core-product-vision)
4. [Core Product Goals](#4-core-product-goals)
5. [Core User Problems](#5-core-user-problems)
6. [Product Positioning](#6-product-positioning)
7. [Product Differentiation](#7-product-differentiation)
8. [Core Product Domains](#8-core-product-domains)
9. [Product Capabilities](#9-product-capabilities)
10. [User Types](#10-user-types)
11. [Core User Journeys](#11-core-user-journeys)
12. [Product Workflow Architecture](#12-product-workflow-architecture)
13. [Data Flow Architecture](#13-data-flow-architecture)
14. [AI Flow Architecture](#14-ai-flow-architecture)
15. [Agent Flow Architecture](#15-agent-flow-architecture)
16. [Dashboard Strategy](#16-dashboard-strategy)
17. [Navigation Strategy](#17-navigation-strategy)
18. [Search Strategy](#18-search-strategy)
19. [Command Center Strategy](#19-command-center-strategy)
20. [Analytics Strategy](#20-analytics-strategy)
21. [Knowledge Strategy](#21-knowledge-strategy)
22. [Learning Strategy](#22-learning-strategy)
23. [Opportunity Strategy](#23-opportunity-strategy)
24. [AI Assistant Strategy](#24-ai-assistant-strategy)
25. **→ NEW: Information Architecture Deep Dive**
26. **→ NEW: AI UX Patterns Catalog**
27. **→ NEW: Agentic UX Patterns**
28. **→ NEW: Render Strategy (CSR/SSR/ISR/RSC)**
29. **→ NEW: Frontend Performance Budget**
30. **→ NEW: Frontend Security Strategy**
31. **→ NEW: Testing Strategy & Quality Gates**
32. **→ NEW: Error Handling & Recovery Architecture**
33. **→ NEW: State Management & Optimistic Update Patterns**
34. **→ NEW: Notification Architecture**
35. **→ NEW: Data Visualization Component Strategy**
36. **→ NEW: Frontend CI/CD Pipeline**
37. **→ NEW: Monitoring & Observability**
38. **→ NEW: Feature Flags & A/B Testing Framework**
39. **→ NEW: Loading / Empty / Error State Catalog**
40. [Mobile Strategy](#40-mobile-strategy)
41. [Tablet Strategy](#41-tablet-strategy)
42. [Desktop Strategy](#42-desktop-strategy)
43. [Offline Strategy](#43-offline-strategy)
44. [Realtime Strategy](#44-realtime-strategy)
45. [Accessibility Strategy](#45-accessibility-strategy)
46. [Product, UX & Technical Risks (Expanded)](#46-product-ux--technical-risks-expanded)
47. [Design & Innovation Opportunities (Expanded)](#47-design--innovation-opportunities-expanded)
48. [Recommended Direction (Product, Frontend, Design, AI)](#48-recommended-direction-product-frontend-design-ai)
49. [Research References](#49-research-references)
50. [Appendices](#50-appendices)

---

> **Note**: Sections 1-24 (pages 1-42) remain as defined in v1.0.0 (SB-DISCOVERY-001). This v2.0.0 document extends the original with 11 new enterprise-depth sections (25-35) and 5 expanded strategic sections (36-50). The total represents a complete enterprise-level discovery document.

---

## 25. Information Architecture Deep Dive

### 25.1 Content Inventory — Complete Module Taxonomy

| Module | Label | Content Types | Relationships | Data Volume (Est.) |
|---|---|---|---|---|
| Dashboard | Home | Briefing cards, score widgets, heatmap, activity feed | Aggregates from all modules | ~50 items |
| Tasks | Tasks | Tasks, subtasks, task dependencies, recurring patterns | → Goals, Courses, Projects, Time | ~500 active |
| Courses | Courses | Courses, modules, progress snapshots, study targets | → Tasks (study tasks), Skills, Goals | ~20 active |
| Goals | Goals | Goals, milestones (roadmap nodes), goal dependencies | → Tasks, Courses, Projects, Income | ~10 active |
| Habits | Habits | Habit definitions, habit logs, streak records | → Goals, Dashboard | ~15 active |
| Sleep | Sleep | Sleep logs, sleep score history, sleep debt | → Dashboard, Task scheduling | ~365/year |
| Income | Income | Income entries, income sources, hourly rates | → Projects, Skills, Goals | ~100/year |
| Projects | Projects | Projects, phases, blockers, GitHub links | → Tasks, Income, Goals | ~5 active |
| Ideas | Ideas | Ideas, status pipeline entries, AI analysis | → Projects, Resources, Goals | ~50/year |
| Resources | Resources | Articles, books, repos, tools, papers, threads | → Goals, Courses, Projects | ~200/year |
| YouTube | YouTube Vault | Saved videos, AI summaries, watch history | → Goals, Courses, Resources | ~100/year |
| Opportunities | Opportunities | Scanned opportunities, applications, matches | → Skills, Goals, Projects | ~500/year |
| Time | Time Tracking | Time entries, Pomodoro sessions, deep work blocks | → Tasks, Projects, Income | ~500/month |
| Academics | Academics | Semester plans, CGPA, subjects, exam schedules | → Courses, Tasks | ~40/semester |
| Chat | ARIA | Chat messages, AI responses, action logs | → All modules (via actions) | ~1000/month |
| Automation | Automation | Cron job status, trigger logs, execution history | → All agents | ~50 logs/day |

### 25.2 Taxonomy Design — Tag & Category System

**Entity Tags (applied to any content type):**
```
Topic: DSA, WebDev, AI/ML, DevOps, Security, DBMS, OS, Networks
Skill: React, Python, Go, Docker, SQL, TypeScript, AWS
Status: Active, Archived, Draft, Completed, Stalled
Priority: Urgent, High, Medium, Low
Effort: Quick (<30m), Medium (2h), Large (1d), Epic (>1d)
Stage: Learning, Building, Earning, Planning
Source: College, Online, Self-taught, Work, Freelance
```

**Cross-module metadata fields (present on all content types):**
```
- id: UUID (primary key)
- user_id: UUID (RLS scope)
- created_at, updated_at: timestamp
- tags: string[] (from taxonomy above)
- linked_goals: UUID[] (optional)
- linked_skills: string[] (auto-extracted by AI)
- ai_summary: text (auto-generated)
- archived: boolean
```

### 25.3 Wayfinding Model

```
Global Wayfinding:
  Cmd+K Command Palette → any module, action, or item
  Sidebar → module-level navigation
  Breadcrumbs → deep page orientation
  Quick Switcher (Cmd+Shift+K) → recents + favorites

Module Wayfinding:
  Tab Bar → view switching (list/kanban/calendar/detail)
  Search Bar → module-scoped search
  Filter Bar → status, priority, date, tags
  Sort Controls → date, priority, title, status

Contextual Wayfinding:
  Related Items → AI-suggested related tasks, resources, ideas
  Back Navigation → previous module context
  Deep Links → shareable URLs for any item
  Notification Links → click → specific item
```

### 25.4 Metadata Schema Per Module

Each module has a standardized metadata footer that appears on detail views:

```
Created: 2 days ago by Quick Capture
Last Modified: 1 hour ago
Linked To: Node.js Course, Full-Stack Goal
Tags: WebDev, React, Tutorial
AI Summary: This resource covers React hooks...
```

---

## 26. AI UX Patterns Catalog

### 26.1 AI Interaction Initiative Spectrum

| Level | Name | Description | Example in ARIA OS | UX Treatment |
|---|---|---|---|---|
| 0 | **Manual** | User initiates, AI does nothing | Raw task creation | Standard form |
| 1 | **Suggestive** | User initiates, AI suggests | Task creation → AI suggests priority | Subtle pill: "Suggested: High" |
| 2 | **Pre-fill** | User initiates, AI pre-fills | Quick Capture → AI detects type + fills fields | Animated fill, editable |
| 3 | **Auto-execute** | User initiates, AI completes silently | Add course → AI auto-generates study tasks | Toast confirmation |
| 4 | **Proactive Suggest** | AI initiates, user confirms | 6 PM: "Behind on Node.js. Add 30min study?" | Notification + one-tap |
| 5 | **Proactive Execute** | AI initiates, executes silently | 7 AM: briefing generated and pushed | Notification only |
| 6 | **Autonomous** | AI acts independently, informs user | Opportunity radar scans, scores, saves | Daily digest |

**Design rule**: Every AI action must have visible agency — user must always know what the AI did, is doing, or will do. Level 5+ requires an audit trail.

### 26.2 Confidence Disclosure Patterns

| AI Confidence | Visual Treatment | User Action |
|---|---|---|
| >90% | Solid state, no indicator | Auto-accept, undo available |
| 70-90% | Subtle "AI suggested" badge | Quick accept/dismiss |
| 50-70% | "Maybe?" indicator + alternatives shown | Review required |
| <50% | Gray, "Couldn't determine" message | Manual input required |
| Error | Red state, fallback value shown | User must correct |

### 26.3 Progressive AI Reveal

AI features should progressively reveal themselves to avoid overwhelming new users:

| Day | AI Feature Revealed | Trigger |
|---|---|---|
| 1 | Quick Capture type detection | First capture |
| 2 | Task priority suggestion | First task creation |
| 3 | Morning Briefing | 7 AM next day |
| 5 | Course study task auto-generation | First course added |
| 7 | Opportunity Radar | First week scan |
| 10 | AI chat (ARIA) | User visits /chat |
| 14 | Memory extraction | 2+ weeks of data |
| 21 | Pattern detection | 3+ weeks of data |
| 30 | Weekly Review | First full month |

### 26.4 AI Feedback Loops

Every AI interaction should have an explicit feedback mechanism:

```
User → AI Action → Outcome → Feedback → Model Improvement
```

| Feedback Type | UX Pattern | Data Collected |
|---|---|---|
| Implicit (accept) | User clicks "Accept" | Confirmed correct |
| Implicit (ignore) | User dismisses / does nothing | Uncertain — use with decay |
| Implicit (override) | User changes AI value | Incorrect — log correction |
| Explicit (positive) | Thumbs up / "Good suggestion" | Training signal |
| Explicit (negative) | Thumbs down / "Not helpful" | Training signal + trigger review |
| Explicit (report) | "This was wrong" + reason | Escalation to prompt review |

---

## 27. Agentic UX Patterns

### 27.1 Agent Initiative Continuum

```
User-Driven ──────────────────────────────────────── System-Driven
     │              │              │              │
   Manual        Suggestive     Proactive      Autonomous
   (User asks)   (AI suggests)  (AI offers)    (AI acts)
```

**Agent visibility rules:**
- **Service agents** (Memory, Learning, Analytics) operate at level 4-6 — user sees results, not process
- **Cron agents** (Briefing, Radar, Nudge) operate at level 5 — user sees delivery, not execution
- **Interactive agents** (Planner, Career, Roadmap) operate at level 1-3 — user must initiate, AI assists
- **ARIA** operates at all levels depending on context — user can query, command, or let ARIA suggest

### 27.2 Multi-Agent Orchestration UX

When ARIA dispatches multiple agents for a single user request:

```
User: "What should I focus on today?"
     ↓
ARIA dispatches: Planner + Sleep + Learning + Opportunity (parallel)
     ↓
Results merge into single briefing response
     ↓
User sees: Unified response with agent attribution
           "📋 Tasks (Planner): 3 priority tasks"
           "😴 Sleep (Sleep Agent): Score 78 — light day"
           "📚 Learning (Learning Agent): Study Node.js"
           "🎯 Opportunities (Radar): 2 new matches"
```

**UX rules for multi-agent responses:**
- Each agent's output is visually grouped with: icon + agent name + content
- Responses ordered by user priority (not agent execution order)
- Agents that timed out show gray "unavailable" placeholder
- User can click "Why?" on any agent output to see reasoning

### 27.3 Agent State Visibility

Every agent has 4 visible states that must be communicated to the user:

| State | Visual | UX Treatment |
|---|---|---|
| **Idle** | Gray/dimmed | Not currently active |
| **Processing** | Pulsing glow + "Thinking..." | Show estimated time |
| **Complete** | Solid state with data | Show results with timestamp |
| **Failed** | Red/orange with error | Show fallback or retry button |

**Agent health dashboard** (placed in Automation module):
- Agent list with status indicators
- Last run time, duration, success/failure
- "Run Now" button for manual trigger
- Schedule visualization for cron agents

### 27.4 Agent Collaboration Patterns

| Pattern | Description | Example |
|---|---|---|
| **Pipeline** | Agents execute sequentially, output feeds next | Planner → Learning → Career |
| **Parallel** | Independent agents execute concurrently | Briefing: Planner + Radar + Sleep |
| **Fan-out** | One agent dispatches to many | ARIA → all service agents |
| **Fan-in** | Many agents feed one aggregator | Weekly Review ← all agents |
| **Competitive** | Multiple agents propose, orchestrator selects | Planner proposes 3 schedules, user picks |
| **Supervised** | AI proposes, human approves, AI executes | "I found 3 opportunities. Apply to these?" |

---

## 28. Render Strategy (CSR / SSR / ISR / RSC)

### 28.1 Rendering Method Per Page

| Page | Method | Rationale |
|---|---|---|
| `/` Dashboard | **CSR + ISR (60s)** | Highly personalized, real-time data, but static shell can be cached |
| `/tasks` | **CSR** | Real-time task data, user-specific |
| `/courses` | **CSR** | Course progress is dynamic, user-specific |
| `/goals` | **CSR** | Milestone data is real-time |
| `/habits` | **CSR** | Streak data is per-user |
| `/sleep` | **CSR** | Sleep data is personal |
| `/income` | **CSR** | Financial data, user-specific |
| `/projects` | **CSR** | Project data, user-specific |
| `/ideas` | **CSR** | Idea data, user-specific |
| `/resources` | **CSR** | Resource library, user-specific |
| `/youtube` | **CSR** | User's saved videos |
| `/opportunities` | **CSR** | Personalized matches |
| `/time` | **CSR** | Time entries, user-specific |
| `/academics` | **CSR** | Academic data, user-specific |
| `/chat` | **CSR** | Real-time chat, streaming |
| `/automation` | **CSR** | Agent health, user-specific |
| `/login` | **SSR** | SEO, fast initial load, redirect handling |
| `/offline` | **SSG** | Static offline page, cacheable globally |
| Landing/marketing | **SSR + ISR (1h)** | SEO content with periodic refresh |

### 28.2 Loading Strategy Per Page Type

| Page Type | Initial Load | Subsequent Navigation | Data Refresh |
|---|---|---|---|
| Data-heavy (dashboard) | Skeleton shell → streaming data | Client cache + background refetch | Realtime subscription + interval |
| List (tasks, courses) | Skeleton rows → fade in items | Client cache | Realtime subscription |
| Detail (task detail) | Skeleton detail → content | Client cache | On mount + pull-to-refresh |
| Chat | Empty shell → streaming messages | Conversation history loaded async | WebSocket/SSE |
| Canvas (goals/roadmap) | Loading spinner → React Flow | Previous state cached | On mount + manual save |
| Static (login, landing) | Full HTML → hydrate | N/A | N/A |

### 28.3 Streaming SSR Strategy

For pages that would benefit from progressive rendering (dashboard, chat):

```
Server sends: HTML skeleton → streaming component chunks → client hydrates progressively

Priority order:
1. Shell layout (sidebar, header) — instant
2. Critical data (briefing, today's tasks) — < 1s
3. Secondary data (goals, courses) — < 2s
4. Analytics data (heatmap, stats) — lazy loaded
5. Non-critical (activity feed, suggestions) — idle load
```

---

## 29. Frontend Performance Budget

### 29.1 Bundle Budget

| Asset | Budget | Current (Est.) | Tool |
|---|---|---|---|
| Total JS (all pages) | <400KB gzip | ~250KB | next/bundle-analyzer |
| Per-page JS | <150KB gzip | ~80KB (avg) | Webpack Bundle Analyzer |
| CSS (all) | <50KB gzip | ~35KB | PurgeCSS + Tailwind |
| Fonts (3 families) | <60KB | ~45KB (subset) | next/font |
| Images/icons | <100KB | ~30KB (Lucide tree-shaken) | next/image, SVGR |
| **Total per page** | **<300KB gzip** | **~190KB (est.)** | Lighthouse |

### 29.2 Performance Budget

| Metric | Target (Desktop) | Target (Mobile) | Tool |
|---|---|---|---|
| First Contentful Paint (FCP) | <1.0s | <1.5s | Lighthouse |
| Largest Contentful Paint (LCP) | <2.0s | <2.5s | Lighthouse |
| Total Blocking Time (TBT) | <100ms | <200ms | Lighthouse |
| Cumulative Layout Shift (CLS) | <0.05 | <0.05 | Lighthouse |
| Time to Interactive (TTI) | <2.0s | <3.0s | Lighthouse |
| Speed Index | <2.0s | <3.0s | Lighthouse |
| API response (p50) | <200ms | <300ms | Sentry/Vercel |
| API response (p95) | <500ms | <800ms | Sentry/Vercel |
| AI response (p50) | <3s | <5s | Custom instrumentation |
| AI response (p95) | <8s | <12s | Custom instrumentation |
| Offline activation | Instant | Instant | Manual test |
| Background sync | <10s after reconnect | <15s | Custom instrumentation |

### 29.3 Bundle Optimization Rules

1. **Route-based code splitting**: every page route is a separate chunk (Next.js default)
2. **Lazy load**: React Flow, Recharts, heatmap — load only when needed
3. **Dynamic import**: Heavy components (markdown renderer, code highlighter) — `next/dynamic`
4. **Tree-shaking**: Lucide icons are imported individually, not as barrel
5. **Font subsetting**: Syne, DM Sans, JetBrains Mono — latin subset only, `display: swap`
6. **Image optimization**: `next/image` with WebP format, lazy loading
7. **Preload critical**: Fonts, hero images, critical CSS — `<link rel="preload">`
8. **Prefetch likely**: Dashboard → Tasks, Chat (highest probability next pages)

### 29.4 Performance Monitoring

| Tool | What It Monitors | Alert Threshold |
|---|---|---|
| Lighthouse CI | Per-PR bundle size, performance score | < 90 score = block |
| Sentry Performance | API latency, page load, slow transactions | p95 > 1s = alert |
| Web Vitals (JS) | FCP, LCP, CLS, INP in production | Any "poor" rating = alert |
| Bundle Analyzer | Per-branch size comparison | +10% = review required |
| Custom RUM | AI latency, task CRUD latency, search latency | p95 > 2x baseline = alert |

---

## 30. Frontend Security Strategy

### 30.1 Security Threat Model (Frontend)

| Threat | Risk Level | Mitigation |
|---|---|---|
| **XSS (Cross-Site Scripting)** | High | React JSX auto-escapes, DOMPurify for markdown/HTML, CSP headers |
| **CSRF (Cross-Site Request Forgery)** | Medium | Supabase auth handles CSRF, JWT in Authorization header (not cookies) |
| **API Key Exposure** | Critical | All API keys server-side only, VITE_* env vars for public keys only |
| **JWT Token Theft** | High | Short-lived tokens (1h), httpOnly refresh tokens, secure localStorage |
| **Sensitive Data in URL** | Medium | Never pass user_id or tokens in URL params, POST for mutations |
| **Clickjacking** | Low | X-Frame-Options: DENY, CSP frame-ancestors 'none' |
| **CORS Abuse** | Medium | Strict origin validation, per-environment CORS config |
| **npm Dependency Attack** | Medium | Lockfile, Dependabot alerts, Snyk scanning, npm audit in CI |
| **LLM Prompt Injection** | High | Input sanitization, output validation, guardrails prompt, rate limiting |
| **Service Worker Hijack** | Low | Scope-limited SW, no eval in SW, CSP restrict |

### 30.2 Content Security Policy (CSP)

```http
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'unsafe-eval' 'unsafe-inline';  <!-- unsafe-eval for Next.js, revisit -->
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https://img.youtube.com https://*.supabase.co;
  font-src 'self' data:;
  connect-src 'self' https://*.supabase.co https://api.anthropic.com http://localhost:11434;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
```

**CSP deployment strategy**: Report-only mode first (2 weeks), enforce after validation.

### 30.3 Frontend Security Checklist

- [ ] All forms use POST method (not GET for mutations)
- [ ] Supabase JWT stored in memory/auth context, not accessible to JS scope leak
- [ ] `dangerouslySetInnerHTML` never used; markdown rendered via DOMPurify + rehype-sanitize
- [ ] No user data in console.log, error messages, or URL params
- [ ] All external links use `rel="noopener noreferrer"`
- [ ] Service worker scope limited to `/` path
- [ ] Sensitive actions (delete, export) require confirmation (double-click or type "DELETE")
- [ ] Rate limiting on auth endpoints (Supabase handles this)
- [ ] File upload validation (when implemented): type, size, scan

---

## 31. Testing Strategy & Quality Gates

### 31.1 Testing Pyramid

```
        ╱╲
       ╱  ╲          E2E (Cypress/Playwright)
      ╱    ╲         10-15 critical user flows
     ╱──────╲
    ╱        ╲       Integration Tests (React Testing Library)
   ╱          ╲      Component interaction, API mocking, state flows
  ╱────────────╲
 ╱              ╲   Unit Tests (Jest/Vitest)
╱                ╲  Pure functions, hooks, utilities, state logic
╱──────────────────╲
╱  Static Analysis  ╲ TypeScript (strict), ESLint, Prettier
╱────────────────────╲
```

### 31.2 Test Coverage Requirements

| Layer | Coverage Target | Critical Paths |
|---|---|---|
| **Unit (hooks, utils)** | >90% | `useTasks`, `useAuth`, `useLocalStorage`, date utils, format utils |
| **Unit (state)** | >90% | Zustand stores: `useUIStore`, `useTaskStore` |
| **Integration (components)** | >80% | TaskCard, QuickCapture, CourseCard, BriefingCard, ARIA chat input |
| **Integration (forms)** | >80% | Task creation, course creation, habit logging, sleep logging |
| **E2E (critical flows)** | 15 flows | Task CRUD, chat with ARIA, briefing view, opportunity save, offline sync |
| **Visual regression** | Key components | Button, Card, Modal, Heatmap at different states |

### 31.3 Critical E2E Flows

| Flow | Steps | Verification |
|---|---|---|
| **Task creation → completion** | Create task → appears in list → complete → disappears | Task count, completion streak |
| **Quick capture → auto-categorize** | Paste URL → AI detects type → save | Correct module save |
| **Chat → action execution** | "Add task X" → ARIA responds → task appears | Chat response + task list |
| **Daily briefing generation** | Wait for 7AM (or manual trigger) → briefing appears | 6 briefing sections |
| **Opportunity radar → save** | Scan runs → results appear → save opportunity | Opportunity in list |
| **Course → study task generation** | Add course → study tasks auto-created | Task list has study tasks |
| **Offline task creation → sync** | Go offline → create task → come online → task syncs | Task on server |
| **Sleep log → score update** | Log sleep → score updates → dashboard reflects | Score + dashboard |
| **Habit streak → miss detection** | Log habit 5 days → miss → streak resets | Streak counter |
| **Goal → milestone → task generation** | Create goal → add milestone → tasks generated | Milestone + tasks |
| **Project phase transition** | Move project to next phase → blockers check | Phase update |
| **Income log → hourly rate calc** | Log income → rate calculated → dashboard shows | Rate display |
| **Notification → navigation** | Click notification → opens correct page | Page + item loaded |
| **Keyboard shortcut → action** | Cmd+K → type → navigate | Page changes |
| **Voice input → ARIA** | Speak → text appears → response | Chat response |

### 31.4 Quality Gates (CI)

| Gate | Tool | Threshold | Action |
|---|---|---|---|
| TypeScript | `tsc --noEmit` | 0 errors | Block PR |
| Lint | `next lint` | 0 errors, 0 warnings | Block PR |
| Unit Tests | Jest | >90% coverage, 0 failures | Block PR |
| Integration | RTL | >80% coverage, 0 failures | Block PR |
| E2E | Cypress | 100% pass rate | Block PR |
| Accessibility | axe-core | 0 violations | Block PR |
| Bundle Size | bundle-analyzer | Within budget | Warning at +10% |
| Lighthouse | Lighthouse CI | Performance > 90 | Warning |
| Visual Regression | Chromatic/Percy | 0 changes > 5% diff | Review required |

---

## 32. Error Handling & Recovery Architecture

### 32.1 Error Classification

| Class | Description | UX Treatment | Recovery |
|---|---|---|---|
| **Network** | API unreachable, timeout | Offline mode activation + toast | Background sync on reconnect |
| **Auth** | Token expired, unauthorized | Silent refresh → if fails, redirect to login | Refresh token rotation |
| **Validation** | Bad input, missing fields | Inline error on field + toast summary | User corrects input |
| **Server** | 500, 503, rate limited | Generic error message + retry button | Exponential backoff retry |
| **AI** | LLM timeout, bad response | Fallback content + "AI unavailable" indicator | Retry → algorithmic fallback |
| **Storage** | IndexedDB full, quota exceeded | Warning toast + oldest data cleanup suggestion | Auto-clean or user action |
| **Runtime** | JS exception | Error boundary → fallback UI + Sentry report | Refresh or navigate away |

### 32.2 Error Boundary Hierarchy

```
App Root Error Boundary
  ├── Layout Error Boundary (sidebar, header)
  ├── Module Error Boundaries (15 modules, each independent)
  │    ├── Tasks Error Boundary
  │    ├── Courses Error Boundary
  │    └── ...
  ├── Chat Error Boundary
  └── Dashboard Error Boundary (with zone-level recovery)
```

Each error boundary shows:
- **First occurrence**: Subtle inline message + retry button
- **Repeated failure**: "Module temporarily unavailable" + link to report issue
- **Critical failure**: Full-page error + email/Slack report automatically sent

### 32.3 API Error Handling Contract

```typescript
// Frontend API client error handling pattern
interface ApiError {
  status: number
  code: ErrorCode       // 'VALIDATION_ERROR' | 'NOT_FOUND' | 'RATE_LIMITED' | ...
  message: string        // User-friendly
  details?: unknown      // Dev-only, never shown to user
  retryAfter?: number    // For rate limiting
}

// Expected handling per error code:
// 400 → Show validation message inline
// 401 → Attempt token refresh → if fails, redirect
// 403 → Show "no access" toast
// 404 → Show "not found" with search suggestion
// 429 → Show "too fast" toast + disable button for retryAfter seconds
// 500 → Show generic error + retry button
// 503 → Show maintenance banner
```

### 32.4 Offline Error Recovery

```
Error: Network request fails
  → Check if request is in offline-allowed list (GET → serve from cache)
  → If mutation → push to offline queue
  → Show optimistic success in UI
  → When online → replay queue in order
  → Conflict detected → server timestamp wins → show toast
  → Queue item fails → keep in queue, notify user, retry with backoff
```

---

## 33. State Management & Optimistic Update Patterns

### 33.1 State Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Zustand (UI State)                       │
│  sidebarOpen, theme, activeModule, modalState, toastQueue   │
│  Keyboard bindings, navigation history, quick capture state │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────────────┐
│                React Query (Server State)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │  Tasks   │ │ Courses  │ │  Goals   │ │   ...    │       │
│  │  query   │ │  query   │ │  query   │ │  other   │       │
│  │  cache   │ │  cache   │ │  cache   │ │ modules  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│  Stale time: 30s │ Cache time: 5min │ Retry: 3x            │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────────────┐
│              IndexedDB (Offline State)                       │
│  tasks (100), courses (active), goals (active), briefings    │
│  + offline mutation queue + sync metadata                    │
└─────────────────────────────────────────────────────────────┘
```

### 33.2 Optimistic Update Pattern (Standard)

```typescript
// Standard pattern for all mutations
const mutation = useMutation({
  mutationFn: (newTask) => api.createTask(newTask),
  
  // 1. Optimistically update the cache
  onMutate: async (newTask) => {
    await queryClient.cancelQueries({ queryKey: ['tasks'] })
    const previous = queryClient.getQueryData(['tasks'])
    queryClient.setQueryData(['tasks'], (old) => [...old, { ...newTask, id: 'temp-id', status: 'pending' }])
    return { previous }  // Rollback context
  },
  
  // 2. On success — replace temp with real data
  onSuccess: (realTask, _vars, context) => {
    queryClient.setQueryData(['tasks'], (old) =>
      old.map(t => t.id === 'temp-id' ? realTask : t)
    )
    toast.success('Task created')
  },
  
  // 3. On error — rollback
  onError: (_err, _vars, context) => {
    queryClient.setQueryData(['tasks'], context.previous)
    toast.error('Failed to create task')
  },
})
```

### 33.3 Optimistic Update Rules by Module

| Module | Optimistic? | Rollback Strategy | Notes |
|---|---|---|---|
| Tasks | ✅ Yes | Full rollback with toast | Most frequent mutation |
| Courses | ✅ Yes | Full rollback | Progress updates are frequent |
| Goals | ✅ Yes | Full rollback | Milestone updates |
| Habits | ✅ Yes | Full rollback | Daily habit logging |
| Sleep | ✅ Yes | Full rollback | Nightly log |
| Income | ❌ No | Error state | Financial accuracy matters |
| Projects | ✅ Yes | Full rollback | Phase transitions |
| Ideas | ✅ Yes | Full rollback | Quick capture |
| Resources | ✅ Yes | Full rollback | Quick save |
| YouTube | ✅ Yes | Full rollback | Quick save |
| Opportunities | ❌ No | Error state | Application status accuracy |
| Time | ✅ Yes | Queue on offline | Timer accuracy is best-effort |
| Chat | ✅ Yes | Optimistic message | Streaming response confirms |
| Academics | ❌ No | Error state | CGPA calculation accuracy |

### 33.4 Zustand Store Architecture

```typescript
// UI Store (global, small, synchronous)
interface UIState {
  sidebarOpen: boolean
  theme: 'dark' | 'light'
  activeModule: ModuleName
  modalStack: ModalState[]
  toastQueue: Toast[]
  commandPaletteOpen: boolean
  quickCaptureOpen: boolean
  
  // Actions
  toggleSidebar: () => void
  setActiveModule: (module: ModuleName) => void
  pushModal: (modal: ModalState) => void
  popModal: () => void
  addToast: (toast: Toast) => void
  removeToast: (id: string) => void
}
```

**Store count**: 1 global UI store + per-module stores for complex state (kanban drag position, roadmap canvas state)

---

## 34. Notification Architecture

### 34.1 Notification Channel Strategy

| Channel | Urgency | Cost | Opt-in Required | Reliability | User Control |
|---|---|---|---|---|---|
| **In-app toast** | All levels | Free | No | High (always on) | Per-module toggle |
| **In-app badge** | Low-Medium | Free | No | High | Per-module toggle |
| **Web Push** | Medium-High | Free | Yes (browser) | Medium | Per-type toggle + quiet hours |
| **Dashboard banner** | Low | Free | No | High | Auto-dismiss |
| **Email (Resend)** | High-Critical | ~$0.001/email | Yes | High | Per-type toggle |
| **SMS (Twilio)** | Critical only | ~$0.02/SMS | Yes | Very High | Critical only |
| **ARIA Chat** | Low | Free | No | High | N/A — always on |

### 34.2 Notification Priority Matrix

| Notification | Channel | Priority | Frequency Cap | Cooldown |
|---|---|---|---|---|
| Morning Briefing | Push + Dashboard | High | 1/day | N/A |
| Deadline in < 2h | Push | High | Per task | N/A |
| Task missed (1st time) | Push | Medium | Per task | 15 min |
| Task missed (2nd time) | Push + Email | High | Per task | 30 min |
| Task missed (3rd + high) | Push + Email + SMS | Critical | Per task | Immediate |
| Course nudge (behind) | Push + Dashboard | Medium | 1/day per course | 24h |
| Course deadline < 1 week | Push | High | 1/day per course | 24h |
| Opportunity found (>80% match) | Push + Briefing | Medium | Per opportunity | N/A |
| Opportunity deadline < 48h | Push + Email | High | 1 per opportunity | 24h |
| Bedtime reminder | Push | Medium | 1/day | N/A |
| Habit missed 2+ days | Push | Low | 1/day per habit | 24h |
| Weekly review ready | Push + Dashboard | Medium | 1/week | N/A |
| Sync conflict | Toast | Low | Per conflict | N/A |
| System update/outage | Email | High | As needed | N/A |

### 34.3 Notification UX Rules

1. **No notification without context**: Every push notification includes the module name and item title
2. **Actionable notifications**: Clicking a notification opens the exact item, not just the module
3. **Quiet hours**: User-configurable (default: 11 PM - 7 AM), only critical alerts pass through
4. **Batched delivery**: Non-urgent notifications (habit miss, course nudge) are batched into daily digests
5. **Notification center**: In-app notification history with read/unread, grouped by module
6. **Rate limiting**: Max 5 push notifications per hour per user (prevents fatigue)
7. **Opt-out granularity**: Per-module, per-type, per-channel toggle in Settings

### 34.4 Notification Center UX (Proposed)

```
┌──────────────────────────────────────┐
│ 🔔 Notifications                    │
├──────────────────────────────────────┤
│ [All] [Unread] [Tasks] [Courses] ... │  ← Filter by module
├──────────────────────────────────────┤
│ Today                                │
├──────────────────────────────────────┤
│ 📋 DBMS assignment due in 2h       │  ← Click → task detail
│   2:30 PM                           │
│ 📚 Node.js — 40% behind schedule   │  ← Click → course detail
│   6:00 PM                           │
│ 😴 Time to wind down               │  ← Click → sleep log
│   9:30 PM                           │
├──────────────────────────────────────┤
│ Yesterday                            │
├──────────────────────────────────────┤
│ 🎯 2 new opportunities matched     │  ← Click → opportunity list
│   7:00 AM                           │
│ ✅ Weekly review ready             │  ← Click → weekly review
│   8:00 PM                           │
└──────────────────────────────────────┘
```

---

## 35. Data Visualization Component Strategy

### 35.1 Chart Types & Usage

| Chart Type | Use Case | Modules | Library | Complexity |
|---|---|---|---|---|
| **Line chart** | Trends over time (sleep score, productivity, income) | Sleep, Dashboard, Income | Recharts | Low |
| **Bar chart** | Comparisons (income by source, time by category) | Income, Time, Analytics | Recharts | Low |
| **Progress bar** | Goal/course completion, streak length | Courses, Goals, Habits | CSS + Tailwind | Low |
| **Donut/pie chart** | Distribution (time allocation, income breakdown) | Time, Income | Recharts | Medium |
| **Heatmap (GitHub-style)** | Daily activity over 6 months | Dashboard, Habits | Custom SVG | High |
| **Kanban board** | Task/project stage visualization | Tasks, Projects | Custom react-dnd | High |
| **Roadmap canvas** | Goal milestones with dependencies | Goals | React Flow | Very High |
| **Radar chart** | Skill profile, multi-dimensional comparison | Profile, Analytics | Recharts | Medium |
| **Timeline/Gantt** | Project phases, task scheduling | Projects, Time | Custom + React Flow | High |
| **Activity feed** | Chronological event stream | Dashboard | Custom list | Low |
| **Treemap** | Resource usage by category | Analytics | Recharts | Medium |
| **Scatter plot** | Correlation (sleep vs productivity) | Analytics, Sleep | Recharts | Medium |

### 35.2 Chart Design Tokens

```css
/* All charts must use these tokens */
--chart-line: #6366F1;            /* Primary line color */
--chart-area: rgba(99, 102, 241, 0.1);  /* Area fill */
--chart-bar: #818CF8;            /* Bar fill */
--chart-point: #00FFA3;          /* Data point highlight */
--chart-grid: #1E293B;           /* Grid lines */
--chart-axis: #475569;           /* Axis labels */

/* Multi-series colors */
--chart-series-1: #6366F1;       /* Indigo */
--chart-series-2: #10B981;       /* Emerald */
--chart-series-3: #F59E0B;       /* Amber */
--chart-series-4: #EF4444;       /* Red */
--chart-series-5: #8B5CF6;       /* Violet */
--chart-series-6: #EC4899;       /* Pink */
```

### 35.3 Chart Interaction Patterns

| Interaction | Description | Implementation |
|---|---|---|
| **Hover tooltip** | Show exact value + context | Recharts Tooltip component |
| **Click drill-down** | Click segment → filter/view detail | OnClick handler → navigate |
| **Brush/zoom** | Select time range to zoom | Recharts Brush component |
| **Legend toggle** | Click legend item → toggle series | Recharts Legend onClick |
| **Animation** | Animate on first render (once) | Framer Motion + Recharts |
| **Export** | Download as PNG via html2canvas | Button → export function |
| **Empty state** | "No data yet — start tracking to see trends" | Illustration + CTA |
| **Loading state** | Skeleton chart | Animated placeholder |
| **Error state** | "Could not load chart" + retry | Error boundary |

---

## 36. Frontend CI/CD Pipeline

### 36.1 Pipeline Stages

```
git push → GitHub
    ↓
┌──────────────────────────────────────────────────────────────────┐
│                        CI Pipeline                               │
│                                                                  │
│  Stage 1: Install & Build                                        │
│  ├── npm ci --frozen-lockfile                                    │
│  ├── next build (production)                                     │
│  └── Store build artifacts (.next/)                              │
│                                                                  │
│  Stage 2: Code Quality                                           │
│  ├── tsc --noEmit (TypeScript check)                             │
│  ├── next lint (ESLint)                                          │
│  └── prettier --check (formatting)                               │
│                                                                  │
│  Stage 3: Tests                                                  │
│  ├── jest --coverage (unit + integration)                        │
│  ├── cypress run (E2E — 15 critical flows)                      │
│  └── axe-core (accessibility scan)                               │
│                                                                  │
│  Stage 4: Performance & Security                                 │
│  ├── Lighthouse CI (performance budget check)                   │
│  ├── next/bundle-analyzer (bundle size check)                   │
│  ├── npm audit (dependency vulnerabilities)                      │
│  └── Snyk scan (supply chain security)                          │
│                                                                  │
│  Stage 5: Visual Regression                                      │
│  └── Chromatic/Percy (UI diff check)                             │
│                                                                  │
│  Stage 6: Deploy (main branch only)                              │
│  ├── Vercel deploy (production)                                  │
│  └── Run E2E smoke tests on production URL                      │
└──────────────────────────────────────────────────────────────────┘
```

### 36.2 Concurrency & Caching

| Resource | Cache Strategy | Cache Key |
|---|---|---|
| node_modules | Save/restore on lockfile change | `package-lock.json` hash |
| .next/cache | Save/restore on source change | All source files hash |
| Cypress binary | Save/restore (rarely changes) | OS + Cypress version |
| Chromatic build | Reuse if no component changes | Component files hash |

### 36.3 Deployment Strategy

| Branch | Deploy Target | Env Variables | Auto-deploy |
|---|---|---|---|
| `main` | Production (vercel.com) | Production env | Yes |
| `staging` | Staging (vercel-staging) | Staging env | Yes |
| `feature/*` | Preview (auto-generated URL) | Preview env | Yes |
| `dependabot/*` | Preview (auto-generated URL) | Preview env | Yes |

**Rollback strategy**: Vercel instant rollback (previous deployment) via dashboard or `vercel rollback` CLI.

---

## 37. Monitoring & Observability

### 37.1 Frontend Monitoring Stack

| Concern | Tool | What It Monitors |
|---|---|---|
| **Real User Monitoring (RUM)** | Vercel Analytics | Page views, web vitals (LCP, FCP, CLS, INP) |
| **Error Tracking** | Sentry | JS exceptions, API errors, unhandled rejections |
| **Performance** | Sentry Tracing | Slow transactions, N+1 queries, bundle load time |
| **AI Performance** | Custom instrumentation | LLM latency, token usage, fallback rate |
| **Offline/Online** | Custom (navigator.onLine + events) | Offline duration, sync queue size, conflict rate |
| **Usage Analytics** | PostHog | Feature adoption, funnel completion, retention |
| **Session Recording** | PostHog (sampled) | User behavior patterns, friction points |
| **Feature Flags** | PostHog/LaunchDarkly | Flag evaluation, A/B test results |
| **Logging** | Browser console (dev) + Sentry (prod) | Debug logs in dev, error logs only in prod |

### 37.2 Custom Instrumentation Points

| Event | Data Captured | Purpose |
|---|---|---|
| `task.created` | source (quick capture / chat / form), time to create | Quick capture efficiency |
| `task.completed` | time since due, priority, category | Completion patterns |
| `ai.chat.started` | message length, module context | Chat usage patterns |
| `ai.chat.completed` | latency, model, tokens, fallback used | AI cost + performance |
| `ai.action.executed` | action type, success/fail | Action execution reliability |
| `briefing.viewed` | time, engagement (scrolled/clicked) | Briefing relevance |
| `offline.action.queued` | action type, queue size | Offline usage patterns |
| `sync.conflict` | module, resolution strategy | Conflict frequency |
| `opportunity.saved` | match score, category | Radar relevance |
| `error.boundary.caught` | error message, module, component | Error frequency per module |

### 37.3 Alert Thresholds

| Alert | Condition | Channel |
|---|---|---|
| High error rate | >1% error rate in last 5 min | Email + Slack |
| Performance regression | LCP > 3s for >10% of users | Email |
| AI fallback rate high | >20% of calls use Claude > 1 hour | Email |
| Offline usage spike | >50% of sessions start offline | Dashboard note |
| Bundle size increase | >10% increase from baseline | PR comment |
| Sentry new issue | New unhandled error type | Slack |

---

## 38. Feature Flags & A/B Testing Framework

### 38.1 Feature Flag Architecture

```typescript
// Feature flag definitions
interface FeatureFlag {
  key: string
  description: string
  owner: string
  expiresAt?: Date
  targeting: {
    users?: string[]           // Specific user IDs
    percentage?: number        // Rollout percentage
    cohorts?: string[]         // A/B test cohorts
    environment?: string[]     // dev, staging, production
  }
  dependsOn?: string[]         // Feature dependencies
}

// Example flags
const flags = {
  'quick-capture-voice': {
    description: 'Voice input for Quick Capture',
    owner: 'product',
    targeting: { percentage: 50, environment: ['production'] },
    expiresAt: '2026-09-01'
  },
  'kanban-view-tasks': {
    description: 'Kanban view for task module',
    owner: 'frontend',
    targeting: { environment: ['staging'] }
  },
  'new-dashboard-layout': {
    description: 'New bento-grid dashboard layout',
    owner: 'design',
    targeting: { percentage: 10, cohorts: ['test-group-a'] }
  },
  'ai-task-breakdown': {
    description: 'AI task breakdown suggestions',
    owner: 'ai',
    dependsOn: ['quick-capture-voice'],
    targeting: { percentage: 25 }
  }
}
```

### 38.2 A/B Testing Framework

| Test Idea | Variant A (Control) | Variant B (Test) | Metric | Sample Size | Duration |
|---|---|---|---|---|---|
| Dashboard layout | Current list | New bento grid | Task completion rate, session duration | 500 users | 2 weeks |
| Quick Capture behavior | Button only | Button + Cmd+Shift+C hint | Capture rate/user/day | 500 users | 1 week |
| AI suggestion prominence | Subtle badge | Highlighted card | Suggestion acceptance rate | 300 users | 2 weeks |
| Briefing time | 7 AM | 6:30 AM | Briefing engagement rate | 500 users | 1 week |
| Task priority UI | Dropdown | AI auto + manual override | Priority accuracy, override rate | 300 users | 2 weeks |
| Notification frequency | Per-event | Batched hourly | Opt-out rate, task completion | 500 users | 2 weeks |

---

## 39. Loading / Empty / Error State Catalog

### 39.1 Loading State Patterns

| Component | Loading Treatment | Animation | Duration (Est.) |
|---|---|---|---|
| Page shell | Skeleton layout (sidebar + header) | Pulse animation | 200-500ms |
| Task list | 5 skeleton rows (varying width) | Staggered fade-in | 300-800ms |
| Dashboard | Zone-by-zone progressive loading | Top-down reveal | 200ms-2s |
| Chat messages | Empty shell with pulsing input | Typing indicator | 500ms-3s |
| Chart/Graph | Animated placeholder shape | Shimmer effect | 200ms-1s |
| Kanban board | Column skeletons with card placeholders | Staggered columns | 500ms-1.5s |
| React Flow canvas | Full-screen loading spinner | Spinner + "Loading roadmap..." | 1-3s |
| Heatmap | Gray grid → colored cells animate in | Cell-by-cell reveal | 500ms-2s |
| ARIA response | Streaming text (character by character) | Typewriter effect | 1-10s |
| Image/Thumbnail | Blur placeholder (LQIP) | Sharp transition | 200ms-2s |

### 39.2 Empty State Catalog

| Module | Empty State Message | Illustration | CTA |
|---|---|---|---|
| Tasks | "No tasks yet. Your second brain is ready." | Empty checklist illustration | "+ Add your first task" |
| Courses | "Start learning something new." | Empty bookshelf | "Add a course from Udemy, Coursera, or YouTube" |
| Goals | "What do you want to achieve?" | Empty roadmap | "Set your first goal" |
| Habits | "Small steps, big changes." | Empty habit tracker | "Start with one habit" |
| Sleep | "Track your sleep to see patterns." | Moon illustration | "Log last night's sleep" |
| Income | "Track your earnings." | Empty wallet | "Add your first income entry" |
| Projects | "Ready to build something?" | Empty workspace | "Start your first project" |
| Ideas | "Your next big idea starts here." | Lightbulb illustration | "Capture your first idea" |
| Resources | "Save resources as you learn." | Empty library | "Save your first resource (or install the browser extension)" |
| YouTube | "Your learning playlist is empty." | Empty video player | "Save your first video" |
| Opportunities | "Opportunities will appear here daily." | Radar illustration | "Setup your skills to start matching" |
| Time | "Start tracking to see where your time goes." | Empty clock | "Start your first timer" |
| Academics | "Plan your semester." | Empty grade book | "Add your subjects" |
| Dashboard (new user) | "Welcome to ARIA OS. Let's set up your second brain." | ARIA illustration | "Start 5-minute onboarding" |
| Chat (first time) | "Hi, I'm ARIA. Ask me anything about your day." | ARIA avatar | Type a message... |

### 39.3 Error State Catalog

| Scenario | Error Message | Illustration | Recovery Action |
|---|---|---|---|
| Network offline | "You're offline. Changes will sync when reconnected." | Offline icon | "Retry" button + auto-sync indicator |
| API 500 | "Something went wrong. Please try again." | Error icon | "Retry" button |
| Rate limited | "Too many requests. Please wait a moment." | Hourglass | Auto-retry with countdown |
| Auth expired | "Session expired. Please log in again." | Lock icon | "Log in" redirect |
| Module not found | "This page doesn't exist." | 404 illustration | "Go to Dashboard" |
| AI unavailable | "ARIA is temporarily unavailable. Your tasks are still here." | ARIA dimmed | "Retry" or "Use offline mode" |
| Storage quota exceeded | "Local storage is full. Old data will be cleaned up." | Storage icon | "Free up space" button |
| Sync conflict | "This item was updated on another device. Using latest version." | Sync icon | "View changes" link |

---

## 40-49. Strategic Sections (Expanded from v1)

### 40. Mobile Strategy (Expanded)

#### 40.4 Mobile Touch Target Specification

| Element | Min Size | Spacing | Visual Feedback |
|---|---|---|---|
| Bottom tab icon | 48x48px | 8px from edges | Scale 0.95 on press |
| List item (task, course) | 100% x 56px | 12px padding | Background highlight |
| Floating action button | 56x56px | 16px from edges | Scale + glow on press |
| Form input | 100% x 48px | 12px padding | Focus ring |
| Swipe action area | Full height x 80px | N/A | Color reveal on threshold |
| Modal close button | 44x44px | 12px from top-right | Opacity on press |
| Checkbox/Radio | 28x28px | 8px from label | Animated check mark |

#### 40.5 Mobile Gesture Map

| Gesture | Action | Module |
|---|---|---|
| Swipe left (task) | Complete task | Tasks |
| Swipe right (task) | Reschedule (tomorrow) | Tasks |
| Swipe left (notification) | Dismiss | Global |
| Swipe right (notification) | View details | Global |
| Swipe down (page) | Pull to refresh | All lists |
| Swipe up (modal) | Close/dismiss | All modals |
| Long press (item) | Context menu | All items |
| Double tap (briefing) | Expand/collapse | Dashboard |
| Pinch (roadmap) | Zoom in/out | Goals |
| Shake (anywhere) | Undo last action | Global (future) |

#### 40.6 Mobile Data Consumption Strategy

| Activity | Data Mode | Data Usage (Est.) |
|---|---|---|
| Morning briefing view | Online only | ~50KB |
| Task list + details | Offline cached | ~10KB (refresh) |
| Quick capture (text) | Optimistic + queue | ~1KB |
| Quick capture (URL) | Optimistic + queue | ~5KB |
| Chat message (send) | Online only | ~2KB |
| Chat response (receive) | Online only | ~10-50KB |
| Habit log | Optimistic | ~ 0.5KB |
| Sleep log | Optimistic | ~0.5KB |
| Dashboard view | Offline cached | ~100KB (refresh) |
| AI summary/image | Online only | ~100-500KB |

---

### 41. Tablet Strategy (Expanded)

#### 41.4 Tablet-Specific Interaction Patterns

| Pattern | Implementation | Benefit |
|---|---|---|
| **Drag & drop split** | Drag task from list → drop into time slot on calendar | Natural scheduling |
| **Two-thumb navigation** | Left thumb: sidebar toggle, Right thumb: content interaction | Ergonomic for tablet hold |
| **Pencil/hover** | Hover to preview, tap to select, pencil to write | Precision input |
| **Floating toolbar** | Context-sensitive toolbar appears near selection | Reduces travel distance |
| **Multi-window (iPad)** | ARIA OS in split view with browser, notes, or IDE | Power user workflow |

#### 41.5 Tablet Keyboard Shortcuts (External Keyboard)

| Shortcut | Action | Context |
|---|---|---|
| `Cmd+Tab` | Switch between open modules | Global |
| `Cmd+Shift+T` | Task quick capture | Global |
| `Cmd+R` | Refresh current module data | Module view |
| `Cmd+F` | Search/filter current module | Module view |
| `Cmd+Opt+D` | Toggle dark mode | Global |
| `Space` | Play/pause video | YouTube |
| `Cmd+Up/Down` | Navigate to top/bottom of list | Lists |

---

### 42. Desktop Strategy (Expanded)

#### 42.5 Desktop Window Management

| Window State | Layout | Trigger |
|---|---|---|
| **Normal** | Sidebar (240px) + Content (flex) | Default |
| **Focus mode** | Sidebar collapsed (64px) + Content (full) | Cmd+Shift+F |
| **Chat overlay** | Content (70%) + Chat panel (30%) | Cmd+Shift+C |
| **Presentation** | Content only (no chrome) | Cmd+Shift+P (future) |
| **Multi-monitor** | Content on main, chat/notifications on secondary | Manual arrange |

#### 42.6 Desktop Context Menu (Right-Click)

| Target | Menu Items |
|---|---|
| Task item | Complete, Reschedule, Edit, Delete, Duplicate, Copy Link, Add SubTask |
| Course card | Mark Progress, View Detail, Edit Deadline, Archive |
| Goal milestone | Edit, Mark Complete, Add Dependency, Delete |
| Habit entry | Edit, Log for Today, Reset Streak, Archive |
| Resource | Open URL, Edit, AI Summarize, Link to Goal, Archive |
| Empty space | New Task, New Idea, New Course, Paste |

#### 42.7 Desktop Drag & Drop Ecosystem

| Source | Target | Action |
|---|---|---|
| Task | Calendar time slot | Schedule task |
| Task | Goal milestone | Link task to milestone |
| Resource | Course card | Link resource to course |
| Idea | Project card | Convert idea to project |
| Course | Goal milestone | Link course to goal |
| Task | Kanban column | Change task status |
| Goal | Goal (dependency) | Create dependency edge |

---

### 45. Accessibility Strategy (Expanded)

#### 45.4 Screen Reader Specific Patterns

| Pattern | Implementation | Benefit |
|---|---|---|
| **Live regions** | `aria-live="polite"` on briefing, notifications, chat responses | Screen reader announces updates without interruption |
| **Alert dialogs** | `role="alertdialog"` + `aria-describedby` for error modals | Immediate focus + context |
| **Progress announcements** | `aria-valuenow`, `aria-valuemin`, `aria-valuemax` on progress bars | Numeric progress for non-visual users |
| **Drag & drop alternatives** | Keyboard reorder (Alt+Up/Down) for all draggable lists | D&D not dependent on pointer |
| **Canvas accessibility** | `role="img"` + `aria-label` describing React Flow state | Roadmap accessibility for non-visual |
| **Chart data tables** | Hidden `<table>` alternative for every chart | Screen reader gets raw data |
| **Command palette** | `role="combobox"` with `aria-activedescendant` | Standard autocomplete interaction |
| **Toast announcements** | `role="status"` + `aria-live="polite"` on toast container | Non-intrusive announcements |

#### 45.5 Reduced Motion Specification

```css
/* All animations MUST respect prefers-reduced-motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
  
  /* Keep essential transitions at minimum */
  .btn:hover {
    opacity: 0.85;  /* Remove scale, keep visual feedback */
  }
  
  /* Disable decorative animations entirely */
  .animate-pulse-glow,
  .animate-float,
  .animate-scan {
    animation: none !important;
  }
  
  /* Keep functional animations but simplified */
  .skeleton {
    animation: none;
    background: var(--bg-elevated);  /* Static placeholder */
  }
}
```

#### 45.6 High Contrast Mode

| Token | Normal | High Contrast |
|---|---|---|
| `bg-background` | #0A0B0F | #000000 |
| `bg-background-card` | #12141C | #1A1A1A |
| `text-primary` | #F0F2F5 | #FFFFFF |
| `text-secondary` | #8B92A5 | #CCCCCC |
| `accent-primary` | #6366F1 | #9999FF |
| `accent-neon` | #00FFA3 | #00FF88 |
| `border-default` | #2A2E3F | #666666 |
| `glass-light` | rgba(255,255,255,0.03) | rgba(255,255,255,0.1) |

#### 45.7 Accessibility Testing Cadence

| Frequency | Test Type | Tool/Method |
|---|---|---|
| Every PR | Automated scan | axe-core via Cypress |
| Weekly | Manual keyboard audit | Tab through all flows |
| Bi-weekly | Screen reader test | VoiceOver (Mac) + NVDA (Windows) |
| Monthly | Color contrast audit | WCAG Contrast Checker |
| Quarterly | Full WCAG 2.1 AA audit | Manual + axe DevTools |
| Per feature release | User testing with screen reader | 2-3 participants |

---

### 46. Product, UX & Technical Risks (Expanded)

#### 46.1 Risk Quantification Matrix

| Risk ID | Risk | Category | Likelihood (1-5) | Impact (1-5) | RPN | Mitigation |
|---|---|---|---|---|---|---|
| R-001 | Single developer leaves | Team | 4 | 5 | **20** | Document everything, cross-train, open source |
| R-002 | Free tier T&Cs change | Infrastructure | 3 | 4 | **12** | Migration plan to paid tiers |
| R-003 | Ollama too slow on student HW | AI | 4 | 4 | **16** | Claude fallback, algorithmic fallback |
| R-004 | 15 modules overwhelm users | UX | 5 | 4 | **20** | Onboarding wizard, progressive reveal |
| R-005 | Notification fatigue | UX | 4 | 4 | **16** | Batching, quiet hours, opt-out granularity |
| R-006 | AI responses feel generic | AI/UX | 3 | 4 | **12** | Memory system, personalization |
| R-007 | Bundle size grows unbounded | Performance | 3 | 3 | **9** | Bundle analyzer in CI, per-page budget |
| R-008 | Offline sync conflicts | Technical | 3 | 3 | **9** | LWW + server timestamps |
| R-009 | Prompt injection vulnerabilities | Security | 3 | 5 | **15** | Input sanitization, guardrails |
| R-010 | IndexedDB storage limits | Technical | 2 | 3 | **6** | Auto-clean, storage pressure handling |
| R-011 | XSS via AI-generated content | Security | 2 | 5 | **10** | DOMPurify, CSP headers |
| R-012 | Realtime connection limits | Infrastructure | 3 | 3 | **9** | Monitor, paid upgrade if needed |
| R-013 | Students don't adopt | Product | 3 | 5 | **15** | Early adopter program, weekly interviews |
| R-014 | Incumbent builds similar features | Competition | 2 | 3 | **6** | Student-specific moat, local AI |
| R-015 | Browser extension maintenance | Technical | 3 | 2 | **6** | Core value independent of extension |

#### 46.2 Technical Debt Register

| Debt Item | Module | Severity | Effort to Fix | Priority |
|---|---|---|---|---|
| No TypeScript strict mode on all files | Global | High | Medium (migration) | P1 |
| No E2E test coverage | Tests | High | High (15 critical flows) | P1 |
| Inconsistent error handling across modules | Global | Medium | High (standardize) | P2 |
| No visual regression tests | UI | Medium | Medium (add Chromatic) | P2 |
| No loading/empty/error state for every component | UI | Medium | High (inventory + implement) | P2 |
| IndexedDB sync queue has no conflict UI | Offline | Low | Low (add toast) | P3 |
| React Query stale time not tuned per module | Data | Low | Low (per-module config) | P3 |
| No bundle size monitoring in CI | CI | Medium | Low (add to pipeline) | P2 |
| No CSP headers in production | Security | High | Low (configure) | P1 |
| Service worker not using versioned caches | Offline | Medium | Low (update SW) | P2 |

---

### 47. Design & Innovation Opportunities (Expanded)

#### 47.1 Design Opportunity Prioritization

| Opportunity | Value (1-5) | Effort (1-5) | Priority Score | Timeline |
|---|---|---|---|---|
| Empty states as onboarding moments | 5 | 1 | **25** | Sprint 1 |
| Morning briefing as interactive widget | 5 | 1 | **25** | Sprint 1 |
| Quick Capture from everywhere | 5 | 2 | **20** | Sprint 2 |
| Sleep score as UI parametrization | 4 | 2 | **16** | Sprint 3 |
| ARIA's memory visible (Things I Know) | 4 | 2 | **16** | Sprint 3 |
| Cross-module compound growth viz | 5 | 3 | **15** | Sprint 4 |
| Weekly review as shareable artifact | 3 | 1 | **15** | Sprint 2 |
| Opportunity radar as daily ritual | 3 | 1 | **12** | Sprint 3 |
| Gamified skill-to-income map | 4 | 4 | **10** | Sprint 5 |
| Offline-first with invisible sync | 5 | 4 | **10** | Sprint 4 |

#### 47.2 Innovation Roadmap

| Quarter | Innovation | Risk Level | Success Metric |
|---|---|---|---|
| Q3 2026 | AI Task Breakdown | Medium | Task completion rate +15% |
| Q3 2026 | Sleep-Adaptive Scheduling | Low | Overdue tasks -20% |
| Q4 2026 | Natural Language Quick Capture | Medium | Capture rate +40% |
| Q4 2026 | Cross-Module Pattern Detection | High | Weekly review engagement +30% |
| Q1 2027 | Knowledge Graph Browse | High | Resource read rate +25% |
| Q1 2027 | Browser Extension Intelligence | Medium | Save rate +50% |
| Q2 2027 | AI Roadmap Generation | High | Goal completion +20% |
| Q2 2027 | Voice-Only Mode | Medium | Chat interactions +30% |
| Q3 2027 | AI Study Buddy | High | Course completion +15% |
| Q4 2027 | ARIA as Career Coach | Medium | Opportunity apply rate +40% |

---

### 48. Recommended Direction (Product, Frontend, Design, AI)

#### 48.1 Product Direction — Phase Gate Model

```
Phase 1: Foundation (Q3 2026)
│  Gate: All P0 modules functional, 50 DAU
│  Deliverables: Tasks, Courses, Goals, Habits, Sleep, Chat
│  AI: Daily Briefing, Opportunity Radar (shell → functional)
│  UX: Quick Capture, Offline PWA, Onboarding wizard
│
├──► Phase 2: Intelligence (Q4 2026)
│  Gate: 100 DAU, >60% 30d retention
│  Deliverables: All 15 modules complete
│  AI: All 8 agents functional, ARIA memory system
│  UX: Browser extension, Weekly Review, Voice input
│
├──► Phase 3: Network Effects (Q1-Q2 2027)
│  Gate: 500 DAU, >70% retention
│  Deliverables: Knowledge graph, Pattern detection
│  AI: Learning Agent, Career Agent
│  UX: Mobile apps (React Native), Community features
│
└──► Phase 4: Platform (Q3-Q4 2027+)
   Gate: 1000+ DAU, revenue experiments
   Deliverables: Public API, Marketplace, Monetization
   AI: AI Study Buddy, Career Coach
   UX: Full native apps, Team features
```

#### 48.2 Frontend Direction — Technology Stack Lock-In

| Layer | Decision | Rationale | Alternatives Considered |
|---|---|---|---|
| Framework | Next.js 14 App Router | Fullstack React, SSR/SSG/ISR, streaming, RSC ready | Remix (less ecosystem), SvelteKit (smaller talent pool) |
| State | Zustand + React Query | Minimal boilerplate, excellent dev tools, React Query handles server state perfectly | Redux (too heavy), Jotai (too experimental) |
| Styling | Tailwind CSS 3 | Design tokens built-in, zero runtime, excellent build-time purge | CSS Modules (no token system), Styled Components (runtime cost) |
| Animation | Framer Motion 11 | Production-proven, AnimatePresence, layout animations, gesture support | GSAP (React-unfriendly), Motion One (less feature-rich) |
| Charts | Recharts + Custom SVG | Declarative, composable, themable via Tailwind tokens | D3 (imperative, steep learning), Nivo (heavier) |
| Canvas | React Flow 11 | Proven for node-based editors, mini-map, controls, custom nodes | Custom D3 (too much effort), XYFlow (React Flow v12 — wait for stable) |
| Testing | Jest + RTL + Cypress | Industry standard, excellent integration test support | Vitest (compatible but smaller ecosystem), Playwright (good but Cypress more integrated) |
| Monitoring | Sentry + PostHog | Error tracking + product analytics in one integrated stack | Datadog RUM (expensive), New Relic (overkill) |
| Offline | Workbox 6 + idb 7 | Battle-tested by Google, excellent precaching + runtime caching | Custom SW (error-prone), UpUp (limited) |

#### 48.3 Design Direction — Component Completion Roadmap

| Component | Current State | Next Action | Owner |
|---|---|---|---|
| Button (5 variants, 3 sizes) | Complete | Add loading state animation | Design |
| Card (6 variants) | Complete | Add interactive variant states | Design |
| Input system | Complete | Add input group, leading/trailing icons | Design |
| DataTable | Design complete | Build sort + filter + paginate | Frontend |
| CommandPalette (Cmd+K) | Not started | Prioritize — power user multiplier | Design + Frontend |
| KanbanBoard | Design complete | Build drag-and-drop with touch support | Frontend |
| Heatmap | Design complete | Build with custom SVG + click-to-detail | Frontend |
| Calendar | Not started | Need for Time module — month/week/day views | Design |
| ActivityFeed | Not started | Need for Dashboard — chronological stream | Design |
| RoadmapCanvas | Design complete | Performance optimize >100 nodes | Frontend |
| MessageList | Design complete | Add markdown + code blocks + streaming | Frontend |
| NotificationCenter | Not started | Need for notification management | Design |
| Progress bar system | Complete | Ensure accessible (aria-valuenow) | Frontend |

#### 48.4 AI Direction — Prompt File Development Plan

| Prompt | Current Size | Action | Priority | Owner |
|---|---|---|---|---|
| `aria_system.md` | 12.5KB | Add capability registry, intent classification examples | P0 | AI |
| `guardrails.md` | 11.7KB | Reduce to essential rules, add prompt injection defense | P0 | AI |
| `briefing_agent.md` | 28KB | Validate day profiles, add edge case examples | P0 | AI |
| `weekly_review_agent.md` | 35KB | Split into system + examples files | P1 | AI |
| `opportunity_radar_agent.md` | 24KB | Add scoring algorithm details, zero-result fallback | P1 | AI |
| `memory_agent.md` | 24KB | Add extraction priorities, fact verification | P1 | AI |
| `sleep_agent.md` | 26KB | Add score formula, adaptive messages | P1 | AI |
| `nudge_agent.md` | 19KB | Add escalation rules, suppression logic | P1 | AI |

---

## 49. Research References (Expanded)

### 49.1 Academic & Industry Frameworks Applied

| Framework | Source | Applied In |
|---|---|---|
| **Atomic Design** | Brad Frost (2016) | Component hierarchy (atoms → molecules → organisms → pages) |
| **WCAG 2.1 AA** | W3C Web Accessibility Initiative | Accessibility strategy §45, contrast requirements, keyboard navigation |
| **Bento Grid** | Pinterest/Microsoft | Dashboard layout §16.4 |
| **DIKW Pyramid** | Russell Ackoff (1989) | Knowledge strategy — Data → Information → Knowledge → Wisdom pipeline |
| **SECI Model** | Nonaka & Takeuchi (1995) | Knowledge creation: Socialization → Externalization → Combination → Internalization |
| **GTD (Getting Things Done)** | David Allen (2001) | Task capture → clarify → organize → reflect → engage workflow |
| **PARA Method** | Tiago Forte (2017) | Information architecture: Projects → Areas → Resources → Archives |
| **Spaced Repetition** | Ebbinghaus Forgetting Curve (1885) | Learning §22.2 — reviews at 1, 3, 7, 14, 30 days |
| **Fitts's Law** | Paul Fitts (1954) | Touch target sizing (44x44px), FAB placement |
| **Hick's Law** | W. E. Hick (1952) | Progressive disclosure, command palette reduces choice paralysis |
| **Jakob's Law** | Jakob Nielsen (2000) | Familiar UI patterns (sidebar nav, bottom tabs, swipe actions) |
| **Miller's Law** | George Miller (1956) | Chunking: 5 bottom tabs, 7±2 module groups, 3 priority tasks |
| **Tesler's Law** | Larry Tesler (1984) | AI handles complexity (auto-priority, auto-category, auto-schedule) |
| **Doherty Threshold** | Walter Doherty (1982) | <400ms for AI responses, <100ms for UI updates |
| **Postel's Law** | Jon Postel (1980) | Forgiving input: natural language dates, typo-tolerant search |
| **Streaming SSR** | React 18 / Next.js 14 | Progressive page rendering §28.3 |
| **Optimistic UI** | React Query patterns | §33.2 — instant local update before API confirmation |
| **Graceful Degradation** | Web design pattern | Every AI feature has algorithmic fallback, every agent has inline prompt |

### 49.2 Design Systems — Specific Pattern Extraction

| Design System | Pattern Extracted | Applied In |
|---|---|---|
| **shadcn/ui** | Copy-paste component model, Radix primitives, accessible by default | Component architecture, a11y-first approach |
| **Material Design 3** | M3 color scheme (primary, secondary, tertiary, error), elevation system, motion timing | Color tokens (adapted to cyberpunk), shadow levels, transition speeds |
| **IBM Carbon** | Enterprise table specification, comprehensive form validation | DataTable component, error state patterns |
| **Ant Design** | Pro-form patterns, table with inline editing, complex data display | Task detail panel, course progress forms |
| **MagicUI** | Animated gradient borders, glow cards, micro-interactions | Visual effects, cyberpunk decorative elements |
| **Aceternity** | Spotlight cards, animated modals, bento grid | Dashboard layout, modal transitions |
| **Origin UI** | Minimalist component, clean state handling, skeleton patterns | Loading states, empty states |
| **21st.dev** | Component marketplace concept, design-to-code workflow | Future: community component sharing |

### 49.3 Products — Specific Learnings Applied

| Product | Learning | Applied As |
|---|---|---|
| **Linear** | Keyboard-first, optimistic UI, command palette | §17 Navigation, §19 Command Center |
| **Notion** | Database views (table/board/calendar), AI writing | §9.2 AI capabilities, module-level views |
| **ClickUp** | Relationship fields, goal → task hierarchy | §12 Cross-module data flow |
| **Motion** | AI auto-scheduling, calendar-first | §22 Learning deadlines, §16 Dashboard schedule |
| **Sunsama** | Daily planning ritual, bounded task lists | §11.1 Aarav daily journey, §16 Briefing |
| **Mem** | AI auto-org, semantic search | §21 Knowledge strategy, §18 Search |
| **Reflect** | Graph navigation, AI linking | §21.3 Knowledge graph (future) |
| **Capacities** | Object-based KM, typed content | §25.1 Content inventory, typed entities |
| **Anytype** | Local-first, offline primary | §28 Offline strategy |
| **Obsidian** | Graph view, bi-directional links | §21.3 Future knowledge graph |
| **Cursor** | Inline AI suggestions, context-aware | §24 ARIA inline suggestions |
| **ChatGPT** | Streaming responses, conversation threading | §24.2 Chat interaction modalities |
| **Claude** | Long context, safe design, structured output | §14 AI architecture, code generation |
| **Perplexity** | Source-backed answers | §23.2 Match scoring — "Why this matches you" |
| **GitHub** | Issues → PR → pipeline workflow | §§ 8-9 Ideas → Projects → Launch pipeline |
| **Vercel** | Performance obsession, route transitions | §37 Performance budget, deploying |
| **Stripe** | Developer UX, progressive disclosure | §39 Error handling, API error codes |
| **PostHog** | Self-serve analytics, feature flags, session recording | §38.2 A/B testing, §37.1 Product analytics |
| **Datadog** | Dashboard-as-command-center, correlated views | §20 Analytics strategy, dashboard design |
| **Supabase** | Realtime subscriptions, RLS, Edge Functions | §29 Realtime, §13 Data layer |

---

## 50. Appendices

### Appendix A: Glossary of Terms

| Term | Definition |
|---|---|
| ARIA | Adaptive Reasoning and Intelligence Assistant — the AI orchestrator |
| Agent | Specialized AI module with a single responsibility (e.g., Planner, Memory) |
| Module | A functional area of the system (e.g., Task Manager, Course Tracker) |
| PromptLoader | System that loads AI prompts from `prompts/` with YAML frontmatter parsing |
| RLS | Row Level Security — Supabase security policy per user |
| Graceful Degradation | Every AI feature has a non-AI fallback; system works without AI |
| Zero-Miss Policy | Every overdue task must be done, rescheduled, or explicitly dropped |
| Resurface Engine | Algorithm that surfaces saved content related to current activity |
| Opportunity Radar | Daily scanner matching external opportunities to user skills |
| Compound Growth | Every action feeds every other action (course → skill → project → income) |
| Active Push Intelligence | System proactively delivers information without user prompting |
| Prompt Frontmatter | YAML metadata block at the top of every prompt file |

### Appendix B: File Reference Index

| Document | Location | Relevance |
|---|---|---|
| AGENTS.md | `/AGENTS.md` | Master reference for all AI agent work (21 sections) |
| Project Vision v4.0.0 | `/docs/product/00_ProjectVision.md` | Vision, BHAG, market timing, 5 pillars |
| PRD v3.0.0 | `/docs/product/02_PRD.md` | Functional reqs (FR-01 to FR-25), personas |
| BRD v3.0.0 | `/docs/product/03_BRD.md` | TAM/SAM/SOM, business goals, risk register |
| SRS v1.0.0 | `/docs/product/04_SRS.md` | FR per module, external interfaces, use cases |
| Architecture | `/docs/engineering/12_Architecture.md` | System diagram, component responsibilities, data flows |
| Agent Architecture v3.0.0 | `/docs/engineering/14_AgentArchitecture.md` | 15 agents, coordination, agent lifecycle |
| Database v3.0.0 | `/docs/engineering/15_Database.md` | 21 tables, DDL, RLS policies |
| API Reference | `/docs/engineering/17_API.md` | ~53 endpoints, auth flow, rate limiting |
| Agent Spec | `/docs/ai/20_Agent.md` | 5209 lines — complete agent specifications |
| Design System v3.0.0 | `/docs/design/10_DesignSystem.md` | Atomic design, component specifications |
| UI/UX Spec v3.0.0 | `/docs/design/08_UIUX.md` | UX principles, research methodology, personas |
| Design Tokens | `/docs/design/35_DesignTokens.md` | All tokens: color, typography, spacing, shadow |
| Prompt Loader | `/packages/ai/prompt_loader.py` | PromptLoader source code (102 lines) |
| Tailwind Config | `/apps/web/tailwind.config.js` | All design token implementations (215 lines) |

### Appendix C: Audit Trail — v1.0.0 to v2.0.0

| Change | v1.0.0 | v2.0.0 | Reason |
|---|---|---|---|
| Line count | 1,913 | ~3,500+ | 11 new enterprise-depth sections added |
| Sections | 40 | 50+ | Information Architecture, AI UX Patterns, Agentic UX, Render Strategy, Performance Budget, Security, Testing, Error Handling, State Management, Notifications, Data Viz, CI/CD, Monitoring, Feature Flags, State Catalog added |
| Risk analysis | 8 items | 15 items + RPN scores | Proper risk quantification matrix |
| Design opportunities | 10 items | 10 items + prioritization scores | Priority score = Value × Effort |
| Innovation roadmap | 3 tiers (near/mid/long) | 4 quarters with success metrics | Measurable outcomes |
| Research references | 20 products | 20 products + 15 frameworks + 8 design systems | Academic rigor added |
| Missing sections from original request | ~10 gaps identified | All gaps filled | Complete enterprise coverage |

---

> **Document Status**: Active — v2.0.0
> **Review Date**: 2026-06-11
> **Next Review**: 2026-09-11
> **This document should be read as a companion to SB-DISCOVERY-001 (v1.0.0), extending it with enterprise-depth analysis across 10 additional domains.**

---

*End of Enterprise Frontend Discovery Report v2.0.0*
