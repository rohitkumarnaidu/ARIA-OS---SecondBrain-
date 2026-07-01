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
