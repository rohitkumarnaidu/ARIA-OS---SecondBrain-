# Database Views — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ENG-VWS-004 |
| **Version** | 1.0.0 |
| **Status** | Approved |
| **Date** | 2026-07-10 |
| **Classification** | Internal |
| **Owner** | Developer |
| **Related Docs** | [Schema.md](Schema.md), [MaterializedViews.md](MaterializedViews.md) |

---

## 1. Executive Summary

Database views provide logical abstractions over raw tables, simplifying dashboard queries, report generation, and cross-module aggregations. Currently, the system uses no persistent SQL views — all aggregation is handled at the application layer (Python/FastAPI). This document defines the view strategy for future performance optimization.

---

## 2. Current Approach

**Decision:** No SQL views in production currently. Aggregations are computed in application code.

**Rationale:**
- Supabase PostgreSQL views cannot be indexed independently (must use materialized views)
- Application-layer aggregation is simpler to version-control and test
- Current query volumes (< 100 req/s) do not require view optimization

---

## 3. Proposed View Catalog

### 3.1 Reporting Views

```sql
-- v_dashboard_summary: Daily snapshot for dashboard
CREATE OR REPLACE VIEW v_dashboard_summary AS
SELECT
  t.user_id,
  DATE(t.created_at) AS date,
  COUNT(*) FILTER (WHERE t.status = 'pending') AS pending_tasks,
  COUNT(*) FILTER (WHERE t.status = 'completed') AS completed_tasks,
  COUNT(*) FILTER (WHERE t.status = 'missed') AS missed_tasks,
  COUNT(*) FILTER (WHERE t.due_date < NOW() AND t.status = 'pending') AS overdue_tasks
FROM tasks t
GROUP BY t.user_id, DATE(t.created_at);
```

### 3.2 Academic Performance View

```sql
-- v_academic_performance: Per-semester GPA calculation
CREATE OR REPLACE VIEW v_academic_performance AS
SELECT
  s.user_id,
  s.semester,
  COUNT(s.id) AS subjects_count,
  ROUND(AVG(s.marks_scored / NULLIF(s.max_marks, 0) * 100), 1) AS avg_percentage,
  COUNT(*) FILTER (WHERE s.at_risk_flag = TRUE) AS at_risk_count
FROM academic_subjects s
GROUP BY s.user_id, s.semester;
```

### 3.3 Weekly Activity View

```sql
-- v_weekly_activity: Weekly productivity metrics
CREATE OR REPLACE VIEW v_weekly_activity AS
SELECT
  t.user_id,
  DATE_TRUNC('week', t.created_at)::DATE AS week_start,
  COUNT(*) FILTER (WHERE t.status = 'completed') AS tasks_done,
  COUNT(*) FILTER (WHERE t.status = 'missed') AS tasks_missed,
  SUM(t.actual_minutes) AS total_minutes
FROM tasks t
GROUP BY t.user_id, DATE_TRUNC('week', t.created_at);
```

### 3.4 Income Trends View

```sql
-- v_income_trends: Monthly income aggregation
CREATE OR REPLACE VIEW v_income_trends AS
SELECT
  il.user_id,
  DATE_TRUNC('month', il.date)::DATE AS month,
  COUNT(il.id) AS entries,
  SUM(il.amount) AS total_amount,
  SUM(il.hours_spent) AS total_hours,
  ROUND(SUM(il.amount) / NULLIF(SUM(il.hours_spent), 0), 2) AS effective_hourly_rate
FROM income_logs il
GROUP BY il.user_id, DATE_TRUNC('month', il.date);
```

### 3.5 Habit Consistency View

```sql
-- v_habit_consistency: 30-day habit streak/consistency
CREATE OR REPLACE VIEW v_habit_consistency AS
SELECT
  hl.habit_id,
  h.user_id,
  h.title AS habit_name,
  COUNT(*) FILTER (WHERE hl.completed = TRUE) * 100.0 / 30 AS consistency_pct,
  MAX(hl.date) AS last_completed
FROM habit_logs hl
JOIN habits h ON h.id = hl.habit_id
WHERE hl.date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY hl.habit_id, h.user_id, h.title;
```

---

## 4. View Naming Convention

```
v_{module}_{purpose}
```

Examples: `v_dashboard_summary`, `v_academic_performance`

---

## 5. View Permissions

```sql
-- All views should be accessible to authenticated users only
GRANT SELECT ON v_dashboard_summary TO authenticated;
GRANT SELECT ON v_academic_performance TO authenticated;
GRANT SELECT ON v_weekly_activity TO authenticated;
GRANT SELECT ON v_income_trends TO authenticated;
GRANT SELECT ON v_habit_consistency TO authenticated;
```

Views do not expose data across users — they inherit RLS from the underlying tables (views respect RLS policies automatically in PostgreSQL).

---

## 6. When to Create Views

| Trigger | Action |
|---|---|
| Repeated query pattern across 3+ endpoints | Create a view |
| Dashboard load exceeds 200ms | Create materialized view |
| Cross-module aggregation needed | Create a view |
| Reporting/analytics requirements | Create a view (or materialized) |

---

## 7. Related Documents

| Document | Description |
|---|---|
| [MaterializedViews.md](MaterializedViews.md) | Materialized view refresh strategy |
| [Schema.md](Schema.md) | Underlying table schemas |
| [Indexes.md](Indexes.md) | Index strategy for performance |
