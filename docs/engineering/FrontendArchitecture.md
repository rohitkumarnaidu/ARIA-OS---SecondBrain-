# Frontend Architecture — Enterprise Reference

**Document ID:** FE-ARCH-001  
**Version:** 2.0.0  
**Status:** Active  
**Last Updated:** 2026-06-13  
**Applies To:** `apps/web/` — Next.js 14 App Router frontend (targeting v15)  
**Classification:** Internal — Architecture Governance  
**Reading Time:** ~45 min  
**Cross-References:** `AGENTS.md §4-6`, `docs/design/10_DesignSystem.md`, `docs/engineering/StateManagement.md`, `docs/engineering/FrontendOfflinePWA.md`, `docs/engineering/FrontendPerformanceGuide.md`, `docs/engineering/FrontendRoutingNavigation.md`, `docs/engineering/FrontendSecurityGuide.md`, `docs/engineering/FrontendTestingGuide.md`, `docs/engineering/FrontendAccessibilityGuide.md`, `docs/engineering/FrontendObservabilityGuide.md`, `packages/ui/`, `packages/types/`

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Frontend Principles](#2-frontend-principles)
3. [Folder Structure](#3-folder-structure)
4. [Route Architecture](#4-route-architecture)
5. [Layout Architecture](#5-layout-architecture)
6. [Component Architecture](#6-component-architecture)
7. [State Architecture](#7-state-architecture)
8. [Data Architecture](#8-data-architecture)
9. [Search Architecture](#9-search-architecture)
10. [Command Center Architecture](#10-command-center-architecture)
11. [Notification Architecture](#11-notification-architecture)
12. [Realtime Architecture](#12-realtime-architecture)
13. [Offline Architecture](#13-offline-architecture)
14. [PWA Architecture](#14-pwa-architecture)
15. [Performance Architecture](#15-performance-architecture)
16. [Accessibility Architecture](#16-accessibility-architecture)
17. [Security Architecture](#17-security-architecture)
18. [Error Handling Architecture](#18-error-handling-architecture)
19. [Observability Architecture](#19-observability-architecture)
20. [Testing Architecture](#20-testing-architecture)
21. [Scalability Architecture](#21-scalability-architecture)
22. [Future Expansion Architecture](#22-future-expansion-architecture)

---

## 1. Executive Summary

### 1.1 Vision Statement

The Second Brain OS frontend is an enterprise-grade, cyberpunk-themed personal AI productivity application built on **Next.js (App Router)**. It serves as the visual and interactive layer for 15 backend modules, connecting users to their tasks, courses, goals, habits, sleep, income, projects, ideas, resources, opportunities, time tracking, AI chat, and automation triggers.

The frontend architecture follows six core pillars:

| Pillar | Description |
|---|---|
| **Component-driven** | Atomic design with shadcn/ui primitives, composed into feature-level organisms |
| **State-isolated** | Six distinct state layers (server, client, realtime, offline, AI, search) with clear boundaries |
| **Offline-first** | Every read path works without network; mutations queue and replay on reconnection |
| **Accessible by default** | WCAG 2.2 AA target with keyboard navigation, screen reader support, reduced motion |
| **Performant at scale** | Core Web Vitals targets (LCP ≤1.5s, FID ≤50ms, CLS ≤0.05, INP ≤100ms) |
| **Observable & testable** | Sentry error tracking, PostHog analytics, Playwright E2E, Vitest unit/integration |

### 1.2 Tech Stack Upgrade Matrix

The frontend currently runs **Next.js 14.2.0 / React 18.2.0 / Tailwind v3.4.1**. The target architecture is **Next.js 15 / React 19 / Tailwind v4 / shadcn/ui**. Each section of this document describes the target state, with migration paths annotated per section.

| Layer | Current (v14) | Target (v15+) | Migration Phase |
|---|---|---|---|
| **Framework** | Next.js 14.2.0 | Next.js 15.x | Phase 1 |
| **UI Library** | React 18.2.0 | React 19.x | Phase 1 |
| **Styling** | Tailwind v3.4.1 + CSS modules | Tailwind v4.x (CSS-first config) | Phase 1 |
| **Component Library** | Custom components/Button, Card, etc. | shadcn/ui + components/ui/ | Phase 2 |
| **Server State** | Zustand stores wrapping Supabase calls | TanStack Query v5 | Phase 2 |
| **Client State** | Zustand v4.4.7 | Zustand v5.x | Phase 1 |
| **Form Management** | react-hook-form v7 | react-hook-form v7 (upgrade) | Phase 1 |
| **Animations** | Framer Motion v10.18 | Framer Motion v11 + GSAP | Phase 2 |
| **PWA** | next-pwa v5.6 (Workbox) | @serwist/next | Phase 2 |
| **E2E Testing** | @playwright/test v1.60 | @playwright/test latest | Phase 1 |
| **Observability** | None | Sentry + PostHog + OpenTelemetry | Phase 2 |
| **State Persistence** | None (in-memory only) | Zustand persist + IndexedDB | Phase 2 |

### 1.3 Architecture at a Glance

```
+------------------------------------------------------------------------------+
|                           CLIENT (Browser)                                    |
|                                                                               |
|  +----------------------------------------------------------------------+    |
|  |                       Next.js 15 App Router                           |    |
|  |                                                                       |    |
|  |  +----------+ +------------------+ +--------------+ +--------------+ |    |
|  |  | Root     | | Dashboard        | | Route Groups | | Parallel     | |    |
|  |  | Layout   | | Layout           | | (public)/    | | Routes       | |    |
|  |  | (fonts,  | | (Sidebar+Navbar) | | (auth)/      | | @modal/@feed | |    |
|  |  | metadata)| |                  | | (dashboard)  | |              | |    |
|  |  +----------+ +------------------+ +--------------+ +--------------+ |    |
|  |                                                                       |    |
|  |  +----------------------------------------------------------------+  |    |
|  |  |                     Module Pages (16)                           |  |    |
|  |  |  Tasks Courses Goals Habits Sleep Income Projects Ideas         |  |    |
|  |  |  Resources Opps Academics YouTube Time Chat Automation          |  |    |
|  |  +----------------------------------------------------------------+  |    |
|  |                                                                       |    |
|  |  +----------------------------------------------------------------+  |    |
|  |  |                     State Layer (6 parts)                       |  |    |
|  |  |  +--------------+ +---------+ +-----------+ +----------------+ |  |    |
|  |  |  | TanStack     | | Zustand | | Supabase  | | IndexedDB      | |  |    |
|  |  |  | Query        | | Client  | | Realtime  | | Offline Queue  | |  |    |
|  |  |  | (Server)     | | (Global)| | (Live)    | | (Sync)         | |  |    |
|  |  |  +--------------+ +---------+ +-----------+ +----------------+ |  |    |
|  |  |  +--------------+ +----------------------------------------+   |  |    |
|  |  |  | AI Streaming | | Search State                            |   |  |    |
|  |  |  | (State      | | (Command palette, full-text index)      |   |  |    |
|  |  |  |  Machine)   | |                                         |   |  |    |
|  |  |  +--------------+ +----------------------------------------+   |  |    |
|  |  +----------------------------------------------------------------+  |    |
|  |                                                                       |    |
|  |  +----------------------------------------------------------------+  |    |
|  |  |              Shared Component Library (shadcn/ui + custom)      |  |    |
|  |  |  ui/button ui/input ui/card ui/dialog ui/select ui/table       |  |    |
|  |  |  ui/toast ui/tabs ui/badge ui/avatar ui/dropdown-menu          |  |    |
|  |  |  Sidebar Navbar OfflineBanner ThreeBackground DataTable         |  |    |
|  |  +----------------------------------------------------------------+  |    |
|  +----------------------------------------------------------------------+    |
|                                                                               |
|  +----------------------------------------------------------------------+    |
|  |                     External Connections                              |    |
|  |  +--------------+ +------------+ +----------+ +----------+ +-------+ |    |
|  |  | Supabase SDK | | FastAPI    | | Ollama   | | Claude   | |Three.js| |    |
|  |  | (Auth+DB+    | | Backend    | | (Local   | | (Cloud   | | (WebGL)| |    |
|  |  |  Realtime)   | | (REST)     | |  AI)     | |  AI)     | |        | |    |
|  |  +--------------+ +------------+ +----------+ +----------+ +-------+ |    |
|  +----------------------------------------------------------------------+    |
+------------------------------------------------------------------------------+
```

### 1.4 Key Metrics & SLAs

| Metric | Target | Measurement |
|---|---|---|
| **LCP** | <=1.5s (P75) | Lighthouse RUM, Sentry Performance |
| **FID / INP** | <=50ms / <=100ms | Web Vitals library, Chrome UX Report |
| **CLS** | <=0.05 | Web Vitals library |
| **Initial JS** | <=80KB gzipped | next/bundle-analyzer |
| **TTI** | <=2.5s | Lighthouse |
| **API response (P95)** | <=500ms | Sentry Performance |
| **Offline read availability** | 100% of cached data | PWA audit |
| **Test coverage** | >=90% unit, >=80% integration, 100% critical E2E | Vitest + Playwright |
| **Accessibility** | WCAG 2.2 AA | axe-core + manual audit |
| **Up time** | 99.9% (frontend SPA) | Vercel status |

---

## 2. Frontend Principles

### 2.1 Architecture Decision Records (as Principles)

| # | Principle | Rationale | Applies To |
|---|---|---|---|
| **ADR-FE-001** | Use Next.js App Router over Pages Router | RSC streaming, nested layouts, route groups, parallel routes | Route architecture |
| **ADR-FE-002** | Prefer Server Components by default; add 'use client' only where interactivity is required | Reduces client JS by ~40%, improves SEO, enables streaming SSR | Component architecture |
| **ADR-FE-003** | Separate state into six layers: server (TanStack Query), client (Zustand), realtime (Supabase), offline (IndexedDB), AI (state machine), search (command palette) | Clear ownership, testability, independent scalability | State architecture |
| **ADR-FE-004** | Use TanStack Query for all server data fetching, not Zustand | Built-in caching, deduplication, stale-while-revalidate, optimistic updates | Data architecture |
| **ADR-FE-005** | Adopt shadcn/ui for primitives, custom components for domain-specific composites | Design consistency, accessibility out of box, customizable via Tailwind | Component architecture |
| **ADR-FE-006** | Implement offline-first via IndexedDB mutation queue + Workbox service worker | Reliable operation on unreliable networks, user trust | Offline architecture |
| **ADR-FE-007** | All component boundaries should be error-bounded at module level, with optional component-level wrapping | Isolate failures, prevent cascade crashes | Error handling |
| **ADR-FE-008** | Animation should use Framer Motion for page transitions, GSAP only for complex timeline-based animations | Framer Motion is React-native; GSAP is reserved for scroll-driven and multi-stage animations | Performance |
| **ADR-FE-009** | Observable from day one: Sentry for errors, PostHog for product analytics, Web Vitals for performance | Data-driven decisions, proactive issue detection | Observability |
| **ADR-FE-010** | Every route can be rendered via SSR, SSG, ISR, or CSR -- determined by data freshness requirements | Right-sizing rendering strategy per page | Route architecture |
| **ADR-FE-011** | Use clsx or tailwind-merge for conditional class composition -- never template literals | Consistent merging, no conflicts, readable | Component architecture |
| **ADR-FE-012** | Environment variables validated at build time via Zod schema, not ad-hoc checks | Fail fast, document all required vars | Security |

### 2.2 Component Design Contract

Every component in the system must satisfy:

```
- Accepts className prop (merged via cn() utility)
- Forwards ref via React.forwardRef (for form controls)
- Provides aria-* attributes matching its semantic role
- Handles disabled, loading, and error states
- Uses design tokens, never raw color/space values
- One file, one named export (default export only for pages)
```

### 2.3 Coding Standards & Conventions

| Construct | Convention | Example | Enforced By |
|---|---|---|---|
| **Components** | PascalCase, named export | export function Button() | ESLint react/prop-types |
| **Hooks** | camelCase + use prefix | useAuth, useNetworkStatus | ESLint react-hooks/rules-of-hooks |
| **Stores** | camelCase + Store suffix | useTaskStore, useUserStore | Convention |
| **Utils** | camelCase | formatDate, cn, showSuccess | Convention |
| **Types/Interfaces** | PascalCase | Task, User, TaskStore | TypeScript strict |
| **Files** | kebab-case | task-card.tsx, use-auth.ts | ESLint import/check |
| **Constants** | UPPER_SNAKE | MAX_RETRY_COUNT, API_BASE_URL | Convention |
| **Imports** | Strict 4-group ordering | React -> External -> Internal -> Relative | ESLint import/order |
| **CSS** | Tailwind utility classes via cn() | cn('btn', 'btn-primary', className) | Convention |

**Imports order (enforced by ESLint):**

```typescript
// 1. React / Next.js
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

// 2. External libraries
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Plus, Trash2 } from 'lucide-react'

// 3. Internal modules & utilities
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { cn } from '@/lib/utils'
import type { Task } from '@/types/task'

// 4. Relative imports
import { TaskCard } from './task-card'
import { EmptyState } from '../ui/empty-state'
```

**TypeScript Strict Rules:**

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true
  }
}
```

- **NEVER use any**. Use unknown with type guards.
- Use interface for object shapes, type for unions/intersections.
- All API responses must have a typed schema (Zod or interface).

---

## 3. Folder Structure

### 3.1 Target Directory Tree

```
apps/web/
├── .next/                              # Build output (gitignored)
├── public/
│   ├── manifest.json                   # PWA manifest
│   ├── sw.js                           # Service worker (generated)
│   ├── icons/                          # App icons
│   │   ├── icon-192x192.png
│   │   ├── icon-512x512.png
│   │   └── icon-512x512-maskable.png
│   └── fonts/                          # Self-hosted font fallbacks
│
├── app/
│   ├── globals.css                     # Global styles + Tailwind v4 layers
│   ├── layout.tsx                      # Root layout (fonts, metadata, providers)
│   ├── page.tsx                        # Landing page (SSR)
│   ├── not-found.tsx                   # 404 page
│   ├── error.tsx                       # Global error boundary
│   ├── loading.tsx                     # Root loading state
│   │
│   ├── login/
│   │   ├── page.tsx                    # Login page (CSR, no auth required)
│   │   └── actions.ts                  # Server actions for auth
│   │
│   ├── (dashboard)/                    # Route group -- shared dashboard layout
│   │   ├── layout.tsx                  # Sidebar + Navbar wrapper + OfflineBanner
│   │   │
│   │   ├── (overview)/
│   │   │   └── dashboard/
│   │   │       ├── page.tsx            # Home dashboard (SSR + client islands)
│   │   │       ├── loading.tsx         # Dashboard skeleton
│   │   │       └── error.tsx           # Dashboard error boundary
│   │   │
│   │   ├── (modules)/
│   │   │   ├── tasks/
│   │   │   │   ├── page.tsx            # Task list (CSR)
│   │   │   │   ├── [id]/
│   │   │   │   │   └── page.tsx        # Task detail (SSR)
│   │   │   │   ├── loading.tsx
│   │   │   │   └── error.tsx
│   │   │   ├── courses/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   ├── goals/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   ├── habits/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   ├── sleep/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   ├── income/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   ├── projects/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   ├── ideas/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   ├── resources/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   ├── opportunities/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   ├── academics/
│   │   │   │   └── page.tsx
│   │   │   ├── youtube/
│   │   │   │   └── page.tsx
│   │   │   ├── time/
│   │   │   │   ├── page.tsx
│   │   │   ├── chat/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   └── automation/
│   │   │       └── page.tsx
│   │   │
│   │   └── @modal/                     # Parallel route for modals
│   │       ├── default.tsx             # No modal by default
│   │       └── (.)tasks/[id]/
│   │           └── page.tsx            # Task detail in modal
│   │
│   ├── (auth)/                         # Route group -- auth pages
│   │   ├── layout.tsx                  # Auth layout (no sidebar)
│   │   ├── register/page.tsx
│   │   ├── forgot-password/page.tsx
│   │   └── reset-password/page.tsx
│   │
│   ├── (public)/                       # Route group -- public pages
│   │   ├── layout.tsx                  # Public layout (header + footer)
│   │   ├── about/page.tsx
│   │   ├── privacy/page.tsx
│   │   └── terms/page.tsx
│   │
│   └── api/
│       ├── auth/
│       │   └── callback/route.ts       # OAuth callback
│       ├── revalidate/route.ts         # On-demand ISR
│       └── health/route.ts             # Health check
│
├── components/
│   ├── ui/                             # shadcn/ui primitives
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── select.tsx
│   │   ├── badge.tsx
│   │   ├── avatar.tsx
│   │   ├── dropdown-menu.tsx
│   │   ├── tabs.tsx
│   │   ├── toast.tsx
│   │   ├── table.tsx
│   │   ├── skeleton.tsx
│   │   ├── tooltip.tsx
│   │   └── command.tsx                 # Command palette (cmdk)
│   │
│   ├── layout/
│   │   ├── sidebar.tsx
│   │   ├── navbar.tsx
│   │   ├── mobile-nav.tsx
│   │   ├── auth-guard.tsx
│   │   └── offline-banner.tsx
│   │
│   ├── shared/
│   │   ├── data-table.tsx
│   │   ├── stat-card.tsx
│   │   ├── filter-tabs.tsx
│   │   ├── empty-state.tsx
│   │   ├── loading-screen.tsx
│   │   ├── error-fallback.tsx
│   │   ├── confirm-dialog.tsx
│   │   ├── page-header.tsx
│   │   └── search-command.tsx
│   │
│   └── features/                       # One subdirectory per module
│       ├── tasks/
│       │   ├── task-card.tsx
│       │   ├── task-list.tsx
│       │   ├── task-form.tsx
│       │   └── task-kanban.tsx
│       ├── courses/
│       │   ├── course-card.tsx
│       │   └── course-progress.tsx
│       ├── goals/
│       │   ├── goal-card.tsx
│       │   └── roadmap-editor.tsx
│       ├── habits/
│       │   ├── habit-card.tsx
│       │   └── habit-calendar.tsx
│       ├── sleep/
│       │   ├── sleep-log-form.tsx
│       │   └── sleep-chart.tsx
│       ├── income/
│       │   ├── income-form.tsx
│       │   └── income-chart.tsx
│       ├── projects/
│       │   ├── project-card.tsx
│       │   └── project-kanban.tsx
│       ├── ideas/
│       │   ├── idea-card.tsx
│       │   └── idea-pipeline.tsx
│       ├── resources/
│       │   ├── resource-card.tsx
│       │   └── resource-search.tsx
│       ├── opportunities/
│       │   ├── opportunity-card.tsx
│       │   └── opportunity-radar.tsx
│       ├── academics/
│       │   ├── course-card.tsx
│       │   └── semester-progress.tsx
│       ├── youtube/
│       │   ├── video-card.tsx
│       │   └── playlist-viewer.tsx
│       ├── time/
│       │   ├── timer.tsx
│       │   ├── time-entry-form.tsx
│       │   └── time-chart.tsx
│       ├── chat/
│       │   ├── chat-message.tsx
│       │   ├── chat-input.tsx
│       │   └── chat-thread.tsx
│       └── automation/
│           ├── trigger-card.tsx
│           └── automation-form.tsx
│
├── hooks/
│   ├── use-auth.ts
│   ├── use-network-status.ts
│   ├── use-realtime.ts
│   ├── use-debounce.ts
│   ├── use-media-query.ts
│   ├── use-intersection-observer.ts
│   ├── use-local-storage.ts
│   └── use-keyboard-shortcut.ts
│
├── lib/
│   ├── supabase/
│   │   ├── client.ts
│   │   ├── server.ts
│   │   └── middleware.ts
│   ├── stores/
│   │   ├── user-store.ts
│   │   ├── task-store.ts
│   │   ├── ui-store.ts
│   │   └── search-store.ts
│   ├── query/
│   │   ├── provider.tsx
│   │   ├── use-tasks.ts
│   │   ├── use-courses.ts
│   │   ├── use-goals.ts
│   │   └── use-user.ts
│   ├── offline/
│   │   ├── db.ts
│   │   ├── sync.ts
│   │   └── conflict.ts
│   ├── ai/
│   │   ├── chat-store.ts
│   │   └── stream.ts
│   ├── utils/
│   │   ├── cn.ts
│   │   ├── format.ts
│   │   ├── validators.ts
│   │   └── constants.ts
│   └── types/
│       ├── task.ts
│       ├── user.ts
│       ├── course.ts
│       ├── goal.ts
│       └── ...
│
├── __tests__/
│   ├── unit/
│   │   ├── hooks/
│   │   ├── stores/
│   │   └── utils/
│   ├── integration/
│   │   └── features/
│   └── setup.ts
│
├── e2e/
│   ├── playwright.config.ts
│   └── fixtures/
│       ├── auth.ts
│       └── db.ts
│
├── package.json
├── next.config.ts
├── postcss.config.mjs
├── tsconfig.json
├── vitest.config.ts
├── Dockerfile
└── .env.local
```

### 3.2 Current vs Target Structure

| Aspect | Current (v14) | Target (v15+) |
|---|---|---|
| **Config** | next.config.js (CommonJS) | next.config.ts (ESM, typed) |
| **PostCSS** | postcss.config.js | postcss.config.mjs |
| **Components** | Flat components/ (14 files) | Layered ui/ + layout/ + shared/ + features/ |
| **Stores** | lib/taskStore.ts, lib/userStore.ts | lib/stores/ directory |
| **Queries** | Inline in Zustand stores | lib/query/ with TanStack Query hooks |
| **Tests** | Ad-hoc | __tests__/unit/, __tests__/integration/, e2e/ |
| **Supabase** | lib/supabase.ts, lib/supabase-server.ts | lib/supabase/client.ts, server.ts, middleware.ts |
| **Hooks** | 3 hooks | 8 hooks |

### 3.3 Boundary Rules

```
  app/        -> Route pages, layouts, error/loading files -- keep thin
  components/ -> Reusable UI units layerered by abstraction
    ui/       -> shadcn/ui primitives (can be regenerated)
    layout/   -> App shell components (sidebar, navbar)
    shared/   -> Cross-module composites (DataTable, EmptyState)
    features/ -> One module = one subdirectory
  hooks/      -> Generic reusable hooks (not module-specific)
  lib/        -> Pure logic: no React imports
    stores/   -> Zustand (client state only)
    query/    -> TanStack Query hooks (server state only)
    offline/  -> IndexedDB + sync queue (no React)
    utils/    -> cn(), format(), validators
  __tests__/  -> Mirror src structure
  e2e/        -> Playwright config + specs
```

### 3.4 Migration Path (Phase 1)

```
1. Create directory structure (components/ui/, lib/stores/, lib/query/, hooks/)
2. Move existing files to new locations with barrel exports
3. Add shadcn/ui init (npx shadcn@latest init)
4. Replace flat components/UI.tsx with individual ui/*.tsx components
5. Update all import paths in app/ pages
6. Delete old flat files
7. Verify all imports resolve (npm run type-check)
```

---

## 4. Route Architecture

### 4.1 Route Map

| Route | Layout | Rendering | Auth | Module | Phase |
|---|---|---|---|---|---|
| / | (public) | SSR | Public | Landing page | Already done |
| /login | (auth) | CSR | Guest only | Auth | Already done |
| /register | (auth) | CSR | Guest only | Auth | Phase 2 |
| /forgot-password | (auth) | CSR | Guest only | Auth | Phase 2 |
| /about | (public) | SSR/ISR | Public | Info | Phase 2 |
| /privacy | (public) | SSR/ISR | Public | Legal | Phase 2 |
| /terms | (public) | SSR/ISR | Public | Legal | Phase 2 |
| /dashboard | (dashboard) | SSR + islands | Required | Overview | Already done |
| /tasks | (dashboard) | CSR | Required | Tasks | Already done |
| /tasks/[id] | (dashboard) | SSR | Required | Task detail | Phase 2 |
| /courses | (dashboard) | CSR | Required | Courses | Already done |
| /courses/[id] | (dashboard) | SSR | Required | Course detail | Phase 2 |
| /goals | (dashboard) | CSR | Required | Goals | Already done |
| /goals/[id] | (dashboard) | SSR | Required | Goal detail | Phase 2 |
| /habits | (dashboard) | CSR | Required | Habits | Already done |
| /sleep | (dashboard) | CSR | Required | Sleep | Already done |
| /income | (dashboard) | CSR | Required | Income | Already done |
| /projects | (dashboard) | CSR | Required | Projects | Already done |
| /projects/[id] | (dashboard) | SSR | Required | Project detail | Phase 2 |
| /ideas | (dashboard) | CSR | Required | Ideas | Already done |
| /ideas/[id] | (dashboard) | SSR | Required | Idea detail | Phase 2 |
| /resources | (dashboard) | CSR | Required | Resources | Already done |
| /resources/[id] | (dashboard) | SSR | Required | Resource detail | Phase 2 |
| /opportunities | (dashboard) | CSR | Required | Opportunities | Already done |
| /opportunities/[id] | (dashboard) | SSR | Required | Opp detail | Phase 2 |
| /academics | (dashboard) | CSR | Required | Academics | Already done |
| /youtube | (dashboard) | CSR | Required | YouTube | Already done |
| /time | (dashboard) | CSR | Required | Time | Already done |
| /chat | (dashboard) | CSR | Required | AI Chat | Already done |
| /chat/[id] | (dashboard) | CSR | Required | Chat thread | Phase 2 |
| /automation | (dashboard) | CSR | Required | Automation | Already done |
| /api/auth/callback | -- | Edge | Public | OAuth | Already done |
| /api/revalidate | -- | Edge | Admin | ISR | Phase 2 |
| /api/health | -- | Edge | Public | Monitoring | Phase 2 |

### 4.2 Route Groups

```
app/
├── (public)/              -> Landing, about, privacy, terms
│   └── layout.tsx         -> Public layout (minimal header + footer)
├── (auth)/                -> Login, register, password reset
│   └── layout.tsx         -> Auth layout (centered card, no sidebar)
├── (dashboard)/           -> All authenticated module pages
│   └── layout.tsx         -> Dashboard layout (sidebar + navbar)
│       ├── (overview)/    -> Dashboard home (aggregate widgets)
│       └── (modules)/     -> 16 module pages
└── api/                   -> Next.js route handlers
```

### 4.3 Rendering Strategy Matrix

| Strategy | When to Use | Current Routes | Target Routes |
|---|---|---|---|
| **SSR** (Server Components) | SEO-critical, initial page load | /, /dashboard | /, /dashboard, /[module]/[id] |
| **CSR** ('use client') | Heavy interactivity, realtime | All 16 module pages | Main list pages |
| **SSG** (Static Generation) | Content never changes | None | /about, /privacy, /terms |
| **ISR** (ISR) | Content that changes rarely | None | Landing page sections, public docs |
| **Streaming SSR** | Slow data dependencies | None | Dashboard with Suspense boundaries |
| **Edge SSR** | Global low-latency | None | Public pages, auth callbacks |

### 4.4 Parallel Routes & Intercepting Routes

**Parallel Route Pattern (Phase 2):**

```typescript
// app/(dashboard)/layout.tsx
export default function DashboardLayout({
  children,
  modal,
}: {
  children: React.ReactNode
  modal: React.ReactNode
}) {
  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1 ml-60">
        <Navbar />
        <main className="pt-20 px-6 pb-6">{children}</main>
        {modal}
      </div>
    </div>
  )
}
```

**Intercepting Route Pattern (Phase 2):**

```typescript
// app/(dashboard)/@modal/(.)tasks/[id]/page.tsx
'use client'

import { Dialog } from '@/components/ui/dialog'
import { TaskDetail } from '@/components/features/tasks/task-detail'

export default function TaskDetailModal({ params }: { params: { id: string } }) {
  return (
    <Dialog open onOpenChange={() => window.history.back()}>
      <TaskDetail id={params.id} />
    </Dialog>
  )
}
```

### 4.5 Deep Linking Specification

Every list item in every module must be deep-linkable:

```
/tasks                           -> Full task list
/tasks?filter=pending            -> Filtered task list
/tasks?sort=due_date&order=asc   -> Sorted task list
/tasks?page=2                    -> Paginated task list
/tasks/[id]                      -> Task detail (full page)
/tasks/[id]?from=list            -> Detail with back-navigation context
```

### 4.6 Current State Audit

**Current realities:**
- All 16 module pages are 'use client' -- no SSR usage beyond landing page and dashboard
- No [id] detail routes exist (list-only for every module)
- No parallel routes, no intercepting routes
- Route parameters not used in module pages (state-based filtering only)
- 3 route groups exist: root, (dashboard), /login

**Migration plan:**
- **Phase 1:** Add loading.tsx and error.tsx to all module directories
- **Phase 2:** Create [id] detail routes for each module with SSR data fetching
- **Phase 2:** Add @modal parallel route for detail modals
- **Phase 2:** Convert dashboard to SSR with Suspense boundaries for each widget
- **Phase 3:** Add (public) and (auth) route groups

---

## 5. Layout Architecture

### 5.1 Layout Hierarchy

```
RootLayout (app/layout.tsx)
├── <html> with font variables (Syne, DM Sans, JetBrains Mono)
├── <body> with antialiased + bg-background
│   ├── <Toaster /> (react-hot-toast, bottom-right)
│   │
│   ├── PublicLayout -> (public) route group
│   │   ├── PublicHeader (minimal logo + nav links)
│   │   └── <main> page content
│   │
│   ├── AuthLayout -> (auth) route group
│   │   └── CenteredCardLayout (logo + card container)
│   │
│   └── DashboardLayout -> (dashboard) route group
│       ├── Sidebar (fixed left, responsive)
│       │   ├── Logo/Brand
│       │   ├── NavItems (16 module links with icons)
│       │   ├── Settings link
│       │   └── UserInfo at bottom
│       ├── MainArea (flex-1)
│       │   ├── OfflineBanner (conditional)
│       │   ├── Navbar (top, sticky)
│       │   │   ├── Breadcrumb
│       │   │   ├── SearchTrigger (Cmd+K)
│       │   │   ├── NotificationBell
│       │   │   └── UserMenu (avatar dropdown)
│       │   ├── <main> page content
│       │   │   └── {children} + @modal parallel route
│       │   └── MobileNav (bottom bar, visible on < md)
│       └── CommandDialog (global Cmd+K overlay)
```

### 5.2 Layout States

| Layout | Desktop (>=1024px) | Tablet (768-1023px) | Mobile (<768px) |
|---|---|---|---|
| **Sidebar** | Expanded, 240px fixed left | Collapsed, 64px icon-only | Hidden, slide-in drawer |
| **Navbar** | Full (breadcrumb + search + bell + avatar) | Compact (search icon + avatar) | Back button + title + hamburger |
| **Main content** | Padding pl-60 pt-20 px-6 | Padding pl-16 pt-20 px-4 | Padding pt-16 px-4 pb-20 |
| **Mobile nav** | Hidden | Hidden | Fixed bottom, 5-tab FAB |
| **Modal** | Centered overlay, max-w-lg | Full-width, 90% max | Full-screen swipeable |

### 5.3 Responsive Breakpoint Hook

```typescript
// hooks/use-media-query.ts
'use client'

import { useEffect, useState } from 'react'

const BREAKPOINTS = {
  sm: 640, md: 768, lg: 1024, xl: 1280, '2xl': 1536,
} as const

export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false)
  useEffect(() => {
    const mql = window.matchMedia(query)
    setMatches(mql.matches)
    const handler = (e: MediaQueryListEvent) => setMatches(e.matches)
    mql.addEventListener('change', handler)
    return () => mql.removeEventListener('change', handler)
  }, [query])
  return matches
}

export function useBreakpoint(b: keyof typeof BREAKPOINTS) {
  return useMediaQuery(`(min-width: ${BREAKPOINTS[b]}px)`)
}
```

### 5.4 Current State Audit

**Current layout structure:**

```typescript
// app/layout.tsx -- Root layout
import { Syne, DM_Sans, JetBrains_Mono } from 'next/font/google'
import { Toaster } from 'react-hot-toast'

const syne = Syne({ subsets: ['latin'], variable: '--font-syne', display: 'swap' })
const dmSans = DM_Sans({ subsets: ['latin'], variable: '--font-dm-sans', display: 'swap' })
const jetbrainsMono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-jetbrains', display: 'swap' })

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${syne.variable} ${dmSans.variable} ${jetbrainsMono.variable}`}>
      <body className="font-body antialiased">
        <Toaster position="bottom-right" toastOptions={{ duration: 4000 }} />
        {children}
      </body>
    </html>
  )
}

// app/(dashboard)/layout.tsx -- Dashboard layout
import Sidebar from '@/components/Sidebar'
import Navbar from '@/components/Navbar'
import OfflineBanner from '@/components/OfflineBanner'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1 ml-60">
        <OfflineBanner />
        <Navbar />
        <main className="pt-20 px-6 pb-6">{children}</main>
      </div>
    </div>
  )
}
```

**Current realities:**
- Root layout handles fonts + Toaster (correct pattern)
- Dashboard layout uses ml-60 for sidebar offset (not responsive)
- No mobile/tablet sidebar collapse
- No mobile bottom navigation
- No @modal parallel route slot
- No public or auth route groups
- Sidebar and Navbar are client components (necessary for interactivity)

**Migration plan:**
- **Phase 1:** Add responsive sidebar (collapsible via CSS + Framer Motion)
- **Phase 1:** Add mobile bottom nav component
- **Phase 2:** Add @modal parallel route to dashboard layout
- **Phase 2:** Create (public) and (auth) route groups with layouts
- **Phase 2:** Add CommandDialog to dashboard layout

---

## 6. Component Architecture

### 6.1 Five-Layer Hierarchy

```
Layer 1: Atoms (shadcn/ui + custom primitives)
  +-- ui/button, ui/input, ui/card, ui/dialog, ui/badge, ui/avatar
  +-- Pure, single-purpose, fully accessible

Layer 2: Molecules (shared composites)
  +-- shared/data-table, shared/stat-card, shared/filter-tabs
  +-- Compose 2+ atoms, data-agnostic

Layer 3: Organisms (layout + app shell)
  +-- layout/sidebar, layout/navbar, layout/mobile-nav
  +-- Application structure, navigation context

Layer 4: Feature Components (domain-specific)
  +-- features/tasks/task-card, features/tasks/task-form
  +-- One module = one subdirectory, hooks-aware

Layer 5: Pages (route entry points)
  +-- app/tasks/page.tsx, app/courses/page.tsx
  +-- Thin orchestration: compose features, handle auth
```

### 6.2 Component Implementation Template

```typescript
// components/features/tasks/task-card.tsx
'use client'

import { forwardRef } from 'react'
import { motion } from 'framer-motion'
import { Checkbox } from '@/components/ui/checkbox'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils/cn'
import type { Task } from '@/lib/types/task'
import { formatDate } from '@/lib/utils/format'

interface TaskCardProps {
  task: Task
  onComplete: (id: string) => void
  onDelete: (id: string) => void
  className?: string
}

export const TaskCard = forwardRef<HTMLDivElement, TaskCardProps>(
  function TaskCard({ task, onComplete, onDelete, className }, ref) {
    return (
      <motion.div
        ref={ref}
        layout
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, x: -10 }}
        className={cn(
          'card card-interactive flex items-center gap-4 p-4',
          task.status === 'completed' && 'opacity-60',
          className
        )}
        role="listitem"
        aria-label={'Task: ' + task.title}
      >
        <Checkbox
          checked={task.status === 'completed'}
          onCheckedChange={() => onComplete(task.id)}
          aria-label={'Mark "' + task.title + '" as complete'}
        />
        <div className="flex-1 min-w-0">
          <p className={cn(
            'font-medium truncate',
            task.status === 'completed' && 'line-through text-text-tertiary'
          )}>
            {task.title}
          </p>
          {task.due_date && (
            <p className="text-sm text-text-secondary">{formatDate(task.due_date)}</p>
          )}
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <Badge variant={task.priority}>
            {task.priority}
          </Badge>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => onDelete(task.id)}
            aria-label={'Delete task "' + task.title + '"'}
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </motion.div>
    )
  }
)
```

### 6.3 Component Category Inventory

| Category | Count (Current) | Count (Target) | Purpose |
|---|---|---|---|
| **ui/** (shadcn primitives) | 0 | 14 | Buttons, inputs, cards, dialogs, etc. |
| **layout/** | 3 | 5 | Sidebar, Navbar, MobileNav, AuthGuard, OfflineBanner |
| **shared/** | 0 | 8 | DataTable, StatCard, FilterTabs, EmptyState, etc. |
| **features/** | 0 | ~40+ | Module-specific composites |
| **Custom (flat)** | 14 | 0 | Being replaced/migrated |

**Custom components currently in components/:**
- UI.tsx (monolithic -- Button, Input, Select, Card, Toast, Skeleton, EmptyState)
- Button.tsx (4 variants)
- Card.tsx (Card, CardHeader, CardTitle, CardContent)
- Input.tsx (Form inputs with labels, errors, validation)
- Modal.tsx (Accessible modal with Framer Motion)
- Sidebar.tsx (Dashboard navigation sidebar)
- Navbar.tsx (Top navigation bar)
- ThreeBackground.tsx (Cyberpunk three.js background)
- RoadmapEditor.tsx (Goal roadmap editor)
- OfflineBanner.tsx (Connectivity banner)
- DataTable.tsx (TanStack Table wrapper)
- FormField.tsx (Form field wrapper)
- Checkbox.tsx (Custom checkbox)

### 6.4 Migration Strategy

```
Current -> Target mapping:

UI.tsx (Button, Input, Select, Card, Skeleton) -> ui/button.tsx, ui/input.tsx, ui/select.tsx, ui/card.tsx, ui/skeleton.tsx
UI.tsx (EmptyState) -> shared/empty-state.tsx
UI.tsx (Toast) -> ui/toast.tsx
Button.tsx -> ui/button.tsx
Card.tsx -> ui/card.tsx
Input.tsx -> ui/input.tsx
Modal.tsx -> ui/dialog.tsx
Checkbox.tsx -> ui/checkbox.tsx
Sidebar.tsx -> layout/sidebar.tsx
Navbar.tsx -> layout/navbar.tsx
OfflineBanner.tsx -> layout/offline-banner.tsx
DataTable.tsx -> shared/data-table.tsx
FormField.tsx -> shared/form-field.tsx
ThreeBackground.tsx -> kept as-is
RoadmapEditor.tsx -> features/goals/roadmap-editor.tsx
```

### 6.5 Utility: cn()

```typescript
// lib/utils/cn.ts
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

---

## 7. State Architecture

### 7.1 State Decision Matrix

| Concern | Tool | Scope | Persistence | Sync | Testability |
|---|---|---|---|---|---|
| **Server State** | TanStack Query v5 | Global (per module) | In-memory cache (gcTime) | Auto-refetch + invalidate | Mock query client |
| **Client State (global)** | Zustand v5 | App-wide | Partial (persist middleware) | Manual | Standalone (no React) |
| **Client State (local)** | useState / useReducer | Component | None | None | Render + fireEvent |
| **URL State** | useSearchParams | Page | URL | Navigation | Mock router |
| **Realtime State** | Supabase Realtime | Per subscription | Supabase (source) | WebSocket push | Mock channel |
| **Offline State** | IndexedDB (via idb) | App-wide | IndexedDB | Mutation queue replay | fake-indexeddb |
| **AI State** | Zustand (chat store) | Chat module | In-memory | Streaming (ReadableStream) | Mock SSE stream |
| **Search State** | Zustand (search store) | App-wide | In-memory | Command palette | Standalone |

### 7.2 Server State -- TanStack Query

**Provider setup (Phase 2):**

```typescript
// lib/query/provider.tsx
'"'"'use client'"'"'

import { QueryClient, QueryClientProvider } from '"'"'@tanstack/react-query'"'"'
import { ReactQueryDevtools } from '"'"'@tanstack/react-query-devtools'"'"'
import { useState } from '"'"'react'"'"'

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30 * 1000,        // 30s before considered stale
            gcTime: 5 * 60 * 1000,        // 5min in garbage collection
            retry: 2,                     // Retry twice on failure
            refetchOnWindowFocus: true,
            refetchOnReconnect: true,
          },
          mutations: {
            retry: 1,
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
```

**Hook example:**

```typescript
// lib/query/use-tasks.ts
import { useQuery, useMutation, useQueryClient } from '"'"'@tanstack/react-query'"'"'
import { supabase } from '"'"'@/lib/supabase/client'"'"'
import type { Task } from '"'"'@/lib/types/task'"'"'

const TASKS_KEY = ['"'"'tasks'"'"'] as const

export function useTasks(userId: string) {
  return useQuery({
    queryKey: [...TASKS_KEY, userId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('"'"'tasks'"'"')
        .select('"'"'*'"'"')
        .eq('"'"'user_id'"'"', userId)
        .order('"'"'created_at'"'"', { ascending: false })
      if (error) throw error
      return data as Task[]
    },
    enabled: !!userId,
  })
}

export function useCreateTask() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (task: Partial<Task>) => {
      const { data, error } = await supabase
        .from('"'"'tasks'"'"').insert(task).select().single()
      if (error) throw error
      return data as Task
    },
    onSuccess: (newTask) => {
      queryClient.invalidateQueries({ queryKey: [...TASKS_KEY, newTask.user_id] })
    },
  })
}
```

### 7.3 Client State -- Zustand

**Current stores (Zustand v4):**

```typescript
// lib/stores/task-store.ts (Zustand v4 -- current)
'"'"'use client'"'"'

import { create } from '"'"'zustand'"'"'
import { supabase } from '"'"'./supabase'"'"'

interface TaskStore {
  tasks: Task[]
  loading: boolean
  error: string | null
  fetchTasks: () => Promise<void>
  addTask: (task: Partial<Task>) => Promise<void>
  updateTask: (id: string, updates: Partial<Task>) => Promise<void>
  deleteTask: (id: string) => Promise<void>
  completeTask: (id: string) => Promise<void>
}

export const useTaskStore = create<TaskStore>((set, get) => ({
  tasks: [],
  loading: false,
  error: null,
  fetchTasks: async () => {
    set({ loading: true, error: null })
    try {
      const { data, error } = await supabase
        .from('"'"'tasks'"'"').select('"'"'*'"'"').order('"'"'created_at'"'"', { ascending: false })
      if (error) throw error
      set({ tasks: data || [], loading: false })
    } catch (error: any) {
      set({ error: error.message, loading: false })
    }
  },
  // ... addTask, updateTask, deleteTask, completeTask
}))
```

**Refactored stores for Phase 2 (Zustand v5, UI-only state):**

```typescript
// lib/stores/ui-store.ts (Zustand v5 -- target)
import { create } from '"'"'zustand'"'"'
import { persist } from '"'"'zustand/middleware'"'"'

interface UIStore {
  sidebarOpen: boolean
  sidebarCollapsed: boolean
  theme: '"'"'dark'"'"' | '"'"'light'"'"'
  toggleSidebar: () => void
  setSidebarCollapsed: (collapsed: boolean) => void
  setTheme: (theme: '"'"'dark'"'"' | '"'"'light'"'"') => void
}

export const useUIStore = create<UIStore>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      sidebarCollapsed: false,
      theme: '"'"'dark'"'"',
      toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: '"'"'ui-preferences'"'"',
      partialize: (state) => ({ theme: state.theme, sidebarCollapsed: state.sidebarCollapsed }),
    }
  )
)
```

**Separation of concerns after migration:**

| Current (Zustand v4 -- mixed server + client) | Target (Split) |
|---|---|
| taskStore.ts (fetch from Supabase + CRUD + state) | -> query/use-tasks.ts (TanStack Query) + stores/task-store.ts (local UI filters) |
| userStore.ts (fetch from Supabase + auth) | -> query/use-user.ts + stores/user-store.ts (auth session) |
| -- | -> stores/ui-store.ts (new -- sidebar, theme, preferences) |
| -- | -> stores/search-store.ts (new -- command palette) |

### 7.4 Offline State -- IndexedDB

```typescript
// lib/offline/db.ts
import { openDB, type IDBPDatabase } from '"'"'idb'"'"'

const DB_NAME = '"'"'second-brain-offline'"'"'
const DB_VERSION = 1

export interface QueuedMutation {
  id: string
  table: string
  action: '"'"'INSERT'"'"' | '"'"'UPDATE'"'"' | '"'"'DELETE'"'"'
  data: any
  timestamp: number
  retryCount: number
}

let dbPromise: Promise<IDBPDatabase> | null = null

export function getDB() {
  if (!dbPromise) {
    dbPromise = openDB(DB_NAME, DB_VERSION, {
      upgrade(db) {
        if (!db.objectStoreNames.contains('"'"'tasks'"'"')) {
          db.createObjectStore('"'"'tasks'"'"', { keyPath: '"'"'id'"'"' })
        }
        if (!db.objectStoreNames.contains('"'"'queue'"'"')) {
          db.createObjectStore('"'"'queue'"'"', { keyPath: '"'"'id'"'"', autoIncrement: true })
        }
      },
    })
  }
  return dbPromise
}

export async function cacheData(storeName: string, data: any[]) {
  const db = await getDB()
  const tx = db.transaction(storeName, '"'"'readwrite'"'"')
  await Promise.all([...data.map((item) => tx.store.put(item)), tx.done])
}

export async function getCachedData(storeName: string): Promise<any[]> {
  const db = await getDB()
  return db.getAll(storeName)
}

export async function enqueueMutation(mutation: Omit<QueuedMutation, '"'"'id'"'"'>) {
  const db = await getDB()
  return db.add('"'"'queue'"'"', { ...mutation, timestamp: Date.now(), retryCount: 0 })
}

export async function dequeueMutations(): Promise<QueuedMutation[]> {
  const db = await getDB()
  const all = await db.getAll('"'"'queue'"'"')
  await db.clear('"'"'queue'"'"')
  return all
}
```

### 7.5 AI State -- Streaming State Machine

```typescript
// lib/ai/chat-store.ts
import { create } from '"'"'zustand'"'"'

export type StreamStatus = '"'"'idle'"'"' | '"'"'connecting'"'"' | '"'"'streaming'"'"' | '"'"'done'"'"' | '"'"'error'"'"'

export interface ChatMessage {
  id: string
  role: '"'"'user'"'"' | '"'"'assistant'"'"' | '"'"'system'"'"' | '"'"'thinking'"'"'
  content: string
  timestamp: number
}

interface ChatStore {
  messages: ChatMessage[]
  status: StreamStatus
  error: string | null
  addMessage: (msg: Omit<ChatMessage, '"'"'id'"'"' | '"'"'timestamp'"'"'>) => void
  appendToLastAssistant: (chunk: string) => void
  setStatus: (status: StreamStatus) => void
  setError: (error: string | null) => void
  clearMessages: () => void
}

export const useChatStore = create<ChatStore>((set, get) => ({
  messages: [],
  status: '"'"'idle'"'"',
  error: null,
  addMessage: (msg) =>
    set((s) => ({
      messages: [...s.messages, { ...msg, id: crypto.randomUUID(), timestamp: Date.now() }],
    })),
  appendToLastAssistant: (chunk) =>
    set((s) => {
      const messages = [...s.messages]
      const last = messages[messages.length - 1]
      if (last?.role === '"'"'assistant'"'"') {
        messages[messages.length - 1] = { ...last, content: last.content + chunk }
      }
      return { messages }
    }),
  setStatus: (status) => set({ status }),
  setError: (error) => set({ error, status: '"'"'error'"'"' }),
  clearMessages: () => set({ messages: [], status: '"'"'idle'"'"', error: null }),
}))
```

### 7.6 Current State Audit

**Current realities:**
- Two Zustand v4 stores: taskStore.ts (116 lines) and userStore.ts (77 lines)
- Both mix server state (Supabase calls) with client state (local arrays)
- No caching, deduplication, or stale-while-revalidate
- No query key management
- No URL state management (filters in local useState)
- No offline persistence
- No AI streaming state machine
- No search/command palette state

**Migration plan:**
- **Phase 1:** Upgrade Zustand v4 -> v5
- **Phase 2:** Create TanStack Query hooks for each module
- **Phase 2:** Strip down Zustand stores to UI-only concerns
- **Phase 2:** Add persist middleware to UI store
- **Phase 2:** Create AI chat store with streaming state machine
- **Phase 3:** Add IndexedDB offline store + mutation queue

---

## 8. Data Architecture

### 8.1 Data Flow Overview

```
User Action
  |
  v
Component (feature/task-card)
  |
  +-- Client Mutation -> TanStack Query useMutation
  |     |
  |     +-- [Online]  -> Supabase REST API
  |     |                  |
  |     |                  +-- Success -> invalidateQueries -> UI updates
  |     |                  +-- Failure -> error toast + retry
  |     |
  |     +-- [Offline] -> IndexedDB sync queue
  |                        |
  |                        +-- Online -> replay queue -> invalidateQueries
  |
  +-- Optimistic UI -> setQueryData (instant update)
                          |
                          +-- On server confirm -> invalidateQueries
                          +-- On server reject  -> rollback toast + refetch
```

### 8.2 Query Key Convention

```typescript
export const queryKeys = {
  tasks: {
    all: ['"'"'tasks'"'"'] as const,
    list: (userId: string) => ['"'"'tasks'"'"', '"'"'list'"'"', userId] as const,
    detail: (taskId: string) => ['"'"'tasks'"'"', '"'"'detail'"'"', taskId] as const,
  },
  courses: {
    all: ['"'"'courses'"'"'] as const,
    list: (userId: string) => ['"'"'courses'"'"', '"'"'list'"'"', userId] as const,
    detail: (courseId: string) => ['"'"'courses'"'"', '"'"'detail'"'"', courseId] as const,
  },
  user: {
    profile: (userId: string) => ['"'"'user'"'"', '"'"'profile'"'"', userId] as const,
  },
}
```

### 8.3 Caching Strategy

| Cache Level | Mechanism | TTL | Purpose |
|---|---|---|---|
| **HTTP** | CDN / Vercel Edge Cache | 1h (public), 0 (auth) | Static assets, public pages |
| **TanStack Query** | In-memory (gcTime) | 5min | Server data with stale-while-revalidate |
| **Supabase Realtime** | WebSocket push | Real-time | Live updates across devices |
| **IndexedDB** | Persistent disk | Until evicted | Offline fallback data |
| **localStorage** | Sync disk (Zustand persist) | Until cleared | UI preferences |
| **Service Worker** | Cache Storage API | SW lifecycle | App shell, static assets |

### 8.4 Optimistic Updates Pattern

```typescript
export function useDeleteTask() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase.from('"'"'tasks'"'"').delete().eq('"'"'id'"'"', id)
      if (error) throw error
    },
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.tasks.all })
      const previousTasks = queryClient.getQueryData(queryKeys.tasks.all)
      queryClient.setQueryData(queryKeys.tasks.all, (old: Task[] = []) =>
        old.filter((t) => t.id !== id)
      )
      return { previousTasks }
    },
    onError: (err, id, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(queryKeys.tasks.all, context.previousTasks)
      }
      showError('"'"'Failed to delete task. It has been restored.'"'"')
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.all })
    },
  })
}
```

### 8.5 Server Component Data Fetching

```typescript
// app/tasks/[id]/page.tsx -- SSR detail page
import { createSupabaseServerClient } from '"'"'@/lib/supabase/server'"'"'
import { TaskDetail } from '"'"'@/components/features/tasks/task-detail'"'"'
import { notFound } from '"'"'next/navigation'"'"'

export default async function TaskDetailPage({ params }: { params: { id: string } }) {
  const supabase = createSupabaseServerClient()
  const { data: task, error } = await supabase
    .from('"'"'tasks'"'"').select('"'"'*'"'"').eq('"'"'id'"'"', params.id).single()

  if (error || !task) notFound()
  return <TaskDetail initialTask={task} />
}
```

### 8.6 Migration Plan

```
Phase 2 -- Server Data Layer:
1. Create QueryProvider in app/layout.tsx
2. Move taskStore.ts -> query/use-tasks.ts (TanStack Query hooks)
3. Move userStore.ts -> query/use-user.ts
4. Create query hooks for each module
5. Update all 16 module pages to use new hooks
6. Delete old inline fetch logic from Zustand stores

Phase 2 -- Optimization:
7. Add query key factory for each module
8. Add optimistic updates for create, update, delete
9. Add pagination via useInfiniteQuery for list-heavy modules
10. Add prefetching for detail pages (hover prefetch)
```

---

## 9. Search Architecture

### 9.1 Search Concerns

| Concern | Tool | Scope | When Used |
|---|---|---|---|
| **Global Command Palette** | cmdk (via shadcn command) | All modules | Cmd+K trigger |
| **Full-Text Search** | Supabase fts (PostgreSQL tsvector) | Per-module | Filter inputs |
| **Client-Side Filter** | JavaScript Array.filter() | Current page | Tab/status filters |
| **Faceted Search** | Supabase queries + client facets | Per-module | Advanced filter panels |

### 9.2 Command Palette (Cmd+K)

```typescript
// components/shared/search-command.tsx
'"'"'use client'"'"'

import { useEffect } from '"'"'react'"'"'
import {
  CommandDialog, CommandEmpty, CommandGroup,
  CommandInput, CommandItem, CommandList,
} from '"'"'@/components/ui/command'"'"'
import { useRouter } from '"'"'next/navigation'"'"'
import { useSearchStore } from '"'"'@/lib/stores/search-store'"'"'

const NAV_ITEMS = [
  { label: '"'"'Dashboard'"'"', route: '"'"'/dashboard'"'"' },
  { label: '"'"'Tasks'"'"', route: '"'"'/tasks'"'"' },
  { label: '"'"'Courses'"'"', route: '"'"'/courses'"'"' },
  { label: '"'"'Goals'"'"', route: '"'"'/goals'"'"' },
  { label: '"'"'Habits'"'"', route: '"'"'/habits'"'"' },
  { label: '"'"'Sleep'"'"', route: '"'"'/sleep'"'"' },
  { label: '"'"'Income'"'"', route: '"'"'/income'"'"' },
  { label: '"'"'Projects'"'"', route: '"'"'/projects'"'"' },
  { label: '"'"'Ideas'"'"', route: '"'"'/ideas'"'"' },
  { label: '"'"'Resources'"'"', route: '"'"'/resources'"'"' },
  { label: '"'"'Opportunities'"'"', route: '"'"'/opportunities'"'"' },
  { label: '"'"'Time'"'"', route: '"'"'/time'"'"' },
  { label: '"'"'Chat'"'"', route: '"'"'/chat'"'"' },
  { label: '"'"'Automation'"'"', route: '"'"'/automation'"'"' },
]

export function SearchCommand() {
  const { open, setOpen } = useSearchStore()
  const router = useRouter()

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === '"'"'k'"'"' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen(!open)
      }
    }
    document.addEventListener('"'"'keydown'"'"', down)
    return () => document.removeEventListener('"'"'keydown'"'"', down)
  }, [open, setOpen])

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="'"'"'Search modules, commands...'"'"'" />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandGroup heading="'"'"'Navigation'"'"'">
          {NAV_ITEMS.map((item) => (
            <CommandItem
              key={item.route}
              onSelect={() => { router.push(item.route); setOpen(false) }}
            >
              <span>{item.label}</span>
            </CommandItem>
          ))}
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  )
}
```

### 9.3 Supabase Full-Text Search

```sql
-- Enable full-text search on tasks table
ALTER TABLE tasks ADD COLUMN search_vector tsvector
  GENERATED ALWAYS AS (
    to_tsvector('"'"'english'"'"', coalesce(title, '"'"''"'"') || '"'"' '"'"' || coalesce(description, '"'"''"'"'))
  ) STORED;

CREATE INDEX tasks_search_idx ON tasks USING GIN(search_vector);
```

```typescript
export function useSearchTasks(userId: string, query: string) {
  return useQuery({
    queryKey: ['"'"'tasks'"'"', '"'"'search'"'"', userId, query],
    queryFn: async () => {
      if (!query.trim()) return []
      const { data, error } = await supabase
        .from('"'"'tasks'"'"').select('"'"'*'"'"')
        .eq('"'"'user_id'"'"', userId)
        .textSearch('"'"'search_vector'"'"', query, { type: '"'"'websearch'"'"', config: '"'"'english'"'"' })
        .limit(20)
      if (error) throw error
      return data as Task[]
    },
    enabled: !!userId && query.length >= 2,
  })
}
```

### 9.4 Migration Plan

- **Phase 2:** Create search-store.ts + SearchCommand component
- **Phase 2:** Add cmdk via npx shadcn@latest add command
- **Phase 2:** Add keyboard shortcut hook (Cmd+K)
- **Phase 3:** Add Supabase full-text search for each module

---

## 10. Command Center Architecture

### 10.1 Command Palette (Cmd+K)

The command palette is the central hub for keyboard-driven navigation. Triggered by Cmd+K (macOS) or Ctrl+K (Windows/Linux).

**Architecture:**
- State managed by search-store.ts (Zustand)
- UI rendered by SearchCommand component (mounted in dashboard layout)
- Commands split into categories: Navigation, Actions, Quick Create, Settings
- Each command can have a keyboard shortcut (shown as badge in palette)

**Command categories:**

| Category | Source | Example Commands |
|---|---|---|
| **Navigation** | Static list (16 modules + detail routes) | "Go to Tasks", "Open Sleep" |
| **Actions** | Static list | "New Task", "Log Sleep" |
| **Quick Create** | Dynamic (per-module) | "Create Task: Buy groceries" |
| **Module Actions** | Dynamic (current page context) | "Complete Task" |
| **Settings** | Static list | "Open Settings", "Change Theme" |

### 10.2 Keyboard Shortcut System

```typescript
// hooks/use-keyboard-shortcut.ts
import { useEffect } from '"'"'react'"'"'

type KeyCombo = {
  key: string
  ctrl?: boolean
  meta?: boolean
  shift?: boolean
  alt?: boolean
}

export function useKeyboardShortcut(
  combo: KeyCombo,
  handler: () => void,
  enabled = true
) {
  useEffect(() => {
    if (!enabled) return
    const listener = (e: KeyboardEvent) => {
      const match =
        e.key.toLowerCase() === combo.key.toLowerCase() &&
        !!e.ctrlKey === !!combo.ctrl &&
        !!e.metaKey === !!combo.meta &&
        !!e.shiftKey === !!combo.shift &&
        !!e.altKey === !!combo.alt
      if (match) { e.preventDefault(); handler() }
    }
    window.addEventListener('"'"'keydown'"'"', listener)
    return () => window.removeEventListener('"'"'keydown'"'"', listener)
  }, [combo, handler, enabled])
}
```

**Planned shortcuts:**

| Shortcut | Action | Scope | Phase |
|---|---|---|---|
| Cmd+K | Toggle command palette | Global | Phase 2 |
| Cmd+B | Toggle sidebar | Global | Phase 2 |
| N | New task | Global | Phase 3 |
| Escape | Close modal / palette | Active | Phase 2 |
| Cmd+Enter | Submit chat message | Chat page | Phase 2 |

### 10.3 Migration Plan

- **Phase 2:** Create keyboard shortcut hook
- **Phase 2:** Build SearchCommand component with cmdk
- **Phase 2:** Register static navigation + action commands
- **Phase 3:** Module-level action registration (context-aware)

---

## 11. Notification Architecture

### 11.1 Notification Channels

| Channel | Tool | Delivery | Persistence | Use Cases |
|---|---|---|---|---|
| **In-app Toast** | react-hot-toast | Bottom-right, auto-dismiss | None (ephemeral) | Success/error feedback |
| **Notification Center** | Custom NotificationBell | Dropdown list | Supabase notifications table | Nudges, reminders, AI briefings |
| **Realtime Push** | Supabase Realtime + Broadcast | WebSocket | In-memory | Live task updates |
| **Push Notification** | Service Worker Push API | Browser notification | SW controlled | Away-from-app alerts |
| **Email** | Resend API (server-triggered) | Email | Email provider | Daily briefing, weekly review |

### 11.2 In-App Toast (Current)

```typescript
// lib/toast.ts (current -- keep as-is)
import toast from '"'"'react-hot-toast'"'"'

export function showSuccess(message: string) {
  toast.success(message, {
    style: { background: '"'"'#13151A'"'"', color: '"'"'#00FFA3'"'"', border: '"'"'1px solid rgba(0, 255, 163, 0.2)'"'"' },
    iconTheme: { primary: '"'"'#00FFA3'"'"', secondary: '"'"'#0A0B0F'"'"' },
  })
}

export function showError(message: string) {
  toast.error(message, {
    style: { background: '"'"'#13151A'"'"', color: '"'"'#EF4444'"'"', border: '"'"'1px solid rgba(239, 68, 68, 0.2)'"'"' },
    iconTheme: { primary: '"'"'#EF4444'"'"', secondary: '"'"'#0A0B0F'"'"' },
    duration: 5000,
  })
}

export function showInfo(message: string) {
  toast(message, {
    style: { background: '"'"'#13151A'"'"', color: '"'"'#818CF8'"'"', border: '"'"'1px solid rgba(129, 140, 248, 0.2)'"'"' },
    iconTheme: { primary: '"'"'#818CF8'"'"', secondary: '"'"'#0A0B0F'"'"' },
  })
}
```

### 11.3 Notification Center (Phase 2)

```typescript
// components/features/notifications/notification-bell.tsx
'"'"'use client'"'"'

import { Bell } from '"'"'lucide-react'"'"'
import { Button } from '"'"'@/components/ui/button'"'"'
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem,
  DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger,
} from '"'"'@/components/ui/dropdown-menu'"'"'
import { useQuery } from '"'"'@tanstack/react-query'"'"'
import { supabase } from '"'"'@/lib/supabase/client'"'"'

interface Notification {
  id: string
  title: string
  body: string
  type: '"'"'nudge'"'"' | '"'"'briefing'"'"' | '"'"'reminder'"'"' | '"'"'opportunity'"'"' | '"'"'system'"'"'
  read: boolean
  created_at: string
  link?: string
}

export function NotificationBell({ userId }: { userId: string }) {
  const { data: notifications = [] } = useQuery({
    queryKey: ['"'"'notifications'"'"', userId],
    queryFn: async () => {
      const { data } = await supabase
        .from('"'"'notifications'"'"').select('"'"'*'"'"')
        .eq('"'"'user_id'"'"', userId).order('"'"'created_at'"'"', { ascending: false }).limit(20)
      return (data || []) as Notification[]
    },
    enabled: !!userId,
  })

  const unreadCount = notifications.filter((n) => !n.read).length

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="'"'"'ghost'"'"'" size="'"'"'icon'"'"'" className="'"'"'relative'"'"'"
          aria-label={'"'"'Notifications ('"'"' + unreadCount + '"'"' unread)'"'"'}>
          <Bell className="'"'"'w-5 h-5'"'"'" />
          {unreadCount > 0 && (
            <span className="'"'"'absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full bg-accent-error text-[10px] font-bold flex items-center justify-center text-white'"'"'">
              {unreadCount > 9 ? '"'"'9+'"'"' : unreadCount}
            </span>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="'"'"'end'"'"'" className="'"'"'w-80'"'"'">
        <DropdownMenuLabel>Notifications</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {notifications.length === 0 ? (
          <p className="'"'"'p-4 text-sm text-text-secondary text-center'"'"'">No notifications</p>
        ) : (
          notifications.map((n) => (
            <DropdownMenuItem key={n.id}>
              <p className="'"'"'text-sm font-medium'"'"'">{n.title}</p>
              <p className="'"'"'text-xs text-text-secondary'"'"'">{n.body}</p>
            </DropdownMenuItem>
          ))
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
```

### 11.4 Current State Audit + Migration Plan

**Current realities:**
- react-hot-toast integration exists (root layout, toast.ts utility)
- Custom toast styling matches cyberpunk theme
- Notification center (bell icon + dropdown) does not exist
- No push notification support
- No Supabase notifications table integration

**Migration plan:**
- **Phase 1:** Keep existing toast system (mature, works well)
- **Phase 2:** Build notification center component
- **Phase 2:** Query Supabase notifications table
- **Phase 3:** Add push notification subscription

---

## 12. Realtime Architecture

### 12.1 Supabase Realtime Channels

```typescript
// hooks/use-realtime.ts (current -- extend with backoff)
'"'"'use client'"'"'

import { useEffect, useCallback, useRef } from '"'"'react'"'"'
import { supabase } from '"'"'@/lib/supabase/client'"'"'
import type { RealtimeChannel } from '"'"'@supabase/supabase-js'"'"'

interface UseRealtimeOptions {
  table: string
  userId: string
  onInsert?: (payload: any) => void
  onUpdate?: (payload: any) => void
  onDelete?: (payload: any) => void
  enabled?: boolean
}

export function useRealtime({ table, userId, onInsert, onUpdate, onDelete, enabled = true }: UseRealtimeOptions) {
  const handlersRef = useRef({ onInsert, onUpdate, onDelete })
  handlersRef.current = { onInsert, onUpdate, onDelete }

  useEffect(() => {
    if (!userId || !enabled) return

    const channel: RealtimeChannel = supabase
      .channel(table + '"'"'_changes'"'"')
      .on('"'"'postgres_changes'"'"',
        { event: '"'"'INSERT'"'"', schema: '"'"'public'"'"', table, filter: '"'"'user_id=eq.'"'"' + userId },
        (payload) => handlersRef.current.onInsert?.(payload.new)
      )
      .on('"'"'postgres_changes'"'"',
        { event: '"'"'UPDATE'"'"', schema: '"'"'public'"'"', table, filter: '"'"'user_id=eq.'"'"' + userId },
        (payload) => handlersRef.current.onUpdate?.(payload.new)
      )
      .on('"'"'postgres_changes'"'"',
        { event: '"'"'DELETE'"'"', schema: '"'"'public'"'"', table, filter: '"'"'user_id=eq.'"'"' + userId },
        (payload) => handlersRef.current.onDelete?.(payload.old)
      )
      .subscribe()

    return () => { supabase.removeChannel(channel) }
  }, [table, userId, enabled])
}
```

### 12.2 Realtime Connection Pooling

| Module | Channel | Events | Phase |
|---|---|---|---|
| Tasks | tasks_changes | INSERT, UPDATE, DELETE | Phase 1 |
| Chat | chat_messages_changes | INSERT | Phase 2 |
| Notifications | notifications_changes | INSERT | Phase 2 |
| Habits | habit_logs_changes | INSERT, UPDATE | Phase 2 |

### 12.3 Current State Audit + Migration Plan

**Current realities:**
- useRealtime hook exists (68 lines) -- supports INSERT, UPDATE, DELETE
- Not used in any module page yet (available but not wired up)
- No reconnection backoff
- No cross-tab broadcast

**Migration plan:**
- **Phase 1:** Wire up useRealtime in task list page (live updates)
- **Phase 2:** Add reconnection backoff, channel lifecycle logging
- **Phase 2:** Add presence tracking for online/offline status
- **Phase 3:** Add cross-tab broadcast for state sync

---

## 13. Offline Architecture

### 13.1 Network Status Detection

```typescript
// hooks/use-network-status.ts (current -- extend with sync trigger)
'"'"'use client'"'"'

import { useEffect, useState } from '"'"'react'"'"'

export function useNetworkStatus() {
  const [isOnline, setIsOnline] = useState(true)

  useEffect(() => {
    setIsOnline(navigator.onLine)
    const handleOnline = () => {
      setIsOnline(true)
      window.dispatchEvent(new CustomEvent('"'"'app:online'"'"'))
    }
    const handleOffline = () => setIsOnline(false)
    window.addEventListener('"'"'online'"'"', handleOnline)
    window.addEventListener('"'"'offline'"'"', handleOffline)
    return () => {
      window.removeEventListener('"'"'online'"'"', handleOnline)
      window.removeEventListener('"'"'offline'"'"', handleOffline)
    }
  }, [])

  return { isOnline }
}
```

### 13.2 Mutation Queue with Replay

```typescript
// lib/offline/sync.ts
import { enqueueMutation, dequeueMutations } from '"'"'./db'"'"'
import { supabase } from '"'"'@/lib/supabase/client'"'"'
import { showInfo, showSuccess } from '"'"'@/lib/toast'"'"'

export async function offlineMutation(
  table: string,
  action: '"'"'INSERT'"'"' | '"'"'UPDATE'"'"' | '"'"'DELETE'"'"',
  data: any
) {
  await enqueueMutation({ table, action, data })
  showInfo('"'"'Change saved offline. Will sync when online.'"'"')
}

export async function replayQueue() {
  const mutations = await dequeueMutations()
  if (mutations.length === 0) return

  for (const mutation of mutations) {
    try {
      switch (mutation.action) {
        case '"'"'INSERT'"'"':
          await supabase.from(mutation.table).insert(mutation.data)
          break
        case '"'"'UPDATE'"'"':
          await supabase.from(mutation.table).update(mutation.data).eq('"'"'id'"'"', mutation.data.id)
          break
        case '"'"'DELETE'"'"':
          await supabase.from(mutation.table).delete().eq('"'"'id'"'"', mutation.data.id)
          break
      }
    } catch (error) {
      await enqueueMutation({ ...mutation, retryCount: mutation.retryCount + 1 })
    }
  }

  const synced = mutations.filter((m) => m.retryCount < 3).length
  if (synced > 0) showSuccess(synced + '"'"' changes synced'"'"')
}
```

### 13.3 Offline State Matrix

| View | Offline Behavior | Data Source | Mutation Support |
|---|---|---|---|
| Task list | Read cached data | IndexedDB | Queue + replay |
| Course list | Read cached data | IndexedDB | Queue + replay |
| Chat history | Read cached messages | IndexedDB | Queue + replay |
| Dashboard stats | Show last-cached values | IndexedDB | Read-only |
| AI Chat | Graceful message: "AI unavailable offline" | N/A | N/A |
| Settings | Full access | localStorage | Direct |

### 13.4 Current State Audit + Migration Plan

**Current realities:**
- useNetworkStatus hook exists (24 lines)
- OfflineBanner component exists (shows warning banner)
- No IndexedDB integration
- No mutation queue
- No offline data persistence

**Migration plan:**
- **Phase 2:** Add idb package, create IndexedDB schema
- **Phase 2:** Create cache-on-read pattern (TanStack Query -> IndexedDB)
- **Phase 2:** Create mutation queue with retry
- **Phase 2:** Wire up app:online event to trigger replay
- **Phase 3:** Add conflict resolution (last-write-wins with timestamp comparison)

---

## 14. PWA Architecture

### 14.1 PWA Manifest

```json
// public/manifest.json (current -- works well)
{
  "name": "ARIA OS -- Your Second Brain",
  "short_name": "ARIA OS",
  "description": "Personal AI productivity system for BTech CSE students",
  "start_url": "/dashboard",
  "display": "standalone",
  "background_color": "#0A0B0F",
  "theme_color": "#6366F1",
  "orientation": "portrait-primary",
  "icons": [
    { "src": "/icons/icon-192x192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable" },
    { "src": "/icons/icon-512x512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable" },
    { "src": "/icons/icon-512x512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ],
  "categories": ["productivity", "education", "ai"],
  "lang": "en-US",
  "scope": "/"
}
```

### 14.2 Service Worker Strategy

**Current (next-pwa v5 with Workbox):**

```javascript
// next.config.js (current)
const withPWA = require('"'"'next-pwa'"'"')({
  dest: '"'"'public'"'"',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === '"'"'development'"'"',
})

const nextConfig = { reactStrictMode: true, /* ... */ }
module.exports = withPWA(nextConfig)
```

**Target (@serwist/next -- Phase 2):**

```typescript
// next.config.ts
import type { NextConfig } from '"'"'next'"'"'
import withSerwistInit from '"'"'@serwist/next'"'"'

const withSerwist = withSerwistInit({
  swSrc: '"'"'app/sw.ts'"'"',
  swDest: '"'"'public/sw.js'"'"',
  reloadOnOnline: true,
})

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      { protocol: '"'"'https'"'"', hostname: '"'"'*.supabase.co'"'"' },
      { protocol: '"'"'https'"'"', hostname: '"'"'img.youtube.com'"'"' },
    ],
  },
}
export default withSerwist(nextConfig)
```

### 14.3 Caching Strategy

| Resource | Strategy | Cache Name | Max Age |
|---|---|---|---|
| App shell (HTML) | NetworkFirst | pages | -- |
| JS/CSS bundles | CacheFirst | static-assets | 30 days |
| Font files | CacheFirst | static-assets | 30 days |
| Images | StaleWhileRevalidate | images | 7 days |
| API responses | NetworkFirst | api-cache | 1 hour |

### 14.4 Current State Audit + Migration Plan

**Current realities:**
- PWA manifest exists with correct icons, theme, background colors
- next-pwa v5 configured in next.config.js
- SW precaches static assets, uses appropriate strategies
- skipWaiting: true for immediate updates
- No custom install prompt UI
- No update notification flow

**Migration plan:**
- **Phase 1:** Keep next-pwa (stable, works with v14)
- **Phase 2:** Migrate to @serwist/next (better v15 support)
- **Phase 2:** Add custom BeforeInstallPrompt UI
- **Phase 3:** Add update notification toast
- **Phase 3:** Add background sync for mutation queue

---

## 15. Performance Architecture

### 15.1 Core Web Vitals Targets

| Metric | Poor | Needs Improvement | Good (Target) |
|---|---|---|---|
| **LCP** | >4.0s | >2.5s | <=1.5s |
| **FID** | >300ms | >100ms | <=50ms |
| **CLS** | >0.25 | >0.1 | <=0.05 |
| **INP** | >500ms | >200ms | <=100ms |
| **TTFB** | >1.8s | >0.8s | <=0.3s |

### 15.2 Bundle Budgets

| Bundle | Budget (gzip) | Enforcement |
|---|---|---|
| **Initial JS** (any route) | <=80KB | next/bundle-analyzer in CI |
| **Initial CSS** | <=20KB | PostCSS + Tailwind purge |
| **Route chunk** (per module) | <=30KB | Dynamic imports |
| **Shared vendor** (react, next) | <=50KB | SplitChunks config |
| **Lazy-loaded** (any) | <=15KB | Dynamic import lint |

### 15.3 Code Splitting Strategy

```typescript
const ThreeBackground = dynamic(() => import('"'"'@/components/ThreeBackground'"'"'), {
  ssr: false,
  loading: () => <div className="'"'"'fixed inset-0 bg-background-page'"'"'" />,
})

const AddTaskModal = dynamic(() => import('"'"'@/components/features/tasks/task-form'"'"'), {
  loading: () => <Skeleton className="'"'"'h-96 w-full rounded-xl'"'"'" />,
})

const SleepChart = dynamic(() => import('"'"'@/components/features/sleep/sleep-chart'"'"'), {
  ssr: false,
  loading: () => <Skeleton className="'"'"'h-64 w-full rounded-xl'"'"'" />,
})
```

### 15.4 Performance Checklist

| Technique | Status | Impact | Phase |
|---|---|---|---|
| Route-level code splitting | Built-in | High | Already done |
| Dynamic imports for heavy components | Implemented | Medium | Already done |
| Image optimization via Image | Implemented | High | Already done |
| Font optimization via next/font | Implemented | Medium | Already done |
| Bundle analyzer | Configure | Medium | Phase 1 |
| Virtual scrolling for long lists | Phase 2 | Medium | Phase 2 |
| Streaming SSR with Suspense | Phase 2 | Medium | Phase 2 |
| Web Vitals monitoring | Phase 2 | Low | Phase 2 |
| Bundle size CI gate | Phase 2 | High | Phase 2 |

### 15.5 Migration Plan

- **Phase 1:** Add @next/bundle-analyzer for bundle monitoring
- **Phase 1:** Add preconnect links in root layout for Supabase, AI APIs
- **Phase 2:** Implement virtual scrolling for lists with >50 items
- **Phase 2:** Add web-vitals tracking, send to PostHog + Sentry
- **Phase 2:** Implement streaming SSR for dashboard page
- **Phase 3:** Add bundle size CI check (fail build if over budget)

---

## 16. Accessibility Architecture

### 16.1 WCAG 2.2 AA Compliance Targets

| Guideline | Target | Verification |
|---|---|---|
| 1.1.1 Non-text Content | All images have alt text | axe-core + manual |
| 1.4.3 Contrast (Minimum) | 4.5:1 text, 3:1 large | Design tokens verified |
| 2.1.1 Keyboard | All interactive elements keyboard-accessible | Tab through pages |
| 2.4.7 Focus Visible | Visible focus ring (2px accent-primary) | Already done |
| 3.3.2 Labels | All inputs have associated labels | Already done |

### 16.2 Focus Management

```typescript
// hooks/use-focus-trap.ts (Phase 2)
import { useEffect, useRef } from '"'"'react'"'"'

export function useFocusTrap(open: boolean) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open || !containerRef.current) return
    const container = containerRef.current
    const selector = '"'"'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])'"'"'
    const getFocusable = () => container.querySelectorAll<HTMLElement>(selector)

    const first = getFocusable()[0]
    first?.focus()

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== '"'"'Tab'"'"') return
      const focusable = getFocusable()
      const firstEl = focusable[0]; const lastEl = focusable[focusable.length - 1]
      if (e.shiftKey && document.activeElement === firstEl) { e.preventDefault(); lastEl?.focus() }
      else if (!e.shiftKey && document.activeElement === lastEl) { e.preventDefault(); firstEl?.focus() }
    }
    container.addEventListener('"'"'keydown'"'"', handleKeyDown)
    return () => container.removeEventListener('"'"'keydown'"'"', handleKeyDown)
  }, [open])

  return containerRef
}
```

### 16.3 Screen Reader Annotations

```typescript
// Icon-only buttons must have aria-label
<Button variant="'"'"'ghost'"'"'" size="'"'"'icon'"'"'"
  onClick={handleDelete}
  aria-label={'"'"'Delete task "'"'"' + task.title + '"'"'"'"'"'}>
  <Trash2 className="'"'"'w-4 h-4'"'"'" aria-hidden="'"'"'true'"'"'" />
</Button>

// Loading states
<div role="'"'"'status'"'"'" aria-live="'"'"'polite'"'"'" aria-busy={loading}>
  {loading ? <Skeleton /> : <Content />}
  {loading && <span className="'"'"'sr-only'"'"'">Loading tasks...</span>}
</div>

// Dynamic content (chat, notifications)
<div aria-live="'"'"'polite'"'"'" aria-atomic="'"'"'true'"'"'">{message}</div>
```

### 16.4 Color Contrast

| Combination | Foreground | Background | Ratio | Passes AA? |
|---|---|---|---|---|
| Body text on page | #F0F2F5 | #0A0B0F | 15.4:1 | Yes |
| Secondary text on page | #8B92A5 | #0A0B0F | 7.2:1 | Yes |
| Primary accent on card | #6366F1 | #12141C | 5.8:1 | Yes |
| Error text on card | #EF4444 | #12141C | 4.8:1 | Yes |
| Disabled text | #475569 | #0A0B0F | 3.8:1 | Needs improvement |

### 16.5 Current State Audit + Migration Plan

**Current realities:**
- Focus-visible ring implemented in globals.css
- sr-only utility class defined
- prefers-reduced-motion respected
- Form inputs have labels with htmlFor
- No screen reader testing
- No keyboard shortcut system
- No focus trap in modals

**Migration plan:**
- **Phase 1:** Audit all images for alt text
- **Phase 1:** Add focus trap to Modal component
- **Phase 2:** Add axe-core to CI pipeline
- **Phase 2:** Add aria-live regions for loading states
- **Phase 2:** Create keyboard shortcut hook, register shortcuts
- **Phase 3:** Screen reader testing with NVDA/VoiceOver

---

## 17. Security Architecture

### 17.1 Content Security Policy

```typescript
const cspDirectives = [
  "default-src '"'"'self'"'"'",
  "script-src '"'"'self'"'"' '"'"'unsafe-eval'"'"' '"'"'unsafe-inline'"'"'",
  "style-src '"'"'self'"'"' '"'"'unsafe-inline'"'"'",
  "img-src '"'"'self'"'"' data: blob: https://*.supabase.co https://img.youtube.com",
  "font-src '"'"'self'"'"' data:",
  "connect-src '"'"'self'"'"' https://*.supabase.co wss://*.supabase.co http://localhost:8000 https://api.anthropic.com",
  "frame-src '"'"'self'"'"' https://*.supabase.co",
  "worker-src '"'"'self'"'"'",
  "base-uri '"'"'self'"'"'",
  "form-action '"'"'self'"'"'",
]
```

### 17.2 Auth Middleware

```typescript
// middleware.ts (current -- correct pattern, keep as-is)
import { createServerClient } from '"'"'@supabase/ssr'"'"'
import { NextResponse } from '"'"'next/server'"'"'
import type { NextRequest } from '"'"'next/server'"'"'

const protectedRoutes = [
  '"'"'/dashboard'"'"', '"'"'/tasks'"'"', '"'"'/courses'"'"', '"'"'/habits'"'"', '"'"'/goals'"'"',
  '"'"'/ideas'"'"', '"'"'/income'"'"', '"'"'/projects'"'"', '"'"'/resources'"'"', '"'"'/opportunities'"'"',
  '"'"'/sleep'"'"', '"'"'/time'"'"', '"'"'/chat'"'"', '"'"'/automation'"'"', '"'"'/youtube'"'"', '"'"'/academics'"'"',
]

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const isProtected = protectedRoutes.some(route =>
    pathname === route || pathname.startsWith(route + '"'"'/"'"'")
  )
  if (!isProtected) return NextResponse.next()

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => request.cookies.getAll(),
        setAll: (cookiesToSet) => {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value))
          const response = NextResponse.next({ request })
          cookiesToSet.forEach(({ name, value, options }) => response.cookies.set(name, value, options))
        },
      },
    }
  )

  const { data: { user } } = await supabase.auth.getUser()
  if (!user) {
    const url = request.nextUrl.clone()
    url.pathname = '"'"'/login'"'"'
    url.searchParams.set('"'"'redirect'"'"', pathname)
    return NextResponse.redirect(url)
  }
  return NextResponse.next()
}

export const config = {
  matcher: ['"'"'/((?!_next/static|_next/image|favicon.ico|manifest.json|sw.js|workbox-.*|icon.*).*)'"'"'],
}
```

### 17.3 Auth Token Management

| Token | Storage | Expiry | Refresh | Purpose |
|---|---|---|---|---|
| **Access Token** | HttpOnly cookie (Supabase SSR) | 1 hour | Auto via Supabase SSR | API auth |
| **Refresh Token** | HttpOnly cookie (Supabase SSR) | 30 days | Rotated on use | Session persistence |
| **Anon Key** | Public env var | Static | Never | Supabase client init |

### 17.4 XSS Prevention

```
- React JSX auto-escapes user input by default
- next/image handles URL sanitization
- Use DOMPurify only if dangerouslySetInnerHTML is absolutely required
- Never log tokens, passwords, or API keys
- Never use eval() on user input
```

### 17.5 Route Protection Matrix

| Route Group | Guard Level | Behavior if Unauthenticated |
|---|---|---|
| (public)/ | Public | No check |
| (auth)/ | GuestOnly | Redirect to /dashboard if logged in |
| (dashboard)/ | AuthRequired | Redirect to /login?redirect=path |
| /api/* | Varies by handler | 401 Unauthorized or public |

### 17.6 Current State Audit + Migration Plan

**Current realities:**
- middleware.ts implements Supabase SSR auth with cookie management
- Protected routes list covers all 16 modules
- Guest redirect preserves original path (redirect param)
- Security headers in CSP format (needs full implementation)
- No build-time env validation
- No CSRF token for custom API calls (Supabase handles this)

**Migration plan:**
- **Phase 1:** Add security headers to next.config.js
- **Phase 1:** Add Zod env validation at build time
- **Phase 2:** Add CSP reporting endpoint (report-uri / CSP violations)
- **Phase 2:** Formalize route protection matrix
- **Phase 2:** Add rate limiting for API routes

---

## 18. Error Handling Architecture

### 18.1 Error Boundary Hierarchy

```
RootLayout
+-- GlobalError (app/global-error.tsx)
    +-- RootLayout (fallback rendering)
        +-- DashboardLayout
            +-- ModuleError (app/tasks/error.tsx)
                +-- TasksPage
                    +-- ComponentError (ErrorBoundary wrapper)
```

### 18.2 3-Tier Error Boundary System

**Tier 1: Global Error Boundary (app/global-error.tsx)**

```
Catches: Unhandled errors in Server Components, layout errors
Renders: Full-page error with error ID, try again, go home
Has access: <html> + <body> tags (separate root)
```

**Tier 2: Module Error Boundary (app/tasks/error.tsx)**

```
Catches: Errors within a module's route segment
Renders: Module-specific error state with retry
Has access: Dashboard layout (sidebar + navbar visible)
```

**Tier 3: Component Error Boundary (ErrorBoundary wrapper)**

```typescript
// components/shared/error-fallback.tsx
'"'"'use client'"'"'

import { Component, ReactNode } from '"'"'react'"'"'

interface Props { children: ReactNode; fallback?: ReactNode }
interface State { hasError: boolean; error?: Error }

export class ErrorBoundary extends Component<Props, State> {
  state = { hasError: false }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('"'"'[ErrorBoundary]'"'"', error, info.componentStack)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <DefaultErrorFallback />
    }
    return this.props.children
  }
}
```

### 18.3 Error Classification & Recovery

| Error Class | Example | HTTP Status | Recovery | User Message |
|---|---|---|---|---|
| **Network** | fetch failed, offline | 0 | Retry, offline mode | "Connection lost. Retrying..." |
| **Auth** | token expired, unauthorized | 401 | Redirect to login | "Session expired. Please log in again." |
| **Validation** | bad request data | 400 | Fix input | "Please check your input." |
| **Not Found** | missing record | 404 | Redirect to list | "This item was not found." |
| **Rate Limit** | too many requests | 429 | Wait + retry | "Too many requests. Please wait." |
| **Server** | internal error, DB down | 500 | Retry, degrade | "Something went wrong. Try again." |
| **Unknown** | unexpected crash | -- | Reset, reload | "An unexpected error occurred." |

### 18.4 Error Reporting Pipeline

```typescript
// lib/observability/sentry.ts (Phase 2)
import * as Sentry from '"'"'@sentry/nextjs'"'"'

export function initSentry() {
  Sentry.init({
    dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
    environment: process.env.NODE_ENV,
    tracesSampleRate: 0.1,  // 10% of transactions for sampling
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration(),
    ],
  })
}

export function captureError(error: Error, context?: Record<string, any>) {
  Sentry.withScope((scope) => {
    if (context) scope.setExtras(context)
    Sentry.captureException(error)
  })
}

export function captureMessage(message: string, level: '"'"'info'"'"' | '"'"'warning'"'"' | '"'"'error'"'"') {
  Sentry.captureMessage(message, level)
}
```

### 18.5 Current State Audit + Migration Plan

**Current realities:**
- Global error boundary exists (app/global-error.tsx) with full-page fallback
- Module-level error boundaries exist (app/tasks/error.tsx pattern)
- Component-level ErrorBoundary class component exists (not used)
- No Sentry integration for error reporting
- No error classification in user-facing messages
- No error recovery strategies (retry/reset patterns exist but are manual)

**Migration plan:**
- **Phase 1:** Add @sentry/nextjs package, initialize in root layout
- **Phase 1:** Add captureError to existing error boundaries
- **Phase 2:** Formalize error classification into utility
- **Phase 2:** Add retry logic for network errors (TanStack Query handles this)
- **Phase 2:** Create consistent error message templates per error class

---

## 19. Observability Architecture

### 19.1 Observability Stack

| Concern | Tool | Data Collected | Cost |
|---|---|---|---|
| **Error Tracking** | Sentry | Exceptions, stack traces, breadcrumbs, releases | Free tier (5k events/mo) |
| **Performance Monitoring** | Sentry Performance | LCP, FID, CLS, INP, API latency, trace view | Included with Sentry |
| **Product Analytics** | PostHog | Page views, feature usage, funnels, retention | Free tier (1M events/mo) |
| **Feature Flags** | PostHog | Feature gating, gradual rollouts | Included with PostHog |
| **Session Replay** | PostHog + Sentry | User sessions, error replay | Free tier |
| **Web Vitals** | web-vitals library | Core Web Vitals + custom metrics | Free (open source) |
| **Custom Metrics** | TanStack Query devtools | Query cache, refetch timing | Free (dev only) |

### 19.2 Sentry Integration (Phase 2)

```typescript
// app/layout.tsx -- Sentry initialization
'"'"'use client'"'"'

import * as Sentry from '"'"'@sentry/nextjs'"'"'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
})

export default function SentryProvider({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
```

### 19.3 PostHog Integration (Phase 2)

```typescript
// lib/observability/posthog.ts
import { PostHog } from '"'"'posthog-js'"'"'

let posthog: PostHog | null = null

export function initPosthog() {
  if (typeof window === '"'"'undefined'"'"') return

  posthog = new PostHog(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
    api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST || '"'"'https://app.posthog.com'"'"',
    capture_pageview: false,  // We use custom pageview tracking
    loaded: (ph) => {
      if (process.env.NODE_ENV !== '"'"'production'"'"') ph.opt_out_capturing()
    },
  })
}

export function trackPageView(url: string, properties?: Record<string, any>) {
  posthog?.capture('"'"'$pageview'"'"', { url, ...properties })
}

export function trackEvent(event: string, properties?: Record<string, any>) {
  posthog?.capture(event, properties)
}

export function identifyUser(userId: string, traits?: Record<string, any>) {
  posthog?.identify(userId, traits)
}
```

### 19.4 Web Vitals Tracking

```typescript
// lib/performance/web-vitals.ts
'"'"'use client'"'"'

import { onCLS, onFCP, onFID, onINP, onLCP, onTTFB } from '"'"'web-vitals'"'"'

export function reportWebVitals() {
  const sendToAnalytics = (metric: any) => {
    // Send to Sentry Performance
    fetch('"'"'/api/analytics/vitals'"'"', {
      method: '"'"'POST'"'"',
      body: JSON.stringify({
        name: metric.name,
        value: metric.value,
        rating: metric.rating,
        delta: metric.delta,
        id: metric.id,
      }),
    })
  }

  onCLS(sendToAnalytics)
  onFCP(sendToAnalytics)
  onFID(sendToAnalytics)
  onINP(sendToAnalytics)
  onLCP(sendToAnalytics)
  onTTFB(sendToAnalytics)
}
```

### 19.5 Current State Audit + Migration Plan

**Current realities:**
- No observability tooling configured
- No Sentry, PostHog, or web-vitals
- Error logging is limited to console.error in catch blocks
- No user session tracking
- No performance monitoring
- No feature flags

**Migration plan:**
- **Phase 2:** Add Sentry (@sentry/nextjs) for error + performance tracking
- **Phase 2:** Add PostHog (posthog-js) for product analytics
- **Phase 2:** Add web-vitals library for Core Web Vitals monitoring
- **Phase 2:** Create analytics API endpoint (/api/analytics/vitals)
- **Phase 3:** Add session replay for error debugging
- **Phase 3:** Add feature flags for gradual rollouts
- **Phase 3:** Create observability dashboard

---

## 20. Testing Architecture

### 20.1 Testing Layers

| Layer | Tool | Scope | Coverage Target | Phase |
|---|---|---|---|---|
| **Unit** | Vitest | Stores, hooks, utilities, pure functions | >=90% | Phase 1 |
| **Component** | Vitest + Testing Library | Individual components (render, interaction) | >=80% | Phase 1 |
| **Integration** | Vitest + Testing Library | Feature workflows (create task, complete flow) | >=80% | Phase 2 |
| **E2E** | Playwright | Critical paths (login -> tasks, PWA install) | 100% critical | Phase 1 |
| **Accessibility** | axe-core (via Playwright) | WCAG 2.2 AA compliance | All pages | Phase 2 |
| **Visual** | Percy / Chromatic | Visual regression of key pages | All pages | Phase 3 |

### 20.2 Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from '"'"'vitest/config'"'"'
import path from '"'"'path'"'"'

export default defineConfig({
  test: {
    environment: '"'"'jsdom'"'"',
    globals: true,
    setupFiles: ['"'"'./__tests__/setup.ts'"'"'],
    include: ['"'"'__tests__/unit/**/*.test.ts'"'"', '"'"'__tests__/unit/**/*.test.tsx'"'"'],
    coverage: {
      provider: '"'"'v8'"'"',
      reporter: ['"'"'text'"'"', '"'"'html'"'"', '"'"'lcov'"'"'],
      thresholds: {
        statements: 80,
        branches: 75,
        functions: 80,
        lines: 80,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '"'"'./'"'"'),
    },
  },
})
```

### 20.3 Unit Test Example

```typescript
// __tests__/unit/stores/ui-store.test.ts
import { useUIStore } from '"'"'@/lib/stores/ui-store'"'"'

describe('"'"'UIStore'"'"'', () => {
  beforeEach(() => {
    useUIStore.setState({ sidebarOpen: true, sidebarCollapsed: false, theme: '"'"'dark'"'"' })
  })

  it('"'"'toggles sidebar'"'"'', () => {
    useUIStore.getState().toggleSidebar()
    expect(useUIStore.getState().sidebarOpen).toBe(false)
  })

  it('"'"'sets theme'"'"'', () => {
    useUIStore.getState().setTheme('"'"'light'"'"')
    expect(useUIStore.getState().theme).toBe('"'"'light'"'"')
  })
})
```

### 20.4 Component Test Example

```typescript
// __tests__/unit/components/button.test.tsx
import { render, screen, fireEvent } from '"'"'@testing-library/react'"'"'
import { Button } from '"'"'@/components/ui/button'"'"'

describe('"'"'Button'"'"'', () => {
  it('"'"'renders with text and handles click'"'"'', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click Me</Button>)
    expect(screen.getByText('"'"'Click Me'"'"')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('"'"'button'"'"'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('"'"'shows loading state'"'"'', () => {
    render(<Button isLoading>Loading</Button>)
    expect(screen.getByRole('"'"'button'"'"')).toBeDisabled()
  })
})
```

### 20.5 E2E Test Example (Playwright)

```typescript
// e2e/specs/tasks.flow.spec.ts
import { test, expect } from '"'"'@playwright/test'"'"'

test.describe('"'"'Tasks Flow'"'"', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('"'"'/login'"'"')
    // Authenticate via Supabase
    await page.fill('"'"'[name="email"]'"'"', process.env.TEST_EMAIL!)
    await page.fill('"'"'[name="password"]'"'"', process.env.TEST_PASSWORD!)
    await page.click('"'"'button[type="submit"]'"'"')
    await page.waitForURL('"'"'/**/dashboard'"'"')
  })

  test('"'"'creates and completes a task'"'"', async ({ page }) => {
    await page.goto('"'"'/tasks'"'"')
    await page.click('"'"'text=Add Task'"'"')
    await page.fill('"'"'#task-title'"'"', '"'"'Test task from Playwright'"'"')
    await page.selectOption('"'"'#task-priority'"'"', '"'"'high'"'"')
    await page.click('"'"'text=Create'"'"')
    await expect(page.getByText('"'"'Test task from Playwright'"'"')).toBeVisible()
  })
})
```

### 20.6 Test Commands

```bash
# Unit + Component tests
npx vitest                        # Run all unit/component tests
npx vitest --watch               # Watch mode
npx vitest --coverage            # With coverage report

# E2E tests
npx playwright test              # Headless
npx playwright test --ui         # Interactive UI mode

# Accessibility
npx playwright test --grep @a11y # Accessibility-specific tests

# CI
npx vitest run --reporter=junit  # JUnit output for CI
```

### 20.7 Current State Audit + Migration Plan

**Current realities:**
- No unit or component tests
- @playwright/test is in devDependencies (v1.60) but no test files exist
- No Vitest setup
- No test configuration files (vitest.config.ts, playwright.config.ts)
- No CI test job

**Migration plan:**
- **Phase 1:** Add Vitest + Testing Library, create config
- **Phase 1:** Write unit tests for Zustand stores (userStore, taskStore)
- **Phase 1:** Write unit tests for utility functions (cn, format, validators)
- **Phase 1:** Write Playwright config + first E2E test (login flow)
- **Phase 2:** Write component tests for shadcn/ui wrappers
- **Phase 2:** Write integration tests for feature workflows
- **Phase 2:** Add CI test job to .github/workflows/ci.yml
- **Phase 3:** Add visual regression and a11y tests

---

## 21. Scalability Architecture

### 21.1 Module Isolation

Each of the 16 modules is independently:
- **Lazy-loadable** -- route-level code splitting means each module is its own JS chunk
- **State-isolated** -- each module uses its own TanStack Query hooks and Zustand stores (no cross-contamination)
- **Testable** -- each module's features/ directory mirrors its data layer
- **Ownable** -- teams can own specific modules without merge conflicts

### 21.2 Performance Budgets (per Module)

| Metric | Per-Module Budget | Enforcement |
|---|---|---|
| Initial JS chunk | <=30KB gzip | next/bundle-analyzer CI gate |
| API calls on mount | <=3 (parallel) | Manual review |
| Number of re-renders | <=5 on mount | React DevTools profiler |
| Subscription count | <=2 Realtime channels | Manual review |
| DOM nodes | <=2000 | Lighthouse |

### 21.3 Data Scalability

| Pattern | When to Use | Implementation |
|---|---|---|
| **Pagination** | >50 items per list | TanStack Query useInfiniteQuery with cursor-based pagination |
| **Virtual Scrolling** | >100 items per list | @tanstack/react-virtual with fixed/estimated row heights |
| **Debounced Search** | Real-time filter inputs | useDebounce hook (300ms delay) |
| **Infinite Scroll** | Feed-based views (chat, activity) | IntersectionObserver trigger |
| **Lazy Loading** | Below-fold content | IntersectionObserver + dynamic import |

### 21.4 Team Scalability

```
Module Ownership Model:

apps/web/
  components/features/tasks/   -> Team Tasks
  components/features/courses/ -> Team Academics
  components/features/chat/    -> Team AI
  lib/query/use-tasks.ts       -> Team Tasks + shared infra
  lib/stores/ui-store.ts       -> Shared infra team
```

### 21.5 Current State Audit + Migration Plan

**Current realities:**
- 16 modules already isolated in (dashboard)/(modules)/ route group -- good foundation
- No pagination or virtual scrolling (all data loaded at once)
- No module-specific performance budgets
- No module ownership documented
- All 16 pages are 'use client' -- no progressive enhancement
- All 16 pages fetch data in useEffect -- no separation of concerns

**Migration plan:**
- **Phase 1:** Add loading.tsx + error.tsx to all modules (already planned in layout)
- **Phase 2:** Implement pagination for list-heavy modules (tasks, courses, resources)
- **Phase 2:** Implement virtual scrolling for modules with large datasets
- **Phase 2:** Add module-specific error boundaries for isolation
- **Phase 3:** Document module ownership in CONTRIBUTING.md
- **Phase 3:** Add bundle size CI gates per module

---

## 22. Future Expansion Architecture

### 22.1 Staged Rollout Plan

```
Phase 1 (Immediate -- Next.js 14 baseline):
  - Keep existing architecture, add loading/error boundaries
  - Add Vitest + Playwright configuration
  - Add bundle analyzer
  - Add responsive sidebar
  - Upgrade Zustand v4 -> v5
  - Pre-commit CI checks

Phase 2 (Short-term -- Data layer + UX):
  - Upgrade Next.js 14 -> 15 + React 18 -> 19
  - Migrate Tailwind v3 -> v4 (CSS-first config)
  - Add TanStack Query for all server data
  - Add shadcn/ui primitives
  - Build Cmd+K command palette
  - Add notification center
  - Add Sentry + PostHog observability
  - Implement IndexedDB offline cache
  - Add detail routes ([id]) for all modules
  - Add parallel routes (@modal)

Phase 3 (Mid-term -- PWA + AI):
  - Migrate PWA from next-pwa to @serwist/next
  - Add push notifications
  - Add background sync for offline mutations
  - Implement streaming SSR for dashboard
  - Add GSAP for complex animations
  - Add session replay (Sentry/PostHog)
  - Add visual regression testing
  - Full E2E test suite (playwright)

Phase 4 (Long-term -- Enterprise):
  - i18n support (next-intl, RTL)
  - Theme marketplace (community themes)
  - Plugin system (custom module API)
  - Edge Functions integration
  - AI agent-to-agent communication in UI
  - Offline-first conflict resolution (CRDT)
  - Desktop via Tauri
  - React Native mobile app (shared types)
```

### 22.2 Technology Radar

| Technology | Phase | Confidence | Risk |
|---|---|---|---|
| **Next.js 15** | Phase 2 | High | Breaking changes from v14 (headers, params) |
| **React 19** | Phase 2 | High | New hooks (use, useOptimistic), concurrent features |
| **Tailwind v4** | Phase 2 | Medium | CSS-first config breaks all existing configs |
| **shadcn/ui** | Phase 2 | High | Easy migration via npx shadcn init |
| **TanStack Query** | Phase 2 | High | Well-documented migration path from inline fetching |
| **Sentry** | Phase 2 | High | Straightforward @sentry/nextjs integration |
| **PostHog** | Phase 2 | Medium | Self-host vs cloud decision |
| **@serwist/next** | Phase 3 | Medium | Newer library, less community than next-pwa |
| **GSAP** | Phase 3 | Medium | Mixing animation libraries adds complexity |
| **Tauri** | Phase 4 | Low | New platform, separate build pipeline |

### 22.3 Plugin System Vision (Phase 4)

```
Module Registration API:

plugins/
  registerModule({
    id: 'my-custom-module',
    name: 'My Custom Tracker',
    icon: 'Activity',
    route: '/custom',
    component: () => import('./custom-page'),
    dataLayer: () => import('./custom-queries'),
  })
```

### 22.4 Migration Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Next.js 15 breaking changes** | Medium | High | Staged upgrade, feature flag behind switch, run both versions |
| **Tailwind v4 CSS-first config** | High | Medium | Wrap configs, use migration script, validate with Percy |
| **React 19 concurrent features** | Low | Medium | All existing code is compatible; new features opt-in |
| **Service worker rewrite** | Medium | Medium | Parallel SW in @serwist during migration window |
| **Observability infrastructure** | Low | Low | Sentry/PostHog have free tiers, add gradually |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-11 | Developer | Initial frontend architecture documentation |
| 2.0.0 | 2026-06-13 | Developer | Enterprise upgrade: 22 sections, target-state architecture (Next.js 15 / React 19 / Tailwind v4 / shadcn), migration paths per section, 12 ADR principles, component 5-layer hierarchy, state 6-layer decision matrix, offline-first IndexedDB, AI streaming state machine, Cmd+K command center, observability stack (Sentry + PostHog), testing stack (Vitest + Playwright), module scalability, phased rollout plan |