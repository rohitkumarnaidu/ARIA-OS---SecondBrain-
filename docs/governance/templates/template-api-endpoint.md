---
category: template
type: api
version: 1.0.0
status: active
---

# [Resource Name] API Reference

## Document Control

| Field | Value |
|---|---|
| Document ID | GOV-TAE-001 |
| Version | 1.0.0 |
| Status | Draft |
| Last Updated | [YYYY-MM-DD] |

---

## Overview

[Brief description of this API endpoint group: what resource it manages, its business purpose, and which clients consume it.]

## Base URL

```
/api/v1/[resource]
```

## Authentication

[Describe auth method: JWT Bearer token, API key, session cookie, etc.]

**Required headers:**
| Header | Value | Required |
|---|---|---|
| `Authorization` | `Bearer <token>` | Yes |
| [Other header] | [Value] | [Yes/No] |

## Endpoints

### `GET /` â€” List [Resources]

Retrieves a paginated list of [resources] with optional filtering.

**Query Parameters:**

| Parameter | Type | Required | Default | Validation | Description |
|---|---|---|---|---|---|
| `limit` | integer | No | 20 | 1â€“100 | Maximum number of results |
| `offset` | integer | No | 0 | >= 0 | Pagination offset |
| [filter_name] | [type] | No | â€” | [validation rules] | [Filter description] |
| [sort_by] | string | No | `created_at` | [valid values] | Sort field |
| [order] | string | No | `desc` | `asc` / `desc` | Sort direction |

**Example Request:**

```bash
curl -H "Authorization: Bearer <token>" \
  "https://api.example.com/api/v1/[resource]?limit=10&offset=0"
```

**Response 200:**

```json
{
  "data": [
    {
      "id": "uuid",
      "field1": "value1",
      "field2": "value2",
      "created_at": "2026-07-11T12:00:00Z",
      "updated_at": "2026-07-11T12:00:00Z"
    }
  ],
  "limit": 10,
  "offset": 0,
  "total": 42
}
```

### `POST /` â€” Create [Resource]

Creates a new [resource].

**Request Body:**

```json
{
  "field1": "string (required) â€” description",
  "field2": "number (optional) â€” description, defaults to 0",
  "field3": {
    "nested_field": "string (optional)"
  }
}
```

**Response 201:**

Returns the created resource with its generated `id` and timestamps.

```json
{
  "id": "uuid",
  "field1": "string",
  "field2": 0,
  "created_at": "2026-07-11T12:00:00Z",
  "updated_at": "2026-07-11T12:00:00Z"
}
```

### `GET /{id}` â€” Get [Resource]

Retrieves a single [resource] by ID.

**Path Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | uuid | Yes | Resource unique identifier |

**Response 200:**

```json
{
  "id": "uuid",
  "field1": "value",
  ...
}
```

**Error Codes:**

| Code | Message | When |
|---|---|---|
| 404 | `[RESOURCE]_NOT_FOUND` | Resource with given ID does not exist |
| 403 | `FORBIDDEN` | User does not own this resource |

### `PUT /{id}` â€” Update [Resource]

Updates an existing [resource]. Performs a full or partial update.

**Path Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | uuid | Yes | Resource unique identifier |

**Request Body:**

```json
{
  "field1": "updated value (optional)",
  "field2": 42
}
```

**Response 200:**

Returns the updated resource.

### `DELETE /{id}` â€” Delete [Resource]

Deletes a [resource] by ID.

**Path Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | uuid | Yes | Resource unique identifier |

**Response 204:**

No content. Resource is deleted.

## Error Response Schema

All errors follow a standard format:

```json
{
  "detail": "Human-readable error message",
  "error_code": "ERROR_CODE",
  "request_id": "uuid",
  "timestamp": "2026-07-11T12:00:00Z"
}
```

### Common Error Codes

| Code | Status | Description |
|---|---|---|
| `[RESOURCE]_NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 422 | Input validation failed |
| `UNAUTHORIZED` | 401 | Missing or invalid auth |
| `FORBIDDEN` | 403 | Authenticated but not authorized |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

## Rate Limiting

| Limit | Window | Scope |
|---|---|---|
| [X] requests | [Y] seconds | Per user / per IP |
| [Z] requests | [W] seconds | Per endpoint (if different) |

**Headers:**
| Header | Description |
|---|---|
| `X-RateLimit-Limit` | Max requests per window |
| `X-RateLimit-Remaining` | Remaining requests |
| `X-RateLimit-Reset` | Unix timestamp when limit resets |

## Versioning

| Header | Value | Description |
|---|---|---|
| `Deprecation` | `true` | Present if endpoint is deprecated |
| `Sunset` | RFC 1123 date | When endpoint will be removed |

See [API Versioning Strategy](../../engineering/adr/ADR-012-api-versioning-strategy.md) for full deprecation policy.

## Related Endpoints

- [Link to related endpoint doc](#) â€” [Description of relationship]

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | YYYY-MM-DD | [Author] | Initial API reference for [resource] |
