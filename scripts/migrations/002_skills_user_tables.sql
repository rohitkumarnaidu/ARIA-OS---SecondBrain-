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
