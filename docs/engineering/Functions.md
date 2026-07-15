# Database Functions — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ENG-FNC-007 |
| **Version** | 1.0.0 |
| **Status** | Approved |
| **Date** | 2026-07-10 |
| **Classification** | Internal |
| **Owner** | Developer |
| **Related Docs** | [Triggers.md](Triggers.md), [RLS.md](RLS.md) |

---

## 1. Executive Summary

Database functions encapsulate reusable SQL logic for triggers, RLS helpers, reporting queries, and data maintenance. All functions are written in PL/pgSQL and follow a strict naming convention.

---

## 2. Function Naming Convention

```
trigger_{purpose}     -- Trigger functions
fn_{module}_{action}  -- Utility functions
rls_{table}_access    -- RLS helper functions
```

---

## 3. Function Catalog

### 3.1 Trigger: updated_at

```sql
CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

**Purpose:** Automatically set `updated_at` timestamp on row update.
**Applied to:** 11 tables with `updated_at` column (tasks, courses, goals, etc.)

---

### 3.2 RLS: User ID Helper

```sql
CREATE OR REPLACE FUNCTION rls_user_id()
RETURNS UUID AS $$
  SELECT auth.uid();
$$ LANGUAGE SQL STABLE;
```

**Purpose:** Returns the current authenticated user ID for RLS policies. Used in policy expressions.

---

### 3.3 RLS: Is Owner Check

```sql
CREATE OR REPLACE FUNCTION rls_is_owner(record_user_id UUID)
RETURNS BOOLEAN AS $$
  SELECT auth.uid() = record_user_id;
$$ LANGUAGE SQL STABLE;
```

**Purpose:** Standardized owner check across all RLS policies.

---

### 3.4 Report: Weekly Summary

```sql
CREATE OR REPLACE FUNCTION fn_weekly_summary(
  p_user_id UUID,
  p_week_start DATE
)
RETURNS JSONB AS $$
DECLARE
  result JSONB;
BEGIN
  SELECT jsonb_build_object(
    'tasks_completed', COUNT(*) FILTER (WHERE t.status = 'completed' AND t.completed_at >= p_week_start),
    'tasks_missed', COUNT(*) FILTER (WHERE t.status = 'missed'),
    'courses_studied', COALESCE(SUM(ts.duration_minutes), 0),
    'income_earned', COALESCE(SUM(il.amount), 0),
    'sleep_avg', ROUND(AVG(sl.sleep_score), 0),
    'habit_consistency', (
      SELECT COUNT(*) FILTER (WHERE hl.completed = TRUE) * 100.0 / 7
      FROM habit_logs hl
      JOIN habits h ON h.id = hl.habit_id
      WHERE h.user_id = p_user_id AND hl.date >= p_week_start AND hl.date < p_week_start + 7
    )
  ) INTO result
  FROM tasks t
  LEFT JOIN study_sessions ts ON ts.user_id = t.user_id AND ts.started_at >= p_week_start
  LEFT JOIN income_logs il ON il.user_id = t.user_id AND il.date >= p_week_start
  LEFT JOIN sleep_logs sl ON sl.user_id = t.user_id AND sl.date >= p_week_start
  WHERE t.user_id = p_user_id AND t.created_at >= p_week_start;

  RETURN result;
END;
$$ LANGUAGE plpgsql STABLE;
```

**Purpose:** Pre-built weekly report aggregation for the Weekly Review agent.

---

### 3.5 Dashboard: Active State

```sql
CREATE OR REPLACE FUNCTION fn_dashboard_state(p_user_id UUID)
RETURNS JSONB AS $$
DECLARE
  result JSONB;
BEGIN
  SELECT jsonb_build_object(
    'pending_tasks', COUNT(*) FILTER (WHERE t.status = 'pending'),
    'overdue_tasks', COUNT(*) FILTER (WHERE t.due_date < NOW() AND t.status = 'pending'),
    'active_courses', COUNT(*) FILTER (WHERE c.status = 'active'),
    'active_goals', COUNT(*) FILTER (WHERE g.status = 'active'),
    'habit_streak', COALESCE(MAX(h.current_streak), 0),
    'next_deadlines', (
      SELECT jsonb_agg(jsonb_build_object('title', t.title, 'due_date', t.due_date))
      FROM tasks t WHERE t.user_id = p_user_id AND t.status = 'pending'
      ORDER BY t.due_date LIMIT 5
    )
  ) INTO result
  FROM tasks t
  CROSS JOIN courses c ON c.user_id = p_user_id
  CROSS JOIN goals g ON g.user_id = p_user_id
  CROSS JOIN habits h ON h.user_id = p_user_id
  WHERE t.user_id = p_user_id;

  RETURN result;
END;
$$ LANGUAGE plpgsql STABLE;
```

**Purpose:** Pre-computed dashboard state snapshot for the working memory context assembly.

---

### 3.6 Maintenance: Memory Decay

```sql
CREATE OR REPLACE FUNCTION fn_decay_memories(
  p_user_id UUID DEFAULT NULL,
  p_decay_factor FLOAT DEFAULT 0.8,
  p_archive_threshold FLOAT DEFAULT 0.1,
  p_forget_threshold FLOAT DEFAULT 0.05
)
RETURNS TABLE(decayed INT, archived INT, deleted INT) AS $$
DECLARE
  v_decayed INT := 0;
  v_archived INT := 0;
  v_deleted INT := 0;
BEGIN
  -- Apply decay to old memories
  UPDATE aria_memory
  SET confidence = confidence * p_decay_factor
  WHERE (p_user_id IS NULL OR user_id = p_user_id)
    AND last_referenced_at < NOW() - INTERVAL '30 days'
    AND confidence > p_archive_threshold;

  GET DIAGNOSTICS v_decayed = ROW_COUNT;

  -- Archive near-forgotten memories (mark as archive via status field)
  -- Delete below-forgotten memories
  DELETE FROM aria_memory
  WHERE confidence < p_forget_threshold
    AND (p_user_id IS NULL OR user_id = p_user_id);

  GET DIAGNOSTICS v_deleted = ROW_COUNT;

  RETURN QUERY SELECT v_decayed, v_archived, v_deleted;
END;
$$ LANGUAGE plpgsql;
```

**Purpose:** Weekly maintenance function that decays memory confidence scores and purges forgotten memories.

---

## 4. Function Migration

Functions are version-controlled alongside table schemas in migration files:

```
supabase/
└── migrations/
    ├── 20260601000000_initial_schema.sql    -- Tables + constraints
    ├── 20260611000000_functions.sql          -- All functions
    └── 20260620000000_triggers.sql           -- Triggers
```

---

## 5. Security

| Function | Security Type | Rationale |
|---|---|---|
| trigger_set_updated_at | INVOKER | Runs as table owner |
| rls_user_id | STABLE | Read-only, no side effects |
| rls_is_owner | STABLE | Read-only, no side effects |
| fn_weekly_summary | STABLE | Read-only aggregation |
| fn_dashboard_state | STABLE | Read-only aggregation |
| fn_decay_memories | SECURITY DEFINER | Needs delete privileges |

---

## 6. Related Documents

| Document | Description |
|---|---|
| [Triggers.md](Triggers.md) | Trigger documentation |
| [RLS.md](RLS.md) | RLS deep dive |
| [MigrationStrategy.md](MigrationStrategy.md) | Schema migration approach |
