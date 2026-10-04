-- =============================================================
-- Migration 015: Memory & Knowledge Graph Schema
-- Creates: 4 tables for the AI memory subsystem and the
--          personal knowledge graph.
--   1. memory           — Tier 2/3/4 unified memory store
--   2. working_memory   — Tier 1 day-level TTL key-value store
--   3. knowledge_nodes  — Knowledge graph vertices
--   4. knowledge_edges  — Knowledge graph relationships
-- Includes: JSONB value payload (dual-shape), tier CHECK
--           constraints, UNIQUE (user_id, type, key) for
--           race-safe read-then-insert dedup, generated
--           tsvector column + GIN indexes, updated_at
--           triggers reusing the 013 trigger function.
-- Depends on: auth.users (Supabase), pgcrypto extension,
--             Migration 013 (trigger_set_updated_at)
-- =============================================================

BEGIN;

-- === Extensions ===
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================
-- 1. IMMUTABLE JSONB TEXT HELPER
-- Required by the GENERATED ... STORED tsvector column below:
-- a direct `value::text` cast resolves to jsonb_out, which
-- PostgreSQL declares STABLE and therefore rejects inside a
-- generated column. jsonb normalises its input, so its text
-- form is deterministic for a given value; wrapping it in an
-- IMMUTABLE SQL function satisfies the generated-column check.
-- =============================================================

CREATE OR REPLACE FUNCTION memory_value_text(val JSONB)
RETURNS TEXT AS $$
    SELECT COALESCE(val::text, '');
$$ LANGUAGE SQL IMMUTABLE STRICT;

COMMENT ON FUNCTION memory_value_text(JSONB) IS 'IMMUTABLE jsonb-to-text projection for the memory.search_vector generated column';

-- =============================================================
-- 2. MEMORY (unified tier 2/3/4 store)
-- Read/written by:
--   apps/api/app/api/memory.py
--   packages/ai/agents/memory_agent.py
--   packages/ai/memory/tiers.py        (Episodic/Semantic/Procedural)
--   packages/ai/memory/retrieval.py
--   packages/ai/memory/compression.py  (prune_old_memories)
--   packages/ai/orchestrator.py        (search_memory)
-- =============================================================

CREATE TABLE IF NOT EXISTS memory (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    type              TEXT NOT NULL CHECK (type IN ('buffer','working','episodic','semantic','procedural','query','consolidated','preference','fact','pattern','interaction')),
    key               TEXT NOT NULL,
    value             JSONB DEFAULT '{}'::jsonb,
    importance        TEXT DEFAULT 'medium' CHECK (importance IN ('low','medium','high','critical')),
    tags              JSONB DEFAULT '[]'::jsonb,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW(),
    expires_at        TIMESTAMPTZ,
    search_vector     TSVECTOR GENERATED ALWAYS AS (
                        to_tsvector('english',
                            COALESCE(key, '') || ' ' || COALESCE(memory_value_text(value), '')
                        )
                      ) STORED,
    UNIQUE (user_id, type, key)
);

COMMENT ON TABLE memory IS 'Unified AI memory store for episodic, semantic, procedural, and working tiers';

-- `value` is JSONB because the Python writers emit two different
-- shapes and both must survive a round-trip:
--   * tiers.py / memory_agent.py:73  -> json.dumps({...})  (serialised JSON text)
--   * memory_agent.py:293            -> a raw Python dict
-- PostgREST stores the first as a JSONB string scalar and the
-- second as a JSONB object. Every reader in the codebase already
-- branches on `isinstance(value, str)` before json.loads(), so a
-- TEXT column would silently break the raw-dict path and a JSONB
-- column would break only paths that json.loads() without the
-- isinstance guard. JSONB is the shape that satisfies both.

-- `type` CHECK mirrors _VALID_MEMORY_TYPES in
-- packages/ai/agents/memory_agent.py:27 — validate_memory_type()
-- coerces anything outside this set to 'episodic' before the
-- insert, so no other value can reach the column.

-- UNIQUE (user_id, type, key) makes the read-then-insert dedup in
-- memory_agent.store_interaction, SemanticMemory.store_fact and
-- ProceduralMemory.store_pattern race-safe under concurrency.

COMMENT ON COLUMN memory.type IS 'Memory tier/kind: buffer, working, episodic, semantic, procedural, query, consolidated, preference, fact, pattern, interaction';
COMMENT ON COLUMN memory.key IS 'Stable dedup key — sha256-derived by every Python writer';
COMMENT ON COLUMN memory.value IS 'Tier payload. Stored as JSONB; may be a JSON object or a JSON-encoded string (both writer shapes are supported)';
COMMENT ON COLUMN memory.importance IS 'Retrieval weight: low, medium, high, critical';
COMMENT ON COLUMN memory.tags IS 'JSON array of strings; queried with PostgREST cs (@>) via .contains(tags, [...])';
COMMENT ON COLUMN memory.expires_at IS 'Optional TTL. NULL means never expire; pruned by memory_agent.prune_expired_memories';
COMMENT ON COLUMN memory.search_vector IS 'Generated tsvector over key + value, for full-text retrieval';

-- =============================================================
-- 3. WORKING MEMORY (tier 1 — day-level TTL key-value store)
-- Read/written by: packages/ai/memory/tiers.py (WorkingMemory)
-- `key` is the PRIMARY KEY on purpose: WorkingMemory.set() calls
-- .upsert({key, user_id, type, value, expires_at}) with no id.
-- PostgREST resolves merge-duplicates against the primary key, so
-- an id-based PK would insert a new row on every set() and let
-- .eq("key", ...) read an arbitrary duplicate. key is the
-- sha256("wm:<key>") digest emitted by _make_key().
-- =============================================================

CREATE TABLE IF NOT EXISTS working_memory (
    key               TEXT PRIMARY KEY,
    user_id           UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    type              TEXT NOT NULL DEFAULT 'working' CHECK (type IN ('buffer','working')),
    value             TEXT NOT NULL,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    expires_at        TIMESTAMPTZ NOT NULL
);

COMMENT ON TABLE working_memory IS 'Tier 1 day-level working memory with per-key TTL, keyed by sha256 digest';

-- `value` is TEXT, not JSONB: WorkingMemory.get() reads it back
-- with an unguarded `json.loads(result.data[0]["value"])`. A JSONB
-- column would hand back a dict and raise TypeError.

COMMENT ON COLUMN working_memory.key IS 'sha256("wm:<logical key>")[:24] digest — primary key so .upsert() merges instead of duplicating';
COMMENT ON COLUMN working_memory.type IS 'Always "working" from tiers.py; "buffer" reserved for tier 0 persistence';
COMMENT ON COLUMN working_memory.value IS 'JSON-encoded string as produced by json.dumps(); read back with json.loads()';
COMMENT ON COLUMN working_memory.expires_at IS 'TTL deadline; swept by WorkingMemory.clear_expired()';

-- NOTE: tiers.py:119 passes user_id="system", which is not a UUID
-- and cannot satisfy this FK. Every WorkingMemory supabase call is
-- wrapped in try/except and falls back to the in-process OrderedDict
-- cache, so the failure degrades to a warn log with no crash. The
-- column is kept UUID NOT NULL so the RLS policy in migration 016 can
-- use the house `auth.uid() = user_id` idiom and so user scoping is
-- always enforced. Fixing the write path requires a Python change.

-- =============================================================
-- 4. KNOWLEDGE NODES (graph vertices)
-- `source_table` + `source_id` make the node polymorphic over the
-- core app tables; no FK is possible on a polymorphic pointer, so
-- referential integrity is enforced by the producing code.
-- Frontend contract (apps/web/components/knowledge/
-- KnowledgeGraph.tsx GraphNode): label renders as `title`,
-- summary renders as `description`, and `type` here is a superset
-- of the frontend union ('note' | 'resource' | 'idea').
-- =============================================================

CREATE TABLE IF NOT EXISTS knowledge_nodes (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    type              TEXT NOT NULL CHECK (type IN ('note','resource','idea','memory','course','task')),
    label             TEXT NOT NULL,
    summary           TEXT,
    source_table      TEXT,
    source_id         UUID,
    weight            FLOAT DEFAULT 1.0,
    degree            INTEGER DEFAULT 0,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE knowledge_nodes IS 'Knowledge graph vertices — notes, resources, ideas, memories, courses, and tasks';

COMMENT ON COLUMN knowledge_nodes.label IS 'Human-readable node name; maps to the frontend GraphNode.title field';
COMMENT ON COLUMN knowledge_nodes.summary IS 'Short description; maps to the frontend GraphNode.description field';
COMMENT ON COLUMN knowledge_nodes.source_table IS 'Origin table name for polymorphic resolution (notes, resources, ideas, memory, courses, tasks)';
COMMENT ON COLUMN knowledge_nodes.source_id IS 'Primary key of the row in source_table';
COMMENT ON COLUMN knowledge_nodes.weight IS 'Node salience weight used for graph layout and ranking';
COMMENT ON COLUMN knowledge_nodes.degree IS 'Cached count of incident knowledge_edges rows';

-- =============================================================
-- 5. KNOWLEDGE EDGES (graph relationships)
-- `relation` maps to the frontend GraphEdge.label field
-- (contains, teaches, used_in, impacts, related_to, ...).
-- =============================================================

CREATE TABLE IF NOT EXISTS knowledge_edges (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    source_id         UUID REFERENCES knowledge_nodes(id) ON DELETE CASCADE NOT NULL,
    target_id         UUID REFERENCES knowledge_nodes(id) ON DELETE CASCADE NOT NULL,
    relation          TEXT NOT NULL,
    weight            FLOAT DEFAULT 1.0,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, source_id, target_id, relation)
);

COMMENT ON TABLE knowledge_edges IS 'Knowledge graph relationships between knowledge_nodes rows';

COMMENT ON COLUMN knowledge_edges.source_id IS 'Origin node (knowledge_nodes.id, ON DELETE CASCADE)';
COMMENT ON COLUMN knowledge_edges.target_id IS 'Destination node (knowledge_nodes.id, ON DELETE CASCADE)';
COMMENT ON COLUMN knowledge_edges.relation IS 'Relationship verb; maps to the frontend GraphEdge.label field';
COMMENT ON COLUMN knowledge_edges.weight IS 'Relationship strength used for graph layout and ranking';

-- =============================================================
-- 6. INDEXES
-- Mirrors the idiom in 011_core_app_indexes.sql.
-- =============================================================

-- 6a. memory (6 indexes)
-- idx_memory_user_type is prefix-redundant with the
-- UNIQUE (user_id, type, key) index but is kept so the tier
-- scan has a dedicated, narrower index.
CREATE INDEX IF NOT EXISTS idx_memory_user_type ON memory(user_id, type);
CREATE INDEX IF NOT EXISTS idx_memory_user_created ON memory(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_memory_user_importance ON memory(user_id, importance);
CREATE INDEX IF NOT EXISTS idx_memory_tags ON memory USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_memory_fts ON memory USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_memory_expires ON memory(expires_at) WHERE expires_at IS NOT NULL;

-- 6b. working_memory (2 indexes)
CREATE INDEX IF NOT EXISTS idx_working_memory_expires ON working_memory(expires_at);
CREATE INDEX IF NOT EXISTS idx_working_memory_user ON working_memory(user_id);

-- 6c. knowledge_nodes (3 indexes)
CREATE INDEX IF NOT EXISTS idx_knowledge_nodes_user_type ON knowledge_nodes(user_id, type);
CREATE INDEX IF NOT EXISTS idx_knowledge_nodes_source ON knowledge_nodes(source_table, source_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_nodes_user_updated ON knowledge_nodes(user_id, updated_at DESC);

-- 6d. knowledge_edges (2 indexes; user_id + source_id are already
-- covered by the UNIQUE (user_id, source_id, target_id, relation)
-- index prefix)
CREATE INDEX IF NOT EXISTS idx_knowledge_edges_target ON knowledge_edges(target_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_edges_user_relation ON knowledge_edges(user_id, relation);

-- =============================================================
-- 7. UPDATED_AT TRIGGERS
-- Reuses trigger_set_updated_at() from 013_core_app_triggers.sql.
-- working_memory and knowledge_edges are intentionally excluded —
-- neither has an updated_at column (see 013 section 4).
-- =============================================================

DROP TRIGGER IF EXISTS set_updated_at ON memory;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON memory
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_updated_at();

DROP TRIGGER IF EXISTS set_updated_at ON knowledge_nodes;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON knowledge_nodes
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_updated_at();

-- =============================================================
-- 8. LEGACY TABLE NOTE
-- aria_memory (created in 010, section 20) is retained for schema
-- continuity only. It is NOT read or written by any backend Python
-- module — every memory code path in apps/api/app/api/memory.py,
-- packages/ai/agents/memory_agent.py, packages/ai/memory/*, and
-- packages/ai/orchestrator.py targets the `memory` table above.
-- =============================================================

COMMENT ON TABLE aria_memory IS "ARIA's long-term memory about user preferences, facts, and patterns — LEGACY: superseded by the memory table from migration 015; not read or written by the backend, retained for backwards compatibility only";

COMMIT;
