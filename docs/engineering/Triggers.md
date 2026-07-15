# Trigger Documentation — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ENG-TRG-006 |
| **Version** | 1.0.0 |
| **Status** | Approved |
| **Date** | 2026-07-10 |
| **Classification** | Internal |
| **Owner** | Developer |
| **Related Docs** | [Functions.md](Functions.md), [HistoryTables.md](HistoryTables.md) |

---

## 1. Executive Summary

Database triggers automate `updated_at` timestamp management and audit logging on mutation operations. Currently, the system uses a lightweight approach — `updated_at` is managed at the application layer via API route handlers. This document defines the trigger strategy for moving timestamp management and audit logging to the database layer.

---

## 2. Trigger: updated_at Timestamp

```sql
-- Generic updated_at trigger function
CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to tables with updated_at column
CREATE TRIGGER set_updated_at
  BEFORE UPDATE ON tasks
  FOR EACH ROW
  EXECUTE FUNCTION trigger_set_updated_at();

CREATE TRIGGER set_updated_at
  BEFORE UPDATE ON courses
  FOR EACH ROW
  EXECUTE FUNCTION trigger_set_updated_at();

CREATE TRIGGER set_updated_at
  BEFORE UPDATE ON goals
  FOR EACH ROW
  EXECUTE FUNCTION trigger_set_updated_at();

CREATE TRIGGER set_updated_at
  BEFORE UPDATE ON resources
  FOR EACH ROW
  EXECUTE FUNCTION trigger_set_updated_at();

CREATE TRIGGER set_updated_at
  BEFORE UPDATE ON habits
  FOR EACH ROW
  EXECUTE FUNCTION trigger_set_updated_at();
```

### Tables with `updated_at` column

| Table | Trigger Applied |
|---|---|
| users_profile | ✅ |
| tasks | ✅ |
| courses | ✅ |
| resources | ✅ |
| ideas | ✅ |
| goals | ✅ |
| roadmaps | ✅ |
| income_sources | ✅ |
| projects | ✅ |
| academic_subjects | ✅ |
| habits | ✅ |

### Tables WITHOUT `updated_at` (immutable logs)

| Table | Rationale |
|---|---|
| subtasks | Append-only; no updates expected |
| task_dependencies | Append-only; delete/drop relations |
| youtube_saves | Status changes only (SET NOT NULL) |
| roadmap_updates | Append-only audit log |
| income_logs | Append-only |
| habit_logs | Append-only; daily entry |
| sleep_logs | Append-only; daily entry |
| time_logs | Append-only |
| chat_messages | Append-only |
| aria_memory | Append-only |
| daily_briefings | Append-only |
| weekly_reviews | Append-only |
| study_sessions | Append-only |
| daily_logs | Append-only |
| marks | Append-only |

---

## 3. Trigger: Audit Logging

```sql
-- Audit trigger function — logs all mutations to audit_log table
CREATE OR REPLACE FUNCTION trigger_audit_log()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO audit_log (
    table_name,
    operation,
    record_id,
    old_data,
    new_data,
    changed_by,
    changed_at
  ) VALUES (
    TG_TABLE_NAME,
    TG_OP,
    COALESCE(NEW.id, OLD.id),
    CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN row_to_json(OLD) ELSE NULL END,
    CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW) ELSE NULL END,
    auth.uid(),
    NOW()
  );
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Apply to sensitive tables
CREATE TRIGGER audit_log_changes
  AFTER INSERT OR UPDATE OR DELETE ON tasks
  FOR EACH ROW EXECUTE FUNCTION trigger_audit_log();

CREATE TRIGGER audit_log_changes
  AFTER INSERT OR UPDATE OR DELETE ON goals
  FOR EACH ROW EXECUTE FUNCTION trigger_audit_log();
```

---

## 4. Trigger Management

| Operation | Method | Example |
|---|---|---|
| List triggers | SQL | `SELECT * FROM information_schema.triggers;` |
| Enable trigger | SQL | `ALTER TABLE tasks ENABLE TRIGGER set_updated_at;` |
| Disable trigger | SQL | `ALTER TABLE tasks DISABLE TRIGGER set_updated_at;` |
| Drop trigger | SQL | `DROP TRIGGER IF EXISTS set_updated_at ON tasks;` |

---

## 5. Trigger Naming Convention

```
{action}_{table}    -- set_updated_at, audit_log_changes
```

---

## 6. Performance Considerations

| Concern | Mitigation |
|---|---|
| Trigger overhead per mutation | < 1ms for updated_at; < 3ms for audit log |
| Audit log growth | Retention policy: 90 days active, archive after |
| Trigger recursion | Use `TG_OP` to prevent infinite loops |
| SECURITY DEFINER | Audit trigger runs with definer privileges |

---

## 7. Related Documents

| Document | Description |
|---|---|
| [Functions.md](Functions.md) | Reusable function catalog |
| [HistoryTables.md](HistoryTables.md) | Audit log table design |
