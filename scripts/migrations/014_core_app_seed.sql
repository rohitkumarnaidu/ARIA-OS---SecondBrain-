-- =============================================================
-- Migration 014: Core Application — Seed Data
-- Creates: Default feature flags, reference/lookup data,
--          and initial configuration state.
-- =============================================================

BEGIN;

-- =============================================================
-- 1. FEATURE FLAGS (application-level toggles)
-- Stored in a simple key-value pattern using a dedicated table.
-- =============================================================

CREATE TABLE IF NOT EXISTS feature_flags (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    flag_key      TEXT NOT NULL UNIQUE,
    flag_value    JSONB NOT NULL DEFAULT 'true',
    description   TEXT,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE feature_flags IS 'Application-level feature flags with JSONB values';

-- Seed default feature flags
INSERT INTO feature_flags (flag_key, flag_value, description) VALUES
    ('daily_briefing_enabled',    'true',  'Enable/disable daily morning briefing generation'),
    ('weekly_review_enabled',     'true',  'Enable/disable Sunday weekly review generation'),
    ('opportunity_radar_enabled', 'true',  'Enable/disable daily opportunity scanning'),
    ('sleep_analysis_enabled',    'true',  'Enable/disable sleep quality analysis and wind-down'),
    ('course_nudge_enabled',      'true',  'Enable/disable course progress nudges at 6 PM'),
    ('habit_reminder_enabled',    'true',  'Enable/disable habit miss detection at midnight'),
    ('aria_memory_enabled',       'true',  'Enable/disable ARIA memory consolidation'),
    ('learning_agent_enabled',    'true',  'Enable/disable learning pattern detection'),
    ('roadmap_updates_enabled',   'true',  'Enable/disable AI roadmap update suggestions'),
    ('realtime_sync_enabled',     'true',  'Enable/disable Supabase realtime subscriptions'),
    ('push_notifications_enabled','true',  'Enable/disable web push notifications'),
    ('email_digest_enabled',      'false', 'Enable/disable email digest of briefings'),
    ('debug_mode',                'false', 'Enable/disable verbose debug logging'),
    ('maintenance_mode',          'false', 'Enable/disable maintenance mode (blocks non-admin)')
ON CONFLICT (flag_key) DO NOTHING;

-- =============================================================
-- 2. SKILL CATEGORIES (reference data for skills taxonomy)
-- These are the top-level categories used in profile.skills.
-- =============================================================

CREATE TABLE IF NOT EXISTS skill_categories (
    id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name    TEXT NOT NULL UNIQUE,
    slug    TEXT NOT NULL UNIQUE,
    icon    TEXT,
    description TEXT,
    sort_order INTEGER DEFAULT 0
);

COMMENT ON TABLE skill_categories IS 'Reference lookup for skill categories used in user profiles';

INSERT INTO skill_categories (name, slug, icon, description, sort_order) VALUES
    ('Programming Languages', 'programming-languages', 'code', 'General-purpose and domain-specific languages', 1),
    ('Web Development', 'web-development', 'globe', 'Frontend, backend, and full-stack web technologies', 2),
    ('Data Science & ML', 'data-science-ml', 'brain', 'Data analysis, machine learning, and AI', 3),
    ('DevOps & Cloud', 'devops-cloud', 'cloud', 'CI/CD, cloud platforms, infrastructure', 4),
    ('Databases', 'databases', 'database', 'SQL, NoSQL, and data storage technologies', 5),
    ('Mobile Development', 'mobile-development', 'smartphone', 'iOS, Android, and cross-platform mobile', 6),
    ('Design & UX', 'design-ux', 'palette', 'UI/UX design, prototyping, and design tools', 7),
    ('Soft Skills', 'soft-skills', 'users', 'Communication, leadership, and collaboration', 8),
    ('Domain Knowledge', 'domain-knowledge', 'book', 'Industry-specific expertise and domain knowledge', 9),
    ('Tools & Productivity', 'tools-productivity', 'settings', 'Development tools, editors, and productivity systems', 10)
ON CONFLICT (slug) DO NOTHING;

-- =============================================================
-- 3. DEFAULT OPPORTUNITY PLATFORMS (reference data)
-- Common platforms scanned by Opportunity Radar agent.
-- =============================================================

CREATE TABLE IF NOT EXISTS opportunity_platforms (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL UNIQUE,
    base_url    TEXT NOT NULL,
    platform_type TEXT CHECK (platform_type IN ('internship','hackathon','fellowship','freelance','scholarship','competition','open_source')),
    is_active   BOOLEAN DEFAULT TRUE,
    scan_frequency TEXT DEFAULT 'daily' CHECK (scan_frequency IN ('daily','weekly','monthly')),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE opportunity_platforms IS 'Reference data for Opportunity Radar scan targets';

INSERT INTO opportunity_platforms (name, base_url, platform_type, is_active, scan_frequency) VALUES
    ('Internshala',          'https://internshala.com',          'internship',  TRUE,  'daily'),
    ('LinkedIn Jobs',        'https://linkedin.com/jobs',       'internship',  TRUE,  'daily'),
    ('AngelList/Wellfound',  'https://wellfound.com',           'freelance',   TRUE,  'daily'),
    ('Devfolio',             'https://devfolio.co',             'hackathon',   TRUE,  'weekly'),
    ('Unstop',               'https://unstop.com',              'competition', TRUE,  'weekly'),
    ('MLH Fellowship',       'https://mlh.io',                  'fellowship',  TRUE,  'weekly'),
    ('Google Summer of Code','https://summerofcode.withgoogle.com','open_source',TRUE, 'yearly'),
    ('Outreachy',            'https://outreachy.org',           'internship',  TRUE,  'yearly'),
    ('Scholars4Dev',         'https://scholars4dev.com',        'scholarship', TRUE,  'monthly'),
    ('Freelancer',           'https://freelancer.com',          'freelance',   TRUE,  'weekly')
ON CONFLICT (name) DO NOTHING;

-- =============================================================
-- 4. AI PERSONA CONFIGURATION (reference data)
-- Default ARIA response personas and tones.
-- =============================================================

CREATE TABLE IF NOT EXISTS ai_personas (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL UNIQUE,
    slug        TEXT NOT NULL UNIQUE,
    description TEXT,
    temperature FLOAT DEFAULT 0.7,
    system_prompt_prefix TEXT,
    is_default  BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE ai_personas IS 'ARIA AI response personas with temperature and system prompt overrides';

INSERT INTO ai_personas (name, slug, description, temperature, is_default) VALUES
    ('Default',     'default',     'Balanced, helpful AI assistant',                       0.5,  TRUE),
    ('Motivator',   'motivator',   'Energetic, encouraging, hype-mode ARIA',              0.8, FALSE),
    ('Minimalist',  'minimalist',  'Brief, direct, no-nonsense responses',                0.3, FALSE),
    ('Mentor',      'mentor',      'Socratic teacher — guides you to answers',             0.6, FALSE),
    ('Strategist',  'strategist',  'Long-term planning focus with systems thinking',       0.4, FALSE)
ON CONFLICT (slug) DO NOTHING;

DROP TRIGGER IF EXISTS set_updated_at ON feature_flags;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON feature_flags
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_updated_at();

COMMIT;
