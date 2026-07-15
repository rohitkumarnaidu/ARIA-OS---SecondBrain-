# Index Strategy — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ENG-IDX-002 |
| **Version** | 1.0.0 |
| **Status** | Approved |
| **Date** | 2026-07-10 |
| **Classification** | Internal |
| **Owner** | Developer |
| **Related Docs** | [Schema.md](Schema.md), [ScalingPlan.md](../operations/ScalingPlan.md) |

---

## 1. Executive Summary

The Second Brain OS uses ~90 indexes across 27 tables to support sub-200ms query performance. The index strategy prioritizes user-scoped queries (`user_id` + filter) and date-range scans (dashboard, reports). Full-text search and GIN indexes on JSONB/array columns handle unstructured queries for resources and opportunities.

---

## 2. Index Naming Convention

```
idx_{table}_{column}         -- Single column
idx_{table}_{col1}_{col2}    -- Composite (order matters)
idx_{table}_{column}_partial -- Partial index with WHERE clause
```

Examples: `idx_tasks_user_status`, `idx_tasks_due_date_partial`

---

## 3. Index Type Catalog

| Type | Use Case | Count |
|---|---|---|
| B-tree (default) | Equality, range, ordering | ~80 |
| Composite B-tree | User-scoped multi-filter queries | ~25 |
| Partial B-tree | Filtered subsets (active, pending) | ~15 |
| GIN | Array columns (tags), full-text search | 3 |
| UNIQUE B-tree | Deduplication constraints | 7 |

---

## 4. Complete Index Catalog

### 4.1 User-Facing Modules

| Table | Index Name | Columns | Type | Purpose |
|---|---|---|---|---|
| tasks | idx_tasks_user_status | user_id, status | Composite | Dashboard task list |
| tasks | idx_tasks_user_due | user_id, due_date | Composite | Upcoming tasks |
| tasks | idx_tasks_user_priority | user_id, priority | Composite | Priority filtering |
| tasks | idx_tasks_due_date | due_date WHERE status NOT IN ('completed','cancelled') | Partial | Overdue task alerts |
| courses | idx_courses_user_status | user_id, status | Composite | Course dashboard |
| courses | idx_courses_deadline | deadline WHERE status='active' | Partial | Deadline alerts |
| youtube_saves | idx_youtube_user_status | user_id, status | Composite | Video library |
| youtube_saves | idx_youtube_expiry | watch_by_date WHERE status='unseen' | Partial | Expiry notification |
| resources | idx_resources_user_type | user_id, resource_type | Composite | Type filtering |
| resources | idx_resources_tags | tags | GIN | Tag search |
| resources | idx_resources_fts | to_tsvector(title \|\| notes) | GIN | Full-text search |
| ideas | idx_ideas_user_status | user_id, status | Composite | Idea pipeline |
| goals | idx_goals_user_status | user_id, status | Composite | Goal dashboard |
| goals | idx_goals_target_date | target_date WHERE status='active' | Partial | Deadline tracking |
| opportunities | idx_opportunities_user_status | user_id, status | Composite | Opportunity list |
| opportunities | idx_opportunities_deadline | deadline WHERE status IN ('new','saved') | Partial | Urgent deadlines |
| opportunities | idx_opportunities_match | match_score WHERE match_score >= 50 | Partial | High-match filter |
| income_sources | idx_income_sources_user | user_id | Single | User scoping |
| income_logs | idx_income_logs_user_date | user_id, date | Composite | Income timeline |
| income_logs | idx_income_logs_source | source_id | Single | Source aggregation |
| projects | idx_projects_user_status | user_id, status | Composite | Project dashboard |
| academic_subjects | idx_subjects_user_semester | user_id, semester | Composite | Semester view |
| academic_subjects | idx_subjects_at_risk | at_risk_flag WHERE at_risk_flag = TRUE | Partial | At-risk monitor |
| habits | idx_habits_user_status | user_id, status | Composite | Habit list |
| sleep_logs | idx_sleep_logs_user_date | user_id, date DESC | Composite | Sleep history |
| sleep_logs | idx_sleep_logs_score | sleep_score WHERE sleep_score < 50 | Partial | Poor sleep alerts |
| habit_logs | idx_habit_logs_habit_date | habit_id, date | Composite | Streak calc |
| time_logs | idx_time_logs_user_start | user_id, started_at DESC | Composite | Time dashboard |
| time_logs | idx_time_logs_task | task_id | Single | Task aggregation |
| time_logs | idx_time_logs_deep | is_deep_work WHERE is_deep_work = TRUE | Partial | Deep work tracking |

### 4.2 AI & System Modules

| Table | Index Name | Columns | Type | Purpose |
|---|---|---|---|---|
| chat_messages | idx_chat_messages_user_created | user_id, created_at DESC | Composite | Chat history |
| aria_memory | idx_aria_memory_user_type | user_id, memory_type | Composite | Memory retrieval |
| aria_memory | idx_aria_memory_last_ref | last_referenced_at | Single | Decay/GC queries |
| roadmaps | idx_roadmaps_user | user_id | Single | User scoping |
| roadmap_updates | idx_roadmap_updates_roadmap | roadmap_id | Single | Per-roadmap updates |
| daily_briefings | idx_briefings_user_date | user_id, date DESC | Composite | Latest briefing |
| weekly_reviews | idx_weekly_reviews_user | user_id, week_start DESC | Composite | Review history |
| study_sessions | idx_study_sessions_user | user_id, started_at DESC | Composite | Study history |
| daily_logs | idx_daily_logs_user_date | user_id, date DESC | Composite | Journal history |

### 4.3 Child Tables (FK-based access)

| Table | Index Name | Columns | Type | Purpose |
|---|---|---|---|---|
| subtasks | idx_subtasks_task | task_id | Single | Subtask list |
| task_dependencies | idx_task_deps_task | task_id | Single | Outgoing deps |
| task_dependencies | idx_task_deps_depends | depends_on_id | Single | Incoming deps |
| marks | idx_marks_subject | subject_id | Single | Per-subject marks |

---

## 5. Composite Index Strategy

Composite indexes follow the **equality-first, range-last** principle:

```sql
-- Good: equality on user_id, then range on date
CREATE INDEX idx_tasks_user_due ON tasks(user_id, due_date);

-- Avoid: range first, then equality (doesn't filter effectively)
-- CREATE INDEX ON tasks(due_date, user_id);
```

**Pattern for all user-owned tables:**
```
Column 1: user_id (equality filter — always present)
Column 2: status/type (equality or IN filter)
Column 3: date/priority (range or ORDER BY)
```

---

## 6. Partial Index Use Cases

Partial indexes index only a subset of rows, saving storage and write overhead:

```sql
-- Only index active goals with deadlines (typically <20% of rows)
CREATE INDEX idx_goals_target_date ON goals(target_date)
  WHERE status = 'active';

-- Only index high-match opportunities
CREATE INDEX idx_opportunities_match ON opportunities(match_score)
  WHERE match_score >= 50;

-- Only index at-risk subjects (typically <10% of rows)
CREATE INDEX idx_subjects_at_risk ON academic_subjects(at_risk_flag)
  WHERE at_risk_flag = TRUE;
```

---

## 7. Full-Text Search Indexes

Resources and notes support full-text search via GIN indexes:

```sql
-- English text search across title + notes
CREATE INDEX idx_resources_fts ON resources
  USING GIN(to_tsvector('english', title || ' ' || COALESCE(notes, '')));

-- Query pattern:
SELECT * FROM resources
WHERE to_tsvector('english', title || ' ' || COALESCE(notes, ''))
  @@ plainto_tsquery('english', 'search terms');
```

---

## 8. Index Maintenance

| Operation | Frequency | Method |
|---|---|---|
| REINDEX | Monthly | `REINDEX INDEX CONCURRENTLY idx_name` |
| Analyze | Weekly | `ANALYZE table_name` (auto-vacuum handles this) |
| Unused index review | Quarterly | `pg_stat_user_indexes` scan |
| Bloat check | Monthly | `pgstattuple` extension |

**Detecting unused indexes:**
```sql
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0  -- Never used
ORDER BY tablename;
```

---

## 9. Performance Considerations

| Index Property | Recommendation | Rationale |
|---|---|---|
| **Cardinality** | High-first in composite | user_id (many values) before status (few values) |
| **Write overhead** | < 5% write perf loss | Acceptable for < 50ms write latency |
| **Selectivity** | Partial when < 20% rows matched | Saves 80% index storage |
| **Covering indexes** | Not used currently | INCLUDE clause for index-only scans |
| **Concurrent creation** | Always use CONCURRENTLY | Avoids table locks in production |

---

## 10. Monitoring Query

```sql
-- Index usage statistics
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan AS scans,
  idx_tup_read AS tuples_read,
  idx_tup_fetch AS tuples_fetched,
  pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

---

## 11. Future Index Candidates

| Candidate | Table | Columns | Priority | Rationale |
|---|---|---|---|---|
| user_created | chat_messages | user_id, created_at | ✅ Done | Already exists |
| memory_content_fts | aria_memory | to_tsvector(content) | Medium | Enable memory search |
| briefings_was_read | daily_briefings | was_read WHERE was_read=FALSE | Low | Unread briefing count |
| habits_last_completed | habits | last_completed_at | Low | Stale habit detection |

---

## 12. Related Documents

| Document | Description |
|---|---|
| [Schema.md](Schema.md) | Complete column-level schema |
| [Constraints.md](Constraints.md) | Constraint catalog |
| [15_Database.md](15_Database.md) | Legacy database overview (deprecated) |
