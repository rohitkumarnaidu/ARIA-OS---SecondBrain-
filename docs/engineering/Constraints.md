# Constraint Documentation — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ENG-CON-003 |
| **Version** | 1.0.0 |
| **Status** | Approved |
| **Date** | 2026-07-10 |
| **Classification** | Internal |
| **Owner** | Developer |
| **Related Docs** | [Schema.md](Schema.md), [Policies.md](Policies.md), [ERD.md](ERD.md) |

---

## 1. Executive Summary

The Second Brain OS database enforces ~200 constraints across 27 tables, ensuring data integrity at the database level. Constraints are grouped into four categories: primary keys (UUID), foreign keys (user_id isolation), check constraints (domain values), and unique constraints (deduplication). All constraints follow a strict naming convention.

---

## 2. Constraint Naming Convention

| Type | Pattern | Example |
|---|---|---|
| Primary Key | `{table}_pkey` (auto) | `tasks_pkey` |
| Foreign Key | `fk_{child}_{parent}` | `fk_tasks_users` |
| Unique | `uq_{table}_{columns}` | `uq_habit_logs_habit_date` |
| Check | `ck_{table}_{column}` | `ck_tasks_priority` |

---

## 3. Primary Keys

All 27 tables use UUID primary keys:

```sql
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
```

**Rationale:** UUIDs prevent enumeration attacks, support offline creation, and avoid sequential ID conflicts in distributed environments.

---

## 4. Foreign Key Catalog

### 4.1 User Isolation (All User-Owned Tables)

Every user-owned table references `auth.users`:

```sql
user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL
```

| Child Table | FK Column | Parent | Delete Rule |
|---|---|---|---|
| users_profile | user_id | auth.users(id) | CASCADE |
| tasks | user_id | auth.users(id) | CASCADE |
| courses | user_id | auth.users(id) | CASCADE |
| youtube_saves | user_id | auth.users(id) | CASCADE |
| resources | user_id | auth.users(id) | CASCADE |
| ideas | user_id | auth.users(id) | CASCADE |
| goals | user_id | auth.users(id) | CASCADE |
| roadmaps | user_id | auth.users(id) | CASCADE |
| roadmap_updates | user_id | auth.users(id) | CASCADE |
| opportunities | user_id | auth.users(id) | CASCADE |
| income_sources | user_id | auth.users(id) | CASCADE |
| income_logs | user_id | auth.users(id) | CASCADE |
| projects | user_id | auth.users(id) | CASCADE |
| academic_subjects | user_id | auth.users(id) | CASCADE |
| habits | user_id | auth.users(id) | CASCADE |
| sleep_logs | user_id | auth.users(id) | CASCADE |
| time_logs | user_id | auth.users(id) | CASCADE |
| chat_messages | user_id | auth.users(id) | CASCADE |
| aria_memory | user_id | auth.users(id) | CASCADE |
| daily_briefings | user_id | auth.users(id) | CASCADE |
| weekly_reviews | user_id | auth.users(id) | CASCADE |
| study_sessions | user_id | auth.users(id) | CASCADE |
| daily_logs | user_id | auth.users(id) | CASCADE |

### 4.2 Module-Relationship FKs

| Child Table | FK Column | Parent | Delete Rule | Purpose |
|---|---|---|---|---|
| tasks | goal_id | goals(id) | SET NULL | Goal-linked tasks |
| tasks | project_id | projects(id) | SET NULL | Project tasks |
| courses | related_goal_id | goals(id) | SET NULL | Goal-linked course |
| youtube_saves | related_goal_id | goals(id) | SET NULL | Goal-linked video |
| resources | related_goal_id | goals(id) | SET NULL | Goal-linked resource |
| goals | linked_roadmap_id | roadmaps(id) | SET NULL | Primary roadmap |
| roadmaps | (user_id only) | auth.users | CASCADE | User ownership |
| roadmap_updates | roadmap_id | roadmaps(id) | CASCADE | Per-roadmap updates |
| habits | linked_goal_id | goals(id) | SET NULL | Goal-linked habit |
| income_logs | source_id | income_sources(id) | CASCADE | Per-source income |
| projects | related_income_source_id | income_sources(id) | SET NULL | Funded project |
| time_logs | task_id | tasks(id) | SET NULL | Tracked task |
| academic_subjects | related_goal_id | goals(id) | SET NULL | Goal-linked subject |
| study_sessions | course_id | courses(id) | SET NULL | Course study |
| subtasks | task_id | tasks(id) | CASCADE | Parent task |
| task_dependencies | task_id | tasks(id) | CASCADE | Dependent task |
| task_dependencies | depends_on_id | tasks(id) | CASCADE | Prerequisite task |
| marks | subject_id | academic_subjects(id) | CASCADE | Parent subject |
| habit_logs | habit_id | habits(id) | CASCADE | Parent habit |

---

## 5. Check Constraints Catalog

### 5.1 Status Enums

| Table | Column | Allowed Values |
|---|---|---|
| tasks | priority | low, medium, high, urgent |
| tasks | category | study, project, habit, personal, income, career, health |
| tasks | status | pending, in_progress, completed, cancelled, missed |
| tasks | source | manual, roadmap, aria, opportunity, recurring, course |
| courses | platform | udemy, coursera, nptel, youtube, college, other |
| courses | status | not_started, active, paused, completed, abandoned |
| youtube_saves | status | unseen, scheduled, watched, archived |
| resources | resource_type | article, book, github, tool, paper, thread, other |
| resources | status | unread, reading, read, archived |
| ideas | idea_type | startup, project, content, feature, other |
| ideas | status | raw, researching, validating, building, archived |
| goals | roadmap_type | career_skills, business_launch, exam_prep, study_learning, project, health, financial, custom |
| goals | intensity | low, medium, high |
| goals | status | active, completed, paused, abandoned |
| roadmaps | roadmap_type | career_skills, business_launch, exam_prep, study_learning, project, health, financial, custom |
| roadmaps | status | active, completed, paused, archived |
| roadmaps | intensity | conservative, normal, aggressive |
| roadmaps | update_frequency | daily, weekly, monthly |
| roadmap_updates | update_type | critical, suggested, informational |
| roadmap_updates | status | pending, accepted, rejected, snoozed |
| opportunities | opportunity_type | internship, hackathon, open_source, fellowship, freelance, competition, scholarship, course |
| opportunities | status | new, saved, applied, rejected, accepted |
| income_sources | source_type | freelance, content, teaching, open_source, product, hackathon, internship, saas, other |
| income_sources | status | active, paused, ended |
| projects | phase | planning, design, build, test, launch, maintain |
| projects | status | active, paused, completed, archived |
| habits | frequency | daily, weekdays, weekends, weekly, custom |
| habits | status | active, paused, archived |
| sleep_logs | quality_rating | 1-5 (integer range) |
| sleep_logs | sleep_score | 0-100 (integer range) |
| sleep_logs | source | manual, google_fit, fitbit |
| chat_messages | role | user, assistant, system |
| aria_memory | memory_type | preference, fact, pattern, decision |
| academic_subjects | marks_scored | DECIMAL (implicit) |
| marks | exam_type | assignment, midterm, final, practical, quiz, other |
| time_logs | energy_level | 1-5 (integer range) |

### 5.2 Range Check Constraints

```sql
-- Sleep quality rating (1-5)
CHECK (quality_rating BETWEEN 1 AND 5)

-- Sleep score (0-100)
CHECK (sleep_score BETWEEN 0 AND 100)

-- Memory confidence (0.0-1.0)
CHECK (confidence BETWEEN 0 AND 1)

-- Energy level (1-5)
CHECK (energy_level BETWEEN 1 AND 5)
```

---

## 6. Unique Constraints

| Table | Columns | Purpose |
|---|---|---|
| users_profile | user_id | One profile per auth user |
| task_dependencies | (task_id, depends_on_id) | No duplicate dependency edges |
| habit_logs | (habit_id, date) | One log per habit per day |
| sleep_logs | (user_id, date) | One sleep log per day |
| daily_briefings | (user_id, date) | One briefing per day |
| weekly_reviews | (user_id, week_start) | One review per week |
| daily_logs | (user_id, date) | One journal entry per day |

---

## 7. NOT NULL Constraints

Enforced on all critical columns:

| Pattern | Columns |
|---|---|
| **Always NOT NULL** | `id`, `user_id`, `title` (on named entities), `url` (on resources/opportunities), `created_at` |
| **Context-dependent** | `date` on logs, `amount` on income_logs, `content` on chat_messages/memory |

**Exception:** All JSONB columns, TEXT descriptions, and numeric aggregates allow NULL (to support partial data entry).

---

## 8. DEFAULT Values

| Column | Default | Rationale |
|---|---|---|
| status | 'pending', 'active', 'unread', etc. | Sensible initial state |
| created_at | NOW() | Automatic timestamp |
| updated_at | NOW() | Automatic timestamp |
| progress_percent | 0 | Start at zero |
| missed_count | 0 | No misses initially |
| confidence | 0.8 | Moderate default |
| is_completed / is_archived | FALSE | Negative defaults |

---

## 9. Constraint Enforcement Strategy

| Layer | Enforcement | Bypass |
|---|---|---|
| **Database** | PK, FK, CHECK, UNIQUE, NOT NULL | Service role key |
| **API (Pydantic)** | Type validation, field required/optional | N/A (client-side) |
| **Frontend (Zod)** | Form validation, type safety | N/A (UX only) |

**Rule:** Database constraints are the final authority. Application-level validation prevents bad data from reaching the DB, but constraints catch edge cases.

---

## 10. Related Documents

| Document | Description |
|---|---|
| [Schema.md](Schema.md) | Complete column-level schema |
| [Policies.md](Policies.md) | RLS policy catalog |
| [RLS.md](RLS.md) | RLS deep dive |

> **Duplicate note:** A business-level constraints document exists at [`docs/product/Constraints.md`](../product/Constraints.md) covering project scope, budget, and timeline constraints. This engineering document covers database, API, and technical constraints. Cross-reference for a complete view of all system constraints.
