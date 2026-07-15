# Frontend Development Learning Path

## Document Control

| Field | Value |
|---|---|
| Document ID | LRN-FE-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-07-12 |
| Classification | Internal |

---

## Module 1: Project Overview & Setup

**Estimated time:** 0.5 day

### Learning Objectives
- Understand the monorepo structure and where the frontend lives
- Set up local development environment (Node 18, npm, env vars)
- Start the dev server and verify it works
- Understand the page routing (18 routes under `apps/web/app/`)

### Reading Materials
- `AGENTS.md` Sections 3-6 (Build Commands, Code Style, Project Structure)
- `apps/web/package.json` — dependency overview (~40 packages)
- `apps/web/app/` — browse the page directory structure
- `apps/web/middleware.ts` — understand auth middleware

### Practice Exercise
1. Clone the repo and run `make install`
2. Run `make dev-web` and verify the app loads at `http://localhost:3000`
3. Navigate through 3 pages (Dashboard, Tasks, Courses)
4. Run `npm run lint` and `npm run type-check` — verify both pass
5. Open the Network tab in DevTools and inspect an API call to Supabase

---

## Module 2: Component Architecture

**Estimated time:** 0.5 day

### Learning Objectives
- Understand the component hierarchy (Button, Card, Modal, etc.)
- Know how to use cyberpunk design tokens in `tailwind.config.js`
- Understand the Storybook setup (380 stories across 72 files)
- Recognize common UI patterns (cards, bento-box, staggered grids)

### Reading Materials
- `AGENTS.md` Section 5 (UI/UX & Design System)
- `apps/web/components/ui/` — browse all base components
- `apps/web/tailwind.config.js` — design tokens (218 lines)
- `apps/web/styles/globals.css` — global styles and CSS variables
- Storybook: run `npm run storybook` and explore component stories

### Design Tokens Reference
```css
--accent-primary: #6366F1;
--accent-secondary: #818CF8;
--accent-neon: #00FFA3;
--text-primary: #F1F5F9;
--bg-card: #13151A;
```

### Practice Exercise
1. Read 3 component files (`Button`, `Card`, `Modal`) to understand the pattern
2. Run Storybook and find a component with multiple variants
3. Create a minor style change using a design token
4. Verify the change renders correctly in Storybook

---

## Module 3: State & Data

**Estimated time:** 1 day

### Learning Objectives
- Understand state management (Zustand for tasks + user, local state elsewhere)
- Know how to use React Query (if applicable) for server state
- Be able to read and write data via the Supabase client
- Understand the `useAuth`, `useNetworkStatus`, `useRealtime` hooks

### Reading Materials
- `AGENTS.md` Section 7 (Database Schema) — understand the data model
- `apps/web/hooks/` — read `useAuth.ts`, `useNetworkStatus.ts`
- `apps/web/lib/supabase.ts` — Supabase client setup
- `apps/web/lib/stores/` — Zustand store patterns
- `AGENTS.md` Section 8 (API Endpoint Reference) — understand the API surface

### Practice Exercise
1. Read the tasks Zustand store and trace how data flows from Supabase → store → component
2. Open the Network tab and inspect a task CRUD operation
3. Write a simple component that fetches and displays data using `useEffect` + `supabase.from()`
4. Add error handling with `toast.error()` for the fetch

---

## Module 4: Feature Implementation

**Estimated time:** 1 day

### Learning Objectives
- Walk through building a new feature page end-to-end
- Understand the pattern: Page → Component → Hook → API → Supabase
- Know how to add a new route in `apps/web/app/`
- Be able to integrate Framer Motion page transitions

### Reading Materials
- `apps/web/app/tasks/` — study a full feature page (the best example)
- `apps/web/app/goals/` — another complete feature page
- `AGENTS.md` Section 12.2 (Adding a New Frontend Page)
- `apps/web/components/ui/` — available components to reuse

### Walkthrough: Building a Feature Page

A standard feature page follows this pattern:

```
apps/web/app/<feature>/
  page.tsx          — Main page (server component)
  client-page.tsx   — Interactive wrapper (client component)
  components/       — Feature-specific components
  hooks/            — Feature-specific hooks (optional)
```

**Steps:**
1. Create the page route file
2. Build the client component with data fetching
3. Create feature-specific sub-components
4. Add Framer Motion page transitions
5. Wire up CRUD operations via the API

### Practice Exercise
1. Pick an existing feature page (e.g., Goals) and trace its full data flow
2. Add a new column/field to the page following existing patterns
3. Add a form for creating a new item
4. Verify the feature works with `npm run dev`

---

## Module 5: Testing & QA

**Estimated time:** 1 day

### Learning Objectives
- Understand the frontend testing setup (Vitest + Playwright)
- Know how to write and run unit tests with Vitest
- Understand Playwright E2E testing (22 spec files covering 9 modules)
- Know how to run accessibility checks

### Reading Materials
- `apps/web/vitest.config.ts` — Vitest configuration
- `apps/web/playwright.config.ts` — Playwright configuration
- `apps/web/e2e/specs/` — browse E2E test specs
- `AGENTS.md` Section 16 (Testing Standards)
- `AGENTS.md` Section 17 (CI/CD Pipeline)

### Test Types
| Type | Tool | What It Tests | Command |
|---|---|---|---|
| Unit tests | Vitest | Component logic, hooks, utils | `npm run test` |
| E2E tests | Playwright | Full user flows | `npm run test:e2e` |
| Storybook tests | Storybook | Component visual states | `npm run test-storybook` |
| Accessibility | axe/lint-a11y | WCAG compliance | `npm run lint-a11y` |

### Practice Exercise
1. Run `npm run test` and verify the test suite passes
2. Read 2 existing Vitest test files to understand the pattern
3. Write a simple unit test for a utility function
4. Run Playwright against one E2E spec and observe the browser automation
5. Run `npm run lint-a11y` and review any findings
