# Backend Architecture

**Document ID:** BE-ARCH-001  
**Version:** 1.0.0  
**Last Updated:** 2026-06-11  
**Applies To:** `apps/api/` — FastAPI backend  

---

## Table of Contents

1. [Framework Choice](#1-framework-choice)
2. [Directory Structure](#2-directory-structure)
3. [Router Organization](#3-router-organization)
4. [Dependency Injection Pattern](#4-dependency-injection-pattern)
5. [Middleware Stack](#5-middleware-stack)
6. [Authentication Flow](#6-authentication-flow)
7. [Authorization Pattern](#7-authorization-pattern)
8. [Error Handling Strategy](#8-error-handling-strategy)
9. [Validation (Pydantic Models)](#9-validation-pydantic-models)
10. [Background Tasks](#10-background-tasks)
11. [Database Access Layer](#11-database-access-layer)
12. [Logging](#12-logging)
13. [Testing Strategy](#13-testing-strategy)
14. [API Documentation](#14-api-documentation)
15. [Performance Optimization](#15-performance-optimization)
16. [Security Middleware](#16-security-middleware)
17. [Graceful Shutdown](#17-graceful-shutdown)
18. [Architecture Diagrams](#18-architecture-diagrams)

---

## 1. Framework Choice

### 1.1 Why FastAPI

Second Brain OS chose **FastAPI** over alternatives for the following reasons:

| Criterion | FastAPI | Flask | Django REST | Express.js |
|---|---|---|---|---|
| Async native | ✅ First-class | ❌ (via extensions) | ❌ (via channels) | ✅ (callback) |
| Auto OpenAPI/Swagger | ✅ Built-in | ❌ (flasgger) | ✅ (DRF-YASG) | ✅ (swagger-jsdoc) |
| Pydantic validation | ✅ Native | ❌ (marshmallow) | ✅ (DRF serializers) | ❌ (Joi/Zod) |
| Dependency injection | ✅ `Depends()` | ❌ (manual) | ✅ (class-based) | ❌ (middleware) |
| Performance (req/s) | ~15,000+ | ~3,000 | ~1,500 | ~25,000 |
| Type hints | ✅ Mandatory | ❌ Optional | ✅ Optional | ❌ (TypeScript) |
| Background tasks | ✅ Built-in | ❌ (celery) | ❌ (celery) | ❌ (bull) |
| File structure | Unopinionated | Unopinionated | Opinionated | Unopinionated |

**Decision:** FastAPI for its async-first design, automatic OpenAPI docs, Pydantic integration, and dependency injection system. Performance is sufficient for a single-user B2C app (peak ~50 concurrent requests).

### 1.2 Version Lock

| Dependency | Version | Purpose |
|---|---|---|
| `fastapi` | `^0.109.0` | Web framework |
| `uvicorn` | `^0.27.0` | ASGI server |
| `pydantic` | `^2.5.0` | Validation + settings |
| `supabase` | `^2.3.0` | Database client |
| `python-jose` | `^3.3.0` | JWT handling |
| `apscheduler` | `^3.10.0` | Cron scheduler |
| `pyyaml` | `^6.0.0` | YAML parsing (prompts) |

---

## 2. Directory Structure

```
apps/api/
├── main.py                              # App entry, middleware, router registration
├── requirements.txt                     # Python dependencies
├── Dockerfile                           # Multi-stage production build
├── runtime.txt                          # Python version pinning
├── __init__.py
│
└── app/
    ├── __init__.py
    │
    ├── api/                             # Route handlers (13 modules)
    │   ├── __init__.py                  # Exports all routers
    │   ├── tasks.py                     # /api/tasks/ — 6 endpoints
    │   ├── courses.py                   # /api/courses/ — 5 endpoints
    │   ├── goals.py                     # /api/goals/ — 5 endpoints
    │   ├── habits.py                    # /api/habits/ — 4 endpoints
    │   ├── sleep.py                     # /api/sleep/ — 3 endpoints
    │   ├── income.py                    # /api/income/ — 4 endpoints
    │   ├── projects.py                  # /api/projects/ — 4 endpoints
    │   ├── ideas.py                     # /api/ideas/ — 4 endpoints
    │   ├── resources.py                 # /api/resources/ — 4 endpoints
    │   ├── opportunities.py             # /api/opportunities/ — 4 endpoints
    │   ├── time.py                      # /api/time/ — 6 endpoints
    │   ├── chat.py                      # /api/chat/ — 1 endpoint
    │   └── automation.py                # /api/automation/ — 3 endpoints
    │
    ├── services/                        # Business logic layer (future)
    │   └── __init__.py
    │
    ├── middleware/                      # Custom middleware (future)
    │   └── __init__.py
    │
    └── exceptions/                     # Custom exception classes (future)
        └── __init__.py

packages/
├── config/
│   └── core/
│       ├── config.py                   # Pydantic Settings (env vars)
│       ├── supabase.py                 # Supabase client singleton
│       └── auth.py                     # JWT creation + validation
│
├── database/
│   └── schemas/
│       ├── __init__.py
│       ├── task.py                     # TaskCreate, TaskUpdate, TaskResponse
│       ├── course.py                   # CourseCreate, CourseUpdate, CourseResponse
│       ├── goal.py                     # GoalCreate, GoalUpdate, GoalResponse
│       ├── habit.py                    # HabitCreate, HabitUpdate, HabitResponse
│       ├── sleep.py                    # SleepCreate, SleepResponse
│       ├── income.py                   # IncomeCreate, IncomeUpdate, IncomeResponse
│       ├── project.py                  # ProjectCreate, ProjectUpdate, ProjectResponse
│       ├── idea.py                     # IdeaCreate, IdeaUpdate, IdeaResponse
│       ├── resource.py                 # ResourceCreate, ResourceUpdate, ResourceResponse
│       ├── opportunity.py             # OpportunityCreate, OpportunityUpdate, OpportunityResponse
│       └── time.py                     # TimeEntryCreate, TimeEntryUpdate, TimeEntryResponse
│
├── shared/
│   └── utils/
│       ├── __init__.py
│       ├── logger.py                   # Structured JSON logger
│       ├── rate_limiter.py             # Rate limiting middleware
│       ├── cache.py                    # In-memory TTL cache
│       ├── security.py                 # Token generation, sanitization
│       └── retry.py                    # Exponential backoff decorator
│
└── ai/
    ├── __init__.py                     # Exports agents module
    ├── client.py                       # LLM client (Ollama + Claude fallback)
    ├── prompt_loader.py                # PromptLoader singleton
    └── agents/
        ├── __init__.py                 # Exports all 8 agent modules
        ├── briefing_agent.py           # A09 — Daily briefing generator
        ├── memory_agent.py             # A02 — Memory consolidation
        ├── learning_agent.py           # A03 — Pattern detection
        ├── opportunity_agent.py        # A06 — Opportunity matching
        ├── task_agent.py               # A01 — Task breakdown & analysis
        ├── weekly_review_agent.py      # A10 — Weekly review generator
        ├── sleep_agent.py              # A13 — Sleep analysis & wind-down
        └── nudge_agent.py              # A14 — Course/habit nudges
```

---

## 3. Router Organization

### 3.1 Router Inventory

| Module | Prefix | Endpoints | Total |
|---|---|---|---|
| `tasks.py` | `/api/tasks` | GET /, POST /, GET /{id}, PUT /{id}, DELETE /{id}, POST /{id}/complete | **6** |
| `courses.py` | `/api/courses` | GET /, POST /, GET /{id}, PUT /{id}, DELETE /{id} | **5** |
| `goals.py` | `/api/goals` | GET /, POST /, GET /{id}, PUT /{id}, DELETE /{id} | **5** |
| `habits.py` | `/api/habits` | GET /, POST /, PUT /{id}, DELETE /{id} | **4** |
| `sleep.py` | `/api/sleep` | GET /, POST /, DELETE /{id} | **3** |
| `income.py` | `/api/income` | GET /, POST /, PUT /{id}, DELETE /{id} | **4** |
| `projects.py` | `/api/projects` | GET /, POST /, PUT /{id}, DELETE /{id} | **4** |
| `ideas.py` | `/api/ideas` | GET /, POST /, PUT /{id}, DELETE /{id} | **4** |
| `resources.py` | `/api/resources` | GET /, POST /, PUT /{id}, DELETE /{id} | **4** |
| `opportunities.py` | `/api/opportunities` | GET /, POST /, PUT /{id}, DELETE /{id} | **4** |
| `time.py` | `/api/time` | GET /, POST /, PUT /{id}, DELETE /{id}, POST /stop, GET /stats/daily | **6** |
| `chat.py` | `/api/chat` | POST / | **1** |
| `automation.py` | `/api/automation` | POST /trigger/briefing, POST /trigger/radar, POST /trigger/weekly-review | **3** |
| **Total** | | | **~53 endpoints** |

### 3.2 Router Registration

```python
# main.py
from fastapi import FastAPI
from app.api import (
    tasks, courses, goals, ideas, chat,
    projects, resources, opportunities,
    income, habits, sleep, time, automation,
)

app = FastAPI(title="Second Brain OS API", version="1.0.0")

app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])
# ... (12 more routers)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
```

### 3.3 Standard Endpoint Pattern

Every CRUD endpoint follows this exact pattern:

```python
from fastapi import APIRouter, Depends, HTTPException
from database.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(current_user=Depends(get_current_user)):
    """LIST: Return all items for the authenticated user."""
    supabase = get_supabase_client()
    response = (
        supabase.from_("tasks")
        .select("*")
        .eq("user_id", current_user.user.id)
        .execute()
    )
    return response.data

@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate, current_user=Depends(get_current_user)):
    """CREATE: Insert a new item with user_id injected."""
    supabase = get_supabase_client()
    data = task.model_dump()
    data["user_id"] = current_user.user.id
    data["status"] = "pending"
    response = supabase.from_("tasks").insert(data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data[0]

@router.get("/{item_id}", response_model=TaskResponse)
async def get_task(item_id: str, current_user=Depends(get_current_user)):
    """READ: Return single item, scoped to user."""
    supabase = get_supabase_client()
    response = (
        supabase.from_("tasks")
        .select("*")
        .eq("id", item_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Item not found")
    return response.data[0]

@router.put("/{item_id}", response_model=TaskResponse)
async def update_task(
    item_id: str, task_update: TaskUpdate, current_user=Depends(get_current_user)
):
    """UPDATE: Partial update, filtering out None values."""
    supabase = get_supabase_client()
    update_data = {k: v for k, v in task_update.model_dump().items() if v is not None}
    response = (
        supabase.from_("tasks")
        .update(update_data)
        .eq("id", item_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    if not response.data:
        raise HTTPException(status_code=404, detail="Item not found")
    return response.data[0]

@router.delete("/{item_id}")
async def delete_task(item_id: str, current_user=Depends(get_current_user)):
    """DELETE: Remove item, scoped to user."""
    supabase = get_supabase_client()
    response = (
        supabase.from_("tasks")
        .delete()
        .eq("id", item_id)
        .eq("user_id", current_user.user.id)
        .execute()
    )
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return {"message": "Item deleted"}
```

### 3.4 Special Endpoint: Chat

The chat endpoint diverges from CRUD: it fetches context from multiple tables, applies rule-based logic (with AI fallback planned), and persists messages.

```python
@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()

    # Fetch context from multiple tables
    tasks = supabase.from_("tasks").select("*").eq("user_id", current_user.user.id).eq("status", "pending").execute()
    goals = supabase.from_("goals").select("*").eq("user_id", current_user.user.id).eq("status", "active").execute()
    courses = supabase.from_("courses").select("*").eq("user_id", current_user.user.id).execute()

    # Rule-based response logic (algorithmic fallback)
    response = generate_chat_response(request.message, tasks.data, goals.data, courses.data)

    # Persist to chat_messages table
    supabase.from_("chat_messages").insert({"user_id": current_user.user.id, "role": "user", "content": request.message}).execute()
    supabase.from_("chat_messages").insert({"user_id": current_user.user.id, "role": "assistant", "content": response}).execute()

    return ChatResponse(response=response)
```

---

## 4. Dependency Injection Pattern

### 4.1 FastAPI `Depends` System

FastAPI's dependency injection handles:
- Authentication (`get_current_user`)
- Database client (`get_supabase_client`)
- Rate limiting (middleware)
- Request validation (Pydantic `Body`, `Query`, `Path`)

### 4.2 Auth Dependency

```python
# packages/config/core/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validates JWT, returns Supabase user object."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    supabase = get_supabase_client()
    user = supabase.auth.get_user(token)
    return user
```

### 4.3 Supabase Client Singleton

```python
# packages/config/core/supabase.py
import supabase
from config.core.config import settings

_supabase_client = None

def get_supabase_client():
    """Returns cached singleton Supabase client."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = supabase.create_client(
            settings.supabase_url, settings.supabase_key
        )
    return _supabase_client
```

### 4.4 Dependency Injection Flow

```
Request ──▶ Router Endpoint
                │
                ├── Depends(get_current_user) ──▶ JWT Validation
                │     ├── Extract Bearer token from Authorization header
                │     ├── Decode JWT (jose library)
                │     ├── Fetch user from Supabase
                │     └── Return user object or raise 401
                │
                ├── Depends(get_supabase_client) ──▶ Database Client
                │     └── Return cached supabase client
                │
                ├── Body / Query / Path validation (Pydantic)
                │     └── Automatic 422 response on validation failure
                │
                └── Handler Function
                      └── Business logic with user context + DB client
```

---

## 5. Middleware Stack

### 5.1 Middleware Order

```
Request
  │
  1. RateLimiter (per-IP, 100 req/min)
  │
  2. CORSMiddleware (allow frontend origins)
  │
  3. Request Logging (structured JSON)
  │
  4. Global Exception Handler (catch-all)
  │
  5. Route Handler
  │
  └── Response
```

### 5.2 Rate Limiter

```python
# packages/shared/utils/rate_limiter.py
class RateLimiter(BaseHTTPMiddleware):
    """In-memory sliding window rate limiter. 100 req/min default."""

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[datetime]] = {}
        self._lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"

        async with self._lock:
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=self.window_seconds)

            # Sliding window cleanup
            if client_ip in self.requests:
                self.requests[client_ip] = [
                    t for t in self.requests[client_ip] if t > window_start
                ]
            else:
                self.requests[client_ip] = []

            if len(self.requests[client_ip]) >= self.max_requests:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Max {self.max_requests} req/{self.window_seconds}s",
                )

            self.requests[client_ip].append(now)

        return await call_next(request)
```

### 5.3 CORS Configuration

```python
# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://secondbrain-os.vercel.app",  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5.4 Registration in main.py

```python
app = FastAPI(title="Second Brain OS API", version="1.0.0")

# Order matters: Rate limiter first (before auth/CORS processing)
app.add_middleware(RateLimiter, max_requests=100, window_seconds=60)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 6. Authentication Flow

### 6.1 Architecture

```
┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐
│  Browser  │    │  Next.js FE  │    │  FastAPI BE   │    │  Supabase  │
└────┬─────┘    └──────┬───────┘    └──────┬───────┘    └─────┬──────┘
     │                 │                    │                  │
     │  1. Click       │                    │                  │
     │  "Sign In"      │                    │                  │
     │────────────────▶│                    │                  │
     │                 │  2. Redirect to    │                  │
     │                 │  Supabase Auth UI  │                  │
     │                 │───────────────────▶│─────────────────▶│
     │                 │                    │                  │
     │  3. Google      │                    │                  │
     │  OAuth Consent  │                    │                  │
     │◀────────────────┴────────────────────┴─────────────────│
     │                 │                    │                  │
     │  4. Auth code   │                    │                  │
     │  callback       │                    │                  │
     │────────────────▶│                    │                  │
     │                 │  5. Exchange       │                  │
     │                 │  code for session  │                  │
     │                 │───────────────────▶│─────────────────▶│
     │                 │                    │                  │
     │  6. JWT +       │                    │                  │
     │  session cookie │                    │                  │
     │◀────────────────┴────────────────────┴─────────────────│
     │                 │                    │                  │
     │  7. API call    │                    │                  │
     │  with Bearer    │                    │                  │
     │  token          │                    │                  │
     │─────────────────────────────────────▶│                  │
     │                 │                    │  8. Validate     │
     │                 │                    │  JWT + user_id  │
     │                 │                    │─────────────────▶│
     │                 │                    │                  │
     │  9. Response    │                    │  10. Return      │
     │◀─────────────────────────────────────│  filtered data   │
     │                 │                    │                  │
```

### 6.2 Frontend Login

```typescript
// apps/web/hooks/useAuth.ts
export function useAuth() {
  const [user, setUser] = useState<SupabaseUser | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check existing session on mount
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null)
      setLoading(false)
    })

    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null)
      setLoading(false)
    })

    return () => subscription.unsubscribe()
  }, [])

  return { user, loading }
}
```

```typescript
// apps/web/lib/userStore.ts — Sign In
signIn: async () => {
  const { error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: { redirectTo: `${window.location.origin}/dashboard` },
  })
  if (error) throw error
}
```

### 6.3 Backend JWT Validation

```python
# packages/config/core/auth.py
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Extract and validate Bearer token from request."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    supabase = get_supabase_client()
    user = supabase.auth.get_user(token)
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Generate JWT for auth flow."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
```

---

## 7. Authorization Pattern

### 7.1 User ID Scoping

**Every database query MUST filter by `user_id`.** RLS is enabled in Supabase as a defense-in-depth measure, but explicit filtering prevents bugs during development.

```python
# ✅ CORRECT: Always filter by user_id
@router.get("/")
async def get_tasks(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = (
        supabase.from_("tasks")
        .select("*")
        .eq("user_id", current_user.user.id)    # REQUIRED
        .execute()
    )
    return response.data

# ❌ WRONG: Missing user_id filter (exposes cross-user data)
@router.get("/")
async def get_tasks(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    response = supabase.from_("tasks").select("*").execute()  # NO USER FILTER
    return response.data
```

### 7.2 RLS Policy (Defense in Depth)

```sql
-- Supabase RLS policy applied to ALL tables
CREATE POLICY user_isolation ON tasks
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
```

---

## 8. Error Handling Strategy

### 8.1 Error Handling Layers

```
Layer 1: Pydantic Validation (automatic)
  └─ Invalid request body → 422 Validation Error

Layer 2: HTTPException (explicit)
  └─ Business logic errors → 400, 401, 404, 429

Layer 3: Global Exception Handler (catch-all)
  └─ Unhandled exceptions → 500 Internal Server Error (logged)
```

### 8.2 HTTPException Usage

```python
from fastapi import HTTPException

# 400 — Bad Request (validation error, duplicate, etc.)
raise HTTPException(status_code=400, detail="Task title already exists")

# 401 — Unauthorized (missing/invalid token)
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# 404 — Not Found
raise HTTPException(status_code=404, detail="Task not found")

# 429 — Rate Limited
raise HTTPException(
    status_code=429,
    detail=f"Rate limit exceeded. Max {self.max_requests} req/{self.window_seconds}s",
)
```

### 8.3 Global Exception Handler

```python
# main.py — For unhandled exceptions
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log full traceback
    logger.error(
        "Unhandled exception",
        endpoint=request.url.path,
        method=request.method,
        error=str(exc),
        traceback=traceback.format_exc(),
    )

    # Return sanitized response (no stack trace to client)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred. Please try again later.",
            "error_id": str(uuid.uuid4()),  # For correlating with logs
        },
    )
```

### 8.4 Per-Endpoint Error Handling

```python
# All endpoints follow this try/except pattern
@router.post("/")
async def create_task(task: TaskCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    data = task.model_dump()
    data["user_id"] = current_user.user.id

    response = supabase.from_("tasks").insert(data).execute()

    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)

    return response.data[0]
```

---

## 9. Validation (Pydantic Models)

### 9.1 Schema Naming Convention

| Model | Purpose | Validation |
|---|---|---|
| `TaskCreate` | Request body for POST | Required + optional fields, length limits |
| `TaskUpdate` | Request body for PUT | All fields optional (partial updates) |
| `TaskResponse` | Response body for all endpoints | All fields, computed timestamps |

### 9.2 Example Schemas

```python
# packages/database/schemas/task.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    priority: Literal['low', 'medium', 'high', 'urgent'] = 'medium'
    category: Literal['study', 'project', 'habit', 'personal', 'income'] = 'personal'
    estimated_minutes: Optional[int] = Field(None, ge=5, le=480)
    due_date: Optional[datetime] = None
    goal_id: Optional[str] = None
    project_id: Optional[str] = None
    is_recurring: bool = False
    recurring_frequency: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    priority: Optional[Literal['low', 'medium', 'high', 'urgent']] = None
    category: Optional[Literal['study', 'project', 'habit', 'personal', 'income']] = None
    status: Optional[Literal['pending', 'in_progress', 'completed', 'cancelled']] = None
    estimated_minutes: Optional[int] = Field(None, ge=5, le=480)
    due_date: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    priority: str
    category: str
    status: str
    estimated_minutes: Optional[int]
    due_date: Optional[datetime]
    goal_id: Optional[str]
    project_id: Optional[str]
    completed_at: Optional[datetime]
    missed_count: int
    dependency_id: Optional[str]
    is_recurring: bool
    recurring_frequency: Optional[str]
    created_at: datetime
    updated_at: datetime
```

### 9.3 Auto-Validation Behavior

```python
# FastAPI automatically validates at these injection points:

# 1. Request body → TaskCreate Pydantic model
async def create_task(task: TaskCreate):  # 422 if invalid

# 2. URL path params
async def get_task(task_id: str):  # Validated as string

# 3. Query params (with defaults)
@router.get("/search")
async def search_tasks(q: str, page: int = 1, limit: int = 50):

# 4. Response model (serialization + field filtering)
@router.get("/", response_model=List[TaskResponse])  # Enforces output shape
```

---

## 10. Background Tasks

### 10.1 Scheduler Service

The scheduler runs as a **separate service** (`services/scheduler/main.py`) using APScheduler's `AsyncIOScheduler` with 6 cron jobs:

| Job ID | Cron Trigger | Description |
|---|---|---|
| `daily_briefing` | 7 AM daily | Generate personalized morning briefing |
| `opportunity_radar` | 6 AM daily | Scan for new opportunities matching preferences |
| `weekly_review` | Sunday 8 PM | Generate weekly performance review |
| `habit_checker` | 8 PM daily | Check habit completion, send reminders |
| `missed_task_checker` | Midnight daily | Flag overdue tasks, increment missed count |
| `sleep_reminder` | 10:30 PM daily | Send wind-down message, log sleep readiness |

### 10.2 Scheduler Implementation

```python
# services/scheduler/main.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()

def setup_cron_jobs():
    scheduler.add_job(
        run_daily_briefing,
        trigger=CronTrigger(hour=7, minute=0),
        id="daily_briefing",
        replace_existing=True,
    )
    scheduler.add_job(
        run_radar,
        trigger=CronTrigger(hour=6, minute=0),
        id="opportunity_radar",
        replace_existing=True,
    )
    scheduler.add_job(
        run_weekly_review,
        trigger=CronTrigger(day_of_week="sunday", hour=20, minute=0),
        id="weekly_review",
        replace_existing=True,
    )
    scheduler.add_job(
        run_habit_checker,
        trigger=CronTrigger(hour=20, minute=0),
        id="habit_checker",
        replace_existing=True,
    )
    scheduler.add_job(
        run_missed_task_checker,
        trigger=CronTrigger(hour=0, minute=0),
        id="missed_task_checker",
        replace_existing=True,
    )
    scheduler.add_job(
        run_sleep_reminder,
        trigger=CronTrigger(hour=22, minute=30),
        id="sleep_reminder",
        replace_existing=True,
    )

if __name__ == "__main__":
    setup_cron_jobs()
    scheduler.start()
    asyncio.get_event_loop().run_forever()
```

### 10.3 Automation API Endpoints

The `automation.py` router provides manual trigger endpoints for testing:

```python
# apps/api/app/api/automation.py
@router.post("/trigger/briefing")
async def trigger_briefing(current_user=Depends(get_current_user)):
    """Manually trigger daily briefing generation."""
    await run_daily_briefing(user_id=current_user.user.id)
    return {"message": "Daily briefing triggered"}

@router.post("/trigger/radar")
async def trigger_radar(current_user=Depends(get_current_user)):
    """Manually trigger opportunity radar scan."""
    await run_radar(user_id=current_user.user.id)
    return {"message": "Opportunity radar triggered"}

@router.post("/trigger/weekly-review")
async def trigger_weekly_review(current_user=Depends(get_current_user)):
    """Manually trigger weekly review generation."""
    await run_weekly_review(user_id=current_user.user.id)
    return {"message": "Weekly review triggered"}
```

---

## 11. Database Access Layer

### 11.1 Supabase Python SDK

All database access uses the official Supabase Python SDK (`supabase-py` v2.x):

```python
# List
response = supabase.from_("tasks").select("*").eq("user_id", user_id).execute()

# Create
response = supabase.from_("tasks").insert(data).execute()

# Read single
response = supabase.from_("tasks").select("*").eq("id", task_id).eq("user_id", user_id).single().execute()

# Update
response = supabase.from_("tasks").update(update_data).eq("id", task_id).eq("user_id", user_id).execute()

# Delete
response = supabase.from_("tasks").delete().eq("id", task_id).eq("user_id", user_id).execute()
```

### 11.2 Query Patterns

| Pattern | Code | Use Case |
|---|---|---|
| List all | `.select("*").eq("user_id", user_id)` | GET / |
| List filtered | `.select("*").eq("status", "pending")` | Filtered views |
| Single by ID | `.select("*").eq("id", item_id).single()` | GET /{id} |
| Ordered | `.select("*").order("created_at", desc=True)` | Recent first |
| Count | `.select("*", count="exact")` | Dashboard stats |
| Text search | `.text_search("title", query)` | Search (future) |

### 11.3 N+1 Query Prevention

Currently, each module page makes a single query to fetch its data. For the dashboard (which aggregates from multiple tables):

```python
# Dashboard — multiple queries (acceptable for single-user app)
@router.get("/api/dashboard/summary")
async def dashboard_summary(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    user_id = current_user.user.id

    # Fire all queries concurrently
    tasks = supabase.from_("tasks").select("*", count="exact").eq("user_id", user_id).execute()
    goals = supabase.from_("goals").select("*", count="exact").eq("user_id", user_id).eq("status", "active").execute()
    habits = supabase.from_("habits").select("*", count="exact").eq("user_id", user_id).execute()
    courses = supabase.from_("courses").select("*", count="exact").eq("user_id", user_id).execute()

    return {
        "pending_tasks": len(tasks.data or []),
        "active_goals": len(goals.data or []),
        "active_habits": len(habits.data or []),
        "in_progress_courses": len([c for c in (courses.data or []) if c.get("status") == "in_progress"]),
    }
```

---

## 12. Logging

### 12.1 Structured JSON Logger

```python
# packages/shared/utils/logger.py
class Logger:
    """Structured JSON logger with correlation IDs."""

    def __init__(self, name: str = "second-brain-os"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter("%(message)s"))
            self.logger.addHandler(handler)

    def info(self, message: str, **kwargs):
        self._log("INFO", message, **kwargs)

    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        self._log("ERROR", message, error_message=str(error) if error else None, **kwargs)

    def _log(self, level: str, message: str, **kwargs):
        entry = {"timestamp": datetime.utcnow().isoformat(), "level": level, "message": message, **kwargs}
        self.logger.info(json.dumps(entry))

logger = Logger()
```

### 12.2 Log Output Format

```json
// Example log entries
{"timestamp": "2026-06-11T07:00:00.123Z", "level": "INFO", "message": "API Request", "endpoint": "/api/tasks", "method": "GET", "user_id": "usr_abc123"}
{"timestamp": "2026-06-11T07:00:00.456Z", "level": "INFO", "message": "API Response", "endpoint": "/api/tasks", "method": "GET", "status_code": 200, "duration_ms": 45.2}
{"timestamp": "2026-06-11T07:00:01.789Z", "level": "ERROR", "message": "API Error", "endpoint": "/api/tasks/xyz", "method": "GET", "error_type": "HTTPException", "error_message": "Task not found"}
```

### 12.3 Correlation ID

For request tracing across the stack:

```python
import uuid

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response
```

---

## 13. Testing Strategy

### 13.1 Testing Layers

| Layer | Tool | Scope | Coverage Target |
|---|---|---|---|
| Unit | pytest | Schemas, utilities, helpers | 90%+ |
| API | pytest + TestClient | Every endpoint, every status code | 85%+ |
| Integration | pytest + Supabase local | Cross-table flows | 70%+ |
| Prompt | pytest | Prompt frontmatter validation | 100% |

### 13.2 Running Tests

```bash
# All tests
pytest

# Single file
pytest tests/test_prompt_loader.py -v

# Single test with verbose output
pytest tests/test_prompt_loader.py::TestPromptLoader::test_loads_system_prompts -v

# Stop on first failure
pytest -xvs

# With coverage
pytest --cov=packages/ai --cov=apps/api
```

### 13.3 API Test Example

```python
# tests/test_tasks_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_tasks_requires_auth():
    response = client.get("/api/tasks/")
    assert response.status_code == 401  # No auth token

def test_create_task_invalid_title():
    # With valid auth token...
    response = client.post(
        "/api/tasks/",
        json={"title": ""},  # Invalid: min_length=1
        headers={"Authorization": f"Bearer {valid_token}"},
    )
    assert response.status_code == 422
    assert "title" in str(response.json()["detail"])
```

### 13.4 Current Test Suite (30 tests)

```bash
tests/
├── conftest.py                       # Adds packages/ to sys.path
├── test_prompt_loader.py              # 16 tests: PromptLoader, frontmatter, rendering
└── test_agent_prompts.py              # 14 tests: per-agent content, size, tags
```

---

## 14. API Documentation

### 14.1 Auto-Generated OpenAPI

FastAPI automatically generates OpenAPI 3.1 spec from route handlers and Pydantic models:

```python
app = FastAPI(
    title="Second Brain OS API",
    description="Personal AI productivity system for BTech CSE students",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc UI
    openapi_url="/openapi.json",  # Raw spec
)
```

### 14.2 Endpoint Documentation

Each endpoint is self-documenting via:
- Function docstrings (used in OpenAPI `description`)
- Type hints (used in OpenAPI `parameters`)
- Pydantic models (used in OpenAPI `requestBody` and `responses`)
- `response_model` (used in OpenAPI response schema)

```python
@router.get("/", response_model=List[TaskResponse])
async def get_tasks(current_user=Depends(get_current_user)):
    """
    Retrieve all tasks for the authenticated user.
    
    Returns an array of task objects sorted by creation date.
    Tasks are scoped to the authenticated user's ID.
    """
    supabase = get_supabase_client()
    response = (
        supabase.from_("tasks")
        .select("*")
        .eq("user_id", current_user.user.id)
        .execute()
    )
    return response.data
```

### 14.3 Available Documentation Endpoints

| URL | Description |
|---|---|
| `http://localhost:8000/docs` | Swagger UI (interactive) |
| `http://localhost:8000/redoc` | ReDoc (readable) |
| `http://localhost:8000/openapi.json` | Raw OpenAPI spec |

---

## 15. Performance Optimization

### 15.1 Connection Pooling

Supabase Python SDK manages connection pooling internally via `httpx`. Configuration:

```python
# packages/config/core/supabase.py
def get_supabase_client():
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = supabase.create_client(
            settings.supabase_url,
            settings.supabase_key,
            options={
                "http2": True,           # HTTP/2 multiplexing
                "timeout": 30,           # 30s request timeout
                "max_connections": 10,   # Connection pool size
            }
        )
    return _supabase_client
```

### 15.2 Query Optimization

| Optimization | Status | Impact |
|---|---|---|
| `SELECT *` only with needed fields | ✅ Implemented | Low |
| User ID filtering in WHERE clause | ✅ Implemented | High (indexed) |
| Indexed columns (id, user_id, status) | ✅ Supabase default | High |
| Text search with GIN indexes | 📋 Phase 2 | High |
| Pagination with `.range()` | 📋 Phase 2 | Medium |
| Aggregation queries with `.select(..., count="exact")` | ✅ Implemented | Medium |

### 15.3 N+1 Prevention

The N+1 query problem (querying a list, then querying details for each item) is currently avoided because:
1. Each module page lists items with all needed fields in a single query
2. Detail views fetch a single item by ID
3. Dashboard aggregates use multiple parallel queries (acceptable for single-user)

### 15.4 Caching

```python
# packages/shared/utils/cache.py
class TTLCache:
    """Simple in-memory TTL cache for frequently accessed data."""

    def __init__(self, default_ttl: int = 300):  # 5 minutes
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            value, expiry = self._cache[key]
            if time.time() < expiry:
                return value
            del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        self._cache[key] = (value, time.time() + (ttl or self._default_ttl))

    def invalidate(self, key: str):
        self._cache.pop(key, None)

# Cache singleton
response_cache = TTLCache(default_ttl=60)
```

---

## 16. Security Middleware

### 16.1 Security Headers

```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
```

### 16.2 Input Sanitization

```python
# packages/shared/utils/security.py
import re
import html

def sanitize_string(value: str) -> str:
    """Strip HTML tags and trim whitespace."""
    return html.escape(value.strip())

def sanitize_filename(filename: str) -> str:
    """Remove path traversal characters."""
    return re.sub(r'[^\w\-_\. ]', '', filename)

def validate_uuid(value: str) -> bool:
    """Validate UUID format."""
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, value, re.I))
```

### 16.3 Secrets Management

```python
# packages/config/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_service_key: str

    # Authentication
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # AI
    claude_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"
    use_local_ai: bool = True

    # Application
    app_name: str = "Second Brain OS"
    debug: bool = False
    cors_origins: str = "http://localhost:3000"

    # Email
    resend_api_key: Optional[str] = None

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
```

---

## 17. Graceful Shutdown

### 17.1 FastAPI Lifespan Events

```python
# main.py
import signal
import asyncio

@app.on_event("startup")
async def startup():
    """Initialize connections and services on startup."""
    logger.info("Second Brain OS API starting", version="1.0.0")
    # Warm up Supabase client
    get_supabase_client()
    # Warm up PromptLoader cache
    from ai.prompt_loader import prompts
    _ = prompts.list_prompts()

@app.on_event("shutdown")
async def shutdown():
    """Gracefully close connections and stop background tasks."""
    logger.info("Second Brain OS API shutting down")
    # Close Supabase client
    # Cancel background tasks
    # Flush logs
```

### 17.2 Signal Handling (Production)

```python
# For Railway/production deployments
import os

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=settings.debug,
        log_level="info",
        timeout_graceful_shutdown=30,  # 30s for in-flight requests
    )
```

---

## 18. Architecture Diagrams

### 18.1 Full System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLIENT (Next.js 14)                              │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  Browser → Edge Middleware (auth check) → App Router → Module    │  │
│  │  Pages → Zustand Stores → Supabase SDK / fetch()                 │  │
│  └──────────────────────────┬────────────────────────────────────────┘  │
│                             │ HTTP / WebSocket                           │
└─────────────────────────────┼───────────────────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────────────────┐
│                    BACKEND (FastAPI)                                    │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                     API Layer (13 routers)                       │  │
│  │  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐  │  │
│  │  │ Tasks │ │Courses│ │ Goals  │ │Habits │ │ Sleep │ │Income │  │  │
│  │  │ 6 eps │ │ 5 eps │ │ 5 eps  │ │ 4 eps │ │ 3 eps │ │ 4 eps │  │  │
│  │  └───────┘ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘  │  │
│  │  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐  │  │
│  │  │Proj   │ │ Ideas │ │Resrce │ │Opportun│ │ Time  │ │ Chat  │  │  │
│  │  │ 4 eps │ │ 4 eps │ │ 4 eps │ │ 4 eps  │ │ 6 eps │ │ 1 ep  │  │  │
│  │  └───────┘ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘  │  │
│  │  ┌──────────────────────────────────────────────────────────────┐ │  │
│  │  │ Automation: 3 eps (trigger briefing, radar, review)          │ │  │
│  │  └──────────────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────┬───────────────────────────────────────┘  │
│                             │                                          │
│  ┌──────────────────────────┴───────────────────────────────────────┐  │
│  │                   Middleware Stack                                │  │
│  │  RateLimiter → CORS → Request Logging → Global Exception Handler │  │
│  └──────────────────────────┬───────────────────────────────────────┘  │
│                             │                                          │
│  ┌──────────────────────────┴───────────────────────────────────────┐  │
│  │                  Dependency Injection Layer                       │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌───────────────────┐  │  │
│  │  │ get_current_user│  │ get_supabase  │  │ Pydantic Models   │  │  │
│  │  │ (JWT validation)│  │ _client       │  │ (request/response)│  │  │
│  │  └────────────────┘  └────────────────┘  └───────────────────┘  │  │
│  └──────────────────────────┬───────────────────────────────────────┘  │
│                             │                                          │
│  ┌──────────────────────────┴───────────────────────────────────────┐  │
│  │                   Database Layer (Supabase SDK)                   │  │
│  │  PostgreSQL 15 + RLS + Realtime Subscriptions                    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    AI Layer                                       │  │
│  │  ┌─────────────────────┐      ┌─────────────────────┐           │  │
│  │  │  Ollama (Local)     │      │  Claude API (Cloud) │           │  │
│  │  │  Mistral 7B /       │──────│  Sonnet 4           │           │  │
│  │  │  Llama 3.1          │      │  (fallback)         │           │  │
│  │  └─────────┬───────────┘      └─────────────────────┘           │  │
│  │            │                                                     │  │
│  │  ┌─────────┴──────────────────────────────────────────────────┐ │  │
│  │  │  PromptLoader → prompts/ directory (YAML frontmatter)     │ │  │
│  │  └────────────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────────────────┐
│                  SCHEDULER (APScheduler - separate service)             │
│                                                                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │ Daily        │ │ Opportunity  │ │ Weekly       │ │ Habit        │  │
│  │ Briefing     │ │ Radar        │ │ Review       │ │ Checker      │  │
│  │ 7 AM         │ │ 6 AM         │ │ Sun 8 PM     │ │ 8 PM         │  │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘  │
│  ┌──────────────┐ ┌──────────────┐                                     │
│  │ Missed Task  │ │ Sleep        │                                     │
│  │ Checker      │ │ Reminder     │                                     │
│  │ Midnight     │ │ 10:30 PM     │                                     │
│  └──────────────┘ └──────────────┘                                     │
└─────────────────────────────────────────────────────────────────────────┘
```

### 18.2 Request Lifecycle

```
Request
  │
  ▼
Edge Middleware (Next.js)
  │ Auth check → redirect if unauthorized
  │ Security headers
  ▼
FastAPI Route Match
  │ /api/tasks → tasks.router
  │
  ▼
Rate Limiter Middleware
  │ Per-IP sliding window check
  │ 429 if exceeded
  ▼
CORS Middleware
  │ Origin whitelist check
  │
  ▼
Request Logging
  │ Structured JSON log
  │
  ▼
Dependency Injection
  │ Depends(get_current_user) → JWT decode → Supabase auth check
  │ Depends(get_supabase_client) → Cached client
  │ Body validation → Pydantic model parse
  │
  ▼
Endpoint Handler
  │ Business logic → Supabase query → Transform → Return
  │
  ▼
Response
  │ Pydantic serialization (response_model)
  │ Security headers
  │ Correlation ID
  │
  ▼
Client
```

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-11 | Developer | Initial backend architecture documentation |
