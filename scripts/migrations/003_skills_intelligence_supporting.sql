-- =============================================================
-- Migration 003: Skills Intelligence & Supporting Tables
-- Creates: market_data, income_data, certifications,
--          junction tables, topics, resources, learning_paths,
--          ai_recommendations, activity_log
-- =============================================================

CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- === 1. skill_market_data ===
CREATE TABLE IF NOT EXISTS skill_market_data (
    skill_id            UUID PRIMARY KEY REFERENCES skills(skill_id) ON DELETE CASCADE,
    demand_score        INT NOT NULL CHECK (demand_score >= 0 AND demand_score <= 100),
    growth_score        REAL NOT NULL CHECK (growth_score >= -100 AND growth_score <= 100),
    salary_median       INT CHECK (salary_median >= 0),
    salary_p10          INT,
    salary_p25          INT,
    salary_p75          INT,
    salary_p90          INT,
    competition_score   INT CHECK (competition_score >= 0 AND competition_score <= 100),
    future_relevance    REAL CHECK (future_relevance >= 0.0 AND future_relevance <= 100.0),
    skill_health        REAL GENERATED ALWAYS AS (
        ROUND((demand_score::REAL * 0.30
            + GREATEST(growth_score, 0) * 0.20
            + COALESCE(salary_median, 0) / 1000.0 * 0.25
            + (100.0 - COALESCE(competition_score, 50)) * 0.10
            + COALESCE(future_relevance, 50) * 0.15)::NUMERIC, 2)
    ) STORED,
    job_postings_count  INT,
    source_data         JSONB NOT NULL DEFAULT '{}',
    data_freshness      TEXT NOT NULL DEFAULT 'current' CHECK (data_freshness IN ('current', 'stale', 'refreshing')),
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
);

COMMENT ON TABLE skill_market_data IS 'Market intelligence scores per skill';

CREATE INDEX IF NOT EXISTS idx_market_demand ON skill_market_data(demand_score DESC);
CREATE INDEX IF NOT EXISTS idx_market_growth ON skill_market_data(growth_score DESC);
CREATE INDEX IF NOT EXISTS idx_market_salary ON skill_market_data(salary_median DESC);
CREATE INDEX IF NOT EXISTS idx_market_health ON skill_market_data(skill_health DESC);
CREATE INDEX IF NOT EXISTS idx_market_freshness ON skill_market_data(data_freshness);

-- === 2. skill_income_data ===
CREATE TABLE IF NOT EXISTS skill_income_data (
    income_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    source              TEXT NOT NULL CHECK (source IN (
        'employment', 'freelance', 'consulting', 'content', 'product',
        'agency', 'teaching', 'opensource', 'digital', 'affiliate'
    )),
    level               INT NOT NULL CHECK (level >= 0 AND level <= 5),
    p10                 INT CHECK (p10 >= 0),
    p25                 INT CHECK (p25 >= 0),
    p50                 INT CHECK (p50 >= 0),
    p75                 INT CHECK (p75 >= 0),
    p90                 INT CHECK (p90 >= 0),
    currency            TEXT NOT NULL DEFAULT 'USD',
    location            TEXT,
    source_data         JSONB NOT NULL DEFAULT '{}',
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_income_record UNIQUE (skill_id, source, level),
    CONSTRAINT valid_percentiles CHECK (p10 <= p25 AND p25 <= p50 AND p50 <= p75 AND p75 <= p90)
);

COMMENT ON TABLE skill_income_data IS 'Income percentiles per skill per level per source type';

CREATE INDEX IF NOT EXISTS idx_income_skill ON skill_income_data(skill_id);
CREATE INDEX IF NOT EXISTS idx_income_source ON skill_income_data(source);
CREATE INDEX IF NOT EXISTS idx_income_level ON skill_income_data(level);
CREATE INDEX IF NOT EXISTS idx_income_skill_source ON skill_income_data(skill_id, source);
CREATE INDEX IF NOT EXISTS idx_income_median ON skill_income_data(p50 DESC);

-- === 3. skill_certifications ===
CREATE TABLE IF NOT EXISTS skill_certifications (
    certification_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    category_id         UUID REFERENCES skill_categories(category_id) ON DELETE SET NULL,
    name                TEXT NOT NULL,
    provider            TEXT NOT NULL,
    level_mapped        INT NOT NULL CHECK (level_mapped >= 0 AND level_mapped <= 5),
    quality_weight      REAL NOT NULL DEFAULT 0.5 CHECK (quality_weight >= 0.0 AND quality_weight <= 1.0),
    is_verified         BOOLEAN NOT NULL DEFAULT false,
    verification_url    TEXT,
    expiration_months   INT,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_certification UNIQUE (name, provider),
    CONSTRAINT unique_cert_per_provider EXCLUDE USING gist (
        name WITH =,
        provider WITH =,
        level_mapped WITH =
    )
);

CREATE INDEX IF NOT EXISTS idx_certs_skill ON skill_certifications(skill_id);
CREATE INDEX IF NOT EXISTS idx_certs_category ON skill_certifications(category_id);
CREATE INDEX IF NOT EXISTS idx_certs_provider ON skill_certifications(provider);
CREATE INDEX IF NOT EXISTS idx_certs_level ON skill_certifications(level_mapped);
CREATE INDEX IF NOT EXISTS idx_certs_verified ON skill_certifications(is_verified) WHERE is_verified = true;

-- === 4. skill_projects (junction) ===
CREATE TABLE IF NOT EXISTS skill_projects (
    project_id          UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    min_level           INT NOT NULL DEFAULT 1 CHECK (min_level >= 0 AND min_level <= 5),
    weight              REAL NOT NULL DEFAULT 1.0 CHECK (weight >= 0.0 AND weight <= 1.0),
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    PRIMARY KEY (project_id, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_projects_skill ON skill_projects(skill_id);
CREATE INDEX IF NOT EXISTS idx_projects_min_level ON skill_projects(min_level);

-- === 5. skill_roadmaps (junction) ===
CREATE TABLE IF NOT EXISTS skill_roadmaps (
    roadmap_id          UUID NOT NULL REFERENCES skill_roadmap_definitions(roadmap_id) ON DELETE CASCADE,
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    phase               TEXT NOT NULL CHECK (phase IN (
        'foundation', 'core', 'intermediate', 'advanced', 'expert', 'optional'
    )),
    sort_order          INT NOT NULL DEFAULT 0,
    target_level        INT NOT NULL CHECK (target_level >= 0 AND target_level <= 5),
    estimated_hours     INT,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    PRIMARY KEY (roadmap_id, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_roadmaps_skill ON skill_roadmaps(skill_id);
CREATE INDEX IF NOT EXISTS idx_roadmaps_phase ON skill_roadmaps(phase);
CREATE INDEX IF NOT EXISTS idx_roadmaps_order ON skill_roadmaps(roadmap_id, sort_order);

-- === 6. skill_opportunities (junction) ===
CREATE TABLE IF NOT EXISTS skill_opportunities (
    opportunity_id       UUID NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
    skill_id             UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    min_level            INT NOT NULL DEFAULT 1 CHECK (min_level >= 0 AND min_level <= 5),
    weight               REAL NOT NULL DEFAULT 1.0 CHECK (weight >= 0.0 AND weight <= 1.0),
    is_required          BOOLEAN NOT NULL DEFAULT true,
    created_at           BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    PRIMARY KEY (opportunity_id, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_opportunities_skill ON skill_opportunities(skill_id);
CREATE INDEX IF NOT EXISTS idx_opportunities_weight ON skill_opportunities(weight DESC);
CREATE INDEX IF NOT EXISTS idx_opportunities_required ON skill_opportunities(opportunity_id) WHERE is_required = true;

-- === 7. skill_topics ===
CREATE TABLE IF NOT EXISTS skill_topics (
    topic_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    name                TEXT NOT NULL,
    description         TEXT NOT NULL DEFAULT '',
    parent_topic_id     UUID REFERENCES skill_topics(topic_id) ON DELETE SET NULL,
    sort_order          INT NOT NULL DEFAULT 0,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_topic_per_skill UNIQUE (skill_id, name)
);

CREATE INDEX IF NOT EXISTS idx_topics_skill ON skill_topics(skill_id);
CREATE INDEX IF NOT EXISTS idx_topics_parent ON skill_topics(parent_topic_id);
CREATE INDEX IF NOT EXISTS idx_topics_order ON skill_topics(skill_id, sort_order);

-- === 8. skill_resources ===
CREATE TABLE IF NOT EXISTS skill_resources (
    resource_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    title               TEXT NOT NULL,
    resource_type       TEXT NOT NULL CHECK (resource_type IN (
        'course', 'book', 'tutorial', 'video', 'article', 'documentation',
        'tool', 'workshop', 'podcast', 'certification_prep'
    )),
    url                 TEXT,
    provider            TEXT,
    difficulty          TEXT NOT NULL DEFAULT 'intermediate' CHECK (difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')),
    estimated_hours     REAL,
    quality_rating      REAL CHECK (quality_rating >= 0.0 AND quality_rating <= 5.0),
    is_free             BOOLEAN NOT NULL DEFAULT false,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_resource_url UNIQUE (url)
);

CREATE INDEX IF NOT EXISTS idx_resources_skill ON skill_resources(skill_id);
CREATE INDEX IF NOT EXISTS idx_resources_type ON skill_resources(resource_type);
CREATE INDEX IF NOT EXISTS idx_resources_difficulty ON skill_resources(difficulty);
CREATE INDEX IF NOT EXISTS idx_resources_rating ON skill_resources(quality_rating DESC);
CREATE INDEX IF NOT EXISTS idx_resources_free ON skill_resources(is_free) WHERE is_free = true;

-- === 9. skill_learning_paths ===
CREATE TABLE IF NOT EXISTS skill_learning_paths (
    path_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_skill_id     UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    name                TEXT NOT NULL,
    description         TEXT NOT NULL DEFAULT '',
    estimated_duration  TEXT,
    difficulty          TEXT NOT NULL DEFAULT 'intermediate' CHECK (difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')),
    steps               JSONB NOT NULL DEFAULT '[]',
    is_ai_generated     BOOLEAN NOT NULL DEFAULT false,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
);

COMMENT ON COLUMN skill_learning_paths.steps IS 'Array of ordered steps: [{step_id, skill_id, resource_id, estimated_hours, description}]';

CREATE INDEX IF NOT EXISTS idx_paths_target ON skill_learning_paths(target_skill_id);
CREATE INDEX IF NOT EXISTS idx_paths_difficulty ON skill_learning_paths(difficulty);
CREATE INDEX IF NOT EXISTS idx_paths_ai ON skill_learning_paths(is_ai_generated) WHERE is_ai_generated = true;

-- === 10. skill_ai_recommendations ===
CREATE TABLE IF NOT EXISTS skill_ai_recommendations (
    recommendation_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL,
    recommendation_type TEXT NOT NULL CHECK (recommendation_type IN (
        'learn', 'improve', 'drop', 'emerging', 'opportunity_readiness',
        'career_path', 'resource_suggestion', 'certification_suggestion'
    )),
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    reasoning           TEXT NOT NULL,
    priority            INT NOT NULL DEFAULT 0 CHECK (priority >= 0 AND priority <= 100),
    accepted            BOOLEAN,
    source              TEXT NOT NULL DEFAULT 'ai',
    metadata            JSONB NOT NULL DEFAULT '{}',
    expires_at          BIGINT,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_active_recommendation UNIQUE (user_id, recommendation_type, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_recommendations_user ON skill_ai_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_type ON skill_ai_recommendations(recommendation_type);
CREATE INDEX IF NOT EXISTS idx_recommendations_skill ON skill_ai_recommendations(skill_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_priority ON skill_ai_recommendations(priority DESC);
CREATE INDEX IF NOT EXISTS idx_recommendations_accepted ON skill_ai_recommendations(accepted) WHERE accepted IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_recommendations_expires ON skill_ai_recommendations(expires_at) WHERE expires_at IS NOT NULL;

-- === 11. skill_user_activity_log ===
CREATE TABLE IF NOT EXISTS skill_user_activity_log (
    activity_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL,
    activity_type       TEXT NOT NULL CHECK (activity_type IN (
        'skill_added', 'level_changed', 'evidence_submitted', 'assessment_taken',
        'target_set', 'target_achieved', 'recommendation_viewed',
        'recommendation_accepted', 'skill_archived', 'skill_deprecated',
        'skill_tree_viewed', 'dashboard_viewed', 'market_data_viewed',
        'income_data_viewed', 'career_readiness_viewed'
    )),
    skill_id            UUID REFERENCES skills(skill_id) ON DELETE SET NULL,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
) PARTITION BY RANGE (created_at);

CREATE INDEX IF NOT EXISTS idx_activity_user ON skill_user_activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_type ON skill_user_activity_log(activity_type);
CREATE INDEX IF NOT EXISTS idx_activity_skill ON skill_user_activity_log(skill_id);
CREATE INDEX IF NOT EXISTS idx_activity_created ON skill_user_activity_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_activity_user_type ON skill_user_activity_log(user_id, activity_type);
CREATE INDEX IF NOT EXISTS idx_activity_user_date ON skill_user_activity_log(user_id, created_at DESC);

-- Partition children for skill_user_activity_log (monthly by created_at)
CREATE TABLE IF NOT EXISTS skill_user_activity_log_2026_q3 PARTITION OF skill_user_activity_log
    FOR VALUES FROM (1767225600000) TO (1775174400000);
CREATE TABLE IF NOT EXISTS skill_user_activity_log_2026_q4 PARTITION OF skill_user_activity_log
    FOR VALUES FROM (1775174400000) TO (1783123200000);
