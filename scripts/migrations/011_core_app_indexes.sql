-- =============================================================
-- Migration 011: Core Application Indexes
-- Creates: ~50 indexes across 30 tables
-- Includes: Composite (user_id + filter), Partial, GIN (tags,
--           full-text search), and single-column FK indexes
-- =============================================================

BEGIN;

-- =============================================================
-- 1. TASKS (4 indexes)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX IF NOT EXISTS idx_tasks_user_due ON tasks(user_id, due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_user_priority ON tasks(user_id, priority);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date) WHERE status NOT IN ('completed', 'cancelled');

-- =============================================================
-- 2. SUBTASKS (1 index)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_subtasks_task ON subtasks(task_id);

-- =============================================================
-- 3. TASK DEPENDENCIES (2 indexes)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_task_deps_task ON task_dependencies(task_id);
CREATE INDEX IF NOT EXISTS idx_task_deps_depends ON task_dependencies(depends_on_id);

-- =============================================================
-- 4. COURSES (2 indexes)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_courses_user_status ON courses(user_id, status);
CREATE INDEX IF NOT EXISTS idx_courses_deadline ON courses(deadline) WHERE status = 'active';

-- =============================================================
-- 5. YOUTUBE SAVES (2 indexes)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_youtube_user_status ON youtube_saves(user_id, status);
CREATE INDEX IF NOT EXISTS idx_youtube_expiry ON youtube_saves(watch_by_date) WHERE status = 'unseen';

-- =============================================================
-- 6. RESOURCES (3 indexes: composite + GIN tags + GIN FTS)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_resources_user_type ON resources(user_id, resource_type);
CREATE INDEX IF NOT EXISTS idx_resources_tags ON resources USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_resources_fts ON resources USING GIN(to_tsvector('english', title || ' ' || COALESCE(notes, '')));

-- =============================================================
-- 7. IDEAS (1 index)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_ideas_user_status ON ideas(user_id, status);

-- =============================================================
-- 8. GOALS (2 indexes)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_goals_user_status ON goals(user_id, status);
CREATE INDEX IF NOT EXISTS idx_goals_target_date ON goals(target_date) WHERE status = 'active';

-- =============================================================
-- 9. ROADMAPS (1 index)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_roadmaps_user ON roadmaps(user_id);

-- =============================================================
-- 10. ROADMAP UPDATES (1 index)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_roadmap_updates_roadmap ON roadmap_updates(roadmap_id);

-- =============================================================
-- 11. OPPORTUNITIES (3 indexes)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_opportunities_user_status ON opportunities(user_id, status);
CREATE INDEX IF NOT EXISTS idx_opportunities_deadline ON opportunities(deadline) WHERE status IN ('new', 'saved');
CREATE INDEX IF NOT EXISTS idx_opportunities_match ON opportunities(match_score) WHERE match_score >= 50;

-- =============================================================
-- 12. INCOME SOURCES (1 index)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_income_sources_user ON income_sources(user_id);

-- =============================================================
-- 13. INCOME LOGS (2 indexes)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_income_logs_user_date ON income_logs(user_id, date);
CREATE INDEX IF NOT EXISTS idx_income_logs_source ON income_logs(source_id);

-- =============================================================
-- 14. PROJECTS (1 index)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_projects_user_status ON projects(user_id, status);

-- =============================================================
-- 15. ACADEMIC SUBJECTS (2 indexes)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_subjects_user_semester ON academic_subjects(user_id, semester);
CREATE INDEX IF NOT EXISTS idx_subjects_at_risk ON academic_subjects(at_risk_flag) WHERE at_risk_flag = TRUE;

-- =============================================================
-- 16. MARKS (1 index)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_marks_subject ON marks(subject_id);

-- =============================================================
-- 17. HABITS (1 index)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_habits_user_status ON habits(user_id, status);

-- =============================================================
-- 18. HABIT LOGS (1 index)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_habit_logs_habit_date ON habit_logs(habit_id, date);

-- =============================================================
-- 19. SLEEP LOGS (2 indexes)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_sleep_logs_user_date ON sleep_logs(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_sleep_logs_score ON sleep_logs(sleep_score) WHERE sleep_score < 50;

-- =============================================================
-- 20. TIME LOGS (3 indexes)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_time_logs_user_start ON time_logs(user_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_time_logs_task ON time_logs(task_id);
CREATE INDEX IF NOT EXISTS idx_time_logs_deep ON time_logs(is_deep_work) WHERE is_deep_work = TRUE;

-- =============================================================
-- 21. CHAT MESSAGES (1 index)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_chat_messages_user_created ON chat_messages(user_id, created_at DESC);

-- =============================================================
-- 22. ARIA MEMORY (2 indexes)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_aria_memory_user_type ON aria_memory(user_id, memory_type);
CREATE INDEX IF NOT EXISTS idx_aria_memory_last_ref ON aria_memory(last_referenced_at);

-- =============================================================
-- 23. DAILY BRIEFINGS (1 index)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_briefings_user_date ON daily_briefings(user_id, date DESC);

-- =============================================================
-- 24. WEEKLY REVIEWS (1 index)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_weekly_reviews_user ON weekly_reviews(user_id, week_start DESC);

-- =============================================================
-- 25. STUDY SESSIONS (1 index)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_study_sessions_user ON study_sessions(user_id, started_at DESC);

-- =============================================================
-- 26. DAILY LOGS (1 index)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_daily_logs_user_date ON daily_logs(user_id, date DESC);

-- =============================================================
-- 27. NOTIFICATIONS (1 index)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read);

-- =============================================================
-- 28. AUDIT LOG (4 indexes)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_audit_log_table_operation ON audit_log(table_name, operation);
CREATE INDEX IF NOT EXISTS idx_audit_log_record_id ON audit_log(record_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_changed_at ON audit_log(changed_at DESC);

-- =============================================================
-- 29. TOKEN USAGE (1 index)
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_token_usage_user_created ON token_usage(user_id, created_at DESC);

COMMIT;
