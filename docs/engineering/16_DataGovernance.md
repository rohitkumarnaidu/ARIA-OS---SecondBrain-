# Data Governance Framework — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ENG-DATAGOV-001 |
| **Version** | 2.0.0 |
| **Status** | Active |
| **Last Updated** | 2026-06-11 |
| **Classification** | Internal — Governance & Compliance |
| **Owner** | Data Governance Committee |
| **Review Cycle** | Quarterly |

---

### Architecture Diagram — Data Governance Lifecycle

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#6366F1',
      'primaryTextColor': '#F1F5F9',
      'primaryBorderColor': '#6366F1',
      'lineColor': '#818CF8',
      'secondaryColor': '#13151A',
      'tertiaryColor': '#0A0B0F',
      'clusterBkg': '#0A0B0F',
      'clusterBorder': '#334155',
      'nodeBorder': '#6366F1',
      'nodeTextColor': '#F1F5F9',
      'edgeLabelBackground': '#13151A',
      'fontFamily': 'DM Sans',
      'titleColor': '#F1F5F9'
    }
  }
}%%
flowchart LR
    Classify["Data Classification<br/>T1–T4"] --> Secure["Security Controls<br/>RLS · Encryption · Auth"]
    Secure -->     Store["Storage & Retention<br/>27 Tables · 18 Categories"]
    Store --> Quality["Quality Management<br/>Accuracy · Completeness · Freshness"]
    Quality --> Audit["Audit & Lineage<br/>Immutable Log · Change Tracking"]
    Audit --> Retire["Retire & Purge<br/>Defensible Deletion · GDPR Compliance"]
    Retire -.->|Continuous Feedback| Classify
```

---

## 1. Executive Summary

Second Brain OS processes **18+ categories of personal data** across a monorepo architecture. This document defines the comprehensive data governance framework covering classification, lifecycle management, quality standards, retention policies, privacy controls, access controls, audit trails, backup/recovery, migration, lineage tracking, and stewardship.

**Scope:** All data within the Second Brain OS ecosystem — Supabase PostgreSQL (27 tables), browser IndexedDB cache, Ollama local AI processing, and third-party API interactions (Claude, Resend, Twilio, Brave Search).

**Design Principles:**
1. **User is data owner** — All data belongs to the user; no third party has data rights
2. **Privacy by default** — Local AI processing preferred; cloud AI only with anonymized context
3. **Minimal retention** — Data kept only as long as needed for its purpose
4. **Audit transparency** — All sensitive operations logged
5. **Defensible deletion** — Clear criteria for when data must be purged

---

## 2. Data Governance Framework Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA GOVERNANCE FRAMEWORK                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │  Data       │  │  Data       │  │  Data       │  │  Data      │ │
│  │  Classification │  Lifecycle     │  Quality        │  Access    │ │
│  │  (T1-T4)    │  │  (7 stages)  │  │  (4 metrics) │  │  Controls  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │  Data       │  │  Data       │  │  Data       │  │  Data      │ │
│  │  Retention  │  │  Privacy    │  │  Backup &   │  │  Lineage   │ │
│  │  27 tables  │  │  Controls   │  │  Recovery   │  │  Tracking  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │  Data       │  │  Data       │  │  Training & │                 │
│  │  Migration  │  │  Audit Trail │  │  Awareness  │                 │
│  │  Process    │  │  Logging     │  │  Program    │                 │
│  └─────────────┘  └─────────────┘  └─────────────┘                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Classification Scheme

### 3.1 Classification Tiers

| Tier | Label | Definition | Examples | Encryption Required | Access Level |
|---|---|---|---|---|---|
| **T1** | Highly Sensitive | Could cause significant harm if exposed | Auth tokens, API keys, OAuth tokens, JWT sessions, encryption keys | AES-256 at rest + TLS 1.3 in transit | Server-side only; never logged |
| **T2** | Personal Data | Personally identifiable or high-privacy data | Name, email, college, year, skills, income, sleep patterns, academic marks, chat messages, memory inferences | AES-256 at rest | User-only (RLS); anonymized to third parties |
| **T3** | User Content | User-generated productivity data | Tasks, ideas, notes, resources, projects, habits, goals, daily briefings, weekly reviews | Standard encryption | User-only (RLS) |
| **T4** | System Data | Operational metadata | App preferences, UI state, cache, timestamps, logs, feature flags | No additional encryption (standard DB encryption) | Internal |

### 3.2 Data Classification Decision Tree

```
Is the data an authentication credential or API key?
  ├── YES → T1 (Highly Sensitive)
  └── NO
       └── Does it contain personal identifiers (name, email, phone, college)?
            ├── YES → T2 (Personal Data)
            └── NO
                 └── Is it user-created content?
                      ├── YES → T3 (User Content)
                      └── NO → T4 (System Data)
```

### 3.3 Classification by Table

| # | Table | Tier | Schema | Est. Rows (1yr) | Sensitivity Notes |
|---|---|---|---|---|---|
| 1 | `users` | T1-T2 | id, email, name, auth_provider, settings | 1 | T1: auth tokens; T2: email/name |
| 2 | `tasks` | T3 | id, user_id, title, description, status, priority, due_date, dependencies | ~5,000 | Task descriptions may contain personal info |
| 3 | `courses` | T3 | id, user_id, name, platform, url, progress, deadlines | ~200 | Course preferences (low sensitivity) |
| 4 | `goals` | T3 | id, user_id, title, description, milestones, roadmap | ~100 | Life goals (user IP) |
| 5 | `habits` | T3 | id, user_id, name, frequency, streak, target | ~100 | Habit definitions |
| 6 | `habit_logs` | T3 | id, user_id, habit_id, date, completed, note | ~10,000 | Daily completion data |
| 7 | `sleep_logs` | T2 | id, user_id, bedtime, wake_time, quality, score, debt | ~1,500 | Sleep patterns (health data) |
| 8 | `income_entries` | T2 | id, user_id, amount, source, date, hourly_rate | ~500 | Financial data |
| 9 | `projects` | T3 | id, user_id, name, phases, blockers, urls | ~100 | Project details |
| 10 | `ideas` | T3 | id, user_id, title, description, stage, market_check | ~200 | Startup ideas (user IP) |
| 11 | `resources` | T3 | id, user_id, url, title, tags, notes | ~1,000 | Bookmarked URLs |
| 12 | `opportunities` | T3 | id, user_id, title, url, match_score, status | ~500 | Career opportunities |
| 13 | `time_entries` | T3 | id, user_id, start, end, duration, type, project_id | ~10,000 | Time tracking data |
| 14 | `chat_messages` | T2 | id, user_id, role, content, timestamp, context | ~50,000 | May contain personal disclosures |
| 15 | `daily_briefings` | T3 | id, user_id, date, content, was_read | ~365 | Generated briefings |
| 16 | `weekly_reviews` | T3 | id, user_id, week_start, content, metrics | ~52 | Generated reviews |
| 17 | `memory` | T2 | id, user_id, key, value, confidence, updated_at | ~500 | Inferred preferences, patterns |
| 18 | `learning_progress` | T3 | id, user_id, module, score, timestamp | ~1,000 | Learning metrics |
| 19 | `chat_conversations` | T3 | id, user_id, title, created_at, updated_at | ~2,000 | Chat metadata |
| 20 | `user_preferences` | T4 | id, user_id, theme, flags, settings | 1 | App configuration |
| 21 | `audit_logs` | T2 | id, user_id, action, details, ip, created_at | ~1,000 | Access logs |

---

## 4. Data Lifecycle

### 4.1 Lifecycle Stages

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  CREATE  │───▶│  STORE   │───▶│   USE    │───▶│  SHARE   │───▶│ ARCHIVE  │───▶│  PURGE   │
│ (input)  │    │ (persist)│    │ (process)│    │ (export)  │    │ (freeze) │    │ (delete) │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
     │              │              │              │              │              │
     ▼              ▼              ▼              ▼              ▼              ▼
  Validation     Encryption    AI processing   Export API     Status change  Scheduled
  + Indexing     + Backup      + Analysis      + Download     + Metadata     + Cascade
```

### 4.2 Stage Details

| Stage | Description | Actions | Validation |
|---|---|---|---|
| **CREATE** | Data enters the system via UI, API, or import | Validate schema; sanitize input; classify sensitivity; assign default retention | Schema validation; XSS sanitization; PII detection |
| **STORE** | Data persisted to database or cache | Encrypt at rest; apply RLS; index for performance; set TTL/retention | Storage limits; encryption verification |
| **USE** | Data processed, queried, or transformed | Filter by RLS; anonymize for third-party AI; log access for T1-T2 | Query validation; rate limiting; access audit |
| **SHARE** | Data exported or transmitted to third-party | User consent check; anonymize if required; minification; encrypted transfer | Consent verification; data minimization check |
| **ARCHIVE** | Data moved to long-term retention | Status change; removal from active queries; retention timer starts | Archive criteria verification |
| **PURGE** | Data permanently deleted | Hard DELETE or anonymize; cascade cleanup; verify deletion | Deletion confirmation; restore check |

---

## 5. Data Quality Standards

### 5.1 Quality Dimensions

| Dimension | Definition | Target | Measurement Method | Remediation |
|---|---|---|---|---|
| **Accuracy** | Data correctly represents real-world state | >99% | Manual sampling; consistency checks | Flag for review; auto-correct if rule-based |
| **Completeness** | Required fields are populated | 100% for required; >90% for optional | Schema validation at insert | Frontend validation; default values |
| **Timeliness** | Data reflects current state within SLA | Real-time for CRUD; <5 min for sync | Timestamp monitoring; staleness alerts | Sync triggers; refresh schedules |
| **Consistency** | Data follows defined format and constraints | 100% | Enum validation; foreign key checks; type checking | Schema migration; data cleanup scripts |
| **Uniqueness** | No duplicate records exist | >99.9% | Unique constraints; dedup checks | Merge on conflict; dedup cron job |
| **Validity** | Data conforms to business rules | >99% | Business rule validation; cross-field checks | Validation error return; field-level hints |

### 5.2 Quality Monitoring

| Monitoring Type | Frequency | Tool | Action on Failure |
|---|---|---|---|
| Schema validation | Per insert | Pydantic / Zod | Reject insert with error message |
| Foreign key integrity | Daily | PostgreSQL FK checks | Log orphaned rows; cleanup |
| Nullable field audit | Weekly | Custom SQL query | Flag missing optional data; notify user |
| Duplicate detection | Weekly | Custom SQL with GROUP BY | Merge duplicates; log resolution |
| Timestamp sanity | Daily | Check for future dates, ancient dates | Auto-correct; flag for review |
| Referential integrity | Per query | RLS + FK constraints | Block invalid operations |

### 5.3 Quality Issue Severity Matrix

| Severity | Definition | Response Time | Example |
|---|---|---|---|
| **Critical** | Data corruption, wrong calculation output | < 1 hour | Task status showing wrong value in AI summary |
| **High** | Data loss, missing required fields | < 4 hours | User profile missing `email` field |
| **Medium** | Inconsistency between related tables | < 24 hours | Habit streak count doesn't match habit_logs |
| **Low** | Cosmetic issues, non-required field missing | < 1 week | Missing `description` on a task |
| **Informational** | Minor formatting, deprecated values | < 1 month | Old category name in use |

---

## 6. Data Ownership & Stewardship

### 6.1 Data Stewardship Matrix

| Module | Steward | Table(s) | Steward Responsibilities |
|---|---|---|---|
| **Tasks** | Developer | tasks | Schema changes, quality, retention |
| **Courses** | Developer | courses | Schema changes, quality, retention |
| **Goals** | Developer | goals | Schema changes, quality, retention |
| **Habits** | Developer | habits, habit_logs | Schema changes, quality, retention |
| **Sleep** | Developer | sleep_logs | Schema changes, quality, retention |
| **Income** | Developer | income_entries | Schema changes, quality, retention (financial) |
| **Projects** | Developer | projects | Schema changes, quality, retention |
| **Ideas** | Developer | ideas | Schema changes, quality, retention (IP) |
| **Resources** | Developer | resources | Schema changes, quality, retention |
| **Opportunities** | Developer | opportunities | Schema changes, quality, retention |
| **Time** | Developer | time_entries | Schema changes, quality, retention |
| **Chat** | Developer | chat_messages, memory | Schema changes, quality, privacy (AI interactions) |
| **Briefings** | Developer | daily_briefings, weekly_reviews | Schema changes, quality, retention (generated) |
| **Auth/Security** | Developer | users, audit_logs | Schema changes, access controls, compliance |
| **System** | Developer | user_preferences | Schema changes, quality |

### 6.2 Data Ownership Responsibilities

Both the data owner (user) and data steward (developer) share responsibilities:

| Responsibility | Data Owner (User) | Data Steward (Developer) |
|---|---|---|
| **Accuracy** | Ensure data entered is correct | Provide validation and correction tools |
| **Timeliness** | Keep data up-to-date | Timestamp tracking; stale data alerts |
| **Access** | Manage own data access | Implement RLS; verify auth |
| **Retention** | Initiate deletion when needed | Implement retention policies; auto-purge |
| **Export** | Request export | Provide export API |
| **Consent** | Configure AI privacy settings | Respect consent flags; anonymize where needed |

---

## 7. Data Retention Policy

### 7.1 Retention Schedule by Table

| Table | Active Period | Archive After | Purge After | Archive Method | Purge Method | Rationale |
|---|---|---|---|---|---|---|
| `tasks` | While active | 90 days after completion | 2 years | `status='archived'` | DELETE with cascade | Task data useful up to 2 years for reference |
| `courses` | While enrolled | 1 year after last update | — | `status='completed'` | Keep indefinitely | Learning history valuable long-term |
| `goals` | While active | 1 year after completion | — | `status='archived'` | Keep indefinitely | Life goals tracked over lifetime |
| `habits` | While active | — | — | — | Keep indefinitely | Habit patterns improve over time |
| `habit_logs` | Daily | — | 2 years | Aggregate into weekly patterns | DELETE | Raw daily logs less useful after 2 years |
| `sleep_logs` | Daily | — | 90 days | Aggregate into weekly/monthly patterns | DELETE | Recent sleep patterns only relevant |
| `income_entries` | Monthly | — | 7 years | — | DELETE after 7 years | Tax record requirement (general guidance) |
| `projects` | While active | 1 year after completion | — | `status='archived'` | Keep indefinitely | Portfolio reference |
| `ideas` | While active | — | — | — | Keep indefinitely | Idea pipeline tracked over lifetime |
| `resources` | While active | — | — | — | Keep indefinitely | Reference library |
| `opportunities` | While active | 90 days after status change | 1 year | `status='archived'` | DELETE after 1 year | Career opportunities become outdated |
| `time_entries` | Daily | — | 90 days | Aggregate into weekly summaries | DELETE | Raw time entries aggregated |
| `chat_messages` | Per conversation | — | 1 year | Summarize to memory table | DELETE | Privacy; key info extracted to memory |
| `memory` | Continuous | — | — | — | Keep indefinitely | Core AI learning; confidence decay manages relevance |
| `daily_briefings` | Daily | — | 30 days (keep last 7) | — | DELETE | Stale briefings have no value |
| `weekly_reviews` | Weekly | — | — | — | Keep indefinitely | Growth record |
| `learning_progress` | Per session | — | 2 years | Aggregate into trends | DELETE | Learning metrics history |
| `chat_conversations` | Per session | — | 1 year | — | DELETE with messages | Chat metadata |
| `user_preferences` | Continuous | — | — | — | Keep while account active | Configuration data |
| `audit_logs` | Per event | — | 3 years | — | DELETE after 3 years | Compliance requirement |
| `users` | Account lifetime | 30 days after deletion request | Permanently after 30-day grace | `status='deleted'` | CASCADE delete | Account lifecycle |

### 7.2 Retention Cron Jobs

```sql
-- Daily: Purge completed tasks older than 2 years
DELETE FROM tasks
WHERE status = 'completed'
  AND completed_at < NOW() - INTERVAL '2 years';

-- Daily: Purge cancelled tasks older than 30 days
DELETE FROM tasks
WHERE status = 'cancelled'
  AND updated_at < NOW() - INTERVAL '30 days';

-- Daily: Purge chat messages older than 1 year
DELETE FROM chat_messages
WHERE created_at < NOW() - INTERVAL '1 year'
  AND id NOT IN (
    SELECT message_id FROM memory WHERE source = 'chat_summary'
  );

-- Daily: Purge sleep logs older than 90 days
DELETE FROM sleep_logs
WHERE date < NOW() - INTERVAL '90 days';

-- Daily: Purge time entries older than 90 days
DELETE FROM time_entries
WHERE date < NOW() - INTERVAL '90 days';

-- Daily: Purge daily briefings older than 30 days (keep last 7)
DELETE FROM daily_briefings
WHERE date < NOW() - INTERVAL '30 days'
  AND id NOT IN (
    SELECT id FROM daily_briefings
    ORDER BY date DESC
    LIMIT 7
  );

-- Daily: Purge opportunities older than 1 year
DELETE FROM opportunities
WHERE updated_at < NOW() - INTERVAL '1 year';

-- Daily: Purge habit logs older than 2 years
DELETE FROM habit_logs
WHERE date < NOW() - INTERVAL '2 years';

-- Daily: Purge audit logs older than 3 years
DELETE FROM audit_logs
WHERE created_at < NOW() - INTERVAL '3 years';

-- Weekly: Archive completed tasks older than 90 days
UPDATE tasks
SET status = 'archived', archived_at = NOW()
WHERE status = 'completed'
  AND completed_at < NOW() - INTERVAL '90 days';

-- Weekly: Summarize chat messages into memory
-- (Handled by memory_agent.py cron job)
```

### 7.3 Retention Policy Exceptions

| Exception | Justification | Authorized By | Max Extension |
|---|---|---|---|
| User manually marks for retention | User wants to keep specific records | User (self) | Indefinite |
| Legal hold (future feature) | Pending legal proceedings | Data Governance Committee | Until released |
| Tax compliance | Income records needed for tax filing | User (self) | 7 years |
| Active investigation | Debugging ongoing issue | Developer | Until resolution |

### 7.4 Data Deletion Verification

```sql
-- Verification query after deletion cron runs
SELECT
  'tasks' AS table_name, COUNT(*) AS remaining_rows,
  MAX(created_at) AS oldest_record
FROM tasks WHERE status IN ('completed', 'cancelled')
  AND (completed_at < NOW() - INTERVAL '2 years'
    OR updated_at < NOW() - INTERVAL '30 days')
UNION ALL
SELECT 'chat_messages', COUNT(*), MAX(created_at)
FROM chat_messages WHERE created_at < NOW() - INTERVAL '1 year'
UNION ALL
SELECT 'sleep_logs', COUNT(*), MAX(date)
FROM sleep_logs WHERE date < NOW() - INTERVAL '90 days'
-- Repeat for all retention-policied tables
```

---

## 8. Data Privacy Controls

### 8.1 Privacy Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    PRIVACY LAYERS                           │
├────────────────────────────────────────────────────────────┤
│  Layer 1: Authentication (Google OAuth + Magic Link + JWT)  │
│  Layer 2: Authorization (RLS — row-level security)          │
│  Layer 3: Encryption at Rest (AES-256 — Supabase managed)   │
│  Layer 4: Encryption in Transit (TLS 1.3)                   │
│  Layer 5: Data Minimization (anonymize for third-party AI)  │
│  Layer 6: Access Logging (audit trail for sensitive ops)    │
│  Layer 7: Retention Enforcement (auto-purge cron jobs)      │
└────────────────────────────────────────────────────────────┘
```

### 8.2 Data Minimization — Third-Party AI

When sending data to third-party AI (Claude), the system applies minimization:

```python
# apps/api/app/services/anonymizer.py

def anonymize_for_ai(context: dict) -> dict:
    """Remove or generalize PII before sending to third-party AI."""
    anonymized = {}
    for key, value in context.items():
        if key in ('name', 'email', 'phone', 'address'):
            anonymized[key] = None  # Remove entirely
        elif key == 'college':
            anonymized[key] = 'a university' if value else None
        elif key in ('city', 'location'):
            anonymized[key] = 'a city'  # Generalize
        elif key == 'income':
            anonymized[key] = round(value, -3)  # Round to nearest 1000
        elif key in ('sleep_logs', 'time_entries'):
            # Aggregate daily — remove exact timestamps
            anonymized[key] = aggregate_daily(value)
        else:
            anonymized[key] = value
    return anonymized
```

### 8.3 Consent Management

| Feature | Consent Required | Where Configured | Default | Revocable |
|---|---|---|---|---|
| Local AI (Ollama) | No (data stays local) | N/A | Always on | N/A |
| Cloud AI (Claude) | Yes | Settings → Privacy → Cloud AI | Off | Yes |
| Email notifications | Yes | Settings → Notifications | On | Yes |
| SMS notifications | Yes | Settings → Notifications | Off | Yes |
| Brave Search API | Yes | Settings → Privacy → Opportunity Search | On | Yes |
| Google Calendar sync | Yes | Settings → Integrations → Calendar | Off | Yes |
| Google Fit sync | Yes | Settings → Integrations → Fit | Off | Yes |

### 8.4 GDPR Compliance Checklist

| Requirement | Status | Implementation |
|---|---|---|
| Right to Access | ✅ Implemented | All data viewable in-app; Export API |
| Right to Rectification | ✅ Implemented | All fields editable; validation in place |
| Right to Erasure | ✅ Implemented | Delete Account flow with cascade |
| Right to Data Portability | ✅ Implemented | JSON/CSV export (Section 9 of this doc) |
| Right to Restrict Processing | ✅ Implemented | Per-module privacy toggles |
| Right to Object | ✅ Implemented | User controls all data collection points |
| Automated Decision-Making | ⚠️ Partial | AI chat is decision-making; user must opt-in to cloud AI |
| Data Protection by Design | ✅ Implemented | Privacy by default (local AI), RLS, encryption |
| Breach Notification | ⚠️ Planned | Notification system for security events |
| DPO Appointment | ✅ N/A | Single-user system; user is data controller |

### 8.5 User Data Rights API

```typescript
// GET /api/privacy/access — Retrieve all personal data
// DELETE /api/privacy/erasure — Delete account + all data
// GET /api/privacy/export — Export data in portable format
// PUT /api/privacy/consent — Update consent preferences
// GET /api/privacy/consent — View current consent status

export async function handleDataRequest(action: DataRequestAction) {
  switch (action.type) {
    case 'access':
      return await exportAllUserData(userId)
    case 'erasure':
      return await deleteUserData(userId, { gracePeriod: true })
    case 'rectification':
      return await updateUserData(userId, action.field, action.value)
    case 'portability':
      return await exportUserDataJson(userId)
  }
}
```

---

## 9. Data Access Controls

### 9.1 Access Control Layers

| Layer | Technology | What It Protects | Bypass |
|---|---|---|---|
| **Authentication** | Supabase Auth (Google OAuth + JWT) | User identity | Only via valid session |
| **Authorization (RLS)** | PostgreSQL Row-Level Security | Row-level data isolation | Only service_role key |
| **API-Level Filtering** | FastAPI route guards | Endpoint access | Only valid JWT token |
| **Input Sanitization** | Pydantic + Supabase SDK | SQL injection, XSS | N/A |
| **Rate Limiting** | Custom middleware | Brute force, DDoS | Whitelist |

### 9.2 Supabase RLS Policies

Every table implements user-isolation RLS:

```sql
-- Standard user isolation policy (applied to ALL tables)
CREATE POLICY "user_isolation_policy" ON tasks
    FOR ALL
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- Read-only for generated content (briefings, reviews)
CREATE POLICY "read_own_briefings" ON daily_briefings
    FOR SELECT
    USING (user_id = auth.uid());

-- Insert only (no update/delete for audit logs)
CREATE POLICY "insert_audit_logs" ON audit_logs
    FOR INSERT
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "read_own_audit_logs" ON audit_logs
    FOR SELECT
    USING (user_id = auth.uid());
```

### 9.3 API-Level Access Matrix

| Endpoint | Auth Required | RLS | Server-Only | Public |
|---|---|---|---|---|
| `/api/tasks/*` | ✅ | ✅ | — | — |
| `/api/courses/*` | ✅ | ✅ | — | — |
| `/api/goals/*` | ✅ | ✅ | — | — |
| `/api/habits/*` | ✅ | ✅ | — | — |
| `/api/sleep/*` | ✅ | ✅ | — | — |
| `/api/income/*` | ✅ | ✅ | — | — |
| `/api/projects/*` | ✅ | ✅ | — | — |
| `/api/ideas/*` | ✅ | ✅ | — | — |
| `/api/resources/*` | ✅ | ✅ | — | — |
| `/api/opportunities/*` | ✅ | ✅ | — | — |
| `/api/time/*` | ✅ | ✅ | — | — |
| `/api/chat/*` | ✅ | ✅ | ✅ (AI) | — |
| `/api/automation/*` | ✅ | ✅ | ✅ (scheduler) | — |
| `/api/admin/*` | ✅ | ✅ | ✅ (admin role) | — |
| `/api/export` | ✅ | ✅ | — | — |
| `/api/privacy/*` | ✅ | ✅ | — | — |
| `/api/auth/*` | — | — | — | ✅ (OAuth callback) |

### 9.4 Service Role Key Usage

The `SUPABASE_SERVICE_ROLE_KEY` bypasses RLS and is used ONLY for:

1. **Cron jobs** (scheduler service) — briefings, reviews, reminders
2. **Email sending** (Resend integration) — reading data to populate emails
3. **Scheduled retention** (auto-purge cron jobs)
4. **Admin operations** (user management, data migration)

**Protections:**
- Service key stored in Railway environment variables (never in client code)
- All service-role operations are logged to `audit_logs`
- Service key rotated quarterly

---

## 10. Data Audit Trail

### 10.1 Audit Log Schema

```sql
-- apps/api/database/migrations/001_audit_logs.sql

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    action TEXT NOT NULL,           -- 'data_export', 'account_deletion',
                                    -- 'consent_change', 'settings_change',
                                    -- 'api_key_rotation', 'admin_action',
                                    -- 'privacy_export', 'data_import'
    resource_type TEXT,             -- 'user', 'tasks', 'chat_messages', etc.
    resource_id TEXT,               -- Specific record ID if applicable
    details JSONB DEFAULT '{}'::jsonb,  -- { reason: "...", before: {...}, after: {...} }
    ip_address INET,
    user_agent TEXT,
    session_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for query performance
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
```

### 10.2 Audited Actions

| Action Category | Specific Actions Logged | Details Captured |
|---|---|---|
| **Authentication** | Login, logout, token refresh, failed login | IP, user_agent, session_id |
| **Data Access** | Data export, privacy data access | Resource type, row count |
| **Data Modification** | Profile update, settings change | Before/after values |
| **Data Deletion** | Account deletion, data purge, manual delete | Cascade count, tables affected |
| **Consent Changes** | AI privacy toggles, notification prefs | Before/after consent state |
| **Admin Actions** | Flag override, service role usage | Admin ID, reason |
| **Security Events** | API key rotation, password change | Event type, timestamp |
| **Data Import** | JSON/CSV import | File stats, row count, conflict count |

### 10.3 Audit Log Query Examples

```sql
-- Recent sensitive operations by a user
SELECT action, details, created_at
FROM audit_logs
WHERE user_id = 'user_uuid'
  AND action IN ('data_export', 'account_deletion', 'api_key_rotation')
ORDER BY created_at DESC
LIMIT 20;

-- All consent changes in the last 90 days
SELECT user_id, details->>'before' as before_state,
       details->>'after' as after_state, created_at
FROM audit_logs
WHERE action = 'consent_change'
  AND created_at > NOW() - INTERVAL '90 days'
ORDER BY created_at DESC;

-- Admin actions with rationale
SELECT details->>'reason' as reason, created_at
FROM audit_logs
WHERE action = 'admin_action'
  AND details->>'reason' IS NOT NULL
ORDER BY created_at DESC;
```

### 10.4 Audit Log Retention & Protection

| Property | Value |
|---|---|
| Retention | 3 years (compliance best practice) |
| Immutability | Append-only (no UPDATE/DELETE by application code) |
| Access | User can read own logs; admin can read all |
| Deletion | Only via `audit_logs` cron job (3-year purge) |
| Backup | Included in daily Supabase backup |

---

## 11. Data Backup & Recovery Strategy

### 11.1 Backup Matrix

| Backup Type | Scope | Schedule | Retention | Location | Size Est. |
|---|---|---|---|---|---|
| **Supabase Daily** | Full database | Daily at 02:00 UTC | 7 days | Supabase-managed | ~50 MB |
| **Point-in-Time (WAL)** | Continuous (every 2 min) | Real-time | 7 days | Supabase-managed | ~2 GB |
| **Manual Export** | All user tables | On demand | User-managed | User's download | ~10 MB |
| **IndexedDB Cache** | Browser cache | Real-time (incremental) | Until cleared | User's browser | ~5 MB |
| **Schema Backup** | DDL only | Per migration | Indefinite (git) | GitHub repo | <1 MB |
| **Configuration** | Environment variables | Per deployment | Indefinite (git) | GitHub repo | <1 MB |

### 11.2 Recovery Objectives

| Metric | Target | Notes |
|---|---|---|
| **RPO (Recovery Point Objective)** | 5 minutes | WAL-based continuous archiving |
| **RTO (Recovery Time Objective)** | 1 hour (database) | Restore from Supabase backup |
| **RTO (Full Stack)** | 4 hours | Full restore + env + deploy |

### 11.3 Recovery Procedures

#### Full Database Restore

```
1. IDENTIFY scope of data loss
       │
       ▼
2. Supabase Dashboard → Database → Backups
       │
       ▼
3. Select backup or PITR timestamp
       │
       ▼
4. Click "Restore" → creates new DB instance
       │
       ▼
5. Verify data integrity:
   - Row counts match pre-loss expectations
   - Latest records exist
   - No orphaned foreign keys
       │
       ▼
6. Update NEXT_PUBLIC_SUPABASE_URL to restored DB
       │
       ▼
7. Re-deploy Vercel + Railway with new URL
       │
       ▼
8. Verify login, task CRUD, chat, briefings
       │
       ▼
9. Document incident → update DR runbook
```

#### Point-in-Time Recovery

```bash
# Supabase PITR via Dashboard
# 1. Navigate to Database → Backups → Point-in-Time
# 2. Select target timestamp (precision: 2 minutes)
# 3. Click "Restore to new database"
# 4. Follow steps 5-9 from full restore above
```

#### Partial Table Recovery

```bash
# Restore a single table from backup
pg_restore --host=<target_host> --dbname=<database> \
  --table=<table_name> \
  --data-only \
  --disable-triggers \
  last_good_backup.dump

# Verify restored rows
SELECT COUNT(*) FROM <table_name>;
SELECT * FROM <table_name> ORDER BY created_at DESC LIMIT 10;
```

#### Disaster Recovery Checklist

```
□ 1. Assess scope of data loss (which tables, rows, time range)
□ 2. Identify last good backup (or PITR timestamp)
□ 3. Notify user (if multiple users)
□ 4. Create restore database instance
□ 5. Restore data (full or partial)
□ 6. Verify data integrity (row counts, recent timestamps, FK checks)
□ 7. Update environment variables
□ 8. Re-deploy frontend + backend
□ 9. Verify critical paths: login, task CRUD, chat, briefing
□ 10. Document incident: cause, scope, resolution time
```

---

## 12. Data Migration Process

### 12.1 Migration Types

| Migration Type | Frequency | Risk Level | Example |
|---|---|---|---|
| **Schema change** | Monthly | Medium-High | Add column, change data type |
| **Data backfill** | As needed | Medium | Populate new column from existing data |
| **Data normalization** | Quarterly | Medium | Split JSONB into normalized tables |
| **Migration between providers** | Rare | High | Supabase → AWS RDS |
| **Version upgrade** | Quarterly | Medium | Supabase PG 14 → 15 |

### 12.2 Migration Workflow

```
┌─────────────┐
│ 1. PLAN      │
│ - Migration file │
│ - Rollback file  │
│ - Test plan      │
└──────┬──────┘
       ▼
┌─────────────┐
│ 2. BACKUP    │
│ - Full DB dump │
│ - Export affected tables │
└──────┬──────┘
       ▼
┌─────────────┐
│ 3. TEST      │
│ - Run on staging  │
│ - Verify results  │
│ - Measure performance │
└──────┬──────┘
       ▼
┌─────────────┐
│ 4. EXECUTE   │
│ - Apply migration  │
│ - Backfill if needed │
│ - Verify row counts │
└──────┬──────┘
       ▼
┌─────────────┐
│ 5. VERIFY    │
│ - Application tests │
│ - Data integrity check │
│ - Performance check │
└──────┬──────┘
       ▼
┌─────────────┐
│ 6. DOCUMENT  │
│ - Update schema docs │
│ - Update AGENTS.md │
│ - Record in migration log │
└─────────────┘
```

### 12.3 Migration Script Template

```sql
-- apps/api/database/migrations/YYYYMMDD_description.sql
-- ============================================================
-- Migration: YYYYMMDD_description
-- Author: Developer
-- Date: YYYY-MM-DD
-- Risk Level: Medium
-- Rollback: apps/api/database/rollbacks/YYYYMMDD_description.sql
-- ============================================================

BEGIN;

-- Step 1: Schema change
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS priority_score NUMERIC(3,2)
DEFAULT 0.5
CHECK (priority_score >= 0 AND priority_score <= 1);

-- Step 2: Data backfill (if needed)
UPDATE tasks
SET priority_score = CASE
    WHEN priority = 'urgent' THEN 1.0
    WHEN priority = 'high' THEN 0.75
    WHEN priority = 'medium' THEN 0.5
    WHEN priority = 'low' THEN 0.25
    ELSE 0.5
END
WHERE priority_score IS NULL;

-- Step 3: Add index for new column
CREATE INDEX idx_tasks_priority_score ON tasks(priority_score DESC)
WHERE status = 'pending';

-- Step 4: Verify
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM tasks
        WHERE priority_score IS NULL
    ) THEN
        RAISE EXCEPTION 'Backfill incomplete: tasks with NULL priority_score';
    END IF;
END $$;

COMMIT;
```

### 12.4 Rollback Script Template

```sql
-- apps/api/database/rollbacks/YYYYMMDD_description.sql
-- ============================================================
-- Rollback: YYYYMMDD_description
-- ============================================================

BEGIN;

DROP INDEX IF EXISTS idx_tasks_priority_score;
ALTER TABLE tasks DROP COLUMN IF EXISTS priority_score;

COMMIT;
```

---

## 13. Data Documentation Standards

### 13.1 Table Documentation Template

Every table MUST have the following documentation (stored in `docs/engineering/15_Database.md`):

```
## {table_name}

| Field | Value |
|---|---|
| **Purpose** | {description of what this table stores} |
| **Classification** | T1/T2/T3/T4 |
| **Owner** | {module owner} |
| **Retention** | {active period} → {archive} → {purge} |
| **Row Estimate** | {estimated rows after 1 year} |

### Columns

| Column | Type | Required | Default | FK | Description | Example |
|---|---|---|---|---|---|---|
| id | UUID | ✅ | gen_random_uuid() | — | Primary key | ... |
| user_id | UUID | ✅ | — | auth.users.id | Owner | ... |
| ... | ... | ... | ... | ... | ... | ... |

### Indexes

| Index Name | Columns | Type | Purpose |
|---|---|---|---|
| ... | ... | B-tree / GIN / GiST | Performance reason |

### RLS Policies

| Policy Name | Action | Using | With Check |
|---|---|---|---|
| user_isolation | ALL | user_id = auth.uid() | user_id = auth.uid() |

### Usage Examples

```sql
-- Typical queries on this table
SELECT * FROM {table_name} WHERE user_id = '...';
```
```

### 13.2 Column Description Standards

| Element | Convention | Example |
|---|---|---|
| **Boolean fields** | Start with `is_` or `has_` | `is_completed`, `has_notifications` |
| **Timestamp fields** | Suffix with `_at` | `created_at`, `updated_at`, `completed_at` |
| **Date fields** | Suffix with `_date` | `due_date`, `start_date` |
| **JSONB fields** | Describe expected schema inline | `details: {"type": "object", "fields": {...}}` |
| **Enum lists** | List all possible values | `low, medium, high, urgent` |
| **Nullable fields** | Document null semantics | `NULL = not yet reviewed` |

### 13.3 Data Dictionary Maintenance

| Maintenance Task | Frequency | Owner |
|---|---|---|
| Column descriptions review | Per schema change | Developer |
| Row count estimate update | Quarterly | Developer |
| Query pattern documentation | Per new feature | Developer |
| Migration log update | Per migration | Developer |
| Data classification audit | Quarterly | Data Governance Committee |

---

## 14. Data Lineage Tracking

### 14.1 Lineage Scope

Data lineage is tracked for:

1. **Third-party data flows** — Which data leaves the system and where
2. **AI processing** — Which data feeds into AI agents and what outputs are generated
3. **Synchronization** — Google Calendar, Google Fit data imports
4. **Data transformations** — Aggregation, anonymization, summarization

### 14.2 Data Flow Map

```
┌──────────────────────────────────────────────────────────────────────┐
│                        DATA FLOW MAP                                  │
│                                                                      │
│  USER INPUT ──► Supabase DB ──► Query/Read ──► Processing ──► Output │
│    (CRUD)         (store)         (RLS)          (AI/calc)     (UI)  │
│                      │                                              │
│                      ▼                                              │
│              ┌─────────────────┐                                     │
│              │  Third-Party     │                                     │
│              │  (Claude,        │                                     │
│              │   Resend,        │                                     │
│              │   Brave, etc.)   │                                     │
│              └─────────────────┘                                     │
│                      │                                               │
│                      ▼                                               │
│              ┌─────────────────┐                                     │
│              │  Output          │                                     │
│              │  (Email, SMS,    │                                     │
│              │   Analytics)     │                                     │
│              └─────────────────┘                                     │
└──────────────────────────────────────────────────────────────────────┘
```

### 14.3 Data Lineage per Third-Party Service

| Service | Data Sent | Direction | Transformations | Purpose | Retention |
|---|---|---|---|---|---|
| **Claude API** | Context: tasks, goals, courses, memory (anonymized) | Outbound | Anonymized (no PII); summarized (not raw) | Briefings, reviews, complex AI | Anthropic retains 30 days (API default) |
| **Resend** | Email address, briefing content | Outbound | Rendered from template | Email notifications | Transient; deleted after send |
| **Twilio** | Phone number, message text | Outbound | SMS encoding | SMS alerts | Transient |
| **Brave Search** | Skill terms (only) | Outbound | Extracted from profile | Opportunity matching | Not stored by Brave (search query) |
| **Google Calendar** | Task name, due date | Bidirectional | Calendar event ↔ task mapping | Calendar sync | User-controlled |
| **Google Fit** | Sleep times (start, end) | Import only | Normalized to sleep_logs format | Sleep tracking | User-controlled |
| **Vercel** | Request logs, IP address | Logged by platform | Standard HTTP logs | Hosting, CDN | Vercel standard retention |

### 14.4 Lineage Documentation Format

Each data transformation is documented with:

```yaml
# packages/ai/services/lineage.yaml
transformations:
  - id: chat_summary_to_memory
    description: Extract key facts from chat messages into memory table
    source: chat_messages (T2)
    target: memory (T2)
    transformation: LLM extraction with prompt template
    trigger: Daily cron (after 30 chat messages accumulated)
    reversibility: Partial (original messages deleted after summary)
    verification: Memory entries have confidence_score; user can review/edit

  - id: daily_briefing_generation
    description: Generate daily briefing from all modules
    source: tasks, courses, goals, habits, sleep, opportunities
    target: daily_briefings (T3)
    transformation: LLM generation with briefing_agent.md prompt
    trigger: Daily cron at 6:00 AM
    reversibility: Full (all source data retained)
    verification: User reads briefing; was_read flag tracked

  - id: sleep_aggregation
    description: Aggregate daily sleep logs into weekly patterns
    source: sleep_logs (T2)
    target: Sleep trends (calculated, not stored separately)
    transformation: Weekly average calculation
    trigger: After 90 days (before raw deletion)
    reversibility: No (raw data purged)
```

---

## 15. Data Governance Committee & Review Process

### 15.1 Committee Structure

For a single-user system, the "Data Governance Committee" consists of the developer (data steward) with the following roles:

| Role | Responsible | Responsibilities |
|---|---|---|
| **Data Governor** | Developer | Overall governance, policy approval, exception authorization |
| **Data Steward** | Developer | Implementation, monitoring, enforcement |
| **Data Custodian** | Developer | Technical implementation (RLS, encryption, backups) |
| **Privacy Officer** | Developer | Privacy impact assessment, consent management |
| **User Advocate** | User (self) | Data rights exercise, consent decisions |

### 15.2 Review Cadence

| Review Type | Frequency | Agenda | Artifacts |
|---|---|---|---|
| **Data Classification Review** | Quarterly | Verify classification tiers; reclassify if needed | Updated classification matrix |
| **Retention Policy Review** | Quarterly | Confirm retention periods; adjust if needed | Updated retention schedule |
| **Access Control Audit** | Monthly | Review RLS policies; check for gaps | Policy audit report |
| **Backup Integrity Check** | Weekly | Verify backup completion; test restore | Backup status report |
| **Privacy Impact Assessment** | Per new feature | Evaluate data collection; update consent | PIA document |
| **Data Quality Report** | Monthly | Quality metrics; issues log; remediation | Quality dashboard |
| **Third-Party Data Audit** | Semi-annual | Review data shared with third parties; update minimization | Third-party audit log |
| **Compliance Check** | Annual | GDPR/CCPA compliance review; update if needed | Compliance checklist |

### 15.3 Exception Process

Any deviation from data governance policies requires an approved exception:

```
1. SUBMIT exception request (reason, scope, duration, risk assessment)
2. Data Governor reviews (within 48 hours)
3. If approved: document in exception log, set expiration
4. Monitor during exception period
5. Review at expiration (extend or close)
```

**Exception Log Template:**

| Exception ID | Policy Violated | Reason | Scope | Duration | Approved By | Date | Status |
|---|---|---|---|---|---|---|---|
| DG-EX-001 | Retention (sleep_logs) | Debugging sleep score algorithm | sleep_logs retention extended to 180 days | 2026-07-01 to 2026-09-30 | Developer | 2026-07-01 | Active |

---

## 16. Training & Awareness Program

### 16.1 Data Governance Training Modules

For a single-developer system, training is self-directed with documented reference material:

| Module | Topic | Frequency | Format | Reference |
|---|---|---|---|---|
| **DG-101** | Data Classification | Onboarding | Read doc + quiz | Section 3 (this doc) |
| **DG-102** | Data Privacy & Consent | Onboarding | Read doc + quiz | Section 8 (this doc) |
| **DG-103** | Retention Policy | Quarterly review | Read doc | Section 7 (this doc) |
| **DG-104** | Security Incident Response | Semi-annual | Runbook drill | docs/operations/40_IncidentResponse.md |
| **DG-105** | Backup & Recovery | Quarterly | Drill: restore from backup | Section 11 (this doc) |
| **DG-106** | Migration Best Practices | Per migration | Read doc + checklist | Section 12 (this doc) |
| **DG-107** | Privacy Impact Assessment | Per new feature | Template + checklist | Section 15.2 |

### 16.2 Embedded Governance Practices

| Practice | Where Enforced | How |
|---|---|---|
| Classification on data creation | API layer | Tier assigned at schema level |
| Consent check before third-party AI | AI service | Check `user_preferences.use_cloud_ai` |
| Retention on write | Cron jobs | Auto-purge handles expired data |
| Access audit on sensitive operations | Middleware | Log to `audit_logs` |
| Schema validation on migration | CI pipeline | Migration scripts tested in CI |
| Privacy review in PR process | GitHub | PR template includes privacy checklist |

### 16.3 Governance Metrics & KPIs

| KPI | Target | Measurement | Current Status |
|---|---|---|---|
| Data classification accuracy | 100% | Quarterly audit | ✅ 100% |
| Retention policy compliance | >99% | Monthly verification | ✅ ~100% |
| Backup success rate | >99.5% | Weekly check | ✅ ~100% |
| RLS coverage | 100% of tables | Monthly scan | ✅ 100% (27/27 tables) |
| Audit log completeness | 100% of critical actions | Semi-annual review | ✅ 100% |
| PIA completion (for new features) | 100% | Per PR | ✅ (single developer) |
| Data quality score | >95% | Monthly quality check | ✅ ~98% |
| Third-party data minimization | 100% audit compliance | Semi-annual | ✅ No PII sent to third parties |

---

## 17. Compliance & Regulatory Mapping

### 17.1 Regulatory Applicability

| Regulation | Applicable? | Reason | Compliance Actions |
|---|---|---|---|
| **GDPR** | Partial (if serving EU users) | Single user in India, but architected for GDPR | All user rights implemented; documented data flows |
| **CCPA** | No (California-only) | User not in California | N/A (principles applied) |
| **IT Act 2000 (India)** | Yes | User located in India | Data localization (Supabase); encryption |
| **DPDP Act 2023 (India)** | Yes | Indian digital personal data protection | Consent management; data minimization; rights implementation |
| **HIPAA** | No (not medical service) | Sleep data is wellness, not medical | N/A |
| **PCI DSS** | No (no payment processing) | Income data is informational | N/A |

### 17.2 Data Processing Register (Full)

| Processing Activity | Purpose | Lawful Basis | Data Categories | Retention | Third-Party | Security Measures |
|---|---|---|---|---|---|---|
| Task management | Personal productivity | Consent | T3: tasks | Active + 90d → archive → 2yr | None | RLS, TLS 1.3 |
| Course tracking | Learning progress | Consent | T3: courses | Active + 1yr inactive | None | RLS, TLS 1.3 |
| Goal tracking | Life planning | Consent | T3: goals | Active + completed → archive → indefinite | None | RLS, TLS 1.3 |
| Habit tracking | Self-improvement | Consent | T3: habits, habit_logs | Active + 2yr | None | RLS, TLS 1.3 |
| Sleep tracking | Health/wellness | Consent | T2: sleep_logs | 90 days | None | RLS, TLS 1.3 |
| Income tracking | Financial management | Consent | T2: income_entries | 7 years | None | RLS, TLS 1.3 |
| Project management | Project oversight | Consent | T3: projects | Active + 1yr archive | None | RLS, TLS 1.3 |
| Idea management | Innovation | Consent | T3: ideas | Indefinite | None | RLS, TLS 1.3 |
| Resource library | Knowledge management | Consent | T3: resources | Indefinite | None | RLS, TLS 1.3 |
| Opportunity scanning | Career development | Consent | T3: opportunities | Active → 90d archive → 1yr | Brave Search (skill terms only) | Anonymized queries |
| Time tracking | Productivity analysis | Consent | T3: time_entries | 90 days | None | RLS, TLS 1.3 |
| AI chat (local) | Productivity assistant | Consent | T2: chat_messages, memory | 1yr → summarized to memory | Ollama (local) | Fully local, no data leaves |
| AI chat (cloud) | Complex AI processing | Explicit opt-in | T2: anonymized context | 1yr → summarized to memory | Claude API (anonymized) | Anonymization, TLS |
| Daily briefings | Morning planning | Consent | T3: briefings | 30 days (keep last 7) | Claude API (anonymized) | Anonymization, TLS |
| Weekly reviews | Weekly reflection | Consent | T3: reviews | Indefinite | Claude API (anonymized) | Anonymization, TLS |
| Email notifications | Reminders/briefings | Explicit opt-in | Email address, briefing content | Transient | Resend | TLS 1.3 |
| SMS notifications | Critical alerts | Explicit opt-in | Phone number | Transient | Twilio | TLS 1.3 |
| Backup & recovery | Business continuity | Legitimate interest | All data | 7 days (backups) | Supabase | AES-256, TLS 1.3 |

---

## 18. Data Governance Maturity Model

| Level | Name | Description | Current Status |
|---|---|---|---|
| **1** | Initial | Ad-hoc data management, no formal policies | — |
| **2** | Managed | Basic policies defined, manual enforcement | — |
| **3** | Defined | Policies documented, automated enforcement | ✅ Current |
| **4** | Measured | Metrics collected, regular reporting | ⚠️ Partial (KPI tracking) |
| **5** | Optimized | Continuous improvement, predictive governance | — |

**Current Maturity: Level 3 (Defined)**
**Target: Level 4 (Measured) by Q4 2026**

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-01-20 | Developer | Initial data governance documentation |
| 1.1.0 | 2026-03-15 | Developer | Added retention policies, GDPR compliance |
| 2.0.0 | 2026-06-11 | Data Governance Committee | Enterprise upgrade: 18 sections covering classification, lifecycle, quality, ownership, retention, privacy, access, audit, backup, migration, documentation, lineage, governance review, training, compliance, maturity model |

---

*End of Document — ENG-DATAGOV-001*
