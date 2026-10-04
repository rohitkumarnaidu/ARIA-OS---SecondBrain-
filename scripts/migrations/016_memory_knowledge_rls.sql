-- =============================================================
-- Migration 016: Memory & Knowledge Graph — RLS Policies
-- Enables RLS on the 4 tables created in 015 and creates one
-- per-table "users_own_data" policy. All four carry a user_id
-- column, so none of them need the EXISTS-subquery pattern used
-- for child tables in 012.
-- Depends on: Migration 015 (memory, working_memory,
--             knowledge_nodes, knowledge_edges)
-- Note: reuses rls_user_id() / rls_is_owner() from 012 and does
--       not redefine them.
-- =============================================================

BEGIN;

-- =============================================================
-- 1. PRIMARY USER-OWNED TABLES (with user_id column)
-- Each table gets: ALTER TABLE ... ENABLE ROW LEVEL SECURITY;
--                  CREATE POLICY "users_own_data" FOR ALL
-- =============================================================

-- 1a. memory
ALTER TABLE memory ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'memory' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON memory
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 1b. working_memory
ALTER TABLE working_memory ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'working_memory' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON working_memory
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 1c. knowledge_nodes
ALTER TABLE knowledge_nodes ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'knowledge_nodes' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON knowledge_nodes
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- 1d. knowledge_edges
ALTER TABLE knowledge_edges ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'knowledge_edges' AND policyname = 'users_own_data') THEN
        CREATE POLICY "users_own_data" ON knowledge_edges
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- =============================================================
-- 2. USER-SCOPED SUPPORT INDEXES
-- Indexes whose leading column is user_id are already provided by
-- a UNIQUE constraint index in 015 and are not duplicated here:
--   memory          -> UNIQUE (user_id, type, key)
--   knowledge_nodes -> idx_knowledge_nodes_user_type
--   knowledge_edges -> UNIQUE (user_id, source_id, target_id, relation)
-- working_memory is keyed by `key`, so its user_id index was added
-- alongside the rest of the indexes in 015 (idx_working_memory_user)
-- and is only re-asserted here for completeness.
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_working_memory_user ON working_memory(user_id);

-- =============================================================
-- 3. VERIFICATION
-- Every row written through the PostgREST API is scoped to
-- auth.uid() by the policies above. Backend access uses the
-- service_role key, which bypasses RLS by design — matching the
-- posture of 012_core_app_rls.sql on all 30 core tables.
-- =============================================================

COMMIT;
