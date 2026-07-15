-- =============================================================
-- Migration 010: Core Application Schema
-- Creates: 30 tables for Second Brain OS core application
-- Includes: ENUM types, all PKs, FKs, CHECK constraints,
--           UNIQUE constraints, JSONB defaults
-- Depends on: auth.users (Supabase), pgcrypto extension
-- =============================================================

BEGIN;

-- === Extensions ===
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================
-- 1. USERS & PROFILE
-- =============================================================

-- 1a. users_profile — One row per auth user
CREATE TABLE IF NOT EXISTS users_profile (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    name              TEXT,
    email             TEXT,
    college           TEXT,
    year              INTEGER,
    branch            TEXT,
    skills            JSONB DEFAULT '[]',
    opportunity_preferences JSONB DEFAULT '{}',
    daily_routine     JSONB DEFAULT '{}',
    github_username   TEXT,
    linkedin_url      TEXT,
    onboarding_completed BOOLEAN DEFAULT FALSE,
    bedtime           TIME,
    wake_time         TIME,
    push_subscription JSONB,
    google_calendar_token JSONB,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE users_profile IS 'User profile, preferences, and system configuration';

-- =============================================================
-- 2. ROADMAPS (created before goals due to FK dependency)
-- =============================================================

-- 2a. roadmaps — Visual roadmap canvas data (React Flow)
CREATE TABLE IF NOT EXISTS roadmaps (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    title             TEXT NOT NULL,
    roadmap_type      TEXT CHECK (roadmap_type IN ('career_skills','business_launch','exam_prep','study_learning','project','health','financial','custom')),
    status            TEXT DEFAULT 'active' CHECK (status IN ('active','completed','paused','archived')),
    nodes             JSONB DEFAULT '[]',
    edges             JSONB DEFAULT '[]',
    hard_deadline     DATE,
    hours_per_day     FLOAT DEFAULT 2.0,
    days_per_week     FLOAT DEFAULT 5.0,
    intensity         TEXT DEFAULT 'normal' CHECK (intensity IN ('conservative','normal','aggressive')),
    last_ai_check_at  TIMESTAMPTZ,
    update_frequency  TEXT DEFAULT 'weekly' CHECK (update_frequency IN ('daily','weekly','monthly')),
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE roadmaps IS 'Visual roadmap canvas with React Flow nodes and edges';

-- 2b. roadmap_updates — AI-detected changes to roadmap nodes
CREATE TABLE IF NOT EXISTS roadmap_updates (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    roadmap_id        UUID REFERENCES roadmaps(id) ON DELETE CASCADE NOT NULL,
    user_id           UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    node_label        TEXT,
    update_type       TEXT CHECK (update_type IN ('critical','suggested','informational')),
    old_value         TEXT,
    new_value         TEXT,
    reason            TEXT,
    source_url        TEXT,
    status            TEXT DEFAULT 'pending' CHECK (status IN ('pending','accepted','rejected','snoozed')),
    detected_at       TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE roadmap_updates IS 'AI-detected suggestions for roadmap node changes';

-- =============================================================
-- 3. GOALS (FK to roadmaps SET NULL, so roadmaps first)
-- =============================================================

-- 3a. goals — Goal management with roadmap tracking
CREATE TABLE IF NOT EXISTS goals (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    title             TEXT NOT NULL,
    description       TEXT,
    roadmap_type      TEXT CHECK (roadmap_type IN ('career_skills','business_launch','exam_prep','study_learning','project','health','financial','custom')),
    target_date       TIMESTAMPTZ,
    why_it_matters    TEXT,
    hours_per_day     FLOAT DEFAULT 2.0,
    days_per_week     FLOAT DEFAULT 5.0,
    intensity         TEXT DEFAULT 'medium' CHECK (intensity IN ('low','medium','high')),
    status            TEXT DEFAULT 'active' CHECK (status IN ('active','completed','paused','abandoned')),
    progress_percent  INTEGER DEFAULT 0,
    is_hard_deadline  BOOLEAN DEFAULT FALSE,
    linked_roadmap_id UUID REFERENCES roadmaps(id) ON DELETE SET NULL,
    nodes             JSONB DEFAULT '[]',
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE goals IS 'Goals with optional roadmap links and progress tracking';

-- =============================================================
-- 4. INCOME SOURCES (needed by projects FK)
-- =============================================================

-- 4a. income_sources — Income source definitions
CREATE TABLE IF NOT EXISTS income_sources (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    name              TEXT NOT NULL,
    source_type       TEXT NOT NULL CHECK (source_type IN ('freelance','content','teaching','open_source','product','hackathon','internship','saas','other')),
    platform          TEXT,
    monthly_amount    DECIMAL DEFAULT 0,
    hours_per_week    DECIMAL DEFAULT 0,
    status            TEXT DEFAULT 'active' CHECK (status IN ('active','paused','ended')),
    started_at        DATE,
    notes             TEXT,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE income_sources IS 'Income source definitions — freelance, content, etc.';

-- =============================================================
-- 5. PROJECTS (FK to income_sources SET NULL)
-- =============================================================

-- 5a. projects — Project tracking with phases and blockers
CREATE TABLE IF NOT EXISTS projects (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    title                  TEXT NOT NULL,
    description            TEXT,
    tech_stack             TEXT[] DEFAULT '{}',
    phase                  TEXT DEFAULT 'planning' CHECK (phase IN ('planning','design','build','test','launch','maintain')),
    status                 TEXT DEFAULT 'active' CHECK (status IN ('active','paused','completed','archived')),
    github_url             TEXT,
    live_url               TEXT,
    next_action            TEXT NOT NULL,
    blocker                TEXT,
    related_income_source_id UUID REFERENCES income_sources(id) ON DELETE SET NULL,
    last_commit_at         TIMESTAMPTZ,
    created_at             TIMESTAMPTZ DEFAULT NOW(),
    updated_at             TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE projects IS 'Project tracking with phases, blockers, GitHub integration';

-- =============================================================
-- 6. TASKS (FK to goals + projects SET NULL)
-- =============================================================

-- 6a. tasks — Task management
CREATE TABLE IF NOT EXISTS tasks (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    title             TEXT NOT NULL,
    description       TEXT,
    priority          TEXT DEFAULT 'medium' CHECK (priority IN ('low','medium','high','urgent')),
    category          TEXT DEFAULT 'personal' CHECK (category IN ('study','project','habit','personal','income','career','health')),
    status            TEXT DEFAULT 'pending' CHECK (status IN ('pending','in_progress','completed','cancelled','missed')),
    estimated_minutes INTEGER,
    actual_minutes    INTEGER,
    due_date          TIMESTAMPTZ,
    scheduled_start   TIMESTAMPTZ,
    source            TEXT DEFAULT 'manual' CHECK (source IN ('manual','roadmap','aria','opportunity','recurring','course')),
    goal_id           UUID REFERENCES goals(id) ON DELETE SET NULL,
    project_id        UUID REFERENCES projects(id) ON DELETE SET NULL,
    completed_at      TIMESTAMPTZ,
    rescheduled_from  TIMESTAMPTZ,
    missed_count      INTEGER DEFAULT 0,
    recurrence        TEXT,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE tasks IS 'Task management with priority, status, dependencies, and recurrence';

-- 6b. subtasks — Subtask breakdown for complex tasks
CREATE TABLE IF NOT EXISTS subtasks (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id       UUID REFERENCES tasks(id) ON DELETE CASCADE NOT NULL,
    title         TEXT NOT NULL,
    is_completed  BOOLEAN DEFAULT FALSE,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE subtasks IS 'Subtasks for breaking down complex tasks';

-- 6c. task_dependencies — Directed dependency graph between tasks
CREATE TABLE IF NOT EXISTS task_dependencies (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id        UUID REFERENCES tasks(id) ON DELETE CASCADE NOT NULL,
    depends_on_id  UUID REFERENCES tasks(id) ON DELETE CASCADE NOT NULL,
    UNIQUE(task_id, depends_on_id)
);

COMMENT ON TABLE task_dependencies IS 'Task dependency relationships for sequenced execution';

-- =============================================================
-- 7. COURSES (FK to goals SET NULL)
-- =============================================================

CREATE TABLE IF NOT EXISTS courses (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    title               TEXT NOT NULL,
    platform            TEXT NOT NULL CHECK (platform IN ('udemy','coursera','nptel','youtube','college','other')),
    url                 TEXT,
    total_videos        INTEGER,
    completed_videos    INTEGER DEFAULT 0,
    progress_percent    INTEGER DEFAULT 0,
    deadline            TIMESTAMPTZ NOT NULL,
    why_enrolled        TEXT,
    status              TEXT DEFAULT 'not_started' CHECK (status IN ('not_started','active','paused','completed','abandoned')),
    daily_minutes_needed FLOAT,
    daily_minutes_target INTEGER DEFAULT 30,
    related_goal_id     UUID REFERENCES goals(id) ON DELETE SET NULL,
    abandonment_reason  TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE courses IS 'Course tracking from multiple platforms with mandatory deadlines';

-- =============================================================
-- 8. YOUTUBE SAVES (FK to goals SET NULL)
-- =============================================================

CREATE TABLE IF NOT EXISTS youtube_saves (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    url               TEXT NOT NULL,
    title             TEXT,
    channel           TEXT,
    thumbnail_url     TEXT,
    ai_summary        TEXT,
    tags              TEXT[] DEFAULT '{}',
    related_goal_id   UUID REFERENCES goals(id) ON DELETE SET NULL,
    status            TEXT DEFAULT 'unseen' CHECK (status IN ('unseen','scheduled','watched','archived')),
    saved_at          TIMESTAMPTZ DEFAULT NOW(),
    watched_at        TIMESTAMPTZ,
    watch_by_date     DATE
);

COMMENT ON TABLE youtube_saves IS 'YouTube knowledge vault with AI summaries and expiry logic';

-- =============================================================
-- 9. RESOURCES (FK to goals SET NULL)
-- =============================================================

CREATE TABLE IF NOT EXISTS resources (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    title             TEXT NOT NULL,
    url               TEXT NOT NULL,
    resource_type     TEXT CHECK (resource_type IN ('article','book','github','tool','paper','thread','other')),
    tags              TEXT[] DEFAULT '{}',
    notes             TEXT,
    ai_summary        TEXT,
    related_goal_id   UUID REFERENCES goals(id) ON DELETE SET NULL,
    status            TEXT DEFAULT 'unread' CHECK (status IN ('unread','reading','read','archived')),
    is_archived       BOOLEAN DEFAULT FALSE,
    saved_at          TIMESTAMPTZ DEFAULT NOW(),
    last_surfaced_at  TIMESTAMPTZ,
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE resources IS 'Article, book, tool, and repo storage with auto-tagging';

-- =============================================================
-- 10. IDEAS
-- =============================================================

CREATE TABLE IF NOT EXISTS ideas (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    title             TEXT NOT NULL,
    description       TEXT,
    idea_type         TEXT CHECK (idea_type IN ('startup','project','content','feature','other')),
    ai_analysis       JSONB DEFAULT '{}',
    status            TEXT DEFAULT 'raw' CHECK (status IN ('raw','researching','validating','building','archived')),
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE ideas IS 'Startup and business idea vault with AI market analysis';

-- =============================================================
-- 11. OPPORTUNITIES
-- =============================================================

CREATE TABLE IF NOT EXISTS opportunities (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    title             TEXT NOT NULL,
    company           TEXT,
    url               TEXT NOT NULL,
    opportunity_type  TEXT CHECK (opportunity_type IN ('internship','hackathon','open_source','fellowship','freelance','competition','scholarship','course')),
    description       TEXT,
    skills_required   TEXT[],
    deadline          TIMESTAMPTZ,
    match_score       INTEGER,
    match_reason      TEXT,
    status            TEXT DEFAULT 'new' CHECK (status IN ('new','saved','applied','rejected','accepted')),
    found_at          TIMESTAMPTZ DEFAULT NOW(),
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE opportunities IS 'Scanned opportunities from Opportunity Radar with match scores';

-- =============================================================
-- 12. INCOME LOGS (FK to income_sources CASCADE)
-- =============================================================

CREATE TABLE IF NOT EXISTS income_logs (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    source_id     UUID REFERENCES income_sources(id) ON DELETE CASCADE,
    amount        DECIMAL NOT NULL,
    date          DATE NOT NULL,
    description   TEXT,
    hours_spent   DECIMAL,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE income_logs IS 'Individual income entries per source';

-- =============================================================
-- 13. ACADEMIC SUBJECTS (FK to goals SET NULL)
-- =============================================================

CREATE TABLE IF NOT EXISTS academic_subjects (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    name              TEXT NOT NULL,
    code              TEXT,
    credits           INTEGER,
    semester          TEXT,
    exam_date         TIMESTAMPTZ,
    marks_scored      DECIMAL,
    max_marks         DECIMAL DEFAULT 100,
    grade             TEXT,
    at_risk_flag      BOOLEAN DEFAULT FALSE,
    related_goal_id   UUID REFERENCES goals(id) ON DELETE SET NULL,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE academic_subjects IS 'Academic subjects with marks and at-risk detection';

-- =============================================================
-- 14. MARKS (FK to academic_subjects CASCADE)
-- =============================================================

CREATE TABLE IF NOT EXISTS marks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id      UUID REFERENCES academic_subjects(id) ON DELETE CASCADE NOT NULL,
    exam_type       TEXT CHECK (exam_type IN ('assignment','midterm','final','practical','quiz','other')),
    marks_obtained  FLOAT NOT NULL,
    max_marks       FLOAT NOT NULL,
    date            DATE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE marks IS 'Academic marks per exam, assignment, or assessment';

-- =============================================================
-- 15. HABITS (FK to goals SET NULL)
-- =============================================================

CREATE TABLE IF NOT EXISTS habits (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id               UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    title                 TEXT NOT NULL,
    frequency             TEXT NOT NULL CHECK (frequency IN ('daily','weekdays','weekends','weekly','custom')),
    custom_days           INTEGER[],
    time_target_minutes   INTEGER,
    current_streak        INTEGER DEFAULT 0,
    best_streak           INTEGER DEFAULT 0,
    consistency_percentage FLOAT DEFAULT 0,
    last_completed_at     DATE,
    linked_goal_id        UUID REFERENCES goals(id) ON DELETE SET NULL,
    status                TEXT DEFAULT 'active' CHECK (status IN ('active','paused','archived')),
    created_at            TIMESTAMPTZ DEFAULT NOW(),
    updated_at            TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE habits IS 'Habit tracking with streaks, goal linking, and flexible frequencies';

-- =============================================================
-- 16. HABIT LOGS (FK to habits CASCADE)
-- =============================================================

CREATE TABLE IF NOT EXISTS habit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    habit_id        UUID REFERENCES habits(id) ON DELETE CASCADE NOT NULL,
    date            DATE NOT NULL,
    completed       BOOLEAN DEFAULT FALSE,
    minutes_spent   INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(habit_id, date)
);

COMMENT ON TABLE habit_logs IS 'Daily habit completion logs';

-- =============================================================
-- 17. SLEEP LOGS
-- =============================================================

CREATE TABLE IF NOT EXISTS sleep_logs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    sleep_start         TIMESTAMPTZ NOT NULL,
    sleep_end           TIMESTAMPTZ NOT NULL,
    duration_minutes    INTEGER,
    quality_rating      INTEGER CHECK (quality_rating BETWEEN 1 AND 5),
    sleep_score         INTEGER CHECK (sleep_score BETWEEN 0 AND 100),
    sleep_debt_minutes  INTEGER DEFAULT 0,
    date                DATE NOT NULL,
    source              TEXT DEFAULT 'manual' CHECK (source IN ('manual','google_fit','fitbit')),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, date)
);

COMMENT ON TABLE sleep_logs IS 'Sleep tracking with quality rating, score, and sleep debt';

-- =============================================================
-- 18. TIME LOGS (FK to tasks SET NULL)
-- =============================================================

CREATE TABLE IF NOT EXISTS time_logs (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    task_id           UUID REFERENCES tasks(id) ON DELETE SET NULL,
    description       TEXT,
    started_at        TIMESTAMPTZ NOT NULL,
    ended_at          TIMESTAMPTZ,
    duration_seconds  INTEGER,
    is_pomodoro       BOOLEAN DEFAULT FALSE,
    is_deep_work      BOOLEAN DEFAULT FALSE,
    energy_level      INTEGER CHECK (energy_level BETWEEN 1 AND 5),
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE time_logs IS 'Time tracking sessions per task with Pomodoro and deep work flags';

-- =============================================================
-- 19. CHAT MESSAGES
-- =============================================================

CREATE TABLE IF NOT EXISTS chat_messages (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('user','assistant','system')),
    content       TEXT NOT NULL,
    action_taken  TEXT,
    metadata      JSONB DEFAULT '{}',
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE chat_messages IS 'ARIA conversation history';

-- =============================================================
-- 20. ARIA MEMORY
-- =============================================================

CREATE TABLE IF NOT EXISTS aria_memory (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    memory_type         TEXT NOT NULL CHECK (memory_type IN ('preference','fact','pattern','decision')),
    content             TEXT NOT NULL,
    confidence          FLOAT DEFAULT 0.8 CHECK (confidence BETWEEN 0 AND 1),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    last_referenced_at  TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE aria_memory IS "ARIA's long-term memory about user preferences, facts, and patterns";

-- =============================================================
-- 21. DAILY BRIEFINGS
-- =============================================================

CREATE TABLE IF NOT EXISTS daily_briefings (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id               UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    date                  DATE NOT NULL,
    briefing_content      JSONB,
    opportunities_shown   INTEGER DEFAULT 0,
    aria_top_pick         TEXT,
    was_read              BOOLEAN DEFAULT FALSE,
    read_at               TIMESTAMPTZ,
    was_emailed           BOOLEAN DEFAULT FALSE,
    created_at            TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, date)
);

COMMENT ON TABLE daily_briefings IS 'Morning intelligence briefings with focus, opportunities, and top pick';

-- =============================================================
-- 22. WEEKLY REVIEWS
-- =============================================================

CREATE TABLE IF NOT EXISTS weekly_reviews (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id               UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    week_start            DATE NOT NULL,
    review_content        TEXT,
    tasks_completed       INTEGER DEFAULT 0,
    tasks_missed          INTEGER DEFAULT 0,
    courses_studied_minutes INTEGER DEFAULT 0,
    income_logged         DECIMAL DEFAULT 0,
    best_day              TEXT,
    aria_pattern_insight  TEXT,
    focus_for_next_week   TEXT,
    was_emailed           BOOLEAN DEFAULT FALSE,
    created_at            TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, week_start)
);

COMMENT ON TABLE weekly_reviews IS 'Sunday weekly review reports with stats and AI insights';

-- =============================================================
-- 23. STUDY SESSIONS (FK to courses SET NULL)
-- =============================================================

CREATE TABLE IF NOT EXISTS study_sessions (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    course_id         UUID REFERENCES courses(id) ON DELETE SET NULL,
    subject           TEXT,
    topic             TEXT,
    started_at        TIMESTAMPTZ NOT NULL,
    ended_at          TIMESTAMPTZ,
    duration_minutes  INTEGER,
    notes             TEXT,
    review_due_dates  JSONB DEFAULT '[]',
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE study_sessions IS 'Focused study sessions with spaced repetition scheduling';

-- =============================================================
-- 24. DAILY LOGS
-- =============================================================

CREATE TABLE IF NOT EXISTS daily_logs (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    date          DATE NOT NULL,
    entry         TEXT,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, date)
);

COMMENT ON TABLE daily_logs IS 'Evening reflection / journal entries';

-- =============================================================
-- 25. NOTIFICATIONS
-- =============================================================

CREATE TABLE IF NOT EXISTS notifications (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    title         TEXT NOT NULL,
    body          TEXT,
    type          TEXT CHECK (type IN ('briefing','opportunity','nudge','reminder','system')),
    is_read       BOOLEAN DEFAULT FALSE,
    read_at       TIMESTAMPTZ,
    action_url    TEXT,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE notifications IS 'In-app notifications for briefings, opportunities, nudges, and reminders';

-- =============================================================
-- 26. AUDIT LOG
-- =============================================================

CREATE TABLE IF NOT EXISTS audit_log (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name    TEXT NOT NULL,
    operation     TEXT NOT NULL CHECK (operation IN ('INSERT','UPDATE','DELETE')),
    record_id     UUID NOT NULL,
    old_data      JSONB,
    new_data      JSONB,
    changed_by    UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    user_id       UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    changed_at    TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE audit_log IS 'Generic audit log capturing all mutations with before/after snapshots';

-- =============================================================
-- 27. TOKEN USAGE
-- =============================================================

CREATE TABLE IF NOT EXISTS token_usage (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    endpoint      TEXT NOT NULL,
    model         TEXT,
    tokens_in     INTEGER DEFAULT 0,
    tokens_out    INTEGER DEFAULT 0,
    total_tokens  INTEGER GENERATED ALWAYS AS (COALESCE(tokens_in, 0) + COALESCE(tokens_out, 0)) STORED,
    cost          DECIMAL DEFAULT 0,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE token_usage IS 'AI token usage tracking per endpoint per user';

COMMIT;
