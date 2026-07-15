# Data Flow Diagrams — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ENG-DFD-001 |
| **Version** | 1.0.0 |
| **Status** | Active |
| **Date** | 2026-07-11 |
| **Classification** | Internal |
| **Owner** | Developer |

---

## Table of Contents

1. [Flow 1: User Authentication (Google OAuth)](#flow-1-user-authentication-google-oauth)
2. [Flow 2: Daily Briefing Generation (AI Agent)](#flow-2-daily-briefing-generation-ai-agent)
3. [Flow 3: Chat with ARIA (Real-Time Interaction)](#flow-3-chat-with-aria-real-time-interaction)
4. [Flow 4: Task Lifecycle (CRUD + Completion)](#flow-4-task-lifecycle-crud--completion)
5. [Flow 5: AI Circuit Breaker (Resilience Pattern)](#flow-5-ai-circuit-breaker-resilience-pattern)
6. [Flow 6: Scheduled Cron Job Execution](#flow-6-scheduled-cron-job-execution)
7. [Flow 7: API Request Lifecycle (Request → Response)](#flow-7-api-request-lifecycle-request--response)

---

## Flow 1: User Authentication (Google OAuth)

```mermaid
sequenceDiagram
    participant User as User (Browser)
    participant Frontend as Next.js Frontend
    participant Supabase as Supabase Auth
    participant Google as Google OAuth
    participant API as FastAPI Backend

    User->>Frontend: Click "Login with Google"
    Frontend->>Supabase: signInWithOAuth({ provider: "google" })
    Supabase->>Google: Redirect to Google OAuth endpoint
    Google->>User: Display consent screen
    User->>Google: Approve & grant permissions
    Google->>Supabase: Authorization code
    Supabase->>Supabase: Exchange code for tokens
    Supabase-->>Frontend: JWT + refresh token (URL fragment)
    Frontend->>Supabase: getSession() → retrieve tokens
    Frontend->>API: Attach JWT in Authorization header
    API->>Supabase: Verify JWT via get_current_user()
    Supabase-->>API: User identity (user_id, email, role)
    API-->>Frontend: 200 OK + user profile
    Frontend->>User: Redirect to dashboard
```

**Key Components:**
- `supabase.auth.signInWithOAuth()` — initiates OAuth flow (`apps/web/lib/supabase.ts`)
- `get_current_user()` — JWT validation with caching (`packages/config/core/auth.py:32`)
- `config.core.supabase` — Supabase client singleton (`packages/config/core/supabase.py`)
- API key auth for machine-to-machine: `config.core.api_key_auth`

---

## Flow 2: Daily Briefing Generation (AI Agent)

```mermaid
sequenceDiagram
    participant Scheduler as APScheduler (Cron)
    participant BriefingAgent as BriefingAgent (agents/briefing_agent.py)
    participant Supabase as Supabase (PostgreSQL)
    participant PromptLoader as PromptLoader (prompt_loader.py)
    participant LLM as LLMClient (ollama/claude)
    participant Cache as In-Memory Cache

    Scheduler->>BriefingAgent: Fire trigger at 7 AM (configurable)
    BriefingAgent->>Supabase: Query tasks (pending + overdue)
    BriefingAgent->>Supabase: Query habits (last 7 days)
    BriefingAgent->>Supabase: Query sleep_logs (last night)
    BriefingAgent->>Supabase: Query goals (active + milestones)
    Supabase-->>BriefingAgent: Aggregated user data
    BriefingAgent->>PromptLoader: get_agent("briefing_agent")
    PromptLoader-->>BriefingAgent: PromptEntry(frontmatter, body)
    BriefingAgent->>Cache: Check for cached LLM response
    Cache-->>BriefingAgent: Cache miss
    BriefingAgent->>LLM: generate_json(user_context, system_prompt)
    LLM->>LLM: Check circuit breaker state
    alt Circuit CLOSED
        LLM->>Ollama: POST /api/generate (model=mistral:7b)
        Ollama-->>LLM: Structured briefing JSON
    else Circuit OPEN → fallback
        LLM->>Claude: messages.create(api_key, claude-3-haiku)
        Claude-->>LLM: Structured briefing JSON
    end
    LLM-->>BriefingAgent: BriefingResponse(title, summary, sections, action_items)
    BriefingAgent->>Supabase: INSERT INTO daily_briefings (user_id, date, content)
    Supabase-->>BriefingAgent: Confirmation
    BriefingAgent->>Supabase: PUSH notification to user
    BriefingAgent-->>Scheduler: Success status
```

**Key Components:**
- `BriefingAgent` — `packages/ai/agents/briefing_agent.py` (A09)
- `PromptLoader` — `packages/ai/prompt_loader.py` (loads `prompts/agents/briefing_agent.md`)
- `LLMClient` — `packages/ai/client.py` with retry + circuit breaker
- **Fallback:** algorithmic results if LLM unavailable (`briefing_agent.py:algorithmic_fallback()`)
- Cron config: `services/scheduler/main.py`

---

## Flow 3: Chat with ARIA (Real-Time Interaction)

```mermaid
sequenceDiagram
    participant User as User (Browser)
    participant Frontend as Next.js Chat UI
    participant API as FastAPI /api/v1/chat
    participant Auth as get_current_user()
    participant Orchestrator as ARIA Orchestrator
    participant Agent as Sub-Agent (task/memory/learning)
    participant Supabase as Supabase DB
    participant PromptLoader as PromptLoader
    participant LLM as LLMClient

    User->>Frontend: Type message + press Enter
    Frontend->>Frontend: Optimistic UI update
    Frontend->>API: POST /api/v1/chat (Authorization: Bearer JWT)
    API->>Auth: Validate JWT + extract user_id
    Auth-->>API: User identity
    API->>Orchestrator: dispatch(user_id, message, history)
    Orchestrator->>Supabase: Fetch chat history (last 10 messages)
    Supabase-->>Orchestrator: Conversation context
    Orchestrator->>Supabase: Fetch memory (user preferences, patterns)
    Supabase-->>Orchestrator: Memory entries
    Orchestrator->>Orchestrator: Intent classification (context, routing)
    Orchestrator->>Agent: Dispatch to relevant sub-agent
    Agent->>Supabase: Fetch domain-specific data (tasks, habits, etc.)
    Supabase-->>Agent: Domain context
    Agent->>PromptLoader: get_agent("<agent_name>")
    PromptLoader-->>Agent: PromptEntry with frontmatter
    Agent->>LLM: generate(user_context, system_prompt)
    LLM->>LLM: Retry up to 3× with exponential backoff (2s, 4s, 8s)
    alt Ollama available
        LLM->>Ollama: Generate response
        Ollama-->>LLM: Response tokens
    else Claude fallback
        LLM->>Claude: Generate response
        Claude-->>LLM: Response tokens
    end
    LLM-->>Agent: Generated response
    Agent-->>Orchestrator: Structured response
    Orchestrator->>Supabase: Store message in chat_messages
    Orchestrator-->>API: Synthesized response
    API-->>Frontend: SSE stream (token by token)
    Frontend->>User: Render streaming response in chat UI
```

**Key Components:**
- `apps/api/app/api/chat.py` — SSE streaming endpoint
- ARIA Orchestrator — `packages/ai/orchestrator.py` (intent classification + dispatch)
- Sub-agents: `memory_agent.py`, `task_agent.py`, `learning_agent.py`, etc.
- `packages/database/schemas/orchestrator.py` — request/response schemas

---

## Flow 4: Task Lifecycle (CRUD + Completion)

```mermaid
stateDiagram-v2
    [*] --> Pending: Create task (POST /api/v1/tasks)
    Pending --> In_Progress: Start task (PUT status=in_progress)
    Pending --> Completed: Quick complete (POST /api/v1/tasks/{id}/complete)
    Pending --> Cancelled: Cancel (PUT status=cancelled)
    In_Progress --> Completed: Mark done (POST /api/v1/tasks/{id}/complete)
    In_Progress --> Blocked: Add dependency conflict
    In_Progress --> Pending: Reset to pending
    Blocked --> In_Progress: Unblock (resolve dependency)
    Blocked --> Cancelled: Cancel while blocked
    Completed --> [*]: Archive (auto after 30 days)
    Cancelled --> [*]: Archive

    note right of Pending: Default status on creation\npriority: low/medium/high/critical
    note right of Completed: Triggers habit streak check\nTriggers weekly review data
```

**Sequence for Task Creation:**

```mermaid
sequenceDiagram
    participant User as User
    participant Frontend as Next.js
    participant API as /api/v1/tasks
    participant Supabase as Supabase
    participant AI as TaskAgent (optional)

    User->>Frontend: Fill task form + Submit
    Frontend->>Frontend: Validate with Zod schema
    Frontend->>API: POST /api/v1/tasks (title, priority, due_date, project_id?)
    API->>Supabase: INSERT INTO tasks (user_id, title, ...)
    Supabase-->>API: Created task row
    API-->>Frontend: 201 Created + TaskResponse
    Frontend->>User: Show success toast + optimistic update

    opt AI breakdown (optional)
        API->>AI: task_agent.breakdown(task_id)
        AI->>Supabase: Read task
        AI-->>API: Subtasks, estimated duration, tags
        API->>Supabase: UPDATE tasks (ai_metadata)
    end
```

**Key Components:**
- `apps/api/app/api/tasks.py` — 6 endpoints (GET, POST, GET/{id}, PUT/{id}, DELETE/{id}, POST/{id}/complete)
- `packages/database/schemas/task.py` — TaskCreate, TaskUpdate, TaskResponse Pydantic models
- State machine enforced at API layer with status validation
- AI breakdown via `packages/ai/agents/task_agent.py` (A01)

---

## Flow 5: AI Circuit Breaker (Resilience Pattern)

```mermaid
sequenceDiagram
    participant Client as Agent / Route Handler
    participant LLMClient as LLMClient (client.py)
    participant CircuitBreaker as CircuitBreaker (retry.py)
    participant Ollama as Ollama (Local Mistral 7B)
    participant Claude as Claude API (Fallback)
    participant Logger as Structured Logger

    Client->>LLMClient: generate() or generate_json()
    LLMClient->>CircuitBreaker: check_state()
    alt Circuit is CLOSED (normal operation)
        CircuitBreaker-->>LLMClient: State: CLOSED
        LLMClient->>Ollama: Attempt 1 — POST /api/generate
        alt Ollama succeeds
            Ollama-->>LLMClient: Response
            LLMClient->>CircuitBreaker: record_success()
            LLMClient-->>Client: Parsed response
        else Ollama fails (timeout / connection error)
            Logger->>Logger: WARN "Ollama attempt 1 failed"
            LLMClient->>Ollama: Attempt 2 — retry after 2s backoff
            alt Retry succeeds
                Ollama-->>LLMClient: Response
                LLMClient->>CircuitBreaker: record_success()
                LLMClient-->>Client: Parsed response
            else Retry fails — timeout
                Logger->>Logger: WARN "Ollama attempt 2 failed"
                LLMClient->>Ollama: Attempt 3 — retry after 4s backoff
                alt Third attempt succeeds
                    Ollama-->>LLMClient: Response
                    LLMClient->>CircuitBreaker: record_success()
                    LLMClient-->>Client: Parsed response
                else All 3 retries exhausted
                    Logger->>Logger: ERROR "Ollama unavailable after 3 retries"
                    LLMClient->>CircuitBreaker: record_failure()
                    alt Claude API is configured
                        LLMClient->>Claude: Fallback — messages.create()
                        Claude-->>LLMClient: Response
                        LLMClient-->>Client: Response (from fallback)
                    else No fallback configured
                        LLMClient-->>Client: Raise LLMProviderUnavailableError
                        Client->>Client: Execute algorithmic fallback
                    end
                end
            end
        end
    else Circuit is OPEN (cooldown mode)
        CircuitBreaker-->>LLMClient: State: OPEN (remaining 42s cooldown)
        LLMClient-->>Client: Raise CircuitBreakerOpenError
        Client->>Client: Execute algorithmic_fallback()
        Client-->>Client: Return default/calculated result
    else Circuit is HALF_OPEN (probing)
        CircuitBreaker-->>LLMClient: State: HALF_OPEN
        LLMClient->>Ollama: Probe request (single attempt)
        alt Probe succeeds
            Ollama-->>LLMClient: Response
            LLMClient->>CircuitBreaker: record_success() → CLOSED
            LLMClient-->>Client: Response
        else Probe fails
            LLMClient->>CircuitBreaker: record_failure() → OPEN
            LLMClient-->>Client: Raise CircuitBreakerOpenError
        end
    end
```

**Key Components:**
- `LLMClient` — `packages/ai/client.py` (534 lines)
- `CircuitBreaker` — `packages/shared/utils/retry.py:114` (failure_threshold=5, recovery_timeout=60s)
- Fallback chain: Ollama → Claude → algorithmic_fallback()
- Retry policy: 3 attempts, exponential backoff (2s, 4s, 8s)
- All agents implement `algorithmic_fallback()` as last resort

---

## Flow 6: Scheduled Cron Job Execution

```mermaid
sequenceDiagram
    participant APScheduler as APScheduler (services/scheduler/main.py)
    participant Job as Cron Job Module (15 jobs)
    participant API as FastAPI (internal HTTP call)
    participant AI as AI Agent Module
    participant Supabase as Supabase DB
    participant Logger as Structured Logger

    APScheduler->>APScheduler: Initialize AsyncIOScheduler
    APScheduler->>APScheduler: Register 15 cron jobs from config

    CriticalSection-->>APScheduler: ⏰ 6:00 AM Daily
    APScheduler->>Job: opportunity_radar_job()
    Job->>API: GET /api/v1/opportunities (internal)
    API->>AI: opportunity_agent.scan(user_id)
    AI-->>API: Matched opportunities
    API-->>Job: Store results
    Job->>Logger: INFO "Opportunity radar complete"

    CriticalSection-->>APScheduler: ⏰ 7:00 AM Daily
    APScheduler->>Job: daily_briefing_job()
    Job->>API: POST /api/v1/automation/trigger/briefing
    API->>AI: briefing_agent.generate(user_id)
    AI->>Supabase: Query user data
    AI-->>API: Generated briefing
    API-->>Job: Briefing stored + notification sent

    CriticalSection-->>APScheduler: ⏰ 9:30 PM Daily
    APScheduler->>Job: sleep_bedtime_job()
    Job->>API: POST /api/v1/automation/sleep-bedtime
    API->>AI: sleep_agent.wind_down(user_id)
    AI-->>API: Wind-down message
    API-->>Job: Notification pushed

    CriticalSection-->>APScheduler: ⏰ 6:00 PM Daily
    APScheduler->>Job: course_nudge_job()
    Job->>API: POST /api/v1/automation/nudges
    API->>AI: nudge_agent.check_courses(user_id)
    AI-->>API: Nudge recommendations
    API-->>Job: Notifications sent

    CriticalSection-->>APScheduler: ⏰ Every 15 min
    APScheduler->>Job: missed_task_checker_job()
    Job->>API: Check overdue tasks
    API-->>Job: Overdue list
    Job->>Logger: INFO "Missed tasks checked"

    Note over APScheduler,Logger: All failures logged with ERROR level\nRecurring failures trigger alert after 3 consecutive errors
```

**Cron Job Registry (`services/scheduler/main.py`):**

| Job ID | Module | Schedule | Agent | Status |
|---|---|---|---|---|
| A06 | `opportunity_radar_job` | Daily 6 AM | opportunity_agent | Live |
| A09 | `daily_briefing_job` | Daily 7 AM | briefing_agent | Live |
| A13 | `sleep_bedtime_job` | Daily 9:30 PM | sleep_agent | Live |
| A14 | `course_nudge_job` | Daily 6 PM | nudge_agent | Live |
| A10 | `weekly_review_job` | Sunday 8 PM | weekly_review_agent | Live |
| A11 | `missed_task_checker_job` | Every 15 min | None (algorithmic) | Live |
| A12 | `habit_miss_checker_job` | Midnight | None (algorithmic) | Live |

---

## Flow 7: API Request Lifecycle (Request → Response)

```mermaid
sequenceDiagram
    participant Client as Client (Browser / Mobile)
    participant LB as Vercel/Railway Edge
    participant Middleware as FastAPI Middleware Stack
    participant Router as Router Handler
    participant Auth as get_current_user()
    participant Supabase as Supabase DB
    participant Logger as Logger

    Client->>LB: HTTPS request
    LB->>Middleware: Pass to FastAPI

    Middleware->>Middleware: 1. Request ID Generation (uuid4 → X-Request-ID header)
    Middleware->>Middleware: 2. CORS Check (allowed_origins match?)
    Middleware->>Middleware: 3. GZip Decompression (if Content-Encoding: gzip)
    Middleware->>Middleware: 4. Rate Limiter Check (sliding window per IP)
    alt Rate limited
        Middleware-->>Client: 429 Too Many Requests + Retry-After header
    end
    Middleware->>Middleware: 5. CSRF Token Validation (for mutation methods)
    alt CSRF invalid
        Middleware-->>Client: 403 Forbidden + CSRF error code
    end
    Middleware->>Middleware: 6. Input Sanitization (strip XSS vectors)
    Middleware->>Middleware: 7. Audit Middleware (log mutation requests)
    Middleware->>Middleware: log_request() → structured JSON log

    Middleware->>Router: Route to matching endpoint
    Router->>Auth: Depends(get_current_user()) → validate JWT
    alt Invalid/expired token
        Auth-->>Router: 401 Unauthorized
        Router-->>Middleware: 401 response
        Middleware-->>Client: 401 + WWW-Authenticate header
    end
    Auth-->>Router: user_id (validated)

    Router->>Supabase: Database operation (select/insert/update/delete)
    Supabase->>Supabase: RLS policy check (auth.uid() = user_id)
    alt RLS violation
        Supabase-->>Router: Empty set / permission denied
        Router-->>Middleware: 403 / 404 response
    end
    Supabase-->>Router: Query result

    Router-->>Middleware: 200/201/204 response
    Middleware->>Middleware: 8. log_response() → duration, status, request_id
    Middleware->>Middleware: 9. Response Cache Store (if cacheable GET)
    Middleware-->>Client: Final HTTP response
```

**Middleware Stack (in order, defined in `apps/api/main.py`):**

| Order | Middleware | File | Config |
|---|---|---|---|
| 1 | Request ID | inline in `main.py` | UUID v4 per request |
| 2 | CORS | `CORSMiddleware` | `settings.cors_origins` |
| 3 | GZip | `GZipMiddleware` | minimum_size=1000 |
| 4 | Rate Limiter | `packages/shared/utils/rate_limiter.py` | 100 req/min default |
| 5 | CSRF | `packages/shared/utils/csrf.py` | Token validation on mutations |
| 6 | Sanitizer | `packages/shared/utils/sanitizer.py` | XSS strip on input |
| 7 | Audit | `packages/shared/utils/audit.py` | Mutation request logging |
| 8 | Cache | `packages/shared/utils/cache_middleware.py` | TTL=300s for GET |
| 9 | Logging | `packages/shared/utils/logger.py` | Structured JSON + Sentry |

---

## Data Flow Principles

1. **All external requests enter through API** — Frontend never queries Supabase directly in production for writes
2. **Every DB query is tenant-isolated** — Filtered by `user_id` at application layer + RLS at database layer
3. **AI calls are resilient** — Circuit breaker → retry → provider failover → algorithmic fallback
4. **All state changes are audited** — Mutations logged via audit middleware
5. **Authentication is validated at middleware level** — Every protected endpoint uses `Depends(get_current_user())`
6. **Prompts are loaded from files, not code** — `PromptLoader` singleton caches all 22 prompt files at import time

---

## Related Documents

| Document | Purpose |
|---|---|
| [AGENTS.md](../../AGENTS.md) | Master project reference — Section 6 (Project Structure), Section 9 (AI Agent Architecture) |
| [API Documentation](../engineering/17_API.md) | API endpoint reference for all 31 routers |
| [Database Schema](../engineering/15_Database.md) | All tables, columns, relationships, RLS policies |
| [Error Catalog](../engineering/api/error-catalog.md) | Standardized error codes and recovery strategies |
| [Event Architecture](../engineering/18_Events.md) | Event-driven patterns and webhook system |
| [Architecture Decisions](../engineering/adr/) | ADR-004 (In-process agents), ADR-005 (API versioning) |
