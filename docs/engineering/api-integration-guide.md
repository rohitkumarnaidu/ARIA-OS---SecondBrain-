# ARIA OS API Integration Guide

> **External developer reference for integrating with the Second Brain OS REST API**

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ENG-AIG-001 |
| **Version** | 1.0.0 |
| **Status** | Active |
| **Date** | 2026-07-11 |
| **Classification** | External |
| **Owner** | Developer |
| **Review Cycle** | Monthly |
| **Related Docs** | [OpenAPI Reference](api/openapi-reference.md), [REST Conventions](REST.md), [Error Codes](ErrorCodes.md), [Rate Limiting](api/rate-limiting.md), [API Changelog](api/changelog.md) |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Authentication](#2-authentication)
3. [Making Requests](#3-making-requests)
4. [API Conventions](#4-api-conventions)
5. [Error Handling](#5-error-handling)
6. [Rate Limiting](#6-rate-limiting)
7. [Versioning](#7-versioning)
8. [Code Examples](#8-code-examples)
9. [Webhooks (Future)](#9-webhooks-future)
10. [Best Practices](#10-best-practices)
11. [Support](#11-support)

---

## 1. Introduction

The ARIA OS API provides programmatic access to all features of the Second Brain personal productivity system. It powers the frontend web application and is fully available for third-party integrations.

### Architecture Overview

- **Framework**: FastAPI (Python 3.10+)
- **Authentication**: JWT Bearer tokens (user sessions) or API Keys (server-to-server)
- **Database**: Supabase (PostgreSQL) with Row-Level Security
- **API Style**: RESTful, JSON request/response bodies
- **Base Path**: All endpoints live under `/api/v1/`
- **Routers**: 31 route modules serving ~256 endpoints across 15 functional domains
- **Docs**: Interactive OpenAPI docs available at `/docs` (Swagger UI) or `/redoc` (ReDoc) when the server is running

### Domain Modules

| Module | Router Prefix | Endpoints | Purpose |
|---|---|---|---|
| Tasks | `/api/v1/tasks` | 6 | Task CRUD, completion, dependencies |
| Courses | `/api/v1/courses` | 4 | Course tracking, progress |
| Goals | `/api/v1/goals` | 5 | Goal management, milestones |
| Habits | `/api/v1/habits` | 4 | Habit definitions, streaks |
| Habit Logs | `/api/v1/habit-logs` | 3 | Daily habit completion |
| Sleep | `/api/v1/sleep` | 3 | Sleep tracking, score, debt |
| Income | `/api/v1/income` | 4 | Income logging, hourly rate |
| Projects | `/api/v1/projects` | 4 | Project phases, blockers |
| Ideas | `/api/v1/ideas` | 4 | Idea pipeline stages |
| Resources | `/api/v1/resources` | 4 | Resource library, tags |
| Opportunities | `/api/v1/opportunities` | 4 | Opportunity radar, match scores |
| Time | `/api/v1/time` | 7 | Time tracking, Pomodoro, deep work |
| Chat | `/api/v1/chat` | 2 | ARIA conversational AI |
| Memory | `/api/v1/memory` | 4 | Persistent AI memory |
| Briefings | `/api/v1/briefings` | 2 | Daily morning briefings |
| Reviews | `/api/v1/reviews` | 2 | Weekly reviews |
| Analytics | `/api/v1/analytics` | 2 | Stats and timeline data |
| Predictions | `/api/v1/predictions` | 2 | Sleep and productivity predictions |
| Notifications | `/api/v1/notifications` | 2 | User notifications |
| Roadmap | `/api/v1/roadmap` | 3 | Skill roadmap optimizer |
| Automation | `/api/v1/automation` | 6 | Trigger AI agents |
| Auth | `/api/v1/auth` | 4 | Login, signup, refresh, logout |

---

## 2. Authentication

ARIA OS supports two authentication methods. Choose the one that fits your use case.

### 2.1 API Key Auth (Server-to-Server)

Best for automated scripts, cron jobs, and long-running integrations.

**How to get a key:**
1. Log in to the ARIA OS dashboard
2. Navigate to Settings > API Keys
3. Click "Generate New Key"
4. Copy the key immediately â€” it is shown only once
5. The key is hashed (SHA-256) before storage; ARIA OS cannot recover a lost key

**Usage:**
```http
GET /api/v1/tasks HTTP/1.1
Host: api.secondbrain-os.com
X-API-Key: aria_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Content-Type: application/json
Accept: application/json
```

**Rate limit:** 1000 requests per hour per API key

**Key management:**
- Keys can be revoked from the dashboard at any time
- Keys can have an optional expiration date
- Deactivated keys return HTTP 401 immediately

### 2.2 JWT Auth (User Sessions)

Best for interactive applications and browser-based clients.

**Login flow:**

```
Client                          ARIA OS API
  â”‚                                   â”‚
  â”‚  POST /api/v1/auth/login          â”‚
  â”‚  { "email": "...",               â”‚
  â”‚    "password": "..." }            â”‚
  â”‚ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€>   â”‚
  â”‚                                   â”‚
  â”‚  200 OK                           â”‚
  â”‚  { "access_token": "eyJ...",     â”‚
  â”‚    "refresh_token": "eyJ...",    â”‚
  â”‚    "expires_in": 3600 }           â”‚
  â”‚ <â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€  â”‚
  â”‚                                   â”‚
  â”‚  GET /api/v1/tasks               â”‚
  â”‚  Authorization: Bearer eyJ...    â”‚
  â”‚ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€>   â”‚
  â”‚                                   â”‚
  â”‚  200 OK                           â”‚
  â”‚  [ ... task data ... ]           â”‚
  â”‚ <â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€  â”‚
```

**Access token:** HS256 JWT, expires in 1 hour
**Refresh token:** Long-lived, single-use, valid for 30 days

**Refresh flow:**
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ_refresh_token_here..."
}
```

**Response:**
```json
{
  "access_token": "eyJ_new_access_token...",
  "refresh_token": "eyJ_new_refresh_token...",
  "expires_in": 3600
}
```

### 2.3 When to Use Each

| Criteria | API Key | JWT |
|---|---|---|
| Use case | Cron jobs, scripts, CI/CD | Browser apps, mobile apps |
| Expiry | Optional (set on creation) | 1 hour (access) + 30 days (refresh) |
| Rate limit | 1000 req/hr | 100 req/min (shared pool) |
| Revocation | Immediate via dashboard | Token blacklist on logout |
| Human user | No | Yes |

---

## 3. Making Requests

### 3.1 Base URLs

| Environment | URL | Notes |
|---|---|---|
| Local Development | `http://localhost:8000` | Requires local backend running |
| Production | `https://api.secondbrain-os.com` | Live service behind TLS |
| Preview/Staging | `https://api-staging.secondbrain-os.com` | Pre-release testing |

### 3.2 Required Headers

```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer <token>          # For JWT auth
# OR
X-API-Key: <api_key>                    # For API key auth
```

### 3.3 Request Format

All request bodies must be JSON. The API does not accept form-encoded or multipart payloads.

```http
POST /api/v1/tasks HTTP/1.1
Host: api.secondbrain-os.com
Content-Type: application/json
Authorization: Bearer fake-jwt-token-string-for-testing...
Accept: application/json

{
  "title": "Complete project proposal",
  "priority": "high",
  "due_date": "2026-07-15T17:00:00Z",
  "estimated_minutes": 120,
  "category": "work"
}
```

### 3.4 Quickstart Examples

**List tasks (curl):**
```bash
curl -s https://api.secondbrain-os.com/api/v1/tasks \
  -H "Authorization: Bearer fake-jwt-token-string-for-testing..." \
  -H "Accept: application/json"
```

**Create a task (curl):**
```bash
curl -s -X POST https://api.secondbrain-os.com/api/v1/tasks \
  -H "Authorization: Bearer fake-jwt-token-string-for-testing..." \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"title": "Review PR", "priority": "medium"}'
```

**Get daily briefing (curl):**
```bash
curl -s https://api.secondbrain-os.com/api/v1/briefings?date=2026-07-11 \
  -H "X-API-Key: aria_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  -H "Accept: application/json"
```

---

## 4. API Conventions

### 4.1 URL Structure

```
/api/v1/{resource}/{id}/
```

All endpoints are versioned under `/api/v1/`. Resources are plural nouns.

### 4.2 HTTP Methods and Status Codes

| Method | Endpoint | Action | Success Code | Idempotent |
|---|---|---|---|---|
| `GET` | `/api/v1/{resource}/` | List resources | 200 | Yes |
| `POST` | `/api/v1/{resource}/` | Create resource | 201 | No |
| `GET` | `/api/v1/{resource}/{id}` | Get single resource | 200 | Yes |
| `PUT` | `/api/v1/{resource}/{id}` | Full/partial update | 200 | Yes |
| `DELETE` | `/api/v1/{resource}/{id}` | Delete resource | 204 | Yes |

**Special action endpoints** use sub-resource naming:

```http
POST /api/v1/tasks/{id}/complete    # Mark task complete (201)
POST /api/v1/time/stop              # Stop active timer (200)
POST /api/v1/notifications/{id}/read # Mark notification read (200)
```

### 4.3 Pagination

List endpoints support cursor-free offset pagination.

| Parameter | Type | Default | Range | Description |
|---|---|---|---|---|
| `limit` | integer | 20 | 1â€“100 | Number of items per page |
| `offset` | integer | 0 | 0+ | Number of items to skip |

**Example:**
```http
GET /api/v1/tasks?limit=10&offset=20
```

**Response includes pagination metadata:**
```json
{
  "data": [...],
  "total": 142,
  "limit": 10,
  "offset": 20
}
```

### 4.4 Filtering

Use query parameters with optional operators:

| Operator | Example | Description |
|---|---|---|
| Exact match | `?status=pending` | Equals comparison |
| `.gte` | `?due_date.gte=2026-06-01` | Greater than or equal |
| `.lte` | `?priority.lte=3` | Less than or equal |
| `.in` | `?status.in=pending,in_progress` | IN list |
| `.like` | `?title.like=%proposal%` | SQL LIKE pattern |

**Example:**
```http
GET /api/v1/tasks?status=pending&due_date.gte=2026-07-01&priority=high
```

### 4.5 Sorting

| Parameter | Values | Default |
|---|---|---|
| `sort` | Field name (e.g., `created_at`, `due_date`, `priority`) | `created_at` |
| `order` | `asc` or `desc` | `desc` |

**Example:**
```http
GET /api/v1/tasks?sort=due_date&order=asc&status=pending
```

---

## 5. Error Handling

### 5.1 Error Response Format

All errors return a consistent JSON structure:

```json
{
  "detail": "Human-readable error message",
  "error_code": "RESOURCE_NOT_FOUND",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2026-07-11T14:30:00Z"
}
```

Every error response includes a unique `request_id` (UUID v4). Include this when reporting issues.

### 5.2 Error Codes

| HTTP Status | Error Code | Meaning | Typical Cause |
|---|---|---|---|
| 400 | `VALIDATION_ERROR` | Request body failed validation | Missing required field, invalid type |
| 400 | `INVALID_INPUT` | Semantically invalid input | Due date in the past |
| 401 | `AUTH_INVALID` | Missing or invalid credentials | Expired token, bad API key |
| 401 | `AUTH_EXPIRED` | Token has expired | Access token beyond 1 hour |
| 403 | `FORBIDDEN` | Authenticated but not allowed | Cross-user resource access |
| 404 | `RESOURCE_NOT_FOUND` | Resource does not exist | Wrong ID, already deleted |
| 409 | `CONFLICT` | Resource state conflict | Duplicate title, status conflict |
| 422 | `UNPROCESSABLE_ENTITY` | Well-formed but unprocessable | Validation logic error |
| 429 | `RATE_LIMITED` | Too many requests | Exceeded rate limit |
| 500 | `INTERNAL_ERROR` | Server-side failure | Database timeout, unhandled exception |
| 503 | `SERVICE_UNAVAILABLE` | Temporary service disruption | AI provider unavailable, maintenance |

### 5.3 Retry Strategy for 429 Responses

When you receive HTTP 429 (`RATE_LIMITED`):

1. **Check the `Retry-After` header** for the number of seconds to wait
2. **Use exponential backoff** with jitter:

```
Initial wait:    1 second
Backoff factor:  2
Max wait:        60 seconds
Jitter:          random(0, 1000ms)
Retry limit:     5 attempts
```

**Example implementation (pseudocode):**
```
attempt = 0
max_attempts = 5
base_delay = 1
max_delay = 60

while attempt < max_attempts:
    response = api_call()
    if response.status != 429:
        return response
    
    delay = min(base_delay * (2 ^ attempt), max_delay)
    delay += random(0, 1)  # jitter
    sleep(delay)
    attempt += 1

raise "Max retries exceeded"
```

---

## 6. Rate Limiting

### 6.1 Limits

| Scope | Limit | Window | Applies To |
|---|---|---|---|
| Global (per IP) | 100 requests | 60 seconds | All endpoints |
| Chat/AI | 30 requests | 60 seconds | `/api/v1/chat/*` |
| API Key | 1000 requests | 1 hour | Key-authenticated requests |
| Auth | 10 requests | 60 seconds | `/api/v1/auth/login` |

### 6.2 Rate Limit Headers

Every response includes these headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1710203400
```

| Header | Description |
|---|---|
| `X-RateLimit-Limit` | Maximum requests allowed in the window |
| `X-RateLimit-Remaining` | Requests remaining in the current window |
| `X-RateLimit-Reset` | Unix timestamp when the window resets |

### 6.3 Handling Rate Limits

When `X-RateLimit-Remaining` approaches zero:

1. **Slow down** â€” increase interval between requests
2. **Cache responses** where freshness allows (see [Best Practices](#10-best-practices))
3. **Batch operations** when possible by adjusting `limit` to fetch more items per request
4. **Distribute load** by staggering cron jobs across the hour

---

## 7. Versioning

### 7.1 URL-Based Versioning

All endpoints use explicit version in the URL path:

```
/api/v1/{resource}    # Current stable version
/api/v2/{resource}    # Future breaking changes
```

### 7.2 Version Status

| Version | Status | Release Date | Sunset Date |
|---|---|---|---|
| v1 | Active | 2026-06-01 | TBD |

### 7.3 Deprecation Headers

When an endpoint is scheduled for deprecation, the API will include:

```http
GET /api/v1/chat HTTP/1.1
Deprecation: true
Sunset: Sat, 01 Jan 2027 00:00:00 GMT
```

| Header | Description |
|---|---|
| `Deprecation: true` | Indicates the endpoint is deprecated |
| `Sunset` | RFC 1123 timestamp when the endpoint will be removed |

### 7.4 Migration Policy

- New endpoints are added under `/api/v1/` â€” backward compatible
- Breaking changes create a new version (e.g., `/api/v2/`)
- Old versions get `Deprecation` + `Sunset` headers at least 6 months before removal
- Migration guides published in the [API Changelog](api/changelog.md)
- At least one full release cycle of overlap before v1 removal

---

## 8. Code Examples

### 8.1 Python (httpx)

**Setup:**
```python
import httpx
from typing import Optional

BASE_URL = "https://api.secondbrain-os.com"
TIMEOUT = httpx.Timeout(30.0, connect=5.0)


class ARIAOSClient:
    def __init__(self, api_key: Optional[str] = None, token: Optional[str] = None):
        self.base_url = BASE_URL
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if api_key:
            headers["X-API-Key"] = api_key
        elif token:
            headers["Authorization"] = f"Bearer {token}"
        else:
            raise ValueError("Provide either api_key or token")

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=TIMEOUT,
        )

    async def list_tasks(
        self,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        """Fetch paginated task list with optional status filter."""
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status

        response = await self.client.get("/api/v1/tasks/", params=params)
        response.raise_for_status()
        return response.json()

    async def create_task(self, title: str, priority: str = "medium", **kwargs) -> dict:
        """Create a new task. Returns the created task object."""
        payload = {"title": title, "priority": priority, **kwargs}
        response = await self.client.post("/api/v1/tasks/", json=payload)
        response.raise_for_status()
        return response.json()

    async def get_daily_briefing(self, date: Optional[str] = None) -> dict:
        """Fetch the daily morning briefing for a given date (default: today)."""
        params = {}
        if date:
            params["date"] = date
        response = await self.client.get("/api/v1/briefings/", params=params)
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()
```

**Usage:**
```python
import asyncio

async def main():
    # Using API key
    client = ARIAOSClient(api_key="aria_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

    # List pending tasks
    tasks = await client.list_tasks(status="pending", limit=5)
    print(f"Found {tasks['total']} pending tasks")

    # Create a new task
    new_task = await client.create_task(
        title="Review architecture doc",
        priority="high",
        due_date="2026-07-15T17:00:00Z",
        estimated_minutes=60,
    )
    print(f"Created task: {new_task['id']}")

    # Get today's briefing
    briefing = await client.get_daily_briefing()
    print(f"Focus: {briefing.get('focus_area')}")

    await client.close()

asyncio.run(main())
```

### 8.2 TypeScript (fetch)

```typescript
interface TaskListResponse {
  data: Task[];
  total: number;
  limit: number;
  offset: number;
}

interface Task {
  id: string;
  title: string;
  status: "pending" | "in_progress" | "completed";
  priority: "low" | "medium" | "high";
  due_date?: string;
  created_at: string;
  estimated_minutes?: number;
}

interface Briefing {
  date: string;
  focus_area: string;
  summary: string;
  top_tasks: Task[];
}

class ARIAOSClient {
  private baseUrl = "https://api.secondbrain-os.com";
  private headers: Record<string, string>;

  constructor(auth: { apiKey?: string; token?: string }) {
    this.headers = {
      "Content-Type": "application/json",
      Accept: "application/json",
    };
    if (auth.apiKey) {
      this.headers["X-API-Key"] = auth.apiKey;
    } else if (auth.token) {
      this.headers["Authorization"] = `Bearer ${auth.token}`;
    } else {
      throw new Error("Provide either apiKey or token");
    }
  }

  async listTasks(params?: {
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<TaskListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.set("status", params.status);
    if (params?.limit) searchParams.set("limit", String(params.limit));
    if (params?.offset) searchParams.set("offset", String(params.offset));

    const url = `${this.baseUrl}/api/v1/tasks/?${searchParams}`;
    const response = await fetch(url, { headers: this.headers });
    if (!response.ok) await this.handleError(response);
    return response.json();
  }

  async createTask(task: {
    title: string;
    priority?: string;
    due_date?: string;
    estimated_minutes?: number;
  }): Promise<Task> {
    const response = await fetch(`${this.baseUrl}/api/v1/tasks/`, {
      method: "POST",
      headers: this.headers,
      body: JSON.stringify(task),
    });
    if (!response.ok) await this.handleError(response);
    return response.json();
  }

  async getDailyBriefing(date?: string): Promise<Briefing> {
    const params = date ? `?date=${date}` : "";
    const response = await fetch(
      `${this.baseUrl}/api/v1/briefings/${params}`,
      { headers: this.headers }
    );
    if (!response.ok) await this.handleError(response);
    return response.json();
  }

  private async handleError(response: Response): Promise<never> {
    const error = await response.json();
    throw new APIError(
      error.detail || "Unknown error",
      error.error_code || "UNKNOWN",
      response.status,
      error.request_id
    );
  }
}

class APIError extends Error {
  constructor(
    message: string,
    public code: string,
    public status: number,
    public requestId: string
  ) {
    super(message);
    this.name = "APIError";
  }
}
```

**Usage:**
```typescript
async function main() {
  const client = new ARIAOSClient({
    apiKey: "aria_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  });

  try {
    const tasks = await client.listTasks({ status: "pending", limit: 5 });
    console.log(`Found ${tasks.total} pending tasks`);

    const newTask = await client.createTask({
      title: "Review architecture doc",
      priority: "high",
      due_date: "2026-07-15T17:00:00Z",
    });
    console.log(`Created task: ${newTask.id}`);

    const briefing = await client.getDailyBriefing();
    console.log(`Focus: ${briefing.focus_area}`);
  } catch (err) {
    if (err instanceof APIError) {
      console.error(`API Error [${err.code}]: ${err.message}`);
    }
  }
}

main();
```

### 8.3 JavaScript (axios)

```javascript
const axios = require("axios");

const client = axios.create({
  baseURL: "https://api.secondbrain-os.com",
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
  timeout: 30000,
});

// Auth setup
const API_KEY = process.env.ARIA_API_KEY;
client.defaults.headers["X-API-Key"] = API_KEY;

// Request interceptor for rate limit handling
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 429) {
      const retryAfter = parseInt(
        error.response.headers["retry-after"] || "1",
        10
      );
      console.warn(`Rate limited. Retrying after ${retryAfter}s`);
      await new Promise((resolve) => setTimeout(resolve, retryAfter * 1000));
      return client.request(error.config);
    }
    return Promise.reject(error);
  }
);

// List tasks
async function listTasks(params = {}) {
  const response = await client.get("/api/v1/tasks/", { params });
  return response.data;
}

// Create task
async function createTask(taskData) {
  const response = await client.post("/api/v1/tasks/", taskData);
  return response.data;
}

// Get daily briefing
async function getDailyBriefing(date) {
  const params = date ? { date } : {};
  const response = await client.get("/api/v1/briefings/", { params });
  return response.data;
}

// Usage
(async () => {
  const tasks = await listTasks({ status: "pending", limit: 10 });
  console.log(`Tasks: ${tasks.total}`);

  const task = await createTask({
    title: "API integration guide review",
    priority: "high",
  });
  console.log(`Created: ${task.id}`);
})();
```

### 8.4 curl Reference

```bash
# â”€â”€ Authentication â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# Login with email/password â†’ get JWT tokens
curl -s -X POST https://api.secondbrain-os.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "your_password"}' | jq .

# Refresh access token
curl -s -X POST https://api.secondbrain-os.com/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "eyJ_refresh_token..."}' | jq .

# â”€â”€ Tasks â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# List tasks (paginated)
curl -s "https://api.secondbrain-os.com/api/v1/tasks/?limit=10&offset=0" \
  -H "Authorization: Bearer eyJ_access_token..." | jq .

# List with filters
curl -s "https://api.secondbrain-os.com/api/v1/tasks/?status=pending&priority=high&sort=due_date&order=asc" \
  -H "Authorization: Bearer eyJ_access_token..." | jq .

# Get single task
curl -s https://api.secondbrain-os.com/api/v1/tasks/task_abc123 \
  -H "Authorization: Bearer eyJ_access_token..." | jq .

# Create task
curl -s -X POST https://api.secondbrain-os.com/api/v1/tasks/ \
  -H "Authorization: Bearer eyJ_access_token..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project proposal",
    "priority": "high",
    "due_date": "2026-07-15T17:00:00Z",
    "estimated_minutes": 120
  }' | jq .

# Update task
curl -s -X PUT https://api.secondbrain-os.com/api/v1/tasks/task_abc123 \
  -H "Authorization: Bearer eyJ_access_token..." \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress", "priority": "medium"}' | jq .

# Delete task (returns 204 No Content)
curl -s -o /dev/null -w "%{http_code}" -X DELETE \
  https://api.secondbrain-os.com/api/v1/tasks/task_abc123 \
  -H "Authorization: Bearer eyJ_access_token..."

# Complete task
curl -s -X POST https://api.secondbrain-os.com/api/v1/tasks/task_abc123/complete \
  -H "Authorization: Bearer eyJ_access_token..." | jq .

# â”€â”€ Briefings â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# Get today's briefing
curl -s https://api.secondbrain-os.com/api/v1/briefings/ \
  -H "X-API-Key: aria_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" | jq .

# Get briefing for specific date
curl -s "https://api.secondbrain-os.com/api/v1/briefings/?date=2026-07-11" \
  -H "X-API-Key: aria_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" | jq .

# â”€â”€ Habits â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# List habits
curl -s https://api.secondbrain-os.com/api/v1/habits/ \
  -H "Authorization: Bearer eyJ_access_token..." | jq .

# Log habit completion
curl -s -X POST https://api.secondbrain-os.com/api/v1/habit-logs/ \
  -H "Authorization: Bearer eyJ_access_token..." \
  -H "Content-Type: application/json" \
  -d '{"habit_id": "habit_xyz", "date": "2026-07-11", "completed": true}' | jq .

# â”€â”€ AI Agent Endpoints â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# Trigger daily briefing generation
curl -s -X POST https://api.secondbrain-os.com/api/v1/automation/trigger/briefing \
  -H "Authorization: Bearer eyJ_access_token..." | jq .

# Trigger opportunity radar scan
curl -s -X POST https://api.secondbrain-os.com/api/v1/automation/trigger/radar \
  -H "Authorization: Bearer eyJ_access_token..." | jq .

# Chat with ARIA
curl -s -X POST https://api.secondbrain-os.com/api/v1/chat/ \
  -H "Authorization: Bearer eyJ_access_token..." \
  -H "Content-Type: application/json" \
  -d '{"message": "What should I focus on today?"}' | jq .

# â”€â”€ Health & Monitoring â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# Health check (no auth required)
curl -s https://api.secondbrain-os.com/api/v1/health | jq .

# Readiness probe
curl -s https://api.secondbrain-os.com/api/v1/health/ready | jq .

# â”€â”€ API Key (Alternate Auth) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# All endpoints support API key auth via header
curl -s "https://api.secondbrain-os.com/api/v1/tasks/?limit=5" \
  -H "X-API-Key: aria_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" | jq .
```

---

## 9. Webhooks (Future)

*This section describes the planned webhook system. Not yet available.*

### Design Intent

Webhooks will allow your application to receive real-time notifications when events occur in ARIA OS, without polling.

### Proposed Event Types

| Event | Trigger | Payload |
|---|---|---|
| `task.created` | New task created | Full task object |
| `task.completed` | Task marked complete | Task ID + completion time |
| `task.overdue` | Task passes due date | Task ID + overdue duration |
| `briefing.generated` | Daily briefing ready | Briefing ID + date |
| `review.generated` | Weekly review ready | Review ID + week |
| `memory.consolidated` | Memory updated | Memory summary |
| `opportunity.found` | New opportunity match | Opportunity ID + score |

### Proposed Delivery

- POST to your registered URL
- JSON payload with `event_type`, `timestamp`, and `data` fields
- Signed with HMAC-SHA256 signature in `X-Webhook-Signature` header
- Retry with exponential backoff (3 attempts)
- Register webhook endpoints via dashboard or future API

---

## 10. Best Practices

### 10.1 Handle Rate Limits Gracefully

- Always check `X-RateLimit-Remaining` headers on responses
- Implement exponential backoff with jitter for 429 responses
- Respect `Retry-After` header values
- For bulk operations, increase `limit` rather than making more requests

### 10.2 Validate Responses

- Always check the HTTP status code first
- Validate response JSON structure matches expected schema
- Handle `total` in paginated responses to know when to stop fetching
- Expect `null` fields on optional properties

### 10.3 Cache Aggressively

- Cache briefing responses for the remainder of the day (they update only once)
- Cache resource metadata (notifications, analytics stats) with 5-minute TTL
- Do NOT cache task, habit, or time entries (high churn)
- Use `ETag` or `Last-Modified` headers if the API returns them

### 10.4 Use Connection Pooling

- Python: Reuse `httpx.AsyncClient` or `requests.Session` across requests
- Node.js: Reuse `axios` instance or enable `http.Agent` keep-alive
- Set reasonable timeouts: 5s connect, 30s total for CRUD, 60s for AI endpoints
- Limit concurrent connections to avoid local resource exhaustion

### 10.5 Error Recovery

- Retry on 429 (rate limit), 503 (service unavailable), and 5xx (server errors)
- Do NOT retry on 400 (client error), 401 (auth), 403 (forbidden), 404 (not found)
- Log `request_id` from error responses for debugging
- Implement circuit breaker if calling AI-heavy endpoints (briefings, chat)

### 10.6 Security

- Never expose API keys or tokens in client-side code
- Use environment variables or secure secret storage
- Rotate API keys periodically (every 90 days recommended)
- Use API keys for server-to-server, JWT for user-facing apps

---

## 11. Support

### API Status

Check the ARIA OS API status page for live service health:

- **Status Page**: `https://status.secondbrain-os.com`
- **Health Endpoint**: `GET /health` (no auth required)
- **Readiness**: `GET /health/ready` (checks dependencies: Supabase, AI providers)

### Reporting Issues

| Issue Type | Where to Report |
|---|---|
| API bugs | GitHub Issues: `https://github.com/your-org/secondbrain-os/issues` |
| Security vulnerabilities | Email: `security@secondbrain-os.com` |
| Integration questions | API Discussion Board (coming soon) |

Include the following in bug reports:
- Endpoint URL and HTTP method
- Full request headers (redact auth tokens)
- Request body (if applicable)
- Response status code and full error body
- `request_id` from the error response
- Timestamp of the request

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-07-11 | Developer | Initial API integration guide â€” 31 routers, auth methods, pagination, error codes, code examples in Python/TS/JS/curl |
