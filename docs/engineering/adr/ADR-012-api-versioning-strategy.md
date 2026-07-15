## Document Control

| Field | Value |
|---|---|
| Document ID | ENG-ADR12-001 |
| Version | 1.0.0 |
| Status | Accepted |
| Last Updated | 2026-07-11 |

# ADR-012: API Versioning Strategy

## Document Control

| Field | Value |
|---|---|
| ADR Number | 012 |
| Status | Accepted |
| Date | 2026-07-10 |
| Deciders | Developer |
| Replaces | None |
| Superseded By | None |
| Category | API Architecture |

---

## 1. Title

API Versioning Strategy â€” URL-Based Versioning with Deprecation Headers

---

## 2. Context

Second Brain OS has 31 API routers with ~120 endpoints. As the application evolves, breaking changes to the API are inevitable â€” new required fields, changed response formats, renamed endpoints. A versioning strategy is needed to:

1. Allow evolution without breaking existing clients
2. Communicate deprecation timelines clearly
3. Maintain backward compatibility for a reasonable period
4. Keep the versioning mechanism simple for a single-developer project

---

## 3. Decision

Adopt **URL-based versioning** with the prefix `/api/v{N}/`:

```
https://api.secondbrain-os.com/api/v1/tasks
https://api.secondbrain-os.com/api/v1/goals
```

Combined with:
- **Deprecation header** on endpoints scheduled for removal
- **Sunset header** indicating when the endpoint will be removed
- **Semantic versioning** for the API itself (independent of application version)

---

## 4. Detailed Design

### 4.1 URL Structure

```
/api/v{version}/{resource}[/{id}][?{query_params}]
```

| Part | Example | Description |
|---|---|---|
| `/api` | `/api` | Fixed prefix |
| `/v1` | `/v1` | Version number |
| `/tasks` | `/tasks` | Resource name |
| `/{id}` | `/abc-123` | Resource ID |
| `?limit=20` | `?limit=20` | Query parameters |

### 4.2 Current Version

| Version | Status | Release Date | Sunset Date |
|---|---|---|---|
| v1 | âœ… Active | 2026-06-01 | TBD |

### 4.3 Version Routes

```python
# apps/api/app/api/tasks.py
router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

@router.get("/")
async def list_tasks(user_id: str = Depends(get_current_user)):
    ...

@router.post("/", status_code=201)
async def create_task(task: TaskCreate, user_id: str = Depends(get_current_user)):
    ...
```

### 4.4 Deprecation Headers

```python
from fastapi.responses import Response

@router.get("/")
async def deprecated_endpoint():
    response = Response(
        content=json.dumps({"data": [...]}),
        headers={
            "Deprecation": "true",
            "Sunset": "Sat, 01 Jan 2027 00:00:00 GMT",
            "Link": "</api/v2/tasks>; rel=\"successor-version\"",
        }
    )
    return response
```

---

## 5. Alternatives Considered

### Alternative 1: Header-Based Versioning

**Approach:** Version via `Accept: application/vnd.sb.v2+json` header.

**Pros:** Clean URLs, no URL duplication
**Cons:** Hard to test in browser, not visible in logs, REST purist
**Decision:** Rejected â€” URL versioning is more visible and debuggable

### Alternative 2: Query Parameter Versioning

**Approach:** `/api/tasks?v=2`

**Pros:** Simple, one URL for all versions
**Cons:** Easy to forget parameter, caching issues, not standard
**Decision:** Rejected â€” URL prefix is the industry standard

### Alternative 3: No Versioning

**Approach:** Always backward compatible, never break API.

**Pros:** Simplest implementation
**Cons:** Impossible for long-lived APIs, accumulates technical debt
**Decision:** Rejected â€” a versioning strategy is needed for long-term maintenance

---

## 6. Version Lifecycle

### 6.1 Version States

| State | Description | Duration |
|---|---|---|
| **Active** | Default version, all features work | Indefinite |
| **Deprecated** | Still functional, headers warn of removal | 6 months minimum |
| **Sunset** | Scheduled for removal, active migration | 3 months |
| **Removed** | No longer available | â€” |

### 6.2 Deprecation Process

```
1. New version (v{N+1}) released
2. Old version (v{N}) marked deprecated with header
3. 6 month migration window
4. Sunset header set 3 months before removal
5. Old version removed after sunset date
```

---

## 7. Consequences

### Positive

| Benefit | Description |
|---|---|
| **Clear versioning** | Version visible in URL, logs, and docs |
| **Backward compatible** | Old clients continue working |
| **Orderly migration** | 6-month deprecation window |
| **Simple to implement** | URL prefix in FastAPI `APIRouter` |
| **Industry standard** | Familiar to API consumers |

### Negative

| Cost | Mitigation |
|---|---|
| **URL duplication** | Shared business logic between versions |
| **Code maintenance** | Version-specific route handlers |
| **Documentation overhead** | Multiple versions in Swagger/Redoc |
| **Rarely needed for single-user** | May never need v2 â€” but prepared |

---

## 8. Version Maintenance Guidelines

### 8.1 When to Create a New Version

| Reason | Example |
|---|---|
| Breaking response format change | Field renamed, removed, or type changed |
| Breaking request format change | Required field added |
| Behavior change | Different semantics for same input |
| Removed functionality | Endpoint deleted |

### 8.2 When NOT to Create a New Version

| Reason | Example |
|---|---|
| Adding a new field to response | New optional field |
| Adding a new endpoint | New resource |
| Bug fix | Same behavior, different result |
| Performance improvement | Faster, same output |

---

## 9. Performance Targets

| Metric | Target |
|---|---|
| Version routing overhead | < 1ms (negligible) |
| v1 â†’ v2 migration effort | < 2 hours (single developer) |
| Minimum deprecation window | 6 months |
| Maximum active versions | 2 (current + previous) |

---

## 10. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Never needing v2 (over-engineering) | High | Low | Simple implementation, minimal overhead |
| Forgetting to add deprecation headers | Medium | Low | Code review checklist item |
| Breaking change without version bump | Low | Medium | CI check for API contract changes |

---

## 11. Related Decisions

| ADR | Relation |
|---|---|
| ADR-001: Monorepo Structure | API in `apps/api/` |
| ADR-003: Database Choice | Supabase queries versioned via API |
| ADR-006: Error Handling | Error schemas versioned per endpoint |

---

## 12. References

| Reference | Link |
|---|---|
| FastAPI Versioning | https://fastapi.tiangolo.com/tutorial/path-params/ |
| Deprecation Header | RFC 8594 |
| Sunset Header | RFC 8594 |
| Implementation | `apps/api/app/api/*.py` (31 routers) |
