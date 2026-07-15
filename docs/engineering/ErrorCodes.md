# Error Code Catalog

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ENG-ERR-011 |
| **Version** | 1.0.0 |
| **Status** | Approved |
| **Date** | 2026-07-10 |
| **Classification** | Internal |
| **Owner** | Developer |

---

## 1. Executive Summary

Second Brain OS uses standardized error codes across all API responses to enable programmatic error handling by clients. Each error code maps to a specific HTTP status code, has a human-readable message template, and documents the root cause and suggested fix. This catalog defines 50+ error codes organized by category: authentication, validation, resource, AI, and system errors.

---

## 2. Purpose

Provide a comprehensive error code registry that enables API clients (frontend, mobile, AI agents) to programmatically handle errors without parsing human-readable messages.

---

## 3. Scope

This document covers:
- Error code format (`{COMPONENT}_{ERROR}`)
- Error categories (auth, validation, resource, AI, system)
- Complete error code registry with 50+ codes
- Each code: HTTP status, message template, cause, suggested fix
- Example error response JSON

Out of scope: REST conventions (see [REST.md](REST.md)), validation specifics (see [Validation.md](Validation.md)).

---

## 4. Business Context

Clients need to handle errors programmatically for toast messages, form validation, retry logic, and user notifications. Standardized error codes eliminate the need to parse error text and enable consistent handling across all frontend modules.

---

## 5. Functional Specification

### 5.1 Error Code Format

```
{COMPONENT}_{ERROR}
```

- `COMPONENT`: Uppercase component identifier (AUTH, TASK, VALIDATION, AI, SYSTEM, etc.)
- `ERROR`: Uppercase error description (NOT_FOUND, TIMEOUT, EXCEEDED, etc.)

### 5.2 Error Response Format

```json
{
  "detail": "Task not found",
  "error_code": "TASK_NOT_FOUND",
  "field_errors": [
    {
      "field": "task_id",
      "message": "No task found with ID 'abc-123'",
      "code": "resource_not_found"
    }
  ],
  "request_id": "req_abc123",
  "timestamp": "2026-07-10T12:00:00Z"
}
```

---

## 6. Non-Functional Requirements

| Requirement | Target | Measurement |
|---|---|---|
| Error response generation | < 5ms | Error handler timing |
| Error code uniqueness | No duplicates | CI validation |
| Error code coverage | Every HTTPException has a code | Lint rule |

---

## 7. Architecture

### 7.1 Error Categories

| Category | Prefix | Range | Description |
|---|---|---|---|
| Authentication | `AUTH_` | 1000-1099 | Token, session, permission errors |
| Validation | `VAL_` | 2000-2099 | Input validation, schema errors |
| Resource | `{MODULE}_` | 3000-3999 | Not found, conflict, duplicate |
| AI | `AI_` | 4000-4099 | Provider errors, quota, timeout |
| System | `SYS_` | 5000-5099 | Internal errors, rate limits, dependencies |
| Rate Limit | `RATE_` | 6000-6099 | Rate limiting errors |

---

## 8. Diagrams

### 8.1 Error Code Registry — Authentication (AUTH_*)

| Code | HTTP Status | Message Template | Cause | Suggested Fix |
|---|---|---|---|---|
| `AUTH_TOKEN_MISSING` | 401 | "No authentication token provided" | Request missing `Authorization: Bearer` header | Include valid Bearer token |
| `AUTH_TOKEN_EXPIRED` | 401 | "Authentication token has expired" | JWT token past its expiry time | Refresh token via auth flow |
| `AUTH_TOKEN_INVALID` | 401 | "Authentication token is invalid or malformed" | JWT decode failure | Obtain a new token |
| `AUTH_INSUFFICIENT_PERMISSIONS` | 403 | "Insufficient permissions for this operation" | Valid token but user lacks access | Request elevated access |
| `AUTH_SESSION_NOT_FOUND` | 401 | "No active session found" | User not logged in with Supabase | Redirect to login |
| `AUTH_OAUTH_FAILED` | 401 | "OAuth authentication failed" | Google OAuth consent denied or error | Try signing in again |
| `AUTH_ACCOUNT_DISABLED` | 403 | "Account has been disabled" | Admin disabled the account | Contact support |

### 8.2 Error Code Registry — Validation (VAL_*)

| Code | HTTP Status | Message Template | Cause | Suggested Fix |
|---|---|---|---|---|
| `VAL_REQUIRED_FIELD_MISSING` | 422 | "Required field '{field}' is missing" | POST body missing required field | Include all required fields |
| `VAL_FIELD_TOO_SHORT` | 422 | "Field '{field}' must be at least {min} characters" | String shorter than `min_length` | Lengthen the input |
| `VAL_FIELD_TOO_LONG` | 422 | "Field '{field}' must be at most {max} characters" | String exceeds `max_length` | Shorten the input |
| `VAL_INVALID_ENUM` | 422 | "Field '{field}' has invalid value '{value}'" | Value not in allowed enum set | Use one of allowed values |
| `VAL_INVALID_FORMAT` | 422 | "Field '{field}' has invalid format" | Email, UUID, URL regex mismatch | Fix the format |
| `VAL_NUMBER_OUT_OF_RANGE` | 422 | "Field '{field}' must be between {min} and {max}" | Number outside `ge`/`le` bounds | Adjust the value |
| `VAL_DATE_IN_PAST` | 422 | "Field '{field}' must be a future date" | Due date is in the past | Set a future date |
| `VAL_CROSS_FIELD` | 422 | "Cross-field validation failed: {message}" | `@model_validator` check failed | Review related fields |

### 8.3 Error Code Registry — Resource (per module)

| Code | HTTP Status | Message Template | Cause | Suggested Fix |
|---|---|---|---|---|
| `TASK_NOT_FOUND` | 404 | "Task not found" | Task ID doesn't exist or not owned by user | Verify task ID |
| `TASK_ALREADY_COMPLETED` | 409 | "Task is already completed" | Attempt to complete an already-completed task | Refresh and check status |
| `TASK_DEPENDENCY_NOT_MET` | 409 | "Dependency task '{title}' is not completed" | Required dependency is still open | Complete the dependency first |
| `COURSE_NOT_FOUND` | 404 | "Course not found" | Course ID doesn't exist | Verify course ID |
| `GOAL_NOT_FOUND` | 404 | "Goal not found" | Goal ID doesn't exist | Verify goal ID |
| `HABIT_NOT_FOUND` | 404 | "Habit not found" | Habit ID doesn't exist | Verify habit ID |
| `IDEA_NOT_FOUND` | 404 | "Idea not found" | Idea ID doesn't exist | Verify idea ID |
| `RESOURCE_NOT_FOUND` | 404 | "Resource not found" | Resource ID doesn't exist | Verify resource ID |
| `OPPORTUNITY_NOT_FOUND` | 404 | "Opportunity not found" | Opportunity ID doesn't exist | Verify opportunity ID |
| `PROJECT_NOT_FOUND` | 404 | "Project not found" | Project ID doesn't exist | Verify project ID |
| `SLEEP_LOG_NOT_FOUND` | 404 | "Sleep log not found" | Sleep log ID doesn't exist | Verify log ID |
| `TIME_ENTRY_NOT_FOUND` | 404 | "Time entry not found" | Time entry ID doesn't exist | Verify entry ID |
| `INCOME_ENTRY_NOT_FOUND` | 404 | "Income entry not found" | Income entry ID doesn't exist | Verify entry ID |
| `MEMORY_ENTRY_NOT_FOUND` | 404 | "Memory entry not found" | Memory entry ID doesn't exist | Verify entry ID |
| `FEEDBACK_NOT_FOUND` | 404 | "Feedback not found" | Feedback ID doesn't exist | Verify feedback ID |
| `NOTIFICATION_NOT_FOUND` | 404 | "Notification not found" | Notification ID doesn't exist | Verify notification ID |
| `VIDEO_NOT_FOUND` | 404 | "Video not found" | Video ID doesn't exist | Verify video ID |
| `ROADMAP_NOT_FOUND` | 404 | "Roadmap not found" | Roadmap ID doesn't exist | Verify roadmap ID |
| `DUPLICATE_RESOURCE` | 409 | "Resource with this identifier already exists" | Unique constraint violation | Use a different identifier |

### 8.4 Error Code Registry — AI (AI_*)

| Code | HTTP Status | Message Template | Cause | Suggested Fix |
|---|---|---|---|---|
| `AI_PROVIDER_UNAVAILABLE` | 503 | "AI service is currently unavailable" | Ollama or Claude API unreachable | Try again later |
| `AI_RATE_LIMIT_EXCEEDED` | 429 | "AI request rate limit exceeded" | Too many AI requests in time window | Wait and retry |
| `AI_QUOTA_EXCEEDED` | 429 | "AI API quota has been exceeded" | Monthly token budget exhausted | Wait for reset or upgrade plan |
| `AI_TIMEOUT` | 504 | "AI request timed out" | LLM took too long to respond | Retry with simpler query |
| `AI_INVALID_RESPONSE` | 500 | "AI returned an unexpected response" | LLM output couldn't be parsed | Retry the request |
| `AI_CIRCUIT_BREAKER_OPEN` | 503 | "AI circuit breaker is open" | Repeated AI failures triggered protection | Wait for cooldown period |
| `AI_CONTENT_FILTERED` | 422 | "Request content was filtered by safety guardrails" | Input triggered content policy | Rephrase the request |

### 8.5 Error Code Registry — System (SYS_* / RATE_*)

| Code | HTTP Status | Message Template | Cause | Suggested Fix |
|---|---|---|---|---|
| `SYS_INTERNAL_ERROR` | 500 | "An internal server error occurred" | Unhandled exception | Retry; contact support if persists |
| `SYS_DEPENDENCY_UNAVAILABLE` | 503 | "A required dependency is unavailable" | Supabase, Redis, or other service down | Try again later |
| `SYS_OPERATION_TIMEOUT` | 504 | "The operation timed out" | Request exceeded maximum duration | Retry with smaller scope |
| `SYS_MAINTENANCE_MODE` | 503 | "System is under maintenance" | Scheduled downtime | Wait for maintenance window |
| `SYS_FEATURE_DISABLED` | 403 | "This feature is currently disabled" | Feature flag turned off | Enable feature flag |
| `SYS_INVALID_REQUEST_ID` | 400 | "Invalid request ID format" | Request ID in header is malformed | Remove or fix request ID |
| `RATE_LIMIT_EXCEEDED` | 429 | "Rate limit exceeded. Max {limit} req/{window}s" | Too many requests in time window | Wait for rate limit reset |
| `RATE_LIMIT_GLOBAL` | 429 | "Global rate limit exceeded" | Per-IP limit exhausted | Wait and retry |
| `RATE_LIMIT_ENDPOINT` | 429 | "Endpoint rate limit exceeded. Max {limit} req/{window}s" | Per-endpoint limit hit | Wait and retry |

---

## 9. Data Models

### 9.1 Error Response Schema

```json
{
  "detail": "Human-readable error message",
  "error_code": "TASK_NOT_FOUND",
  "field_errors": [
    { "field": "task_id", "message": "No task found", "code": "resource_not_found" }
  ],
  "request_id": "req_uuid",
  "timestamp": "2026-07-10T12:00:00Z"
}
```

---

## 10. APIs

### 10.1 Programmatic Error Handling (Frontend)

```typescript
// apps/web/lib/api-client.ts
async function handleApiError(response: Response) {
  const body = await response.json()
  switch (body.error_code) {
    case 'AUTH_TOKEN_EXPIRED':
      await refreshAuthToken()
      return retryRequest()
    case 'RATE_LIMIT_EXCEEDED':
      const retryAfter = response.headers.get('Retry-After')
      await sleep(Number(retryAfter) * 1000)
      return retryRequest()
    case 'AI_PROVIDER_UNAVAILABLE':
      toast.warning('AI is temporarily unavailable. Using offline mode.')
      return fallbackResponse()
    default:
      toast.error(body.detail)
      throw new ApiError(body.error_code, body.detail)
  }
}
```

---

## 11. Security

| Concern | Implementation |
|---|---|
| Internal details leakage | 500 errors never expose stack traces |
| Error code enumeration | Generic messages for auth failures |
| Rate limit info disclosure | Headers added for legitimate clients |

---

## 12. Performance Targets

| Metric | Target |
|---|---|
| Error response generation | < 5ms |
| Error code lookup | < 1ms (dict lookup) |
| Error response size | < 500 bytes |

---

## 13. Edge Cases

| Edge Case | Handling |
|---|---|
| Multiple validation errors | All errors returned in `field_errors` array |
| Unknown error code | Fall back to `SYS_INTERNAL_ERROR` |
| Error code in non-error response | Not included (only on 4xx/5xx) |

---

## 14. Failure Scenarios

| Scenario | Impact | Recovery |
|---|---|---|
| Error handler itself throws | Returns generic 500 | Global exception handler catches |
| Error code not found in registry | Fall back to `SYS_INTERNAL_ERROR` | Log missing code for developer |

---

## 15. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Error code drift (code doesn't match registry) | Low | Medium | CI validation checks codes are used |
| Missing error codes for new modules | Medium | Low | Code review checklist includes error codes |

---

## 16. Acceptance Criteria

- [ ] Every `HTTPException` includes an `error_code` field
- [ ] Error responses always include `detail`, `error_code`, `request_id`, `timestamp`
- [ ] Validation errors include `field_errors` array
- [ ] Error codes follow `{COMPONENT}_{ERROR}` format
- [ ] Error code registry is maintained alongside code

---

## 17. Traceability

| Requirement ID | Source | Implementation |
|---|---|---|
| ERR-01 | UX-003 (Error clarity) | Standardized error codes |
| ERR-02 | DEV-001 (Debugging) | `request_id` for log correlation |
| ERR-03 | SEC-008 (Info leakage) | Sanitized error messages |

---

## 18. Implementation Notes

1. Error codes are Python constants in `packages/shared/utils/error_codes.py`
2. Each `HTTPException` includes `headers={"X-Error-Code": "TASK_NOT_FOUND"}`
3. Pydantic validation errors auto-map to `VAL_*` codes
4. New modules add their own `{MODULE}_NOT_FOUND` / `{MODULE}_CONFLICT` codes

---

## 19. Testing Strategy

| Test Type | Coverage | Tools |
|---|---|---|
| Error code tests | Every `HTTPException` has valid code | pytest |
| Response format tests | JSON matches error envelope schema | pytest + jsonschema |
| Frontend handling tests | Every code handled in API client | jest |

---

## 20. References

| Reference | Document |
|---|---|
| REST API Conventions | [REST.md](REST.md) |
| Validation Architecture | [Validation.md](Validation.md) |
| Rate Limiting | [RateLimiting.md](RateLimiting.md) |
| Controller Layer | [Controllers.md](Controllers.md) |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-07-10 | Developer | Initial error code catalog |
