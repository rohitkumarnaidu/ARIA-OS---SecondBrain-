# Complete Database Schema Reference — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ENG-SCH-001 |
| **Version** | 1.0.0 |
| **Status** | Approved |
| **Date** | 2026-07-10 |
| **Classification** | Internal |
| **Owner** | Developer |
| **Related Docs** | [ERD.md](ERD.md), [Constraints.md](Constraints.md), [Indexes.md](Indexes.md) |

---

## 1. Executive Summary

The Second Brain OS database consists of 27 tables across 15 functional modules, hosted on Supabase PostgreSQL 15. Every user-owned table enforces tenant isolation via `user_id` column with Row Level Security. This document provides the complete column-level schema reference for all tables.

**Key numbers:** 27 tables, 18+ user-owned entities, ~60 FKs, ~90 indexes, ~200 columns.

---

## 2. Conventions

| Convention | Rule |
|---|---|
| **Primary Keys** | UUID v4, default `gen_random_uuid()` |
| **Foreign Keys** | `user_id` references `auth.users(id) ON DELETE CASCADE` on every user-owned table |
| **Timestamps** | `created_at TIMESTAMPTZ DEFAULT NOW()`, `updated_at TIMESTAMPTZ DEFAULT NOW()` |
| **Soft Delete** | Not used; records are hard-deleted or marked with status |
| **RLS** | Enabled on all user-owned tables (`FOR ALL USING (auth.uid() = user_id)`) |

---

## 3. Module: User Profile

### users_profile

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | Unique identifier |
| user_id | UUID | UNIQUE, FK -> auth.users(id) ON DELETE CASCADE | Supabase auth user |
| name | TEXT | | Display name |
| email | TEXT | | Email address |
| college | TEXT | | Institution name |
| year | INTEGER | | Academic year (1-4) |
| branch | TEXT | | Engineering branch |
| skills | JSONB | DEFAULT '[]' | Array of {name, level} objects |
| opportunity_preferences | JSONB | DEFAULT '{}' | {types:[], min_match_score:60, ...} |
| daily_routine | JSONB | DEFAULT '{}' | {study_start_time, hours_available, study_days[]} |
| github_username | TEXT | | GitHub handle |
| linkedin_url | TEXT | | LinkedIn profile URL |
| onboarding_completed | BOOLEAN | DEFAULT FALSE | Whether onboarding flow is done |
| bedtime | TIME | | Preferred bedtime |
| wake_time | TIME | | Preferred wake time |
| push_subscription | JSONB | | Web push notification subscription |
| google_calendar_token | JSONB | | OAuth token for Google Calendar |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Row creation timestamp |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Row update timestamp |

---

## 4. Module: Tasks

### tasks

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | Unique identifier |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | Owner |
| title | TEXT | NOT NULL | Task title |
| description | TEXT | | Detailed description |
| priority | TEXT | DEFAULT 'medium' CHECK (low, medium, high, urgent) | Priority level |
| category | TEXT | DEFAULT 'personal' CHECK (study, project, habit, personal, income, career, health) | Task category |
| status | TEXT | DEFAULT 'pending' CHECK (pending, in_progress, completed, cancelled, missed) | Current status |
| estimated_minutes | INTEGER | | Estimated effort |
| actual_minutes | INTEGER | | Actual effort logged |
| due_date | TIMESTAMPTZ | | Due date/time |
| scheduled_start | TIMESTAMPTZ | | Planned start time |
| source | TEXT | DEFAULT 'manual' CHECK (manual, roadmap, aria, opportunity, recurring, course) | Creation source |
| goal_id | UUID | FK -> goals(id) ON DELETE SET NULL | Linked goal |
| project_id | UUID | FK -> projects(id) ON DELETE SET NULL | Linked project |
| completed_at | TIMESTAMPTZ | | When completed |
| rescheduled_from | TIMESTAMPTZ | | Original due date before reschedule |
| missed_count | INTEGER | DEFAULT 0 | Times missed |
| recurrence | TEXT | | Cron expression for recurring tasks |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | |

### subtasks

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| task_id | UUID | FK -> tasks(id) ON DELETE CASCADE NOT NULL | Parent task |
| title | TEXT | NOT NULL | Subtask title |
| is_completed | BOOLEAN | DEFAULT FALSE | Completion status |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

### task_dependencies

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| task_id | UUID | FK -> tasks(id) ON DELETE CASCADE NOT NULL | Dependent task |
| depends_on_id | UUID | FK -> tasks(id) ON DELETE CASCADE NOT NULL | Prerequisite task |
| UNIQUE(task_id, depends_on_id) | | | Prevents duplicate dependencies |

---

## 5. Module: Courses

### courses

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | |
| title | TEXT | NOT NULL | Course name |
| platform | TEXT | NOT NULL CHECK (udemy, coursera, nptel, youtube, college, other) | Learning platform |
| url | TEXT | | Course URL |
| total_videos | INTEGER | | Total lecture count |
| completed_videos | INTEGER | DEFAULT 0 | Lectures completed |
| progress_percent | INTEGER | DEFAULT 0 | 0-100 completion |
| deadline | TIMESTAMPTZ | NOT NULL | Completion deadline |
| why_enrolled | TEXT | | Motivation for enrolling |
| status | TEXT | DEFAULT 'not_started' CHECK (not_started, active, paused, completed, abandoned) | |
| daily_minutes_needed | FLOAT | | Calculated daily effort |
| daily_minutes_target | INTEGER | DEFAULT 30 | Target daily study time |
| related_goal_id | UUID | FK -> goals(id) ON DELETE SET NULL | |
| abandonment_reason | TEXT | | Why abandoned |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | |

---

## 6. Module: YouTube Saves

### youtube_saves

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | |
| url | TEXT | NOT NULL | Video URL |
| title | TEXT | | Video title |
| channel | TEXT | | Channel name |
| thumbnail_url | TEXT | | Thumbnail image URL |
| ai_summary | TEXT | | AI-generated summary |
| tags | TEXT[] | DEFAULT '{}' | User-defined tags |
| related_goal_id | UUID | FK -> goals(id) ON DELETE SET NULL | |
| status | TEXT | DEFAULT 'unseen' CHECK (unseen, scheduled, watched, archived) | Viewing status |
| saved_at | TIMESTAMPTZ | DEFAULT NOW() | |
| watched_at | TIMESTAMPTZ | | When watched |
| watch_by_date | DATE | | Expiry: saved_at + 60 days |

---

## 7. Module: Resources

### resources

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | |
| title | TEXT | NOT NULL | Resource title |
| url | TEXT | NOT NULL | Resource URL |
| resource_type | TEXT | CHECK (article, book, github, tool, paper, thread, other) | Content type |
| tags | TEXT[] | DEFAULT '{}' | User tags |
| notes | TEXT | | Personal notes |
| ai_summary | TEXT | | AI-generated summary |
| related_goal_id | UUID | FK -> goals(id) ON DELETE SET NULL | |
| status | TEXT | DEFAULT 'unread' CHECK (unread, reading, read, archived) | |
| is_archived | BOOLEAN | DEFAULT FALSE | |
| saved_at | TIMESTAMPTZ | DEFAULT NOW() | |
| last_surfaced_at | TIMESTAMPTZ | | Last surfaced by AI |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | |

---

## 8. Module: Ideas

### ideas

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | |
| title | TEXT | NOT NULL | Idea title |
| description | TEXT | | Detailed description |
| idea_type | TEXT | CHECK (startup, project, content, feature, other) | |
| ai_analysis | JSONB | DEFAULT '{}' | {competitors:[], market_size, feasibility, insight} |
| status | TEXT | DEFAULT 'raw' CHECK (raw, researching, validating, building, archived) | Pipeline stage |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | |

---

## 9. Module: Goals

### goals

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | |
| title | TEXT | NOT NULL | Goal title |
| description | TEXT | | |
| roadmap_type | TEXT | CHECK (career_skills, business_launch, exam_prep, study_learning, project, health, financial, custom) | Goal type |
| target_date | TIMESTAMPTZ | | Target completion |
| why_it_matters | TEXT | | Motivation |
| hours_per_day | FLOAT | DEFAULT 2.0 | |
| days_per_week | FLOAT | DEFAULT 5.0 | |
| intensity | TEXT | DEFAULT 'medium' CHECK (low, medium, high) | |
| status | TEXT | DEFAULT 'active' CHECK (active, completed, paused, abandoned) | |
| progress_percent | INTEGER | DEFAULT 0 | |
| is_hard_deadline | BOOLEAN | DEFAULT FALSE | |
| linked_roadmap_id | UUID | FK -> roadmaps(id) ON DELETE SET NULL | |
| nodes | JSONB | DEFAULT '[]' | Legacy roadmap nodes |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | |

### roadmaps

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | |
| title | TEXT | NOT NULL | |
| roadmap_type | TEXT | CHECK (career_skills, business_launch, exam_prep, study_learning, project, health, financial, custom) | |
| status | TEXT | DEFAULT 'active' CHECK (active, completed, paused, archived) | |
| nodes | JSONB | DEFAULT '[]' | React Flow nodes |
| edges | JSONB | DEFAULT '[]' | React Flow edges |
| hard_deadline | DATE | | |
| hours_per_day | FLOAT | DEFAULT 2.0 | |
| days_per_week | FLOAT | DEFAULT 5.0 | |
| intensity | TEXT | DEFAULT 'normal' CHECK (conservative, normal, aggressive) | |
| last_ai_check_at | TIMESTAMPTZ | | |
| update_frequency | TEXT | DEFAULT 'weekly' CHECK (daily, weekly, monthly) | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | |

### roadmap_updates

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| roadmap_id | UUID | FK -> roadmaps(id) ON DELETE CASCADE NOT NULL | |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | |
| node_label | TEXT | | Affected node |
| update_type | TEXT | CHECK (critical, suggested, informational) | |
| old_value | TEXT | | |
| new_value | TEXT | | |
| reason | TEXT | | Why AI suggests change |
| source_url | TEXT | | Supporting link |
| status | TEXT | DEFAULT 'pending' CHECK (pending, accepted, rejected, snoozed) | |
| detected_at | TIMESTAMPTZ | DEFAULT NOW() | |

---

## 10. Module: Opportunities

### opportunities

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | |
| title | TEXT | NOT NULL | |
| company | TEXT | | Organization name |
| url | TEXT | NOT NULL | Application URL |
| opportunity_type | TEXT | CHECK (internship, hackathon, open_source, fellowship, freelance, competition, scholarship, course) | |
| description | TEXT | | |
| skills_required | TEXT[] | | Skills extracted from listing |
| deadline | TIMESTAMPTZ | | Application deadline |
| match_score | INTEGER | | 0-100 AI match score |
| match_reason | TEXT | | Why it matches user profile |
| status | TEXT | DEFAULT 'new' CHECK (new, saved, applied, rejected, accepted) | |
| found_at | TIMESTAMPTZ | DEFAULT NOW() | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

---

## 11. Module: Income

### income_sources

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | |
| name | TEXT | NOT NULL | |
| source_type | TEXT | NOT NULL CHECK (freelance, content, teaching, open_source, product, hackathon, internship, saas, other) | |
| platform | TEXT | | Platform name |
| monthly_amount | DECIMAL | DEFAULT 0 | |
| hours_per_week | DECIMAL | DEFAULT 0 | |
| status | TEXT | DEFAULT 'active' CHECK (active, paused, ended) | |
| started_at | DATE | | |
| notes | TEXT | | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | |

### income_logs

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | |
| source_id | UUID | FK -> income_sources(id) ON DELETE CASCADE | |
| amount | DECIMAL | NOT NULL | |
| date | DATE | NOT NULL | |
| description | TEXT | | |
| hours_spent | DECIMAL | | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

---

## 12. Module: Projects

### projects

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | |
| title | TEXT | NOT NULL | |
| description | TEXT | | |
| tech_stack | TEXT[] | DEFAULT '{}' | |
| phase | TEXT | DEFAULT 'planning' CHECK (planning, design, build, test, launch, maintain) | |
| status | TEXT | DEFAULT 'active' CHECK (active, paused, completed, archived) | |
| github_url | TEXT | | |
| live_url | TEXT | | |
| next_action | TEXT | NOT NULL | Immediate next step |
| blocker | TEXT | | Current blocker |
| related_income_source_id | UUID | FK -> income_sources(id) ON DELETE SET NULL | |
| last_commit_at | TIMESTAMPTZ | | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | |

---

## 13. Module: Academics

### academic_subjects

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | |
| name | TEXT | NOT NULL | Subject name |
| code | TEXT | | Course code |
| credits | INTEGER | | Credit hours |
| semester | TEXT | | Semester identifier |
| exam_date | TIMESTAMPTZ | | |
| marks_scored | DECIMAL | | |
| max_marks | DECIMAL | DEFAULT 100 | |
| grade | TEXT | | Letter grade |
| at_risk_flag | BOOLEAN | DEFAULT FALSE | |
| related_goal_id | UUID | FK -> goals(id) ON DELETE SET NULL | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | |

### marks

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| subject_id | UUID | FK -> academic_subjects(id) ON DELETE CASCADE NOT NULL | |
| exam_type | TEXT | CHECK (assignment, midterm, final, practical, quiz, other) | |
| marks_obtained | FLOAT | NOT NULL | |
| max_marks | FLOAT | NOT NULL | |
| date | DATE | | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

---

## 14. Module: Habits

### habits

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | |
| title | TEXT | NOT NULL | |
| frequency | TEXT | NOT NULL CHECK (daily, weekdays, weekends, weekly, custom) | |
| custom_days | INTEGER[] | | Days for custom frequency (0=Sun) |
| time_target_minutes | INTEGER | | |
| current_streak | INTEGER | DEFAULT 0 | |
| best_streak | INTEGER | DEFAULT 0 | |
| consistency_percentage | FLOAT | DEFAULT 0 | |
| last_completed_at | DATE | | |
| linked_goal_id | UUID | FK -> goals(id) ON DELETE SET NULL | |
| status | TEXT | DEFAULT 'active' CHECK (active, paused, archived) | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | |

### habit_logs

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| habit_id | UUID | FK -> habits(id) ON DELETE CASCADE NOT NULL | |
| date | DATE | NOT NULL | |
| completed | BOOLEAN | DEFAULT FALSE | |
| minutes_spent | INTEGER | | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| UNIQUE(habit_id, date) | | | One log per habit per day |

---

## 15. Module: Sleep

### sleep_logs

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | |
| sleep_start | TIMESTAMPTZ | NOT NULL | Bedtime |
| sleep_end | TIMESTAMPTZ | NOT NULL | Wake time |
| duration_minutes | INTEGER | | Calculated duration |
| quality_rating | INTEGER | CHECK (1-5) | Subjective rating |
| sleep_score | INTEGER | CHECK (0-100) | Composite score |
| sleep_debt_minutes | INTEGER | DEFAULT 0 | Accumulated debt |
| date | DATE | NOT NULL | |
| source | TEXT | DEFAULT 'manual' CHECK (manual, google_fit, fitbit) | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| UNIQUE(user_id, date) | | | One log per day |

---

## 16. Module: Time Tracking

### time_logs

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | |
| task_id | UUID | FK -> tasks(id) ON DELETE SET NULL | |
| description | TEXT | | |
| started_at | TIMESTAMPTZ | NOT NULL | |
| ended_at | TIMESTAMPTZ | | |
| duration_seconds | INTEGER | | |
| is_pomodoro | BOOLEAN | DEFAULT FALSE | |
| is_deep_work | BOOLEAN | DEFAULT FALSE | Sessions >90min |
| energy_level | INTEGER | CHECK (1-5) | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

---

## 17. Module: AI Chat

### chat_messages

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | |
| role | TEXT | NOT NULL CHECK (user, assistant, system) | |
| content | TEXT | NOT NULL | Message body |
| action_taken | TEXT | | Action ARIA executed |
| metadata | JSONB | DEFAULT '{}' | {context_used, model, tokens_used} |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

---

## 18. Module: AI Memory

### aria_memory

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | |
| memory_type | TEXT | NOT NULL CHECK (preference, fact, pattern, decision) | |
| content | TEXT | NOT NULL | Memory content |
| confidence | FLOAT | DEFAULT 0.8 CHECK (0-1) | Certainty score |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| last_referenced_at | TIMESTAMPTZ | DEFAULT NOW() | |

---

## 19. Module: Briefings & Reviews

### daily_briefings

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | |
| date | DATE | NOT NULL | |
| briefing_content | JSONB | | {today_focus, opportunities, ...} |
| opportunities_shown | INTEGER | DEFAULT 0 | |
| aria_top_pick | TEXT | | |
| was_read | BOOLEAN | DEFAULT FALSE | |
| read_at | TIMESTAMPTZ | | |
| was_emailed | BOOLEAN | DEFAULT FALSE | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| UNIQUE(user_id, date) | | | |

### weekly_reviews

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | |
| week_start | DATE | NOT NULL | |
| review_content | TEXT | | |
| tasks_completed | INTEGER | DEFAULT 0 | |
| tasks_missed | INTEGER | DEFAULT 0 | |
| courses_studied_minutes | INTEGER | DEFAULT 0 | |
| income_logged | DECIMAL | DEFAULT 0 | |
| best_day | TEXT | | |
| aria_pattern_insight | TEXT | | |
| focus_for_next_week | TEXT | | |
| was_emailed | BOOLEAN | DEFAULT FALSE | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| UNIQUE(user_id, week_start) | | | |

---

## 20. Module: Study Sessions

### study_sessions

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | |
| course_id | UUID | FK -> courses(id) ON DELETE SET NULL | |
| subject | TEXT | | |
| topic | TEXT | | |
| started_at | TIMESTAMPTZ | NOT NULL | |
| ended_at | TIMESTAMPTZ | | |
| duration_minutes | INTEGER | | |
| notes | TEXT | | |
| review_due_dates | JSONB | DEFAULT '[]' | Spaced repetition schedule |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

---

## 21. Module: Daily Logs

### daily_logs

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | |
| date | DATE | NOT NULL | |
| entry | TEXT | | Evening reflection |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| UNIQUE(user_id, date) | | | |

---

## 22. Notifications Table (Future)

### notifications

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK DEFAULT gen_random_uuid() | |
| user_id | UUID | FK -> auth.users(id) ON DELETE CASCADE NOT NULL | |
| title | TEXT | NOT NULL | |
| body | TEXT | | |
| type | TEXT | CHECK (briefing, opportunity, nudge, reminder, system) | |
| is_read | BOOLEAN | DEFAULT FALSE | |
| read_at | TIMESTAMPTZ | | |
| action_url | TEXT | | Deeplink |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

---

## 23. Schema Evolution Notes

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-01 | Initial schema (18 tables) |
| 1.1.0 | 2026-06-11 | Added roadmaps, roadmap_updates, study_sessions, daily_logs |
| 1.2.0 | 2026-06-20 | Added notifications table, marks table, habit_logs improvements |

---

## 24. Cross-Reference

| Module | Tables | Schema Doc | API Doc |
|---|---|---|---|
| User Profile | users_profile | §3 | Auth API |
| Tasks | tasks, subtasks, task_dependencies | §4 | Tasks API |
| Courses | courses | §5 | Courses API |
| YouTube | youtube_saves | §6 | Videos API |
| Resources | resources | §7 | Resources API |
| Ideas | ideas | §8 | Ideas API |
| Goals | goals, roadmaps, roadmap_updates | §9 | Goals API, Roadmap API |
| Opportunities | opportunities | §10 | Opportunities API |
| Income | income_sources, income_logs | §11 | Income API |
| Projects | projects | §12 | Projects API |
| Academics | academic_subjects, marks | §13 | Academics API |
| Habits | habits, habit_logs | §14 | Habits API |
| Sleep | sleep_logs | §15 | Sleep API |
| Time | time_logs | §16 | Time API |
| AI Chat | chat_messages | §17 | Chat API |
| AI Memory | aria_memory | §18 | Memory API |
| Briefings | daily_briefings, weekly_reviews | §19 | Briefings API, Reviews API |
| Study | study_sessions | §20 | — |
| Journal | daily_logs | §21 | — |

---

## 25. Related Documents

| Document | Description |
|---|---|
| [ERD.md](ERD.md) | Entity relationship diagram with cardinalities |
| [Indexes.md](Indexes.md) | Index strategy and catalog |
| [Constraints.md](Constraints.md) | Constraint catalog |
| [Policies.md](Policies.md) | RLS policy catalog |
| [15_Database.md](15_Database.md) | Legacy database overview (deprecated) |
