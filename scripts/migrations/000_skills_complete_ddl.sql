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
