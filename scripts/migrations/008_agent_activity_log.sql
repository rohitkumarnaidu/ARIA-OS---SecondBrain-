-- =============================================================
-- AGENT ACTIVITY LOG — Tracks agent execution history
-- =============================================================

CREATE TABLE IF NOT EXISTS agent_activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('running', 'completed', 'failed')),
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    error_message TEXT,
    input_summary TEXT,
    output_summary TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_agent_activity_user ON agent_activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_activity_status ON agent_activity_log(status);
CREATE INDEX IF NOT EXISTS idx_agent_activity_started ON agent_activity_log(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_activity_user_started ON agent_activity_log(user_id, started_at DESC);

ALTER TABLE agent_activity_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_agent_activity_isolation ON agent_activity_log
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());