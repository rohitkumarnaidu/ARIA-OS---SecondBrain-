-- =============================================================
-- Migration 006: Skills Materialized Views — KPI Dashboards
-- Creates: 7 materialized views for analytics, performance,
--          and intelligence dashboards.
-- Dependent on: 001-005 (all prior migrations)
-- Refresh: via pg_cron or application scheduler
-- All column references verified against actual table schemas.
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
    COUNT(DISTINCT us.skill_id) FILTER (WHERE us.level >= 3) AS skills_intermediate_plus,
    COUNT(DISTINCT us.skill_id) FILTER (WHERE us.level >= 4) AS skills_advanced_plus,
    ROUND(AVG(us.level)::NUMERIC, 2) AS avg_level,
    MAX(us.level) AS max_level,
    MIN(us.level) AS min_level,
    ROUND(AVG(us.confidence_score)::NUMERIC, 3) AS avg_confidence,
    ROUND(AVG(us.evidence_score)::NUMERIC, 3) AS avg_evidence,
    ROUND(AVG(us.level_change_90d)::NUMERIC, 3) AS avg_velocity_90d,
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
    COUNT(DISTINCT ua.assessment_id) AS total_assessments,
    MAX(us.last_activity_at) AS last_activity,
    CURRENT_TIMESTAMP AS computed_at
FROM user_skills us
LEFT JOIN user_skill_evidence ue ON us.user_id = ue.user_id AND us.skill_id = ue.skill_id
LEFT JOIN user_skill_targets ut ON us.user_id = ut.user_id AND us.skill_id = ut.skill_id
LEFT JOIN user_skill_assessments ua ON us.user_id = ua.user_id AND us.skill_id = ua.skill_id
GROUP BY us.user_id, us.tenant_id
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_proficiency_user ON mv_skill_user_proficiency(user_id, tenant_id);
COMMENT ON MATERIALIZED VIEW mv_skill_user_proficiency IS 'Aggregated user skill proficiency metrics for dashboard KPI cards';

-- === 3. mv_skill_market_intelligence — Market & Income Dashboard ===

DROP MATERIALIZED VIEW IF EXISTS mv_skill_market_intelligence CASCADE;
CREATE MATERIALIZED VIEW mv_skill_market_intelligence AS
SELECT
    s.skill_id,
    s.name AS skill_name,
    sc.name AS category_name,
    smd.demand_score,
    smd.growth_score,
    smd.salary_median,
    smd.salary_p10, smd.salary_p25, smd.salary_p75, smd.salary_p90,
    smd.competition_score,
    smd.future_relevance,
    smd.skill_health,
    smd.job_postings_count,
    smd.data_freshness,
    sid.p50 AS median_income,
    sid.currency,
    scrt.certification_count,
    RANK() OVER (ORDER BY smd.demand_score DESC NULLS LAST) AS demand_rank,
    RANK() OVER (ORDER BY smd.growth_score DESC NULLS LAST) AS growth_rank,
    RANK() OVER (ORDER BY smd.salary_median DESC NULLS LAST) AS salary_rank,
    CURRENT_TIMESTAMP AS computed_at
FROM skills s
JOIN skill_categories sc ON s.category_id = sc.category_id
LEFT JOIN skill_market_data smd ON s.skill_id = smd.skill_id
LEFT JOIN skill_income_data sid ON s.skill_id = sid.skill_id AND sid.source = 'employment' AND sid.level = 3
LEFT JOIN LATERAL (
    SELECT COUNT(*) AS certification_count
    FROM skill_certifications sc2
    WHERE sc2.skill_id = s.skill_id
) scrt ON true
WHERE s.is_deprecated = false
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_market_skill ON mv_skill_market_intelligence(skill_id);
CREATE INDEX IF NOT EXISTS idx_mv_market_demand_rank ON mv_skill_market_intelligence(demand_rank);
CREATE INDEX IF NOT EXISTS idx_mv_market_salary_rank ON mv_skill_market_intelligence(salary_rank);
COMMENT ON MATERIALIZED VIEW mv_skill_market_intelligence IS 'Skill market intelligence with demand, salary, and growth rankings';

-- === 4. mv_skill_roadmap_progress — Roadmap Tracking Dashboard ===

DROP MATERIALIZED VIEW IF EXISTS mv_skill_roadmap_progress CASCADE;
CREATE MATERIALIZED VIEW mv_skill_roadmap_progress AS
SELECT
    sr.roadmap_id,
    rd.name AS roadmap_name,
    rd.difficulty,
    rd.estimated_duration,
    sr.skill_id,
    s.name AS skill_name,
    sr.phase,
    sr.sort_order,
    sr.target_level,
    sr.estimated_hours,
    sr.created_at
FROM skill_roadmaps sr
JOIN skill_roadmap_definitions rd ON sr.roadmap_id = rd.roadmap_id
JOIN skills s ON sr.skill_id = s.skill_id
ORDER BY sr.roadmap_id, sr.sort_order
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_roadmap_entry ON mv_skill_roadmap_progress(roadmap_id, skill_id);
CREATE INDEX IF NOT EXISTS idx_mv_roadmap_phase ON mv_skill_roadmap_progress(phase);
COMMENT ON MATERIALIZED VIEW mv_skill_roadmap_progress IS 'Skill roadmap entries with phase, order, and target level';

-- === 5. mv_skill_learning_velocity — Learning Rate Analytics ===

DROP MATERIALIZED VIEW IF EXISTS mv_skill_learning_velocity CASCADE;
CREATE MATERIALIZED VIEW mv_skill_learning_velocity AS
SELECT
    ush.user_id,
    ush.tenant_id,
    ush.skill_id,
    COUNT(*) AS total_change_events,
    MIN(ush.proficiency_before) AS min_proficiency,
    MAX(ush.proficiency_after) AS max_proficiency,
    COALESCE(MAX(ush.proficiency_after) - MIN(ush.proficiency_before), 0) AS total_proficiency_gain,
    ROUND(AVG(ush.hours_since_last)::NUMERIC, 1) AS avg_hours_between_events,
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
    sc.name AS category_name,
    sc.slug AS category_slug,
    COUNT(DISTINCT s.skill_id) AS skill_count,
    COUNT(DISTINCT sr.relationship_id) AS relationship_count,
    COUNT(DISTINCT st.tag_id) AS tag_count,
    COUNT(DISTINCT smd.skill_id) FILTER (WHERE smd.skill_id IS NOT NULL) AS skills_with_market_data,
    COUNT(DISTINCT sid.skill_id) FILTER (WHERE sid.skill_id IS NOT NULL) AS skills_with_income_data,
    COUNT(DISTINCT scrt.skill_id) AS skills_with_certifications,
    CASE
        WHEN COUNT(DISTINCT s.skill_id) = 0 THEN 0
        ELSE ROUND(
            (COUNT(DISTINCT smd.skill_id)::NUMERIC / NULLIF(COUNT(DISTINCT s.skill_id), 0)::NUMERIC) * 100, 1
        )
    END AS market_data_coverage_pct,
    CURRENT_TIMESTAMP AS computed_at
FROM skill_categories sc
LEFT JOIN skills s ON sc.category_id = s.category_id AND s.is_deprecated = false
LEFT JOIN skill_relationships sr ON s.skill_id = sr.from_skill_id OR s.skill_id = sr.to_skill_id
LEFT JOIN skill_tags st ON s.skill_id = st.skill_id
LEFT JOIN skill_market_data smd ON s.skill_id = smd.skill_id
LEFT JOIN skill_income_data sid ON s.skill_id = sid.skill_id
LEFT JOIN skill_certifications scrt ON s.skill_id = scrt.skill_id
GROUP BY sc.category_id, sc.name, sc.slug
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
    COUNT(*) FILTER (WHERE accepted = true) AS accepted_count,
    COUNT(*) FILTER (WHERE accepted = false) AS dismissed_count,
    COUNT(*) FILTER (WHERE accepted IS NULL) AS pending_count,
    CASE
        WHEN COUNT(*) = 0 THEN 0
        ELSE ROUND(
            (COUNT(*) FILTER (WHERE accepted = true)::NUMERIC / COUNT(*)::NUMERIC) * 100, 1
        )
    END AS acceptance_rate_pct,
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
    DATE_TRUNC('day', TO_TIMESTAMP(created_at / 1000))::DATE AS activity_date,
    EXTRACT(DOW FROM TO_TIMESTAMP(created_at / 1000))::INT AS day_of_week,
    EXTRACT(HOUR FROM TO_TIMESTAMP(created_at / 1000))::INT AS hour_of_day,
    activity_type,
    COUNT(*) AS event_count,
    CURRENT_TIMESTAMP AS computed_at
FROM skill_user_activity_log
GROUP BY user_id, tenant_id, activity_date, day_of_week, hour_of_day, activity_type
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_activity_user_date ON mv_skill_activity_heatmap(user_id, tenant_id, activity_date, hour_of_day, activity_type);
CREATE INDEX IF NOT EXISTS idx_mv_activity_day ON mv_skill_activity_heatmap(day_of_week);
COMMENT ON MATERIALIZED VIEW mv_skill_activity_heatmap IS 'Temporal activity heatmap for user engagement patterns';

-- === 9. pg_cron Refresh Jobs ===

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_cron') THEN
        PERFORM cron.schedule('skill-proficiency-refresh', '*/5 6-23 * * *',
            'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_user_proficiency');
        PERFORM cron.schedule('skill-market-refresh', '0 6,18 * * *',
            'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_market_intelligence');
        PERFORM cron.schedule('skill-roadmap-refresh', '*/15 * * * *',
            'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_roadmap_progress');
        PERFORM cron.schedule('skill-velocity-refresh', '0 * * * *',
            'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_learning_velocity');
        PERFORM cron.schedule('skill-taxonomy-health-refresh', '0 0 * * *',
            'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_taxonomy_health');
        PERFORM cron.schedule('skill-ai-effective-refresh', '*/30 * * * *',
            'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_ai_recommendation_effectiveness');
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
