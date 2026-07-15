# History & Audit Tables — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ENG-HST-012 |
| **Version** | 1.0.0 |
| **Status** | Approved |
| **Date** | 2026-07-10 |
| **Classification** | Internal |
| **Owner** | Developer |
| **Related Docs** | [Triggers.md](Triggers.md), [Schema.md](Schema.md), [AuditLogs.md](../operations/AuditLogs.md) |

---

## 1. Executive Summary

History tables capture every mutation on user data for audit, rollback, and temporal analysis. The system uses a lightweight audit log pattern — a single `audit_log` table records all INSERT, UPDATE, and DELETE operations across tracked tables, with JSON snapshots of old and new values.

---

## 2. Audit Log Table Schema

```sql
CREATE TABLE audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  table_name TEXT NOT NULL,
  operation TEXT NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
  record_id UUID NOT NULL,
  old_data JSONB,
  new_data JSONB,
  changed_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  changed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_audit_log_table_operation ON audit_log(table_name, operation);
CREATE INDEX idx_audit_log_record_id ON audit_log(record_id);
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_changed_at ON audit_log(changed_at DESC);
```

---

## 3. Data Retention for Audit Logs

| Time Period | Retention | Action |
|---|---|---|
| 0-90 days | Full detail | Available for queries |
| 90-365 days | Compressed summary | Monthly aggregate only |
| > 365 days | Deleted | Purge via cron job |

**Cleanup job (monthly):**

```sql
DELETE FROM audit_log
WHERE changed_at < NOW() - INTERVAL '365 days'
RETURNING count(*) AS purged_records;
```

---

## 4. Query Patterns

### 4.1 Record History

```sql
-- Full audit trail for a specific record
SELECT
  changed_at,
  operation,
  old_data,
  new_data,
  changed_by
FROM audit_log
WHERE table_name = 'tasks' AND record_id = 'abc-123'
ORDER BY changed_at DESC;
```

### 4.2 User Activity Timeline

```sql
-- All changes made by a user in the last 7 days
SELECT
  changed_at,
  table_name,
  operation,
  record_id
FROM audit_log
WHERE user_id = 'user-uuid'
  AND changed_at >= NOW() - INTERVAL '7 days'
ORDER BY changed_at DESC;
```

### 4.3 Undo/Reconstruct Past State

```sql
-- Reconstruct task state as of a specific timestamp
WITH task_history AS (
  SELECT
    new_data,
    operation,
    changed_at,
    ROW_NUMBER() OVER (PARTITION BY record_id ORDER BY changed_at DESC) AS rn
  FROM audit_log
  WHERE table_name = 'tasks'
    AND record_id = 'abc-123'
    AND changed_at <= '2026-06-15 12:00:00'
)
SELECT new_data FROM task_history WHERE rn = 1;
```

---

## 5. History Tables (Table-Specific)

For frequently accessed historical data, dedicated history tables provide faster queries than the generic audit_log:

```sql
CREATE TABLE task_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  status_before TEXT,
  status_after TEXT,
  changed_by TEXT, -- 'user' | 'system' | 'cron' | 'aria'
  changed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_task_history_task_id ON task_history(task_id);
CREATE INDEX idx_task_history_changed_at ON task_history(changed_at DESC);
```

### Status Change Tracking

The most common audit need is tracking status changes:

```sql
-- Track when tasks are completed or missed
CREATE TABLE status_changes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  table_name TEXT NOT NULL,
  record_id UUID NOT NULL,
  from_status TEXT,
  to_status TEXT NOT NULL,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  changed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_status_changes_record ON status_changes(table_name, record_id);
```

---

## 6. Temporal Query Patterns

```sql
-- Find all tasks completed in a date range (via audit trail)
SELECT DISTINCT record_id
FROM audit_log
WHERE table_name = 'tasks'
  AND operation = 'UPDATE'
  AND new_data->>'status' = 'completed'
  AND changed_at BETWEEN '2026-06-01' AND '2026-06-30';
```

---

## 7. GDPR Compliance

For GDPR data export requests:

```sql
-- Export all data + audit trail for a specific user
SELECT * FROM audit_log
WHERE user_id = 'requested-user-uuid'
ORDER BY changed_at DESC;

-- For deletion: cascade delete handles user data
-- Audit log retains anonymized entries
UPDATE audit_log
SET changed_by = NULL, user_id = NULL, old_data = '{"redacted": true}', new_data = '{"redacted": true}'
WHERE user_id = 'deleted-user-uuid';
```

---

## 8. Performance & Storage

| Metric | Estimate | Note |
|---|---|---|
| Daily audit entries | ~500 per active user | Per-user average |
| Entry size | ~500 bytes avg | JSON overhead |
| Monthly storage | ~75 MB per 100 users | Acceptable |
| Query time (indexed) | < 50ms | With proper indexes |

---

## 9. Related Documents

| Document | Description |
|---|---|
| [Triggers.md](Triggers.md) | Trigger-based audit logging |
| [Schema.md](Schema.md) | Table schemas that feed audit log |
| [Compliance.md](../security/25_Compliance.md) | GDPR/SOC 2 compliance requirements |
