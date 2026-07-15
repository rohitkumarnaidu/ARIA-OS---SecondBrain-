# Webhook Integration Guide — Second Brain OS API

> **External developer reference for receiving real-time event notifications from ARIA OS via webhooks**

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ENG-WHK-001 |
| **Version** | 1.0.0 |
| **Status** | Draft (Design Intent) |
| **Date** | 2026-07-12 |
| **Classification** | External |
| **Owner** | Developer |
| **Review Cycle** | Monthly |
| **Related Docs** | [API Integration Guide](../api-integration-guide.md), [Error Catalog](error-catalog.md), [Rate Limiting](rate-limiting.md), [Webhook Architecture](../Webhooks.md) |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Event Types](#2-event-types)
3. [Webhook Payload Format](#3-webhook-payload-format)
4. [Delivery Mechanism](#4-delivery-mechanism)
5. [Retry Policy](#5-retry-policy)
6. [Signature Verification](#6-signature-verification)
7. [Registering a Webhook](#7-registering-a-webhook)
8. [Best Practices](#8-best-practices)
9. [Common Errors & Troubleshooting](#9-common-errors--troubleshooting)
10. [Rate Limits](#10-rate-limits)
11. [Security Considerations](#11-security-considerations)
12. [Related Documentation](#12-related-documentation)

---

## 1. Introduction

Webhooks enable external services to receive **real-time event notifications** from ARIA OS without polling. When an event occurs (e.g., a task is completed, a briefing is generated), ARIA OS sends an HTTP POST request to a URL you register.

### Use Cases in ARIA OS

| Use Case | Example |
|---|---|
| **Slack/Teams notifications** | Post "Task completed" message to a channel |
| **Notion/Linear sync** | Create/update records when tasks change |
| **Zapier/Make automation** | Trigger multi-step workflows |
| **Custom dashboards** | Feed events into a real-time dashboard |
| **CI/CD pipelines** | Trigger builds when milestones are reached |
| **Analytics pipelines** | Stream events to data warehouse |

---

## 2. Event Types

Webhooks are triggered by specific events across ARIA OS modules. Each event type has a unique identifier and a typed payload.

### 2.1 Task Events

| Event | Trigger | Payload Highlights |
|---|---|---|
| `task.created` | New task created via API or UI | `id`, `title`, `priority`, `due_date`, `category` |
| `task.updated` | Task properties modified | `id`, `changes` (diff of modified fields) |
| `task.completed` | Task marked complete | `id`, `title`, `completed_at`, `category` |
| `task.deleted` | Task removed | `id`, `title` (for reference) |

### 2.2 Habit Events

| Event | Trigger | Payload Highlights |
|---|---|---|
| `habit.completed` | Habit logged for the day | `habit_id`, `title`, `current_streak`, `date` |
| `habit.streak_broken` | Streak reset due to missed day | `habit_id`, `title`, `previous_streak`, `missed_date` |

### 2.3 Briefing & Review Events

| Event | Trigger | Payload Highlights |
|---|---|---|
| `briefing.generated` | Daily briefing created by A09 | `briefing_id`, `date`, `focus_area`, `task_count` |
| `review.generated` | Weekly review created by A10 | `review_id`, `week_start`, `week_end`, `completion_rate` |

### 2.4 Opportunity Events

| Event | Trigger | Payload Highlights |
|---|---|---|
| `opportunity.found` | New opportunity matched by A06/A15 | `opportunity_id`, `title`, `match_score`, `deadline` |

### 2.5 Event Type Reference

| Field | Description |
|---|---|
| **Event ID format** | `{domain}.{action}` — e.g., `task.completed`, `habit.streak_broken` |
| **Versioning** | Event types are versioned implicitly by the `webhook_version` field in the payload |
| **Idempotency** | Each event delivery carries a unique `event_id` for deduplication |

---

## 3. Webhook Payload Format

Every webhook delivery uses a standardized JSON envelope:

```json
{
  "id": "evt_abc123def456",
  "type": "task.completed",
  "created_at": "2026-07-11T12:00:00Z",
  "webhook_version": "1.0",
  "data": {
    "task_id": "uuid",
    "title": "Complete project proposal",
    "category": "work",
    "completed_at": "2026-07-11T12:00:00Z"
  }
}
```

### Payload Schema

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | `string` | ✅ | Unique event identifier (`evt_` prefix + UUID) |
| `type` | `string` | ✅ | Event type (e.g., `task.completed`) |
| `created_at` | `string` (ISO 8601) | ✅ | UTC timestamp of event creation |
| `webhook_version` | `string` | ✅ | Webhook payload schema version (`1.0`) |
| `data` | `object` | ✅ | Event-specific payload (varies by event type) |

### Per-Event Data Schemas

**task.created / task.updated / task.completed:**
```json
{
  "data": {
    "id": "task_uuid",
    "title": "Complete project proposal",
    "status": "completed",
    "priority": "high",
    "category": "work",
    "due_date": "2026-07-15T17:00:00Z",
    "completed_at": "2026-07-11T12:00:00Z"
  }
}
```

**habit.completed / habit.streak_broken:**
```json
{
  "data": {
    "habit_id": "uuid",
    "title": "Morning meditation",
    "current_streak": 14,
    "previous_streak": 14,
    "date": "2026-07-11",
    "missed_date": "2026-07-11"
  }
}
```

**briefing.generated:**
```json
{
  "data": {
    "briefing_id": "uuid",
    "date": "2026-07-11",
    "focus_area": "Study",
    "task_count": 5,
    "summary": "Focus on completing the React module and reviewing PRs."
  }
}
```

**review.generated:**
```json
{
  "data": {
    "review_id": "uuid",
    "week_start": "2026-07-06",
    "week_end": "2026-07-12",
    "completion_rate": 0.78,
    "task_count": 14,
    "summary": "Good week overall. Focus on maintaining study streak."
  }
}
```

**opportunity.found:**
```json
{
  "data": {
    "opportunity_id": "uuid",
    "title": "Summer Internship - Backend Engineer",
    "match_score": 0.85,
    "deadline": "2026-08-01T23:59:00Z",
    "source": "linkedin",
    "url": "https://linkedin.com/jobs/view/123"
  }
}
```

---

## 3. Delivery Mechanism

Webhooks are delivered via **HTTP POST** to the URL you register. Each delivery includes standard headers and a JSON body.

### Request Headers

| Header | Description | Example |
|---|---|---|
| `Content-Type` | Always `application/json` | `application/json` |
| `X-Webhook-ID` | Unique webhook registration identifier | `wh_abc123` |
| `X-Webhook-Event` | Event type being delivered | `task.completed` |
| `X-Webhook-Signature` | HMAC-SHA256 signature for verification | `sha256=abc123...` |
| `X-Webhook-Timestamp` | ISO 8601 timestamp of delivery attempt | `2026-07-11T12:00:00Z` |
| `X-Webhook-Attempt` | Delivery attempt number (1-based) | `1` |
| `User-Agent` | Always `ARIA-OS-Webhook/1.0` | `ARIA-OS-Webhook/1.0` |

### Delivery Timeout

The webhook engine expects a response within **10 seconds**. If the target URL does not respond within this window, the delivery is treated as a failure and queued for retry.

---

### 4.2 Webhook Delivery Sequence

`mermaid
sequenceDiagram
    participant Ext as External Service
    participant ARIA as ARIA OS
    participant DB as Supabase DB
    participant Q as Retry Queue

    Ext->>ARIA: POST /api/v1/webhooks/register
    ARIA->>DB: Store webhook config + secret
    ARIA-->>Ext: 201 Created (webhook_id)

    Note over ARIA,Q: When event occurs...

    ARIA->>ARIA: Build event payload
    ARIA->>ARIA: Sign payload (HMAC-SHA256)
    ARIA->>Ext: POST to callback_url
    Note right of Ext: Headers: X-Signature, X-Event-Type
    
    alt Delivery successful
        Ext-->>ARIA: 200 OK
        ARIA->>DB: Mark delivery successful
    else Delivery failed (4xx/5xx)
        Ext-->>ARIA: Error response
        ARIA->>Q: Enqueue for retry
        Q->>Ext: Retry 1 (5s delay)
        Q->>Ext: Retry 2 (30s delay)
        Q->>Ext: Retry 3 (5min delay)
        alt All retries exhausted
            Q->>DB: Mark delivery failed
            ARIA->>Ext: Dead letter notification
        end
    end

    Note over Ext,Q: Max 3 retries · Exponential backoff · 24h TTL
`

### 4.2 Webhook Delivery Sequence

`mermaid
sequenceDiagram
    participant Ext as External Service
    participant ARIA as ARIA OS
    participant DB as Supabase DB
    participant Q as Retry Queue

    Ext->>ARIA: POST /api/v1/webhooks/register
    ARIA->>DB: Store webhook config + secret
    ARIA-->>Ext: 201 Created (webhook_id)

    Note over ARIA,Q: When event occurs...

    ARIA->>ARIA: Build event payload
    ARIA->>ARIA: Sign payload (HMAC-SHA256)
    ARIA->>Ext: POST to callback_url
    Note right of Ext: Headers: X-Signature, X-Event-Type
    
    alt Delivery successful
        Ext-->>ARIA: 200 OK
        ARIA->>DB: Mark delivery successful
    else Delivery failed (4xx/5xx)
        Ext-->>ARIA: Error response
        ARIA->>Q: Enqueue for retry
        Q->>Ext: Retry 1 (5s delay)
        Q->>Ext: Retry 2 (30s delay)
        Q->>Ext: Retry 3 (5min delay)
        alt All retries exhausted
            Q->>DB: Mark delivery failed
            ARIA->>Ext: Dead letter notification
        end
    end

    Note over Ext,Q: Max 3 retries . Exponential backoff . 24h TTL
`

## 5. Retry Policy

If a webhook delivery fails (timeout, network error, or non-2xx response), the system retries with exponential backoff:

| Attempt | Delay | Cumulative Wait |
|---|---|---|
| 1 | 0s (immediate) | 0s |
| 2 | 1 min | 1 min |
| 3 | 5 min | 6 min |
| 4 | 15 min | 21 min |
| 5 | 1 hr | 1 hr 21 min |
| 6 (final) | 6 hr | 7 hr 21 min |

After the final retry fails, the webhook endpoint is **automatically disabled** and the webhook owner is notified via email and in-app notification.

### Retry Decision Matrix

| HTTP Status | Retry? | Reason |
|---|---|---|
| `2xx` | No | Success |
| `3xx` | No | Redirect — follow redirects automatically |
| `400 Bad Request` | No | Client error — fix webhook handler |
| `401 Unauthorized` | No | Auth issue — check webhook handler |
| `404 Not Found` | No | URL changed — update webhook registration |
| `408 Request Timeout` | Yes | Transient network issue |
| `429 Too Many Requests` | Yes | Target rate limited — back off |
| `5xx Server Error` | Yes | Transient server issue |
| Connection timeout | Yes | Network issue |
| DNS resolution failure | Yes | Temporary DNS issue |

---

## 6. Signature Verification

Every webhook payload is signed with **HMAC-SHA256** using the secret associated with your webhook registration. Always verify the signature before processing the payload.

### Verifying the Signature

**Python:**
```python
import hmac
import hashlib
import json
from datetime import datetime, timezone

def verify_webhook_signature(
    payload: bytes,
    signature_header: str,
    timestamp_header: str,
    secret: str,
    max_age_seconds: int = 300,
) -> bool:
    # 1. Check timestamp freshness (prevent replay attacks)
    timestamp = datetime.fromisoformat(timestamp_header.replace("Z", "+00:00"))
    age = (datetime.now(timezone.utc) - timestamp).total_seconds()
    if age > max_age_seconds:
        return False  # Replay attack or stale delivery

    # 2. Reconstruct signed message
    message = f"{timestamp_header}.{payload.decode('utf-8')}"

    # 3. Compute expected signature
    expected = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()

    # 4. Constant-time comparison
    received = signature_header.replace("sha256=", "")
    return hmac.compare_digest(expected, received)
```

**TypeScript:**
```typescript
import { createHmac, timingSafeEqual } from "crypto";

function verifyWebhookSignature(
  payload: string,
  signatureHeader: string,
  timestampHeader: string,
  secret: string,
  maxAgeSeconds: number = 300
): boolean {
  // 1. Check timestamp freshness
  const timestamp = new Date(timestampHeader).getTime();
  const age = (Date.now() - timestamp) / 1000;
  if (age > maxAgeSeconds) return false;

  // 2. Reconstruct signed message
  const message = `${timestampHeader}.${payload}`;

  // 3. Compute expected signature
  const expected = crypto
    .createHmac("sha256", secret)
    .update(message)
    .digest("hex");

  // 4. Extract received signature
  const received = signatureHeader.replace("sha256=", "");

  // 5. Constant-time comparison
  return crypto.timingSafeEqual(
    Buffer.from(expected),
    Buffer.from(received)
  );
```

---

## 7. Registering a Webhook

### 7.1 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/webhooks` | Register a new webhook |
| `GET` | `/api/v1/webhooks` | List all registered webhooks |
| `GET` | `/api/v1/webhooks/{id}` | Get webhook details |
| `PUT` | `/api/v1/webhooks/{id}` | Update webhook URL, events, or secret |
| `DELETE` | `/api/v1/webhooks/{id}` | Delete a webhook |
| `POST` | `/api/v1/webhooks/{id}/test` | Send a test `ping` event |
| `GET` | `/api/v1/webhooks/{id}/deliveries` | View delivery history |

### 7.2 Registering a Webhook

```http
POST /api/v1/webhooks HTTP/1.1
Host: api.secondbrain-os.com
Content-Type: application/json
Authorization: Bearer eyJ_access_token...

{
  "url": "https://myservice.example.com/webhooks/aria",
  "events": [
    "task.created",
    "task.completed",
    "briefing.generated",
    "opportunity.found"
  ],
  "description": "Sync tasks to Notion database"
}
```

**Response (201 Created):**
```json
{
  "id": "wh_abc123def456",
  "url": "https://myservice.example.com/webhooks/aria",
  "events": ["task.created", "task.completed", "briefing.generated", "opportunity.found"],
  "status": "active",
  "secret": "whsec_abc123def456...",
  "description": "Sync tasks to Notion database",
  "created_at": "2026-07-11T12:00:00Z"
}
```

> **Important:** The `secret` is shown only once at creation. Store it securely. ARIA OS cannot recover a lost secret.

### 7.3 Testing a Webhook

```http
POST /api/v1/webhooks/{id}/test HTTP/1.1
Host: api.secondbrain-os.com
Authorization: Bearer eyJ_access_token...
```

The test endpoint sends a `ping` event to verify your endpoint is reachable and signature verification works:

```json
{
  "id": "evt_ping_abc123",
  "type": "ping",
  "created_at": "2026-07-11T12:00:00Z",
  "webhook_version": "1.0",
  "data": {
    "message": "This is a test webhook from ARIA OS",
    "webhook_id": "wh_abc123"
  }
}
```

### 7.4 Viewing Delivery History

```http
GET /api/v1/webhooks/{id}/deliveries?limit=10&offset=0 HTTP/1.1
Authorization: Bearer eyJ_access_token...
```

**Response:**
```json
{
  "data": [
    {
      "id": "del_abc123",
      "event_id": "evt_def456",
      "event_type": "task.completed",
      "status": "success",
      "status_code": 200,
      "attempt": 1,
      "created_at": "2026-07-11T12:00:00Z",
      "completed_at": "2026-07-11T12:00:01Z"
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

---

## 8. Best Practices

### 8.1 Idempotency Keys

Each webhook delivery includes a unique `event_id`. Use it to deduplicate deliveries:

```python
# Track processed event IDs to handle duplicate deliveries
processed_events = set()  # Use persistent storage in production

async def handle_webhook(request):
    event_id = request.json()["id"]
    if event_id in processed_events:
        return {"status": "duplicate"}, 200  # Acknowledge silently
    processed_events.add(event_id)
    # Process the event...
```

### 8.2 Verify the Signature

Always verify the HMAC-SHA256 signature before processing the payload. See [Section 6](#6-signature-verification) for code examples.

### 8.3 Respond Quickly

Your webhook endpoint should respond within **5 seconds**. The webhook engine has a 10-second timeout. If your processing takes longer:

1. Acknowledge the webhook immediately with `HTTP 200`
2. Process the event asynchronously in a background job
3. Use the `event_id` for idempotency

```python
# FastAPI example — acknowledge immediately, process later
@app.post("/webhooks/aria")
async def handle_aria_webhook(payload: dict):
    event_id = payload["id"]
    if event_id in processed_cache:
        return {"status": "duplicate"}

    # Acknowledge immediately
    asyncio.create_task(process_event_async(payload))

    return {"status": "accepted"}
```

### 8.4 Use a Dead Letter Queue

For events that fail after all retries, implement a dead letter queue (DLQ) for manual inspection:

```python
# Server-side: ARIA OS automatically logs failed deliveries
# Client-side: Log failed events for manual replay
import logging

logger = logging.getLogger("webhook_consumer")

async def handle_webhook(payload: dict):
    try:
        # Process the event
        await process_event(payload)
    except Exception as e:
        logger.error(
            "Webhook processing failed",
            extra={
                "event_id": payload["id"],
                "event_type": payload["type"],
                "error": str(e),
            },
        )
        # Store in dead letter queue for manual inspection
        await dead_letter_queue.store(payload)
        raise  # Return 500 so ARIA OS retries
```

### 8.5 Monitor Delivery Health

Track these metrics for your webhook integration:

| Metric | What to Monitor | Alert Threshold |
|---|---|---|
| Delivery success rate | % of 2xx responses | < 95% |
| Average response time | Time to process webhook | > 3s |
| Signature failures | HMAC mismatch count | > 0 |
| Duplicate events | Events with same `event_id` | > 1% of total |

---

## 9. Common Errors & Troubleshooting

| Error | HTTP Status | Likely Cause | Solution |
|---|---|---|---|
| `WEBHOOK_INVALID_URL` | 400 | URL is malformed or points to private IP | Use a publicly accessible HTTPS URL |
| `WEBHOOK_INVALID_EVENT` | 400 | Event type not recognized | Check event types in [Section 2](#2-event-types) |
| `WEBHOOK_NOT_FOUND` | 404 | Webhook ID does not exist | Verify the webhook ID |
| `WEBHOOK_DISABLED` | 400 | Webhook auto-disabled after failures | Re-enable via dashboard or recreate |
| `WEBHOOK_LIMIT_REACHED` | 400 | Max webhooks per user reached | Delete unused webhooks first |
| `SIGNATURE_MISMATCH` | 401 | HMAC signature does not match | Verify secret and payload encoding |
| `TIMESTAMP_EXPIRED` | 401 | Delivery timestamp is too old | Check system clock synchronization |
| `DELIVERY_FAILED` | 502 | Target URL unreachable or returned error | Check endpoint availability and logs |

### Troubleshooting Checklist

1. **Webhook not firing?** Verify the webhook is `active` and subscribed to the correct event type
2. **Signature mismatch?** Ensure you're using the raw request body (not parsed/re-serialized JSON)
3. **Deliveries failing?** Check the delivery history at `GET /api/v1/webhooks/{id}/deliveries`
4. **Receiving duplicates?** Use the `event_id` field for idempotent processing
5. **Slow responses?** Ensure your endpoint responds within 5 seconds; defer heavy processing
6. **Secret lost?** Delete and recreate the webhook — secrets are shown only once

---

## 10. Rate Limits

| Limit | Value | Scope |
|---|---|---|
| Max webhooks per user | 100 | Per authenticated user |
| Max retries per event | 5 | Per event delivery |
| Max delivery attempts | 6 (1 initial + 5 retries) | Per event |
| Delivery timeout | 10 seconds | Per HTTP POST attempt |
| Max payload size | 64 KB | Per delivery |
| Max events per webhook | 20 | Per webhook registration |
| Delivery rate | 10 deliveries/min | Per webhook endpoint |

### Rate Limit Headers on Webhook API

The webhook registration endpoints (`/api/v1/webhooks/*`) follow the same rate limiting policy as the rest of the API (see [Rate Limiting](rate-limiting.md)).

---

## 10. Security Considerations

| Concern | Mitigation |
|---|---|
| **Payload tampering** | Every delivery is signed with HMAC-SHA256. Verify the signature before processing. |
| **Replay attacks** | Signature includes a timestamp. Reject deliveries older than 5 minutes. |
| **Secret exposure** | Secret is shown only once at creation. Store it securely (env vars, secret manager). |
| **URL validation** | ARIA OS rejects webhook URLs pointing to private IP ranges, localhost, or internal networks. |
| **Rate limiting** | Max 10 deliveries per minute per webhook endpoint. Auto-disable after 10 consecutive failures. |
| **HTTPS required** | All webhook URLs must use HTTPS in production. HTTP is allowed only for local development. |
| **Payload validation** | Always verify the HMAC signature before processing. Never trust unverified payloads. |
| **Data minimization** | Webhook payloads contain only the minimum data needed for the event type. |

---

## 11. Related Documentation

| Document | Description |
|---|---|
| [API Integration Guide](../api-integration-guide.md) | General API usage, authentication, rate limits |
| [Error Catalog](error-catalog.md) | Standardized error codes and recovery strategies |
| [Rate Limiting](rate-limiting.md) | API rate limit policies and configuration |
| [Webhook Architecture](../Webhooks.md) | Internal architecture design for the webhook system |
| [API Changelog](changelog.md) | API version history and deprecation notices |
| [OpenAPI Reference](openapi-reference.md) | Interactive API specification |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-07-12 | Developer | Initial webhook integration guide — event types, payload schema, delivery, retry, signature, registration, best practices |
