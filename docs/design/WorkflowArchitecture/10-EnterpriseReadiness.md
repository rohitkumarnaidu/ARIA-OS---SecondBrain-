# Part X — Enterprise Readiness

> **Part of the Workflow Architecture (SB-WFARCH-001). See `README.md` for document control.**
> Related: `AuditLogs.md` (backend audit), `32_Monitoring.md` (observability), `40_IncidentResponse.md` (incident response), `39_Runbooks.md` (operational procedures).

---

## 10.1 Audit Dashboard

**Route:** `/admin/audit`
**Access:** Admin role only (RBAC)
**Purpose:** Real-time view of all system events for compliance and debugging

### Layout

```
┌──────────────────────────────────────────────────┐
│  🛡️ Audit Dashboard                    [Export]  │
│                                                    │
│  ┌──────────┬──────────┬──────────┬──────────┐     │
│  │ Events   │ Users    │ Errors   │ Export   │     │
│  │ 12,847   │ 342      │ 23       │ [CSV]    │     │
│  │ Last 24h │ Active   │ Today    │ [JSON]   │     │
│  └──────────┴──────────┴──────────┴──────────┘     │
│                                                    │
│  Recent Events                        [Filter ▼]   │
│  ┌────────────────────────────────────────────┐    │
│  │ 14:30:22 · user_abc · task.create     ✅   │    │
│  │ 14:28:15 · user_def · goal.update     ✅   │    │
│  │ 14:25:00 · system  · cron.briefing    ✅   │    │
│  │ 14:20:44 · user_abc · auth.login      ✅   │    │
│  │ 14:15:12 · system  · ai.fallback      ⚠️   │    │
│  │ 14:10:03 · user_ghi · task.delete     ✅   │    │
│  └────────────────────────────────────────────┘    │
│                                                    │
│  Search: [____________________________]            │
│  Date Range: [2026-06-16] → [2026-06-17]          │
│  Event Type: [All ▼]  Severity: [All ▼]           │
│                                                    │
│  └── Pagination: 1 2 3 ... 428 ›                   │
└──────────────────────────────────────────────────┘
```

### Event Categories

| Category | Icon | Events Tracked |
|---|---|---|
| Auth | 🔑 | login, logout, token_refresh, password_reset, mfa_challenge |
| Data | 📝 | task.*, goal.*, course.*, habit.*, sleep.*, project.*, idea.* |
| AI | 🤖 | agent.run, agent.fail, agent.fallback, llm.call, memory.write |
| System | ⚙️ | cron.start, cron.complete, cron.fail, sync.conflict, backup.run |
| Security | 🛡️ | auth.fail, rate_limit.hit, suspicious.ip, api.abuse |
| Admin | 👑 | admin.login, config.change, user.impersonate, feature.toggle |

### States

| State | UI Treatment |
|---|---|
| **Empty** | "No events in selected time range" |
| **Loading** | Skeleton table rows (10 rows shimmer) |
| **Populated** | Paginated table with live updates |
| **Filtered** | Active filter chips below search bar |
| **Exporting** | Progress bar + "Generating CSV..." |
| **Error** | "Couldn't load audit events" + retry |
| **Historical** | Date range selector + "Viewing archived events" indicator |

### Data Model

Each audit event includes:
- `id` (UUID), `timestamp` (ISO 8601)
- `user_id` (UUID, nullable for system events)
- `event_type` (string: "task.create", "auth.login", etc.)
- `severity` (info / warning / error / critical)
- `metadata` (JSON: request_id, ip, user_agent, diff)
- `checksum` (SHA-256 of event fields for tamper detection)

---

## 10.2 Admin Panel

**Route:** `/admin`
**Access:** Admin role only
**Purpose:** Central administration for user management, system config, and feature flags

### Layout

```
┌──────────────────────────────────────────────┐
│  Admin Panel                                  │
│  ┌────────┬────────┬────────┬────────┐       │
│  │ Users  │ Config │ Feature │ System│       │
│  ├────────┴────────┴────────┴────────┤       │
│  │                                    │       │
│  │ Tab Content Area                   │       │
│  │                                    │       │
│  │ ┌──────────────────────────┐       │       │
│  │ │ User table: search,      │       │       │
│  │ │ filter, view, suspend,   │       │       │
│  │ │ delete, impersonate      │       │       │
│  │ └──────────────────────────┘       │       │
│  └────────────────────────────────────┘       │
└──────────────────────────────────────────────┘
```

### Tabs

| Tab | Content | Actions |
|---|---|---|
| **Users** | Searchable table with status, modules used, last active | View, Suspend, Delete, Impersonate (audit-logged) |
| **Config** | Key-value environment config viewer | Edit, Reset, Diff against last config |
| **Feature Flags** | Toggle per feature across all users | Enable/disable, percentage rollout, user segment |
| **System** | Service dependencies health, version info | Restart service, trigger job, view logs |

### Feature Flag Schema

| Field | Type | Description |
|---|---|---|
| `name` | String | Feature identifier (e.g., "semantic-search") |
| `enabled` | Boolean | Global toggle |
| `rollout_percentage` | Integer (0-100) | Gradual rollout |
| `user_segments` | String[] | "alpha", "beta", "internal" |
| `dependencies` | String[] | Required feature flags |
| `expires_at` | Timestamp | Auto-disable date |

---

## 10.3 System Status Dashboard

**Route:** `/admin/status`
**Purpose:** Real-time health of all system components

### Layout

```
┌──────────────────────────────────────────────┐
│  System Status                    Last: 30s  │
│                                              │
│  🟢 All Systems Operational                  │
│                                              │
│  ┌──────────────┬──────────┬────────┐        │
│  │ Component    │ Status   │ Latency│        │
│  ├──────────────┼──────────┼────────┤        │
│  │ API Server   │ 🟢 Up    │ 42ms   │        │
│  │ Database     │ 🟢 Up    │ 12ms   │        │
│  │ Auth Service │ 🟢 Up    │ 85ms   │        │
│  │ Ollama       │ 🟢 Up    │ 1.2s   │        │
│  │ Claude API   │ ⚪ Idle  │ —      │        │
│  │ Scheduler    │ 🟢 Up    │ —      │        │
│  │ CDN          │ 🟢 Up    │ 35ms   │        │
│  │ Email        │ 🟢 Up    │ 210ms  │        │
│  └──────────────┴──────────┴────────┘        │
│                                              │
│  [View Details] [Run Health Check]            │
│  [Configure Alerts]                           │
└──────────────────────────────────────────────┘
```

### States

| State | UI Treatment |
|---|---|
| **All Green** | 🟢 "All Systems Operational" + green banner |
| **Degraded** | 🟡 "1 System Degraded" + amber banner + affected component highlighted |
| **Down** | 🔴 "2 Systems Down" + red banner + ETA if available |
| **Loading** | Skeleton component list (8 rows shimmer) |
| **Error** | "Couldn't fetch status" + retry + last known state |

---

## 10.4 Integration Hub

**Route:** `/admin/integrations`
**Purpose:** Manage all third-party integrations, API keys, and webhooks

### Layout

| Integration | Status | API Version | Rate Limit | Last Sync | Actions |
|---|---|---|---|---|---|
| Google Calendar | ✅ Connected | v3 | 100/hr | 2m ago | Reconnect, Webhook |
| GitHub | ✅ Connected | REST v3 | 500/hr | 1h ago | Disconnect |
| YouTube | ⚠️ Expiring | v3 | 10K/day | — | Reauth |
| Resend | ✅ Connected | v1 | 100/hr | Active | Test |
| Webhook (Custom) | 🔴 Failed | — | — | — | Retry, Edit |

---

## 10.5 Logs Viewer

**Route:** `/admin/logs`
**Purpose:** Centralized log viewer with filtering, search, and live tail

### Layout

```
┌──────────────────────────────────────────────┐
│  Logs Viewer                     [Live Tail] │
│                                              │
│  Search: [___________________________]       │
│  Level: [All ▼]  Source: [All ▼]  Time: [▼] │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ 14:30:22 INFO  api.server  GET /api/v1 │  │
│  │ 14:30:20 WARN  ai.client   Ollama slow │  │
│  │ 14:30:18 ERROR auth.jwt    Token exp'd │  │
│  │ 14:30:15 INFO  scheduler   cron.start  │  │
│  │ 14:30:12 DEBUG memory.ag   Extracting  │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  [Pause] [Copy] [Export] [Settings]          │
└──────────────────────────────────────────────┘
```

### States

| State | UI Treatment |
|---|---|
| **Empty** | "No logs matching filters" + adjust suggestion |
| **Live** | Auto-scrolling with new entries appearing at top |
| **Paused** | "Paused — 15 new entries" button |
| **Filtered** | Active filter badges |
| **Historical** | Date range with "Loading older entries..." |
| **Error** | "Log stream disconnected" + reconnect button |

---

## 10.6 Usage Monitor

**Route:** `/admin/usage`
**Purpose:** Track system-wide usage metrics

### Metrics

| Metric | Chart | Periods |
|---|---|---|
| DAU (Daily Active Users) | Line chart | 7d / 30d / 90d |
| API Requests | Area chart | 24h / 7d / 30d |
| AI Token Consumption | Stacked bar (per agent) | 7d / 30d |
| Error Rate | Line chart with threshold line | 24h / 7d |
| Avg Response Time | Line chart with p50/p95/p99 | 24h |
| Storage | Gauge (used/total) | Real-time |

---

## 10.7 Health Dashboard

**Route:** `/admin/health`
**Purpose:** Deep health checks with dependency graph

### Response Schema

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 86400,
  "dependencies": {
    "supabase": { "status": "ok", "latency_ms": 12 },
    "ollama": { "status": "ok", "latency_ms": 1200 },
    "claude_api": { "status": "configured", "latency_ms": null },
    "resend": { "status": "ok", "latency_ms": 210 },
    "scheduler": { "status": "ok", "last_run": "2026-06-17T06:00:00Z" }
  },
  "checks": {
    "database_connectivity": "pass",
    "ai_model_loaded": "pass",
    "queue_healthy": "pass",
    "cache_reachable": "pass",
    "disk_space": "warning (78% used)"
  }
}
```

---

## 10.8 Compliance Center

**Route:** `/admin/compliance`
**Purpose:** GDPR, SOC2, and data governance compliance views

### Sections

| Section | Content |
|---|---|
| Data Processing Register | All data categories, purposes, retention periods |
| User Data Requests | Right to access, rectification, erasure requests queue |
| Audit Log Export | Download audit logs filtered by date range (GDPR Art. 30) |
| Retention Policies | Per-category data retention with enforcement status |
| Breach Log | Security incident register with timestamps |
| Consent Records | User consent records for data processing |
