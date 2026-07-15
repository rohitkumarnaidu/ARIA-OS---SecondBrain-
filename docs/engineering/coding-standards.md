# Coding Standards

## Document Control

| Field | Value |
|---|---|
| Document ID | ENG-CST-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-07-14 |
| Classification | Internal |
| Owner | Developer |
| Review Cycle | Monthly |
| Supersedes | AGENTS.md Section 4 (Code Style Guidelines) |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Overview and Purpose](#2-overview-and-purpose)
3. [Language Standards](#3-language-standards)
4. [Python Coding Standards](#4-python-coding-standards)
5. [TypeScript/React Coding Standards](#5-typescriptreact-coding-standards)
6. [YAML/Prompt Frontmatter Standards](#6-yamlprompt-frontmatter-standards)
7. [SQL Standards](#7-sql-standards)
8. [File Organization Standards](#8-file-organization-standards)
9. [Naming Conventions](#9-naming-conventions)
10. [Code Review Standards](#10-code-review-standards)
11. [Tooling](#11-tooling)
12. [CI Enforcement](#12-ci-enforcement)
13. [Related Documents](#13-related-documents)

---

## 1. Executive Summary

This document defines the single authoritative coding standard for the ARIA OS project. It covers Python (FastAPI), TypeScript/React (Next.js), YAML (prompt frontmatter), and SQL conventions. All code written for this project MUST conform to these standards. These standards are enforced by pre-commit hooks, CI pipeline jobs, and code review checklists.

---

## 2. Overview and Purpose

### 2.1 Purpose

- Provide a single source of truth for all coding conventions across the monorepo
- Ensure consistency between human-written and AI-generated code
- Reduce code review friction by establishing clear expectations upfront
- Enable automated enforcement through linting, formatting, and CI tools
- Support onboarding of new developers with explicit, documented standards

### 2.2 Scope

These standards apply to all source code in the following directories:

| Directory | Language | Enforcement |
|---|---|---|
| `apps/api/` | Python (FastAPI) | Ruff, Black, pre-commit |
| `apps/web/` | TypeScript/React (Next.js) | ESLint, Prettier, tsc |
| `packages/` | Python + TypeScript | Ruff, Black, ESLint, tsc |
| `services/scheduler/` | Python | Ruff, Black, pre-commit |
| `prompts/` | YAML + Markdown | `validate_prompts.py` |
| `scripts/` | Python + Bash | Ruff, ShellCheck |
| `tests/` | Python + TypeScript | Same as source language |

### 2.3 Backward Compatibility

These standards are effective immediately. Existing code that does not conform should be updated opportunistically. New code MUST conform. PRs that introduce non-conforming code will be rejected.

---

## 3. Language Standards

### 3.1 Python

| Property | Requirement |
|---|---|
| Minimum version | 3.10+ |
| Package manager | pip with `requirements.txt` |
| Formatting | Black (line length 100) |
| Linting | Ruff (all rules enabled by default) |
| Type checking | Not enforced by CI (use type hints for documentation) |
| Testing | pytest with coverage >= 85% |

### 3.2 TypeScript

| Property | Requirement |
|---|---|
| Minimum version | 5.x |
| Package manager | npm with `package.json` |
| Formatting | Prettier |
| Linting | ESLint (strict config) |
| Type checking | `tsc --noEmit` (strict mode) |
| Testing | Vitest (unit) + Playwright (E2E) |

### 3.3 YAML / Markdown

| Property | Requirement |
|---|---|
| Encoding | UTF-8 (BOM auto-stripped by PromptLoader) |
| Frontmatter | YAML with required fields per category |
| Validation | `scripts/validate_prompts.py` in CI |
| Formatting | Not auto-formatted (manual review) |

---

## 4. Python Coding Standards

### 4.1 Import Order

Imports MUST be grouped in three sections, separated by a blank line:

```python
# 1. Standard library
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# 2. Third-party
from fastapi import APIRouter, HTTPException, Depends
from supabase import create_client
import httpx

# 3. Local application
from config.core.supabase import get_supabase
from database.schemas.task import TaskCreate, TaskResponse
from shared.utils.logger import logger
```

**Rules:**
- Within each group, sort alphabetically
- `import X` before `from X import Y`
- No wildcard imports (`from module import *`)
- Never use relative imports (`from ..module import`)

### 4.2 Naming Conventions

| Construct | Convention | Example |
|---|---|---|
| Functions | `snake_case` | `create_task()`, `get_user_by_id()` |
| Classes | `PascalCase` | `TaskCreate`, `UserResponse` |
| Constants | `UPPER_SNAKE` | `DEFAULT_PAGE_SIZE`, `MAX_RETRIES` |
| Modules | `snake_case` | `task_routes.py`, `auth_middleware.py` |
| Pydantic models | `PascalCase` | `TaskCreate(BaseModel)` |
| Router variables | `snake_case` | `router = APIRouter(...)` |
| Private functions | `_prefix` | `_validate_task()` |
| Protected members | `_prefix` | `self._internal_state` |

### 4.3 Type Hints

- All function parameters and return types MUST be annotated
- Use `Optional[T]` for nullable values (Python 3.10+ `T | None` is also acceptable)
- Use `list[T]` and `dict[str, T]` over `List[T]` and `Dict[str, T]`
- Define type aliases for complex types

```python
from typing import Optional

def process_tasks(
    user_id: str,
    status: Optional[str] = None,
    limit: int = 20,
) -> list[dict]:
    ...
```

### 4.4 Docstrings

- All public functions, classes, and modules MUST have docstrings
- Use Google-style docstrings (not reStructuredText or NumPy)
- One-line docstrings for simple functions

```python
def get_task(task_id: str) -> dict:
    """Retrieve a single task by its UUID.

    Args:
        task_id: The UUID of the task to retrieve.

    Returns:
        The task record as a dictionary.

    Raises:
        HTTPException: If the task does not exist or user lacks access.
    """
    ...
```

### 4.5 Error Handling

```python
# Standard pattern for API endpoints
@router.get("/{task_id}")
async def get_task(task_id: str, user_id: str = Depends(get_current_user)):
    data = supabase.table("tasks").select("*").eq("id", task_id).eq("user_id", user_id).execute()
    if not data.data:
        raise HTTPException(status_code=404, detail="Task not found")
    return data.data[0]

# Standard status codes:
#   200 OK | 201 Created | 204 No Content (DELETE)
#   400 Bad Request | 401 Unauthorized | 403 Forbidden
#   404 Not Found | 409 Conflict | 422 Unprocessable Entity
#   429 Rate Limited | 500 Internal Server Error
```

**Rules:**
- Wrap ALL Supabase/fetch calls in try/catch with user-friendly messages
- Raise `HTTPException` with appropriate status codes
- Never expose internal error details to the user
- Log errors with structured logging (`logger.error(...)`)
- Wrap ALL AI calls in try/except handling `LLMProviderUnavailableError`

### 4.6 Database Access

```python
# Always filter by user_id — RLS is not a substitute for explicit filtering
data = supabase.table("tasks").select("*").eq("user_id", user_id).execute()

# Always check for errors after mutations
result = supabase.table("tasks").insert(task).execute()
if result.error:
    raise HTTPException(status_code=400, detail=str(result.error))

# Never use select('*') in production — always specify columns
data = supabase.table("tasks").select("id, title, status, priority").execute()
```

### 4.7 Pydantic Models

```python
# MUST be defined in database/schemas/ — NEVER inline in route files
# ✅ Correct:
from database.schemas.task import TaskCreate, TaskUpdate, TaskResponse

# ❌ NEVER do this in route files:
# class TaskCreate(BaseModel): ...
```

### 4.8 Testing

```python
# Use pytest with async support
@pytest.mark.asyncio
async def test_list_tasks_structure(mock_supabase):
    mock_supabase.from_.return_value.select.return_value\
        .eq.return_value.execute.return_value.data = [
            {"id": "1", "title": "Test", "status": "pending"}
        ]
    from app.api.tasks import list_tasks
    result = await list_tasks(user_id="test-user")
    assert isinstance(result, list)

# Every endpoint needs 200, 400, and 404 test cases
# Every agent module needs happy + error path tests
```

---

## 5. TypeScript/React Coding Standards

### 5.1 Import Order

Imports MUST be ordered in four groups, separated by a blank line:

```typescript
// 1. React / Next.js
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

// 2. External libraries
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, Trash2 } from 'lucide-react'

// 3. Internal hooks and utilities
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'

// 4. Relative imports (last)
import { TaskCard } from './task-card'
import type { Task } from '@/types'
```

### 5.2 Naming Conventions

| Construct | Convention | Example |
|---|---|---|
| Components | `PascalCase` | `TaskCard`, `HabitCalendar` |
| Hooks | `camelCase` + `use` prefix | `useAuth`, `useLocalStorage` |
| Types/Interfaces | `PascalCase` | `Task`, `User`, `HabitLog` |
| Files | `kebab-case` | `task-card.tsx`, `use-auth.ts` |
| Functions | `camelCase` | `formatDate()`, `calculateScore()` |
| Constants | `UPPER_SNAKE` | `MAX_RETRY_COUNT`, `API_BASE_URL` |
| CSS classes | `kebab-case` | `btn-primary`, `card-hover` |
| API Routes | `kebab-case` | `/api/v1/tasks`, `/api/v1/daily-briefings` |

### 5.3 TypeScript Rules

```typescript
// NEVER use any — use unknown and narrow with type guards
function processValue(value: unknown): string {
  if (typeof value === 'string') return value
  if (typeof value === 'number') return String(value)
  throw new Error('Invalid value type')
}

// Define interfaces for ALL data structures
interface Task {
  id: string
  title: string
  status: 'pending' | 'in_progress' | 'completed'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  due_date?: string
}

// Use type for unions/intersections, interface for object shapes
type TaskStatus = 'pending' | 'in_progress' | 'completed'
type PrioritizedTask = Task & { priority: 'high' | 'urgent' }

// Prefer const over let. Never use var.
const MAX_RETRIES = 3
```

**Rules:**
- Enable `strict` mode in `tsconfig.json`
- Enable `noUncheckedIndexedAccess`
- ALL function return types MUST be explicitly annotated
- Define shared types in `packages/types/` for cross-app usage

### 5.4 React Hooks Rules

```typescript
// Always use 'use client' for interactive components
'use client'
import { useEffect, useState } from 'react'

export default function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/v1/tasks')
      .then(res => res.json())
      .then(data => {
        setTasks(data.data)
        setLoading(false)
      })
      .catch(err => {
        toast.error('Failed to load tasks')
        setLoading(false)
      })
  }, [])

  if (loading) return <div className="animate-pulse-glow">Loading...</div>
  return (
    <div className="card">
      {tasks.map(task => (
        <TaskCard key={task.id} task={task} />
      ))}
    </div>
  )
}
```

**Rules:**
- Custom hooks MUST start with `use` and be placed in `hooks/` directory
- Hooks must follow the Rules of Hooks (no conditional calls)
- Use Zustand for global state (tasks + user stores only)
- Other modules use local state (useState/useReducer)

### 5.5 Error Handling

```typescript
// Always wrap Supabase/fetch calls in try/catch with user-friendly messages
try {
  const { data, error } = await supabase.from('tasks').select('*')
  if (error) throw error
  setTasks(data)
} catch (err) {
  toast.error('Failed to load tasks. Please try again.')
  console.error('[Tasks] Fetch failed:', err)
}
```

### 5.6 Tailwind CSS

```tsx
// Use design tokens from tailwind.config.js — never plain colors
// ✅ Correct:
<div className="bg-background-card text-text-primary border-border-default" />

// ❌ Wrong:
<div className="bg-gray-800 text-white border-gray-600" />

// No arbitrary values:
// ✅ Correct: text-text-secondary
// ❌ Wrong: text-[#94A3B8]

// Use component classes:
<button className="btn btn-primary">Save</button>
<div className="card">
  <h3 className="card-title">Title</h3>
  <div className="card-content">Content</div>
</div>
<input className="input" placeholder="Enter text..." />
<h1 className="text-gradient">Section Heading</h1>
```

### 5.7 Testing (Frontend)

```typescript
// Vitest for unit tests
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { TaskCard } from './task-card'

describe('TaskCard', () => {
  it('renders task title and status', () => {
    render(<TaskCard task={{ id: '1', title: 'Test', status: 'pending' }} />)
    expect(screen.getByText('Test')).toBeDefined()
    expect(screen.getByText('pending')).toBeDefined()
  })
})
```

---

## 6. YAML/Prompt Frontmatter Standards

### 6.1 Required Fields

Every prompt file in `prompts/` MUST have valid YAML frontmatter:

```yaml
---
version: 2.1.0                    # semver, updated per revision
status: active                     # active | draft | deprecated
model: ollama/mistral:7b           # AI model this prompt targets
max_tokens: 4096                   # Token budget for this prompt
temperature: 0.5                   # 0.0 (deterministic) - 1.0 (creative)
description: >                     # Brief purpose
  One-line summary of what this prompt does.
last_updated: 2026-06-11           # ISO date
approved_by: developer              # Who approved this prompt
review_cycle: weekly                # How often to review
tags: [tag1, tag2]                  # Categorization tags
---
```

### 6.2 Field Requirements by Category

| Field | System | Agent | Template |
|---|---|---|---|
| `version` | Required | Required | Required |
| `status` | Required | Required | Required |
| `model` | Required | Required | Required |
| `max_tokens` | Required | Required | Required |
| `temperature` | Required | Required | Required |
| `description` | Required | Recommended | Recommended |
| `tags` | Required | Required | Recommended |

### 6.3 Validation Rules

- `max_tokens` and `temperature` must be numbers (not strings)
- `status` must be one of: `active`, `draft`, `deprecated`
- `version` must follow semver (MAJOR.MINOR.PATCH)
- Files MUST use UTF-8 encoding (BOM is auto-stripped by PromptLoader)
- Minimum body length: > 50 chars for all prompts, > 1000 chars for agent prompts
- Validation enforced by CI, pre-commit hooks, and unit tests

---

## 7. SQL Standards

### 7.1 RLS Policy Pattern

```sql
CREATE POLICY user_isolation ON tasks
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
```

### 7.2 Query Rules

- ALL queries MUST filter by `user_id`
- Never write queries that could expose cross-user data
- Validate `user_id` matches authenticated user
- Always specify columns in SELECT — never use `SELECT *`
- Use parameterized queries (Supabase SDK handles this automatically)
- Add appropriate indexes for frequently filtered columns (user_id, status, date)

### 7.3 Common Query Pattern

```sql
-- TypeScript (Frontend)
SELECT id, title, status, priority, due_date
FROM tasks
WHERE user_id = :user_id
  AND status = :status
ORDER BY due_date ASC
LIMIT :limit OFFSET :offset;

-- Python (Backend)
data = supabase.table("tasks")\
  .select("id, title, status, priority, due_date")\
  .eq("user_id", user_id)\
  .eq("status", "pending")\
  .order("due_date", ascending=True)\
  .range(offset, offset + limit - 1)\
  .execute()
```

---

## 8. File Organization Standards

### 8.1 File Location Rules

| File Type | Location | Example |
|---|---|---|
| API route handlers | `apps/api/app/api/` | `tasks.py` |
| Frontend pages | `apps/web/app/` | `tasks/page.tsx` |
| UI components | `apps/web/components/ui/` | `button.tsx` |
| Custom hooks | `apps/web/hooks/` | `use-auth.ts` |
| Library code | `apps/web/lib/` | `supabase.ts` |
| Pydantic models | `packages/database/schemas/` | `task.py` |
| Shared types | `packages/types/` | `task.ts` |
| Agent modules | `packages/ai/agents/` | `briefing_agent.py` |
| Prompt files | `prompts/agents/` | `briefing_agent.md` |
| Tests | `tests/` | `test_tasks.py` |
| E2E tests | `apps/web/e2e/` | `task-crud.spec.ts` |
| Scripts | `scripts/` | `validate_prompts.py` |

### 8.2 One Thing Per File

- One component per file (React/TypeScript)
- One route handler module per file (Python FastAPI)
- One Pydantic schema per file (one model or logically related group)
- One agent module per file (Python)
- One prompt per file (Markdown)
- One test file per source file (or per logical module)

### 8.3 File Naming

| Language | Convention | Example |
|---|---|---|
| Python | `snake_case.py` | `task_routes.py` |
| TypeScript (component) | `kebab-case.tsx` | `task-card.tsx` |
| TypeScript (hook) | `kebab-case.ts` | `use-auth.ts` |
| TypeScript (type) | `kebab-case.ts` | `task-types.ts` |
| Markdown (docs) | `NN_TitleCase.md` | `01_DocumentationStandards.md` |
| Markdown (prompts) | `snake_case.md` | `briefing_agent.md` |
| SQL | `kebab-case.sql` | `init-feature-flags.sql` |
| Shell | `kebab-case.sh` | `run-pentest.sh` |

---

## 9. Naming Conventions

### 9.1 Complete Reference Table

| Context | Convention | Example | Language |
|---|---|---|---|
| Python functions | `snake_case` | `get_user_by_id()` | Python |
| Python classes | `PascalCase` | `TaskCreate` | Python |
| Python constants | `UPPER_SNAKE` | `DEFAULT_PAGE_SIZE` | Python |
| Python modules | `snake_case` | `task_routes.py` | Python |
| Python private | `_prefix` | `_validate_input()` | Python |
| TS components | `PascalCase` | `TaskCard` | TS |
| TS hooks | `camelCase` + `use` | `useLocalStorage` | TS |
| TS types/interfaces | `PascalCase` | `TaskStatus` | TS |
| TS functions | `camelCase` | `formatDate()` | TS |
| TS constants | `UPPER_SNAKE` | `API_BASE_URL` | TS |
| Files (Python) | `snake_case` | `task_routes.py` | All |
| Files (TS/React) | `kebab-case` | `task-card.tsx` | All |
| Files (docs) | `NN_Name.md` | `01_API.md` | All |
| Files (prompts) | `snake_case.md` | `briefing_agent.md` | All |
| API endpoints | `kebab-case` | `/api/v1/tasks` | URL |
| CSS classes | `kebab-case` | `btn-primary` | CSS / TSX |
| DB columns | `snake_case` | `user_id` | SQL |
| DB tables | `snake_case` | `daily_briefings` | SQL |
| Env variables | `UPPER_SNAKE` | `SUPABASE_URL` | All |
| JSON fields | `snake_case` | `"user_id"` | JSON |
| Git branches | `kebab-case` | `feature/task-export` | Git |

### 9.2 API Route Naming

All API routes follow RESTful conventions:

```
/api/v1/{resource}          # List (GET), Create (POST)
/api/v1/{resource}/{id}     # Get (GET), Update (PUT), Delete (DELETE)
/api/v1/{resource}/{id}/action  # Action endpoints (POST)
```

Resources use plural nouns: `/tasks`, `/courses`, `/goals`. Never use verbs in resource paths (`/getTasks`).

---

## 10. Code Review Standards

### 10.1 Review Checklist (30 items)

**Functionality (6):**
- [ ] Does the code do what it is supposed to do?
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

### 10.2 Approval Rules

| PR Type | Minimum Approvals | Required Reviewers |
|---|---|---|
| Bug fix | 1 | Any |
| Feature | 2 | Area owner + 1 |
| Architecture change | 3 | All area owners |
| Prompt change | 1 | Developer or AI specialist |
| Emergency fix | 1 (post-merge) | Any |

### 10.3 Ownership Model

| Area | Owner | Backup |
|---|---|---|
| Frontend (UI/UX) | Developer | -- |
| Backend (API) | Developer | -- |
| AI/Agents | Developer | -- |
| Prompts | Developer | -- |
| Database | Developer | -- |
| DevOps/Docker | Developer | -- |
| Security | Developer | -- |

---

## 11. Tooling

### 11.1 Python

| Tool | Purpose | Configuration | Command |
|---|---|---|---|
| **Ruff** | Linting and auto-fix | `ruff.toml` (root) | `ruff check .` |
| **Black** | Formatting | Line length: 100 | `black .` |
| **pytest** | Testing | `pytest.ini` (root) | `pytest` |
| **pytest-cov** | Coverage | Threshold: 85% | `pytest --cov=...` |

### 11.2 TypeScript / React

| Tool | Purpose | Configuration | Command |
|---|---|---|---|
| **ESLint** | Linting | `.eslintrc.json` | `npm run lint` |
| **Prettier** | Formatting | `.prettierrc` | `npx prettier --check .` |
| **tsc** | Type checking | `tsconfig.json` (strict) | `npm run type-check` |
| **Vitest** | Unit testing | `vitest.config.ts` | `npm run test` |
| **Playwright** | E2E testing | `playwright.config.ts` | `npx playwright test` |

### 11.3 Prompt Validation

| Tool | Purpose | Configuration | Command |
|---|---|---|---|
| **validate_prompts.py** | YAML frontmatter validation | `scripts/validate_prompts.py` | `make validate-prompts` |

### 11.4 Pre-commit Hooks

Configured in `.pre-commit-config.yaml`:

| Hook | Files | Runs |
|---|---|---|
| `ruff` | `*.py` | Lint check |
| `black` | `*.py` | Format check |
| `validate-prompts` | `prompts/*.md` | Frontmatter validation |
| `eslint` | `*.ts`, `*.tsx` | Lint check |
| `prettier` | `*.ts`, `*.tsx`, `*.json`, `*.css` | Format check |

### 11.5 VS Code Settings

Recommended extensions (from `.vscode/extensions.json`):

| Extension | Purpose |
|---|---|
| `ms-python.python` | Python language support |
| `ms-python.black-formatter` | Black integration |
| `charliermarsh.ruff` | Ruff integration |
| `dbaeumer.vscode-eslint` | ESLint integration |
| `esbenp.prettier-vscode` | Prettier integration |
| `bradlc.vscode-tailwindcss` | Tailwind CSS IntelliSense |

Settings (from `.vscode/settings.json`):
- `editor.formatOnSave`: true
- `editor.codeActionsOnSave`: `source.fixAll.ruff`
- `python.formatting.provider`: `black`
- `typescript.preferences.importModuleSpecifier`: `non-relative`

---

## 12. CI Enforcement

### 12.1 CI Jobs

All coding standards are enforced in CI. See `AGENTS.md` Section 17 for complete CI pipeline.

| Job | What It Enforces | Failure Action |
|---|---|---|
| **Frontend** | ESLint, TypeScript, build | PR blocked |
| **Backend** | Ruff, Black, pytest (coverage >= 85%) | PR blocked |
| **Prompts** | Frontmatter validation, prompt content tests | PR blocked |
| **Docker** | Build succeeds | PR blocked |
| **Security** | npm audit (high severity), Trivy scan | PR blocked |

### 12.2 Pre-Commit Checklist

Run this before every commit:

```bash
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
python -m pytest tests/ --cov=packages --cov=apps/api --cov-fail-under=85
```

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `AGENTS.md` Section 4 | Source base for this document's style guidelines |
| `AGENTS.md` Section 28 | Source base for code review standards |
| `docs/governance/01_DocumentationStandards.md` | Document-level standards (not code-level) |
| `docs/qa/28_Testing.md` | Testing strategy and patterns |
| `.github/workflows/ci.yml` | CI pipeline that enforces these standards |
| `.pre-commit-config.yaml` | Pre-commit hook configuration |
| `.vscode/settings.json` | Editor settings for standard compliance |
| `ruff.toml` | Ruff configuration for Python linting |
| `pytest.ini` | pytest configuration with coverage thresholds |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-07-14 | Developer | Initial coding standards document, extracted from AGENTS.md and expanded |
