# Backend Development Learning Path

## Document Control

| Field | Value |
|---|---|
| Document ID | LRN-BE-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-07-12 |
| Classification | Internal |

---

## Module 1: API Architecture

**Estimated time:** 0.5 day

### Learning Objectives
- Understand the FastAPI application structure (~29 route handlers)
- Know how routers are registered in `main.py`
- Understand middleware order (CORS → CSRF → Auth → Rate Limiter → Cache)
- Be able to read API docs at `/docs` (Swagger UI)

### Reading Materials
- `AGENTS.md` Section 8 (API Endpoint Reference) — 31 routers, ~80 endpoints
- `apps/api/main.py` — app entry, middleware, router registration
- `apps/api/app/api/` — browse all route handler files
- `AGENTS.md` Section 25 (Observability & Monitoring) — request tracing, logging
- Visit `http://localhost:8000/docs` — explore available endpoints

### Key Concepts
- All endpoints under `/api/v1/` prefix
- Every request gets a unique `X-Request-ID`
- Structured JSON logging with level, endpoint, duration
- Standard status codes: 200, 201, 204, 400, 401, 403, 404, 409, 422, 429, 500

### Practice Exercise
1. Start the backend with `make dev-api`
2. Open Swagger UI at `http://localhost:8000/docs`
3. Read 3 route handler files and identify the common pattern
4. Trace a request through middleware by checking logs
5. Verify the health endpoint returns OK

---

## Module 2: Database & Schemas

**Estimated time:** 1 day

### Learning Objectives
- Understand the 27 tables and their relationships
- Know how Pydantic schemas map to database tables
- Understand RLS policies and user data isolation
- Be able to write Supabase queries in Python

### Reading Materials
- `AGENTS.md` Section 7 (Database Schema) — full table reference
- `packages/database/schemas/` — browse all Pydantic models
- `packages/config/core/supabase.py` — Supabase client initialization
- `AGENTS.md` Section 7.2 (RLS Policy Template) — security model
- `AGENTS.md` Section 7.3 (Common Query Patterns) — query examples

### Key Tables
| Table | Purpose | Key Columns |
|---|---|---|
| `tasks` | Task CRUD | user_id, status, priority, due_date |
| `courses` | Course tracking | user_id, status, progress |
| `goals` | Goal management | user_id, status, milestones |
| `habits`, `habit_logs` | Habit tracking | user_id, date, streak |
| `sleep_logs` | Sleep tracking | user_id, date, score, debt |
| `chat_messages` | AI chat history | user_id, created_at |

### Practice Exercise
1. Read the `TaskCreate`, `TaskUpdate`, and `TaskResponse` Pydantic schemas
2. Trace how a field flows: DB column → Pydantic schema → API response
3. Write a simple Supabase query in Python that filters by `user_id`
4. Review the RLS policy for the tasks table

---

## Module 3: Implementing an Endpoint

**Estimated time:** 1 day

### Learning Objectives
- Walk through building a new API endpoint from schema to route
- Understand pagination (`limit`, `offset`) and error handling patterns
- Know how to register a new router in `main.py`

### Reading Materials
- `apps/api/app/api/tasks.py` — the canonical endpoint example
- `AGENTS.md` Section 8.2 (Standard Endpoint Pattern) — code template
- `AGENTS.md` Section 8.3 (Error Response Schema) — error format

### Walkthrough: Creating a New Endpoint

**Step 1: Define the schema**
```python
# In packages/database/schemas/<module>.py
class MyItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None

class MyItemResponse(BaseModel):
    id: str
    name: str
    description: str | None
    created_at: datetime
```

**Step 2: Create the route**
```python
# In apps/api/app/api/<module>.py
from fastapi import APIRouter, Depends, Query, HTTPException

router = APIRouter(prefix="/api/v1/my-items", tags=["my-items"])

@router.get("/")
async def list_items(
    user_id: str = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    data = supabase.table("my_items").select("*")\
        .eq("user_id", user_id)\
        .range(offset, offset + limit - 1)\
        .execute()
    return {"data": data.data, "limit": limit, "offset": offset}
```

**Step 3: Register the router** in `apps/api/main.py`

### Practice Exercise
1. Read `apps/api/app/api/tasks.py` — understand every line
2. Trace a POST request from route handler → Supabase → response
3. Add a `search` query parameter to an existing endpoint
4. Test the new parameter via Swagger UI

---

## Module 4: Authentication & Security

**Estimated time:** 0.5 day

### Learning Objectives
- Understand JWT-based authentication flow
- Know how RLS policy enforces user isolation
- Understand API key authentication for machine-to-machine
- Know rate limiting configuration

### Reading Materials
- `AGENTS.md` Section 23 (Security Compliance) — data classification, best practices
- `packages/config/core/auth.py` — JWT validation
- `packages/config/core/api_key_auth.py` — API key auth
- `packages/shared/utils/rate_limiter.py` — rate limiting
- `packages/shared/utils/csrf.py` — CSRF protection
- `packages/shared/utils/xss.py` — XSS sanitization

### Security Checklist
- [ ] All queries filtered by `user_id`
- [ ] Never use `select('*')` in production — specify columns
- [ ] Never log secrets, tokens, or passwords
- [ ] Always validate user input
- [ ] Always use parameterized queries (Supabase SDK does this automatically)
- [ ] Wrap external service calls with timeouts

### Practice Exercise
1. Read the JWT validation code and understand the token lifecycle
2. Trace how `get_current_user` dependency works in a route
3. Check the rate limiter configuration — identify the global and per-endpoint limits
4. Review a route handler for security compliance (all checklist items)

---

## Module 5: Testing & Deployment

**Estimated time:** 1 day

### Learning Objectives
- Understand the pytest test suite (2795+ tests, 58 test files)
- Know how to run specific test categories
- Understand the CI/CD pipeline (14 jobs)
- Be able to deploy the backend to Railway

### Reading Materials
- `AGENTS.md` Section 16 (Testing Standards) — full test inventory
- `AGENTS.md` Section 17 (CI/CD Pipeline) — 14 CI jobs
- `AGENTS.md` Section 20 (Deployment Guide) — Railway, rollback
- `pytest.ini` — pytest configuration with coverage
- `apps/api/Dockerfile` — multi-stage Docker build

### Test Categories
| Category | File(s) | Count | When to Run |
|---|---|---|---|
| All tests | `make test` | 2795+ | Before every commit |
| API tests | `test_api_endpoints.py` | 132 | After API changes |
| Schema tests | `test_schemas.py` | 97 | After schema changes |
| Config tests | `test_config_core.py` | 28 | After config changes |
| Integration | `test_integration.py` | 5 | Cross-module changes |

### Practice Exercise
1. Run `make test` and verify all tests pass
2. Run `make test-coverage` and open the HTML report
3. Run a single test with `pytest tests/test_api_endpoints.py -xvs`
4. Read the CI workflow at `.github/workflows/ci.yml`
5. Run `make docker-build` and verify the API image builds
