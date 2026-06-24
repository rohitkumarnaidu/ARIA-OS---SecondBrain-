-- =============================================================
-- Migration 006: Skills Materialized Views — KPI Dashboards
-- Creates: 7 materialized views for analytics, performance,
--          and intelligence dashboards.
-- Dependent on: 001-005 (all prior migrations)
-- Refresh: via pg_cron or application scheduler
-- =============================================================

-- === 1. Extension Setup ===

CREATE EXTENSION IF NOT EXISTS pg_stat_statements WITH SCHEMA public;

-- === 2. mv_skill_user_proficiency — User Skill Dashboard ===

DROP MATERIALIZED VIEW IF EXISTS mv_skill_user_proficiency CASCADE;
CREATE MATERIALIZED VIEW mv_skill_user_proficiency AS
SELECT
    us.user_id,
    us.tenant_id,
    COUNT(DISTINCT us.skill_id) AS total_skills_tracked,
    COUNT(DISTINCT us.evidence_id) FILTER (WHERE us.proficiency_level >= 3) AS skills_at_or_above_intermediate,
    COUNT(DISTINCT us.evidence_id) FILTER (WHERE us.proficiency_level >= 4) AS skills_at_or_above_advanced,
    ROUND(AVG(us.proficiency_level)::NUMERIC, 2) AS avg_proficiency,
    MAX(us.proficiency_level) AS max_proficiency,
    MIN(us.proficiency_level) AS min_proficiency,
    SUM(us.hours_practiced) AS total_hours_practiced,
    SUM(us.hours_taught) AS total_hours_taught,
    COUNT(DISTINCT ue.evidence_id) AS total_evidence_pieces,
    COUNT(DISTINCT ut.target_id) AS total_targets_set,
    COUNT(DISTINCT ut.target_id) FILTER (WHERE ut.status = 'achieved') AS targets_achieved,
    CASE
        WHEN COUNT(DISTINCT ut.target_id) = 0 THEN 0
        ELSE ROUND(
            (COUNT(DISTINCT ut.target_id) FILTER (WHERE ut.status = 'achieved')::NUMERIC /
             COUNT(DISTINCT ut.target_id)::NUMERIC) * 100, 1
        )
    END AS target_achievement_rate_pct,
    MAX(us.last_practiced_at) AS last_practice_date,
    CURRENT_TIMESTAMP AS computed_at
FROM user_skills us
LEFT JOIN user_skill_evidence ue ON us.user_id = ue.user_id AND us.skill_id = ue.skill_id
LEFT JOIN user_skill_targets ut ON us.user_id = ut.user_id AND us.skill_id = ut.skill_id
GROUP BY us.user_id, us.tenant_id
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_proficiency_user ON mv_skill_user_proficiency(user_id, tenant_id);
COMMENT ON MATERIALIZED VIEW mv_skill_user_proficiency IS 'Aggregated user skill proficiency metrics for dashboard KPI cards';

-- === 3. mv_skill_market_intelligence — Market & Income Dashboard ===

DROP MATERIALIZED VIEW IF EXISTS mv_skill_market_intelligence CASCADE;
CREATE MATERIALIZED VIEW mv_skill_market_intelligence AS
SELECT
    s.skill_id,
    s.skill_name,
    sc.category_name,
    smd.median_salary,
    smd.demand_score,
    smd.supply_score,
    smd.market_saturation_pct,
    smd.growth_rate_pct,
    sid.median_hourly_rate,
    sid.freelance_avg_rate,
    sid.salary_range_low,
    sid.salary_range_high,
    scrt.certification_count,
    scrt.top_certification,
    smd.data_currency_date,
    CURRENT_TIMESTAMP AS computed_at,
    RANK() OVER (ORDER BY smd.demand_score DESC NULLS LAST) AS demand_rank,
    RANK() OVER (ORDER BY smd.growth_rate_pct DESC NULLS LAST) AS growth_rank,
    RANK() OVER (ORDER BY smd.median_salary DESC NULLS LAST) AS salary_rank
FROM skills s
JOIN skill_categories sc ON s.category_id = sc.category_id
LEFT JOIN skill_market_data smd ON s.skill_id = smd.skill_id
LEFT JOIN skill_income_data sid ON s.skill_id = sid.skill_id
LEFT JOIN LATERAL (
    SELECT
        COUNT(DISTINCT cert_id) AS certification_count,
        MAX(cert_name) AS top_certification
    FROM skill_certifications sc2
    WHERE sc2.skill_id = s.skill_id
) scrt ON true
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_market_skill ON mv_skill_market_intelligence(skill_id);
CREATE INDEX IF NOT EXISTS idx_mv_market_demand_rank ON mv_skill_market_intelligence(demand_rank);
CREATE INDEX IF NOT EXISTS idx_mv_market_salary_rank ON mv_skill_market_intelligence(salary_rank);
COMMENT ON MATERIALIZED VIEW mv_skill_market_intelligence IS 'Skill market intelligence with demand, salary, and growth rankings';

-- === 4. mv_skill_roadmap_progress — Roadmap Tracking Dashboard ===

DROP MATERIALIZED VIEW IF EXISTS mv_skill_roadmap_progress CASCADE;
CREATE MATERIALIZED VIEW mv_skill_roadmap_progress AS
SELECT
    r.roadmap_id,
    r.user_id,
    r.tenant_id,
    r.roadmap_name,
    r.skill_id,
    r.total_milestones,
    r.completed_milestones,
    CASE
        WHEN r.total_milestones = 0 THEN 0
        ELSE ROUND((r.completed_milestones::NUMERIC / r.total_milestones::NUMERIC) * 100, 1)
    END AS completion_pct,
    r.started_at,
    r.estimated_completion_at,
    r.completed_at,
    CASE
        WHEN r.completed_at IS NOT NULL THEN 'Complete'
        WHEN r.estimated_completion_at < CURRENT_DATE THEN 'Overdue'
        ELSE 'On Track'
    END AS status_label,
    r.priority_score,
    COUNT(DISTINCT ops.opportunity_id) AS linked_opportunities,
    CURRENT_TIMESTAMP AS computed_at
FROM skill_roadmaps r
LEFT JOIN skill_opportunities ops ON r.skill_id = ops.skill_id AND r.user_id = ops.user_id
GROUP BY r.roadmap_id, r.user_id, r.tenant_id, r.roadmap_name, r.skill_id,
         r.total_milestones, r.completed_milestones, r.started_at,
         r.estimated_completion_at, r.completed_at, r.priority_score
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_roadmap_id ON mv_skill_roadmap_progress(roadmap_id);
CREATE INDEX IF NOT EXISTS idx_mv_roadmap_user ON mv_skill_roadmap_progress(user_id, tenant_id);
CREATE INDEX IF NOT EXISTS idx_mv_roadmap_status ON mv_skill_roadmap_progress(status_label);
COMMENT ON MATERIALIZED VIEW mv_skill_roadmap_progress IS 'Skill roadmap completion progress with status labels';

-- === 5. mv_skill_learning_velocity — Learning Rate Analytics ===

DROP MATERIALIZED VIEW IF EXISTS mv_skill_learning_velocity CASCADE;
CREATE MATERIALIZED VIEW mv_skill_learning_velocity AS
SELECT
    ush.user_id,
    ush.tenant_id,
    ush.skill_id,
    COUNT(*) AS total_assessment_events,
    MIN(ush.proficiency_before) AS min_proficiency,
    MAX(ush.proficiency_after) AS max_proficiency,
    MAX(ush.proficiency_after) - MIN(ush.proficiency_before) AS total_proficiency_gain,
    ROUND(
        EXTRACT(EPOCH FROM (MAX(ush.created_at) - MIN(ush.created_at))) / 86400.0, 1
    ) AS days_tracked,
    CASE
        WHEN EXTRACT(EPOCH FROM (MAX(ush.created_at) - MIN(ush.created_at))) = 0 THEN 0
        ELSE ROUND(
            (MAX(ush.proficiency_after) - MIN(ush.proficiency_before))::NUMERIC /
            NULLIF(EXTRACT(EPOCH FROM (MAX(ush.created_at) - MIN(ush.created_at))) / 86400.0, 0) * 30, 3
        )
    END AS proficiency_gain_per_month,
    ROUND(AVG(ush.hours_since_last)::NUMERIC, 1) AS avg_hours_between_assessments,
    CURRENT_TIMESTAMP AS computed_at
FROM skill_user_skill_history ush
GROUP BY ush.user_id, ush.tenant_id, ush.skill_id
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_velocity_user_skill ON mv_skill_learning_velocity(user_id, skill_id, tenant_id);
COMMENT ON MATERIALIZED VIEW mv_skill_learning_velocity IS 'Learning velocity — proficiency gain rate per skill per user';

-- === 6. mv_skill_taxonomy_health — Taxonomy Completeness ===

DROP MATERIALIZED VIEW IF EXISTS mv_skill_taxonomy_health CASCADE;
CREATE MATERIALIZED VIEW mv_skill_taxonomy_health AS
SELECT
    sc.category_id,
    sc.category_name,
    sc.domain_name,
    COUNT(DISTINCT s.skill_id) AS skill_count,
    COUNT(DISTINCT sr.relationship_id) AS relationship_count,
    COUNT(DISTINCT t.tag_id) AS tag_count,
    COUNT(DISTINCT smd.skill_id) FILTER (WHERE smd.skill_id IS NOT NULL) AS skills_with_market_data,
    COUNT(DISTINCT sid.skill_id) FILTER (WHERE sid.skill_id IS NOT NULL) AS skills_with_income_data,
    COUNT(DISTINCT scrt.cert_id) FILTER (WHERE scrt.cert_id IS NOT NULL) AS skills_with_certifications,
    CASE
        WHEN COUNT(DISTINCT s.skill_id) = 0 THEN 0
        ELSE ROUND(
            (COUNT(DISTINCT smd.skill_id)::NUMERIC / COUNT(DISTINCT s.skill_id)::NUMERIC) * 100, 1
        )
    END AS market_data_coverage_pct,
    CURRENT_TIMESTAMP AS computed_at
FROM skill_categories sc
LEFT JOIN skills s ON sc.category_id = s.category_id
LEFT JOIN skill_relationships sr ON s.skill_id = sr.parent_skill_id OR s.skill_id = sr.child_skill_id
LEFT JOIN tags t ON t.tag_name IS NOT NULL
LEFT JOIN skill_market_data smd ON s.skill_id = smd.skill_id
LEFT JOIN skill_income_data sid ON s.skill_id = sid.skill_id
LEFT JOIN skill_certifications scrt ON s.skill_id = scrt.skill_id
GROUP BY sc.category_id, sc.category_name, sc.domain_name
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_taxonomy_category ON mv_skill_taxonomy_health(category_id);
COMMENT ON MATERIALIZED VIEW mv_skill_taxonomy_health IS 'Taxonomy health — coverage metrics per domain and category';

-- === 7. mv_skill_ai_recommendation_effectiveness — AI Performance ===

DROP MATERIALIZED VIEW IF EXISTS mv_skill_ai_recommendation_effectiveness CASCADE;
CREATE MATERIALIZED VIEW mv_skill_ai_recommendation_effectiveness AS
SELECT
    user_id,
    tenant_id,
    COUNT(*) AS total_recommendations,
    COUNT(*) FILTER (WHERE status = 'accepted') AS accepted_count,
    COUNT(*) FILTER (WHERE status = 'dismissed') AS dismissed_count,
    COUNT(*) FILTER (WHERE status = 'pending') AS pending_count,
    CASE
        WHEN COUNT(*) = 0 THEN 0
        ELSE ROUND(
            (COUNT(*) FILTER (WHERE status = 'accepted')::NUMERIC / COUNT(*)::NUMERIC) * 100, 1
        )
    END AS acceptance_rate_pct,
    AVG(confidence_score) FILTER (WHERE status = 'accepted') AS avg_confidence_accepted,
    AVG(confidence_score) FILTER (WHERE status = 'dismissed') AS avg_confidence_dismissed,
    CURRENT_TIMESTAMP AS computed_at
FROM skill_ai_recommendations
GROUP BY user_id, tenant_id
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_ai_effectiveness_user ON mv_skill_ai_recommendation_effectiveness(user_id, tenant_id);
COMMENT ON MATERIALIZED VIEW mv_skill_ai_recommendation_effectiveness IS 'AI recommendation acceptance rates and confidence analysis';

-- === 8. mv_skill_activity_heatmap — Temporal Activity Patterns ===

DROP MATERIALIZED VIEW IF EXISTS mv_skill_activity_heatmap CASCADE;
CREATE MATERIALIZED VIEW mv_skill_activity_heatmap AS
SELECT
    user_id,
    tenant_id,
    DATE_TRUNC('day', created_at)::DATE AS activity_date,
    EXTRACT(DOW FROM created_at)::INTEGER AS day_of_week,
    EXTRACT(HOUR FROM created_at)::INTEGER AS hour_of_day,
    action,
    COUNT(*) AS event_count,
    CURRENT_TIMESTAMP AS computed_at
FROM skill_user_activity_log
GROUP BY user_id, tenant_id, DATE_TRUNC('day', created_at)::DATE,
         EXTRACT(DOW FROM created_at)::INTEGER,
         EXTRACT(HOUR FROM created_at)::INTEGER,
         action
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_activity_user_date ON mv_skill_activity_heatmap(user_id, tenant_id, activity_date, hour_of_day, action);
CREATE INDEX IF NOT EXISTS idx_mv_activity_day ON mv_skill_activity_heatmap(day_of_week);
COMMENT ON MATERIALIZED VIEW mv_skill_activity_heatmap IS 'Temporal activity heatmap for user engagement patterns';

-- === 9. pg_cron Refresh Jobs ===

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_cron') THEN
        -- User proficiency: refresh every 5 minutes during peak hours
        PERFORM cron.schedule('skill-proficiency-refresh', '*/5 6-23 * * *',
            'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_user_proficiency');

        -- Market intelligence: refresh twice daily
        PERFORM cron.schedule('skill-market-refresh', '0 6,18 * * *',
            'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_market_intelligence');

        -- Roadmap progress: refresh every 15 minutes
        PERFORM cron.schedule('skill-roadmap-refresh', '*/15 * * * *',
            'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_roadmap_progress');

        -- Learning velocity: refresh hourly
        PERFORM cron.schedule('skill-velocity-refresh', '0 * * * *',
            'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_learning_velocity');

        -- Taxonomy health: refresh daily at midnight
        PERFORM cron.schedule('skill-taxonomy-health-refresh', '0 0 * * *',
            'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_taxonomy_health');

        -- AI effectiveness: refresh every 30 minutes
        PERFORM cron.schedule('skill-ai-effective-refresh', '*/30 * * * *',
            'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_ai_recommendation_effectiveness');

        -- Activity heatmap: refresh hourly
        PERFORM cron.schedule('skill-activity-heatmap-refresh', '0 * * * *',
            'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_activity_heatmap');
    END IF;
END $$;

-- === 10. Non-pg_cron Fallback: Manual Refresh Helper ===

CREATE OR REPLACE FUNCTION skill_refresh_all_materialized_views()
RETURNS JSONB AS $$
DECLARE
    results JSONB := '[]'::JSONB;
    start_ts TIMESTAMPTZ;
    end_ts TIMESTAMPTZ;
BEGIN
    start_ts := clock_timestamp();
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_user_proficiency;
    results := results || '{"view":"mv_skill_user_proficiency","status":"ok"}'::JSONB;

    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_market_intelligence;
    results := results || '{"view":"mv_skill_market_intelligence","status":"ok"}'::JSONB;

    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_roadmap_progress;
    results := results || '{"view":"mv_skill_roadmap_progress","status":"ok"}'::JSONB;

    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_learning_velocity;
    results := results || '{"view":"mv_skill_learning_velocity","status":"ok"}'::JSONB;

    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_taxonomy_health;
    results := results || '{"view":"mv_skill_taxonomy_health","status":"ok"}'::JSONB;

    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_ai_recommendation_effectiveness;
    results := results || '{"view":"mv_skill_ai_recommendation_effectiveness","status":"ok"}'::JSONB;

    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_activity_heatmap;
    results := results || '{"view":"mv_skill_activity_heatmap","status":"ok"}'::JSONB;

    end_ts := clock_timestamp();
    results := results || jsonb_build_object('total_views', 7, 'duration_ms', ROUND(EXTRACT(EPOCH FROM (end_ts - start_ts))::NUMERIC * 1000, 0));
    RETURN results;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION skill_refresh_all_materialized_views IS 'Manual refresh all 7 materialized views, returns status JSON';
