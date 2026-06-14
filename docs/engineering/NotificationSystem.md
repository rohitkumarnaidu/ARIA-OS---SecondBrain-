# Notification System

## Document Control

| Metadata | Value |
|---|---|
| **Document ID** | ENG-NOTIF-001 |
| **Status** | Draft |
| **Version** | 1.0.0 |
| **Last Updated** | 2026-06-11 |
| **Author** | ARIA OS Engineering |
| **Approval** | Pending |
| **Related Docs** | ENG-ARCH-004 (Microservices), ENG-RT-001 (Realtime Architecture) |

---

## 1. Executive Summary

### 1.1 Purpose

Define the notification system for Second Brain OS, covering delivery channels, queue architecture, template management, user preferences, and the notification center UI.

### 1.2 Scope

Encompasses all notification generation, queuing, delivery, and tracking. Includes in-app, email, push, and SMS channels. Excludes realtime WebSocket infrastructure (see RealtimeArchitecture.md) and scheduler/cron configuration (see Scheduler Service).

### 1.3 Design Principles

- **Channel Agnostic**: Notifications are generated once and routed to one or more channels based on user preference
- **At-Least-Once Delivery**: Every notification is delivered at least once; duplicates are handled via idempotency
- **Respectful Delivery**: Rate limits, quiet hours, and preference opt-in/opt-out are enforced at the system level
- **Observable**: Every notification is tracked from creation to delivery with full audit trail

---

## 2. Notification Types

### 2.1 Priority Levels

| Priority | Label | Max Per Hour | Delivery Guarantee |
|---|---|---|---|
| **P0** | Critical | Unlimited | Immediate — all channels |
| **P1** | High | 30 | Within 1 minute |
| **P2** | Normal | 15 | Within 5 minutes |
| **P3** | Low | 5 | Best effort (batched) |

### 2.2 Notification Catalog

| Notification | Priority | Channels | Trigger |
|---|---|---|---|
| **Task Reminder** | P2 | In-app, Push (mobile), Email (daily digest) | Scheduler — 30 min before due |
| **Overdue Task** | P1 | In-app, Push | Scheduler — when task passes due date |
| **Habit Streak** | P2 | In-app, Push | Scheduler — daily at streak check time |
| **Habit Broken** | P2 | In-app | Scheduler — when streak is broken |
| **Goal Milestone** | P2 | In-app, Push, Email | Core CRUD — when goal progress >= milestone |
| **AI Analysis Ready** | P2 | In-app, Push, Email | AI Service — when async analysis completes |
| **AI Insight Generated** | P3 | In-app | AI Service — weekly insight generation |
| **Idea Saved** | P3 | In-app | Core CRUD — idea creation (subtle toast) |
| **Course Reminder** | P2 | In-app, Push, Email | Scheduler — based on study schedule |
| **Weekly Summary** | P2 | Email, In-app | Scheduler — every Sunday 9 AM |
| **Project Deadline** | P1 | In-app, Push, Email | Scheduler — 24h before project deadline |
| **Study Session Reminder** | P2 | In-app, Push | Scheduler — based on course schedule |
| **Income/Expense Alert** | P2 | In-app | Core CRUD — threshold-based (future) |
| **Sleep Goal Alert** | P2 | In-app, Push | Scheduler — bedtime reminder |
| **Sync Conflict** | P1 | In-app | Core CRUD — when sync conflict detected |

---

## 3. Architecture Overview

### 3.1 High-Level Flow

```
                    ┌─────────────────────────────────────────┐
                    │         Event Sources                    │
                    │  ┌────────┐ ┌──────────┐ ┌──────────┐  │
                    │  │  Core  │ │Scheduler │ │ AI Svc   │  │
                    │  │ CRUD   │ │ Service  │ │          │  │
                    │  └────┬───┘ └─────┬────┘ └─────┬────┘  │
                    └───────┼───────────┼────────────┼───────┘
                            │           │            │
                            ▼           ▼            ▼
                    ┌─────────────────────────────────────────┐
                    │         Notification Queue              │
                    │  (In-Memory Queue — Alpha)              │
                    │  (Redis Streams — Beta/Future)          │
                    └────────────────┬────────────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────────────┐
                    │        Notification Service              │
                    │  ┌────────┐ ┌──────┐ ┌──────────────┐  │
                    │  │Template│ │Pref  │ │  Channel     │  │
                    │  │Engine  │ │Mgr   │ │  Router      │  │
                    │  └────────┘ └──────┘ └──────┬───────┘  │
                    └──────────────────────────────┼─────────┘
                                                   │
                    ┌──────────────────────────────┼──────────────┐
                    │               ┌──────────────┼──────────┐   │
                    │               ▼              ▼          ▼   │
                    │          ┌────────┐  ┌─────────┐  ┌────┐  │
                    │          │ In-App │  │  Email  │  │Push│  │
                    │          │ Channel│  │ Channel │  │Chnl│  │
                    │          └────────┘  └─────────┘  └────┘  │
                    │         Channel Adapters                    │
                    └─────────────────────────────────────────────┘
```

### 3.2 Component Descriptions

| Component | Responsibility | Technology |
|---|---|---|
| **Event Sources** | Publish notification triggers as domain events | FastAPI event bus |
| **Notification Queue** | Buffer incoming notifications, provide retry/dead-letter | In-memory deque (alpha), Redis Streams (future) |
| **Notification Service** | Core orchestration: template rendering, preference filtering, channel routing | FastAPI standalone service |
| **Template Engine** | Render notification content from templates + context variables | Jinja2 (email), React (in-app), plain text (SMS) |
| **Preference Manager** | Evaluate user notification preferences, quiet hours, rate limits | PostgreSQL preference store |
| **Channel Router** | Dispatch notifications to appropriate delivery adapters | Router function with pluggable adapters |
| **Channel Adapters** | Deliver via specific channels (in-app, email, push, SMS) | Resend SDK, Web Push API, Twilio SDK |

---

## 4. Delivery Channels

### 4.1 In-App Notifications

| Aspect | Detail |
|---|---|
| **Storage** | `notifications` table in Supabase PostgreSQL |
| **Delivery** | Supabase Realtime channel `notifications:{user_id}` — pushes to UI in real-time |
| **UI Component** | Notification bell icon → dropdown feed → full notification center page |
| **States** | unread, read, archived |
| **Retention** | 90 days unread; 365 days read; archived forever |
| **Max Display** | 50 most recent in dropdown; paginated in full view |

**Schema:**

```sql
CREATE TABLE notifications (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  type         VARCHAR(64) NOT NULL,          -- e.g., 'task.reminder', 'habit.streak'
  title        VARCHAR(255) NOT NULL,
  body         TEXT NOT NULL,
  data         JSONB DEFAULT '{}',            -- contextual payload for UI actions
  priority     VARCHAR(8) NOT NULL DEFAULT 'P2',
  channel      VARCHAR(16) NOT NULL DEFAULT 'in-app',
  status       VARCHAR(16) NOT NULL DEFAULT 'unread',  -- unread | read | archived
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  read_at      TIMESTAMPTZ,
  archived_at  TIMESTAMPTZ
);

CREATE INDEX idx_notifications_user_status ON notifications(user_id, status, created_at DESC);
CREATE INDEX idx_notifications_user_type ON notifications(user_id, type);
```

### 4.2 Email (Resend)

| Aspect | Detail |
|---|---|
| **Provider** | Resend (resend.com) — transactional email API |
| **Sender** | `notifications@secondbrain.io` |
| **Template Engine** | Jinja2 HTML templates with inline CSS |
| **Send Mode** | Direct API call via Resend SDK |
| **Tracking** | Open tracking via Resend pixel; click tracking via link wrapping |
| **Rate Limit** | Resend default: 10 emails/second; user-level: 5 emails/hour for P2, 2/day for P3 |
| **Batching** | Low-priority notifications batched into daily digest email |
| **Unsubscribe** | One-click unsubscribe via `List-Unsubscribe` header and preference page link |

**Email Templates:**
- `templates/email/task-reminder.html` — task title, due time, priority badge
- `templates/email/daily-digest.html` — agenda, overdue tasks, habits, AI insights
- `templates/email/weekly-summary.html` — weekly stats, streaks, goal progress
- `templates/email/ai-insight.html` — AI-generated personal insight
- `templates/email/milestone.html` — congratulations with progress visualization

### 4.3 Push (Web Push API / Supabase Realtime)

| Aspect | Detail |
|---|---|
| **Web Push API** | Browser push notifications via Service Worker (VAPID keys) |
| **Mobile Push** | Expo Push Notifications or Firebase Cloud Messaging (future) |
| **Supabase Realtime** | Presence-based push for in-app real-time delivery |
| **Delivery** | Push notification triggers → Service Worker receive → click opens notification center |
| **Icon** | ARIA OS logo badge |
| **Actions** | "Mark as Read", "View Details" action buttons on push notifications |

### 4.4 SMS (Twilio — Future)

| Aspect | Detail |
|---|---|
| **Provider** | Twilio (future integration — post-alpha) |
| **Use Cases** | P0 critical alerts only: password reset, account recovery, 2FA |
| **Cost Control** | Hard limit: $10/month; per-task approval for premium tiers |
| **Rate Limit** | 1 SMS/user/hour |

---

## 5. Notification Queue

### 5.1 Alpha Phase — In-Memory Queue

```python
class NotificationQueue:
    """In-memory queue for alpha. Replaced by Redis Streams in beta."""

    def __init__(self, maxsize: int = 1000):
        self.queue = deque(maxlen=maxsize)
        self.dlq = deque(maxlen=100)  # dead letter queue
        self._lock = Lock()

    def enqueue(self, notification: Notification) -> None:
        with self._lock:
            self.queue.append(notification)

    def dequeue(self) -> Optional[Notification]:
        with self._lock:
            return self.queue.popleft() if self.queue else None

    def requeue(self, notification: Notification) -> None:
        with self._lock:
            self.queue.appendleft(notification)  # retry with priority

    def dead_letter(self, notification: Notification) -> None:
        with self._lock:
            self.dlq.append(notification)
```

**Limitations:**
- No persistence across restarts
- No distributed processing
- No consumer group semantics
- Acceptable for single-user alpha

### 5.2 Production Phase — Redis Streams

```
┌─────────────┐   XADD    ┌─────────────┐   XREADGROUP   ┌────────────────┐
│  Producers  │──────────▶│  Redis      │────────────────▶│  Notification  │
│  (Events)   │           │  Stream     │                 │  Workers (x3)  │
└─────────────┘           └─────────────┘                 └────────────────┘
                                   │                              │
                                   │                              │
                              ┌────▼────┐                   ┌────▼────┐
                              │  DLQ    │                   │  Retry  │
                              │ Stream  │                   │  Stream │
                              └─────────┘                   └─────────┘
```

**Queue Configuration:**
- Stream: `notifications` with max length 100,000 entries
- Consumer Group: `notification-workers` with 3 consumers
- Retry Stream: `notifications:retry` — TTL 1 hour, max 5 retries
- DLQ: `notifications:dead` — manual inspection and replay
- Backoff: exponential — 10s, 30s, 60s, 5min, 15min

---

## 6. Template System

### 6.1 Template Engine

- **Engine**: Jinja2 (Python) for email and SMS templates
- **Variable Injection**: Context dictionary passed by the notification service
- **Localization**: `en` locale only for alpha; locale-keyed template directories for future

### 6.2 Template Types

| Template Type | Format | Variables | Rendering Location |
|---|---|---|---|
| **In-App Notification** | JSON-definable + plain text | `title`, `body`, `data` (JSON) | Notification Service |
| **Email (HTML)** | Jinja2 HTML + inline CSS | Full context object | Notification Service |
| **Email (Text)** | Jinja2 plain text | Full context object (fallback) | Notification Service |
| **SMS** | Jinja2 plain text (160 char limit) | Minimal context | Notification Service |

### 6.3 Template Directory Structure

```
apps/api/templates/notifications/
├── email/
│   ├── base.html                    # Base HTML layout (header, footer, styles)
│   ├── task-reminder.html
│   ├── daily-digest.html
│   ├── weekly-summary.html
│   ├── ai-insight.html
│   └── milestone.html
├── in-app/
│   ├── task-reminder.json           # Default in-app notification config
│   └── habit-streak.json
└── sms/
    └── reminder.txt
```

---

## 7. Preference Management

### 7.1 User Preferences Schema

```sql
CREATE TABLE notification_preferences (
  user_id       UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  email_enabled BOOLEAN DEFAULT TRUE,
  push_enabled  BOOLEAN DEFAULT TRUE,
  sms_enabled   BOOLEAN DEFAULT FALSE,
  quiet_hours_start TIME DEFAULT NULL,     -- e.g., '22:00'
  quiet_hours_end   TIME DEFAULT NULL,     -- e.g., '07:00'
  quiet_hours_tz   VARCHAR(32) DEFAULT 'UTC',
  max_p2_per_hour INT DEFAULT 15,
  max_p3_per_hour INT DEFAULT 5,
  daily_digest   BOOLEAN DEFAULT TRUE,
  weekly_summary BOOLEAN DEFAULT TRUE,
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE notification_channel_permissions (
  user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  notification_type VARCHAR(64) NOT NULL,   -- e.g., 'task.reminder'
  channel         VARCHAR(16) NOT NULL,      -- 'in-app', 'email', 'push', 'sms'
  enabled         BOOLEAN NOT NULL DEFAULT TRUE,
  PRIMARY KEY (user_id, notification_type, channel)
);
```

### 7.2 Preference Evaluation Flow

```
Notification Created
        │
        ▼
Load user preferences
        │
        ├── Quiet hours active? ──▶ P2/P3 held until quiet hours end
        │
        ├── Rate limit reached? ──▶ Queue for next interval
        │
        └── Channel permitted? ──▶ Route to approved channels
                                     │
                                     ▼
                                   Deliver
```

### 7.3 Default Preferences

| Notification Type | In-App | Email | Push | SMS |
|---|---|---|---|---|
| Task Reminder | ✅ | ❌ (digest only) | ✅ | ❌ |
| Overdue Task | ✅ | ✅ | ✅ | ❌ |
| Habit Streak | ✅ | ❌ | ✅ | ❌ |
| Goal Milestone | ✅ | ✅ | ✅ | ❌ |
| AI Analysis Ready | ✅ | ✅ | ✅ | ❌ |
| AI Insight | ✅ | ❌ | ❌ | ❌ |
| Weekly Summary | ✅ | ✅ | ❌ | ❌ |
| Daily Digest | ❌ | ✅ | ❌ | ❌ |
| Password Reset | ❌ | ✅ | ❌ | ❌ |
| 2FA Code | ❌ | ✅ | ❌ | ✅ |

---

## 8. Delivery Guarantees

### 8.1 Delivery Semantics

| Level | Description | Implementation |
|---|---|---|
| **At-Least-Once** | Every notification is delivered at least once | Queue persistence + delivery confirmation + retry |
| **Ordered Delivery** | Notifications from the same source delivered in order (best effort) | Single-consumer ordering within Redis stream |
| **Deduplication** | Duplicate notifications within 60-second window are collapsed | Idempotency key = `sha256(type + user_id + data_hash + timestamp_window)` |

### 8.2 Retry Strategy

| Attempt | Delay | Channel |
|---|---|---|
| 1 | 0s (immediate) | Primary |
| 2 | 10s | Primary |
| 3 | 30s | Primary |
| 4 | 60s | Primary |
| 5 | 5 min | Fallback channel (if available) |
| 6+ | 15 min | Dead letter queue after 24h |

### 8.3 Dead Letter Queue

Notifications moved to DLQ after:
- 5 failed delivery attempts (any channel)
- Invalid template rendering (jinja2 syntax error)
- Recipient channel unreachable for > 24 hours
- Rate limit exceeded for > 6 hours

DLQ entries are logged for manual review with replay capability.

---

## 9. Rate Limiting & Throttling

### 9.1 Rate Limits

| Scope | Limit | Window | Enforced At |
|---|---|---|---|
| Per user, all channels | 50 | 1 hour | Notification Service |
| Per user, email | 5 (P2), 2 (P3) | 1 hour | Email Channel Adapter |
| Per user, push | 20 | 1 hour | Push Channel Adapter |
| Per user, SMS | 1 | 1 hour | SMS Channel Adapter |
| Global email sending | 10 | 1 second | Resend API quota |
| Per notification type | Configurable per type | 1 hour | Preference Manager |

### 9.2 Throttling Behavior

When a rate limit is reached:
1. P2/P3 notifications are queued for delivery in the next interval
2. P0/P1 notifications are delivered immediately (bypass rate limits)
3. User receives an "in-app only" digest notification: "You have 5 notifications waiting"
4. Rate limit counters are stored in Redis with TTL matching the window

---

## 10. Notification Center UI

### 10.1 Components

| Component | Description | File |
|---|---|---|
| `NotificationBell` | Bell icon in header with unread badge count | `apps/web/components/notifications/notification-bell.tsx` |
| `NotificationDropdown` | Dropdown with 5 most recent unread notifications | `apps/web/components/notifications/notification-dropdown.tsx` |
| `NotificationList` | Full paginated list of all notifications | `apps/web/components/notifications/notification-list.tsx` |
| `NotificationItem` | Single notification with icon, title, body, timestamp | `apps/web/components/notifications/notification-item.tsx` |
| `NotificationSettings` | Preference toggle form per channel per type | `apps/web/components/notifications/notification-settings.tsx` |

### 10.2 User Flow

```
┌──────────────────────────────────────────────────────────────┐
│  ARIA OS Header                          [🔔 3]  [Avatar]   │
│                                        ┌───────▼────────┐   │
│                                        │ Notifications  │   │
│                                        │ ─────────────  │   │
│                                        │ ● Task "Math   │   │
│                                        │   HW" due in   │   │
│                                        │   30 min       │   │
│                                        │ ● ● Streak: 7  │   │
│                                        │   days! 🔥     │   │
│                                        │ ○ AI Insight:  │   │
│                                        │   Study pattern │   │
│                                        │   identified    │   │
│                                        │                │   │
│                                        │ [View All]     │   │
│                                        └────────────────┘   │
│                                                              │
│  Click "View All" → /notifications page                      │
└──────────────────────────────────────────────────────────────┘
```

### 10.3 State Management (Zustand)

```typescript
interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  loading: boolean;
  markAsRead: (id: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  archive: (id: string) => Promise<void>;
  fetchPage: (page: number) => Promise<void>;
}
```

### 10.4 Supabase Realtime Subscription

```typescript
const channel = supabase
  .channel('notifications')
  .on(
    'postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'notifications',
      filter: `user_id=eq.${userId}`,
    },
    (payload) => {
      addNotification(payload.new as Notification);
      incrementUnreadCount();
    }
  )
  .subscribe();
```

---

## 11. Analytics & Tracking

### 11.1 Events Tracked

| Event | Triggered When | Payload |
|---|---|---|
| `notification.created` | Notification inserted into queue | `{ id, type, user_id, channel, priority }` |
| `notification.delivered` | Channel confirms delivery | `{ id, channel, delivery_time_ms }` |
| `notification.opened` | User clicks notification | `{ id, channel, open_time_ms }` |
| `notification.bounced` | Email bounced / push invalid | `{ id, channel, error }` |
| `notification.preference_updated` | User changes preferences | `{ user_id, changes }` |

### 11.2 Metrics Dashboard

| Metric | Target | Measured By |
|---|---|---|
| Delivery Rate | > 99% | `delivered / (created - bounced)` |
| Open Rate (Email) | > 40% | Resend open tracking pixel |
| Click Rate (In-App) | > 60% | Click event on notification item |
| Average Delivery Latency | < 500ms (P0), < 5s (P1-P2) | Timestamp diff |
| Bounce Rate | < 1% | Resend bounce webhook |
| User Opt-Out Rate | < 5% | Preference changes per month |

### 11.3 Analytics Storage

```sql
CREATE TABLE notification_events (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  notification_id UUID NOT NULL REFERENCES notifications(id) ON DELETE CASCADE,
  event_type      VARCHAR(32) NOT NULL,  -- created | delivered | opened | bounced
  channel         VARCHAR(16),
  metadata        JSONB DEFAULT '{}',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notif_events_type ON notification_events(event_type);
CREATE INDEX idx_notif_events_notif ON notification_events(notification_id);
```

---

## 12. Appendices

### 12.1 Template Examples

**Email Template (task-reminder.html):**

```html
{% extends "base.html" %}
{% block content %}
<div class="card">
  <h2 class="title">⏰ Task Reminder</h2>
  <p class="body"><strong>{{ task.title }}</strong> is due in <strong>{{ time_remaining }}</strong>.</p>
  {% if task.priority == 'high' %}
  <span class="badge badge-high">High Priority</span>
  {% endif %}
  <p class="due">Due: {{ task.due_date | date('full') }}</p>
  <a href="{{ task_url }}" class="button">View Task</a>
</div>
{% endblock %}
```

**In-App Template (task-reminder.json):**

```json
{
  "title": "Task Reminder",
  "body": "{{ task.title }} is due in {{ time_remaining }}.",
  "data": {
    "task_id": "{{ task.id }}",
    "priority": "{{ task.priority }}",
    "action_url": "/tasks/{{ task.id }}"
  }
}
```

### 12.2 Scheduling Rules

| Notification | Schedule | Crontab |
|---|---|---|
| Task Reminders | 30 minutes before due | Dynamic — per task |
| Overdue Check | Every 15 minutes | `*/15 * * * *` |
| Habit Streak Check | 9 PM daily | `0 21 * * *` |
| Weekly Summary | Sunday 9 AM | `0 9 * * 0` |
| Daily Digest | 7 AM daily | `0 7 * * *` |
| AI Weekly Insight | Monday 8 AM | `0 8 * * 1` |
| Cleanup Old Notifications | Daily 3 AM | `0 3 * * *` |

### 12.3 Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-11 | ARIA OS Engineering | Initial draft |
