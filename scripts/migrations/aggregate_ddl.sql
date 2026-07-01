-- =============================================================
-- SKILLS DATABASE — AUTO-GENERATED AGGREGATE DDL
-- Generated: 2026-06-27T18:04:42.721075
-- Source: gen_sdb_full.py
-- =============================================================

-- ===== Begin: 000_skills_complete_ddl.sql =====
-- =============================================================
-- SKILLS DATABASE — COMPLETE DDL (Monolithic)
-- Aggregates: 6 migrations (001-006) + seed taxonomy
-- Total tables: 33 | Materialized views: 7 | Roles: 8
-- Deploy: psql -f 000_skills_complete_ddl.sql
-- Requires: PostgreSQL 15+ (ltree, pgcrypto, btree_gist)
-- =============================================================

BEGIN;

-- =============================================================
-- EXTENSIONS
-- =============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "ltree";
CREATE EXTENSION IF NOT EXISTS "btree_gist";
CREATE EXTENSION IF NOT EXISTS pg_stat_statements WITH SCHEMA public;

-- =============================================================
-- GROUP 1: CORE TAXONOMY (7 tables)
-- =============================================================

-- 1.1 skill_categories
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
COMMENT ON TABLE skill_categories IS 'Hierarchical category tree for skills taxonomy with LTREE ancestry';

-- 1.2 skills
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
CREATE INDEX IF NOT EXISTS idx_skills_deprecated ON skills(is_deprecated) WHERE is_deprecated = false;
CREATE INDEX IF NOT EXISTS idx_skills_metadata ON skills USING GIN(metadata jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_skills_health ON skills(skill_health DESC) WHERE skill_health IS NOT NULL;
COMMENT ON TABLE skills IS 'Canonical skill definitions -- single source of truth for the skill taxonomy';

-- 1.3 skill_relationships
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
CREATE INDEX IF NOT EXISTS idx_relationships_weight ON skill_relationships(weight DESC);
CREATE INDEX IF NOT EXISTS idx_relationships_from_type ON skill_relationships(from_skill_id, relationship_type);
ALTER TABLE skill_relationships ADD CONSTRAINT IF NOT EXISTS no_overlapping_prereqs
    EXCLUDE USING gist (from_skill_id WITH =, to_skill_id WITH =, relationship_type WITH =);
COMMENT ON TABLE skill_relationships IS 'Typed, weighted, directed edges between skills for graph traversal';

-- 1.4 tags
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

-- 1.5 skill_tags (junction)
CREATE TABLE IF NOT EXISTS skill_tags (
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    tag_id              UUID NOT NULL REFERENCES tags(tag_id) ON DELETE CASCADE,
    PRIMARY KEY (skill_id, tag_id)
);
CREATE INDEX IF NOT EXISTS idx_skill_tags_tag ON skill_tags(tag_id);

-- 1.6 skill_external_mappings
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

-- 1.7 skill_roadmap_definitions
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
-- GROUP 2: USER SKILLS (5 tables)
-- =============================================================

-- 2.1 user_skills
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
CREATE INDEX IF NOT EXISTS idx_user_skills_user_level ON user_skills(user_id, level DESC);
CREATE INDEX IF NOT EXISTS idx_user_skills_user_state ON user_skills(user_id, state);
CREATE INDEX IF NOT EXISTS idx_user_skills_stale ON user_skills(is_stale) WHERE is_stale = true;
CREATE INDEX IF NOT EXISTS idx_user_skills_emerging ON user_skills(is_emerging) WHERE is_emerging = true;
CREATE INDEX IF NOT EXISTS idx_user_skills_updated ON user_skills(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_skills_metadata ON user_skills USING GIN(metadata jsonb_path_ops);

-- 2.2 user_skill_evidence
CREATE TABLE IF NOT EXISTS user_skill_evidence (
    evidence_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_skill_id       UUID NOT NULL REFERENCES user_skills(user_skill_id) ON DELETE CASCADE,
    user_id             UUID NOT NULL,
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
) PARTITION BY RANGE (collected_at);
CREATE INDEX IF NOT EXISTS idx_evidence_user_skill ON user_skill_evidence(user_skill_id);
CREATE INDEX IF NOT EXISTS idx_evidence_user ON user_skill_evidence(user_id);
CREATE INDEX IF NOT EXISTS idx_evidence_source ON user_skill_evidence(source_type);
CREATE INDEX IF NOT EXISTS idx_evidence_state ON user_skill_evidence(state);
CREATE INDEX IF NOT EXISTS idx_evidence_quality ON user_skill_evidence(quality_score DESC);
CREATE INDEX IF NOT EXISTS idx_evidence_trust ON user_skill_evidence(trust_score DESC);
CREATE INDEX IF NOT EXISTS idx_evidence_weight ON user_skill_evidence(weight DESC);
CREATE INDEX IF NOT EXISTS idx_evidence_collected ON user_skill_evidence(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_evidence_expires ON user_skill_evidence(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_evidence_metadata ON user_skill_evidence USING GIN(metadata jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_evidence_user_state ON user_skill_evidence(user_id, state);
CREATE INDEX IF NOT EXISTS idx_evidence_user_source ON user_skill_evidence(user_id, source_type);

-- 2.3 user_skill_targets
CREATE TABLE IF NOT EXISTS user_skill_targets (
    target_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_skill_id       UUID NOT NULL REFERENCES user_skills(user_skill_id) ON DELETE CASCADE,
    user_id             UUID NOT NULL,
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
CREATE INDEX IF NOT EXISTS idx_targets_user_skill ON user_skill_targets(user_skill_id);
CREATE INDEX IF NOT EXISTS idx_targets_user ON user_skill_targets(user_id);
CREATE INDEX IF NOT EXISTS idx_targets_status ON user_skill_targets(status);
CREATE INDEX IF NOT EXISTS idx_targets_priority ON user_skill_targets(priority DESC);
CREATE INDEX IF NOT EXISTS idx_targets_date ON user_skill_targets(target_date) WHERE target_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_targets_active_user ON user_skill_targets(user_id) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_targets_gap ON user_skill_targets(gap_size DESC) WHERE status IN ('active', 'in_progress');
ALTER TABLE user_skill_targets ADD CONSTRAINT IF NOT EXISTS no_overlapping_active_targets
    EXCLUDE USING gist (
        user_skill_id WITH =,
        daterange((TO_TIMESTAMP(created_at / 1000))::DATE, COALESCE(target_date, 'infinity'::date), '[]'::TEXT) WITH &&
    ) WHERE (status = 'active' OR status = 'in_progress');

-- 2.4 user_skill_assessments
CREATE TABLE IF NOT EXISTS user_skill_assessments (
    assessment_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_skill_id       UUID NOT NULL REFERENCES user_skills(user_skill_id) ON DELETE CASCADE,
    user_id             UUID NOT NULL,
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
CREATE INDEX IF NOT EXISTS idx_assessments_user_skill ON user_skill_assessments(user_skill_id);
CREATE INDEX IF NOT EXISTS idx_assessments_user ON user_skill_assessments(user_id);
CREATE INDEX IF NOT EXISTS idx_assessments_type ON user_skill_assessments(assessment_type);
CREATE INDEX IF NOT EXISTS idx_assessments_status ON user_skill_assessments(status);
CREATE INDEX IF NOT EXISTS idx_assessments_completed ON user_skill_assessments(completed_at DESC) WHERE completed_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_assessments_level ON user_skill_assessments(level_achieved DESC);

-- 2.5 user_skill_versions
CREATE TABLE IF NOT EXISTS user_skill_versions (
    version_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_skill_id       UUID NOT NULL REFERENCES user_skills(user_skill_id) ON DELETE CASCADE,
    user_id             UUID NOT NULL,
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
    CONSTRAINT unique_version_per_skill UNIQUE (user_skill_id, version_number)
) PARTITION BY RANGE (created_at);
CREATE INDEX IF NOT EXISTS idx_versions_user_skill ON user_skill_versions(user_skill_id);
CREATE INDEX IF NOT EXISTS idx_versions_user ON user_skill_versions(user_id);
CREATE INDEX IF NOT EXISTS idx_versions_type ON user_skill_versions(change_type);
CREATE INDEX IF NOT EXISTS idx_versions_created ON user_skill_versions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_versions_changed_by ON user_skill_versions(changed_by);

-- =============================================================
-- GROUP 3: INTELLIGENCE & SUPPORTING (11 tables)
-- =============================================================

-- 3.1 skill_market_data
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

-- 3.2 skill_income_data
CREATE TABLE IF NOT EXISTS skill_income_data (
    income_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    source              TEXT NOT NULL CHECK (source IN (
        'employment','freelance','consulting','content','product',
        'agency','teaching','opensource','digital','affiliate'
    )),
    level               INT NOT NULL CHECK (level >= 0 AND level <= 5),
    p10 INT CHECK (p10 >= 0), p25 INT CHECK (p25 >= 0),
    p50 INT CHECK (p50 >= 0), p75 INT CHECK (p75 >= 0), p90 INT CHECK (p90 >= 0),
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
CREATE INDEX IF NOT EXISTS idx_income_skill_source ON skill_income_data(skill_id, source);
CREATE INDEX IF NOT EXISTS idx_income_median ON skill_income_data(p50 DESC);

-- 3.3 skill_certifications
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
        name WITH =, provider WITH =, level_mapped WITH =
    )
);
CREATE INDEX IF NOT EXISTS idx_certs_skill ON skill_certifications(skill_id);
CREATE INDEX IF NOT EXISTS idx_certs_category ON skill_certifications(category_id);
CREATE INDEX IF NOT EXISTS idx_certs_provider ON skill_certifications(provider);
CREATE INDEX IF NOT EXISTS idx_certs_level ON skill_certifications(level_mapped);
CREATE INDEX IF NOT EXISTS idx_certs_verified ON skill_certifications(is_verified) WHERE is_verified = true;

-- 3.4 skill_projects (junction)
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

-- 3.5 skill_roadmaps (junction)
CREATE TABLE IF NOT EXISTS skill_roadmaps (
    roadmap_id          UUID NOT NULL REFERENCES skill_roadmap_definitions(roadmap_id) ON DELETE CASCADE,
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    phase               TEXT NOT NULL CHECK (phase IN ('foundation','core','intermediate','advanced','expert','optional')),
    sort_order          INT NOT NULL DEFAULT 0,
    target_level        INT NOT NULL CHECK (target_level >= 0 AND target_level <= 5),
    estimated_hours     INT,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    PRIMARY KEY (roadmap_id, skill_id)
);
CREATE INDEX IF NOT EXISTS idx_roadmaps_skill ON skill_roadmaps(skill_id);
CREATE INDEX IF NOT EXISTS idx_roadmaps_phase ON skill_roadmaps(phase);
CREATE INDEX IF NOT EXISTS idx_roadmaps_order ON skill_roadmaps(roadmap_id, sort_order);

-- 3.6 skill_opportunities (junction)
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

-- 3.7 skill_topics
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

-- 3.8 skill_resources
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
CREATE INDEX IF NOT EXISTS idx_resources_free ON skill_resources(is_free) WHERE is_free = true;

-- 3.9 skill_learning_paths
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
CREATE INDEX IF NOT EXISTS idx_paths_ai ON skill_learning_paths(is_ai_generated) WHERE is_ai_generated = true;

-- 3.10 skill_ai_recommendations
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
CREATE INDEX IF NOT EXISTS idx_recommendations_accepted ON skill_ai_recommendations(accepted) WHERE accepted IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_recommendations_expires ON skill_ai_recommendations(expires_at) WHERE expires_at IS NOT NULL;

-- 3.11 skill_user_activity_log
CREATE TABLE IF NOT EXISTS skill_user_activity_log (
    activity_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL,
    activity_type       TEXT NOT NULL CHECK (activity_type IN (
        'skill_added','level_changed','evidence_submitted','assessment_taken',
        'target_set','target_achieved','recommendation_viewed',
        'recommendation_accepted','skill_archived','skill_deprecated',
        'skill_tree_viewed','dashboard_viewed','market_data_viewed',
        'income_data_viewed','career_readiness_viewed'
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

-- =============================================================
-- GROUP 4: AUDIT, EVENTS & ANALYTICS (10 tables)
-- =============================================================

-- 4.1 skill_audit_log
CREATE TABLE IF NOT EXISTS skill_audit_log (
    audit_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name          TEXT NOT NULL,
    record_id           UUID NOT NULL,
    user_id             UUID,
    action              TEXT NOT NULL CHECK (action IN ('INSERT','UPDATE','DELETE','TRUNCATE','SOFT_DELETE','RESTORE')),
    old_data            JSONB,
    new_data            JSONB,
    changed_fields      TEXT[],
    change_reason       TEXT,
    ip_address          TEXT,
    user_agent          TEXT,
    request_id          TEXT,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
) PARTITION BY RANGE (created_at);
CREATE INDEX IF NOT EXISTS idx_audit_table ON skill_audit_log(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_record ON skill_audit_log(record_id);
CREATE INDEX IF NOT EXISTS idx_audit_user ON skill_audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON skill_audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_created ON skill_audit_log(created_at DESC);
COMMENT ON TABLE skill_audit_log IS 'Immutable append-only audit log. Partitioned monthly by created_at.';

-- 4.2 skill_taxonomy_history
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

-- 4.3 skill_user_skill_history
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
CREATE INDEX IF NOT EXISTS idx_user_skill_history_created ON skill_user_skill_history(created_at DESC);

-- 4.4 skill_market_history
CREATE TABLE IF NOT EXISTS skill_market_history (
    market_history_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    demand_score        INT,
    growth_score        REAL,
    salary_median       INT,
    competition_score   INT,
    future_relevance    REAL,
    skill_health        REAL,
    snapshot_source     TEXT NOT NULL DEFAULT 'automated',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
);
CREATE INDEX IF NOT EXISTS idx_market_history_skill ON skill_market_history(skill_id);
CREATE INDEX IF NOT EXISTS idx_market_history_created ON skill_market_history(created_at DESC);

-- 4.5 skill_events
CREATE TABLE IF NOT EXISTS skill_events (
    event_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type          TEXT NOT NULL,
    event_version       TEXT NOT NULL DEFAULT '1.0',
    aggregate_type      TEXT NOT NULL,
    aggregate_id        UUID NOT NULL,
    user_id             UUID,
    data                JSONB NOT NULL,
    metadata            JSONB NOT NULL DEFAULT '{}',
    correlation_id      UUID,
    causation_id        UUID,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
) PARTITION BY RANGE (created_at);
CREATE INDEX IF NOT EXISTS idx_events_type ON skill_events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_aggregate ON skill_events(aggregate_type, aggregate_id);
CREATE INDEX IF NOT EXISTS idx_events_user ON skill_events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_created ON skill_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_correlation ON skill_events(correlation_id);
ALTER TABLE skill_events ADD COLUMN IF NOT EXISTS event_version_int INT DEFAULT 1;
COMMENT ON TABLE skill_events IS 'Event sourcing bus. Partitioned monthly by created_at.';

-- 4.6 skill_event_outbox
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
    scheduled_at        BIGINT,
    processed_at        BIGINT,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
);
CREATE INDEX IF NOT EXISTS idx_outbox_status ON skill_event_outbox(status) WHERE status IN ('pending','failed');
CREATE INDEX IF NOT EXISTS idx_outbox_scheduled ON skill_event_outbox(scheduled_at) WHERE scheduled_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_outbox_created ON skill_event_outbox(created_at);

-- 4.7 skill_webhook_queue
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
    last_error          TEXT,
    last_http_status    INT,
    scheduled_at        BIGINT,
    delivered_at        BIGINT,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
) PARTITION BY RANGE (created_at);
CREATE INDEX IF NOT EXISTS idx_webhook_status ON skill_webhook_queue(status) WHERE status IN ('pending','failed');
CREATE INDEX IF NOT EXISTS idx_webhook_subscription ON skill_webhook_queue(subscription_id);
CREATE INDEX IF NOT EXISTS idx_webhook_scheduled ON skill_webhook_queue(scheduled_at) WHERE scheduled_at IS NOT NULL;
COMMENT ON TABLE skill_webhook_queue IS 'Webhook delivery queue. Partitioned daily by created_at.';

-- 4.8 skill_event_subscriptions
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

-- 4.9 skill_analytics_snapshots
CREATE TABLE IF NOT EXISTS skill_analytics_snapshots (
    snapshot_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL,
    snapshot_date       DATE NOT NULL,
    avg_skill_level     REAL,
    skill_count         INT,
    readiness_score     REAL,
    learning_velocity   REAL,
    diversification_score REAL,
    income_per_hour     REAL,
    market_alignment    REAL,
    emerging_coverage   INT,
    milestone_completion REAL,
    evidence_ratio      REAL,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_user_snapshot_date UNIQUE (user_id, snapshot_date)
) PARTITION BY RANGE (snapshot_date);
CREATE INDEX IF NOT EXISTS idx_snapshots_user ON skill_analytics_snapshots(user_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_date ON skill_analytics_snapshots(snapshot_date DESC);
CREATE INDEX IF NOT EXISTS idx_snapshots_user_date ON skill_analytics_snapshots(user_id, snapshot_date DESC);
COMMENT ON TABLE skill_analytics_snapshots IS 'Daily analytics snapshots. Partitioned quarterly by snapshot_date.';

-- 4.10 skill_forecasts
CREATE TABLE IF NOT EXISTS skill_forecasts (
    forecast_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    metric              TEXT NOT NULL CHECK (metric IN ('demand','growth','salary','competition','future_relevance','skill_health')),
    forecast_date       DATE NOT NULL,
    predicted_value     REAL NOT NULL,
    confidence_lower    REAL,
    confidence_upper    REAL,
    model_version       TEXT NOT NULL DEFAULT '1.0',
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_forecast UNIQUE (skill_id, metric, forecast_date)
);
CREATE INDEX IF NOT EXISTS idx_forecasts_skill ON skill_forecasts(skill_id);
CREATE INDEX IF NOT EXISTS idx_forecasts_metric ON skill_forecasts(metric);
CREATE INDEX IF NOT EXISTS idx_forecasts_date ON skill_forecasts(forecast_date);
CREATE INDEX IF NOT EXISTS idx_forecasts_skill_metric ON skill_forecasts(skill_id, metric);

-- =============================================================
-- NOTIFY TRIGGERS
-- =============================================================

CREATE OR REPLACE FUNCTION fn_notify_taxonomy_change()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('taxonomy_changed', jsonb_build_object(
        'table', TG_TABLE_NAME, 'operation', TG_OP,
        'changed_at', EXTRACT(EPOCH FROM NOW()) * 1000
    )::TEXT);
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql STABLE;

CREATE TRIGGER trg_skills_notify AFTER INSERT OR UPDATE OR DELETE ON skills
    FOR EACH ROW EXECUTE FUNCTION fn_notify_taxonomy_change();
CREATE TRIGGER trg_categories_notify AFTER INSERT OR UPDATE OR DELETE ON skill_categories
    FOR EACH ROW EXECUTE FUNCTION fn_notify_taxonomy_change();

-- =============================================================
-- PARTITION CHILDREN (2026 Q3 + Q4)
-- =============================================================

-- skill_audit_log: monthly by created_at
CREATE TABLE IF NOT EXISTS skill_audit_log_2026_q3 PARTITION OF skill_audit_log
    FOR VALUES FROM (1767225600000) TO (1775174400000);
CREATE TABLE IF NOT EXISTS skill_audit_log_2026_q4 PARTITION OF skill_audit_log
    FOR VALUES FROM (1775174400000) TO (1783123200000);

-- user_skill_evidence: monthly by collected_at
CREATE TABLE IF NOT EXISTS user_skill_evidence_2026_q3 PARTITION OF user_skill_evidence
    FOR VALUES FROM (1767225600000) TO (1775174400000);
CREATE TABLE IF NOT EXISTS user_skill_evidence_2026_q4 PARTITION OF user_skill_evidence
    FOR VALUES FROM (1775174400000) TO (1783123200000);

-- user_skill_versions: monthly by created_at
CREATE TABLE IF NOT EXISTS user_skill_versions_2026_q3 PARTITION OF user_skill_versions
    FOR VALUES FROM (1767225600000) TO (1775174400000);
CREATE TABLE IF NOT EXISTS user_skill_versions_2026_q4 PARTITION OF user_skill_versions
    FOR VALUES FROM (1775174400000) TO (1783123200000);

-- skill_events: monthly by created_at
CREATE TABLE IF NOT EXISTS skill_events_2026_q3 PARTITION OF skill_events
    FOR VALUES FROM (1767225600000) TO (1775174400000);
CREATE TABLE IF NOT EXISTS skill_events_2026_q4 PARTITION OF skill_events
    FOR VALUES FROM (1775174400000) TO (1783123200000);

-- skill_user_activity_log: monthly by created_at
CREATE TABLE IF NOT EXISTS skill_user_activity_log_2026_q3 PARTITION OF skill_user_activity_log
    FOR VALUES FROM (1767225600000) TO (1775174400000);
CREATE TABLE IF NOT EXISTS skill_user_activity_log_2026_q4 PARTITION OF skill_user_activity_log
    FOR VALUES FROM (1775174400000) TO (1783123200000);

-- skill_webhook_queue: daily by created_at
CREATE TABLE IF NOT EXISTS skill_webhook_queue_2026_q3 PARTITION OF skill_webhook_queue
    FOR VALUES FROM (1767225600000) TO (1775174400000);
CREATE TABLE IF NOT EXISTS skill_webhook_queue_2026_q4 PARTITION OF skill_webhook_queue
    FOR VALUES FROM (1775174400000) TO (1783123200000);

-- skill_analytics_snapshots: quarterly by snapshot_date (DATE type)
CREATE TABLE IF NOT EXISTS skill_analytics_snapshots_2026_q3 PARTITION OF skill_analytics_snapshots
    FOR VALUES FROM ('2026-07-01') TO ('2026-10-01');
CREATE TABLE IF NOT EXISTS skill_analytics_snapshots_2026_q4 PARTITION OF skill_analytics_snapshots
    FOR VALUES FROM ('2026-10-01') TO ('2027-01-01');

-- =============================================================
-- SECURITY: ROLES, RLS, ENCRYPTION
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

CREATE OR REPLACE FUNCTION skill_is_admin() RETURNS BOOLEAN AS $$
    BEGIN RETURN pg_has_role(current_user, 'skill_admin', 'member'); END;
$$ LANGUAGE plpgsql STABLE;

CREATE OR REPLACE FUNCTION skill_is_auditor() RETURNS BOOLEAN AS $$
    BEGIN RETURN pg_has_role(current_user, 'skill_auditor', 'member'); END;
$$ LANGUAGE plpgsql STABLE;

-- PII encryption helpers
CREATE OR REPLACE FUNCTION skill_encrypt_pii(plaintext TEXT) RETURNS BYTEA AS $$
DECLARE enc_key TEXT;
BEGIN
    enc_key := current_setting('app.encryption_key', true);
    IF enc_key IS NULL THEN RETURN convert_to(plaintext, 'UTF8'); END IF;
    RETURN pgp_sym_encrypt(plaintext, enc_key);
END;
$$ LANGUAGE plpgsql STABLE;

CREATE OR REPLACE FUNCTION skill_decrypt_pii(ciphertext BYTEA) RETURNS TEXT AS $$
DECLARE enc_key TEXT;
BEGIN
    enc_key := current_setting('app.encryption_key', true);
    IF enc_key IS NULL THEN RETURN convert_from(ciphertext, 'UTF8'); END IF;
    RETURN pgp_sym_decrypt(ciphertext, enc_key);
END;
$$ LANGUAGE plpgsql STABLE;

-- Audit trigger function
CREATE OR REPLACE FUNCTION skill_audit_trigger_func() RETURNS TRIGGER AS $$
DECLARE
    audit_row skill_audit_log%ROWTYPE;
BEGIN
    audit_row.table_name := TG_TABLE_NAME;
    audit_row.record_id := COALESCE(NEW.user_skill_id, OLD.user_skill_id, NEW.skill_id, OLD.skill_id, NEW.assessment_id, OLD.assessment_id);
    audit_row.user_id := COALESCE(NEW.user_id, OLD.user_id, auth.uid());
    audit_row.action := TG_OP;
    IF TG_OP = 'INSERT' THEN
        audit_row.new_data := row_to_json(NEW)::JSONB;
    ELSIF TG_OP = 'UPDATE' THEN
        audit_row.old_data := row_to_json(OLD)::JSONB;
        audit_row.new_data := row_to_json(NEW)::JSONB;
        SELECT array_agg(k) INTO audit_row.changed_fields
        FROM jsonb_object_keys(row_to_json(NEW)::JSONB) k
        WHERE row_to_json(OLD)::JSONB->>k IS DISTINCT FROM row_to_json(NEW)::JSONB->>k;
    ELSIF TG_OP = 'DELETE' THEN
        audit_row.old_data := row_to_json(OLD)::JSONB;
    END IF;
    INSERT INTO skill_audit_log VALUES (audit_row.*);
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Attach audit triggers to user-facing tables
CREATE TRIGGER trg_skills_audit AFTER INSERT OR UPDATE OR DELETE ON skills FOR EACH ROW EXECUTE FUNCTION skill_audit_trigger_func();
CREATE TRIGGER trg_skill_categories_audit AFTER INSERT OR UPDATE OR DELETE ON skill_categories FOR EACH ROW EXECUTE FUNCTION skill_audit_trigger_func();
CREATE TRIGGER trg_user_skills_audit AFTER INSERT OR UPDATE OR DELETE ON user_skills FOR EACH ROW EXECUTE FUNCTION skill_audit_trigger_func();
CREATE TRIGGER trg_user_skill_evidence_audit AFTER INSERT OR UPDATE OR DELETE ON user_skill_evidence FOR EACH ROW EXECUTE FUNCTION skill_audit_trigger_func();
CREATE TRIGGER trg_user_skill_targets_audit AFTER INSERT OR UPDATE OR DELETE ON user_skill_targets FOR EACH ROW EXECUTE FUNCTION skill_audit_trigger_func();
CREATE TRIGGER trg_user_skill_assessments_audit AFTER INSERT OR UPDATE OR DELETE ON user_skill_assessments FOR EACH ROW EXECUTE FUNCTION skill_audit_trigger_func();
CREATE TRIGGER trg_skill_market_data_audit AFTER INSERT OR UPDATE OR DELETE ON skill_market_data FOR EACH ROW EXECUTE FUNCTION skill_audit_trigger_func();
CREATE TRIGGER trg_skill_relationships_audit AFTER INSERT OR UPDATE OR DELETE ON skill_relationships FOR EACH ROW EXECUTE FUNCTION skill_audit_trigger_func();
CREATE TRIGGER trg_skill_certifications_audit AFTER INSERT OR UPDATE OR DELETE ON skill_certifications FOR EACH ROW EXECUTE FUNCTION skill_audit_trigger_func();

-- Notify trigger for audit events
CREATE OR REPLACE FUNCTION skill_notify_audit_event() RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('audit_event', jsonb_build_object(
        'table', TG_TABLE_NAME, 'action', TG_OP,
        'record_id', NEW.record_id, 'user_id', NEW.user_id
    )::TEXT);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER trg_audit_log_notify AFTER INSERT ON skill_audit_log
    FOR EACH ROW EXECUTE FUNCTION skill_notify_audit_event();

-- Tenant ID + RLS on all tables
DO $$ DECLARE tbl TEXT; BEGIN
    FOREACH tbl IN ARRAY ARRAY[
        'skill_categories','skills','skill_relationships','tags','skill_tags',
        'skill_external_mappings','skill_roadmap_definitions',
        'user_skills','user_skill_evidence','user_skill_targets','user_skill_assessments','user_skill_versions',
        'skill_market_data','skill_income_data','skill_certifications',
        'skill_projects','skill_roadmaps','skill_opportunities',
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

-- Encrypted PII columns
ALTER TABLE skill_external_mappings ADD COLUMN IF NOT EXISTS external_credentials BYTEA;
ALTER TABLE skill_event_subscriptions ADD COLUMN IF NOT EXISTS encrypted_secret BYTEA;
ALTER TABLE user_skill_evidence ADD COLUMN IF NOT EXISTS encrypted_description BYTEA;

-- Tenant indexes
CREATE INDEX IF NOT EXISTS idx_skill_categories_tenant ON skill_categories(tenant_id);
CREATE INDEX IF NOT EXISTS idx_skills_tenant ON skills(tenant_id);
CREATE INDEX IF NOT EXISTS idx_user_skills_tenant ON user_skills(tenant_id);

-- RLS policies for core taxonomy (role-based read/write)
CREATE POLICY admin_all_skill_categories ON skill_categories FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY manager_all_skill_categories ON skill_categories FOR ALL TO skill_manager USING (true) WITH CHECK (true);
CREATE POLICY user_sel_skill_categories ON skill_categories FOR SELECT TO skill_user USING (true);
CREATE POLICY viewer_sel_skill_categories ON skill_categories FOR SELECT TO skill_viewer USING (true);
CREATE POLICY auditor_sel_skill_categories ON skill_categories FOR SELECT TO skill_auditor USING (true);
CREATE POLICY api_all_skill_categories ON skill_categories FOR ALL TO skill_api USING (true) WITH CHECK (true);

CREATE POLICY admin_all_skills ON skills FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY manager_all_skills ON skills FOR ALL TO skill_manager USING (true) WITH CHECK (true);
CREATE POLICY user_sel_skills ON skills FOR SELECT TO skill_user USING (true);
CREATE POLICY viewer_sel_skills ON skills FOR SELECT TO skill_viewer USING (true);
CREATE POLICY auditor_sel_skills ON skills FOR SELECT TO skill_auditor USING (true);
CREATE POLICY api_all_skills ON skills FOR ALL TO skill_api USING (true) WITH CHECK (true);

CREATE POLICY admin_all_skill_relationships ON skill_relationships FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY manager_all_skill_relationships ON skill_relationships FOR ALL TO skill_manager USING (true) WITH CHECK (true);
CREATE POLICY user_sel_skill_relationships ON skill_relationships FOR SELECT TO skill_user USING (true);
CREATE POLICY api_all_skill_relationships ON skill_relationships FOR ALL TO skill_api USING (true) WITH CHECK (true);

-- User-isolated tables (user sees only own data)
CREATE POLICY admin_all_user_skills ON user_skills FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY manager_sel_user_skills ON user_skills FOR SELECT TO skill_manager USING (true);
CREATE POLICY user_all_user_skills ON user_skills FOR ALL TO skill_user USING (user_id = skill_current_user_id()) WITH CHECK (user_id = skill_current_user_id());
CREATE POLICY api_all_user_skills ON user_skills FOR ALL TO skill_api USING (true) WITH CHECK (true);

CREATE POLICY admin_all_user_skill_evidence ON user_skill_evidence FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY user_all_user_skill_evidence ON user_skill_evidence FOR ALL TO skill_user USING (user_id = skill_current_user_id()) WITH CHECK (user_id = skill_current_user_id());
CREATE POLICY api_all_user_skill_evidence ON user_skill_evidence FOR ALL TO skill_api USING (true) WITH CHECK (true);

-- Market data: read for most, write for admin/scheduler
CREATE POLICY admin_all_market ON skill_market_data FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY manager_all_market ON skill_market_data FOR ALL TO skill_manager USING (true) WITH CHECK (true);
CREATE POLICY user_sel_market ON skill_market_data FOR SELECT TO skill_user USING (true);
CREATE POLICY scheduler_upd_market ON skill_market_data FOR UPDATE TO skill_scheduler USING (true);
CREATE POLICY scheduler_ins_market ON skill_market_data FOR INSERT TO skill_scheduler WITH CHECK (true);

-- Audit: admin/auditor read, api insert only
CREATE POLICY admin_all_audit ON skill_audit_log FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY auditor_sel_audit ON skill_audit_log FOR SELECT TO skill_auditor USING (true);
CREATE POLICY api_ins_audit ON skill_audit_log FOR INSERT TO skill_api WITH CHECK (true);

-- Events: append-only for api/user, read for admin/auditor
CREATE POLICY admin_all_events ON skill_events FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY auditor_sel_events ON skill_events FOR SELECT TO skill_auditor USING (true);
CREATE POLICY api_ins_events ON skill_events FOR INSERT TO skill_api WITH CHECK (true);
CREATE POLICY user_ins_events ON skill_events FOR INSERT TO skill_user WITH CHECK (true);

-- Column-level permissions
REVOKE UPDATE ON user_skill_evidence FROM PUBLIC;
GRANT UPDATE (title, description, url, metadata) ON user_skill_evidence TO authenticated;
REVOKE DELETE ON skill_audit_log FROM PUBLIC;
REVOKE DELETE ON skill_taxonomy_history FROM PUBLIC;
REVOKE DELETE ON skill_events FROM PUBLIC;

-- Statement timeouts
ALTER ROLE skill_user SET statement_timeout = '30s';
ALTER ROLE skill_api SET statement_timeout = '60s';
ALTER ROLE skill_scheduler SET statement_timeout = '120s';
ALTER ROLE skill_analytics SET statement_timeout = '120s';

-- =============================================================
-- MATERIALIZED VIEWS (7 views)
-- =============================================================

-- MV 1: User proficiency
DROP MATERIALIZED VIEW IF EXISTS mv_skill_user_proficiency CASCADE;
CREATE MATERIALIZED VIEW mv_skill_user_proficiency AS
SELECT us.user_id, us.tenant_id,
    COUNT(DISTINCT us.skill_id) AS total_skills_tracked,
    COUNT(DISTINCT us.skill_id) FILTER (WHERE us.level >= 3) AS skills_intermediate_plus,
    COUNT(DISTINCT us.skill_id) FILTER (WHERE us.level >= 4) AS skills_advanced_plus,
    ROUND(AVG(us.level)::NUMERIC, 2) AS avg_level,
    MAX(us.level) AS max_level,
    ROUND(AVG(us.confidence_score)::NUMERIC, 3) AS avg_confidence,
    ROUND(AVG(us.level_change_90d)::NUMERIC, 3) AS avg_velocity_90d,
    COUNT(DISTINCT ue.evidence_id) AS total_evidence_pieces,
    COUNT(DISTINCT ut.target_id) AS total_targets_set,
    COUNT(DISTINCT ut.target_id) FILTER (WHERE ut.status = 'achieved') AS targets_achieved,
    COUNT(DISTINCT ua.assessment_id) AS total_assessments,
    MAX(us.last_activity_at) AS last_activity,
    CURRENT_TIMESTAMP AS computed_at
FROM user_skills us
LEFT JOIN user_skill_evidence ue ON us.user_id = ue.user_id AND us.skill_id = ue.skill_id
LEFT JOIN user_skill_targets ut ON us.user_id = ut.user_id AND us.skill_id = ut.skill_id
LEFT JOIN user_skill_assessments ua ON us.user_id = ua.user_id AND us.skill_id = ua.skill_id
GROUP BY us.user_id, us.tenant_id WITH NO DATA;
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_proficiency_user ON mv_skill_user_proficiency(user_id, tenant_id);

-- MV 2: Market intelligence
DROP MATERIALIZED VIEW IF EXISTS mv_skill_market_intelligence CASCADE;
CREATE MATERIALIZED VIEW mv_skill_market_intelligence AS
SELECT s.skill_id, s.name AS skill_name, sc.name AS category_name,
    smd.demand_score, smd.growth_score, smd.salary_median, smd.skill_health,
    smd.job_postings_count, smd.data_freshness,
    sid.p50 AS median_income, scrt.certification_count,
    RANK() OVER (ORDER BY smd.demand_score DESC) AS demand_rank,
    RANK() OVER (ORDER BY smd.salary_median DESC) AS salary_rank
FROM skills s
JOIN skill_categories sc ON s.category_id = sc.category_id
LEFT JOIN skill_market_data smd ON s.skill_id = smd.skill_id
LEFT JOIN skill_income_data sid ON s.skill_id = sid.skill_id AND sid.source='employment' AND sid.level=3
LEFT JOIN LATERAL (SELECT COUNT(*) AS certification_count FROM skill_certifications sc2 WHERE sc2.skill_id = s.skill_id) scrt ON true
WHERE s.is_deprecated = false WITH NO DATA;
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_market_skill ON mv_skill_market_intelligence(skill_id);

-- MV 3: Learning velocity
DROP MATERIALIZED VIEW IF EXISTS mv_skill_learning_velocity CASCADE;
CREATE MATERIALIZED VIEW mv_skill_learning_velocity AS
SELECT ush.user_id, ush.tenant_id, ush.skill_id,
    COUNT(*) AS total_change_events,
    COALESCE(MAX(ush.proficiency_after) - MIN(ush.proficiency_before), 0) AS total_proficiency_gain,
    ROUND(AVG(ush.hours_since_last)::NUMERIC, 1) AS avg_hours_between_events,
    CURRENT_TIMESTAMP AS computed_at
FROM skill_user_skill_history ush
GROUP BY ush.user_id, ush.tenant_id, ush.skill_id WITH NO DATA;
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_velocity_user_skill ON mv_skill_learning_velocity(user_id, skill_id, tenant_id);

-- MV 4: Taxonomy health
DROP MATERIALIZED VIEW IF EXISTS mv_skill_taxonomy_health CASCADE;
CREATE MATERIALIZED VIEW mv_skill_taxonomy_health AS
SELECT sc.category_id, sc.name AS category_name,
    COUNT(DISTINCT s.skill_id) AS skill_count,
    COUNT(DISTINCT smd.skill_id) AS with_market_data,
    COUNT(DISTINCT sid.skill_id) AS with_income_data,
    CURRENT_TIMESTAMP AS computed_at
FROM skill_categories sc
LEFT JOIN skills s ON sc.category_id = s.category_id AND s.is_deprecated = false
LEFT JOIN skill_market_data smd ON s.skill_id = smd.skill_id
LEFT JOIN skill_income_data sid ON s.skill_id = sid.skill_id
GROUP BY sc.category_id, sc.name WITH NO DATA;
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_taxonomy_category ON mv_skill_taxonomy_health(category_id);

-- MV 5: AI effectiveness
DROP MATERIALIZED VIEW IF EXISTS mv_skill_ai_effectiveness CASCADE;
CREATE MATERIALIZED VIEW mv_skill_ai_effectiveness AS
SELECT user_id, tenant_id,
    COUNT(*) AS total_recommendations,
    COUNT(*) FILTER (WHERE accepted = true) AS accepted_count,
    ROUND((COUNT(*) FILTER (WHERE accepted = true)::NUMERIC / NULLIF(COUNT(*),0)) * 100, 1) AS acceptance_rate_pct,
    CURRENT_TIMESTAMP AS computed_at
FROM skill_ai_recommendations GROUP BY user_id, tenant_id WITH NO DATA;
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_ai_user ON mv_skill_ai_effectiveness(user_id, tenant_id);

-- MV 6: Activity heatmap
DROP MATERIALIZED VIEW IF EXISTS mv_skill_activity_heatmap CASCADE;
CREATE MATERIALIZED VIEW mv_skill_activity_heatmap AS
SELECT user_id, tenant_id,
    DATE_TRUNC('day', TO_TIMESTAMP(created_at / 1000))::DATE AS activity_date,
    EXTRACT(DOW FROM TO_TIMESTAMP(created_at / 1000))::INT AS day_of_week,
    EXTRACT(HOUR FROM TO_TIMESTAMP(created_at / 1000))::INT AS hour_of_day,
    activity_type, COUNT(*) AS event_count,
    CURRENT_TIMESTAMP AS computed_at
FROM skill_user_activity_log
GROUP BY user_id, tenant_id, activity_date, day_of_week, hour_of_day, activity_type WITH NO DATA;
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_activity_user_date ON mv_skill_activity_heatmap(user_id, tenant_id, activity_date, hour_of_day, activity_type);

-- MV 7: Roadmap progress
DROP MATERIALIZED VIEW IF EXISTS mv_skill_roadmap_progress CASCADE;
CREATE MATERIALIZED VIEW mv_skill_roadmap_progress AS
SELECT sr.roadmap_id, rd.name AS roadmap_name, rd.difficulty,
    sr.skill_id, s.name AS skill_name, sr.phase, sr.sort_order,
    sr.target_level, sr.estimated_hours
FROM skill_roadmaps sr
JOIN skill_roadmap_definitions rd ON sr.roadmap_id = rd.roadmap_id
JOIN skills s ON sr.skill_id = s.skill_id
ORDER BY sr.roadmap_id, sr.sort_order WITH NO DATA;
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_roadmap_entry ON mv_skill_roadmap_progress(roadmap_id, skill_id);

-- =============================================================
-- PG_CRON REFRESH (if extension available)
-- =============================================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_cron') THEN
        PERFORM cron.schedule('skill-proficiency-refresh', '*/5 6-23 * * *', 'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_user_proficiency');
        PERFORM cron.schedule('skill-market-refresh', '0 6,18 * * *', 'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_market_intelligence');
        PERFORM cron.schedule('skill-velocity-refresh', '0 * * * *', 'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_learning_velocity');
        PERFORM cron.schedule('skill-taxonomy-health-refresh', '0 0 * * *', 'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_taxonomy_health');
        PERFORM cron.schedule('skill-ai-effective-refresh', '*/30 * * * *', 'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_ai_effectiveness');
        PERFORM cron.schedule('skill-activity-heatmap-refresh', '0 * * * *', 'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_activity_heatmap');
        PERFORM cron.schedule('skill-roadmap-refresh', '*/15 * * * *', 'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_roadmap_progress');
    END IF;
END $$;

-- Manual refresh helper
CREATE OR REPLACE FUNCTION skill_refresh_all_materialized_views()
RETURNS JSONB AS $$
DECLARE results JSONB := '[]'::JSONB; start_ts TIMESTAMPTZ; end_ts TIMESTAMPTZ;
BEGIN
    start_ts := clock_timestamp();
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_user_proficiency;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_market_intelligence;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_roadmap_progress;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_learning_velocity;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_taxonomy_health;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_ai_effectiveness;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_skill_activity_heatmap;
    end_ts := clock_timestamp();
    results := results || jsonb_build_object('total_views', 7, 'duration_ms', ROUND(EXTRACT(EPOCH FROM (end_ts - start_ts))::NUMERIC * 1000, 0));
    RETURN results;
END;
$$ LANGUAGE plpgsql;

COMMIT;

-- ===== End: 000_skills_complete_ddl.sql =====

-- ===== Begin: 001_skills_core_taxonomy.sql =====
-- =============================================================
-- Migration 001: Skills Core Taxonomy
-- Creates: skill_categories, skills, skill_relationships,
--          tags, skill_tags, skill_external_mappings,
--          skill_roadmap_definitions
-- Extensions: pgcrypto, ltree, btree_gist
-- =============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "ltree";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- === 1. skill_categories ===
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

COMMENT ON TABLE skill_categories IS 'Hierarchical category tree for skills taxonomy with LTREE ancestry';

CREATE INDEX IF NOT EXISTS idx_categories_parent ON skill_categories(parent_category_id);
CREATE INDEX IF NOT EXISTS idx_categories_path ON skill_categories USING GIST(path);
CREATE INDEX IF NOT EXISTS idx_categories_sort ON skill_categories(sort_order);
CREATE INDEX IF NOT EXISTS idx_categories_active ON skill_categories(is_active) WHERE is_active = true;

-- === 2. skills ===
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

COMMENT ON TABLE skills IS 'Canonical skill definitions -- single source of truth for the skill taxonomy';
COMMENT ON COLUMN skills.skill_health IS 'Computed health metric: D*0.30 + G*0.20 + S*0.25 + (100-C)*0.10 + F*0.15';
COMMENT ON COLUMN skills.metadata IS 'Flexible metadata: icon, color, keywords, external_refs, custom_fields';

CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category_id);
CREATE INDEX IF NOT EXISTS idx_skills_slug ON skills(slug);
CREATE INDEX IF NOT EXISTS idx_skills_deprecated ON skills(is_deprecated) WHERE is_deprecated = false;
CREATE INDEX IF NOT EXISTS idx_skills_metadata ON skills USING GIN(metadata jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_skills_health ON skills(skill_health DESC) WHERE skill_health IS NOT NULL;

-- === 3. skill_relationships ===
CREATE TABLE IF NOT EXISTS skill_relationships (
    relationship_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_skill_id       UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    to_skill_id         UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    relationship_type   TEXT NOT NULL CHECK (relationship_type IN (
        'prerequisite', 'related_to', 'supersedes', 'variant_of',
        'similar_to', 'recommended_before', 'complementary', 'alternative'
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

COMMENT ON TABLE skill_relationships IS 'Typed, weighted, directed edges between skills for graph traversal';

CREATE INDEX IF NOT EXISTS idx_relationships_from ON skill_relationships(from_skill_id);
CREATE INDEX IF NOT EXISTS idx_relationships_to ON skill_relationships(to_skill_id);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON skill_relationships(relationship_type);
CREATE INDEX IF NOT EXISTS idx_relationships_weight ON skill_relationships(weight DESC);
CREATE INDEX IF NOT EXISTS idx_relationships_from_type ON skill_relationships(from_skill_id, relationship_type);

-- EXCLUDE constraint: prevent overlapping prerequisite relationships (Section 6.4 of architecture doc)
ALTER TABLE skill_relationships ADD CONSTRAINT IF NOT EXISTS no_overlapping_prereqs
EXCLUDE USING gist (
    from_skill_id WITH =,
    to_skill_id WITH =,
    relationship_type WITH =
);

COMMENT ON TABLE skill_relationships IS 'Typed, weighted, directed edges between skills for graph traversal with EXCLUDE constraint preventing duplicate relationship types between same skill pair';

-- === 4. tags ===
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

-- === 5. skill_tags (junction) ===
CREATE TABLE IF NOT EXISTS skill_tags (
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    tag_id              UUID NOT NULL REFERENCES tags(tag_id) ON DELETE CASCADE,
    PRIMARY KEY (skill_id, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_skill_tags_tag ON skill_tags(tag_id);

-- === 6. skill_external_mappings ===
CREATE TABLE IF NOT EXISTS skill_external_mappings (
    mapping_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    external_system     TEXT NOT NULL CHECK (external_system IN (
        'linkedin', 'esco', 'onet', 'workday', 'bamboohr',
        'cornerstone', 'docebo', 'greenhouse', 'lever', 'custom'
    )),
    external_id         TEXT NOT NULL,
    external_name       TEXT NOT NULL,
    mapping_type        TEXT NOT NULL DEFAULT 'exact' CHECK (mapping_type IN (
        'exact', 'broader', 'narrower', 'related', 'close_match'
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

-- === 7. skill_roadmap_definitions ===
CREATE TABLE IF NOT EXISTS skill_roadmap_definitions (
    roadmap_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                TEXT NOT NULL,
    description         TEXT NOT NULL DEFAULT '',
    target_skill_id     UUID REFERENCES skills(skill_id) ON DELETE SET NULL,
    difficulty          TEXT NOT NULL DEFAULT 'intermediate' CHECK (difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')),
    estimated_duration  TEXT,
    is_ai_generated     BOOLEAN NOT NULL DEFAULT false,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_roadmap_name UNIQUE (name)
);

CREATE INDEX IF NOT EXISTS idx_roadmap_defs_target ON skill_roadmap_definitions(target_skill_id);
CREATE INDEX IF NOT EXISTS idx_roadmap_defs_difficulty ON skill_roadmap_definitions(difficulty);

-- ===== End: 001_skills_core_taxonomy.sql =====

-- ===== Begin: 002_skills_user_tables.sql =====
-- =============================================================
-- Migration 002: Skills User Tables
-- Creates: user_skills, user_skill_evidence,
--          user_skill_targets, user_skill_assessments,
--          user_skill_versions
-- =============================================================

CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- === 1. user_skills ===
CREATE TABLE IF NOT EXISTS user_skills (
    user_skill_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL,
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE RESTRICT,
    level               INT NOT NULL DEFAULT 0 CHECK (level >= 0 AND level <= 5),
    state               TEXT NOT NULL DEFAULT 'learning' CHECK (state IN (
        'planned', 'learning', 'practicing', 'active', 'reviewing',
        'archived', 'deprecated'
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

COMMENT ON TABLE user_skills IS 'Per-user skill inventory with level, state, confidence, and velocity';
COMMENT ON COLUMN user_skills.level_change_90d IS 'Level delta over 90 days for velocity calculation';
COMMENT ON COLUMN user_skills.is_emerging IS 'Flag for rapidly growing skills';
COMMENT ON COLUMN user_skills.is_stale IS 'Flag for skills inactive 30+ days';

CREATE INDEX IF NOT EXISTS idx_user_skills_user ON user_skills(user_id);
CREATE INDEX IF NOT EXISTS idx_user_skills_skill ON user_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_user_skills_level ON user_skills(level);
CREATE INDEX IF NOT EXISTS idx_user_skills_state ON user_skills(state);
CREATE INDEX IF NOT EXISTS idx_user_skills_user_level ON user_skills(user_id, level DESC);
CREATE INDEX IF NOT EXISTS idx_user_skills_user_state ON user_skills(user_id, state);
CREATE INDEX IF NOT EXISTS idx_user_skills_stale ON user_skills(is_stale) WHERE is_stale = true;
CREATE INDEX IF NOT EXISTS idx_user_skills_emerging ON user_skills(is_emerging) WHERE is_emerging = true;
CREATE INDEX IF NOT EXISTS idx_user_skills_updated ON user_skills(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_skills_metadata ON user_skills USING GIN(metadata jsonb_path_ops);

-- === 2. user_skill_evidence ===
CREATE TABLE IF NOT EXISTS user_skill_evidence (
    evidence_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_skill_id       UUID NOT NULL REFERENCES user_skills(user_skill_id) ON DELETE CASCADE,
    user_id             UUID NOT NULL,
    source_type         TEXT NOT NULL CHECK (source_type IN (
        'project', 'github', 'certification', 'hackathon', 'freelance',
        'opensource', 'assessment', 'work_experience', 'course', 'publication',
        'patent', 'award'
    )),
    state               TEXT NOT NULL DEFAULT 'raw' CHECK (state IN (
        'raw', 'pending_verification', 'verified', 'verified_auto',
        'verified_ai', 'verified_human', 'rejected', 'flagged', 'active', 'expired'
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
) PARTITION BY RANGE (collected_at);

COMMENT ON TABLE user_skill_evidence IS 'Evidence items shadow table -- denormalized for fast user-skill queries';
COMMENT ON COLUMN user_skill_evidence.signed_hash IS 'SHA-256 hash of evidence content for tamper detection';

CREATE INDEX IF NOT EXISTS idx_evidence_user_skill ON user_skill_evidence(user_skill_id);
CREATE INDEX IF NOT EXISTS idx_evidence_user ON user_skill_evidence(user_id);
CREATE INDEX IF NOT EXISTS idx_evidence_source ON user_skill_evidence(source_type);
CREATE INDEX IF NOT EXISTS idx_evidence_state ON user_skill_evidence(state);
CREATE INDEX IF NOT EXISTS idx_evidence_quality ON user_skill_evidence(quality_score DESC);
CREATE INDEX IF NOT EXISTS idx_evidence_trust ON user_skill_evidence(trust_score DESC);
CREATE INDEX IF NOT EXISTS idx_evidence_weight ON user_skill_evidence(weight DESC);
CREATE INDEX IF NOT EXISTS idx_evidence_collected ON user_skill_evidence(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_evidence_expires ON user_skill_evidence(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_evidence_metadata ON user_skill_evidence USING GIN(metadata jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_evidence_user_state ON user_skill_evidence(user_id, state);
CREATE INDEX IF NOT EXISTS idx_evidence_user_source ON user_skill_evidence(user_id, source_type);

-- === 3. user_skill_targets ===
CREATE TABLE IF NOT EXISTS user_skill_targets (
    target_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_skill_id       UUID NOT NULL REFERENCES user_skills(user_skill_id) ON DELETE CASCADE,
    user_id             UUID NOT NULL,
    target_level        INT NOT NULL CHECK (target_level >= 1 AND target_level <= 5),
    current_level       INT NOT NULL DEFAULT 0 CHECK (current_level >= 0 AND current_level <= 5),
    priority            TEXT NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    target_date         DATE,
    status              TEXT NOT NULL DEFAULT 'active' CHECK (status IN (
        'active', 'in_progress', 'achieved', 'paused', 'abandoned', 'expired'
    )),
    gap_size            INT GENERATED ALWAYS AS (target_level - current_level) STORED,
    progress_pct        REAL GENERATED ALWAYS AS (
        CASE WHEN target_level > 0
             THEN LEAST(1.0, current_level::REAL / target_level::REAL) * 100
             ELSE 0 END
    ) STORED,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT valid_target CHECK (target_level > current_level)
);

COMMENT ON TABLE user_skill_targets IS 'Career and learning targets with auto-computed gap and progress';

CREATE INDEX IF NOT EXISTS idx_targets_user_skill ON user_skill_targets(user_skill_id);
CREATE INDEX IF NOT EXISTS idx_targets_user ON user_skill_targets(user_id);
CREATE INDEX IF NOT EXISTS idx_targets_status ON user_skill_targets(status);
CREATE INDEX IF NOT EXISTS idx_targets_priority ON user_skill_targets(priority DESC);
CREATE INDEX IF NOT EXISTS idx_targets_date ON user_skill_targets(target_date) WHERE target_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_targets_active_user ON user_skill_targets(user_id) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_targets_gap ON user_skill_targets(gap_size DESC) WHERE status IN ('active', 'in_progress');

-- === 4. user_skill_assessments ===
CREATE TABLE IF NOT EXISTS user_skill_assessments (
    assessment_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_skill_id       UUID NOT NULL REFERENCES user_skills(user_skill_id) ON DELETE CASCADE,
    user_id             UUID NOT NULL,
    assessment_type     TEXT NOT NULL CHECK (assessment_type IN (
        'self', 'ai_evaluated', 'auto_mcq', 'peer_review',
        'human_review', 'project_evaluation', 'certification_equivalency'
    )),
    score               REAL CHECK (score >= 0.0 AND score <= 100.0),
    level_achieved      INT CHECK (level_achieved >= 0 AND level_achieved <= 5),
    confidence          REAL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    status              TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
        'pending', 'in_progress', 'completed', 'expired', 'invalidated'
    )),
    duration_seconds    INT,
    result_data         JSONB NOT NULL DEFAULT '{}',
    started_at          BIGINT,
    completed_at        BIGINT,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
);

COMMENT ON TABLE user_skill_assessments IS 'Assessment attempts and results with question-level result data';
COMMENT ON COLUMN user_skill_assessments.result_data IS 'Full response including question-level scores, timestamps, metadata';

CREATE INDEX IF NOT EXISTS idx_assessments_user_skill ON user_skill_assessments(user_skill_id);
CREATE INDEX IF NOT EXISTS idx_assessments_user ON user_skill_assessments(user_id);
CREATE INDEX IF NOT EXISTS idx_assessments_type ON user_skill_assessments(assessment_type);
CREATE INDEX IF NOT EXISTS idx_assessments_status ON user_skill_assessments(status);
CREATE INDEX IF NOT EXISTS idx_assessments_completed ON user_skill_assessments(completed_at DESC) WHERE completed_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_assessments_level ON user_skill_assessments(level_achieved DESC);

-- === 5. user_skill_versions ===
CREATE TABLE IF NOT EXISTS user_skill_versions (
    version_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_skill_id       UUID NOT NULL REFERENCES user_skills(user_skill_id) ON DELETE CASCADE,
    user_id             UUID NOT NULL,
    version_number      INT NOT NULL,
    change_type         TEXT NOT NULL CHECK (change_type IN (
        'created', 'level_changed', 'state_changed', 'evidence_added',
        'metadata_updated', 'archived', 'deprecated', 'restored'
    )),
    previous_state      JSONB NOT NULL,
    new_state           JSONB NOT NULL,
    changed_by          UUID NOT NULL,
    change_reason       TEXT,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_version_per_skill UNIQUE (user_skill_id, version_number)
) PARTITION BY RANGE (created_at);

COMMENT ON TABLE user_skill_versions IS 'Immutable version history of user_skill state changes';

CREATE INDEX IF NOT EXISTS idx_versions_user_skill ON user_skill_versions(user_skill_id);
CREATE INDEX IF NOT EXISTS idx_versions_user ON user_skill_versions(user_id);
CREATE INDEX IF NOT EXISTS idx_versions_type ON user_skill_versions(change_type);
CREATE INDEX IF NOT EXISTS idx_versions_created ON user_skill_versions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_versions_changed_by ON user_skill_versions(changed_by);

-- EXCLUDE constraint: prevent overlapping active targets per user_skill (Section 6.4)
ALTER TABLE user_skill_targets ADD CONSTRAINT IF NOT EXISTS no_overlapping_active_targets
EXCLUDE USING gist (
    user_skill_id WITH =,
    daterange(
        (TO_TIMESTAMP(created_at / 1000))::DATE,
        COALESCE(target_date, 'infinity'::date),
        '[]'::TEXT
    ) WITH &&
) WHERE (status = 'active' OR status = 'in_progress');

-- Partition children for user_skill_evidence (monthly by collected_at)
CREATE TABLE IF NOT EXISTS user_skill_evidence_2026_q3 PARTITION OF user_skill_evidence
    FOR VALUES FROM (1767225600000) TO (1775174400000);
CREATE TABLE IF NOT EXISTS user_skill_evidence_2026_q4 PARTITION OF user_skill_evidence
    FOR VALUES FROM (1775174400000) TO (1783123200000);

-- Partition children for user_skill_versions (monthly by created_at)
CREATE TABLE IF NOT EXISTS user_skill_versions_2026_q3 PARTITION OF user_skill_versions
    FOR VALUES FROM (1767225600000) TO (1775174400000);
CREATE TABLE IF NOT EXISTS user_skill_versions_2026_q4 PARTITION OF user_skill_versions
    FOR VALUES FROM (1775174400000) TO (1783123200000);

-- Comments
COMMENT ON TABLE user_skill_evidence IS 'Evidence items shadow table -- denormalized for fast user-skill queries. Partitioned monthly by collected_at.';
COMMENT ON TABLE user_skill_versions IS 'Immutable version history of user_skill state changes. Partitioned monthly by created_at.';

-- ===== End: 002_skills_user_tables.sql =====

-- ===== Begin: 003_skills_intelligence_supporting.sql =====
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

-- ===== End: 003_skills_intelligence_supporting.sql =====

-- ===== Begin: 004_skills_audit_events_analytics.sql =====
-- =============================================================
-- Migration 004: Skills Audit, Events & Analytics Tables
-- Creates: audit_log, taxonomy_history, user_skill_history,
--          market_history, events, event_outbox, webhook_queue,
--          event_subscriptions, analytics_snapshots, forecasts
-- =============================================================

-- === 1. skill_audit_log ===
CREATE TABLE IF NOT EXISTS skill_audit_log (
    audit_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name          TEXT NOT NULL,
    record_id           UUID NOT NULL,
    user_id             UUID,
    action              TEXT NOT NULL CHECK (action IN (
        'INSERT', 'UPDATE', 'DELETE', 'TRUNCATE', 'SOFT_DELETE', 'RESTORE'
    )),
    old_data            JSONB,
    new_data            JSONB,
    changed_fields      TEXT[],
    ip_address          TEXT,
    user_agent          TEXT,
    request_id          TEXT,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
) PARTITION BY RANGE (created_at);

COMMENT ON TABLE skill_audit_log IS 'Immutable append-only audit log for all skill entity state changes';

CREATE INDEX IF NOT EXISTS idx_audit_table ON skill_audit_log(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_record ON skill_audit_log(record_id);
CREATE INDEX IF NOT EXISTS idx_audit_user ON skill_audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON skill_audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_created ON skill_audit_log(created_at DESC);

-- Create initial partitions
CREATE TABLE IF NOT EXISTS skill_audit_log_2026_q3 PARTITION OF skill_audit_log
    FOR VALUES FROM (1767225600000) TO (1775174400000);
CREATE TABLE IF NOT EXISTS skill_audit_log_2026_q4 PARTITION OF skill_audit_log
    FOR VALUES FROM (1775174400000) TO (1783123200000);

-- === 2. skill_taxonomy_history ===
CREATE TABLE IF NOT EXISTS skill_taxonomy_history (
    history_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type         TEXT NOT NULL CHECK (entity_type IN ('skill', 'category', 'relationship', 'tag')),
    entity_id           UUID NOT NULL,
    version             INT NOT NULL,
    previous_state      JSONB NOT NULL,
    new_state           JSONB NOT NULL,
    change_type         TEXT NOT NULL CHECK (change_type IN (
        'created', 'updated', 'deprecated', 'restored', 'merged', 'split'
    )),
    changed_by          UUID,
    change_reason       TEXT,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_taxonomy_version UNIQUE (entity_type, entity_id, version)
);

CREATE INDEX IF NOT EXISTS idx_taxonomy_history_entity ON skill_taxonomy_history(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_taxonomy_history_created ON skill_taxonomy_history(created_at DESC);

-- === 3. skill_user_skill_history ===
CREATE TABLE IF NOT EXISTS skill_user_skill_history (
    history_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_skill_id       UUID NOT NULL,
    user_id             UUID NOT NULL,
    version             INT NOT NULL,
    previous_state      JSONB NOT NULL,
    new_state           JSONB NOT NULL,
    change_type         TEXT NOT NULL CHECK (change_type IN (
        'level_changed', 'state_changed', 'evidence_added', 'confidence_changed',
        'metadata_updated', 'archived', 'deprecated', 'restored'
    )),
    changed_by          UUID,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_user_skill_history_version UNIQUE (user_skill_id, version)
);

CREATE INDEX IF NOT EXISTS idx_user_skill_history_skill ON skill_user_skill_history(user_skill_id);
CREATE INDEX IF NOT EXISTS idx_user_skill_history_user ON skill_user_skill_history(user_id);
CREATE INDEX IF NOT EXISTS idx_user_skill_history_type ON skill_user_skill_history(change_type);
CREATE INDEX IF NOT EXISTS idx_user_skill_history_created ON skill_user_skill_history(created_at DESC);

-- === 4. skill_market_history ===
CREATE TABLE IF NOT EXISTS skill_market_history (
    market_history_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    demand_score        INT,
    growth_score        REAL,
    salary_median       INT,
    competition_score   INT,
    future_relevance    REAL,
    skill_health        REAL,
    snapshot_source     TEXT NOT NULL DEFAULT 'automated',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
);

CREATE INDEX IF NOT EXISTS idx_market_history_skill ON skill_market_history(skill_id);
CREATE INDEX IF NOT EXISTS idx_market_history_created ON skill_market_history(created_at DESC);

-- === 5. skill_events (event sourcing bus) ===
CREATE TABLE IF NOT EXISTS skill_events (
    event_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type          TEXT NOT NULL,
    event_version       TEXT NOT NULL DEFAULT '1.0',
    aggregate_type      TEXT NOT NULL,
    aggregate_id        UUID NOT NULL,
    user_id             UUID,
    data                JSONB NOT NULL,
    metadata            JSONB NOT NULL DEFAULT '{}',
    correlation_id      UUID,
    causation_id        UUID,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
) PARTITION BY RANGE (created_at);

COMMENT ON TABLE skill_events IS 'Event sourcing bus recording all domain events';

CREATE INDEX IF NOT EXISTS idx_events_type ON skill_events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_aggregate ON skill_events(aggregate_type, aggregate_id);
CREATE INDEX IF NOT EXISTS idx_events_user ON skill_events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_created ON skill_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_correlation ON skill_events(correlation_id);

CREATE TABLE IF NOT EXISTS skill_events_2026_q3 PARTITION OF skill_events
    FOR VALUES FROM (1767225600000) TO (1775174400000);
CREATE TABLE IF NOT EXISTS skill_events_2026_q4 PARTITION OF skill_events
    FOR VALUES FROM (1775174400000) TO (1783123200000);

-- === 6. skill_event_outbox ===
CREATE TABLE IF NOT EXISTS skill_event_outbox (
    outbox_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type          TEXT NOT NULL,
    aggregate_type      TEXT NOT NULL,
    aggregate_id        UUID NOT NULL,
    payload             JSONB NOT NULL,
    status              TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
        'pending', 'processing', 'delivered', 'failed', 'dead_letter'
    )),
    retry_count         INT NOT NULL DEFAULT 0,
    max_retries         INT NOT NULL DEFAULT 3,
    last_error          TEXT,
    scheduled_at        BIGINT,
    processed_at        BIGINT,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
);

CREATE INDEX IF NOT EXISTS idx_outbox_status ON skill_event_outbox(status) WHERE status IN ('pending', 'failed');
CREATE INDEX IF NOT EXISTS idx_outbox_scheduled ON skill_event_outbox(scheduled_at) WHERE scheduled_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_outbox_created ON skill_event_outbox(created_at);

-- === 7. skill_webhook_queue ===
CREATE TABLE IF NOT EXISTS skill_webhook_queue (
    webhook_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id     UUID NOT NULL,
    event_type          TEXT NOT NULL,
    payload             JSONB NOT NULL,
    url                 TEXT NOT NULL,
    headers             JSONB NOT NULL DEFAULT '{}',
    status              TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
        'pending', 'delivering', 'delivered', 'failed', 'dead_letter'
    )),
    retry_count         INT NOT NULL DEFAULT 0,
    max_retries         INT NOT NULL DEFAULT 5,
    last_error          TEXT,
    last_http_status    INT,
    scheduled_at        BIGINT,
    delivered_at        BIGINT,
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000)
);

CREATE INDEX IF NOT EXISTS idx_webhook_status ON skill_webhook_queue(status) WHERE status IN ('pending', 'failed');
CREATE INDEX IF NOT EXISTS idx_webhook_subscription ON skill_webhook_queue(subscription_id);
CREATE INDEX IF NOT EXISTS idx_webhook_scheduled ON skill_webhook_queue(scheduled_at) WHERE scheduled_at IS NOT NULL;

-- === 8. skill_event_subscriptions ===
CREATE TABLE IF NOT EXISTS skill_event_subscriptions (
    subscription_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                TEXT NOT NULL,
    url                 TEXT NOT NULL,
    event_types         TEXT[] NOT NULL DEFAULT '{}',
    headers             JSONB NOT NULL DEFAULT '{}',
    is_active           BOOLEAN NOT NULL DEFAULT true,
    secret              TEXT,
    retry_policy        JSONB NOT NULL DEFAULT '{"max_retries": 5, "backoff": "exponential", "initial_delay_ms": 1000}',
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    updated_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_subscription_url UNIQUE (name, url)
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_active ON skill_event_subscriptions(is_active) WHERE is_active = true;

-- === 9. skill_analytics_snapshots ===
CREATE TABLE IF NOT EXISTS skill_analytics_snapshots (
    snapshot_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL,
    snapshot_date       DATE NOT NULL,
    avg_skill_level     REAL,
    skill_count         INT,
    readiness_score     REAL,
    learning_velocity   REAL,
    diversification_score REAL,
    income_per_hour     REAL,
    market_alignment    REAL,
    emerging_coverage   INT,
    milestone_completion REAL,
    evidence_ratio      REAL,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_user_snapshot_date UNIQUE (user_id, snapshot_date)
);

CREATE INDEX IF NOT EXISTS idx_snapshots_user ON skill_analytics_snapshots(user_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_date ON skill_analytics_snapshots(snapshot_date DESC);
CREATE INDEX IF NOT EXISTS idx_snapshots_user_date ON skill_analytics_snapshots(user_id, snapshot_date DESC);

-- === 10. skill_forecasts ===
CREATE TABLE IF NOT EXISTS skill_forecasts (
    forecast_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id            UUID NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    metric              TEXT NOT NULL CHECK (metric IN (
        'demand', 'growth', 'salary', 'competition', 'future_relevance', 'skill_health'
    )),
    forecast_date       DATE NOT NULL,
    predicted_value     REAL NOT NULL,
    confidence_lower    REAL,
    confidence_upper    REAL,
    model_version       TEXT NOT NULL DEFAULT '1.0',
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          BIGINT NOT NULL DEFAULT (EXTRACT(EPOCH FROM NOW()) * 1000),
    CONSTRAINT unique_forecast UNIQUE (skill_id, metric, forecast_date)
);

CREATE INDEX IF NOT EXISTS idx_forecasts_skill ON skill_forecasts(skill_id);
CREATE INDEX IF NOT EXISTS idx_forecasts_metric ON skill_forecasts(metric);
CREATE INDEX IF NOT EXISTS idx_forecasts_date ON skill_forecasts(forecast_date);
CREATE INDEX IF NOT EXISTS idx_forecasts_skill_metric ON skill_forecasts(skill_id, metric);

-- === 11. Notify Trigger: Taxonomy Changes ===

CREATE OR REPLACE FUNCTION fn_notify_taxonomy_change()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('taxonomy_changed', jsonb_build_object(
        'table', TG_TABLE_NAME,
        'operation', TG_OP,
        'changed_at', EXTRACT(EPOCH FROM NOW()) * 1000
    )::TEXT);
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql STABLE;

CREATE TRIGGER trg_skills_notify AFTER INSERT OR UPDATE OR DELETE ON skills
    FOR EACH ROW EXECUTE FUNCTION fn_notify_taxonomy_change();
CREATE TRIGGER trg_categories_notify AFTER INSERT OR UPDATE OR DELETE ON skill_categories
    FOR EACH ROW EXECUTE FUNCTION fn_notify_taxonomy_change();

-- === 12. Extended Partitioning — Additional Partition Children ===

-- skill_webhook_queue: daily by created_at
CREATE TABLE IF NOT EXISTS skill_webhook_queue_2026_q3 PARTITION OF skill_webhook_queue
    FOR VALUES FROM (1767225600000) TO (1775174400000);
CREATE TABLE IF NOT EXISTS skill_webhook_queue_2026_q4 PARTITION OF skill_webhook_queue
    FOR VALUES FROM (1775174400000) TO (1783123200000);

-- skill_analytics_snapshots: quarterly by snapshot_date (DATE type)
CREATE TABLE IF NOT EXISTS skill_analytics_snapshots_2026_q3 PARTITION OF skill_analytics_snapshots
    FOR VALUES FROM ('2026-07-01') TO ('2026-10-01');
CREATE TABLE IF NOT EXISTS skill_analytics_snapshots_2026_q4 PARTITION OF skill_analytics_snapshots
    FOR VALUES FROM ('2026-10-01') TO ('2027-01-01');

-- === 13. Doc Compatibility: Add missing columns ===

ALTER TABLE skill_events ADD COLUMN IF NOT EXISTS event_version INT DEFAULT 1;

-- === 14. Improved Comments ===

COMMENT ON TABLE skill_events IS 'Event sourcing bus recording all domain events. Partitioned monthly by created_at.';
COMMENT ON TABLE skill_webhook_queue IS 'Webhook delivery queue. Partitioned daily by created_at.';
COMMENT ON TABLE skill_analytics_snapshots IS 'Daily analytics snapshots per user for trend analysis. Partitioned quarterly by snapshot_date.';

-- ===== End: 004_skills_audit_events_analytics.sql =====

-- ===== Begin: 005_skills_security_rls.sql =====
-- =============================================================
-- Migration 005: Skills Security — RLS Policies & Role-Based Access
-- Creates: 8 database roles, enables RLS on all 31 tables,
--          creates per-table policies for each role,
--          column-level encryption for PII fields,
--          tenant isolation via app.tenant_id
-- =============================================================

-- === 1. Create Custom Roles ===
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'skill_admin') THEN
        CREATE ROLE skill_admin;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'skill_manager') THEN
        CREATE ROLE skill_manager;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'skill_user') THEN
        CREATE ROLE skill_user;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'skill_auditor') THEN
        CREATE ROLE skill_auditor;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'skill_viewer') THEN
        CREATE ROLE skill_viewer;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'skill_api') THEN
        CREATE ROLE skill_api;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'skill_scheduler') THEN
        CREATE ROLE skill_scheduler;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'skill_analytics') THEN
        CREATE ROLE skill_analytics;
    END IF;
END $$;

-- === 2. Create Tenant/Audit Helper Functions ===

CREATE OR REPLACE FUNCTION skill_current_tenant_id()
RETURNS UUID AS $$
BEGIN
    RETURN NULLIF(current_setting('app.tenant_id', true), '')::UUID;
END;
$$ LANGUAGE plpgsql STABLE;

CREATE OR REPLACE FUNCTION skill_current_user_id()
RETURNS UUID AS $$
BEGIN
    RETURN NULLIF(current_setting('app.user_id', true), '')::UUID;
END;
$$ LANGUAGE plpgsql STABLE;

CREATE OR REPLACE FUNCTION skill_is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN pg_has_role(current_user, 'skill_admin', 'member');
END;
$$ LANGUAGE plpgsql STABLE;

CREATE OR REPLACE FUNCTION skill_is_auditor()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN pg_has_role(current_user, 'skill_auditor', 'member');
END;
$$ LANGUAGE plpgsql STABLE;

-- === 3. Add tenant_id to all multi-tenant tables ===

ALTER TABLE skill_categories ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skills ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_relationships ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE tags ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_tags ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_external_mappings ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_roadmap_definitions ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE user_skills ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE user_skill_evidence ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE user_skill_targets ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE user_skill_assessments ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE user_skill_versions ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_market_data ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_income_data ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_certifications ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_projects ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_roadmaps ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_opportunities ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_topics ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_resources ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_learning_paths ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_ai_recommendations ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_user_activity_log ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_audit_log ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_taxonomy_history ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_user_skill_history ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_market_history ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_events ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_event_outbox ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_webhook_queue ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_event_subscriptions ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_analytics_snapshots ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE skill_forecasts ADD COLUMN IF NOT EXISTS tenant_id UUID;

CREATE INDEX IF NOT EXISTS idx_skill_categories_tenant ON skill_categories(tenant_id);
CREATE INDEX IF NOT EXISTS idx_skills_tenant ON skills(tenant_id);
CREATE INDEX IF NOT EXISTS idx_user_skills_tenant ON user_skills(tenant_id);

-- === 4. Enable RLS on All Tables ===

ALTER TABLE skill_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_relationships ENABLE ROW LEVEL SECURITY;
ALTER TABLE tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_external_mappings ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_roadmap_definitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_skill_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_skill_targets ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_skill_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_skill_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_market_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_income_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_certifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_roadmaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_resources ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_learning_paths ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_ai_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_user_activity_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_taxonomy_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_user_skill_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_market_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_event_outbox ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_webhook_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_event_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_analytics_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_forecasts ENABLE ROW LEVEL SECURITY;

-- === 5. RLS Policies — Helper Templates ===
-- Pattern: {role}_{table}_{action}
-- Admin: full access to everything
-- Manager: CRUD on taxonomy, read on user data
-- User: CRUD on own records, read on taxonomy
-- Auditor: read-only on audit/history, read on taxonomy
-- Viewer: read-only on taxonomy
-- API: service account full access
-- Scheduler: write to event/analytics tables
-- Analytics: read-only on analytics snapshots

-- ==================== Core Taxonomy Tables ====================

-- skill_categories
CREATE POLICY admin_skill_categories_all ON skill_categories FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY manager_skill_categories_all ON skill_categories FOR ALL TO skill_manager USING (true) WITH CHECK (true);
CREATE POLICY user_skill_categories_select ON skill_categories FOR SELECT TO skill_user USING (true);
CREATE POLICY viewer_skill_categories_select ON skill_categories FOR SELECT TO skill_viewer USING (true);
CREATE POLICY auditor_skill_categories_select ON skill_categories FOR SELECT TO skill_auditor USING (true);
CREATE POLICY api_skill_categories_all ON skill_categories FOR ALL TO skill_api USING (true) WITH CHECK (true);

-- skills
CREATE POLICY admin_skills_all ON skills FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY manager_skills_all ON skills FOR ALL TO skill_manager USING (true) WITH CHECK (true);
CREATE POLICY user_skills_select ON skills FOR SELECT TO skill_user USING (true);
CREATE POLICY viewer_skills_select ON skills FOR SELECT TO skill_viewer USING (true);
CREATE POLICY auditor_skills_select ON skills FOR SELECT TO skill_auditor USING (true);
CREATE POLICY api_skills_all ON skills FOR ALL TO skill_api USING (true) WITH CHECK (true);

-- skill_relationships
CREATE POLICY admin_skill_relationships_all ON skill_relationships FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY manager_skill_relationships_all ON skill_relationships FOR ALL TO skill_manager USING (true) WITH CHECK (true);
CREATE POLICY user_skill_relationships_select ON skill_relationships FOR SELECT TO skill_user USING (true);
CREATE POLICY viewer_skill_relationships_select ON skill_relationships FOR SELECT TO skill_viewer USING (true);
CREATE POLICY api_skill_relationships_all ON skill_relationships FOR ALL TO skill_api USING (true) WITH CHECK (true);

-- tags
CREATE POLICY admin_tags_all ON tags FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY manager_tags_all ON tags FOR ALL TO skill_manager USING (true) WITH CHECK (true);
CREATE POLICY user_tags_select ON tags FOR SELECT TO skill_user USING (true);
CREATE POLICY viewer_tags_select ON tags FOR SELECT TO skill_viewer USING (true);
CREATE POLICY api_tags_all ON tags FOR ALL TO skill_api USING (true) WITH CHECK (true);

-- skill_tags
CREATE POLICY admin_skill_tags_all ON skill_tags FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY manager_skill_tags_all ON skill_tags FOR ALL TO skill_manager USING (true) WITH CHECK (true);
CREATE POLICY user_skill_tags_select ON skill_tags FOR SELECT TO skill_user USING (true);
CREATE POLICY api_skill_tags_all ON skill_tags FOR ALL TO skill_api USING (true) WITH CHECK (true);

-- skill_external_mappings
CREATE POLICY admin_skill_external_mappings_all ON skill_external_mappings FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY manager_skill_external_mappings_all ON skill_external_mappings FOR ALL TO skill_manager USING (true) WITH CHECK (true);
CREATE POLICY user_skill_external_mappings_select ON skill_external_mappings FOR SELECT TO skill_user USING (true);
CREATE POLICY api_skill_external_mappings_all ON skill_external_mappings FOR ALL TO skill_api USING (true) WITH CHECK (true);

-- skill_roadmap_definitions
CREATE POLICY admin_skill_roadmap_definitions_all ON skill_roadmap_definitions FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY manager_skill_roadmap_definitions_all ON skill_roadmap_definitions FOR ALL TO skill_manager USING (true) WITH CHECK (true);
CREATE POLICY user_skill_roadmap_definitions_select ON skill_roadmap_definitions FOR SELECT TO skill_user USING (true);
CREATE POLICY api_skill_roadmap_definitions_all ON skill_roadmap_definitions FOR ALL TO skill_api USING (true) WITH CHECK (true);

-- ==================== User Skills Tables ====================

-- user_skills: User isolation — can only see own records
CREATE POLICY admin_user_skills_all ON user_skills FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY manager_user_skills_select ON user_skills FOR SELECT TO skill_manager USING (true);
CREATE POLICY user_user_skills_all ON user_skills FOR ALL TO skill_user USING (user_id = skill_current_user_id()) WITH CHECK (user_id = skill_current_user_id());
CREATE POLICY api_user_skills_all ON user_skills FOR ALL TO skill_api USING (true) WITH CHECK (true);

-- user_skill_evidence: User isolation
CREATE POLICY admin_user_skill_evidence_all ON user_skill_evidence FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY manager_user_skill_evidence_select ON user_skill_evidence FOR SELECT TO skill_manager USING (true);
CREATE POLICY user_user_skill_evidence_all ON user_skill_evidence FOR ALL TO skill_user USING (user_id = skill_current_user_id()) WITH CHECK (user_id = skill_current_user_id());
CREATE POLICY api_user_skill_evidence_all ON user_skill_evidence FOR ALL TO skill_api USING (true) WITH CHECK (true);

-- user_skill_targets: User isolation
CREATE POLICY admin_user_skill_targets_all ON user_skill_targets FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY user_user_skill_targets_all ON user_skill_targets FOR ALL TO skill_user USING (user_id = skill_current_user_id()) WITH CHECK (user_id = skill_current_user_id());
CREATE POLICY api_user_skill_targets_all ON user_skill_targets FOR ALL TO skill_api USING (true) WITH CHECK (true);

-- user_skill_assessments: User isolation
CREATE POLICY admin_user_skill_assessments_all ON user_skill_assessments FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY user_user_skill_assessments_all ON user_skill_assessments FOR ALL TO skill_user USING (user_id = skill_current_user_id()) WITH CHECK (user_id = skill_current_user_id());
CREATE POLICY api_user_skill_assessments_all ON user_skill_assessments FOR ALL TO skill_api USING (true) WITH CHECK (true);

-- user_skill_versions: User isolation
CREATE POLICY admin_user_skill_versions_all ON user_skill_versions FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY user_user_skill_versions_select ON user_skill_versions FOR SELECT TO skill_user USING (user_id = skill_current_user_id());
CREATE POLICY api_user_skill_versions_all ON user_skill_versions FOR ALL TO skill_api USING (true) WITH CHECK (true);
CREATE POLICY auditor_user_skill_versions_select ON user_skill_versions FOR SELECT TO skill_auditor USING (true);

-- ==================== Intelligence Tables ====================

-- skill_market_data
CREATE POLICY admin_skill_market_data_all ON skill_market_data FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY manager_skill_market_data_all ON skill_market_data FOR ALL TO skill_manager USING (true) WITH CHECK (true);
CREATE POLICY user_skill_market_data_select ON skill_market_data FOR SELECT TO skill_user USING (true);
CREATE POLICY viewer_skill_market_data_select ON skill_market_data FOR SELECT TO skill_viewer USING (true);
CREATE POLICY api_skill_market_data_all ON skill_market_data FOR ALL TO skill_api USING (true) WITH CHECK (true);
CREATE POLICY scheduler_skill_market_data_update ON skill_market_data FOR UPDATE TO skill_scheduler USING (true);
CREATE POLICY scheduler_skill_market_data_insert ON skill_market_data FOR INSERT TO skill_scheduler WITH CHECK (true);

-- skill_income_data
CREATE POLICY admin_skill_income_data_all ON skill_income_data FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY user_skill_income_data_select ON skill_income_data FOR SELECT TO skill_user USING (true);
CREATE POLICY api_skill_income_data_all ON skill_income_data FOR ALL TO skill_api USING (true) WITH CHECK (true);

-- skill_certifications
CREATE POLICY admin_skill_certifications_all ON skill_certifications FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY manager_skill_certifications_all ON skill_certifications FOR ALL TO skill_manager USING (true) WITH CHECK (true);
CREATE POLICY user_skill_certifications_select ON skill_certifications FOR SELECT TO skill_user USING (true);
CREATE POLICY api_skill_certifications_all ON skill_certifications FOR ALL TO skill_api USING (true) WITH CHECK (true);

-- Junction tables
CREATE POLICY admin_skill_projects_all ON skill_projects FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY user_skill_projects_select ON skill_projects FOR SELECT TO skill_user USING (true);
CREATE POLICY api_skill_projects_all ON skill_projects FOR ALL TO skill_api USING (true) WITH CHECK (true);

CREATE POLICY admin_skill_roadmaps_all ON skill_roadmaps FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY user_skill_roadmaps_select ON skill_roadmaps FOR SELECT TO skill_user USING (true);
CREATE POLICY api_skill_roadmaps_all ON skill_roadmaps FOR ALL TO skill_api USING (true) WITH CHECK (true);

CREATE POLICY admin_skill_opportunities_all ON skill_opportunities FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY user_skill_opportunities_select ON skill_opportunities FOR SELECT TO skill_user USING (true);
CREATE POLICY api_skill_opportunities_all ON skill_opportunities FOR ALL TO skill_api USING (true) WITH CHECK (true);

-- ==================== Supporting Tables ====================

CREATE POLICY admin_skill_topics_all ON skill_topics FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY manager_skill_topics_all ON skill_topics FOR ALL TO skill_manager USING (true) WITH CHECK (true);
CREATE POLICY user_skill_topics_select ON skill_topics FOR SELECT TO skill_user USING (true);
CREATE POLICY api_skill_topics_all ON skill_topics FOR ALL TO skill_api USING (true) WITH CHECK (true);

CREATE POLICY admin_skill_resources_all ON skill_resources FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY manager_skill_resources_all ON skill_resources FOR ALL TO skill_manager USING (true) WITH CHECK (true);
CREATE POLICY user_skill_resources_select ON skill_resources FOR SELECT TO skill_user USING (true);
CREATE POLICY api_skill_resources_all ON skill_resources FOR ALL TO skill_api USING (true) WITH CHECK (true);

CREATE POLICY admin_skill_learning_paths_all ON skill_learning_paths FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY user_skill_learning_paths_select ON skill_learning_paths FOR SELECT TO skill_user USING (true);
CREATE POLICY api_skill_learning_paths_all ON skill_learning_paths FOR ALL TO skill_api USING (true) WITH CHECK (true);

-- skill_ai_recommendations: User isolation
CREATE POLICY admin_skill_ai_recommendations_all ON skill_ai_recommendations FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY user_skill_ai_recommendations_all ON skill_ai_recommendations FOR ALL TO skill_user USING (user_id = skill_current_user_id()) WITH CHECK (user_id = skill_current_user_id());
CREATE POLICY api_skill_ai_recommendations_all ON skill_ai_recommendations FOR ALL TO skill_api USING (true) WITH CHECK (true);
CREATE POLICY scheduler_skill_ai_recommendations_insert ON skill_ai_recommendations FOR INSERT TO skill_scheduler WITH CHECK (true);

-- skill_user_activity_log: User isolation
CREATE POLICY admin_skill_user_activity_log_all ON skill_user_activity_log FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY user_skill_user_activity_log_all ON skill_user_activity_log FOR ALL TO skill_user USING (user_id = skill_current_user_id()) WITH CHECK (user_id = skill_current_user_id());
CREATE POLICY api_skill_user_activity_log_all ON skill_user_activity_log FOR ALL TO skill_api USING (true) WITH CHECK (true);

-- ==================== Audit Tables ====================

-- skill_audit_log: Append-only for all, full access for admin+auditor
CREATE POLICY admin_skill_audit_log_all ON skill_audit_log FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY auditor_skill_audit_log_select ON skill_audit_log FOR SELECT TO skill_auditor USING (true);
CREATE POLICY api_skill_audit_log_insert ON skill_audit_log FOR INSERT TO skill_api WITH CHECK (true);

-- skill_taxonomy_history
CREATE POLICY admin_skill_taxonomy_history_all ON skill_taxonomy_history FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY auditor_skill_taxonomy_history_select ON skill_taxonomy_history FOR SELECT TO skill_auditor USING (true);
CREATE POLICY api_skill_taxonomy_history_insert ON skill_taxonomy_history FOR INSERT TO skill_api WITH CHECK (true);

-- skill_user_skill_history
CREATE POLICY admin_skill_user_skill_history_all ON skill_user_skill_history FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY user_skill_user_skill_history_select ON skill_user_skill_history FOR SELECT TO skill_user USING (user_id = skill_current_user_id());
CREATE POLICY auditor_skill_user_skill_history_select ON skill_user_skill_history FOR SELECT TO skill_auditor USING (true);
CREATE POLICY api_skill_user_skill_history_insert ON skill_user_skill_history FOR INSERT TO skill_api WITH CHECK (true);

-- skill_market_history
CREATE POLICY admin_skill_market_history_all ON skill_market_history FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY auditor_skill_market_history_select ON skill_market_history FOR SELECT TO skill_auditor USING (true);
CREATE POLICY api_skill_market_history_insert ON skill_market_history FOR INSERT TO skill_api WITH CHECK (true);
CREATE POLICY scheduler_skill_market_history_insert ON skill_market_history FOR INSERT TO skill_scheduler WITH CHECK (true);

-- ==================== Event Tables ====================

CREATE POLICY admin_skill_events_all ON skill_events FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY auditor_skill_events_select ON skill_events FOR SELECT TO skill_auditor USING (true);
CREATE POLICY api_skill_events_insert ON skill_events FOR INSERT TO skill_api WITH CHECK (true);
CREATE POLICY user_skill_events_insert ON skill_events FOR INSERT TO skill_user WITH CHECK (true);

CREATE POLICY admin_skill_event_outbox_all ON skill_event_outbox FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY api_skill_event_outbox_all ON skill_event_outbox FOR ALL TO skill_api USING (true) WITH CHECK (true);
CREATE POLICY scheduler_skill_event_outbox_update ON skill_event_outbox FOR UPDATE TO skill_scheduler USING (true);

CREATE POLICY admin_skill_webhook_queue_all ON skill_webhook_queue FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY api_skill_webhook_queue_all ON skill_webhook_queue FOR ALL TO skill_api USING (true) WITH CHECK (true);
CREATE POLICY scheduler_skill_webhook_queue_update ON skill_webhook_queue FOR UPDATE TO skill_scheduler USING (true);

CREATE POLICY admin_skill_event_subscriptions_all ON skill_event_subscriptions FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY api_skill_event_subscriptions_all ON skill_event_subscriptions FOR ALL TO skill_api USING (true) WITH CHECK (true);

-- ==================== Analytics Tables ====================

CREATE POLICY admin_skill_analytics_snapshots_all ON skill_analytics_snapshots FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY user_skill_analytics_snapshots_select ON skill_analytics_snapshots FOR SELECT TO skill_user USING (user_id = skill_current_user_id());
CREATE POLICY analytics_skill_analytics_snapshots_select ON skill_analytics_snapshots FOR SELECT TO skill_analytics USING (true);
CREATE POLICY api_skill_analytics_snapshots_all ON skill_analytics_snapshots FOR ALL TO skill_api USING (true) WITH CHECK (true);
CREATE POLICY scheduler_skill_analytics_snapshots_insert ON skill_analytics_snapshots FOR INSERT TO skill_scheduler WITH CHECK (true);

CREATE POLICY admin_skill_forecasts_all ON skill_forecasts FOR ALL TO skill_admin USING (true) WITH CHECK (true);
CREATE POLICY user_skill_forecasts_select ON skill_forecasts FOR SELECT TO skill_user USING (true);
CREATE POLICY analytics_skill_forecasts_select ON skill_forecasts FOR SELECT TO skill_analytics USING (true);
CREATE POLICY api_skill_forecasts_all ON skill_forecasts FOR ALL TO skill_api USING (true) WITH CHECK (true);

-- === 6. Column-Level Encryption for PII Fields ===

-- Create encryption key (in production, use a key management service)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Function to encrypt PII data
CREATE OR REPLACE FUNCTION skill_encrypt_pii(plaintext TEXT)
RETURNS BYTEA AS $$
DECLARE
    enc_key TEXT;
BEGIN
    enc_key := current_setting('app.encryption_key', true);
    IF enc_key IS NULL THEN
        RETURN convert_to(plaintext, 'UTF8');
    END IF;
    RETURN pgp_sym_encrypt(plaintext, enc_key);
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to decrypt PII data
CREATE OR REPLACE FUNCTION skill_decrypt_pii(ciphertext BYTEA)
RETURNS TEXT AS $$
DECLARE
    enc_key TEXT;
BEGIN
    enc_key := current_setting('app.encryption_key', true);
    IF enc_key IS NULL OR ciphertext IS NULL THEN
        RETURN NULL;
    END IF;
    BEGIN
        RETURN pgp_sym_decrypt(ciphertext, enc_key);
    EXCEPTION WHEN OTHERS THEN
        RETURN NULL;
    END;
END;
$$ LANGUAGE plpgsql STABLE;

-- Add encrypted columns for PII
ALTER TABLE skill_external_mappings ADD COLUMN IF NOT EXISTS external_credentials BYTEA;
ALTER TABLE skill_event_subscriptions ADD COLUMN IF NOT EXISTS encrypted_secret BYTEA;
ALTER TABLE user_skill_evidence ADD COLUMN IF NOT EXISTS encrypted_description BYTEA;

-- === 7. Audit Trigger Function ===

CREATE OR REPLACE FUNCTION skill_audit_trigger_func()
RETURNS TRIGGER AS $$
DECLARE
    tid UUID := skill_current_tenant_id();
    uid UUID := skill_current_user_id();
    rid TEXT;
    changed_cols TEXT[];
BEGIN
    rid := current_setting('app.request_id', true);
    IF TG_OP IN ('UPDATE', 'DELETE') THEN
        SELECT array_agg(key) INTO changed_cols FROM jsonb_each(to_jsonb(OLD)) j WHERE j.value IS DISTINCT FROM to_jsonb(NEW)->>j.key;
        INSERT INTO skill_audit_log (table_name, record_id, user_id, action, old_data, new_data, changed_fields, request_id, tenant_id, created_at)
        VALUES (TG_TABLE_NAME, COALESCE(NEW.OLD.skill_id, NEW.OLD.user_skill_id, OLD.evidence_id, OLD.assessment_id, OLD.target_id, OLD.category_id, OLD.tag_id, OLD.mapping_id, gen_random_uuid()::TEXT)::UUID, uid, TG_OP, to_jsonb(OLD), to_jsonb(NEW), changed_cols, rid, tid, EXTRACT(EPOCH FROM NOW()) * 1000);
    ELSE
        INSERT INTO skill_audit_log (table_name, record_id, user_id, action, new_data, request_id, tenant_id, created_at)
        VALUES (TG_TABLE_NAME, COALESCE(NEW.skill_id, NEW.user_skill_id, NEW.evidence_id, NEW.assessment_id, NEW.target_id, NEW.category_id, gen_random_uuid()::TEXT)::UUID, uid, TG_OP, to_jsonb(NEW), rid, tid, EXTRACT(EPOCH FROM NOW()) * 1000);
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- === 8. Apply Audit Triggers to Key Tables ===

CREATE TRIGGER trg_skills_audit AFTER INSERT OR UPDATE OR DELETE ON skills FOR EACH ROW EXECUTE FUNCTION skill_audit_trigger_func();
CREATE TRIGGER trg_skill_categories_audit AFTER INSERT OR UPDATE OR DELETE ON skill_categories FOR EACH ROW EXECUTE FUNCTION skill_audit_trigger_func();
CREATE TRIGGER trg_user_skills_audit AFTER INSERT OR UPDATE OR DELETE ON user_skills FOR EACH ROW EXECUTE FUNCTION skill_audit_trigger_func();
CREATE TRIGGER trg_user_skill_evidence_audit AFTER INSERT OR UPDATE OR DELETE ON user_skill_evidence FOR EACH ROW EXECUTE FUNCTION skill_audit_trigger_func();
CREATE TRIGGER trg_user_skill_targets_audit AFTER INSERT OR UPDATE OR DELETE ON user_skill_targets FOR EACH ROW EXECUTE FUNCTION skill_audit_trigger_func();
CREATE TRIGGER trg_user_skill_assessments_audit AFTER INSERT OR UPDATE OR DELETE ON user_skill_assessments FOR EACH ROW EXECUTE FUNCTION skill_audit_trigger_func();
CREATE TRIGGER trg_skill_market_data_audit AFTER INSERT OR UPDATE OR DELETE ON skill_market_data FOR EACH ROW EXECUTE FUNCTION skill_audit_trigger_func();
CREATE TRIGGER trg_skill_relationships_audit AFTER INSERT OR UPDATE OR DELETE ON skill_relationships FOR EACH ROW EXECUTE FUNCTION skill_audit_trigger_func();
CREATE TRIGGER trg_skill_certifications_audit AFTER INSERT OR UPDATE OR DELETE ON skill_certifications FOR EACH ROW EXECUTE FUNCTION skill_audit_trigger_func();

-- === 9. Row-Level Security Default Deny for All Roles ===

-- Ensure all tables have a default deny policy (no explicit policy = deny)
ALTER TABLE skill_categories FORCE ROW LEVEL SECURITY;
ALTER TABLE skills FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_relationships FORCE ROW LEVEL SECURITY;
ALTER TABLE tags FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_tags FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_external_mappings FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_roadmap_definitions FORCE ROW LEVEL SECURITY;
ALTER TABLE user_skills FORCE ROW LEVEL SECURITY;
ALTER TABLE user_skill_evidence FORCE ROW LEVEL SECURITY;
ALTER TABLE user_skill_targets FORCE ROW LEVEL SECURITY;
ALTER TABLE user_skill_assessments FORCE ROW LEVEL SECURITY;
ALTER TABLE user_skill_versions FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_market_data FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_income_data FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_certifications FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_projects FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_roadmaps FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_opportunities FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_topics FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_resources FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_learning_paths FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_ai_recommendations FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_user_activity_log FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_audit_log FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_taxonomy_history FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_user_skill_history FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_market_history FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_events FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_event_outbox FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_webhook_queue FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_event_subscriptions FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_analytics_snapshots FORCE ROW LEVEL SECURITY;
ALTER TABLE skill_forecasts FORCE ROW LEVEL SECURITY;

-- === Column-Level Permissions (Section 11.3 of architecture doc) ===

REVOKE UPDATE ON user_skill_evidence FROM PUBLIC;
GRANT UPDATE (title, description, url, metadata) ON user_skill_evidence TO authenticated;

REVOKE DELETE ON skill_audit_log FROM PUBLIC;
REVOKE DELETE ON skill_taxonomy_history FROM PUBLIC;
REVOKE DELETE ON skill_events FROM PUBLIC;

-- === Connection Security (Section 11.5 — requires superuser to execute) ===

DO $$
BEGIN
    -- These require superuser; run separately if not available
    -- ALTER SYSTEM SET ssl = on;
    -- ALTER SYSTEM SET ssl_ciphers = 'HIGH:!aNULL:!eNULL:!DES';
    RAISE NOTICE 'Connection security settings (ssl, ciphers) require superuser. Apply manually.';
END $$;

ALTER ROLE skill_user SET statement_timeout = '30s';
ALTER ROLE skill_api SET statement_timeout = '60s';
ALTER ROLE skill_scheduler SET statement_timeout = '120s';
ALTER ROLE skill_analytics SET statement_timeout = '120s';

-- === Audit Notify Trigger Function ===

CREATE OR REPLACE FUNCTION skill_notify_audit_event()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('audit_event', jsonb_build_object(
        'table', TG_TABLE_NAME,
        'action', TG_OP,
        'record_id', NEW.record_id,
        'user_id', NEW.user_id,
        'changed_at', NEW.created_at
    )::TEXT);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Attach to high-volume tables only
CREATE TRIGGER trg_audit_log_notify AFTER INSERT ON skill_audit_log
    FOR EACH ROW EXECUTE FUNCTION skill_notify_audit_event();

-- ===== End: 005_skills_security_rls.sql =====

-- ===== Begin: 006_skills_materialized_views.sql =====
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

-- ===== End: 006_skills_materialized_views.sql =====

-- ===== Begin: 007_skills_partman_cron.sql =====
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

-- ===== End: 007_skills_partman_cron.sql =====
