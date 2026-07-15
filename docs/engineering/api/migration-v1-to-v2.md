# API Migration Guide: v1 to v2

> **Migration guide for upgrading from ARIA OS API v1 to v2**

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ENG-MIG-001 |
| **Version** | 1.0.0 |
| **Status** | Draft (Template) |
| **Date** | 2026-07-12 |
| **Classification** | External |
| **Owner** | Developer |
| **Review Cycle** | Monthly |
| **Related Docs** | [API Integration Guide](../api-integration-guide.md), [Versioning Strategy](../Versioning.md), [API Changelog](changelog.md), [Error Catalog](error-catalog.md) |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Current State: v1 Endpoints](#2-current-state-v1-endpoints)
3. [Breaking Changes in v2](#3-breaking-changes-in-v2)
4. [Timeline & Deprecation](#4-timeline--deprecation)
5. [Migration Steps](#5-migration-steps)
6. [Backward Compatibility](#6-backward-compatibility)
7. [Testing the Migration](#7-testing-the-migration)
8. [Common Migration Issues](#8-common-migration-issues)
9. [Rollback Plan](#9-rollback-plan)
10. [Related Documentation](#10-related-documentation)

---

## 1. Introduction

This guide documents the migration from **ARIA OS API v1** to **API v2**. It covers breaking changes, step-by-step migration instructions, testing procedures, and rollback plans.

### What to Expect in v2

- **Improved response format** — consistent `items` + `pagination` structure
- **Cursor-based pagination** — more reliable for large datasets
- **Standardized error format** — machine-readable error codes with request tracing
- **Enhanced filtering** — richer query operators
- **Performance improvements** — reduced latency for list endpoints
- **New features** — additional endpoints and capabilities

---

## 2. Current State: v1 Endpoints

All v1 endpoints remain fully operational during the migration window. The following table shows the current status of each module:

| Module | v1 Prefix | Status | v2 Available |
|---|---|---|---|
| Tasks | `/api/v1/tasks` | ✅ Active | 📋 Planned |
| Courses | `/api/v1/courses` | ✅ Active | 📋 Planned |
| Goals | `/api/v1/goals` | ✅ Active | 📋 Planned |
| Habits | `/api/v1/habits` | ✅ Active | 📋 Planned |
| Habit Logs | `/api/v1/habit-logs` | ✅ Active | 📋 Planned |
| Sleep | `/api/v1/sleep` | ✅ Active | 📋 Planned |
| Income | `/api/v1/income` | ✅ Active | 📋 Planned |
| Projects | `/api/v1/projects` | ✅ Active | 📋 Planned |
| Ideas | `/api/v1/ideas` | ✅ Active | 📋 Planned |
| Resources | `/api/v1/resources` | ✅ Active | 📋 Planned |
| Opportunities | `/api/v1/opportunities` | ✅ Active | 📋 Planned |
| Time | `/api/v1/time` | ✅ Active | 📋 Planned |
| Chat | `/api/v1/chat` | ✅ Active | 📋 Planned |
| Memory | `/api/v1/memory` | ✅ Active | 📋 Planned |
| Briefings | `/api/v1/briefings` | ✅ Active | 📋 Planned |
| Reviews | `/api/v1/reviews` | ✅ Active | 📋 Planned |
| Analytics | `/api/v1/analytics` | ✅ Active | 📋 Planned |
| Predictions | `/api/v1/predictions` | ✅ Active | 📋 Planned |
| Notifications | `/api/v1/notifications` | ✅ Active | 📋 Planned |
| Roadmap | `/api/v1/roadmap` | ✅ Active | 📋 Planned |
| Automation | `/api/v1/automation` | ✅ Active | 📋 Planned |
| Auth | `/api/v1/auth` | ✅ Active | 📋 Planned |

---

## 3. Breaking Changes in v2

### 3.1 Change Summary

| Change | v1 (Old) | v2 (New) | Migration Effort |
|---|---|---|---|
| **URL prefix** | `/api/v1/tasks` | `/api/v2/tasks` | Simple prefix change |
| **Response format** | `{data: [...], limit, offset}` | `{items: [...], pagination: {limit, offset, total}}` | Update response parsing |
| **Error format** | `{detail: "msg"}` | `{error: {code, message, request_id, timestamp}}` | Update error handling |
| **Pagination** | `limit` / `offset` query params | Cursor-based (`cursor` param) | Add cursor tracking |
| **Filtering** | Query params with `.gte`/`.lte` suffixes | Structured filter object in query | Update filter construction |
| **Sorting** | `sort` + `order` query params | `sort` param with `+`/`-` prefix | Update sort parameter format |
| **Rate limit headers** | `X-RateLimit-*` | `X-RateLimit-*` + `Retry-After` | Add `Retry-After` parsing |
| **Deprecation headers** | Not present | `Deprecation` + `Sunset` on v1 | Monitor headers for migration timing |

### 3.1 Response Format Change

**v1 (current):**
```json
{
  "data": [
    {"id": "1", "title": "Task 1", "status": "pending"}
  ],
  "total": 142,
  "limit": 20,
  "offset": 0
}
```

**v2 (new):**
```json
{
  "items": [
    {"id": "1", "title": "Task 1", "status": "pending"}
  ],
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 142,
    "has_more": true,
    "next_cursor": "cursor_abc123"
  }
}
```

### 3.2 Error Format Change

**v1 (current):**
```json
{
  "detail": "Task not found",
  "error_code": "RESOURCE_NOT_FOUND",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2026-07-11T12:00:00Z"
}
```

**v2 (new):**
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested task does not exist.",
    "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "timestamp": "2026-07-11T12:00:00Z",
    "retry_after": null
  }
}
```

### 3.3 Pagination Change

**v1 — offset-based:**
```http
GET /api/v1/tasks?limit=20&offset=40
```

**v2 — cursor-based:**
```http
GET /api/v2/tasks?limit=20&cursor=cursor_abc123
```

**v2 pagination response:**
```json
{
  "items": [...],
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 142,
    "has_more": true,
    "next_cursor": "cursor_def456",
    "prev_cursor": null
  }
}
```

### 3.3 Error Format Comparison

**v1 error:**
```json
{
  "detail": "Task not found",
  "error_code": "RESOURCE_NOT_FOUND",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2026-07-11T12:00:00Z"
}
```

**v2 error:**
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested task does not exist.",
    "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "timestamp": "2026-07-11T12:00:00Z",
    "retry_after": null
  }
}
```

---

## 4. Timeline & Deprecation

### 4.1 Key Dates

| Milestone | Date | Description |
|---|---|---|
| **v2 Release** | TBD | v2 endpoints become available alongside v1 |
| **v1 Deprecation announced** | v2 release date + 0 days | `Deprecation: true` header added to v1 responses |
| **Migration window opens** | v2 release date | Both v1 and v2 available |
| **v1 Sunset date** | v2 release date + 6 months | v1 endpoints return `410 Gone` |
| **v1 fully removed** | Sunset date + 0 days | v1 routes removed from API |

### 4.1 Deprecation Headers

When v1 is deprecated, all v1 responses will include:

```http
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sat, 01 Jan 2027 00:00:00 GMT
Link: <https://docs.secondbrain-os.com/api/migration-v1-to-v2>; rel="deprecation"
```

| Header | Description |
|---|---|
| `Deprecation: true` | Indicates this API version is deprecated |
| `Sunset` | RFC 1123 timestamp when the endpoint will be removed |
| `Link` | URL to this migration guide |

### 4.2 Monitoring Deprecation Headers

Update your client to log deprecation warnings when these headers are detected:

```python
import warnings

async def make_api_request(url: str, **kwargs):
    response = await client.request(url, **kwargs)

    if response.headers.get("Deprecation") == "true":
        sunset = response.headers.get("Sunset", "unknown")
        warnings.warn(
            f"API version deprecated. Sunset: {sunset}. "
            f"See migration guide: https://docs.secondbrain-os.com/api/migration-v1-to-v2"
        )

    return response
```

---

## 5. Migration Steps

### Step 1: Update Base URL

Replace `/api/v1/` with `/api/v2/` in all API calls.

**Before (v1):**
```python
response = await client.get("/api/v1/tasks/", params={"limit": 20})
```

**After (v2):**
```python
response = await client.get("/api/v2/tasks/", params={"limit": 20})
```

### Step 2: Update Response Parsing

Update your client to handle the new response format:

**Python:**
```python
# v1 — old parsing
def parse_tasks_v1(response: dict) -> list:
    return response["data"]  # Direct array access

# v2 — new parsing
def parse_tasks_v2(response: dict) -> list:
    items = response["items"]
    pagination = response["pagination"]
    has_more = pagination["has_more"]
    next_cursor = pagination.get("next_cursor")
    return items, has_more, next_cursor
```

**TypeScript:**
```typescript
// v1 — old parsing
interface V1Response {
  data: Task[];
  total: number;
  limit: number;
  offset: number;
}

// v2 — new parsing
interface V2Response {
  items: Task[];
  pagination: {
    limit: number;
    offset: number;
    total: number;
    has_more: boolean;
    next_cursor: string | null;
    prev_cursor: string | null;
  };
}
```

### Step 2: Update Error Handling

**Python:**
```python
# v1 — old error handling
def handle_error_v1(response):
    error = response.json()
    print(f"Error: {error['detail']} (code: {error.get('error_code', 'UNKNOWN')})")

# v2 — new error handling
def handle_error_v2(response):
    error = response.json()["error"]
    print(f"Error [{error['code']}]: {error['message']}")
    print(f"Request ID: {error['request_id']}")
    if error.get("retry_after"):
        print(f"Retry after: {error['retry_after']}s")
```

**TypeScript:**
```typescript
// v1 — old error handling
interface V1Error {
  detail: string;
  error_code: string;
  request_id: string;
  timestamp: string;
}

// v2 — new error handling
interface V2Error {
  error: {
    code: string;
    message: string;
    request_id: string;
    timestamp: string;
    retry_after: number | null;
  };
}

function handleErrorV2(response: Response): never {
  const body: V2Error = await response.json();
  const err = body.error;
  throw new APIError(err.code, err.message, response.status, err.request_id);
}
```

### Step 3: Update Pagination Logic

**Python — cursor-based pagination:**
```python
async def fetch_all_tasks_v2(client, limit: int = 100):
    items = []
    cursor = None

    while True:
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor

        response = await client.get("/api/v2/tasks/", params=params)
        body = response.json()

        items.extend(body["items"])

        if not body["pagination"]["has_more"]:
            break

        cursor = body["pagination"]["next_cursor"]

    return items
```

**TypeScript:**
```typescript
async function* iterateTasksV2(client: ARIAOSClient, limit = 100) {
  let cursor: string | null = null;

  do {
    const params: Record<string, string> = { limit: String(limit) };
    if (cursor) params.cursor = cursor;

    const response = await client.get("/api/v2/tasks/", { params });
    const body = response.data;

    yield body.items;

    cursor = body.pagination.next_cursor;
  } while (cursor);
}

// Usage
for await (const batch of iterateTasksV2(client)) {
  for (const task of batch) {
    console.log(task.title);
  }
}
```

### Step 4: Test with Sandbox Environment

Before migrating production traffic, test against the sandbox environment:

```bash
# Sandbox base URL
SANDBOX_URL="https://api-sandbox.secondbrain-os.com"

# Test v2 endpoint
curl -s "$SANDBOX_URL/api/v2/tasks/?limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Compare with v1 response
curl -s "$SANDBOX_URL/api/v1/tasks/?limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### Step 5: Monitor Deprecation Headers

Add monitoring for deprecation headers in your client to ensure you're notified of upcoming changes:

```python
import logging

logger = logging.getLogger("api_client")

class MonitoredClient:
    async def request(self, method: str, path: str, **kwargs):
        response = await self.client.request(method, path, **kwargs)

        if response.headers.get("Deprecation") == "true":
            sunset = response.headers.get("Sunset", "unknown")
            logger.warning(
                f"API version deprecated. Endpoint: {path}. "
                f"Sunset: {sunset}. "
                f"Migration guide: https://docs.secondbrain-os.com/api/migration-v1-to-v2"
            )

        return response
```

---

## 6. Backward Compatibility

### 6.1 Overlap Period

v1 and v2 endpoints will run concurrently for **6 months** after the v2 release. During this period:

- **v1 endpoints** continue to function unchanged
- **v1 responses** include `Deprecation: true` and `Sunset` headers
- **v2 endpoints** are available for new development
- **No data migration** is required — both versions read from the same database

### 6.2 What Stays the Same

- **Authentication** — JWT Bearer tokens and API keys work identically in v2
- **Base domain** — `https://api.secondbrain-os.com` remains unchanged
- **Resource IDs** — IDs are consistent across versions (no ID migration needed)
- **Data model** — The underlying database schema does not change
- **Rate limits** — Same rate limiting policy applies to both versions

---

## 7. Testing the Migration

### 7.1 Test Plan

| Test | Description | Expected Result |
|---|---|---|
| **Endpoint reachability** | Call each v2 endpoint | HTTP 200 with valid response |
| **Response format** | Verify `items` + `pagination` structure | Matches v2 schema |
| **Error format** | Trigger 404, 400, 422 errors | Returns v2 error format |
| **Pagination** | Iterate through multiple pages | Cursor pagination works correctly |
| **Filtering** | Apply filters to list endpoints | Results match v1 equivalent |
| **Authentication** | Call v2 with JWT and API key | Both auth methods work |
| **Rate limiting** | Exceed rate limit on v2 | Returns 429 with v2 error format |
| **Deprecation headers** | Call v1 endpoint | Returns `Deprecation: true` + `Sunset` |

### 7.3 Response Comparison Script

```python
import httpx
import json

async def compare_responses(client, endpoint: str, params: dict = None):
    """Compare v1 and v2 responses for the same request."""
    v1_response = await client.get(f"/api/v1/{endpoint}", params=params)
    v2_response = await client.get(f"/api/v2/{endpoint}", params=params)

    v1_data = v1_response.json()
    v2_data = v2_response.json()

    comparison = {
        "endpoint": endpoint,
        "v1_status": v1_response.status_code,
        "v2_status": v2_response.status_code,
        "v1_keys": list(v1_data.keys()),
        "v2_keys": list(v2_data.keys()),
        "item_count_match": len(v1_data.get("data", [])) == len(v2_data.get("items", [])),
        "error_format_match": "error" in v2_data if v1_response.status_code >= 400 else True,
    }

    return comparison
```

---

## 8. Common Migration Issues

| Issue | Cause | Solution |
|---|---|---|
| **Response parsing fails** | Client expects `data` array but v2 returns `items` | Update response parsing to use `items` and `pagination` |
| **Error handling broken** | Client expects `detail` field but v2 nests under `error` | Update error handling to read `error.message` |
| **Pagination breaks** | Client uses `offset` but v2 uses cursor | Implement cursor tracking; see [Step 3](#step-3-update-pagination-logic) |
| **Missing fields** | Client relies on undocumented fields | Check v2 response schema; add fallbacks for missing fields |
| **Rate limit errors** | Client not handling `Retry-After` header | Add `Retry-After` parsing to rate limit handling |
| **Deprecation warnings** | Client ignores `Deprecation` header | Add monitoring for deprecation headers |
| **Custom headers** | Client sends v1-specific headers | Remove or update custom headers for v2 |

---

## 8. Rollback Plan

If issues are detected after migrating to v2, follow this rollback procedure:

### 8.1 Immediate Rollback (within 24 hours)

1. **Revert the base URL** from `/api/v2/` back to `/api/v1/`
2. **Restore response parsing** to the v1 format (`data` array, `limit`/`offset`)
3. **Restore error handling** to the v1 format (`detail` field)
4. **Verify** all endpoints return expected v1 responses
5. **Monitor** for 30 minutes to confirm stability

### 8.2 Rollback Script

```python
# Rollback configuration
ROLLBACK_CONFIG = {
    "base_url": "https://api.secondbrain-os.com",
    "api_version": "v1",  # Revert from v2 to v1
    "response_format": "data",  # Revert from items to data
    "pagination": "offset",  # Revert from cursor to offset
    "error_format": "flat",  # Revert from nested to flat
}

# Quick rollback verification
async def verify_rollback(client):
    """Verify v1 endpoints are still functional after rollback."""
    checks = [
        ("GET", "/api/v1/tasks/"),
        ("GET", "/api/v1/tasks/some_id"),
        ("POST", "/api/v1/tasks/", {"title": "Rollback test"}),
    ]

    for method, path, *body in checks:
        response = await client.request(method, path, json=body[0] if body else None)
        assert response.status_code in (200, 201), f"{method} {path} failed"
        assert "data" in response.json(), f"{path} missing 'data' field"

    print("Rollback verification passed — all v1 endpoints functional")
```

---

## 9. Common Migration Issues

| Issue | Cause | Solution |
|---|---|---|
| **`data` field missing** | Client parses v2 response with v1 parser | Update to use `items` instead of `data` |
| **`total` field missing** | Client expects `total` at root level | Read `pagination.total` instead |
| **Error parsing fails** | Client reads `detail` but v2 nests under `error` | Update to read `error.message` |
| **Pagination breaks** | Client uses `offset` parameter | Switch to `cursor` parameter |
| **Sort order reversed** | v2 uses `+`/`-` prefix instead of `sort`/`order` | Update sort parameter format |
| **Deprecation warnings** | Client ignores `Deprecation` header | Add monitoring for deprecation headers |
| **Custom error handling** | Client expects flat error structure | Update to read nested `error` object |

---

## 10. Related Documentation

| Document | Description |
|---|---|
| [API Integration Guide](../api-integration-guide.md) | General API usage, authentication, rate limits |
| [Versioning Strategy](../Versioning.md) | API version lifecycle, deprecation policy, backward compatibility |
| [API Changelog](changelog.md) | Version history, added/changed/deprecated endpoints |
| [Error Catalog](error-catalog.md) | Standardized error codes and recovery strategies |
| [Rate Limiting](rate-limiting.md) | API rate limit policies and configuration |
| [Webhook Guide](webhook-guide.md) | Real-time event notifications via webhooks |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-07-12 | Developer | Initial migration guide template — v1 to v2 breaking changes, migration steps, rollback plan |
