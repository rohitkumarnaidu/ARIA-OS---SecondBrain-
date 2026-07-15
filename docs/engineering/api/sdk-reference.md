# SDK Reference

## Document Control

| Field | Value |
|---|---|
| Document ID | ENG-SDK-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-07-14 |
| Classification | Internal |
| Owner | Developer |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Overview of ARIA OS API SDK](#2-overview-of-aria-os-api-sdk)
3. [Python SDK](#3-python-sdk)
4. [TypeScript SDK](#4-typescript-sdk)
5. [Authentication](#5-authentication)
6. [Core Client Class](#6-core-client-class)
7. [Module Reference](#7-module-reference)
8. [Error Handling](#8-error-handling)
9. [Rate Limiting Awareness](#9-rate-limiting-awareness)
10. [Pagination Handling](#10-pagination-handling)
11. [WebSocket and Realtime Subscriptions](#11-websocket-and-realtime-subscriptions)
12. [Error Code Reference](#12-error-code-reference)
13. [Testing with the SDK](#13-testing-with-the-sdk)
14. [Related Documents](#14-related-documents)

---

## 1. Executive Summary

The ARIA OS SDK provides programmatic access to all 31 API routers through idiomatic Python and TypeScript clients. It abstracts authentication, pagination, error handling, rate limiting, and realtime subscriptions behind a clean client interface. The SDK is the recommended way to build integrations, scripts, and automation on top of ARIA OS.

---

## 2. Overview of ARIA OS API SDK

### 2.1 SDK Architecture

```mermaid
graph TB
    subgraph SDK["ARIA OS SDK"]
        AUTH["Auth Layer<br/>JWT + API Key"]
        CLIENT["Base Client<br/>HTTP + Realtime"]
        MODULES["Module Clients"]
        ERRORS["Error Handler<br/>Retry + Rate Limit"]
    end

    subgraph API["ARIA OS API"]
        R1["/api/v1/tasks"]
        R2["/api/v1/courses"]
        R3["/api/v1/goals"]
        R4["/api/v1/habits"]
        R5["/api/v1/chat"]
        R6["/api/v1/automation"]
        RN["... 25 more routers"]
    end

    SDK -->|HTTP Requests| API
    API -->|JSON Responses| SDK

    MODULES --> CLIENT
    CLIENT --> AUTH
    CLIENT --> ERRORS
```

### 2.2 Available Packages

| Language | Package Location | Installation |
|---|---|---|
| Python | `packages/sdk/` | `pip install -e packages/sdk` or copy `packages/sdk/` |
| TypeScript | `packages/sdk-ts/` | `npm install @aria-os/sdk` or local path dependency |

### 2.3 Supported Features

| Feature | Python SDK | TypeScript SDK |
|---|---|---|
| All 31 API modules | Yes | Yes |
| JWT authentication | Yes | Yes |
| API key authentication | Yes | Yes |
| Pagination helpers | Yes | Yes |
| Rate limit awareness | Yes | Yes |
| Retry with backoff | Yes | Yes |
| Realtime subscriptions | Via Supabase client | Via Supabase client |
| Request ID tracing | Yes | Yes |
| Token usage tracking | Yes | Yes |
| Streaming (chat) | Yes | Yes |

---

## 3. Python SDK

### 3.1 Installation

```bash
# From the monorepo root
pip install -e packages/sdk

# Or copy the SDK module directly
cp -r packages/sdk/aria_os_sdk /your/project/
```

### 3.2 Requirements

```
httpx>=0.27.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

### 3.3 Quick Start

```python
import os
from aria_os_sdk import AriaOSClient

# Initialize with JWT token
client = AriaOSClient(
    base_url="http://localhost:8000",
    auth_token=os.getenv("ARIA_OS_TOKEN"),
)

# List tasks
tasks = client.tasks.list(limit=10, offset=0)
print(tasks["data"])

# Create a task
task = client.tasks.create({
    "title": "Complete SDK documentation",
    "priority": "high",
    "due_date": "2026-07-20T00:00:00Z",
})
print(f"Created task: {task['id']}")

# Get a specific task
task = client.tasks.get(task_id="some-uuid-here")
print(task["title"])

# Update a task
updated = client.tasks.update(
    task_id="some-uuid-here",
    data={"status": "completed"},
)

# Delete a task
client.tasks.delete(task_id="some-uuid-here")
```

---

## 4. TypeScript SDK

### 4.1 Installation

```bash
# From the monorepo root
npm install ./packages/sdk-ts

# Or install from npm registry
npm install @aria-os/sdk
```

### 4.2 Requirements

```json
{
  "dependencies": {
    "@aria-os/sdk": "^1.0.0"
  },
  "peerDependencies": {
    "@supabase/supabase-js": "^2.39.0"
  }
}
```

### 4.3 Quick Start

```typescript
import { AriaOSClient } from '@aria-os/sdk'

const client = new AriaOSClient({
  baseUrl: 'http://localhost:8000',
  authToken: process.env.ARIA_OS_TOKEN!,
})

// List tasks
const tasks = await client.tasks.list({ limit: 10, offset: 0 })
console.log(tasks.data)

// Create a task
const task = await client.tasks.create({
  title: 'Complete SDK documentation',
  priority: 'high',
  dueDate: '2026-07-20T00:00:00Z',
})
console.log(`Created task: ${task.id}`)

// Get a specific task
const fetched = await client.tasks.get('some-uuid-here')
console.log(fetched.title)

// Update a task
const updated = await client.tasks.update('some-uuid-here', {
  status: 'completed',
})

// Delete a task
await client.tasks.delete('some-uuid-here')
```

---

## 5. Authentication

### 5.1 JWT Token Auth (Default)

All endpoints except `/health` require Bearer JWT authentication. Obtain a token by signing in through Supabase Auth (Google OAuth or email/password).

```python
from aria_os_sdk import AriaOSClient

# With JWT token
client = AriaOSClient(
    base_url="http://localhost:8000",
    auth_token="eyJhbGciOiJIUzI1NiIs...",  # Your Supabase access token
)

# The SDK automatically sends:
# Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

```typescript
import { AriaOSClient } from '@aria-os/sdk'

const client = new AriaOSClient({
  baseUrl: 'http://localhost:8000',
  authToken: 'eyJhbGciOiJIUzI1NiIs...',
})
```

### 5.2 API Key Auth (Machine-to-Machine)

For server-to-server integrations, use API key authentication:

```python
# With API key
client = AriaOSClient(
    base_url="http://localhost:8000",
    api_key="aria_sk_abc123...",
)

# The SDK automatically sends:
# Authorization: Bearer <api_key>
```

```typescript
const client = new AriaOSClient({
  baseUrl: 'http://localhost:8000',
  apiKey: 'aria_sk_abc123...',
})
```

### 5.3 Token Refresh

The Python SDK supports automatic token refresh if a refresh token callback is provided:

```python
import jwt
from aria_os_sdk import AriaOSClient

async def refresh_token():
    """Fetch a new access token using your refresh token."""
    # Call your auth provider's refresh endpoint
    async with httpx.AsyncClient() as http:
        resp = await http.post(
            "https://your-project.supabase.co/auth/v1/token?grant_type=refresh_token",
            json={"refresh_token": stored_refresh_token},
        )
        data = resp.json()
        return data["access_token"]

client = AriaOSClient(
    base_url="http://localhost:8000",
    auth_token=current_token,
    refresh_callback=refresh_token,  # Called on 401 responses automatically
)
```

---

## 6. Core Client Class

### 6.1 Constructor

#### Python

```python
class AriaOSClient:
    def __init__(
        self,
        base_url: str,
        auth_token: Optional[str] = None,
        api_key: Optional[str] = None,
        refresh_callback: Optional[Callable[[], Awaitable[str]]] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        enable_request_logging: bool = False,
    ):
        ...
```

#### TypeScript

```typescript
interface AriaOSClientOptions {
  baseUrl: string
  authToken?: string
  apiKey?: string
  refreshCallback?: () => Promise<string>
  timeout?: number       // default: 30000 (30s)
  maxRetries?: number    // default: 3
  enableLogging?: boolean
}

class AriaOSClient {
  constructor(options: AriaOSClientOptions)
}
```

### 6.2 Client Properties

| Property | Type | Python | TypeScript |
|---|---|---|---|
| `tasks` | ModuleClient | `client.tasks` | `client.tasks` |
| `courses` | ModuleClient | `client.courses` | `client.courses` |
| `goals` | ModuleClient | `client.goals` | `client.goals` |
| `habits` | ModuleClient | `client.habits` | `client.habits` |
| `sleep` | ModuleClient | `client.sleep` | `client.sleep` |
| `income` | ModuleClient | `client.income` | `client.income` |
| `projects` | ModuleClient | `client.projects` | `client.projects` |
| `ideas` | ModuleClient | `client.ideas` | `client.ideas` |
| `resources` | ModuleClient | `client.resources` | `client.resources` |
| `opportunities` | ModuleClient | `client.opportunities` | `client.opportunities` |
| `time` | ModuleClient | `client.time_entries` | `client.timeEntries` |
| `chat` | ChatClient | `client.chat` | `client.chat` |
| `briefings` | ModuleClient | `client.briefings` | `client.briefings` |
| `reviews` | ModuleClient | `client.reviews` | `client.reviews` |
| `memory` | ModuleClient | `client.memory` | `client.memory` |
| `roadmap` | ModuleClient | `client.roadmap` | `client.roadmap` |
| `academics` | ModuleClient | `client.academics` | `client.academics` |
| `videos` | ModuleClient | `client.videos` | `client.videos` |
| `analytics` | StatsClient | `client.analytics` | `client.analytics` |
| `predictions` | StatsClient | `client.predictions` | `client.predictions` |
| `notifications` | ModuleClient | `client.notifications` | `client.notifications` |
| `nlp` | ModuleClient | `client.nlp` | `client.nlp` |
| `prompts` | ModuleClient | `client.prompts` | `client.prompts` |
| `feedback` | ModuleClient | `client.feedback` | `client.feedback` |
| `monitoring` | ModuleClient | `client.monitoring` | `client.monitoring` |
| `automation` | ModuleClient | `client.automation` | `client.automation` |
| `auth` | ModuleClient | `client.auth` | `client.auth` |
| `featureFlags` | ModuleClient | `client.feature_flags` | `client.featureFlags` |
| `dataExport` | ModuleClient | `client.data_export` | `client.dataExport` |

### 6.3 Generic ModuleClient Methods

Every CRUD module client exposes these methods:

| Method | HTTP | Path | Description |
|---|---|---|---|
| `.list(params?)` | GET | `/` | List items with pagination and filters |
| `.create(data)` | POST | `/` | Create a new item |
| `.get(id)` | GET | `/{id}` | Get a single item by ID |
| `.update(id, data)` | PUT | `/{id}` | Update an existing item |
| `.delete(id)` | DELETE | `/{id}` | Delete an item |

```python
# All CRUD methods return typed dictionaries matching the API response schema
tasks = await client.tasks.list(limit=10, offset=0)
task = await client.tasks.get("uuid-here")
created = await client.tasks.create({"title": "New Task"})
updated = await client.tasks.update("uuid-here", {"status": "completed"})
await client.tasks.delete("uuid-here")
```

### 6.4 Request Configuration

Every method accepts an optional `RequestConfig` for fine-grained control:

```python
from aria_os_sdk import RequestConfig

config = RequestConfig(
    timeout=10.0,           # Override default timeout for this request
    retries=1,              # Override retry count for this request
    headers={"X-Custom": "value"},  # Additional headers
    request_id="my-trace-id",       # Custom request ID for tracing
)

tasks = client.tasks.list(limit=5, config=config)
```

```typescript
const tasks = await client.tasks.list(
  { limit: 5 },
  { timeout: 10000, requestId: 'my-trace-id' }
)
```

---

## 7. Module Reference

### 7.1 Tasks

```python
# List tasks with optional filters
tasks = client.tasks.list(
    limit=20,
    offset=0,
    status="pending",        # pending | in_progress | completed | cancelled
    priority="high",         # low | medium | high | urgent
)

# Create a task
task = client.tasks.create({
    "title": "Complete project report",
    "description": "Write the final report for the capstone project",
    "priority": "high",
    "due_date": "2026-07-25T23:59:00Z",
    "category": "academic",
    "estimated_minutes": 120,
    "project_id": "project-uuid",  # Optional: link to project
    "goal_id": "goal-uuid",        # Optional: link to goal
})

# Get with related data
task = client.tasks.get("task-uuid")

# Complete a task (convenience method)
task = client.tasks.complete("task-uuid")

# Update partial fields
task = client.tasks.update("task-uuid", {
    "status": "in_progress",
    "priority": "urgent",
})
```

```typescript
// Tasks module
const tasks = await client.tasks.list({
  limit: 20,
  offset: 0,
  status: 'pending',
  priority: 'high',
})

const task = await client.tasks.create({
  title: 'Complete project report',
  description: 'Write the final report',
  priority: 'high',
  dueDate: '2026-07-25T23:59:00Z',
})

await client.tasks.complete('task-uuid')
```

### 7.2 Chat (ARIA)

```python
# Send a message and get a response
response = client.chat.send(
    message="What is on my schedule today?",
    conversation_id="conv-uuid",  # Optional: continue a conversation
)
print(response["reply"])

# Stream a response
async for chunk in client.chat.stream(
    message="Summarize my week",
    conversation_id="conv-uuid",
):
    print(chunk, end="", flush=True)
```

```typescript
// Chat with streaming
const response = await client.chat.send({
  message: 'What is on my schedule today?',
  conversationId: 'conv-uuid',
})

// Streaming
const stream = client.chat.stream({
  message: 'Summarize my week',
  conversationId: 'conv-uuid',
})
for await (const chunk of stream) {
  process.stdout.write(chunk)
}
```

### 7.3 Automation

```python
# Trigger AI agent actions
briefing = client.automation.trigger_briefing()
radar = client.automation.trigger_opportunity_radar()
review = client.automation.trigger_weekly_review()
sleep_analysis = client.automation.trigger_sleep_analysis()
sleep_bedtime = client.automation.trigger_sleep_bedtime_message()
nudges = client.automation.trigger_nudges()
```

### 7.4 Memory

```python
# Get preferences from AI memory
memory = client.memory.list(limit=10)

# Store a preference
client.memory.create({
    "key": "preferred_study_time",
    "value": "morning",
    "category": "preference",
})

# Retrieve a specific memory
preference = client.memory.get("memory-uuid")

# Update a memory
client.memory.update("memory-uuid", {
    "value": "afternoon",
})
```

### 7.5 Analytics and Predictions

```python
# Get aggregate stats
stats = client.analytics.stats(period="week")  # day | week | month | quarter | year
print(stats["completion_rate"])
print(stats["total_tasks"])

# Get timeline data
timeline = client.analytics.timeline(
    metric="tasks_completed",
    start_date="2026-07-01",
    end_date="2026-07-14",
)

# ML predictions
sleep_prediction = client.predictions.sleep(score_threshold=75)
productivity_prediction = client.predictions.productivity()
```

### 7.6 Briefings and Reviews

```python
# Get today's briefing (returns existing or triggers generation)
briefing = client.briefings.get(date="2026-07-14")
print(briefing["summary"])
print(briefing["tasks_today"])
print(briefing["opportunities"])

# Generate a new briefing (force regeneration)
new_briefing = client.briefings.create({"date": "2026-07-14"})

# Weekly review
review = client.reviews.get(week_start="2026-07-08")
print(review["achievements"])
print(review["challenges"])
```

### 7.7 Monitoring

```python
# Record token usage (internal use)
client.monitoring.record_token_usage({
    "agent": "briefing_agent",
    "model": "mistral:7b",
    "provider": "ollama",
    "prompt_tokens": 800,
    "completion_tokens": 600,
    "duration_ms": 4500,
})

# Get usage summary
summary = client.monitoring.token_usage_summary(
    period="month",  # day | week | month
)
print(summary["total_cost"])
print(summary["total_tokens"])
```

### 7.8 NLP

```python
# Parse a natural language command
parsed = client.nlp.parse("Create a high priority task to study for the exam tomorrow")
# Returns: {"intent": "create_task", "entities": {"title": "Study for exam", "priority": "high", "due_date": "..."}}

# Execute a parsed command
result = client.nlp.execute("Mark the math assignment as complete")
# Returns: {"action": "task_completed", "details": {"task_id": "uuid", "title": "Math assignment"}}
```

### 7.9 Videos and Resources

```python
# List saved YouTube videos
videos = client.videos.list(limit=10)

# Save a new video
video = client.videos.create({
    "url": "https://youtube.com/watch?v=abc123",
    "title": "Machine Learning Course - Lecture 1",
    "notes": "Good introduction to supervised learning",
})

# List resources with tag filter
resources = client.resources.list(tags=["python", "fastapi"], limit=5)
```

### 7.10 Roadmap

```python
# Get skill development roadmap
roadmap = client.roadmap.list(goal_id="goal-uuid")
print(roadmap["milestones"])
print(roadmap["progress_pct"])

# Create a roadmap for a goal
new_roadmap = client.roadmap.create({
    "goal_id": "goal-uuid",
    "milestones": [
        {"title": "Complete course 1", "target_date": "2026-08-01"},
        {"title": "Build project 1", "target_date": "2026-09-01"},
    ],
})

# Update roadmap progress
client.roadmap.update("roadmap-uuid", {
    "progress_pct": 50,
    "current_milestone": "Complete course 1",
})
```

---

## 8. Error Handling

### 8.1 Error Types

#### Python

```python
from aria_os_sdk.exceptions import (
    AriaOSError,            # Base exception
    AuthenticationError,    # 401 - Invalid or expired token
    AuthorizationError,     # 403 - Insufficient permissions
    NotFoundError,          # 404 - Resource not found
    ConflictError,          # 409 - Resource conflict
    ValidationError,        # 422 - Invalid input
    RateLimitError,         # 429 - Rate limit exceeded
    ServerError,            # 5xx - Server-side error
    NetworkError,           # Connection timeout or failure
)
```

#### TypeScript

```typescript
import {
  AriaOSError,
  AuthenticationError,
  NotFoundError,
  ValidationError,
  RateLimitError,
} from '@aria-os/sdk'
```

### 8.2 Error Handling Patterns

```python
from aria_os_sdk import AriaOSClient
from aria_os_sdk.exceptions import NotFoundError, RateLimitError, ValidationError

client = AriaOSClient(base_url="...", auth_token="...")

try:
    task = client.tasks.get("non-existent-uuid")
except NotFoundError as e:
    print(f"Task not found: {e.detail}")
    print(f"Request ID: {e.request_id}")  # For tracing
except ValidationError as e:
    print(f"Validation failed: {e.errors}")  # List of field errors
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
    # Automatically retried by the SDK if retries are available
except AriaOSError as e:
    print(f"API error: {e.status_code} - {e.detail}")
```

```typescript
try {
  const task = await client.tasks.get('non-existent-uuid')
} catch (error) {
  if (error instanceof NotFoundError) {
    console.log(`Task not found: ${error.detail}`)
  } else if (error instanceof RateLimitError) {
    console.log(`Rate limited, retry after ${error.retryAfter}s`)
  } else if (error instanceof ValidationError) {
    console.log(`Validation errors:`, error.errors)
  }
}
```

### 8.3 Automatic Retry

The SDK automatically retries on the following conditions:

| Condition | Retry Strategy | Max Retries |
|---|---|---|
| HTTP 429 (Rate Limited) | Up to `Retry-After` header or 60s | 3 |
| HTTP 502/503/504 (Server Error) | Exponential backoff (2s, 4s, 8s) | 3 |
| Network timeout / connection error | Exponential backoff (1s, 2s, 4s) | 3 |
| HTTP 4xx (Client Error) | No retry | 0 |

### 8.4 Error Response Schema

All errors return this structure:

```json
{
  "detail": "Human-readable error message",
  "error_code": "TASK_NOT_FOUND",
  "request_id": "uuid-string",
  "timestamp": "2026-06-14T12:00:00Z"
}
```

The SDK maps these to typed exceptions. The `request_id` is always accessible for tracing in logs.

---

## 9. Rate Limiting Awareness

### 9.1 Default Limits

| Scope | Limit | Applied At |
|---|---|---|
| Global (per IP) | 100 req/min | Middleware |
| Chat endpoint | 30 req/min | Per-endpoint |
| AI automation triggers | 10 req/min | Per-endpoint |
| Analytics aggregations | 20 req/min | Per-endpoint |

### 9.2 Rate Limit Headers

Every response includes rate limit headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1689358800
Retry-After: 45
```

### 9.3 SDK Rate Limit Handling

```python
# The SDK automatically:
# 1. Reads Retry-After header on 429 responses
# 2. Waits the specified duration
# 3. Retries the request (up to max_retries)
# 4. Raises RateLimitError if all retries exhausted

# You can also check rate limit status proactively:
stats = client.get_rate_limit_status()
print(stats["remaining"])  # Requests remaining in current window
print(stats["reset_at"])   # Timestamp when window resets
```

---

## 10. Pagination Handling

### 10.1 Paginated Response Format

All list endpoints return this structure:

```json
{
  "data": [...],
  "total": 142,
  "limit": 20,
  "offset": 0
}
```

### 10.2 Manual Pagination

```python
# Page through results manually
page = 0
limit = 20
total = None

while total is None or page * limit < total:
    response = client.tasks.list(limit=limit, offset=page * limit)
    total = response["total"]
    for item in response["data"]:
        process(item)
    page += 1
```

### 10.3 Automatic Pagination (Python)

```python
# Use the paginate helper for automatic page iteration
from aria_os_sdk import paginate

for task in paginate(client.tasks.list, limit=20):
    process(task)
# Automatically handles offset/limit, yields individual items
```

### 10.4 Automatic Pagination (TypeScript)

```typescript
import { paginate } from '@aria-os/sdk'

for await (const task of paginate(
  (params) => client.tasks.list(params),
  { limit: 20 }
)) {
  process(task)
}
```

---

## 11. WebSocket and Realtime Subscriptions

### 11.1 Supabase Realtime (Recommended)

For real-time updates, use the Supabase client directly. The SDK does not wrap Supabase Realtime but it is compatible:

```python
from supabase import create_client

supabase = create_client(
    supabase_url="https://your-project.supabase.co",
    supabase_key="your-anon-key",
)

# Subscribe to task changes
channel = supabase.channel("task-updates")
channel.on_postgres_changes(
    event="*",  # INSERT | UPDATE | DELETE | *
    schema="public",
    table="tasks",
    filter=f"user_id=eq.{user_id}",
    callback=lambda payload: print(f"Task changed: {payload}"),
)
channel.subscribe()
```

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

const channel = supabase
  .channel('task-updates')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'tasks', filter: `user_id=eq.${userId}` },
    (payload) => console.log('Task changed:', payload)
  )
  .subscribe()
```

### 11.2 Polling Fallback

If Realtime is unavailable, the SDK provides a polling helper:

```python
from aria_os_sdk import poll

# Poll every 30 seconds for task changes
async for tasks in poll(
    fn=lambda: client.tasks.list(status="pending"),
    interval=30,
):
    process_tasks(tasks["data"])
```

---

## 12. Error Code Reference

### 12.1 Complete Error Code Catalog

| Error Code | HTTP Status | Description | Recovery |
|---|---|---|---|
| `INTERNAL_ERROR` | 500 | Unexpected server error | Retry with backoff; check logs |
| `NOT_FOUND` | 404 | Resource does not exist | Verify ID and user_id |
| `VALIDATION_ERROR` | 422 | Input validation failed | Fix request body per schema |
| `UNAUTHORIZED` | 401 | Missing or expired token | Refresh token or re-authenticate |
| `FORBIDDEN` | 403 | Insufficient permissions | Verify user owns the resource |
| `RATE_LIMITED` | 429 | Too many requests | Wait for Retry-After duration |
| `CONFLICT` | 409 | Resource state conflict | Handle idempotently or abort |
| `AI_UNAVAILABLE` | 503 | AI provider offline | Use algorithmic fallback |
| `TASK_NOT_FOUND` | 404 | Task ID does not exist | Verify task exists |
| `COURSE_NOT_FOUND` | 404 | Course ID does not exist | Verify course exists |
| `GOAL_NOT_FOUND` | 404 | Goal ID does not exist | Verify goal exists |
| `MEMORY_NOT_FOUND` | 404 | Memory key not found | Set memory first before reading |
| `BRIEFING_NOT_FOUND` | 404 | No briefing for this date | Trigger generation via automation |
| `DEPENDENCY_CYCLE` | 409 | Circular task dependency | Break the dependency chain |
| `DUPLICATE_ENTRY` | 409 | Unique constraint violation | Check for existing record |
| `INVALID_DATE_RANGE` | 422 | Start date after end date | Correct date ordering |
| `QUOTA_EXCEEDED` | 429 | Token budget exceeded | Wait for quota reset or upgrade |
| `CIRCUIT_BREAKER_OPEN` | 503 | AI circuit breaker is open | Wait for cooldown period |

### 12.2 Mapping Error Codes to SDK Exceptions

```python
ERROR_CODE_MAP = {
    "INTERNAL_ERROR": ServerError,
    "NOT_FOUND": NotFoundError,
    "VALIDATION_ERROR": ValidationError,
    "UNAUTHORIZED": AuthenticationError,
    "FORBIDDEN": AuthorizationError,
    "RATE_LIMITED": RateLimitError,
    "CONFLICT": ConflictError,
    "AI_UNAVAILABLE": ServerError,
}
```

---

## 13. Testing with the SDK

### 13.1 Mocking the Client (Python)

```python
import pytest
from unittest.mock import AsyncMock, patch
from aria_os_sdk import AriaOSClient

@pytest.fixture
def mock_client():
    client = AsyncMock(spec=AriaOSClient)
    client.tasks.list.return_value = {
        "data": [
            {"id": "1", "title": "Test Task", "status": "pending"}
        ],
        "total": 1,
        "limit": 20,
        "offset": 0,
    }
    return client

async def test_task_processing(mock_client):
    tasks = await mock_client.tasks.list(limit=10)
    assert len(tasks["data"]) == 1
    assert tasks["data"][0]["title"] == "Test Task"
```

### 13.2 Integration Test Pattern (Python)

```python
import pytest
from aria_os_sdk import AriaOSClient
from aria_os_sdk.exceptions import NotFoundError

@pytest.mark.integration
async def test_task_lifecycle():
    """Full CRUD lifecycle test against a real API."""
    client = AriaOSClient(
        base_url="http://localhost:8000",
        auth_token="test-token",
    )

    # Create
    created = await client.tasks.create({
        "title": "Integration test task",
        "priority": "low",
    })
    assert created["id"] is not None

    # Read
    fetched = await client.tasks.get(created["id"])
    assert fetched["title"] == "Integration test task"

    # Update
    updated = await client.tasks.update(created["id"], {"status": "completed"})
    assert updated["status"] == "completed"

    # Delete
    await client.tasks.delete(created["id"])

    # Verify deletion
    with pytest.raises(NotFoundError):
        await client.tasks.get(created["id"])
```

### 13.3 Testing with Recorded Responses (TypeScript)

```typescript
import { describe, it, expect, vi } from 'vitest'
import { AriaOSClient } from '@aria-os/sdk'

describe('Tasks SDK', () => {
  it('should list tasks with correct parameters', async () => {
    const client = new AriaOSClient({
      baseUrl: 'http://localhost:8000',
      authToken: 'test-token',
    })

    // Mock the HTTP layer
    vi.spyOn(client, 'request').mockResolvedValue({
      data: [{ id: '1', title: 'Test' }],
      total: 1,
      limit: 20,
      offset: 0,
    })

    const result = await client.tasks.list({ limit: 20 })
    expect(result.data).toHaveLength(1)
    expect(result.total).toBe(1)
  })
})
```

---

## 14. Related Documents

| Document | Relationship |
|---|---|
| `docs/engineering/17_API.md` | REST API that the SDK wraps |
| `docs/engineering/api/openapi-reference.md` | OpenAPI spec used to generate SDK types |
| `docs/engineering/api/rate-limiting.md` | Rate limit policies the SDK handles |
| `docs/engineering/api/error-catalog.md` | Error codes mapped to SDK exceptions |
| `docs/engineering/api/changelog.md` | API version history for migration |
| `docs/engineering/api/webhook-guide.md` | Webhook alternative to polling |
| `docs/engineering/integrations/Supabase.md` | Supabase Realtime setup for subscriptions |
| `docs/governance/01_DocumentationStandards.md` | Document standards followed in this reference |
| `docs/engineering/coding-standards.md` | Coding standards for SDK contributions |
| `packages/database/schemas/` | Pydantic models mapping to SDK response types |
| `.env.example` | Environment variables for SDK configuration |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-07-14 | Developer | Initial SDK reference covering Python and TypeScript clients |
