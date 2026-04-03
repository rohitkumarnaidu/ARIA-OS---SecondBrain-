# AGENTS.md - Second Brain OS Developer Guide

## Project Overview

Second Brain OS is a personal AI productivity system for BTech CSE students with 15 modules (Dashboard, Tasks, Courses, YouTube, Resources, Ideas, Goals, Opportunities, Income, Projects, Academics, Habits, Sleep, Time, Chat).

- **Frontend**: Next.js 14 + React 18 + Tailwind CSS + Zustand + TypeScript
- **Backend**: FastAPI (Python 3.10+) + Supabase (PostgreSQL)
- **AI**: Ollama (local) or Claude API (fallback)

---

## Build Commands

### Frontend
```bash
cd frontend

# Development
npm run dev                  # Start dev server at localhost:3000
npm run build               # Production build
npm run start               # Start production server
npm run lint                # Run ESLint
npm run type-check          # TypeScript type checking

# Single file lint
npx next lint --file path/to/file.tsx
```

### Backend
```bash
cd backend

# Development
uvicorn main:app --reload   # Start FastAPI dev server at localhost:8000

# Install dependencies
pip install -r requirements.txt

# Python syntax check
python -m py_compile backend/main.py

# Format code
black .
ruff check .

# Run tests (if available)
pytest
pytest tests/test_file.py::TestClass::test_method -v
```

---

## Code Style Guidelines

### TypeScript / Frontend

**Imports**
- Use absolute imports with `@/` prefix (e.g., `@/components`, `@/lib`, `@/hooks`)
- Group imports: external → internal → relative
- Example:
```typescript
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { Plus, Trash2 } from 'lucide-react'
```

**Naming Conventions**
- Components: PascalCase (e.g., `TaskCard`, `Sidebar`)
- Hooks: camelCase with `use` prefix (e.g., `useAuth`, `useTasks`)
- Types/Interfaces: PascalCase (e.g., `Task`, `User`)
- Files: kebab-case (e.g., `task-card.tsx`, `use-auth.ts`)
- Constants: UPPER_SNAKE_CASE for config, camelCase for values

**Types**
- Always use TypeScript types - avoid `any`
- Define interfaces for all data structures
- Use optional properties with `?` when appropriate

**Error Handling**
- Always handle Supabase errors
- Show user-friendly error messages in UI
- Use try/catch for async operations

**Component Structure**
- Keep components under 300 lines
- Extract reusable logic into custom hooks
- Use Zustand for global state, useState for local

**Tailwind CSS**
- Use semantic color classes: `text-text-primary`, `bg-background-card`
- Avoid hardcoded colors - use design tokens
- Responsive: `md:`, `lg:` prefixes

---

### Python / Backend

**Imports**
- Standard library → Third-party → Local application
- Use absolute imports (e.g., `from app.core.supabase import get_supabase_client`)

**Naming**
- Functions/variables: snake_case (e.g., `get_tasks`, `user_id`)
- Classes: PascalCase (e.g., `TaskCreate`, `UserResponse`)
- Constants: UPPER_SNAKE_CASE

**Types**
- Use Pydantic models for all request/response schemas
- Define base models with defaults, create/response models as variants

**Error Handling**
- Use HTTPException for API errors
- Return appropriate status codes (200, 400, 401, 404, 500)
- Log errors for debugging

**FastAPI Conventions**
- Use `APIRouter` for route grouping
- Dependency injection with `Depends(get_current_user)`
- Prefix routes (e.g., `/api/tasks`, `/api/goals`)

**Database**
- Use Supabase client from `app.core.supabase`
- Always filter by `user_id` for security
- Use `.execute()` and check for `.error`

---

## Project Structure

```
ARIA OS - SecondBrain/
├── frontend/                 # Next.js 14 application
│   ├── app/                  # App router pages
│   │   ├── dashboard/        # Dashboard page
│   │   ├── tasks/            # Task manager
│   │   ├── courses/          # Course tracker
│   │   ├── goals/            # Goals & roadmaps
│   │   ├── chat/             # ARIA chat
│   │   └── ...               # Other modules
│   ├── components/           # Reusable components
│   ├── hooks/                # Custom React hooks
│   ├── lib/                  # Utilities (supabase, stores)
│   └── types/                # TypeScript definitions
│
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── api/              # API route handlers
│   │   │   ├── tasks.py       # Task CRUD
│   │   │   ├── goals.py      # Goal CRUD
│   │   │   └── ...           # Other endpoints
│   │   ├── core/             # Config, auth, supabase
│   │   └── schemas/          # Pydantic models
│   ├── agents/               # AI agents (briefing, opportunity)
│   ├── crons/                # Cron jobs (daily briefing, radar)
│   ├── services/             # Business logic
│   └── utils/                # Helper functions
│
├── docs/                     # Documentation
└── README.md                 # Setup instructions
```

---

## Database (Supabase)

Tables: `tasks`, `courses`, `goals`, `ideas`, `projects`, `resources`, `opportunities`, `income`, `habits`, `sleep_entries`, `time_entries`, `users`

Always use Row Level Security (RLS) policies. All queries must include `.eq("user_id", current_user.user.id)`.

---

## Common Patterns

### Adding a New API Endpoint
1. Create route in `backend/app/api/<module>.py`
2. Use existing pattern from other routes
3. Register router in `backend/main.py`
4. Add to frontend API call in appropriate store/hook

### Adding a New Frontend Page
1. Create directory in `frontend/app/<module>/`
2. Create `page.tsx` with full UI code
3. Add navigation link in `components/Sidebar.tsx`

### Running a Specific Test
```bash
# Backend pytest
pytest backend/tests/test_tasks.py::test_create_task -v

# Frontend - run lint on single file
npx next lint frontend/app/tasks/page.tsx
```

---

## Notes for AI Agents

- When fixing bugs, check both frontend and backend
- Supabase is the single source of truth for data
- All user data must be filtered by `user_id`
- Use Zustand stores in `frontend/lib/` for state management
- Pydantic models define API schemas in `backend/app/schemas/`
- AI agents are in `backend/agents/`, cron jobs in `backend/crons/`
- Always verify changes with lint before committing