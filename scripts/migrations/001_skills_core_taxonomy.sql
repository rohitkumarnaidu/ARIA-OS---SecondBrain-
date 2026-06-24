-- =============================================================
-- Migration 001: Skills Core Taxonomy
-- Creates: skill_categories, skills, skill_relationships,
--          tags, skill_tags, skill_external_mappings,
--          skill_roadmap_definitions
-- =============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "ltree";

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
