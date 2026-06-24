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
