-- =============================================================
-- Migration 007: Skills Partition Management & Cron Jobs
-- Creates: pg_partman partition sets, pg_cron job registrations,
--          monthly partition templates, data retention policies,
--          archival helper functions, stale/emerging flag updates
-- Requires: pg_partman, pg_cron extensions
-- Dependent on: 001-006 (all prior migrations)
-- =============================================================

BEGIN;

-- =============================================================
-- 1. pg_partman Partition Management
-- =============================================================

CREATE EXTENSION IF NOT EXISTS partman WITH SCHEMA public;
CREATE SCHEMA IF NOT EXISTS partman;

-- Register partitioned tables with pg_partman for automated maintenance
DO $$
DECLARE
    tbl TEXT;
BEGIN
    FOREACH tbl IN ARRAY ARRAY[
        'user_skill_evidence',    -- monthly by collected_at
        'user_skill_versions',    -- monthly by created_at
        'skill_user_activity_log', -- monthly by created_at
        'skill_audit_log',        -- monthly by created_at
        'skill_events',           -- monthly by created_at
        'skill_webhook_queue',    -- daily by created_at
        'skill_analytics_snapshots', -- quarterly by snapshot_date
        'skill_market_history'    -- quarterly by created_at
    ] LOOP
        EXECUTE format('SELECT partman.create_parent(
            p_parent_table := ''public.%I'',
            p_control := CASE WHEN %L = ''skill_analytics_snapshots'' THEN ''snapshot_date''
                              WHEN %L = ''skill_webhook_queue'' THEN ''created_at''
                              ELSE ''created_at'' END,
            p_type := ''native'',
            p_interval := CASE WHEN %L = ''skill_webhook_queue'' THEN ''1 day''
                               WHEN %L IN (''skill_analytics_snapshots'', ''skill_market_history'') THEN ''3 months''
                               ELSE ''1 month'' END,
            p_premake := 3,
            p_start_partition := ''2026-01-01''
        )', tbl, tbl, tbl, tbl, tbl);
    END LOOP;
END $$;

-- =============================================================
-- 2. pg_cron Job Registrations
-- =============================================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_cron') THEN

        -- 2.1 Materialized View Refreshes

        PERFORM cron.schedule('skill-proficiency-refresh', '*/5 6-23 * * *',
            $$REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_user_proficiency$$);

        PERFORM cron.schedule('skill-market-refresh', '0 6,18 * * *',
            $$REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_market_intelligence$$);

        PERFORM cron.schedule('skill-velocity-refresh', '0 * * * *',
            $$REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_learning_velocity$$);

        PERFORM cron.schedule('skill-taxonomy-health-refresh', '0 0 * * *',
            $$REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_taxonomy_health$$);

        PERFORM cron.schedule('skill-ai-effective-refresh', '*/30 * * * *',
            $$REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_ai_effectiveness$$);

        PERFORM cron.schedule('skill-activity-heatmap-refresh', '0 * * * *',
            $$REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_activity_heatmap$$);

        PERFORM cron.schedule('skill-roadmap-refresh', '*/15 * * * *',
            $$REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_roadmap_progress$$);

        -- 2.2 Data Maintenance Jobs

        PERFORM cron.schedule('skill-update-stale-flags', '0 2 * * *',
            $$UPDATE user_skills
              SET is_stale = true, updated_at = EXTRACT(EPOCH FROM NOW()) * 1000
              WHERE updated_at < EXTRACT(EPOCH FROM NOW() - INTERVAL '90 days') * 1000
                AND is_stale = false AND state NOT IN ('archived', 'deprecated')$$);

        PERFORM cron.schedule('skill-update-velocity-90d', '0 3 * * *',
            $$UPDATE user_skills us
              SET level_change_90d = COALESCE((
                  SELECT ush_new.new_level - ush_old.previous_level
                  FROM skill_user_skill_history ush_new
                  JOIN skill_user_skill_history ush_old
                    ON ush_old.user_id = ush_new.user_id
                   AND ush_old.skill_id = ush_new.skill_id
                   AND ush_old.created_at < ush_new.created_at
                  WHERE ush_new.user_id = us.user_id
                    AND ush_new.skill_id = us.skill_id
                    AND ush_new.created_at > EXTRACT(EPOCH FROM NOW() - INTERVAL '90 days') * 1000
                  ORDER BY ush_new.created_at ASC
                  LIMIT 1
              ), 0)
              WHERE us.state NOT IN ('archived', 'deprecated')$$);

        PERFORM cron.schedule('skill-purge-expired-recommendations', '0 4 * * *',
            $$DELETE FROM skill_ai_recommendations
              WHERE expires_at IS NOT NULL
                AND expires_at < EXTRACT(EPOCH FROM NOW()) * 1000$$);

        PERFORM cron.schedule('skill-purge-stale-forecasts', '0 5 * * 0',
            $$DELETE FROM skill_forecasts
              WHERE created_at < EXTRACT(EPOCH FROM NOW() - INTERVAL '6 months') * 1000$$);

        PERFORM cron.schedule('skill-vacuum-main', '0 6 * * 0',
            $$VACUUM ANALYZE user_skills, user_skill_evidence, skill_market_data,
              skill_user_skill_history, skill_events, skill_analytics_snapshots$$);

        -- 2.3 Partition Maintenance

        PERFORM cron.schedule('skill-partman-maintenance', '0 0 * * *',
            $$SELECT partman.run_maintenance()$$);

        PERFORM cron.schedule('skill-detach-old-partitions', '0 1 1 * *',
            $$SELECT partman.undo_partition('public.skill_audit_log', p_batch_count := 1, p_keep_table := true)
              WHERE EXISTS (
                  SELECT 1 FROM pg_class WHERE relname LIKE 'skill_audit_log_%'
                  AND relid < (SELECT (pg_stat_file('/proc/self/fd/1')).modification)
              )$$);

        -- 2.4 Event Outbox Processing

        PERFORM cron.schedule('skill-process-outbox', '* * * * *',
            $$UPDATE skill_event_outbox
              SET status = 'processing', scheduled_at = EXTRACT(EPOCH FROM NOW()) * 1000
              WHERE status = 'pending'
                AND (scheduled_at IS NULL OR scheduled_at <= EXTRACT(EPOCH FROM NOW()) * 1000)
              LIMIT 100$$);

        -- 2.5 Webhook Delivery Attempt

        PERFORM cron.schedule('skill-process-webhooks', '*/5 * * * *',
            $$UPDATE skill_webhook_queue
              SET status = 'delivering', retry_count = retry_count + 1,
                  scheduled_at = EXTRACT(EPOCH FROM NOW()) * 1000
              WHERE status IN ('pending', 'failed')
                AND retry_count < max_retries
                AND (scheduled_at IS NULL OR scheduled_at <= EXTRACT(EPOCH FROM NOW()) * 1000)
              LIMIT 50$$);

    END IF;
END $$;

-- =============================================================
-- 3. Retention Policy Functions
-- =============================================================

CREATE OR REPLACE FUNCTION skill_archive_old_partitions()
RETURNS TABLE(partition_name TEXT, rows_archived BIGINT) AS $$
DECLARE
    rec RECORD;
    archive_ts BIGINT;
    archive_name TEXT;
    row_count BIGINT;
BEGIN
    -- Archive audit log partitions older than 12 months
    archive_ts := EXTRACT(EPOCH FROM NOW() - INTERVAL '12 months') * 1000;
    FOR rec IN (
        SELECT relname, nspname
        FROM pg_class c
        JOIN pg_namespace n ON c.relnamespace = n.oid
        WHERE c.relname LIKE 'skill_audit_log_%'
        AND c.relispartition
        ORDER BY c.relname
    ) LOOP
        EXECUTE format('SELECT COUNT(*) FROM %I.%I WHERE created_at < %s',
            rec.nspname, rec.relname, archive_ts) INTO row_count;
        IF row_count > 0 THEN
            archive_name := rec.relname || '_archived';
            partition_name := rec.relname;
            rows_archived := row_count;
            -- Detach partition
            EXECUTE format('ALTER TABLE %I.%I DETACH PARTITION %I.%I',
                rec.nspname, 'skill_audit_log', rec.nspname, rec.relname);
            -- Mark as archived
            EXECUTE format('COMMENT ON TABLE %I.%I IS ''Archived %s rows, detached at %s''',
                rec.nspname, rec.relname,
                row_count, NOW());
            RETURN NEXT;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================================
-- 4. Stale/Emerging Detection Function
-- =============================================================

CREATE OR REPLACE FUNCTION skill_detect_emerging_skills()
RETURNS TABLE(user_skill_id UUID, user_id UUID, skill_id UUID, reason TEXT) AS $$
BEGIN
    RETURN QUERY
    UPDATE user_skills us
    SET is_emerging = true,
        updated_at = EXTRACT(EPOCH FROM NOW()) * 1000
    FROM (
        SELECT us2.user_skill_id, us2.user_id, us2.skill_id
        FROM user_skills us2
        WHERE us2.level_change_90d > 1
          AND us2.is_emerging = false
          AND us2.state NOT IN ('archived', 'deprecated')
    ) emerging
    WHERE us.user_skill_id = emerging.user_skill_id
    RETURNING us.user_skill_id, us.user_id, us.skill_id,
              'level_change_90d > 1'::TEXT AS reason;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================================
-- 5. Event Outbox Processing Function
-- =============================================================

CREATE OR REPLACE FUNCTION skill_process_event_outbox(batch_size INT DEFAULT 100)
RETURNS TABLE(processed INT, failed INT) AS $$
DECLARE
    rec RECORD;
    p_processed INT := 0;
    p_failed INT := 0;
BEGIN
    FOR rec IN (
        SELECT * FROM skill_event_outbox
        WHERE status = 'pending'
          AND (scheduled_at IS NULL OR scheduled_at <= EXTRACT(EPOCH FROM NOW()) * 1000)
          AND locked_until IS NULL
        ORDER BY created_at ASC
        LIMIT batch_size
        FOR UPDATE SKIP LOCKED
    ) LOOP
        BEGIN
            -- Insert into skill_events
            INSERT INTO skill_events (
                event_type, event_version, aggregate_type, aggregate_id,
                user_id, data, metadata, correlation_id, created_at
            ) VALUES (
                rec.event_type, '1.0', rec.aggregate_type, rec.aggregate_id,
                NULL, rec.payload, rec.headers, NULL, rec.created_at
            );

            -- Mark as delivered
            UPDATE skill_event_outbox
            SET status = 'delivered',
                processed_at = EXTRACT(EPOCH FROM NOW()) * 1000
            WHERE outbox_id = rec.outbox_id;

            p_processed := p_processed + 1;

        EXCEPTION WHEN OTHERS THEN
            UPDATE skill_event_outbox
            SET status = CASE WHEN retry_count >= max_retries THEN 'dead_letter' ELSE 'failed' END,
                retry_count = retry_count + 1,
                last_error = SQLERRM,
                scheduled_at = EXTRACT(EPOCH FROM NOW()) * 1000 + (retry_count * 2000)
            WHERE outbox_id = rec.outbox_id;
            p_failed := p_failed + 1;
        END;
    END LOOP;

    RETURN QUERY SELECT p_processed, p_failed;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================================
-- 6. Analytics Snapshot Builder Function
-- =============================================================

CREATE OR REPLACE FUNCTION skill_build_analytics_snapshot(p_user_id UUID DEFAULT NULL)
RETURNS TABLE(user_id UUID, snapshot_date DATE, skill_count INT) AS $$
BEGIN
    RETURN QUERY
    INSERT INTO skill_analytics_snapshots (
        user_id, snapshot_date, avg_skill_level, skill_count,
        readiness_score, learning_velocity, diversification_score,
        income_per_hour, market_alignment, emerging_coverage,
        milestone_completion, evidence_ratio
    )
    SELECT
        us.user_id,
        CURRENT_DATE,
        ROUND(AVG(us.level)::NUMERIC, 2),
        COUNT(DISTINCT us.skill_id)::INT,
        ROUND(AVG(us.confidence_score)::NUMERIC * 100, 2),
        ROUND(AVG(us.level_change_90d)::NUMERIC, 3),
        ROUND(COUNT(DISTINCT s.category_id)::NUMERIC / NULLIF(COUNT(DISTINCT s.skill_id), 0) * 100, 2),
        0, -- income_per_hour placeholder
        ROUND(AVG(smd.skill_health)::NUMERIC, 2),
        COUNT(DISTINCT us.skill_id) FILTER (WHERE us.is_emerging)::INT,
        ROUND((COUNT(*) FILTER (WHERE ut.status = 'achieved')::NUMERIC
            / NULLIF(COUNT(DISTINCT ut.target_id), 0)) * 100, 2),
        ROUND((COUNT(ue.evidence_id)::NUMERIC / NULLIF(COUNT(DISTINCT us.skill_id), 0))::NUMERIC, 2)
    FROM user_skills us
    LEFT JOIN skills s ON us.skill_id = s.skill_id
    LEFT JOIN skill_market_data smd ON us.skill_id = smd.skill_id
    LEFT JOIN user_skill_targets ut ON us.user_skill_id = ut.user_skill_id
    LEFT JOIN user_skill_evidence ue ON us.user_skill_id = ue.user_skill_id
    WHERE (p_user_id IS NULL OR us.user_id = p_user_id)
    GROUP BY us.user_id
    ON CONFLICT (user_id, snapshot_date)
    DO UPDATE SET
        avg_skill_level = EXCLUDED.avg_skill_level,
        skill_count = EXCLUDED.skill_count,
        readiness_score = EXCLUDED.readiness_score,
        learning_velocity = EXCLUDED.learning_velocity,
        diversification_score = EXCLUDED.diversification_score,
        market_alignment = EXCLUDED.market_alignment,
        emerging_coverage = EXCLUDED.emerging_coverage,
        milestone_completion = EXCLUDED.milestone_completion,
        evidence_ratio = EXCLUDED.evidence_ratio
    RETURNING user_id, snapshot_date, skill_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMIT;
