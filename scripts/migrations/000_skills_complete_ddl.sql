-- =============================================================
-- SKILLS DATABASE — COMPLETE DDL (Monolithic)
-- Aggregates: 6 migrations (001-006) + seed taxonomy
-- Total tables: 33 | Materialized views: 6 | Roles: 8
-- Deploy: psql -f 000_skills_complete_ddl.sql
-- Requires: PostgreSQL 15+ (ltree, pgcrypto)
-- =============================================================

BEGIN;

-- =============================================================
-- MIGRATION 001: Core Taxonomy (7 tables)
-- =============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "ltree";

CREATE TABLE IF NOT EXISTS skill_categories (
    category_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_category_id  UUID REFERENCES skill_categories(category_id) ON DELETE SET NULL,
    name                TEXT NOT NULL,
    slug                TEXT NOT NULL,
    description         TEXT NOT NULL DEFAULT '',
    icon                TEXT,
    color               TEXT,
    sort_order          INT NOT NULL DEFAULT 0,
    level               INT NOT NULL DEFAULT 0 CHECK (level >= 0 AND level <= 10),
    path                LTREE,
    is_active           BOOLEAN NOT NULL DEFAULT true,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_category_name UNIQUE (name),
    CONSTRAINT unique_category_slug UNIQUE (slug)
);

CREATE INDEX IF NOT EXISTS idx_categories_parent ON skill_categories(parent_category_id);
CREATE INDEX IF NOT EXISTS idx_categories_path ON skill_categories USING GIST(path);
CREATE INDEX IF NOT EXISTS idx_categories_sort ON skill_categories(sort_order);
CREATE INDEX IF NOT EXISTS idx_categories_active ON skill_categories(is_active) WHERE is_active = true;

CREATE TABLE IF NOT EXISTS skills (
    skill_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id         UUID NOT NULL REFERENCES skill_categories(category_id) ON DELETE RESTRICT,
    name                TEXT NOT NULL,
    slug                TEXT NOT NULL,
    description         TEXT NOT NULL DEFAULT '',
    level_min           INT NOT NULL DEFAULT 0 CHECK (level_min >= 0 AND level_min <= 5),
    level_max           INT NOT NULL DEFAULT 5 CHECK (level_max >= 0 AND level_max <= 5),
    aliases             TEXT[] NOT NULL DEFAULT '{}',
    skill_health        REAL,
    metadata            JSONB NOT NULL DEFAULT '{}',
    is_deprecated       BOOLEAN NOT NULL DEFAULT false,
    deprecated_at       BIGINT,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT valid_level_range CHECK (level_min <= level_max),
    CONSTRAINT unique_skill_name_per_category UNIQUE (category_id, name),
    CONSTRAINT unique_skill_slug UNIQUE (slug)
);

CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category_id);
CREATE INDEX IF NOT EXISTS idx_skills_slug ON skills(slug);
CREATE INDEX IF NOT EXISTS idx_skills_health ON skills(skill_health DESC) WHERE skill_health IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_skills_metadata ON skills USING GIN(metadata jsonb_path_ops);

CREATE TABLE IF NOT EXISTS skill_relationships (
    relationship_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_skill_id       UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    to_skill_id         UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    relationship_type   TEXT NOT NULL CHECK (relationship_type IN (
        'prerequisite','related_to','supersedes','variant_of',
        'similar_to','recommended_before','complementary','alternative'
    )),
    min_level_from      INT CHECK (min_level_from >= 0 AND min_level_from <= 5),
    min_level_to        INT CHECK (min_level_to >= 0 AND min_level_to <= 5),
    weight              REAL NOT NULL DEFAULT 1.0 CHECK (weight >= 0.0 AND weight <= 1.0),
    is_directed         BOOLEAN NOT NULL DEFAULT true,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_relationship UNIQUE (from_skill_id, to_skill_id, relationship_type),
    CONSTRAINT no_self_relationship CHECK (from_skill_id <> to_skill_id)
);

CREATE INDEX IF NOT EXISTS idx_relationships_from ON skill_relationships(from_skill_id);
CREATE INDEX IF NOT EXISTS idx_relationships_to ON skill_relationships(to_skill_id);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON skill_relationships(relationship_type);
CREATE INDEX IF NOT EXISTS idx_relationships_from_type ON skill_relationships(from_skill_id, relationship_type);

CREATE TABLE IF NOT EXISTS tags (
    tag_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                TEXT NOT NULL,
    slug                TEXT NOT NULL,
    description         TEXT NOT NULL DEFAULT '',
    color               TEXT,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_tag_name UNIQUE (name),
    CONSTRAINT unique_tag_slug UNIQUE (slug)
);

CREATE INDEX IF NOT EXISTS idx_tags_slug ON tags(slug);

CREATE TABLE IF NOT EXISTS skill_tags (
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    tag_id              UUID NOT NULL REFERENCES tags(tag_id) ON DELETE CASCADE,
    PRIMARY KEY (skill_id, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_skill_tags_tag ON skill_tags(tag_id);

CREATE TABLE IF NOT EXISTS skill_external_mappings (
    mapping_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    external_system     TEXT NOT NULL CHECK (external_system IN (
        'linkedin','esco','onet','workday','bamboohr',
        'cornerstone','docebo','greenhouse','lever','custom'
    )),
    external_id         TEXT NOT NULL,
    external_name       TEXT NOT NULL,
    mapping_type        TEXT NOT NULL DEFAULT 'exact' CHECK (mapping_type IN (
        'exact','broader','narrower','related','close_match'
    )),
    confidence          REAL NOT NULL DEFAULT 1.0 CHECK (confidence >= 0.0 AND confidence <= 1.0),
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_external_mapping UNIQUE (skill_id, external_system, external_id)
);

CREATE INDEX IF NOT EXISTS idx_mappings_skill ON skill_external_mappings(skill_id);
CREATE INDEX IF NOT EXISTS idx_mappings_system ON skill_external_mappings(external_system);
CREATE INDEX IF NOT EXISTS idx_mappings_external_id ON skill_external_mappings(external_system, external_id);

CREATE TABLE IF NOT EXISTS skill_roadmap_definitions (
    roadmap_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                TEXT NOT NULL,
    description         TEXT NOT NULL DEFAULT '',
    target_skill_id     UUID REFERENCES skills(skill_id) ON DELETE SET NULL,
    difficulty          TEXT NOT NULL DEFAULT 'intermediate' CHECK (difficulty IN ('beginner','intermediate','advanced','expert')),
    estimated_duration  TEXT,
    is_ai_generated     BOOLEAN NOT NULL DEFAULT false,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_roadmap_name UNIQUE (name)
);

CREATE INDEX IF NOT EXISTS idx_roadmap_defs_target ON skill_roadmap_definitions(target_skill_id);
CREATE INDEX IF NOT EXISTS idx_roadmap_defs_difficulty ON skill_roadmap_definitions(difficulty);

-- =============================================================
-- MIGRATION 002: User Skills (5 tables)
-- =============================================================

CREATE TABLE IF NOT EXISTS user_skills (
    user_skill_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL,
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE RESTRICT,
    level               INT NOT NULL DEFAULT 0 CHECK (level >= 0 AND level <= 5),
    state               TEXT NOT NULL DEFAULT 'learning' CHECK (state IN (
        'planned','learning','practicing','active','reviewing','archived','deprecated'
    )),
    confidence_score    REAL NOT NULL DEFAULT 0.0 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    evidence_score      REAL NOT NULL DEFAULT 0.0 CHECK (evidence_score >= 0.0 AND evidence_score <= 1.0),
    level_change_90d    REAL NOT NULL DEFAULT 0.0,
    is_emerging         BOOLEAN NOT NULL DEFAULT false,
    is_stale            BOOLEAN NOT NULL DEFAULT false,
    last_activity_at    BIGINT,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_user_skill UNIQUE (user_id, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_user_skills_user ON user_skills(user_id);
CREATE INDEX IF NOT EXISTS idx_user_skills_skill ON user_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_user_skills_level ON user_skills(level);
CREATE INDEX IF NOT EXISTS idx_user_skills_state ON user_skills(state);
CREATE INDEX IF NOT EXISTS idx_user_skills_stale ON user_skills(is_stale) WHERE is_stale = true;
CREATE INDEX IF NOT EXISTS idx_user_skills_emerging ON user_skills(is_emerging) WHERE is_emerging = true;

CREATE TABLE IF NOT EXISTS user_skill_evidence (
    evidence_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL,
    skill_id            UUID NOT NULL,
    source_type         TEXT NOT NULL CHECK (source_type IN (
        'project','github','certification','hackathon','freelance',
        'opensource','assessment','work_experience','course','publication','patent','award'
    )),
    state               TEXT NOT NULL DEFAULT 'raw' CHECK (state IN (
        'raw','pending_verification','verified','verified_auto',
        'verified_ai','verified_human','rejected','flagged','active','expired'
    )),
    title               TEXT NOT NULL,
    description         TEXT NOT NULL DEFAULT '',
    url                 TEXT,
    quality_score       REAL NOT NULL DEFAULT 0.0 CHECK (quality_score >= 0.0 AND quality_score <= 1.0),
    trust_score         REAL NOT NULL DEFAULT 0.0 CHECK (trust_score >= 0.0 AND trust_score <= 1.0),
    weight              REAL NOT NULL DEFAULT 0.0 CHECK (weight >= 0.0 AND weight <= 1.0),
    signed_hash         TEXT NOT NULL,
    previous_hash       TEXT,
    metadata            JSONB NOT NULL DEFAULT '{}',
    collected_at        BIGINT NOT NULL,
    verified_at         BIGINT,
    expires_at          BIGINT,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_evidence_signed_hash UNIQUE (signed_hash)
);

CREATE INDEX IF NOT EXISTS idx_evidence_user ON user_skill_evidence(user_id);
CREATE INDEX IF NOT EXISTS idx_evidence_skill ON user_skill_evidence(skill_id);
CREATE INDEX IF NOT EXISTS idx_evidence_source ON user_skill_evidence(source_type);
CREATE INDEX IF NOT EXISTS idx_evidence_state ON user_skill_evidence(state);
CREATE INDEX IF NOT EXISTS idx_evidence_quality ON user_skill_evidence(quality_score DESC);

CREATE TABLE IF NOT EXISTS user_skill_targets (
    target_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL,
    skill_id            UUID NOT NULL,
    target_level        INT NOT NULL CHECK (target_level >= 1 AND target_level <= 5),
    current_level       INT NOT NULL DEFAULT 0 CHECK (current_level >= 0 AND current_level <= 5),
    priority            TEXT NOT NULL DEFAULT 'medium' CHECK (priority IN ('low','medium','high','urgent')),
    target_date         DATE,
    status              TEXT NOT NULL DEFAULT 'active' CHECK (status IN (
        'active','in_progress','achieved','paused','abandoned','expired'
    )),
    gap_size            INT GENERATED ALWAYS AS (target_level - current_level) STORED,
    progress_pct        REAL GENERATED ALWAYS AS (
        CASE WHEN target_level > 0 THEN LEAST(1.0, current_level::REAL / target_level::REAL) * 100 ELSE 0 END
    ) STORED,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT valid_target CHECK (target_level > current_level)
);

CREATE INDEX IF NOT EXISTS idx_targets_user ON user_skill_targets(user_id);
CREATE INDEX IF NOT EXISTS idx_targets_skill ON user_skill_targets(skill_id);
CREATE INDEX IF NOT EXISTS idx_targets_status ON user_skill_targets(status);
CREATE INDEX IF NOT EXISTS idx_targets_active_user ON user_skill_targets(user_id) WHERE status = 'active';

CREATE TABLE IF NOT EXISTS user_skill_assessments (
    assessment_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL,
    skill_id            UUID NOT NULL,
    assessment_type     TEXT NOT NULL CHECK (assessment_type IN (
        'self','ai_evaluated','auto_mcq','peer_review',
        'human_review','project_evaluation','certification_equivalency'
    )),
    score               REAL CHECK (score >= 0.0 AND score <= 100.0),
    level_achieved      INT CHECK (level_achieved >= 0 AND level_achieved <= 5),
    confidence          REAL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    status              TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
        'pending','in_progress','completed','expired','invalidated'
    )),
    duration_seconds    INT,
    result_data         JSONB NOT NULL DEFAULT '{}',
    started_at          BIGINT,
    completed_at        BIGINT,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
);

CREATE INDEX IF NOT EXISTS idx_assessments_user ON user_skill_assessments(user_id);
CREATE INDEX IF NOT EXISTS idx_assessments_skill ON user_skill_assessments(skill_id);
CREATE INDEX IF NOT EXISTS idx_assessments_type ON user_skill_assessments(assessment_type);
CREATE INDEX IF NOT EXISTS idx_assessments_status ON user_skill_assessments(status);

CREATE TABLE IF NOT EXISTS user_skill_versions (
    version_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL,
    skill_id            UUID NOT NULL,
    version_number      INT NOT NULL,
    change_type         TEXT NOT NULL CHECK (change_type IN (
        'created','level_changed','state_changed','evidence_added',
        'metadata_updated','archived','deprecated','restored'
    )),
    previous_state      JSONB NOT NULL,
    new_state           JSONB NOT NULL,
    changed_by          UUID NOT NULL,
    change_reason       TEXT,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_version_per_skill UNIQUE (user_id, skill_id, version_number)
);

CREATE INDEX IF NOT EXISTS idx_versions_user ON user_skill_versions(user_id);
CREATE INDEX IF NOT EXISTS idx_versions_skill ON user_skill_versions(skill_id);
CREATE INDEX IF NOT EXISTS idx_versions_type ON user_skill_versions(change_type);

-- =============================================================
-- MIGRATION 003: Intelligence & Supporting (11 tables)
-- =============================================================

CREATE TABLE IF NOT EXISTS skill_market_data (
    skill_id            UUID PRIMARY KEY REFERENCES skills(skill_id) ON DELETE CASCADE,
    demand_score        INT NOT NULL CHECK (demand_score >= 0 AND demand_score <= 100),
    growth_score        REAL NOT NULL CHECK (growth_score >= -100 AND growth_score <= 100),
    salary_median       INT CHECK (salary_median >= 0),
    salary_p10          INT, salary_p25 INT, salary_p75 INT, salary_p90 INT,
    competition_score   INT CHECK (competition_score >= 0 AND competition_score <= 100),
    future_relevance    REAL CHECK (future_relevance >= 0.0 AND future_relevance <= 100.0),
    skill_health        REAL GENERATED ALWAYS AS (
        ROUND((demand_score::REAL * 0.30 + GREATEST(growth_score, 0) * 0.20
            + COALESCE(salary_median, 0) / 1000.0 * 0.25
            + (100.0 - COALESCE(competition_score, 50)) * 0.10
            + COALESCE(future_relevance, 50) * 0.15)::NUMERIC, 2)
    ) STORED,
    job_postings_count  INT,
    source_data         JSONB NOT NULL DEFAULT '{}',
    data_freshness      TEXT NOT NULL DEFAULT 'current' CHECK (data_freshness IN ('current','stale','refreshing')),
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
);

CREATE INDEX IF NOT EXISTS idx_market_demand ON skill_market_data(demand_score DESC);
CREATE INDEX IF NOT EXISTS idx_market_growth ON skill_market_data(growth_score DESC);
CREATE INDEX IF NOT EXISTS idx_market_salary ON skill_market_data(salary_median DESC);
CREATE INDEX IF NOT EXISTS idx_market_health ON skill_market_data(skill_health DESC);
CREATE INDEX IF NOT EXISTS idx_market_freshness ON skill_market_data(data_freshness);

CREATE TABLE IF NOT EXISTS skill_income_data (
    income_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    source              TEXT NOT NULL CHECK (source IN (
        'employment','freelance','consulting','content','product',
        'agency','teaching','opensource','digital','affiliate'
    )),
    level               INT NOT NULL CHECK (level >= 0 AND level <= 5),
    p10 INT, p25 INT, p50 INT, p75 INT, p90 INT,
    currency            TEXT NOT NULL DEFAULT 'USD',
    location            TEXT,
    source_data         JSONB NOT NULL DEFAULT '{}',
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_income_record UNIQUE (skill_id, source, level),
    CONSTRAINT valid_percentiles CHECK (p10 <= p25 AND p25 <= p50 AND p50 <= p75 AND p75 <= p90)
);

CREATE INDEX IF NOT EXISTS idx_income_skill ON skill_income_data(skill_id);
CREATE INDEX IF NOT EXISTS idx_income_source ON skill_income_data(source);
CREATE INDEX IF NOT EXISTS idx_income_level ON skill_income_data(level);

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
    CONSTRAINT unique_certification UNIQUE (name, provider)
);

CREATE INDEX IF NOT EXISTS idx_certs_skill ON skill_certifications(skill_id);
CREATE INDEX IF NOT EXISTS idx_certs_category ON skill_certifications(category_id);
CREATE INDEX IF NOT EXISTS idx_certs_provider ON skill_certifications(provider);
CREATE INDEX IF NOT EXISTS idx_certs_level ON skill_certifications(level_mapped);

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

CREATE TABLE IF NOT EXISTS skill_resources (
    resource_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    title               TEXT NOT NULL,
    resource_type       TEXT NOT NULL CHECK (resource_type IN (
        'course','book','tutorial','video','article','documentation',
        'tool','workshop','podcast','certification_prep'
    )),
    url                 TEXT,
    provider            TEXT,
    difficulty          TEXT NOT NULL DEFAULT 'intermediate' CHECK (difficulty IN ('beginner','intermediate','advanced','expert')),
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

CREATE TABLE IF NOT EXISTS skill_learning_paths (
    path_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_skill_id     UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    name                TEXT NOT NULL,
    description         TEXT NOT NULL DEFAULT '',
    estimated_duration  TEXT,
    difficulty          TEXT NOT NULL DEFAULT 'intermediate' CHECK (difficulty IN ('beginner','intermediate','advanced','expert')),
    steps               JSONB NOT NULL DEFAULT '[]',
    is_ai_generated     BOOLEAN NOT NULL DEFAULT false,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
);

CREATE INDEX IF NOT EXISTS idx_paths_target ON skill_learning_paths(target_skill_id);
CREATE INDEX IF NOT EXISTS idx_paths_difficulty ON skill_learning_paths(difficulty);

CREATE TABLE IF NOT EXISTS skill_ai_recommendations (
    recommendation_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL,
    recommendation_type TEXT NOT NULL CHECK (recommendation_type IN (
        'learn','improve','drop','emerging','opportunity_readiness',
        'career_path','resource_suggestion','certification_suggestion'
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

CREATE TABLE IF NOT EXISTS skill_user_activity_log (
    activity_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL,
    activity_type       TEXT NOT NULL CHECK (activity_type IN (
        'skill_added','level_changed','evidence_submitted','assessment_taken',
        'target_set','target_achieved','recommendation_viewed',
        'recommendation_accepted','skill_archived','skill_deprecated',
        'dashboard_viewed','market_data_viewed','income_data_viewed'
    )),
    skill_id            UUID REFERENCES skills(skill_id) ON DELETE SET NULL,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
);

CREATE INDEX IF NOT EXISTS idx_activity_user ON skill_user_activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_type ON skill_user_activity_log(activity_type);
CREATE INDEX IF NOT EXISTS idx_activity_skill ON skill_user_activity_log(skill_id);
CREATE INDEX IF NOT EXISTS idx_activity_created ON skill_user_activity_log(created_at DESC);

-- =============================================================
-- MIGRATION 004: Audit, Events & Analytics (10 tables)
-- =============================================================

CREATE TABLE IF NOT EXISTS skill_audit_log (
    audit_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name          TEXT NOT NULL,
    record_id           UUID NOT NULL,
    user_id             UUID,
    action              TEXT NOT NULL CHECK (action IN ('INSERT','UPDATE','DELETE','TRUNCATE','SOFT_DELETE','RESTORE')),
    old_data            JSONB,
    new_data            JSONB,
    changed_fields      TEXT[],
    ip_address          TEXT,
    user_agent          TEXT,
    request_id          TEXT,
    tenant_id           UUID,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
);

CREATE INDEX IF NOT EXISTS idx_audit_table ON skill_audit_log(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_record ON skill_audit_log(record_id);
CREATE INDEX IF NOT EXISTS idx_audit_user ON skill_audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON skill_audit_log(created_at DESC);

CREATE TABLE IF NOT EXISTS skill_taxonomy_history (
    history_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type         TEXT NOT NULL CHECK (entity_type IN ('skill','category','relationship','tag')),
    entity_id           UUID NOT NULL,
    version             INT NOT NULL,
    previous_state      JSONB NOT NULL,
    new_state           JSONB NOT NULL,
    change_type         TEXT NOT NULL CHECK (change_type IN ('created','updated','deprecated','restored','merged','split')),
    changed_by          UUID,
    change_reason       TEXT,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_taxonomy_version UNIQUE (entity_type, entity_id, version)
);

CREATE INDEX IF NOT EXISTS idx_taxonomy_history_entity ON skill_taxonomy_history(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_taxonomy_history_created ON skill_taxonomy_history(created_at DESC);

CREATE TABLE IF NOT EXISTS skill_user_skill_history (
    history_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL,
    skill_id            UUID NOT NULL,
    version             INT NOT NULL,
    proficiency_before  INT,
    proficiency_after   INT,
    hours_since_last    REAL,
    change_type         TEXT NOT NULL CHECK (change_type IN (
        'level_changed','state_changed','evidence_added','confidence_changed',
        'metadata_updated','archived','deprecated','restored'
    )),
    changed_by          UUID,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_user_skill_history_version UNIQUE (user_id, skill_id, version)
);

CREATE INDEX IF NOT EXISTS idx_user_skill_history ON skill_user_skill_history(user_id, skill_id);
CREATE INDEX IF NOT EXISTS idx_user_skill_history_user ON skill_user_skill_history(user_id);
CREATE INDEX IF NOT EXISTS idx_user_skill_history_type ON skill_user_skill_history(change_type);

CREATE TABLE IF NOT EXISTS skill_market_history (
    market_history_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    demand_score        INT, growth_score REAL, salary_median INT,
    competition_score   INT, future_relevance REAL, skill_health REAL,
    snapshot_source     TEXT NOT NULL DEFAULT 'automated',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
);

CREATE INDEX IF NOT EXISTS idx_market_history_skill ON skill_market_history(skill_id);
CREATE INDEX IF NOT EXISTS idx_market_history_created ON skill_market_history(created_at DESC);

CREATE TABLE IF NOT EXISTS skill_events (
    event_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type          TEXT NOT NULL,
    event_version       TEXT NOT NULL DEFAULT '1.0',
    aggregate_type      TEXT NOT NULL,
    aggregate_id        UUID NOT NULL,
    user_id             UUID,
    data                JSONB NOT NULL,
    metadata            JSONB NOT NULL DEFAULT '{}',
    correlation_id      UUID, causation_id UUID,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
);

CREATE INDEX IF NOT EXISTS idx_events_type ON skill_events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_aggregate ON skill_events(aggregate_type, aggregate_id);
CREATE INDEX IF NOT EXISTS idx_events_user ON skill_events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_created ON skill_events(created_at DESC);

CREATE TABLE IF NOT EXISTS skill_event_outbox (
    outbox_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type          TEXT NOT NULL,
    aggregate_type      TEXT NOT NULL,
    aggregate_id        UUID NOT NULL,
    payload             JSONB NOT NULL,
    status              TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','processing','delivered','failed','dead_letter')),
    retry_count         INT NOT NULL DEFAULT 0,
    max_retries         INT NOT NULL DEFAULT 3,
    last_error          TEXT,
    scheduled_at        BIGINT, processed_at BIGINT,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
);

CREATE INDEX IF NOT EXISTS idx_outbox_status ON skill_event_outbox(status) WHERE status IN ('pending','failed');

CREATE TABLE IF NOT EXISTS skill_webhook_queue (
    webhook_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id     UUID NOT NULL,
    event_type          TEXT NOT NULL,
    payload             JSONB NOT NULL,
    url                 TEXT NOT NULL,
    headers             JSONB NOT NULL DEFAULT '{}',
    status              TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','delivering','delivered','failed','dead_letter')),
    retry_count         INT NOT NULL DEFAULT 0,
    max_retries         INT NOT NULL DEFAULT 5,
    last_error          TEXT, last_http_status INT,
    scheduled_at        BIGINT, delivered_at BIGINT,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
);

CREATE INDEX IF NOT EXISTS idx_webhook_status ON skill_webhook_queue(status) WHERE status IN ('pending','failed');
CREATE INDEX IF NOT EXISTS idx_webhook_subscription ON skill_webhook_queue(subscription_id);

CREATE TABLE IF NOT EXISTS skill_event_subscriptions (
    subscription_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                TEXT NOT NULL,
    url                 TEXT NOT NULL,
    event_types         TEXT[] NOT NULL DEFAULT '{}',
    headers             JSONB NOT NULL DEFAULT '{}',
    is_active           BOOLEAN NOT NULL DEFAULT true,
    secret              TEXT,
    retry_policy        JSONB NOT NULL DEFAULT '{"max_retries":5,"backoff":"exponential","initial_delay_ms":1000}',
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_subscription_url UNIQUE (name, url)
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_active ON skill_event_subscriptions(is_active) WHERE is_active = true;

CREATE TABLE IF NOT EXISTS skill_analytics_snapshots (
    snapshot_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL,
    snapshot_date       DATE NOT NULL,
    avg_skill_level     REAL, skill_count INT, readiness_score REAL,
    learning_velocity   REAL, diversification_score REAL, income_per_hour REAL,
    market_alignment    REAL, emerging_coverage INT,
    milestone_completion REAL, evidence_ratio REAL,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_user_snapshot_date UNIQUE (user_id, snapshot_date)
);

CREATE INDEX IF NOT EXISTS idx_snapshots_user ON skill_analytics_snapshots(user_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_date ON skill_analytics_snapshots(snapshot_date DESC);

CREATE TABLE IF NOT EXISTS skill_forecasts (
    forecast_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    metric              TEXT NOT NULL CHECK (metric IN ('demand','growth','salary','competition','future_relevance','skill_health')),
    forecast_date       DATE NOT NULL,
    predicted_value     REAL NOT NULL,
    confidence_lower    REAL, confidence_upper REAL,
    model_version       TEXT NOT NULL DEFAULT '1.0',
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_forecast UNIQUE (skill_id, metric, forecast_date)
);

CREATE INDEX IF NOT EXISTS idx_forecasts_skill ON skill_forecasts(skill_id);
CREATE INDEX IF NOT EXISTS idx_forecasts_metric ON skill_forecasts(metric);
CREATE INDEX IF NOT EXISTS idx_forecasts_date ON skill_forecasts(forecast_date);

-- =============================================================
-- MIGRATION 005: Security — RLS, Roles, Encryption
-- =============================================================

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'skill_admin') THEN CREATE ROLE skill_admin; END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'skill_manager') THEN CREATE ROLE skill_manager; END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'skill_user') THEN CREATE ROLE skill_user; END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'skill_auditor') THEN CREATE ROLE skill_auditor; END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'skill_viewer') THEN CREATE ROLE skill_viewer; END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'skill_api') THEN CREATE ROLE skill_api; END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'skill_scheduler') THEN CREATE ROLE skill_scheduler; END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'skill_analytics') THEN CREATE ROLE skill_analytics; END IF;
END $$;

CREATE OR REPLACE FUNCTION skill_current_tenant_id() RETURNS UUID AS $$
    BEGIN RETURN NULLIF(current_setting('app.tenant_id', true), '')::UUID; END;
$$ LANGUAGE plpgsql STABLE;

CREATE OR REPLACE FUNCTION skill_current_user_id() RETURNS UUID AS $$
    BEGIN RETURN NULLIF(current_setting('app.user_id', true), '')::UUID; END;
$$ LANGUAGE plpgsql STABLE;

DO $$ DECLARE tbl TEXT; BEGIN
    FOREACH tbl IN ARRAY ARRAY[
        'skill_categories','skills','skill_relationships','tags','skill_tags',
        'skill_external_mappings','skill_roadmap_definitions','user_skills',
        'user_skill_evidence','user_skill_targets','user_skill_assessments','user_skill_versions',
        'skill_market_data','skill_income_data','skill_certifications',
        'skill_topics','skill_resources','skill_learning_paths','skill_ai_recommendations','skill_user_activity_log',
        'skill_audit_log','skill_taxonomy_history','skill_user_skill_history','skill_market_history',
        'skill_events','skill_event_outbox','skill_webhook_queue','skill_event_subscriptions',
        'skill_analytics_snapshots','skill_forecasts'
    ] LOOP
        EXECUTE format('ALTER TABLE %I ADD COLUMN IF NOT EXISTS tenant_id UUID', tbl);
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', tbl);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', tbl);
    END LOOP;
END $$;

-- RLS policies (abbreviated set — full in 005_skills_security_rls.sql)
CREATE POLICY admin_all_skill_categories ON skill_categories FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY manager_all_skill_categories ON skill_categories FOR ALL TO skill_manager USING (true) WITH CHECK (true);
CREATE POLICY user_sel_skill_categories ON skill_categories FOR SELECT TO skill_user USING (true);
CREATE POLICY api_all_skill_categories ON skill_categories FOR ALL TO skill_api USING (true) WITH CHECK (true);
CREATE POLICY admin_all_skills ON skills FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY manager_all_skills ON skills FOR ALL TO skill_manager USING (true) WITH CHECK (true);
CREATE POLICY user_sel_skills ON skills FOR SELECT TO skill_user USING (true);
CREATE POLICY api_all_skills ON skills FOR ALL TO skill_api USING (true) WITH CHECK (true);
CREATE POLICY admin_all_user_skills ON user_skills FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY user_all_user_skills ON user_skills FOR ALL TO skill_user USING (user_id = skill_current_user_id()) WITH CHECK (user_id = skill_current_user_id());
CREATE POLICY api_all_user_skills ON user_skills FOR ALL TO skill_api USING (true) WITH CHECK (true);

-- PII encryption
CREATE OR REPLACE FUNCTION skill_encrypt_pii(plaintext TEXT) RETURNS BYTEA AS $$
DECLARE enc_key TEXT;
BEGIN enc_key := current_setting('app.encryption_key', true);
    IF enc_key IS NULL THEN RETURN convert_to(plaintext, 'UTF8'); END IF;
    RETURN pgp_sym_encrypt(plaintext, enc_key);
END;
$$ LANGUAGE plpgsql STABLE;

ALTER TABLE skill_external_mappings ADD COLUMN IF NOT EXISTS external_credentials BYTEA;

-- =============================================================
-- MIGRATION 006: Materialized Views (6 views)
-- =============================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_skill_user_proficiency AS
SELECT us.user_id, us.tenant_id,
    COUNT(DISTINCT us.skill_id) AS total_skills,
    COUNT(DISTINCT us.skill_id) FILTER (WHERE us.level >= 3) AS intermediate_plus,
    ROUND(AVG(us.level)::NUMERIC, 2) AS avg_level,
    MAX(us.level) AS max_level,
    MAX(us.last_activity_at) AS last_active
FROM user_skills us GROUP BY us.user_id, us.tenant_id WITH NO DATA;
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_prof_user ON mv_skill_user_proficiency(user_id, tenant_id);

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_skill_market_intelligence AS
SELECT s.skill_id, s.name AS skill_name, sc.name AS category_name,
    smd.demand_score, smd.growth_score, smd.salary_median, smd.skill_health,
    sid.p50 AS median_income,
    RANK() OVER (ORDER BY smd.demand_score DESC) AS demand_rank
FROM skills s JOIN skill_categories sc ON s.category_id = sc.category_id
LEFT JOIN skill_market_data smd ON s.skill_id = smd.skill_id
LEFT JOIN skill_income_data sid ON s.skill_id = sid.skill_id AND sid.source='employment' AND sid.level=3
WITH NO DATA;
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_market_skill ON mv_skill_market_intelligence(skill_id);

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_skill_learning_velocity AS
SELECT ush.user_id, ush.tenant_id, ush.skill_id,
    COUNT(*) AS total_events,
    COALESCE(MAX(ush.proficiency_after) - MIN(ush.proficiency_before), 0) AS total_gain
FROM skill_user_skill_history ush GROUP BY ush.user_id, ush.tenant_id, ush.skill_id WITH NO DATA;
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_velocity ON mv_skill_learning_velocity(user_id, skill_id, tenant_id);

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_skill_taxonomy_health AS
SELECT sc.category_id, sc.name,
    COUNT(DISTINCT s.skill_id) AS skill_count,
    COUNT(DISTINCT smd.skill_id) AS with_market_data
FROM skill_categories sc LEFT JOIN skills s ON sc.category_id = s.category_id
LEFT JOIN skill_market_data smd ON s.skill_id = smd.skill_id
GROUP BY sc.category_id, sc.name WITH NO DATA;
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_taxonomy_cat ON mv_skill_taxonomy_health(category_id);

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_skill_ai_effectiveness AS
SELECT user_id, tenant_id,
    COUNT(*) AS total, COUNT(*) FILTER (WHERE accepted = true) AS accepted,
    ROUND((COUNT(*) FILTER (WHERE accepted = true)::NUMERIC / NULLIF(COUNT(*),0)) * 100, 1) AS acceptance_pct
FROM skill_ai_recommendations GROUP BY user_id, tenant_id WITH NO DATA;
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_ai_user ON mv_skill_ai_effectiveness(user_id, tenant_id);

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_skill_activity_heatmap AS
SELECT user_id, tenant_id,
    DATE_TRUNC('day', TO_TIMESTAMP(created_at / 1000))::DATE AS d,
    EXTRACT(DOW FROM TO_TIMESTAMP(created_at / 1000))::INT AS dow,
    EXTRACT(HOUR FROM TO_TIMESTAMP(created_at / 1000))::INT AS hod,
    activity_type, COUNT(*) AS cnt
FROM skill_user_activity_log GROUP BY user_id, tenant_id, d, dow, hod, activity_type WITH NO DATA;
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_heatmap ON mv_skill_activity_heatmap(user_id, tenant_id, d, hod, activity_type);

COMMIT;
