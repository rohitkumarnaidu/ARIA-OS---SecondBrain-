-- =============================================================
-- Migration 017: Knowledge Graph — node tags, idempotent upsert
--               key, and the 'goal' node type.
-- Depends on: Migration 015 (knowledge_nodes, knowledge_edges),
--             Migration 016 (RLS on knowledge_nodes/edges).
--
-- WHY THIS MIGRATION EXISTS
-- -------------------------
-- 015 created knowledge_nodes with no `tags` column and no unique
-- constraint, and closed its `type` CHECK at six values. All three are
-- gaps against code that already exists in this repo:
--
--   1. tags — apps/web/components/knowledge/KnowledgeGraph.tsx:13
--      declares `tags?: string[]` on GraphNode, and TWO frontend
--      features read it:
--        * app/(dashboard)/knowledge/page.tsx:67-71 builds `allTags`
--          from node tags and hands them to <KnowledgeSearch/>;
--          KnowledgeSearch.tsx:147 only renders its tag filter when
--          `tags.length > 0`, so with no column the filter is
--          permanently hidden.
--        * page.tsx:77 filters nodes by tag and page.tsx:189 renders
--          `#tag` chips; NodeDetail.tsx:106-119 renders tag badges.
--      Every knowledge_nodes.tags read is therefore unsatisfiable
--      today. This is a genuine missing column, not a nicety.
--
--   2. UNIQUE (user_id, type, source_table, source_id) — 015 gives
--      `memory` UNIQUE (user_id, type, key) and `knowledge_edges`
--      UNIQUE (user_id, source_id, target_id, relation), but leaves
--      knowledge_nodes without any unique constraint, even though
--      idx_knowledge_nodes_source indexes (source_table, source_id)
--      — the very pair that identifies a node. Extraction therefore
--      has no conflict target, so a repeat run cannot be made
--      idempotent at the database level.
--      packages/ai/agents/knowledge_agent.py calls
--      .upsert(..., on_conflict="user_id,type,source_table,source_id"),
--      which Postgres resolves against this unique index.
--      Note: plain (not NULLS NOT DISTINCT) uniqueness is deliberate —
--      rows whose source_id IS NULL stay unconstrained, so manually
--      created free-form nodes are never rejected.
--
--   3. 'goal' in the type CHECK — the extractor reads goals as a
--      source table, and goals are the hub of this schema:
--      tasks.goal_id, courses.related_goal_id and
--      resources.related_goal_id all FK to goals(id). Without a goal
--      node the three most informative edges in the graph cannot be
--      written. Widening a CHECK never invalidates an existing row,
--      so this is additive.
--
-- NOT CHANGED: every other column of knowledge_nodes/knowledge_edges
-- matches 015 exactly and is consumed as-is by the API layer.
-- =============================================================

BEGIN;

-- =============================================================
-- 1. tags (JSONB array of strings)
-- JSONB rather than TEXT[] to match `memory.tags`, so the two tag
-- stores stay the same type for the same query idiom
-- (.contains(tags, [...])).
-- =============================================================

ALTER TABLE knowledge_nodes
    ADD COLUMN IF NOT EXISTS tags JSONB DEFAULT '[]'::jsonb;

COMMENT ON COLUMN knowledge_nodes.tags IS
    'JSON array of strings: the row''s own tags (resources.tags, memory.tags) merged with tags derived by the knowledge extractor. Queried with PostgREST cs (@>) via .contains(tags, [...]); maps to the frontend GraphNode.tags field';

-- =============================================================
-- 2. Idempotent-upsert conflict target for nodes
-- =============================================================

CREATE UNIQUE INDEX IF NOT EXISTS uq_knowledge_nodes_user_source
    ON knowledge_nodes(user_id, type, source_table, source_id);

COMMENT ON INDEX uq_knowledge_nodes_user_source IS
    'Conflict target for knowledge extraction upserts — one node per (user, type, source row) makes POST /api/v1/knowledge/extract idempotent across repeat runs';

-- =============================================================
-- 3. Widen the node type vocabulary with 'goal'
-- Dropped conditionally so this file is re-runnable, and re-added
-- with an explicit name so the allowed set has one obvious home.
-- =============================================================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'knowledge_nodes'::regclass
          AND conname = 'knowledge_nodes_type_check'
    ) THEN
        ALTER TABLE knowledge_nodes DROP CONSTRAINT knowledge_nodes_type_check;
    END IF;
END $$;

ALTER TABLE knowledge_nodes
    ADD CONSTRAINT knowledge_nodes_type_check
    CHECK (type IN ('note', 'resource', 'idea', 'memory', 'course', 'task', 'goal'));

COMMENT ON COLUMN knowledge_nodes.type IS
    'Node kind: note, resource, idea, memory, course, task, goal. Superset of the frontend GraphNode union (''note'' | ''resource'' | ''idea''); the knowledge page falls back to a generic file icon for the other four';

-- =============================================================
-- 4. GIN index on tags
-- Mirrors idx_memory_tags in 015. Leading user_id scans still use
-- idx_knowledge_nodes_user_type; this one serves containment.
-- =============================================================

CREATE INDEX IF NOT EXISTS idx_knowledge_nodes_tags
    ON knowledge_nodes USING GIN(tags);

COMMIT;
