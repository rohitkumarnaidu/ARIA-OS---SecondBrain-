-- ARIA OS — Database Index Optimization Migration
-- Run in Supabase SQL Editor to add missing performance indexes

-- ============================================================================
-- 1. Composite indexes for frequent query patterns
-- ============================================================================

-- Tasks: filter by user + status, sorted by due_date
CREATE INDEX IF NOT EXISTS idx_tasks_user_status_due
    ON tasks (user_id, status, due_date DESC);

-- Tasks: filter by user + priority
CREATE INDEX IF NOT EXISTS idx_tasks_user_priority
    ON tasks (user_id, priority DESC);

-- Habits: filter by user + active
CREATE INDEX IF NOT EXISTS idx_habits_user_active
    ON habits (user_id, is_active);

-- Habit Logs: filter by user + date range (daily briefing query)
CREATE INDEX IF NOT EXISTS idx_habit_logs_user_date
    ON habit_logs (user_id, date DESC);

-- Time Logs: user + date for daily stats
CREATE INDEX IF NOT EXISTS idx_time_logs_user_date
    ON time_logs (user_id, date DESC);

-- Sleep Logs: user + date for sleep analysis
CREATE INDEX IF NOT EXISTS idx_sleep_logs_user_date
    ON sleep_logs (user_id, date DESC);

-- Chat Messages: user + created_at for history view
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_created
    ON chat_messages (user_id, created_at DESC);

-- ============================================================================
-- 2. Partial indexes for filtered queries
-- ============================================================================

-- Only active tasks (common dashboard query)
CREATE INDEX IF NOT EXISTS idx_tasks_active
    ON tasks (user_id) WHERE status = 'pending';

-- Only incomplete habit logs today
CREATE INDEX IF NOT EXISTS idx_habit_logs_today
    ON habit_logs (user_id, habit_id)
    WHERE completed = false AND date = CURRENT_DATE;

-- ============================================================================
-- 3. Full-text search indexes for search functionality
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_tasks_title_search
    ON tasks USING gin(to_tsvector('english', title));

CREATE INDEX IF NOT EXISTS idx_ideas_title_search
    ON ideas USING gin(to_tsvector('english', title));

CREATE INDEX IF NOT EXISTS idx_resources_title_search
    ON resources USING gin(to_tsvector('english', title));

-- ============================================================================
-- 4. Indexes for order-by performance
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_daily_briefings_user_date
    ON daily_briefings (user_id, date DESC);

CREATE INDEX IF NOT EXISTS idx_weekly_reviews_user_week
    ON weekly_reviews (user_id, week_start DESC);

CREATE INDEX IF NOT EXISTS idx_aria_memory_user_updated
    ON aria_memory (user_id, updated_at DESC);

-- ============================================================================
-- 5. Index maintenance recommendations
-- ============================================================================

-- Run this periodically (e.g., weekly via cron):
-- REINDEX INDEX CONCURRENTLY idx_tasks_user_status_due;
-- ANALYZE tasks;

COMMENT ON INDEX idx_tasks_user_status_due IS 'Optimizes dashboard task list queries';
COMMENT ON INDEX idx_habit_logs_user_date IS 'Optimizes daily briefing habit queries';
COMMENT ON INDEX idx_time_logs_user_date IS 'Optimizes daily time stats queries';
COMMENT ON INDEX idx_chat_messages_user_created IS 'Optimizes chat history pagination';
COMMENT ON INDEX idx_tasks_title_search IS 'Enables full-text search on tasks';
