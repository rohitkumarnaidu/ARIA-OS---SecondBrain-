# Database Entity Relationship Diagram — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ARCH-ERD-001 |
| **Version** | 1.0.0 |
| **Status** | Active |
| **Date** | 2026-07-10 |
| **Classification** | Internal |
| **Owner** | Developer |
| **Supersedes** | `docs/engineering/ERD.md` (partial update) |
| **Related Docs** | [Schema.md](/docs/engineering/Schema.md), [Constraints.md](/docs/engineering/Constraints.md), [Indexes.md](/docs/engineering/Indexes.md), [Policies.md](/docs/engineering/Policies.md) |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Conventions](#2-conventions)
3. [Complete ERD — All 18 Core Tables](#3-complete-erd--all-18-core-tables)
4. [Table Definitions & Relationships](#4-table-definitions--relationships)
5. [RLS Policy Summary](#5-rls-policy-summary)
6. [Index Strategy Summary](#6-index-strategy-summary)
7. [Query Patterns](#7-query-patterns)
8. [Foreign Key Reference Map](#8-foreign-key-reference-map)

---

## 1. Executive Summary

The Second Brain OS database consists of **18+ core user-owned tables** hosted on Supabase PostgreSQL 15. Every user-owned table enforces tenant isolation via `user_id` column with Row-Level Security (RLS).

**Key numbers:** 18+ user tables, ~60 foreign keys, UUID v4 primary keys, all tables RLS-enabled.

---

## 2. Conventions

| Convention | Rule |
|---|---|
| **Primary Keys** | UUID v4, `DEFAULT gen_random_uuid()` |
| **Foreign Keys** | `user_id` references `auth.users(id) ON DELETE CASCADE` on every user-owned table |
| **Timestamps** | `created_at TIMESTAMPTZ DEFAULT NOW()`, `updated_at TIMESTAMPTZ DEFAULT NOW()` |
| **Soft Delete** | Not used; records are hard-deleted or marked with status field |
| **RLS** | Enabled on all user-owned tables (`FOR ALL USING (auth.uid() = user_id)`) |

---

## 3. Complete ERD — All 18 Core Tables

```mermaid
erDiagram
    %% ============================================================
    %% CORE — auth.users is the root identity
    %% ============================================================
    auth_users ||--o{ tasks : "user_id"
    auth_users ||--o{ courses : "user_id"
    auth_users ||--o{ goals : "user_id"
    auth_users ||--o{ habits : "user_id"
    auth_users ||--o{ habit_logs : "user_id"
    auth_users ||--o{ sleep_logs : "user_id"
    auth_users ||--o{ income_entries : "user_id"
    auth_users ||--o{ projects : "user_id"
    auth_users ||--o{ ideas : "user_id"
    auth_users ||--o{ resources : "user_id"
    auth_users ||--o{ opportunities : "user_id"
    auth_users ||--o{ time_entries : "user_id"
    auth_users ||--o{ chat_messages : "user_id"
    auth_users ||--o{ daily_briefings : "user_id"
    auth_users ||--o{ weekly_reviews : "user_id"
    auth_users ||--o{ memory : "user_id"
    auth_users ||--o{ learning_progress : "user_id"
    auth_users ||--o{ users : "user_id"}

    %% ============================================================
    %% MODULE RELATIONSHIPS
    %% ============================================================
    tasks ||--o{ time_entries : "task_id"
    tasks }o--|| goals : "goal_id"
    tasks }o--|| projects : "project_id"

    goals ||--o{ courses : "related_goal_id"
    goals ||--o{ habits : "linked_goal_id"

    habits ||--o{ habit_logs : "habit_id"

    courses ||--o{ learning_progress : "course_id"

    %% ============================================================
    %% TABLE DEFINITIONS — Columns & Types (from Pydantic schemas)
    %% ============================================================
    auth_users {
        uuid id PK
        text email
        text encrypted_password
    }

    users {
        uuid id PK
        uuid user_id FK "unique"
        text email
        text name
        text avatar_url
        text college
        int year
        jsonb skills
        text bio
        jsonb daily_routine
        jsonb opportunity_preferences
        timestamptz created_at
        timestamptz updated_at
    }

    tasks {
        uuid id PK
        uuid user_id FK "not null"
        text title "not null"
        text description
        text priority "low|medium|high|urgent"
        text category "study|project|habit|personal|income"
        text status "pending|in_progress|completed|cancelled"
        int estimated_minutes
        timestamptz due_date
        uuid goal_id FK
        uuid project_id FK
        uuid dependency_id FK
        bool is_recurring
        text recurring_frequency
        int missed_count "default 0"
        timestamptz completed_at
        timestamptz created_at
        timestamptz updated_at
    }

    courses {
        uuid id PK
        uuid user_id FK "not null"
        text title "not null"
        text platform "not null"
        text url
        int total_videos
        int completed_videos "default 0"
        text deadline
        text why_enrolled
        text status "not_started|active|paused|completed|abandoned"
        uuid related_goal_id FK
        timestamptz created_at
    }

    goals {
        uuid id PK
        uuid user_id FK "not null"
        text title "not null"
        text description
        text roadmap_type "career_skills|business_launch|exam_prep|study_learning|project|health|financial|custom"
        text target_date
        float hours_per_day "default 2.0"
        float days_per_week "default 5.0"
        text intensity "low|medium|high"
        text status "active|completed|paused|abandoned"
        int progress "default 0"
        text category
        timestamptz created_at
    }

    habits {
        uuid id PK
        uuid user_id FK "not null"
        text name "not null"
        text frequency "daily|weekdays|weekends|weekly|custom"
        jsonb custom_days
        int time_target_minutes
        bool is_active "default true"
        int current_streak "default 0"
        int best_streak "default 0"
        float consistency_percentage "default 0"
        uuid linked_goal_id FK
        timestamptz created_at
    }

    habit_logs {
        uuid id PK
        uuid user_id FK "not null"
        uuid habit_id FK "not null"
        date date "not null"
        bool completed "default false"
        int minutes_spent
        timestamptz created_at
    }

    sleep_logs {
        uuid id PK
        uuid user_id FK "not null"
        text bedtime "not null"
        text wake_time "not null"
        int quality_rating "1-5"
        float duration_hours
        int sleep_score "0-100"
        float sleep_debt
        timestamptz created_at
    }

    income_entries {
        uuid id PK
        uuid user_id FK "not null"
        text source_type "not null"
        float amount "not null"
        text platform
        text description
        text date
        float hours_spent
        float effective_hourly_rate
        timestamptz created_at
    }

    projects {
        uuid id PK
        uuid user_id FK "not null"
        text title "not null"
        text description
        text phase "planning|design|build|test|launch|maintain"
        text github_url
        text live_url
        text next_action
        text blocker
        timestamptz created_at
    }

    ideas {
        uuid id PK
        uuid user_id FK "not null"
        text title "not null"
        text description
        text status "raw|researching|validating|building|archived"
        text market_research
        text competitors
        timestamptz created_at
    }

    resources {
        uuid id PK
        uuid user_id FK "not null"
        text title "not null"
        text url "not null"
        text resource_type "article|book|github|tool|paper|thread|other"
        jsonb tags "default []"
        text notes
        bool is_archived "default false"
        timestamptz created_at
    }

    opportunities {
        uuid id PK
        uuid user_id FK "not null"
        text title "not null"
        text url "not null"
        text opportunity_type "internship|hackathon|open_source|fellowship|freelance|competition|scholarship|course"
        text company
        text description
        jsonb skills_required
        text deadline
        text status "new|saved|applied|rejected|accepted"
        float match_score
        timestamptz created_at
    }

    time_entries {
        uuid id PK
        uuid user_id FK "not null"
        uuid task_id FK
        timestamptz start_time "not null"
        timestamptz end_time
        int duration_minutes
        text description
        text category "work|study|break|personal"
        timestamptz created_at
    }

    chat_messages {
        uuid id PK
        uuid user_id FK "not null"
        text conversation_id
        text role "user|assistant|system"
        text content "not null"
        jsonb metadata
        timestamptz created_at
    }

    daily_briefings {
        uuid id PK
        uuid user_id FK "not null"
        text date "not null"
        text title
        text summary
        text opening
        text top_priority
        int tasks_count
        int habits_streak
        float sleep_score
        text ai_insight
        text productivity_tip
        text focus_area
        text generated_by
        bool read "default false"
        jsonb raw_json
        timestamptz created_at
    }

    weekly_reviews {
        uuid id PK
        uuid user_id FK "not null"
        text week_start "not null"
        text week_end
        text summary
        int tasks_completed
        int tasks_added
        float habits_consistency
        float focus_hours
        jsonb highlights
        jsonb challenges
        jsonb next_week_focus
        text ai_insights
        text mood_trend
        text generated_by
        timestamptz created_at
    }

    memory {
        uuid id PK
        uuid user_id FK "not null"
        text type "preference|fact|pattern|decision"
        text key "not null"
        jsonb value "not null"
        text importance "low|medium|high"
        jsonb tags
        text expires_at
        timestamptz created_at
        timestamptz updated_at
    }

    learning_progress {
        uuid id PK
        uuid user_id FK "not null"
        uuid course_id FK
        text metric
        float value
        date date
        timestamptz created_at
    }

    notifications {
        uuid id PK
        uuid user_id FK "not null"
        text title "not null"
        text message
        text category
        text priority
        bool read "default false"
        text action_url
        text icon
        timestamptz created_at
    }

    academic_subjects {
        uuid id PK
        uuid user_id FK "not null"
        text name "not null"
        text code
        int credits
        text semester
        text exam_date
        float target_marks
        timestamptz created_at
    }

    marks {
        uuid id PK
        uuid user_id FK "not null"
        uuid subject_id FK "not null"
        text exam_type
        float marks_obtained "not null"
        float max_marks "not null"
        text date
        timestamptz created_at
    }

    roadmap_milestones {
        uuid id PK
        uuid user_id FK "not null"
        text skill "not null"
        text category "not null"
        text target_date
        float progress "default 0"
        text status "not_started|in_progress|completed"
        bool is_recommended "default false"
        timestamptz created_at
        timestamptz updated_at
    }

    audit_logs {
        uuid id PK
        uuid user_id FK
        text action
        text resource
        text resource_id
        jsonb details
        text ip_address
        text user_agent
        timestamptz created_at
    }

    feature_flags {
        uuid id PK
        text key "not null unique"
        bool enabled "default false"
        int rollout_percentage "default 0"
        jsonb user_segments
        jsonb metadata
        timestamptz created_at
        timestamptz updated_at
    }
```

---

## 4. Table Definitions & Relationships

### 4.1 Core User Tables

| Table | Source Schema | Description | Key Relationships |
|---|---|---|---|
| `users` | `user.py` | User profiles with preferences, college info, skills | FK to `auth.users` |
| `tasks` | `task.py` | Task CRUD with priority, status, dependencies | FK to `goals`, `projects` |
| `courses` | `course.py` | Course tracking with progress, deadlines | FK to `goals` |
| `goals` | `goal.py` | Goal management with roadmap, milestones | FK from `tasks`, `courses`, `habits` |
| `habits` | `habit.py` | Habit definitions with frequency, streaks | FK to `goals`, FK from `habit_logs` |
| `habit_logs` | `habit.py` | Daily habit completion logs | FK to `habits` |
| `sleep_logs` | `sleep.py` | Sleep tracking with score, debt | FK to `auth.users` |
| `income_entries` | `income.py` | Income logs with hourly rate | FK to `auth.users` |
| `projects` | `project.py` | Project phases, blockers, URLs | FK from `tasks` |
| `ideas` | `idea.py` | Idea pipeline (raw → researching → building) | FK to `auth.users` |
| `resources` | `resource.py` | Resource library with tags | FK to `auth.users` |
| `opportunities` | `opportunity.py` | Opportunity radar with match scores | FK to `auth.users` |
| `time_entries` | `time_entry.py` | Time tracking with Pomodoro, deep work | FK to `tasks` |
| `chat_messages` | `chat.py` | ARIA chat history | FK to `auth.users` |
| `daily_briefings` | `briefing.py` | Generated morning briefings | FK to `auth.users` |
| `weekly_reviews` | `review.py` | Generated weekly reviews | FK to `auth.users` |
| `memory` | `memory.py` | AI persistent memory (preferences, patterns) | FK to `auth.users` |
| `learning_progress` | (derived) | Learning metrics snapshots per course | FK to `courses` |
| `notifications` | `notification.py` | Proactive nudges and alerts | FK to `auth.users` |
| `academic_subjects` | `academic.py` | Subject and marks tracking | FK to `auth.users`, FK from `marks` |
| `marks` | `academic.py` | Exam marks for academic subjects | FK to `academic_subjects` |
| `roadmap_milestones` | `roadmap.py` | Skill development milestones | FK to `auth.users` |
| `audit_logs` | `audit.py` | Audit trail for all mutations | FK to `auth.users` |
| `feature_flags` | `feature_flag.py` | Feature flag configuration | No user FK (global) |
| `api_keys` | `api_key.py` | API key authentication | FK to `auth.users` |

---

## 5. RLS Policy Summary

Every user-owned table has the standard RLS policy. The following table summarizes policy assignments:

| Table | RLS Enabled | Policy Name | Policy Definition |
|---|---|---|---|
| `tasks` | ✅ | `user_isolation_tasks` | `FOR ALL USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid())` |
| `courses` | ✅ | `user_isolation_courses` | Same pattern |
| `goals` | ✅ | `user_isolation_goals` | Same pattern |
| `habits` | ✅ | `user_isolation_habits` | Same pattern |
| `habit_logs` | ✅ | `user_isolation_habit_logs` | Same pattern |
| `sleep_logs` | ✅ | `user_isolation_sleep_logs` | Same pattern |
| `income_entries` | ✅ | `user_isolation_income` | Same pattern |
| `projects` | ✅ | `user_isolation_projects` | Same pattern |
| `ideas` | ✅ | `user_isolation_ideas` | Same pattern |
| `resources` | ✅ | `user_isolation_resources` | Same pattern |
| `opportunities` | ✅ | `user_isolation_opportunities` | Same pattern |
| `time_entries` | ✅ | `user_isolation_time_entries` | Same pattern |
| `chat_messages` | ✅ | `user_isolation_chat` | Same pattern |
| `daily_briefings` | ✅ | `user_isolation_briefings` | Same pattern |
| `weekly_reviews` | ✅ | `user_isolation_reviews` | Same pattern |
| `memory` | ✅ | `user_isolation_memory` | Same pattern |
| `users` | ✅ | `user_isolation_users` | Same pattern |
| `notifications` | ✅ | `user_isolation_notifications` | Same pattern |
| `academic_subjects` | ✅ | `user_isolation_academic` | Same pattern |
| `marks` | ✅ | `user_isolation_marks` | Same pattern |
| `roadmap_milestones` | ✅ | `user_isolation_roadmap` | Same pattern |
| `audit_logs` | ✅ | `user_isolation_audit` | Same pattern |
| `feature_flags` | ❌ | N/A | Global table, no user isolation |
| `api_keys` | ✅ | `user_isolation_api_keys` | Same pattern |

**Standard RLS template:**
```sql
CREATE POLICY user_isolation ON table_name
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

ALTER TABLE table_name ENABLE ROW LEVEL SECURITY;
```

---

## 6. Index Strategy Summary

| Table | Indexed Columns | Index Type | Purpose |
|---|---|---|---|
| All user-owned tables | `user_id` | B-tree | Primary tenant isolation filter |
| All tables | `id` (PK) | B-tree (unique) | Primary key lookups |
| `tasks` | `status` | B-tree | Filter by status (pending/completed) |
| `tasks` | `priority` | B-tree | Sort/filter by priority |
| `tasks` | `due_date` | B-tree | Sort by deadline, find overdue |
| `tasks` | `goal_id` | B-tree | FK lookup for goal-scoped queries |
| `tasks` | `project_id` | B-tree | FK lookup for project-scoped queries |
| `habits` | `linked_goal_id` | B-tree | FK lookup |
| `habit_logs` | `habit_id` | B-tree | FK lookup |
| `habit_logs` | `date` | B-tree | Daily aggregation queries |
| `sleep_logs` | `date` | B-tree | Daily trend queries |
| `time_entries` | `start_time` | B-tree | Time-range queries |
| `time_entries` | `task_id` | B-tree | FK lookup |
| `daily_briefings` | `date` | B-tree | Date-scoped queries |
| `weekly_reviews` | `week_start` | B-tree | Week-scoped queries |
| `opportunities` | `match_score` | B-tree | Sort by relevance |
| `chat_messages` | `created_at` | B-tree | Chronological ordering |

**Recommended additional indexes (not yet implemented):**
```sql
-- Full-text search on common lookup fields
CREATE INDEX idx_tasks_title_trgm ON tasks USING GIN (title gin_trgm_ops);
CREATE INDEX idx_resources_tags ON resources USING GIN (tags);
CREATE INDEX idx_ideas_status ON ideas (status);
CREATE INDEX idx_opportunities_type ON opportunities (opportunity_type);
CREATE INDEX idx_courses_status ON courses (status);
```

---

## 7. Query Patterns

### 7.1 Common CRUD Patterns (Python/Backend)

| Operation | Pattern | Example |
|---|---|---|
| **List all** | `.select("*").eq("user_id", user_id).execute()` | `GET /api/v1/tasks/` |
| **List filtered** | `.select("*").eq("user_id", user_id).eq("status", "pending").execute()` | `GET /api/v1/tasks/?status=pending` |
| **Single by ID** | `.select("*").eq("id", item_id).eq("user_id", user_id).execute()` | `GET /api/v1/tasks/{id}` |
| **Create** | `.insert({**data, "user_id": user_id}).execute()` | `POST /api/v1/tasks/` |
| **Update** | `.update(update_data).eq("id", item_id).eq("user_id", user_id).execute()` | `PUT /api/v1/tasks/{id}` |
| **Delete** | `.delete().eq("id", item_id).eq("user_id", user_id).execute()` | `DELETE /api/v1/tasks/{id}` |
| **Ordered** | `.select("*").eq("user_id", user_id).order("created_at", desc=True).execute()` | Recent items first |
| **Paginated** | `.select("*").eq("user_id", user_id).range(offset, offset + limit - 1).execute()` | `?limit=20&offset=0` |
| **Count** | `.select("*", count="exact").eq("user_id", user_id).execute()` | Dashboard stats |

### 7.2 Common Query Patterns (TypeScript/Frontend)

| Operation | Pattern | Example |
|---|---|---|
| **List user items** | `supabase.from('tasks').select('id, title, status').eq('user_id', user.id)` | Task list page |
| **Realtime subscription** | `supabase.channel('tasks').on('postgres_changes', { event: '*', schema: 'public', table: 'tasks', filter: 'user_id=eq.' + user.id }, cb).subscribe()` | Live task updates |
| **Auth session** | `supabase.auth.getSession()` | Login check |
| **Sign in** | `supabase.auth.signInWithOAuth({ provider: 'google' })` | Auth flow |

### 7.3 Cross-Table Aggregation Pattern (Dashboard)

```python
# Dashboard — parallel queries for summary view
tasks = supabase.from_("tasks").select("*", count="exact").eq("user_id", user_id).execute()
goals = supabase.from_("goals").select("*", count="exact").eq("user_id", user_id).eq("status", "active").execute()
habits = supabase.from_("habits").select("*", count="exact").eq("user_id", user_id).execute()
sleep = supabase.from_("sleep_logs").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
```

---

## 8. Foreign Key Reference Map

### 8.1 Direct `user_id` References (every user-owned table)

All 18+ user tables have `user_id UUID FK -> auth.users(id) ON DELETE CASCADE NOT NULL`.

### 8.2 Cross-Module Foreign Keys

| Source Table | FK Column | Target Table | Delete Rule | Purpose |
|---|---|---|---|---|
| `tasks` | `goal_id` | `goals(id)` | SET NULL | Link task to goal |
| `tasks` | `project_id` | `projects(id)` | SET NULL | Link task to project |
| `tasks` | `dependency_id` | `tasks(id)` | SET NULL | Task dependency |
| `courses` | `related_goal_id` | `goals(id)` | SET NULL | Link course to goal |
| `habits` | `linked_goal_id` | `goals(id)` | SET NULL | Link habit to goal |
| `habit_logs` | `habit_id` | `habits(id)` | CASCADE | Log belongs to habit |
| `time_entries` | `task_id` | `tasks(id)` | SET NULL | Time entry for task |
| `marks` | `subject_id` | `academic_subjects(id)` | CASCADE | Mark belongs to subject |
| `learning_progress` | `course_id` | `courses(id)` | SET NULL | Progress for course |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-07-10 | Developer | Initial ERD with 18 core tables, RLS summary, index strategy, query patterns |
