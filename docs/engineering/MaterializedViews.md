# Materialized Views — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ENG-MVW-005 |
| **Version** | 1.0.0 |
| **Status** | Approved |
| **Date** | 2026-07-10 |
| **Classification** | Internal |
| **Owner** | Developer |
| **Related Docs** | [Views.md](Views.md), [Schema.md](Schema.md), [CronJobs.md](CronJobs.md) |

---

## 1. Executive Summary

Materialized views provide pre-computed, indexed snapshots of expensive aggregations for dashboard displays and weekly reports. They trade storage for query speed, refreshing on a scheduled cadence (cron jobs). The system targets < 50ms dashboard load times using materialized views for heavy aggregations.

---

## 2. Materialized View Catalog

### 2.1 Dashboard Aggregation

```sql
-- mv_dashboard_metrics: Pre-computed daily dashboard numbers
CREATE MATERIALIZED VIEW mv_dashboard_metrics AS
SELECT
  t.user_id,
  CURRENT_DATE AS snapshot_date,
  COUNT(*) FILTER (WHERE t.status = 'pending' AND t.due_date >= CURRENT_DATE) AS today_tasks,
  COUNT(*) FILTER (WHERE t.due_date < CURRENT_DATE AND t.status = 'pending') AS overdue_tasks,
  COUNT(*) FILTER (WHERE t.due_date = CURRENT_DATE AND t.status = 'pending') AS due_today,
  COUNT(*) FILTER (WHERE t.completed_at >= CURRENT_DATE) AS completed_today,
  COUNT(*) FILTER (WHERE t.status = 'in_progress') AS in_progress_tasks
FROM tasks t
GROUP BY t.user_id;

CREATE UNIQUE INDEX idx_mv_dashboard_user ON mv_dashboard_metrics(user_id);
```

### 2.2 Weekly Performance Report

```sql
-- mv_weekly_performance: Sunday morning refresh for weekly reviews
CREATE MATERIALIZED VIEW mv_weekly_performance AS
SELECT
  t.user_id,
  DATE_TRUNC('week', t.created_at)::DATE AS week_start,
  COUNT(*) FILTER (WHERE t.status = 'completed') AS tasks_completed,
  COUNT(*) FILTER (WHERE t.status = 'missed') AS tasks_missed,
  ROUND(AVG(t.actual_minutes) FILTER (WHERE t.status = 'completed'), 0) AS avg_completion_minutes,
  COUNT(*) FILTER (WHERE t.source = 'recurring') AS recurring_tasks_done,
  COUNT(DISTINCT t.goal_id) AS goals_contributed
FROM tasks t
GROUP BY t.user_id, DATE_TRUNC('week', t.created_at);

CREATE INDEX idx_mv_weekly_user_week ON mv_weekly_performance(user_id, week_start DESC);
```

### 2.3 Course Progress Summary

```sql
-- mv_course_progress: Snapshot of all course progress
CREATE MATERIALIZED VIEW mv_course_progress AS
SELECT
  c.user_id,
  COUNT(*) AS total_courses,
  COUNT(*) FILTER (WHERE c.status = 'active') AS active_courses,
  COUNT(*) FILTER (WHERE c.status = 'active' AND c.deadline < CURRENT_DATE + INTERVAL '7 days') AS deadline_this_week,
  ROUND(AVG(c.progress_percent) FILTER (WHERE c.status = 'active'), 0) AS avg_active_progress,
  SUM(c.daily_minutes_needed) FILTER (WHERE c.status = 'active') AS total_daily_minutes_needed
FROM courses c
GROUP BY c.user_id;

CREATE UNIQUE INDEX idx_mv_course_user ON mv_course_progress(user_id);
```

### 2.4 Sleep Trend

```sql
-- mv_sleep_trend: 7-day rolling sleep metrics
CREATE MATERIALIZED VIEW mv_sleep_trend AS
SELECT
  user_id,
  ROUND(AVG(sleep_score), 0) AS avg_7day_score,
  ROUND(AVG(duration_minutes), 0) AS avg_7day_duration,
  ROUND(AVG(sleep_debt_minutes), 0) AS avg_7day_debt,
  COUNT(*) FILTER (WHERE sleep_score < 50) AS poor_sleep_days
FROM sleep_logs
WHERE date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY user_id;

CREATE UNIQUE INDEX idx_mv_sleep_user ON mv_sleep_trend(user_id);
```

---

## 3. Refresh Strategy

| View | Refresh Frequency | Trigger | Max Refresh Time |
|---|---|---|---|
| mv_dashboard_metrics | Every 5 minutes | Cron (short interval) | < 2s |
| mv_weekly_performance | Weekly (Sunday 2 AM) | Cron (weekly) | < 5s |
| mv_course_progress | Every 15 minutes | Cron | < 2s |
| mv_sleep_trend | Every 30 minutes | Cron | < 1s |

---

## 4. Refresh Implementation

```sql
-- Concurrent refresh (no locking)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_dashboard_metrics;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_course_progress;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_sleep_trend;

-- Non-concurrent is faster but locks the table
REFRESH MATERIALIZED VIEW mv_weekly_performance;
```

**Rule:** Always use `CONCURRENTLY` for views refreshed more frequently than daily.

---

## 5. Storage Impact

| View | Est. Rows | Est. Size | Refresh Overhead |
|---|---|---|---|
| mv_dashboard_metrics | ~100 (one per user) | ~10 KB | Minimal |
| mv_weekly_performance | ~5,200 (1yr × users) | ~500 KB | Low |
| mv_course_progress | ~100 | ~10 KB | Minimal |
| mv_sleep_trend | ~100 | ~10 KB | Minimal |

**Total storage:** < 1 MB (negligible for a 500MB Supabase free tier).

---

## 6. Query Pattern

```python
# Application layer uses materialized views for dashboard
async def get_dashboard_metrics(user_id: str):
    data = supabase.table("mv_dashboard_metrics")\
        .select("*")\
        .eq("user_id", user_id)\
        .execute()
    return data.data[0] if data.data else default_metrics()
```

---

## 7. When to Create Materialized Views

| Condition | Action |
|---|---|
| Query takes > 200ms and runs > 10x/day | Create materialized view |
| Dashboard needs sub-50ms load | Create materialized view |
| Aggregation spans 3+ tables | Create materialized view |
| Weekly report generation | Create materialized view |

---

## 8. Refresh Job Monitoring

```sql
-- Check when each view was last refreshed
SELECT
  oid::REGCLASS AS matview_name,
  pg_stat_get_last_analyze_time(oid) AS last_refresh
FROM pg_class
WHERE oid IN (
  'mv_dashboard_metrics'::REGCLASS,
  'mv_weekly_performance'::REGCLASS,
  'mv_course_progress'::REGCLASS,
  'mv_sleep_trend'::REGCLASS
);
```

---

## 9. Related Documents

| Document | Description |
|---|---|
| [Views.md](Views.md) | Regular (non-materialized) views |
| [Schema.md](Schema.md) | Underlying table schemas |
| [CronJobs.md](CronJobs.md) | Cron job configuration |
