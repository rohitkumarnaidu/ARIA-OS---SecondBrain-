-- =============================================================
-- Migration 012: Core Application — RLS Policies
-- Enables RLS on all 30 tables, creates per-table policies
-- Child tables (subtasks, task_dependencies, marks) use
-- EXISTS subquery policies for inherited access.
-- =============================================================

BEGIN;

-- =============================================================
-- 1. RLS HELPER FUNCTIONS
-- =============================================================

CREATE OR REPLACE FUNCTION rls_user_id()
RETURNS UUID AS $$
    SELECT auth.uid();
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION rls_user_id() IS 'Returns current authenticated user ID for RLS policies';

CREATE OR REPLACE FUNCTION rls_is_owner(record_user_id UUID)
RETURNS BOOLEAN AS $$
    SELECT auth.uid() = record_user_id;
$$ LANGUAGE SQL STABLE;

COMMENT ON FUNCTION rls_is_owner(UUID) IS 'Standardized owner check across all RLS policies';

-- =============================================================
-- 2. PRIMARY USER-OWNED TABLES (with user_id column)
-- Each table gets: ALTER TABLE ... ENABLE ROW LEVEL SECURITY;
--                  CREATE POLICY "users_own_data" FOR ALL
-- =============================================================

-- 2a. users_profile
ALTER TABLE users_profile ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'users_profile' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON users_profile
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2b. tasks
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'tasks' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON tasks
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2c. courses
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'courses' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON courses
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2d. youtube_saves
ALTER TABLE youtube_saves ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'youtube_saves' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON youtube_saves
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2e. resources
ALTER TABLE resources ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'resources' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON resources
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2f. ideas
ALTER TABLE ideas ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'ideas' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON ideas
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2g. goals
ALTER TABLE goals ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'goals' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON goals
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2h. roadmaps
ALTER TABLE roadmaps ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'roadmaps' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON roadmaps
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2i. roadmap_updates
ALTER TABLE roadmap_updates ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'roadmap_updates' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON roadmap_updates
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2j. opportunities
ALTER TABLE opportunities ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'opportunities' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON opportunities
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2k. income_sources
ALTER TABLE income_sources ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'income_sources' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON income_sources
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2l. income_logs
ALTER TABLE income_logs ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'income_logs' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON income_logs
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2m. projects
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'projects' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON projects
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2n. academic_subjects
ALTER TABLE academic_subjects ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'academic_subjects' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON academic_subjects
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2o. habits
ALTER TABLE habits ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'habits' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON habits
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2p. habit_logs
ALTER TABLE habit_logs ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'habit_logs' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON habit_logs
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2q. sleep_logs
ALTER TABLE sleep_logs ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'sleep_logs' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON sleep_logs
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2r. time_logs
ALTER TABLE time_logs ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'time_logs' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON time_logs
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2s. chat_messages
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'chat_messages' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON chat_messages
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2t. aria_memory
ALTER TABLE aria_memory ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'aria_memory' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON aria_memory
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2u. daily_briefings
ALTER TABLE daily_briefings ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'daily_briefings' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON daily_briefings
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2v. weekly_reviews
ALTER TABLE weekly_reviews ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'weekly_reviews' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON weekly_reviews
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2w. study_sessions
ALTER TABLE study_sessions ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'study_sessions' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON study_sessions
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2x. daily_logs
ALTER TABLE daily_logs ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'daily_logs' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON daily_logs
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2y. notifications
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'notifications' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON notifications
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 2z. token_usage
ALTER TABLE token_usage ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'token_usage' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON token_usage
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- =============================================================
-- 3. CHILD TABLES (no user_id column — inherit via parent)
-- These use EXISTS subquery to check parent table ownership.
-- =============================================================

-- 3a. subtasks — parent is tasks
ALTER TABLE subtasks ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'subtasks' AND policyname = 'subtasks_via_task') THEN
        CREATE POLICY "subtasks_via_task" ON subtasks
            FOR ALL USING (
                EXISTS (
                    SELECT 1 FROM tasks
                    WHERE tasks.id = subtasks.task_id
                      AND tasks.user_id = auth.uid()
                )
            )
            WITH CHECK (
                EXISTS (
                    SELECT 1 FROM tasks
                    WHERE tasks.id = subtasks.task_id
                      AND tasks.user_id = auth.uid()
                )
            );
    END IF;
END $$;

-- 3b. task_dependencies — parent is tasks (both FK sides)
ALTER TABLE task_dependencies ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'task_dependencies' AND policyname = 'task_dependencies_via_task') THEN
        CREATE POLICY "task_dependencies_via_task" ON task_dependencies
            FOR ALL USING (
                EXISTS (
                    SELECT 1 FROM tasks
                    WHERE tasks.id = task_dependencies.task_id
                      AND tasks.user_id = auth.uid()
                )
            )
            WITH CHECK (
                EXISTS (
                    SELECT 1 FROM tasks
                    WHERE tasks.id = task_dependencies.task_id
                      AND tasks.user_id = auth.uid()
                )
            );
    END IF;
END $$;

-- 3c. marks — parent is academic_subjects
ALTER TABLE marks ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'marks' AND policyname = 'marks_via_subject') THEN
        CREATE POLICY "marks_via_subject" ON marks
            FOR ALL USING (
                EXISTS (
                    SELECT 1 FROM academic_subjects
                    WHERE academic_subjects.id = marks.subject_id
                      AND academic_subjects.user_id = auth.uid()
                )
            )
            WITH CHECK (
                EXISTS (
                    SELECT 1 FROM academic_subjects
                    WHERE academic_subjects.id = marks.subject_id
                      AND academic_subjects.user_id = auth.uid()
                )
            );
    END IF;
END $$;

-- =============================================================
-- 4. AUDIT LOG (separate policy — access controlled)
-- =============================================================

ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- Users can see their own audit trail
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'audit_log' AND policyname = 'users_own_audit') THEN
        CREATE POLICY "users_own_audit" ON audit_log
            FOR SELECT USING (auth.uid() = user_id);
    END IF;
END $$;

-- Service role handles INSERT via trigger (SECURITY DEFINER)

COMMIT;
