# AGENTS.md — Second Brain OS Master Reference (Enterprise v4)

## Document Control

| Field | Value |
|---|---|
| Document ID | SB-AGENTS-REF-001 |
| Version | 4.0.0 |
| Status | Active |
| Last Updated | 2026-06-14 |
| Classification | Internal — AI Agent Instructions |
| Target Audience | AI Agents (Claude, Cursor, Copilot, Copilot Chat) + Human Developers |
| Review Cycle | Bi-weekly |
| Approver | Developer |
| SLA Tier | Tier 1 (Critical) |

---

## 1. Executive Summary

**Second Brain OS (ARIA OS)** is a personal AI productivity system for BTech CSE students with **17 modules** (15 functional + 2 in design). It follows a monorepo structure with a Next.js 14 frontend, FastAPI backend, Supabase PostgreSQL database, and AI agents powered by Ollama (local) and Claude API (cloud).

**This file is the master reference for AI agents working on this project.** Every section below contains essential context that agents must follow when generating code, fixing bugs, or suggesting changes.

**Key architectural decisions:**
- **Prompt System**: All AI prompts live in `prompts/` with YAML frontmatter, loaded via `PromptLoader` in `packages/ai/prompt_loader.py`
- **In-process agents**: Agents run as async functions within FastAPI, not microservices (per ADR-004)
- **Graceful degradation**: Every feature works without AI via algorithmic fallback
- **Cyberpunk design**: Dark theme (#0A0B0F), neon accents (#6366F1, #00FFA3), Syne/DM Sans fonts
- **API-first with versioning**: All endpoints under `/api/v1/` with Sunset/Deprecation header support
- **Resilience by default**: Circuit breakers, exponential backoff retries, provider failover for all AI calls

---

## 2. Quick Navigation

| Section | What You'll Find |
|---|---|
| [3. Build & Test Commands](#3-build--test-commands) | All CLI commands for dev, build, lint, test, type-check, prompt validation |
| [4. Code Style Guidelines](#4-code-style-guidelines) | Frontend (TS/React) + Backend (Python) + Prompt YAML conventions |
| [5. UI/UX & Design System](#5-uiux--design-system) | Cyberpunk theme, design tokens, component library |
| [6. Project Structure](#6-project-structure) | Full directory tree with file purposes |
| [7. Database Schema](#7-database-schema) | All tables, columns, relationships, RLS policies |
| [8. API Endpoint Reference](#8-api-endpoint-reference) | 13 routers, ~53 endpoints with routes, pagination, versioning |
| [9. AI Agent Architecture](#9-ai-agent-architecture) | ARIA orchestrator, 17 agents, PromptLoader, prompt files |
| [10. Prompt System Architecture](#10-prompt-system-architecture) | PromptLoader API, frontmatter schema, directory layout, fallback logic |
| [11. Prompt Development Guide](#11-prompt-development-guide) | How to create/edit prompts, frontmatter requirements, validation, testing |
| [12. Common Patterns](#12-common-patterns) | How to add features, fix bugs, work with prompts, run tests |
| [13. Environment Setup](#13-environment-setup) | Local dev configuration, env vars, quick start |
| [14. Documentation Map](#14-documentation-map) | Where to find every doc in the project |
| [15. AI Agent Instructions](#15-ai-agent-instructions) | 25 Golden Rules for AI agents |
| [16. Testing Standards](#16-testing-standards) | Test categories, writing tests, coverage thresholds, mutation testing |
| [17. CI/CD Pipeline](#17-cicd-pipeline) | 5 CI jobs: frontend, backend, prompts, docker, security |
| [18. Cost & Performance](#18-cost--performance) | AI cost tracking, token budgets, caching strategy, SLOs |
| [19. Debugging Guide](#19-debugging-guide) | Common issues, solutions, debugging tools, distributed tracing |
| [20. Deployment Guide](#20-deployment-guide) | Production stack, deployment process, rollback, canary releases |
| [21. Onboarding & Process](#21-onboarding--process) | PR workflow, code review, changelog expectations, 30-60-90 day plan |
| [22. Incident Response](#22-incident-response) | Severity levels, SLAs, escalation matrix, postmortem template |
| [23. Security Compliance](#23-security-compliance) | Data classification, GDPR/SOC2 mappings, audit logging, vulnerability disclosure |
| [24. API Versioning Strategy](#24-api-versioning-strategy) | URL-based versioning, deprecation headers, migration guides |
| [25. Observability & Monitoring](#25-observability--monitoring) | Log levels, RED metrics, alerting rules, dashboard definitions |
| [26. Performance Benchmarks](#26-performance-benchmarks) | API latency SLOs, AI response budgets, DB query limits, bundle budgets |
| [27. Dependency Management](#27-dependency-management) | Dependabot config, update cadence, breaking change handling, license compliance |
| [28. Code Review Standards](#28-code-review-standards) | 30-item review checklist, approval rules, ownership model |

---

## 3. Build & Test Commands

### 3.1 Makefile (Recommended)

```bash
make help              # Show all available targets
make dev-api           # Start FastAPI backend (uvicorn --reload)
make dev-web           # Start Next.js frontend (npm run dev)
make dev-scheduler     # Start APScheduler cron jobs
make lint              # Run all linters (Python + TS + prompt validation)
make format            # Format all Python with Black
make test              # Run all Python tests with coverage
make test-coverage     # Run tests + HTML coverage report
make validate-prompts  # Validate all prompt YAML frontmatter
make docker-up         # Start all Docker services
make docker-build      # Build all Docker images
make pre-commit        # Full pre-commit check: lint → validate → test → type-check
make install           # Install all dependencies (pip + npm)
make clean             # Remove build artifacts and caches
```

### 3.2 Frontend (Next.js 14)

```bash
cd apps/web

npm run dev              # Start dev server → http://localhost:3000
npm run build            # Production build (outputs .next/)
npm run start            # Start production server
npm run lint             # Run ESLint across all files
npm run type-check       # TypeScript type checking (tsc --noEmit)

# Bundle analysis (if installed)
npx next/bundle-analyzer
```

### 3.3 Backend (FastAPI)

```bash
cd apps/api

uvicorn main:app --reload              # Dev server → http://localhost:8000
uvicorn main:app --host 0.0.0.0 --port 8000  # Production server

# API docs
open http://localhost:8000/docs        # Swagger UI
open http://localhost:8000/redoc       # ReDoc UI
```

### 3.4 Scheduler (APScheduler)

```bash
cd services/scheduler

pip install -r requirements.txt
python main.py           # Start scheduler (runs all 7 cron jobs)
```

### 3.5 General

```bash
# Root-level testing
pytest                                 # Run all 50+ tests with coverage
pytest -xvs                             # Verbose, stop on first failure
pytest --cov=packages --cov-report=html  # HTML coverage report

# Formatting
black apps/ packages/ services/ tests/ scripts/   # Format all Python
ruff check --fix .                      # Lint and auto-fix all Python

# Git
git status                              # Check working tree
git diff                                # View unstaged changes
git log --oneline -10                   # Recent commits
```

### 3.6 Prompt System Commands

```bash
# Validate all prompt YAML frontmatter
python scripts/validate_prompts.py

# Run prompt-specific tests
pytest tests/test_prompt_loader.py tests/test_agent_prompts.py -v

# Test a single prompt's frontmatter
python -c "from ai.prompt_loader import prompts; print(prompts.get_agent('briefing_agent').frontmatter)"

# List all available prompts
python -c "from ai.prompt_loader import prompts; print(prompts.list_prompts())"
```

### 3.7 Pre-Commit Checklist

```bash
# Run these BEFORE every commit:
make pre-commit
```

Or manually:
```bash
# 1. Python lint + format
ruff check apps/api/ packages/ services/scheduler/ scripts/ tests/
black --check apps/ packages/ services/ tests/ scripts/

# 2. TypeScript lint + type-check
cd apps/web && npm run lint && npm run type-check

# 3. Validate prompt frontmatter
python scripts/validate_prompts.py

# 4. Run all tests with coverage
python -m pytest tests/ --cov=packages --cov=apps/api --cov-fail-under=70
```

---

## 4. Code Style Guidelines

### 4.1 Frontend (TypeScript/React)

#### Imports — Order strictly enforced
```typescript
// 1. React / Next.js
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

// 2. External libraries
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, Trash2 } from 'lucide-react'

// 3. Internal hooks & utilities
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'

// 4. Relative imports (last)
import { TaskCard } from './task-card'
import type { Task } from '@/types'
```

#### Naming Conventions
| Construct | Convention | Example |
|---|---|---|
| Components | PascalCase | `TaskCard`, `HabitCalendar` |
| Hooks | camelCase + `use` prefix | `useAuth`, `useLocalStorage` |
| Types/Interfaces | PascalCase | `Task`, `User`, `HabitLog` |
| Files | kebab-case | `task-card.tsx`, `use-auth.ts` |
| Functions | camelCase | `formatDate()`, `calculateScore()` |
| Constants | UPPER_SNAKE | `MAX_RETRY_COUNT`, `API_BASE_URL` |
| CSS classes | kebab-case | `btn-primary`, `card-hover` |
| API Routes | kebab-case | `/api/v1/tasks`, `/api/v1/daily-briefings` |

#### TypeScript Rules
- **NEVER use `any`**. Use `unknown` if type is truly unknown, then narrow with type guards.
- Define interfaces for ALL data structures in `packages/types/`.
- Use `type` for unions/intersections, `interface` for object shapes.
- Prefer `const` over `let`. Never use `var`.
- Use `strict` mode in tsconfig. Enable `noUncheckedIndexedAccess`.
- All function return types MUST be explicitly annotated.

#### Error Handling (Frontend)
```typescript
// ✅ Always wrap Supabase/fetch calls in try/catch with user-friendly messages
try {
  const { data, error } = await supabase.from('tasks').select('*')
  if (error) throw error
  setTasks(data)
} catch (err) {
  toast.error('Failed to load tasks. Please try again.')
  console.error('[Tasks] Fetch failed:', err)
}
```

#### Tailwind CSS
- Use design tokens from `tailwind.config.js`:
  - `text-text-primary`, `text-text-secondary`
  - `bg-background-card`, `bg-background-page`
  - `border-border-default`, `border-border-accent`
- Use component classes: `.btn`, `.card`, `.input`
- Avoid inline styles. Use Tailwind utility classes.
- No arbitrary values (`bg-[#123]`) — use design tokens only.

### 4.2 Backend (Python/FastAPI)

#### Imports — Order strictly enforced
```python
# 1. Standard library
import uuid
from datetime import datetime, timedelta

# 2. Third-party
from fastapi import APIRouter, HTTPException, Depends
from supabase import create_client

# 3. Local application
from config.core.supabase import get_supabase
from database.schemas.task import TaskCreate, TaskResponse
from shared.utils.logger import logger
```

#### Naming Conventions
| Construct | Convention | Example |
|---|---|---|
| Functions | snake_case | `create_task()`, `get_user_by_id()` |
| Classes | PascalCase | `TaskCreate`, `UserResponse` |
| Constants | UPPER_SNAKE | `DEFAULT_PAGE_SIZE`, `MAX_RETRIES` |
| Modules | snake_case | `task_routes.py`, `auth_middleware.py` |
| Pydantic models | PascalCase | `TaskCreate(BaseModel)` |
| Router variables | snake_case | `router = APIRouter(...)` |

#### Pydantic Models — ALWAYS use `database/schemas/` 
```python
# ✅ Import from database/schemas/ — never define inline in route files
from database.schemas.task import TaskCreate, TaskUpdate, TaskResponse

# ❌ NEVER do this in route files:
# class TaskCreate(BaseModel): ...
```

#### Error Handling (Backend)
```python
@router.get("/{task_id}")
async def get_task(task_id: str):
    data = supabase.table("tasks").select("*").eq("id", task_id).execute()
    if not data.data:
        raise HTTPException(status_code=404, detail="Task not found")
    return data.data[0]

# Standard status codes:
#   200 OK | 201 Created | 204 No Content (DELETE)
#   400 Bad Request | 401 Unauthorized | 403 Forbidden
#   404 Not Found | 409 Conflict | 422 Unprocessable Entity
#   429 Rate Limited | 500 Internal Server Error
```

#### Database Access — Always filter by user_id
```python
data = supabase.table("tasks").select("*").eq("user_id", user_id).execute()

result = supabase.table("tasks").insert(task).execute()
if result.error:
    raise HTTPException(status_code=400, detail=str(result.error))
```

### 4.3 Prompt YAML Frontmatter Style

Every prompt file in `prompts/` MUST have valid YAML frontmatter:

```yaml
---
version: 2.1.0                    # semver, updated per revision
status: active                     # active | draft | deprecated
model: ollama/mistral:7b           # AI model this prompt targets
max_tokens: 4096                   # Token budget for this prompt
temperature: 0.5                   # 0.0 (deterministic) - 1.0 (creative)
description: >                     # Brief purpose (required for system prompts)
  One-line summary of what this prompt does.
last_updated: 2026-06-11           # ISO date
approved_by: developer              # Who approved this prompt
review_cycle: weekly                # How often to review this prompt
tags: [tag1, tag2]                  # Categorization tags
---
```

**Rules:**
- `version`, `status`, `model`, `max_tokens`, `temperature` are **REQUIRED** on all prompts
- `description` is **REQUIRED** on system prompts; **RECOMMENDED** on agent prompts
- `tags` is **REQUIRED** on system and agent prompts; **RECOMMENDED** on templates
- `max_tokens` and `temperature` must be numbers (not strings)
- `status` must be one of: `active`, `draft`, `deprecated`
- `version` must follow semver (MAJOR.MINOR.PATCH)
- Files MUST use UTF-8 encoding (BOM is auto-stripped by PromptLoader)

---

## 5. UI/UX & Design System

### 5.1 Design Direction

**Commit to bold, distinctive cyberpunk aesthetics.** This is NOT a generic AI product. Every visual element should feel intentional and distinctive.

### 5.2 Design Tokens

```css
--bg-page: #0A0B0F;
--bg-card: #13151A;
--bg-card-hover: #1A1D24;
--accent-primary: #6366F1;
--accent-secondary: #818CF8;
--accent-neon: #00FFA3;
--accent-warning: #F59E0B;
--accent-danger: #EF4444;
--text-primary: #F1F5F9;
--text-secondary: #94A3B8;
--border-default: #1E293B;
--border-accent: #334155;
```

### 5.3 Typography

| Usage | Font | Weight | Size |
|---|---|---|---|
| Display / Headings | Syne | 600-700 | 24px-48px |
| Body text | DM Sans | 400-500 | 14px-16px |
| Code / Monospace | JetBrains Mono | 400 | 13px-14px |

### 5.4 Required Component Classes

```html
<button class="btn btn-primary">Primary</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn btn-ghost">Ghost</button>
<button class="btn btn-danger">Danger</button>

<div class="card">
  <h3 class="card-title">Section Title</h3>
  <div class="card-content">Content here</div>
</div>

<input class="input" placeholder="Enter text..." />
<h1 class="text-gradient">Section Heading</h1>
<div class="animate-pulse-glow"></div>
```

### 5.5 Effects & Motion
- **Framer Motion** for page loads (staggered reveals, fade-ins)
- **Glow shadows** on interactive elements (`box-shadow` with neon colors)
- **Glass morphism** for modals/overlays (`backdrop-filter: blur()`)
- **Grid backgrounds** for hero/landing sections
- **Backdrop blur** on navbars and sticky headers

### 5.6 What to AVOID
- Generic AI aesthetics (bubbly, pastel, robotic)
- System fonts (Inter, Arial, Helvetica)
- Predictable layouts — use staggered grids, asymmetric cards, bento-box patterns
- Overly complex gradients — keep it clean cyberpunk, not rainbow
- Arbitrary Tailwind values — always use design tokens

---

## 6. Project Structure

```
ARIA OS - SecondBrain/
│
├── AGENTS.md                       # THIS FILE — AI agent reference (v4)
├── Makefile                        # Common dev commands (dev-api, lint, test, etc.)
├── .pre-commit-config.yaml         # Pre-commit hooks (ruff, black, prompts, security)
├── CHANGELOG.md                    # Release history
├── CODE_OF_CONDUCT.md              # Community standards
├── CONTRIBUTING.md                 # Contribution guide
├── LICENSE                        # MIT License
├── SECURITY.md                     # Vulnerability reporting
├── .env.example                    # Environment template (comprehensive)
├── docker-compose.yml              # Local dev orchestration (3 services + optional Ollama)
├── pytest.ini                      # Pytest configuration (with coverage)
│
├── .github/
│   ├── dependabot.yml              # Automated dependency updates (npm + pip + docker)
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       └── ci.yml                  # 5 CI jobs: frontend, backend, prompts, docker, security
│
├── .vscode/
│   ├── extensions.json             # Recommended extensions
│   └── settings.json               # Editor settings (format-on-save, linting, etc.)
│
├── apps/
│   ├── api/                        # FastAPI backend (v1 API)
│   │   ├── main.py                 # App entry, middleware, router registration, health checks
│   │   ├── requirements.txt        # Python deps (fastapi, supabase, anthropic, etc.)
│   │   ├── Dockerfile              # Multi-stage build (non-root user)
│   │   ├── .dockerignore
│   │   └── app/api/               # 13 route handlers
│   │       ├── tasks.py            # /api/v1/tasks/ (6 endpoints)
│   │       ├── courses.py          # /api/v1/courses/ (4 endpoints)
│   │       ├── goals.py            # /api/v1/goals/ (4 endpoints)
│   │       ├── habits.py           # /api/v1/habits/ (4 endpoints)
│   │       ├── ideas.py            # /api/v1/ideas/ (4 endpoints)
│   │       ├── income.py           # /api/v1/income/ (4 endpoints)
│   │       ├── opportunities.py    # /api/v1/opportunities/ (4 endpoints)
│   │       ├── projects.py         # /api/v1/projects/ (4 endpoints)
│   │       ├── resources.py        # /api/v1/resources/ (4 endpoints)
│   │       ├── sleep.py            # /api/v1/sleep/ (3 endpoints)
│   │       ├── time.py             # /api/v1/time/ (7 endpoints)
│   │       ├── chat.py             # /api/v1/chat/ (1 endpoint) — ARIA
│   │       └── automation.py       # /api/v1/automation/ (3 endpoints)
│   │
│   ├── web/                        # Next.js 14 frontend
│   │   ├── package.json            # ~40 deps (next, framer-motion, supabase, etc.)
│   │   ├── tailwind.config.js      # Cyberpunk design tokens (218 lines)
│   │   ├── Dockerfile
│   │   ├── .dockerignore
│   │   ├── middleware.ts            # Auth middleware
│   │   ├── playwright.config.ts     # E2E tests
│   │   ├── vitest.config.ts         # Unit tests
│   │   ├── sentry.client.config.ts  # Error tracking
│   │   ├── app/                    # Pages (18 routes: dashboard, tasks, courses, etc.)
│   │   ├── components/             # UI components (Button, Card, Modal, etc.)
│   │   ├── hooks/                  # useAuth, useNetworkStatus, useRealtime
│   │   ├── lib/                    # supabase, stores, query, types, utils
│   │   ├── styles/                 # globals.css
│   │   ├── types/                  # Shared TypeScript types
│   │   └── public/                 # Icons, manifest, service worker
│   │
│   ├── admin/                      # WIP — Admin panel
│   └── mobile/                     # WIP — React Native / PWA
│
├── packages/
│   ├── ai/                         # AI agent system
│   │   ├── __init__.py             # Exports agents module
│   │   ├── client.py               # LLMClient with retry, circuit breaker, fallback
│   │   ├── prompt_loader.py         # PromptLoader — reads prompts/, parses YAML frontmatter
│   │   └── agents/                  # 10 agent modules (8 live + 2 new)
│   │       ├── __init__.py          # Exports all 10 agent modules
│   │       ├── briefing_agent.py    # A09 — Daily briefing generator
│   │       ├── memory_agent.py      # A02 — Memory consolidation
│   │       ├── learning_agent.py    # A03 — Pattern detection
│   │       ├── opportunity_agent.py # A06 — Opportunity matching
│   │       ├── opportunity_matching_agent.py # A15 — Opportunity scoring engine
│   │       ├── task_agent.py        # A01 — Task breakdown & analysis
│   │       ├── weekly_review_agent.py # A10 — Weekly review generator
│   │       ├── sleep_agent.py       # A13 — Sleep analysis & wind-down
│   │       ├── nudge_agent.py       # A14 — Course/habit nudges
│   │       └── roadmap_agent.py     # A08 — Skill development roadmap optimizer
│   │
│   ├── config/core/                # FastAPI configuration
│   │   ├── config.py               # Pydantic Settings (22 fields)
│   │   ├── supabase.py             # Supabase client
│   │   └── auth.py                 # JWT validation
│   ├── database/schemas/           # Pydantic models (all 13 tables)
│   ├── shared/utils/               # Cross-cutting utilities
│   │   ├── logger.py               # Structured JSON logging
│   │   ├── rate_limiter.py         # Per-endpoint rate limiter
│   │   ├── cache.py                # In-memory TTL cache with decorator
│   │   ├── security.py             # Token gen, sanitization
│   │   ├── retry.py                # Exponential backoff + CircuitBreaker
│   │   └── validators.py           # Input validators
│   ├── types/                      # Shared TypeScript types
│   └── ui/                         # Shared React components
│
├── services/
│   └── scheduler/                  # APScheduler with 7 cron jobs
│       ├── main.py                 # 7 jobs: briefing, radar, review, habits, tasks, sleep, nudges
│       ├── requirements.txt        # Dependencies
│       ├── Dockerfile
│       ├── .dockerignore
│       └── crons/                  # 7 individual cron job modules
│
├── prompts/                        # 14 AI prompt templates
│   ├── system/                     # 2 system prompts
│   │   ├── aria_system.md          # ARIA orchestration (369 lines, v3.0.0)
│   │   └── guardrails.md           # Safety guardrails (346 lines, v2.0.0)
│   ├── agents/                     # 10 agent prompts
│   │   ├── briefing_agent.md       # Daily briefing — 957 lines
│   │   ├── weekly_review_agent.md  # Weekly review — 1264 lines
│   │   ├── opportunity_radar_agent.md # Opportunity matching — 822 lines
│   │   ├── opportunity_matching_agent.md # Scoring engine — 210 lines (NEW)
│   │   ├── memory_agent.md         # Memory consolidation — 821 lines
│   │   ├── learning_agent.md       # Pattern detection — 850 lines
│   │   ├── task_agent.md           # Task analysis — 839 lines
│   │   ├── sleep_agent.md          # Wind-down messages — 905 lines
│   │   ├── nudge_agent.md          # Course/habit nudges — 665 lines
│   │   └── roadmap_agent.md        # Skill roadmap optimizer — 257 lines (NEW)
│   └── templates/                  # 2 template prompts
│       ├── context_assembly.md
│       └── email_templates.md
│
├── docs/                           # ~120 documentation files, ~16 MB
│   ├── product/                    # Vision, PRD, BRD, SRS, Features, Personas
│   ├── engineering/                # Architecture, API, DB, Events, ADRs, Modules
│   │   └── adr/                    # 8 Architecture Decision Records
│   ├── design/                     # UI/UX, Design System, Tokens, Wireframes
│   ├── ai/                         # Agent spec (239KB), Memory, Knowledge Graph
│   ├── security/                   # Security, Compliance, Data Privacy
│   ├── devops/                     # Deployment, DevOps, Release Mgmt
│   ├── qa/                         # Testing, QA, E2E, Performance
│   └── operations/                 # Runbooks, Monitoring, DR, SLA, Risk
│
├── infrastructure/                 # Docker, Terraform (WIP)
├── tests/                          # 50+ tests (6 test files)
│   ├── conftest.py                 # Adds packages/ to sys.path
│   ├── test_prompt_loader.py       # 16 tests: PromptLoader, frontmatter, rendering
│   ├── test_agent_prompts.py       # 14 tests: per-agent content, size, tags
│   ├── test_api_endpoints.py       # API endpoint behavior tests (mocked)
│   ├── test_llm_client.py          # LLM client retry, circuit breaker, JSON parsing
│   ├── test_scheduler.py           # Scheduler job registration, trigger configs
│   └── test_validate_script.py     # Validation script unit tests
├── scripts/                        # Utility scripts
│   └── validate_prompts.py         # CI script — validates all 14 prompts' frontmatter
├── analytics/                      # Analytics config (WIP)
├── monitoring/                     # Monitoring config (WIP)
└── .github/workflows/
    └── ci.yml                      # 5 CI jobs: frontend, backend, prompts, docker, security
```

---

## 7. Database Schema

### 7.1 Complete Table List

| Table | Purpose | RLS Enabled | Indexed Columns |
|---|---|---|---|
| `tasks` | Task CRUD with priority, status, dependencies | ✅ | user_id, status, due_date, priority |
| `courses` | Course tracking with progress, deadlines | ✅ | user_id, status |
| `goals` | Goal management with roadmap, milestones | ✅ | user_id, status |
| `habits` | Habit definitions with frequency, streaks | ✅ | user_id |
| `habit_logs` | Daily habit completion logs | ✅ | user_id, date |
| `sleep_logs` | Sleep tracking with score, debt | ✅ | user_id, date |
| `income_entries` | Income logs with hourly rate | ✅ | user_id, date |
| `projects` | Project phases, blockers, URLs | ✅ | user_id |
| `ideas` | Idea pipeline (raw → validating → building) | ✅ | user_id, stage |
| `resources` | Resource library with tags | ✅ | user_id |
| `opportunities` | Opportunity radar with match scores | ✅ | user_id, match_score |
| `time_entries` | Time tracking with Pomodoro, deep work | ✅ | user_id, date |
| `chat_messages` | ARIA chat history | ✅ | user_id, created_at |
| `daily_briefings` | Generated morning briefings | ✅ | user_id, date |
| `weekly_reviews` | Generated weekly reviews | ✅ | user_id, week_start |
| `memory` | AI persistent memory (preferences, patterns) | ✅ | user_id |
| `learning_progress` | Learning metrics snapshots | ✅ | user_id, date |
| `users` | User profile, preferences, settings | ✅ | id, email |

### 7.2 RLS Policy Template

```sql
CREATE POLICY user_isolation ON tasks
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
```

**AGENTS MUST:**
- Filter ALL queries by `user_id`
- Never write queries that could expose cross-user data
- Validate `user_id` matches authenticated user
- Never use `select('*')` in production — always specify columns

### 7.3 Common Query Patterns

```typescript
// TypeScript (Frontend)
const { data, error } = await supabase
  .from('tasks')
  .select('id, title, status, priority, due_date')
  .eq('user_id', user.id)
  .eq('status', 'pending')
  .order('due_date', { ascending: true })
  .limit(20)

// Python (Backend)
data = supabase.table("tasks")\
  .select("id, title, status, priority, due_date")\
  .eq("user_id", user_id)\
  .execute()
```

---

## 8. API Endpoint Reference

### 8.1 Router Inventory

All endpoints are under `/api/v1/` prefix. See [Section 24](#24-api-versioning-strategy) for versioning details.

| Module | File | Endpoints | Auth | Pagination |
|---|---|---|---|---|
| Tasks | `tasks.py` | GET, POST, GET/{id}, PUT/{id}, DELETE/{id}, POST/{id}/complete | ✅ | ✅ |
| Courses | `courses.py` | GET, POST, GET/{id}, PUT/{id}, DELETE/{id} | ✅ | ✅ |
| Goals | `goals.py` | GET, POST, GET/{id}, PUT/{id}, DELETE/{id} | ✅ | ✅ |
| Habits | `habits.py` | GET, POST, PUT/{id}, DELETE/{id} | ✅ | ✅ |
| Sleep | `sleep.py` | GET, POST, DELETE/{id} | ✅ | ✅ |
| Income | `income.py` | GET, POST, PUT/{id}, DELETE/{id} | ✅ | ✅ |
| Projects | `projects.py` | GET, POST, PUT/{id}, DELETE/{id} | ✅ | ✅ |
| Ideas | `ideas.py` | GET, POST, PUT/{id}, DELETE/{id} | ✅ | ✅ |
| Resources | `resources.py` | GET, POST, PUT/{id}, DELETE/{id} | ✅ | ✅ |
| Opportunities | `opportunities.py` | GET, POST, PUT/{id}, DELETE/{id} | ✅ | ✅ |
| Time | `time.py` | GET, POST, PUT/{id}, DELETE/{id}, POST/stop, GET/stats/daily | ✅ | ✅ |
| Chat | `chat.py` | POST | ✅ | — |
| Automation | `automation.py` | POST trigger/briefing, POST/radar, POST/weekly-review | ✅ | — |

### 8.2 Standard Endpoint Pattern

```python
from fastapi import APIRouter, HTTPException, Depends, Query
from database.schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

@router.get("/")
async def list_tasks(
    user_id: str = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    data = supabase.table("tasks")\
        .select("id, title, status, priority, due_date")\
        .eq("user_id", user_id)\
        .order("created_at", desc=True)\
        .range(offset, offset + limit - 1)\
        .execute()
    return {"data": data.data, "limit": limit, "offset": offset}

@router.post("/", status_code=201)
async def create_task(task: TaskCreate, user_id: str = Depends(get_current_user)):
    result = supabase.table("tasks").insert({
        **task.model_dump(), "user_id": user_id
    }).execute()
    if result.error:
        raise HTTPException(status_code=400, detail=str(result.error))
    return result.data[0]
```

### 8.3 Error Response Schema

```json
{
  "detail": "Human-readable error message",
  "error_code": "TASK_NOT_FOUND",
  "request_id": "uuid-string",
  "timestamp": "2026-06-14T12:00:00Z"
}
```

---

## 9. AI Agent Architecture

### 9.1 ARIA — Orchestrator Agent

ARIA is the single point of intelligence. It receives every user message, classifies intent, dispatches to sub-agents, and synthesizes responses.

**Architecture:** In-process async function calls (per ADR-004)
**Default AI:** Ollama (Mistral 7B, local, free)
**Fallback AI:** Claude Sonnet 4 (cloud, ~$0.015/request)
**Resilience:** Circuit breaker (5 failures → 60s cooldown), exponential backoff retry (3 attempts)
**Prompt System:** All agent prompts loaded from `prompts/` via `PromptLoader` with graceful fallback to inline defaults

### 9.2 PromptLoader — Central Prompt Registry

Every agent module imports prompts from `PromptLoader`, not inline strings:

```python
from ai.prompt_loader import prompts

entry = prompts.get_agent("agent_name")     # Returns PromptEntry | None
entry = prompts.get_required("agent_name")  # Raises if not found
entry.render(field1="value1")               # Renders template with kwargs
```

### 9.3 Agent Registry (17 agents)

| ID | Agent | Type | Trigger | LLM | Module | Prompt File | Status |
|---|---|---|---|---|---|---|---|
| A00 | ARIA (Orchestrator) | Orchestrator | User message | Yes | — | `system/aria_system.md` | Design |
| A01 | Planner | Service | 7 AM + on-demand | Yes | — | — | Design |
| A02 | Memory | Service | Every chat (bg) | Yes | `memory_agent.py` | `agents/memory_agent.md` | ✅ Live |
| A03 | Learning | Service | Daily + on-demand | Yes | `learning_agent.py` | `agents/learning_agent.md` | ✅ Live |
| A04 | Reminder | Cron | Every 15 min | No | — | — | ✅ Live |
| A05 | Career | Service | Weekly + on-demand | Yes | — | — | Design |
| A06 | Opportunity | Cron | 6 AM daily | Yes | `opportunity_agent.py` | `agents/opportunity_radar_agent.md` | ✅ Live |
| A07 | Analytics | Service | Real-time + weekly | No | — | — | Design |
| A08 | Roadmap | Service | On-demand + weekly | Yes | `roadmap_agent.py` | `agents/roadmap_agent.md` | ✅ Live |
| A09 | Daily Briefing | Cron | 7 AM daily | Yes | `briefing_agent.py` | `agents/briefing_agent.md` | ✅ Live |
| A10 | Weekly Review | Cron | Sun 8 PM | Yes | `weekly_review_agent.py` | `agents/weekly_review_agent.md` | ✅ Live |
| A11 | Missed Task Checker | Cron | Every 15 min | No | — | — | ✅ Live |
| A12 | Habit Miss Checker | Cron | Midnight daily | No | — | — | ✅ Live |
| A13 | Sleep & Bedtime | Cron | 9:30 PM + wake | Yes | `sleep_agent.py` | `agents/sleep_agent.md` | ✅ Live |
| A14 | Course Progress Nudge | Cron | 6 PM daily | Yes | `nudge_agent.py` | `agents/nudge_agent.md` | ✅ Live |
| A15 | Opportunity Matching | Service | On-demand | Yes | `opportunity_matching_agent.py` | `agents/opportunity_matching_agent.md` | ✅ Live |
| A16 | (Reserved) | — | — | — | — | — | — |

### 9.4 Prompt Files Inventory (14 files)

```
prompts/
├── system/
│   ├── aria_system.md            (12.5KB, 369 lines)  — Core ARIA orchestration prompt
│   └── guardrails.md             (11.7KB, 346 lines)  — Safety rules, content boundaries
├── agents/
│   ├── briefing_agent.md         (28KB, 957 lines)    — 7 day profiles, 5 examples
│   ├── weekly_review_agent.md    (35KB, 1264 lines)   — 5 review profiles, 4 examples
│   ├── opportunity_radar_agent.md(24KB, 822 lines)    — Category matching algorithm
│   ├── opportunity_matching_agent.md (6KB, 210 lines) — Scoring engine (NEW)
│   ├── memory_agent.md           (24KB, 821 lines)    — Retention/discard logic
│   ├── learning_agent.md         (18KB, 850 lines)    — Pattern detection
│   ├── task_agent.md             (20KB, 839 lines)    — Breakdown + prioritization
│   ├── sleep_agent.md            (26KB, 905 lines)    — 5 sleep profiles, wind-down
│   ├── nudge_agent.md            (19KB, 665 lines)    — 5 nudge scenarios, escalation
│   └── roadmap_agent.md          (7KB, 257 lines)     — Skill roadmap optimizer (NEW)
└── templates/
    ├── context_assembly.md                — Data assembly for agent inputs
    └── email_templates.md                 — Digest and notification templates
```

All prompts include: role definition, input schema, output JSON schema, step-by-step instructions, 3-5 few-shot examples, edge cases, anti-patterns, quality criteria, and error recovery.

---

## 10. Prompt System Architecture

### 10.1 PromptLoader API Reference

The `PromptLoader` singleton is at `packages/ai/prompt_loader.py`. Every agent imports it as:

```python
from ai.prompt_loader import prompts
```

**Public API:**

| Method | Returns | Description |
|---|---|---|
| `get(name, category=None)` | `PromptEntry \| None` | Get prompt by name (optionally scoped to category) |
| `get_required(name, category=None)` | `PromptEntry` | Raises `PromptLoaderError` if not found |
| `get_system(name)` | `PromptEntry \| None` | Shorthand for `get(name, 'system')` |
| `get_agent(name)` | `PromptEntry \| None` | Shorthand for `get(name, 'agents')` |
| `get_template(name)` | `PromptEntry \| None` | Shorthand for `get(name, 'templates')` |
| `list_prompts(category=None)` | `list[str]` | List all prompt keys, optionally filtered |
| `list_categories()` | `list[str]` | List all prompt categories |
| `validate_frontmatter(name)` | `list[str]` | Returns validation errors (empty list = valid) |
| `validate_all()` | `dict[str, list[str]]` | Returns all validation errors across all prompts |
| `count_prompts()` | `dict[str, int]` | Count of prompts per category |
| `reload()` | `None` | Reload all prompts from disk |

**PromptEntry properties:**

| Property | Type | Description |
|---|---|---|
| `frontmatter` | `dict` | Parsed YAML frontmatter |
| `body` | `str` | Markdown body (prompt content) |
| `name` | `str` | Stem of filename (e.g., `briefing_agent`) |
| `file_path` | `Path` | Full path to prompt file |
| `category` | `str` | Category (system, agents, templates) |
| `system_prompt` | `str` | Alias for `body` (clarity in code) |
| `agent_prompt` | `str` | Alias for `body` (clarity in code) |
| `render(**kwargs)` | `str` | Returns `body.format(**kwargs)` if kwargs provided |
| `validate()` | `list[str]` | Validate frontmatter fields |

### 10.2 Fallback Mechanism

Every agent module implements graceful degradation with retry-aware clients:

```python
from ai.prompt_loader import prompts
from ai.client import llm

async def agent_function(...):
    loaded = prompts.get_agent("agent_name")
    if loaded:
        system = loaded.system_prompt
        user = construct_user_prompt(...)
    else:
        system = "You are an AI assistant..."
        user = "Do this thing..."

    try:
        return await llm.generate_json(user, system=system)
    except LLMProviderUnavailableError:
        return algorithmic_fallback(...)  # Always works
```

This ensures **zero downtime** if a prompt file is missing, malformed, or all AI providers fail.

### 10.3 Directory Layout Rules

```
prompts/
├── system/     # Maximum 3 files. Always loaded first. No user data references.
├── agents/     # One file per agent. Matches agent module name.
└── templates/  # Context builders, email templates. Never directly sent to LLM.
```

**Naming:** Prompt filenames use snake_case matching the agent module name (e.g., `briefing_agent.md` → `briefing_agent.py`).

**README.md** in any subdirectory is automatically skipped.

### 10.4 Frontmatter Schema

Required fields per prompt category:

| Field | System | Agent | Template |
|---|---|---|---|
| `version` | ✅ Required | ✅ Required | ✅ Required |
| `status` | ✅ Required | ✅ Required | ✅ Required |
| `model` | ✅ Required | ✅ Required | ✅ Required |
| `max_tokens` | ✅ Required | ✅ Required | ✅ Required |
| `temperature` | ✅ Required | ✅ Required | ✅ Required |
| `description` | ✅ Required | Recommended | Recommended |
| `tags` | ✅ Required | ✅ Required | Recommended |

Validation is enforced by:
1. **CI job** (`.github/workflows/ci.yml`): runs `scripts/validate_prompts.py` on every push
2. **Pre-commit hooks**: `validate-prompts` and `pytest-prompts` in `.pre-commit-config.yaml`
3. **Unit tests**: 16 tests in `tests/test_prompt_loader.py` + 14 tests in `tests/test_agent_prompts.py`
4. **Pre-merge check**: `make pre-commit`

---

## 11. Prompt Development Guide

### 11.1 Creating a New Prompt

1. Create `prompts/<category>/<name>.md` with YAML frontmatter
2. Follow the structure: Role Definition → Input Schema → Output Schema → Instructions → Examples → Edge Cases → Anti-Patterns → Quality Criteria → Error Recovery
3. Add at least 3 few-shot examples showing realistic input/output pairs
4. Run `make validate-prompts` to validate frontmatter
5. Create/update the agent module in `packages/ai/agents/` to use `prompts.get_agent("name")`
6. Register in `packages/ai/agents/__init__.py`
7. Add tests in `tests/test_agent_prompts.py` (content checks, tags, size)
8. Add frontmatter tests in `tests/test_validate_script.py` if new validation rules
9. Run `make test` to confirm 50+/50+ tests pass

### 11.2 Editing an Existing Prompt

1. Update the `version` field (bump semver appropriately: MAJOR for breaking, MINOR for additions, PATCH for fixes)
2. Edit content, keeping frontmatter valid
3. If you change the output schema, update the agent module's parsing logic
4. If you change input schema, update context builders in `prompts/templates/`
5. Run validation + tests: `make pre-commit`

### 11.3 Prompt Structure Template

```
---
<YAML frontmatter>
---

# <Title>

## Role Definition
(Who the agent is, its purpose, tone, constraints)

## Input Schema
(YAML or JSON schema of all input fields with types, defaults, examples)

## Output JSON Schema
(Full JSON schema with required/optional fields, validation rules, examples)

## Detailed Instructions
(Step-by-step reasoning chain, priority rules, decision trees)

## Few-Shot Examples
(3-5 complete input → output examples with explanations)

## Edge Cases
(Empty data, missing fields, contradictory data, errors, boundary conditions)

## Anti-Patterns
(What NOT to do, with examples of bad outputs and why they're bad)

## Quality Criteria
(Checklist for self-verification before output)

## Error Recovery
(What to do when generation fails, token budget exceeded, etc.)
```

### 11.4 Testing Prompts

```bash
# Frontmatter validation
make validate-prompts

# Content tests (keywords, size, tags)
pytest tests/test_agent_prompts.py -v

# Loader tests (loading, rendering, error cases)
pytest tests/test_prompt_loader.py -v

# Validation script tests
pytest tests/test_validate_script.py -v

# All prompt-related tests
pytest tests/ -m "prompt or agent" -v
```

**Every prompt must pass:**
- Frontmatter validation (5 required fields)
- Minimum body length (>50 chars for all, >1000 chars for agents)
- Required tags on system and agent prompts
- Valid semver version
- Valid status value

---

## 12. Common Patterns

### 12.1 Adding a New API Endpoint

```python
# 1. Create route in apps/api/app/api/<module>.py
@router.get("/search")
async def search_tasks(
    q: str,
    user_id: str = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
):
    data = supabase.table("tasks").select("*").eq("user_id", user_id)\
        .text_search("title", q).limit(limit).execute()
    return {"data": data.data, "count": len(data.data)}

# 2. Schema goes in database/schemas/ — never inline
# 3. Register in apps/api/main.py (already includes all routers)
```

### 12.2 Adding a New Frontend Page

```typescript
'use client'
import { useEffect, useState } from 'react'
import { Card } from '@/components/ui/card'

export default function ModulePage() {
  const [data, setData] = useState([])
  useEffect(() => {
    fetch('/api/v1/<module>/').then(r => r.json()).then(setData)
  }, [])
  return <Card>...</Card>
}
```

### 12.3 Adding a New Agent + Prompt

```python
# 1. Create prompt file: prompts/agents/<name>.md
# 2. Create agent module: packages/ai/agents/<name>.py

from ai.client import llm
from ai.prompt_loader import prompts

async def my_agent(user_id: str) -> dict:
    loaded = prompts.get_agent("<name>")
    system = loaded.system_prompt if loaded else "Fallback system prompt"
    user = "Your prompt here"

    try:
        return await llm.generate_json(user, system=system)
    except LLMProviderUnavailableError:
        return {"fallback": True, "data": algorithmic_result()}

# 3. Update packages/ai/agents/__init__.py
# 4. Add tests in tests/test_agent_prompts.py
# 5. Run python -m pytest tests/
```

### 12.4 Running Tests

```bash
# All tests with coverage
make test

# Specific test categories
pytest tests/ -m "prompt" -v     # Prompt-related tests only
pytest tests/ -m "agent" -v      # Agent module tests only
pytest tests/ -m "api" -v        # API endpoint tests only
pytest tests/ -m "scheduler" -v  # Scheduler tests only
pytest tests/ -k "circuit" -v    # Circuit breaker tests

# Coverage report
make test-coverage
# → Open htmlcov/index.html in browser
```

### 12.5 Debugging Tips

| Issue | Check First |
|---|---|
| API returns 500 | Check Railway logs / terminal output |
| Frontend can't connect | Check `NEXT_PUBLIC_SUPABASE_URL` in .env.local |
| Auth fails | Check Google OAuth redirect URIs in Supabase Dashboard |
| AI not responding | Check `ollama ps` (is model running?) |
| API returns 429 | Rate limit exceeded — wait 60s |
| Circuit breaker open | `python -c "from ai.client import llm; print(llm.ollama_circuit.state)"` |
| Prompt not loading | `python -c "from ai.prompt_loader import prompts; print(prompts.list_prompts())"` |
| Prompt validation fails | `python scripts/validate_prompts.py` for errors |
| CORS error | Check `CORS_ORIGINS` in backend .env |
| Port already in use | `npx kill-port 3000 8000` |
| Module import error | `pip install -r apps/api/requirements.txt` |
| Slow AI responses | Check `OLLAMA_BASE_URL` — local or cloud? |
| Missing dependencies | `make install` |

---

## 13. Environment Setup

### 13.1 Required Environment Variables

See `.env.example` for the complete list with descriptions.

**Essential variables:**
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJ...
SUPABASE_SERVICE_KEY=eyJhbGciOiJ...
JWT_SECRET=your-jwt-secret
JWT_ALGORITHM=HS256
USE_LOCAL_AI=True
OLLAMA_BASE_URL=http://localhost:11434
```

### 13.2 Quick Start (Full Stack)

```bash
# Terminal 1: Start Ollama (if using local AI)
ollama serve

# Terminal 2: Start backend
make dev-api

# Terminal 3: Start frontend
make dev-web

# Terminal 4: Start scheduler (optional)
make dev-scheduler

# Terminal 5: Validate everything
make validate-prompts
make test

# Open http://localhost:3000
```

### 13.3 Docker Quick Start

```bash
# Start all services
make docker-up

# Build and start
make docker-build
make docker-up

# Follow logs
docker compose logs -f
```

---

## 14. Documentation Map

### 14.1 Quick Reference

| Topic | Primary Document | Backup / Related |
|---|---|---|
| Product Vision | `docs/product/00_ProjectVision.md` | `docs/product/01_CurrentStateAudit.md` |
| PRD / BRD / SRS | `docs/product/02_PRD.md` | `docs/product/03_BRD.md`, `docs/product/04_SRS.md` |
| Features | `docs/product/03_Features.md` | `docs/product/05_Features.md` |
| User Stories / Acceptance | `docs/product/06_UserStories.md` | `docs/product/07_AcceptanceCriteria.md` |
| Architecture | `docs/engineering/12_Architecture.md` | `docs/engineering/13_SystemArchitecture.md` |
| API Reference | `docs/engineering/17_API.md` | `docs/engineering/18_Events.md` |
| Database | `docs/engineering/15_Database.md` | `docs/engineering/16_DataGovernance.md` |
| AI Agents | `docs/ai/20_Agent.md` (239KB) | `docs/ai/19_AI_Instructions.md` |
| Prompts | `docs/ai/PromptVersioning.md` | `prompts/` + `packages/ai/prompt_loader.py` |
| Memory Architecture | `docs/ai/22_MemoryArchitecture.md` | `docs/ai/23_KnowledgeGraph.md` |
| Design System | `docs/design/10_DesignSystem.md` | `docs/design/35_DesignTokens.md` |
| UI/UX Guidelines | `docs/design/08_UIUX.md` | `docs/design/09_Design.md` |
| Security | `docs/security/24_Security.md` | `docs/security/ThreatModel.md` |
| Deployment | `docs/devops/26_Deployment.md` | `docs/devops/27_DevOps.md` |
| Testing Strategy | `docs/qa/28_Testing.md` | `docs/qa/29_QA.md` |
| Operations / Runbooks | `docs/operations/39_Runbooks.md` | `docs/operations/40_IncidentResponse.md` |
| ADRs | `docs/engineering/adr/ADR-001*.md` (8 files) | `docs/engineering/adr/` |
| Implementation Status | `docs/operations/IMPLEMENTATION_STATUS.md` | — |

### 14.2 All Docs by Category

| Category | Count | Key Files |
|---|---|---|
| **Product** | 14 | Vision, PRD, BRD, SRS, Features, User Stories, Personas, Roadmap |
| **Design** | 8 | UI/UX, Design System, Tokens, Accessibility, Motion, Responsive |
| **Engineering** | 27 + 8 ADRs | Architecture, API, DB, Events, Agent Arch, ADRs, Modules |
| **AI** | 11 | Agent spec (239KB), Memory, Knowledge Graph, Skills, RAG |
| **Security** | 7 | Security, Compliance, Data Privacy, Auth, Encryption |
| **DevOps** | 8 | Deployment, DevOps, Release Mgmt, Docker, Kubernetes |
| **QA** | 6 | Testing, QA, E2E, Performance, Security Testing |
| **Operations** | 23 | Runbooks, Monitoring, DR, SLA, Risk, Sprint Plan, Backlog |
| **Total** | **~120 files** | **~16 MB documentation** |

---

## 15. AI Agent Instructions

### 15.1 Golden Rules (25 rules)

**Always follow these rules in order of priority:**

1. **Run `make pre-commit` before committing.** This runs all linters, validators, and tests.
2. **Supabase is the single source of truth.** Never assume data exists — always query.
3. **Filter ALL database queries by `user_id`.** RLS is enabled but explicit filtering prevents bugs.
4. **Check both frontend AND backend when fixing bugs.** Many issues span the full stack.
5. **Use cyberpunk design tokens** (`tailwind.config.js`, `globals.css`) — never plain Tailwind colors.
6. **Apply Framer Motion** for page loads (staggered reveals). Avoid jarring transitions.
7. **Avoid generic aesthetics.** Use distinctive fonts (Syne, DM Sans, JetBrains Mono) and neon accents.
8. **Never use `any` in TypeScript.** Always define proper types. Use `unknown` + type guards.
9. **Handle errors gracefully.** Every Supabase/fetch call must have try/catch with user-friendly messages.
10. **Document your changes.** Update or create doc files alongside code changes.
11. **Use PromptLoader for all agent prompts.** Never hardcode prompts in agent modules unless as fallback.
12. **Validate all prompt frontmatter.** Every prompt file must pass `make validate-prompts`.
13. **Graceful degradation first.** Every agent must work without AI via algorithmic fallback before trying the LLM.
14. **Test at three levels.** Frontend (lint + type-check), Backend (ruff + pytest), Prompts (frontmatter validation + content tests).
15. **Always use API version prefix `/api/v1/`.** Never add unversioned endpoints.
16. **Import Pydantic models from `database/schemas/`.** Never define schemas inline in route files.
17. **Use structured logging** (`logger.info`, `logger.warn`, `logger.error`) — never `print()`.
18. **Wrap ALL AI calls in try/except** with `LLMProviderUnavailableError` handling.
19. **Add pagination** (`limit`, `offset` params) to every GET list endpoint.
20. **Annotate ALL function return types** in both Python and TypeScript.
21. **Keep prompt files modular.** One agent = one prompt file. Don't merge or split arbitrarily.
22. **Bump prompt `version` on every change.** Follow semver: MAJOR.breaking, MINOR.feature, PATCH.fix.
23. **Never commit `.env` files, secrets, or API keys.** Use `.env.example` for documentation.
24. **Every new agent needs tests** in `test_agent_prompts.py` and (if applicable) `test_llm_client.py`.
25. **Every new endpoint needs a 200, 400, and 404 test case.**

### 15.2 When to Read Which Docs

| If you're working on... | Read these first |
|---|---|
| A new feature | `docs/product/03_Features.md` → `docs/engineering/12_Architecture.md` |
| A bug fix | `docs/engineering/17_API.md` → `docs/engineering/15_Database.md` |
| UI changes | `docs/design/10_DesignSystem.md` → `docs/design/35_DesignTokens.md` |
| AI/Agent changes | `docs/ai/20_Agent.md` → `prompts/` → `packages/ai/prompt_loader.py` |
| Prompt changes | `prompts/` → `scripts/validate_prompts.py` → `tests/test_agent_prompts.py` |
| API changes | `docs/engineering/17_API.md` → `docs/engineering/18_Events.md` |
| Database changes | `docs/engineering/15_Database.md` → `docs/security/24_Security.md` |
| Deployment | `docs/devops/26_Deployment.md` → `docs/operations/39_Runbooks.md` |
| Security review | `docs/security/24_Security.md` → `docs/security/ThreatModel.md` |
| Performance issue | `docs/engineering/45_PerformanceScalability.md` → Section 26 |

### 15.3 Security Reminders

- **NEVER** commit `.env` files or secrets to the repository
- **NEVER** log tokens, passwords, or API keys
- **NEVER** use `print()` for sensitive data — use structured logger with `redact=True`
- **ALWAYS** use parameterized queries (Supabase SDK handles this)
- **ALWAYS** verify `user_id` matches the authenticated user
- **NEVER** expose internal error details to the user (use generic messages)
- **ALWAYS** validate prompt frontmatter — malformed YAML can expose data
- **ALWAYS** sanitize user input before passing to LLM prompts
- **ALWAYS** use `httpx` with timeouts — never allow infinite waits

### 15.4 Architecture Principles

- **Separation of concerns:** Frontend, Backend, Scheduler, AI are independent
- **Graceful degradation:** Every feature works without AI (algorithmic fallback)
- **In-process agents:** Agents run as async functions in FastAPI (no microservices)
- **Resilience by default:** Circuit breakers, retry with backoff, provider failover
- **Zustand for state:** Only tasks + user stores; other modules use local state
- **API-first with versioning:** All data flows through `/api/v1/` REST endpoints
- **PromptLoader-driven:** All AI prompts are externalized in `prompts/` with YAML frontmatter
- **Fail-safe defaults:** Every agent has inline fallback prompts if the prompt file is unavailable
- **Observability:** Every request gets a unique ID, structured logging, duration tracking
- **Immutable prompts:** Never edit a prompt in place — bump version, keep old versions in git history

---

## 16. Testing Standards

### 16.1 Test Categories

| Category | Location | Count | Purpose |
|---|---|---|---|
| Prompt Loader | `tests/test_prompt_loader.py` | 16 | Frontmatter validation, loading, rendering, edge cases |
| Agent Prompts | `tests/test_agent_prompts.py` | 14 | Per-agent content checks, size thresholds, tags |
| API Endpoints | `tests/test_api_endpoints.py` | 6 | Endpoint response structure, error handling |
| LLM Client | `tests/test_llm_client.py` | 7 | Retry logic, circuit breaker, JSON parsing |
| Scheduler | `tests/test_scheduler.py` | 9 | Cron job registration, trigger configs, imports |
| Validate Script | `tests/test_validate_script.py` | 7 | Validation script unit tests |
| **Total** | | **~59 tests** | |

### 16.2 Coverage Thresholds

| Package | Minimum Coverage | Current |
|---|---|---|
| `packages/ai/` | 80% | ⏳ |
| `packages/config/` | 80% | ⏳ |
| `packages/shared/` | 70% | ⏳ |
| `apps/api/` | 60% | ⏳ |
| **Overall** | **70%** | ⏳ |

### 16.3 Writing Tests

**For prompt loader tests:**
```python
from ai.prompt_loader import PromptLoader

def test_my_prompt():
    loader = PromptLoader(prompts_dir)
    entry = loader.get_agent("my_agent")
    assert entry is not None
    assert "expected_keyword" in entry.body
    assert entry.frontmatter.get("status") == "active"
```

**For agent prompt content tests:**
```python
def test_my_agent_prompt():
    prompt = loader.get_agent("my_agent")
    assert prompt is not None
    assert len(prompt.body) > 1000  # Substantial content
    assert "tags" in prompt.frontmatter
```

**For API endpoint tests (mocked):**
```python
@pytest.mark.asyncio
async def test_list_tasks_structure(mock_supabase):
    mock_supabase.from_.return_value.select.return_value\
        .eq.return_value.execute.return_value.data = [
            {"id": "1", "title": "Test", "status": "pending"}
        ]
    from app.api.tasks import list_tasks
    result = await list_tasks(user_id="test-user")
    assert isinstance(result, list)
```

### 16.4 Testing Requirements

- **Prompt system**: 100% of frontmatter fields tested across all prompts
- **Agent modules**: Every public function tested (happy + error path)
- **API endpoints**: Every status code path tested (200, 400, 404, 429, 500)
- **LLM Client**: Retry logic, circuit breaker states, JSON parsing edge cases
- **New code**: Any new function/endpoint/agent MUST have corresponding tests
- **PRs without tests**: Will be blocked by CI

---

## 17. CI/CD Pipeline

### 17.1 CI Jobs (5 total)

| Job | Trigger | Steps | Timeout |
|---|---|---|---|
| **Frontend** | Push/PR to main | Checkout → Setup Node 18 → `npm ci` → `npm run lint` → `npm run type-check` → `npm run build` → upload artifact | 15 min |
| **Backend** | Push/PR to main | Checkout → Setup Python 3.10 → pip install → `ruff check` → `black --check` → pytest (with coverage, JUnit XML) → upload coverage | 15 min |
| **Prompts** | Push/PR to main | Checkout → Setup Python → pip install pytest pyyaml → `python scripts/validate_prompts.py` → `pytest -m "prompt or agent"` | 10 min |
| **Docker** | Push/PR to main (depends on frontend, backend, prompts) | Checkout → Setup Docker Buildx → Build 3 images (api, web, scheduler) → smoke test backend image | 20 min |
| **Security** | Push/PR to main | Checkout → Setup Node → `npm audit` (high severity) → Trivy vulnerability scan (Python) → OSSF Scorecard (main only) → upload SARIF | 15 min |

**Concurrency**: Jobs cancel in-progress runs for the same branch.
**Dependency chain**: Docker job depends on frontend + backend + prompts passing.

### 17.2 Local CI Simulation

```bash
# Simulate the full CI pipeline locally:
make pre-commit           # Frontend + Backend + Prompts + Tests
make docker-build         # Docker build check
make test-coverage        # Coverage report
```

### 17.3 Pre-Merge Checklist

- [ ] `make lint` (frontend + backend + prompts pass)
- [ ] `make test` (all 50+ tests pass)
- [ ] `make test-coverage` (coverage meets thresholds)
- [ ] `make docker-build` (all 3 images build successfully)
- [ ] CI passes on GitHub (all 5 jobs green)
- [ ] PR has at least 2 approvals (or 1 + owner review)
- [ ] No unresolved conversations in PR
- [ ] CHANGELOG.md updated (if user-facing changes)

---

## 18. Cost & Performance

### 18.1 AI Cost Tracking

| Agent | Default AI | Tokens/Request | Est. Cost/Req (Ollama) | Est. Cost/Req (Claude) |
|---|---|---|---|---|
| A09 — Daily Briefing | Ollama | ~800 in / ~600 out | Free (local) | ~$0.003 |
| A10 — Weekly Review | Ollama | ~1500 in / ~800 out | Free (local) | ~$0.006 |
| A06 — Opportunity Radar | Ollama | ~600 in / ~1000 out | Free (local) | ~$0.004 |
| A02 — Memory | Ollama | ~400 in / ~200 out | Free (local) | ~$0.001 |
| A03 — Learning | Ollama | ~500 in / ~300 out | Free (local) | ~$0.002 |
| A13 — Sleep | Ollama | ~300 in / ~400 out | Free (local) | ~$0.001 |
| A14 — Nudge | Ollama | ~400 in / ~200 out | Free (local) | ~$0.001 |
| A08 — Roadmap | Ollama | ~500 in / ~300 out | Free (local) | ~$0.002 |
| A15 — Opp. Matching | Ollama | ~300 in / ~200 out | Free (local) | ~$0.001 |

**Ollama (default):** Free, local, no data leaves the machine.
**Claude fallback:** Only used when `USE_LOCAL_AI=False` or Ollama circuit breaker opens.
**Monthly estimate (Ollama only):** ~50,000 tokens/day = ~$0/month.
**Monthly estimate (Claude fallback):** ~500 requests/month × $0.003 = ~$1.50/month.

### 18.2 Prompt Token Budgets

| File | max_tokens | Typical Output | Buffer |
|---|---|---|---|
| `aria_system.md` | 2048 | System context | 50% headroom |
| `briefing_agent.md` | 4096 | ~800 tokens | 5x headroom |
| `weekly_review_agent.md` | 4096 | ~1200 tokens | 3x headroom |
| `memory_agent.md` | 4096 | ~300 tokens | 12x headroom |
| All agent prompts | 4096 | Varies | 2-10x headroom |

### 18.3 Caching Strategy

- **Prompt files**: Cached in memory by `PromptLoader` singleton (loaded once at import)
- **AI responses**: No LLM response caching currently (future: semantic cache for repeated queries)
- **API responses**: In-memory TTL cache via `packages/shared/utils/cache.py` (default 5 min TTL)
- **Cache invalidation**: Manual via `cache.clear()` on shutdown, `invalidate_cache(pattern)` for targeted clears

### 18.4 Rate Limiting

- **Global:** 100 requests/minute per IP (configurable via `RATE_LIMIT_MAX` and `RATE_LIMIT_WINDOW` env vars)
- **Per-endpoint:** `/api/v1/chat` limited to 30 req/min (AI is expensive)
- **AI circuit breaker:** Opens after 5 consecutive failures, 60s cooldown
- **AI retry:** 3 attempts with exponential backoff (2s, 4s, 8s)

### 18.5 Performance SLOs

| Metric | Target | Measurement |
|---|---|---|
| API p95 latency | < 500ms | Request ID logging |
| AI response time | < 30s | LLM client timing |
| DB query time | < 200ms | Supabase dashboard |
| Frontend TTI | < 3s | Lighthouse |
| Frontend bundle size | < 300KB gzip | next/bundle-analyzer |
| Prompt load time | < 100ms | PromptLoader init |

---

## 19. Debugging Guide

### 19.1 Common Issues

| Symptom | Likely Cause | Solution |
|---|---|---|
| `cannot find module` | Missing dependency | `make install` |
| `Supabase connection refused` | Wrong URL/key | Check .env.local values |
| `Ollama not responding` | Service not running | `ollama serve` |
| `Prompts not loading` | YAML frontmatter error | `make validate-prompts` |
| `Prompt returning None` | Wrong key or file missing | `python -c "from ai.prompt_loader import prompts; print(prompts.list_prompts())"` |
| `CORS error in browser` | Wrong origin | Add origin to `CORS_ORIGINS` env var |
| `Port already in use` | Another process | `npx kill-port 3000 8000` |
| `JWT validation failed` | Wrong secret | Match `JWT_SECRET` with Supabase JWT secret |
| `Rate limited (429)` | Too many requests | Wait 60s or increase `RATE_LIMIT_MAX` |
| `Claude API error` | API key issue | Check `CLAUDE_API_KEY` is set and has credits |
| `Circuit breaker is OPEN` | Repeated AI failures | Wait for cooldown or restart service |
| `All LLM providers exhausted` | Both providers failed | Check Ollama + Claude connectivity |
| `Python module not found` | Wrong venv | `.\venv\Scripts\Activate` (Windows) |
| `Docker build fails` | Missing context | Check `.dockerignore` rules |
| `Test coverage below threshold` | Missing tests | `pytest --cov-fail-under=0` to bypass temporarily |

### 19.2 Debugging Tools

| Tool | What to Check | Command |
|---|---|---|
| Browser DevTools | Network tab, Console errors, React DevTools | F12 |
| VS Code Debugger | API breakpoints, variable inspection | F5 |
| API Docs | Endpoint schemas, try-it-out | http://localhost:8000/docs |
| Thunder Client / curl | API endpoint testing | `curl http://localhost:8000/api/v1/health` |
| Python REPL | PromptLoader contents | `python -c "from ai.prompt_loader import prompts; print(prompts.list_prompts())"` |
| Prompt Validator | Frontmatter correctness | `make validate-prompts` |
| Supabase Dashboard | Table data, RLS policies, SQL editor | supabase.com/dashboard |
| Ollama Logs | AI model output, errors | Terminal running `ollama serve` |
| Railway Logs | Backend errors in production | railway.app/dashboard |
| Vercel Logs | Frontend build errors | vercel.com/dashboard |
| Docker Logs | Container-level issues | `docker compose logs -f` |
| Coverage Report | Test coverage gaps | `open htmlcov/index.html` |

### 19.3 Request Tracing

Every API request gets a unique `X-Request-ID` header. Use it to correlate logs:

```bash
# Trace a specific request through the system
curl -v http://localhost:8000/api/v1/health  # Returns X-Request-ID header

# Search logs by request ID (if using Logtail/Datadog)
# https://logtail.com/logs?query=X-Request-ID:abc-123
```

---

## 20. Deployment Guide

### 20.1 Production Stack

| Component | Hosting | URL | Plan |
|---|---|---|---|
| Frontend | Vercel (Free) | `secondbrain-os.vercel.app` | Hobby |
| Backend | Railway (Free) | `api.secondbrain-os.com` | Starter |
| Database | Supabase (Free) | Project URL | Free |
| AI (local) | Ollama on dev machine | `localhost:11434` | Local |
| AI (fallback) | Anthropic API | Cloud | Pay-as-you-go |
| Email | Resend (Free) | API | Starter |
| Monitoring | (WIP — Logtail / Sentry) | — | — |

### 20.2 Deployment Process

```bash
# 1. Frontend (auto-deploys on git push to main)
git push origin main
# → Vercel auto-builds and deploys (preview for PRs, production for main)

# 2. Backend (auto-deploys via Railway)
# → Railway detects changes from GitHub repo

# 3. Scheduler (deployed alongside backend or as separate Railway service)
# → Requires `services/scheduler/requirements.txt` to be installed

# 4. All CI checks must pass before merge
# → 5 jobs: frontend, backend, prompts, docker, security

# 5. Manual rollback if needed
# Vercel: Dashboard → Deployments → ... → Rollback
# Railway: Dashboard → Deployments → Previous → Redeploy
```

### 20.3 Rollback Procedure

```bash
# Frontend (Vercel)
vercel rollback secondbrain-os --safe=10

# Backend (Railway)
# Dashboard → Deployments → Select previous → "Redeploy"

# Database (Supabase)
# Dashboard → Database → Backups → Restore

# If database migration caused the issue:
# Execute DOWN migration SQL in Supabase SQL Editor
```

### 20.4 Versioning

- **Prompt files**: Independent semver in YAML frontmatter `version` field
- **AGENTS.md**: Major version bumps when structure changes significantly
- **API**: Versioned via URL path (`/api/v1/`) per Section 24
- **Docs**: Tracked via git history + CHANGELOG.md
- **Docker images**: Tagged with `:latest`, `:ci`, and git SHA

---

## 21. Onboarding & Process

### 21.1 PR Workflow

1. Create a branch from `main` (`feature/`, `fix/`, `chore/`, `docs/`)
2. Make changes (code + prompts + docs + tests as needed)
3. Run pre-commit checklist: `make pre-commit`
4. Push branch and create PR (use PR template)
5. CI runs automatically (5 jobs)
6. Request review from at least 1 other developer
7. All checks must pass before merge
8. After merge, deploy happens automatically

### 21.2 What Every PR Should Include

- **Code changes**: The actual feature/bugfix
- **Tests**: At minimum, any new function needs a test
- **Documentation**: If adding features, update relevant docs
- **Prompt updates**: If changing agent behavior, update both prompt file and agent module
- **Frontmatter updates**: If editing a prompt, bump its `version` field
- **CHANGELOG entry**: Brief description of what changed
- **PR description**: What, why, how, testing done

### 21.3 Changelog Expectations

- `CHANGELOG.md` follows Keep a Changelog format
- Every version bump noted with date, author, and summary
- Prompt version bumps tracked separately in each prompt file's frontmatter
- Sections: Added, Changed, Deprecated, Removed, Fixed, Security

### 21.4 30-60-90 Day Onboarding Plan

| Day | Milestone | Tasks |
|---|---|---|
| **Day 1** | Environment setup | Clone repo, `make install`, `make test`, `make validate-prompts` |
| **Day 3** | Read AGENTS.md | Understand architecture, conventions, workflows |
| **Day 5** | First PR | Fix a small bug or add a test |
| **Day 14** | Module ownership | Take ownership of 1-2 API modules (tasks, goals, etc.) |
| **Day 30** | Prompt contribution | Create or edit a prompt file |
| **Day 60** | Cross-module feature | Build a feature spanning frontend + backend + AI |
| **Day 90** | Architecture review | Propose an ADR for architectural improvement |

### 21.5 New Developer Setup

```bash
# 1. Clone the repo
git clone <repo-url>
cd "ARIA OS - SecondBrain"

# 2. Set up environment
cp .env.example .env.local  # Edit with your values

# 3. Install all dependencies
make install

# 4. Validate setup
make validate-prompts
make test

# 5. Read AGENTS.md (this file) — start with Sections 1-6
# 6. Read docs/product/00_ProjectVision.md for product context
# 7. Start with the Quick Start (Section 13.2)
# 8. Read docs/operations/44_DeveloperOnboarding.md
```

---

## 22. Incident Response

### 22.1 Severity Levels

| Level | Label | Definition | Response SLA | Examples |
|---|---|---|---|---|
| P0 | Critical | Complete service outage, data loss, security breach | 15 min response, 1 hr fix | API down, DB corruption, auth broken |
| P1 | High | Major feature unavailable, degradation > 25% of users | 30 min response, 4 hr fix | AI not responding, scheduler stopped |
| P2 | Medium | Partial feature degradation, < 25% users affected | 2 hr response, 24 hr fix | One module failing, slow responses |
| P3 | Low | Non-critical bug, cosmetic issue, missing edge case | 24 hr response, next sprint | UI glitch, typo in prompt |
| P4 | Wishlist | Enhancement, tech debt, minor improvement | Next release | Performance optimization, refactor |

### 22.2 Escalation Matrix

| Level | Escalate To | Contact Method |
|---|---|---|
| P0 | Developer (primary) | Phone / SMS / Slack @here |
| P0 (unresponsive) | Backup Developer | Phone / Email |
| P1 | Developer | Slack DM / Email |
| P2 | Developer (next business day) | GitHub Issue / Email |
| P3-P4 | Team (sprint planning) | GitHub Issue / Project Board |

### 22.3 Incident Response Process

1. **Detect**: Automated monitoring or user report
2. **Triage**: Determine severity level (P0-P4)
3. **Respond**: Assign owner, create incident channel
4. **Mitigate**: Apply fix, rollback, or feature flag
5. **Resolve**: Confirm fix, monitor for 30 min
6. **Postmortem**: Within 48 hours for P0/P1

### 22.4 Postmortem Template

```markdown
# Incident Postmortem: [Title]

**Date:** YYYY-MM-DD
**Severity:** P0/P1/P2
**Duration:** HH:MM
**Responders:** @person

## Summary
(What happened in 2-3 sentences)

## Timeline
- HH:MM - Detection
- HH:MM - Triage
- HH:MM - Mitigation applied
- HH:MM - Resolution confirmed

## Root Cause
(What caused the incident)

## Impact
- Users affected: #
- Downtime: HH:MM
- Data loss: Yes/No

## Action Items
- [ ] Fix (link to PR)
- [ ] Monitoring (link to dashboard)
- [ ] Tests (link to test file)

## Lessons Learned
(What went well, what could be improved)
```

---

## 23. Security Compliance

### 23.1 Data Classification

| Level | Description | Examples | Storage Requirements |
|---|---|---|---|
| Public | Non-sensitive, intended for public | App version, prompt templates | No restrictions |
| Internal | Business operations, not public | User count, feature usage stats | Basic access control |
| Confidential | User-identifiable information | Email, name, preferences | Encryption at rest, RLS |
| Restricted | Highly sensitive, regulated | Auth tokens, API keys, passwords | Encryption at rest + transit, audit logs |

### 23.2 Security Best Practices

- All passwords hashed with bcrypt via `passlib`
- All JWT tokens use HS256 with configurable expiry
- All database queries filtered by `user_id` (RLS + explicit filtering)
- All API endpoints require authentication (except health)
- All secrets managed through environment variables (never in code)
- All AI prompts sanitize user input before LLM submission
- All file uploads validated for type and size (resourcs module)

### 23.3 Vulnerability Disclosure

Report security vulnerabilities to:
- **Email**: developer@secondbrain-os.com (encrypted preferred)
- **GitHub**: Use "Report a vulnerability" in repository Security tab
- **SLA**: Acknowledgment within 24 hours, fix within 7 days for critical

---

## 24. API Versioning Strategy

### 24.1 URL-Based Versioning

All endpoints are under versioned paths:

```
/api/v1/tasks        # Current stable version
/api/v2/tasks        # Future breaking changes
```

### 24.2 Deprecation Headers

When an endpoint is deprecated:

```http
GET /api/v1/tasks HTTP/1.1
Deprecation: true
Sunset: Sat, 01 Jan 2027 00:00:00 GMT
```

### 24.3 Migration Strategy

1. New endpoints are added under `/api/v1/` (backward compatible)
2. Breaking changes go under `/api/v2/`
3. Old version is deprecated with `Deprecation` + `Sunset` headers
4. Old version is removed after sunset date + 6 month notice
5. Migration guide published in docs/engineering/

### 24.4 Current Version Status

| Version | Status | Release Date | Sunset Date |
|---|---|---|---|
| v1 | ✅ Active | 2026-06-01 | TBD |

---

## 25. Observability & Monitoring

### 25.1 Log Levels

| Level | Usage | Example |
|---|---|---|
| `ERROR` | Failures requiring immediate attention | DB connection failed, AI provider down |
| `WARN` | Degraded but functioning | Circuit breaker opened, retry attempt |
| `INFO` | Normal operations | Request completed, briefing generated |
| `DEBUG` | Detailed troubleshooting | LLM prompt sent, cache hit/miss |

### 25.2 Structured Log Schema

Every log entry follows this JSON schema:

```json
{
  "timestamp": "2026-06-14T12:00:00.000Z",
  "level": "INFO",
  "message": "API Request",
  "endpoint": "/api/v1/tasks",
  "method": "GET",
  "request_id": "uuid",
  "duration_ms": 42.5,
  "status_code": 200,
  "user_id": "user-uuid"
}
```

### 25.3 RED Metrics

| Metric | Definition | Target | Alert |
|---|---|---|---|
| **Rate** | Requests per second | < 100 req/s | > 100 req/s |
| **Errors** | Error rate (5xx) | < 1% | > 5% |
| **Duration** | p95 response time | < 500ms | > 2s |

### 25.4 Health Check Endpoints

```
GET /health         → Simple alive check
GET /health/live    → Liveness (Kubernetes)
GET /health/ready   → Readiness (dependencies status)
```

**`/health/ready` response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "dependencies": {
    "supabase": {"status": "ok"},
    "ollama": {"status": "ok"},
    "claude_api": {"status": "configured"}
  }
}
```

---

## 26. Performance Benchmarks

### 26.1 API Latency SLOs

| Endpoint Category | p50 | p95 | p99 |
|---|---|---|---|
| Simple CRUD (tasks, goals) | < 100ms | < 300ms | < 1s |
| AI-powered (chat, briefing) | < 10s | < 30s | < 60s |
| Aggregations (stats, reports) | < 500ms | < 2s | < 5s |
| Health checks | < 50ms | < 100ms | < 200ms |

### 26.2 AI Response Budgets

| Agent | Target | Hard Limit |
|---|---|---|
| Daily Briefing | < 15s | 30s |
| Weekly Review | < 20s | 45s |
| Opportunity Radar | < 15s | 30s |
| Memory Agent | < 5s | 15s |
| Learning Agent | < 10s | 20s |
| Sleep Agent | < 10s | 20s |
| Nudge Agent | < 5s | 15s |
| Roadmap Agent | < 15s | 30s |

### 26.3 Bundle Size Budgets

| Asset | Budget | Current |
|---|---|---|
| Main JS bundle | < 300KB gzip | ⏳ |
| CSS bundle | < 50KB gzip | ⏳ |
| Fonts | < 100KB | ⏳ |
| Images (per page) | < 200KB | ⏳ |
| Total page weight | < 500KB | ⏳ |

---

## 27. Dependency Management

### 27.1 Update Cadence

| Ecosystem | Check Frequency | Update Window | Critical Fix |
|---|---|---|---|
| npm (frontend) | Weekly (Monday) | Within 7 days | Within 24 hours |
| pip (backend) | Weekly (Monday) | Within 14 days | Within 48 hours |
| pip (scheduler) | Weekly (Monday) | Within 14 days | Within 48 hours |
| Docker base images | Monthly | Within 30 days | Within 7 days |
| GitHub Actions | Monthly | Within 30 days | Within 7 days |

### 27.2 Dependabot Configuration

See `.github/dependabot.yml` for full configuration. Key settings:
- **Grouped PRs**: React, Next.js, Supabase, FastAPI updates grouped
- **Auto-merge disabled**: All updates require CI passing + review
- **Ignore rules**: Major version bumps for Next.js (≥15) and TypeScript (≥6)
- **Labels**: All PRs tagged with `dependencies`, ecosystem label, and `automated`

### 27.3 Breaking Change Handling

1. Dependabot PR created with changelog link
2. CI must pass (including all tests)
3. Review dependency changelog for breaking changes
4. If breaking: create migration branch, update code, merge both
5. If non-breaking: approve and merge

### 27.4 License Compliance

| License | Allowed | Notes |
|---|---|---|
| MIT | ✅ | Preferred |
| Apache 2.0 | ✅ | Compatible |
| BSD | ✅ | Compatible |
| ISC | ✅ | Compatible |
| GPL v2/v3 | ❌ | Not compatible with MIT |
| AGPL | ❌ | Not compatible |
| Proprietary | ⚠️ | Review required |

**All packages MUST pass license check before adding.**

---

## 28. Code Review Standards

### 28.1 Review Checklist (30 items)

**Functionality (6):**
- [ ] Does the code do what it's supposed to do?
- [ ] Are edge cases handled (empty data, errors, timeouts)?
- [ ] Are there race conditions or timing issues?
- [ ] Is error handling complete (try/catch everywhere)?
- [ ] Are all Supabase queries filtered by user_id?
- [ ] Does graceful degradation work without AI?

**Security (5):**
- [ ] Are secrets/credentials exposed anywhere?
- [ ] Is user input properly sanitized?
- [ ] Are environment variables used for config?
- [ ] Is RLS bypassed anywhere?
- [ ] Are LLM prompts vulnerable to injection?

**Performance (4):**
- [ ] Are N+1 queries avoided?
- [ ] Is pagination implemented for list endpoints?
- [ ] Are AI calls wrapped with timeouts?
- [ ] Are expensive operations cached?

**Maintainability (5):**
- [ ] Is the code readable and well-named?
- [ ] Are imports properly ordered?
- [ ] Are inline Pydantic models avoided (use database/schemas/)?
- [ ] Are magic numbers/strings extracted to constants?
- [ ] Is dead code removed?

**Testing (5):**
- [ ] Are there tests for the new feature/fix?
- [ ] Do all existing tests still pass?
- [ ] Are edge cases tested?
- [ ] Is coverage above threshold?
- [ ] Are mocks used for external services?

**Documentation (3):**
- [ ] Are docs updated (if needed)?
- [ ] Are prompts version-bumped?
- [ ] Is CHANGELOG.md updated?

**Style (2):**
- [ ] Does code follow project conventions (imports, naming)?
- [ ] Does frontend use design tokens?

### 28.2 Approval Rules

| PR Type | Minimum Approvals | Required Reviewers |
|---|---|---|
| Bug fix | 1 | Any |
| Feature | 2 | Area owner + 1 |
| Architecture change | 3 | All area owners |
| Prompt change | 1 | Developer or AI specialist |
| Emergency fix | 1 (post-merge) | Any |

### 28.3 Ownership Model

| Area | Owner | Backup |
|---|---|---|
| Frontend (UI/UX) | Developer | — |
| Backend (API) | Developer | — |
| AI/Agents | Developer | — |
| Prompts | Developer | — |
| Database | Developer | — |
| DevOps/Docker | Developer | — |
| Security | Developer | — |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-01 | Developer | Initial agent instructions |
| 2.0.0 | 2026-06-11 | Developer | Enterprise upgrade: 15 sections, doc map, debugging, deployment |
| 3.0.0 | 2026-06-11 | Developer | Enterprise v3: Prompt System Architecture (Sec 10), Prompt Development Guide (Sec 11), Testing Standards (Sec 16), CI/CD Pipeline (Sec 17), Cost & Performance (Sec 18), Onboarding & Process (Sec 21). Updated agent registry with 8 live agents, Project Structure with all modules, expanded Golden Rules to 16 rules. |
| **4.0.0** | **2026-06-14** | **Developer** | **Enterprise v4: Full project upgrade — 7 new sections (Incident Response, Security Compliance, API Versioning, Observability, Performance Benchmarks, Dependency Management, Code Review Standards). Expanded to 17 agents (added roadmap_agent, opportunity_matching_agent). Updated prompt inventory to 14 files. Added 5 CI jobs with Docker build stage. Created Makefile, pre-commit hooks, VSCode settings, Dependabot config. Added 4 new test files (API, LLM client, scheduler, validate script). Upgraded LLM client with circuit breaker + fallback chain. Upgraded main.py with health checks + request IDs. Removed stale agent-orchestrator duplicate. Standardized API to /api/v1/ prefix. Added .dockerignore files. Coverage threshold at 70%. 25 Golden Rules. 30-item code review checklist.** |
