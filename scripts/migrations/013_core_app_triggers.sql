-- =============================================================
-- Migration 013: Core Application — Triggers & Functions
-- Creates: trigger_set_updated_at function + triggers on 11
--          tables with updated_at column. Optional audit log
--          trigger on sensitive tables (tasks, goals).
-- =============================================================

BEGIN;

-- =============================================================
-- 1. UPDATED_AT TRIGGER FUNCTION
-- Auto-sets updated_at = NOW() on every row UPDATE
-- =============================================================

CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION trigger_set_updated_at() IS 'Automatically set updated_at timestamp on row update';

-- =============================================================
-- 2. APPLY TRIGGER TO TABLES WITH updated_at COLUMN
-- =============================================================

-- 2a. users_profile
DROP TRIGGER IF EXISTS set_updated_at ON users_profile;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON users_profile
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_updated_at();

-- 2b. tasks
DROP TRIGGER IF EXISTS set_updated_at ON tasks;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_updated_at();

-- 2c. courses
DROP TRIGGER IF EXISTS set_updated_at ON courses;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON courses
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_updated_at();

-- 2d. resources
DROP TRIGGER IF EXISTS set_updated_at ON resources;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON resources
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_updated_at();

-- 2e. ideas
DROP TRIGGER IF EXISTS set_updated_at ON ideas;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON ideas
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_updated_at();

-- 2f. goals
DROP TRIGGER IF EXISTS set_updated_at ON goals;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON goals
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_updated_at();

-- 2g. roadmaps
DROP TRIGGER IF EXISTS set_updated_at ON roadmaps;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON roadmaps
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_updated_at();

-- 2h. income_sources
DROP TRIGGER IF EXISTS set_updated_at ON income_sources;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON income_sources
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_updated_at();

-- 2i. projects
DROP TRIGGER IF EXISTS set_updated_at ON projects;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_updated_at();

-- 2j. academic_subjects
DROP TRIGGER IF EXISTS set_updated_at ON academic_subjects;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON academic_subjects
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_updated_at();

-- 2k. habits
DROP TRIGGER IF EXISTS set_updated_at ON habits;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON habits
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_updated_at();

-- =============================================================
-- 3. AUDIT LOG TRIGGER (optional — enable per sensitivity)
-- Logs all INSERT/UPDATE/DELETE on tracked tables to audit_log
-- Uses SECURITY DEFINER so trigger can write audit regardless
-- of RLS on audit_log table.
-- =============================================================

CREATE OR REPLACE FUNCTION trigger_audit_log()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (
        table_name,
        operation,
        record_id,
        old_data,
        new_data,
        changed_by,
        user_id,
        changed_at
    ) VALUES (
        TG_TABLE_NAME,
        TG_OP,
        COALESCE(NEW.id, OLD.id),
        CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW) ELSE NULL END,
        auth.uid(),
        COALESCE(NEW.user_id, OLD.user_id),
        NOW()
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION trigger_audit_log() IS 'Logs all mutations to audit_log table with before/after snapshots';

-- Apply audit logging to sensitive tables (tasks + goals as baseline)
DROP TRIGGER IF EXISTS audit_log_changes ON tasks;
CREATE TRIGGER audit_log_changes
    AFTER INSERT OR UPDATE OR DELETE ON tasks
    FOR EACH ROW EXECUTE FUNCTION trigger_audit_log();

DROP TRIGGER IF EXISTS audit_log_changes ON goals;
CREATE TRIGGER audit_log_changes
    AFTER INSERT OR UPDATE OR DELETE ON goals
    FOR EACH ROW EXECUTE FUNCTION trigger_audit_log();

-- =============================================================
-- 4. READ-ONLY (IMMUTABLE) TABLE VALIDATION
-- These tables do NOT have updated_at triggers by design:
-- subtasks, task_dependencies, youtube_saves, roadmap_updates,
-- income_logs, habit_logs, sleep_logs, time_logs, chat_messages,
-- aria_memory, daily_briefings, weekly_reviews, study_sessions,
-- daily_logs, marks, notifications, token_usage, audit_log
-- Rationale: Append-only logs or status-change-only tables
-- =============================================================

COMMIT;
