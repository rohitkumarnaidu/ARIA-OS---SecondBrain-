-- Feature Flags Table
-- Used for canary deployments and A/B testing
-- Supports percentage-based rollout + user segment targeting

CREATE TABLE IF NOT EXISTS feature_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(255) UNIQUE NOT NULL,
    enabled BOOLEAN DEFAULT FALSE,
    rollout_percentage INTEGER DEFAULT 0 CHECK (rollout_percentage >= 0 AND rollout_percentage <= 100),
    user_segments TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_feature_flags_key ON feature_flags(key);
CREATE INDEX IF NOT EXISTS idx_feature_flags_enabled ON feature_flags(enabled) WHERE enabled = TRUE;

-- Trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_feature_flags_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_feature_flags_updated_at ON feature_flags;
CREATE TRIGGER trigger_feature_flags_updated_at
    BEFORE UPDATE ON feature_flags
    FOR EACH ROW
    EXECUTE FUNCTION update_feature_flags_updated_at();

-- RLS
ALTER TABLE feature_flags ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Admins can manage feature_flags"
    ON feature_flags FOR ALL
    USING (auth.role() = 'service_role');

-- Seed: safe defaults
INSERT INTO feature_flags (key, enabled, rollout_percentage, metadata) VALUES
    ('new.dashboard', FALSE, 0, '{"description": "New dashboard v2 layout", "owner": "developer"}'),
    ('ai.briefing', TRUE, 100, '{"description": "AI-powered daily briefing", "owner": "developer"}'),
    ('canary.api-v2', FALSE, 5, '{"description": "Canary API v2 endpoints", "owner": "developer"}')
ON CONFLICT (key) DO NOTHING;
