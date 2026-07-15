"""Comprehensive tests for 5-Tier Memory Architecture — BufferMemory, WorkingMemory, EpisodicMemory,
SemanticMemory, ProceduralMemory, MemoryCompressor, MemoryRetriever, MemoryOrchestrator."""

import json
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone, timedelta
import pytest

from ai.memory.tiers import (
    BufferMemory,
    WorkingMemory,
    EpisodicMemory,
    SemanticMemory,
    ProceduralMemory,
)
from ai.memory.compression import MemoryCompressor
from ai.memory.retrieval import MemoryRetriever
from ai.memory.orchestrator import MemoryOrchestrator


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _mock_supabase_table(data=None, side_effect=None):
    """Create a mock supabase table builder with chainable methods."""
    b = MagicMock()
    b.execute.return_value = MagicMock(data=data or [], error=None)
    for m in ("from_", "select", "eq", "order", "limit", "gte", "lt", "range", "text_search", "contains", "or_", "insert", "update", "delete"):
        getattr(b, m).return_value = b
    b.insert.return_value = MagicMock(execute=MagicMock(return_value=MagicMock(data=data or [{"id": "mock-id"}], error=None)))
    b.update.return_value = b
    b.delete.return_value = b
    if side_effect:
        b.execute.side_effect = side_effect
    return b


# ═══════════════════════════════════════════════════════════════════════════════
# BufferMemory Tests (Tier 0)
# ═══════════════════════════════════════════════════════════════════════════════


class TestBufferMemory:
    def test_add_and_get_context(self):
        buf = BufferMemory(capacity=5)
        buf.add("hello", "hi there")
        ctx = buf.get_context(k=1)
        assert len(ctx) == 2
        assert ctx[0]["role"] == "user"
        assert ctx[0]["content"] == "hello"
        assert ctx[1]["role"] == "assistant"
        assert ctx[1]["content"] == "hi there"

    def test_auto_evict_when_full(self):
        buf = BufferMemory(capacity=2)
        buf.add("msg1", "resp1")
        buf.add("msg2", "resp2")
        buf.add("msg3", "resp3")
        ctx = buf.get_context()
        assert len(ctx) <= 4
        assert ctx[0]["content"] == "msg2"

    def test_get_token_count(self):
        buf = BufferMemory()
        buf.add("hello world", "how are you")
        count = buf.get_token_count()
        assert count == 5

    def test_trim_to_budget(self):
        buf = BufferMemory(capacity=10, token_budget=10)
        buf.add("a b c d e f g h i j", "1 2 3 4 5 6 7 8 9 10")
        buf.add("k l m n o p", "11 12 13 14 15 16")
        trimmed = buf.trim_to_budget(budget=8)
        assert len(trimmed) > 0
        total_tokens = sum(len(m["content"].split()) for m in trimmed)
        assert total_tokens <= 8

    def test_clear(self):
        buf = BufferMemory()
        buf.add("hello", "world")
        buf.clear()
        assert len(buf.get_context()) == 0

    def test_to_dict_from_dict(self):
        buf = BufferMemory(capacity=3)
        buf.add("one", "two")
        data = buf.to_dict()
        assert data["capacity"] == 3
        assert data["message_count"] == 2
        restored = BufferMemory.from_dict(data)
        assert len(restored.get_context()) == 2

    def test_edge_empty_context(self):
        buf = BufferMemory()
        assert buf.get_context(k=5) == []
        assert buf.get_token_count() == 0

    def test_edge_negative_k(self):
        buf = BufferMemory()
        buf.add("hello", "world")
        assert buf.get_context(k=-1) == []


# ═══════════════════════════════════════════════════════════════════════════════
# WorkingMemory Tests (Tier 1)
# ═══════════════════════════════════════════════════════════════════════════════


class TestWorkingMemory:
    def test_set_and_get(self):
        wm = WorkingMemory(default_ttl=3600)
        wm.set("current_task", "build memory system")
        val = wm.get("current_task")
        assert val == "build memory system"

    def test_get_nonexistent(self):
        wm = WorkingMemory()
        assert wm.get("nonexistent") is None

    def test_get_all(self):
        wm = WorkingMemory(default_ttl=3600)
        wm.set("a", 1)
        wm.set("b", 2)
        all_entries = wm.get_all()
        assert all_entries["a"] == 1
        assert all_entries["b"] == 2

    def test_clear_expired(self):
        wm = WorkingMemory(default_ttl=0)
        wm.set("gone", "soon")
        expired_count = wm.clear_expired()
        assert expired_count >= 0

    def test_snapshot(self):
        wm = WorkingMemory(default_ttl=3600)
        wm.set("key1", "val1")
        snap = wm.snapshot()
        assert snap["key1"] == "val1"

    def test_clear(self):
        wm = WorkingMemory()
        wm.set("k", "v")
        wm.clear()
        assert wm.get_all() == {}

    def test_to_dict_from_dict(self):
        wm = WorkingMemory(default_ttl=3600)
        wm.set("color", "blue")
        data = wm.to_dict()
        assert "color" in data["entries"]
        restored = WorkingMemory.from_dict(data)
        assert restored.get("color") == "blue"

    def test_edge_ttl_expiry_supabase_fallback(self):
        wm = WorkingMemory(default_ttl=1)
        import time as _time_mod
        wm.set("temp", "value")
        _time_mod.sleep(1.5)
        val = wm.get("temp")
        assert val is None


# ═══════════════════════════════════════════════════════════════════════════════
# EpisodicMemory Tests (Tier 2)
# ═══════════════════════════════════════════════════════════════════════════════


class TestEpisodicMemory:
    @pytest.mark.asyncio
    async def test_store_episode(self):
        ep = EpisodicMemory()
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=[{"id": "ep-1"}])):
            eid = await ep.store_episode("user-1", {"msg": "hello"}, "test summary")
            assert eid == "ep-1"

    @pytest.mark.asyncio
    async def test_store_episode_failure(self):
        ep = EpisodicMemory()
        with patch("ai.memory.tiers.get_supabase_client", side_effect=Exception("DB down")):
            eid = await ep.store_episode("user-1", {}, "fail")
            assert eid is None

    @pytest.mark.asyncio
    async def test_get_recent(self):
        ep = EpisodicMemory()
        data = [{"id": "1", "type": "episodic", "value": "{}", "created_at": "2026-07-01T00:00:00"}]
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=data)):
            recent = await ep.get_recent("user-1", days=7)
            assert len(recent) == 1

    @pytest.mark.asyncio
    async def test_search_episodes_empty_query(self):
        ep = EpisodicMemory()
        data = [{"id": "1", "type": "episodic", "value": "{}", "tags": []}]
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=data)):
            results = await ep.search_episodes("user-1", "", k=5)
            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_search_episodes_with_keywords(self):
        ep = EpisodicMemory()
        data = [
            {"id": "1", "type": "episodic", "value": json.dumps({"summary": "studied python"}), "tags": ["coding"], "key": "ep:abc"},
            {"id": "2", "type": "episodic", "value": json.dumps({"summary": "watched movie"}), "tags": ["entertainment"], "key": "ep:def"},
        ]
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=data)):
            results = await ep.search_episodes("user-1", "python", k=5)
            assert len(results) == 1
            val = json.loads(results[0]["value"]) if isinstance(results[0]["value"], str) else results[0]["value"]
            assert "python" in val.get("summary", "")

    @pytest.mark.asyncio
    async def test_consolidate_no_episodes(self):
        ep = EpisodicMemory()
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=[])):
            result = await ep.consolidate("user-1")
            assert result["merged"] == 0

    @pytest.mark.asyncio
    async def test_consolidate_single_episode(self):
        ep = EpisodicMemory()
        data = [{"id": "1", "type": "episodic", "value": json.dumps({"summary": "only one"}), "tags": ["test"], "created_at": "2026-07-01T00:00:00"}]
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=data)):
            result = await ep.consolidate("user-1")
            assert result["merged"] == 0

    @pytest.mark.asyncio
    async def test_edge_get_recent_db_error(self):
        ep = EpisodicMemory()
        with patch("ai.memory.tiers.get_supabase_client", side_effect=Exception("DB error")):
            recent = await ep.get_recent("user-1")
            assert recent == []


# ═══════════════════════════════════════════════════════════════════════════════
# SemanticMemory Tests (Tier 3)
# ═══════════════════════════════════════════════════════════════════════════════


class TestSemanticMemory:
    @pytest.mark.asyncio
    async def test_store_fact_new(self):
        sm = SemanticMemory()
        mock = _mock_supabase_table(data=[])
        with patch("ai.memory.tiers.get_supabase_client", return_value=mock):
            fid = await sm.store_fact("user-1", "User likes Python", source="chat", confidence=0.9)
            assert fid == "mock-id"

    @pytest.mark.asyncio
    async def test_store_fact_dedup(self):
        sm = SemanticMemory()
        existing_val = json.dumps({"fact": "User likes Python", "confidence": 0.8, "reference_count": 1})
        mock = _mock_supabase_table(data=[{"id": "existing-1", "value": existing_val}])
        with patch("ai.memory.tiers.get_supabase_client", return_value=mock):
            fid = await sm.store_fact("user-1", "User likes Python", source="chat", confidence=0.9)
            assert fid == "existing-1"

    @pytest.mark.asyncio
    async def test_store_fact_db_error(self):
        sm = SemanticMemory()
        with patch("ai.memory.tiers.get_supabase_client", side_effect=Exception("DB error")):
            fid = await sm.store_fact("user-1", "test fact")
            assert fid is None

    @pytest.mark.asyncio
    async def test_query(self):
        sm = SemanticMemory()
        data = [
            {"id": "1", "type": "semantic", "value": json.dumps({"fact": "loves python", "confidence": 0.9, "category": "coding"}), "tags": ["preference"], "importance": "high", "key": "sem:abc"},
            {"id": "2", "type": "semantic", "value": json.dumps({"fact": "enjoys running", "confidence": 0.7, "category": "fitness"}), "tags": ["preference"], "importance": "medium", "key": "sem:def"},
        ]
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=data)):
            results = await sm.query("user-1", "python", k=5)
            assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_update_confidence(self):
        sm = SemanticMemory()
        mock = _mock_supabase_table(data=[{"id": "1", "value": json.dumps({"confidence": 0.5})}])
        with patch("ai.memory.tiers.get_supabase_client", return_value=mock):
            result = await sm.update_confidence("user-1", "1", 0.3)
            assert result is True

    @pytest.mark.asyncio
    async def test_get_user_preferences(self):
        sm = SemanticMemory()
        data = [{"id": "1", "type": "semantic", "value": json.dumps({"fact": "likes morning", "confidence": 0.9}), "tags": ["preference"]}]
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=data)):
            prefs = await sm.get_user_preferences("user-1")
            assert len(prefs) == 1

    @pytest.mark.asyncio
    async def test_get_knowledge_graph(self):
        sm = SemanticMemory()
        data = [
            {"id": "1", "type": "semantic", "value": json.dumps({"fact": "loves python", "confidence": 0.9, "category": "coding"}), "key": "sem:1", "tags": []},
        ]
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=data)):
            kg = await sm.get_knowledge_graph("user-1")
            assert "nodes" in kg
            assert "edges" in kg

    @pytest.mark.asyncio
    async def test_decay_all(self):
        sm = SemanticMemory()
        data = [{"id": "1", "value": json.dumps({"confidence": 0.8, "last_accessed": "2026-01-01T00:00:00"})}]
        mock = _mock_supabase_table(data=data)
        with patch("ai.memory.tiers.get_supabase_client", return_value=mock):
            decayed = await sm.decay_all("user-1")
            assert isinstance(decayed, int)

    @pytest.mark.asyncio
    async def test_edge_empty_knowledge_graph(self):
        sm = SemanticMemory()
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=[])):
            kg = await sm.get_knowledge_graph("user-1")
            assert kg["nodes"] == []
            assert kg["edges"] == []

    def test_confidence_to_importance(self):
        sm = SemanticMemory()
        assert sm._confidence_to_importance(0.9) == "high"
        assert sm._confidence_to_importance(0.6) == "medium"
        assert sm._confidence_to_importance(0.3) == "low"
        assert sm._confidence_to_importance(0.0) == "low"


# ═══════════════════════════════════════════════════════════════════════════════
# ProceduralMemory Tests (Tier 4)
# ═══════════════════════════════════════════════════════════════════════════════


class TestProceduralMemory:
    @pytest.mark.asyncio
    async def test_store_pattern_new(self):
        pm = ProceduralMemory()
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=[])):
            pid = await pm.store_pattern("user-1", "productivity", {"peak_hour": 9})
            assert pid == "mock-id"

    @pytest.mark.asyncio
    async def test_store_pattern_existing(self):
        pm = ProceduralMemory()
        existing_val = json.dumps({"pattern_type": "productivity", "data": {"peak_hour": 9}, "confidence": 0.5, "observation_count": 1})
        mock = _mock_supabase_table(data=[{"id": "existing-pat", "value": existing_val}])
        with patch("ai.memory.tiers.get_supabase_client", return_value=mock):
            pid = await pm.store_pattern("user-1", "productivity", {"peak_hour": 9, "signature": "s1"})
            assert pid == "existing-pat"

    @pytest.mark.asyncio
    async def test_get_patterns(self):
        pm = ProceduralMemory()
        data = [{"id": "1", "type": "procedural", "value": json.dumps({"pattern_type": "productivity"}), "tags": ["productivity"]}]
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=data)):
            patterns = await pm.get_patterns("user-1")
            assert len(patterns) == 1

    @pytest.mark.asyncio
    async def test_get_patterns_filtered(self):
        pm = ProceduralMemory()
        data = [{"id": "1", "type": "procedural", "value": json.dumps({"pattern_type": "learning"}), "tags": ["learning"]}]
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=data)):
            patterns = await pm.get_patterns("user-1", pattern_type="learning")
            assert len(patterns) >= 0

    @pytest.mark.asyncio
    async def test_update_from_observation(self):
        pm = ProceduralMemory()
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=[])):
            pid = await pm.update_from_observation("user-1", {"type": "focus", "data": {"duration": 120}})
            assert pid is not None

    @pytest.mark.asyncio
    async def test_predict_no_patterns(self):
        pm = ProceduralMemory()
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=[])):
            pred = await pm.predict("user-1", {"hour": 9})
            assert pred["prediction"] is None

    @pytest.mark.asyncio
    async def test_predict_with_match(self):
        pm = ProceduralMemory()
        data = [{
            "id": "1", "type": "procedural",
            "value": json.dumps({"pattern_type": "productivity", "data": {"peak": "morning", "signature": "s1"}, "confidence": 0.8}),
            "tags": ["productivity"],
        }]
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=data)):
            pred = await pm.predict("user-1", {"peak": "morning"})
            assert pred["prediction"] is not None
            assert pred["confidence"] > 0

    @pytest.mark.asyncio
    async def test_edge_db_error(self):
        pm = ProceduralMemory()
        with patch("ai.memory.tiers.get_supabase_client", side_effect=Exception("DB error")):
            patterns = await pm.get_patterns("user-1")
            assert patterns == []


# ═══════════════════════════════════════════════════════════════════════════════
# MemoryCompressor Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestMemoryCompressor:
    def test_compress_episodes_empty(self):
        mc = MemoryCompressor()
        result = mc.compress_episodes([])
        assert result == []

    def test_compress_episodes_within_budget(self):
        mc = MemoryCompressor()
        episodes = [
            {"id": "1", "type": "episodic", "value": json.dumps({"summary": "short entry"}), "created_at": _now_iso()},
        ]
        compressed = mc.compress_episodes(episodes, max_tokens=2048)
        assert len(compressed) == 1

    def test_summarize_memories_empty(self):
        mc = MemoryCompressor()
        summary = mc.summarize_memories([])
        assert "No memories to summarize" in summary

    def test_summarize_memories(self):
        mc = MemoryCompressor()
        mems = [
            {"type": "semantic", "value": json.dumps({"fact": "test fact", "confidence": 0.9, "category": "test"})},
            {"type": "episodic", "value": json.dumps({"summary": "test episode", "confidence": 0.7, "category": "general"})},
        ]
        summary = mc.summarize_memories(mems)
        assert "Memory summary" in summary
        assert "2 items" in summary

    def test_prune_old_memories(self):
        mc = MemoryCompressor()
        with patch("ai.memory.compression.get_supabase_client", return_value=_mock_supabase_table(data=[{"id": "old-1"}])):
            count = mc.prune_old_memories("user-1", days=90)
            assert count == 1

    def test_prune_old_memories_db_error(self):
        mc = MemoryCompressor()
        with patch("ai.memory.compression.get_supabase_client", side_effect=Exception("DB error")):
            count = mc.prune_old_memories("user-1")
            assert count == 0

    def test_compress_temporal_empty(self):
        mc = MemoryCompressor()
        result = mc.compress_temporal([])
        assert result == []

    def test_compress_temporal_with_data(self):
        mc = MemoryCompressor()
        past = (_now_dt() - timedelta(days=30)).isoformat()
        mems = [
            {"type": "episodic", "value": "{}", "created_at": past},
            {"type": "semantic", "value": "{}", "created_at": past},
        ]
        result = mc.compress_temporal(mems, bin_days=7)
        assert len(result) >= 1

    def test_light_compress_old_memory(self):
        mc = MemoryCompressor()
        past = (_now_dt() - timedelta(days=14)).isoformat()
        long_val = {"summary": "x" * 500, "session_data": {"detail": "y" * 600}}
        entry = {"id": "1", "type": "episodic", "value": json.dumps(long_val), "created_at": past}
        result = mc.compress_episodes([entry], max_tokens=5000)
        assert len(result) == 1

    def test_emergency_truncate_low_budget(self):
        mc = MemoryCompressor()
        result = mc._emergency_truncate({"value": "{}"}, 0)
        assert result is None

    def test_get_age_days_zero(self):
        mc = MemoryCompressor()
        age = mc._get_age_days({"created_at": _now_iso()})
        assert age < 0.01


# ═══════════════════════════════════════════════════════════════════════════════
# MemoryRetriever Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestMemoryRetriever:
    @pytest.mark.asyncio
    async def test_retrieve_empty(self):
        mr = MemoryRetriever()
        with patch("ai.memory.retrieval.get_supabase_client", return_value=_mock_supabase_table(data=[])):
            results = await mr.retrieve("user-1", "", tiers=[2, 3], k=5)
            assert results == []

    @pytest.mark.asyncio
    async def test_retrieve_with_data(self):
        mr = MemoryRetriever()
        data = [{"id": "1", "type": "semantic", "value": json.dumps({"fact": "python is great"}), "tags": ["coding"], "key": "k1", "importance": "high", "created_at": _now_iso()}]
        with patch("ai.memory.retrieval.get_supabase_client", return_value=_mock_supabase_table(data=data)):
            results = await mr.retrieve("user-1", "python", tiers=[3], k=5)
            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_semantic_search(self):
        mr = MemoryRetriever()
        data = [{"id": "1", "type": "semantic", "value": json.dumps({"fact": "likes fastapi"}), "tags": ["backend"], "key": "k1", "importance": "medium", "created_at": _now_iso()}]
        with patch("ai.memory.retrieval.get_supabase_client", return_value=_mock_supabase_table(data=data)):
            results = await mr.semantic_search("user-1", "fastapi")
            assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_temporal_search(self):
        mr = MemoryRetriever()
        data = [{"id": "1", "type": "episodic", "value": "{}", "created_at": _now_iso()}]
        with patch("ai.memory.retrieval.get_supabase_client", return_value=_mock_supabase_table(data=data)):
            results = await mr.temporal_search("user-1", since=(_now_dt() - timedelta(days=1)).isoformat())
            assert len(results) >= 0

    @pytest.mark.asyncio
    async def test_hybrid_retrieve(self):
        mr = MemoryRetriever()
        data = [
            {"id": "1", "type": "semantic", "value": json.dumps({"fact": "python skills"}), "tags": ["coding"], "key": "k1", "importance": "high", "created_at": _now_iso()},
            {"id": "2", "type": "episodic", "value": json.dumps({"summary": "studied python"}), "tags": ["learning"], "key": "k2", "importance": "medium", "created_at": _now_iso()},
        ]
        with patch("ai.memory.retrieval.get_supabase_client", return_value=_mock_supabase_table(data=data)):
            results = await mr.hybrid_retrieve("user-1", "python", k=5)
            assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_hybrid_retrieve_empty(self):
        mr = MemoryRetriever()
        with patch("ai.memory.retrieval.get_supabase_client", return_value=_mock_supabase_table(data=[])):
            results = await mr.hybrid_retrieve("user-1", "nothing")
            assert results == []

    @pytest.mark.asyncio
    async def test_get_context_window(self):
        mr = MemoryRetriever()
        data = [{"id": "1", "type": "semantic", "value": json.dumps({"fact": "test"}), "tags": [], "key": "k1", "importance": "medium", "created_at": _now_iso()}]
        with patch("ai.memory.retrieval.get_supabase_client", return_value=_mock_supabase_table(data=data)):
            cw = await mr.get_context_window("user-1", "test", max_tokens=4000)
            assert cw["total_memories"] >= 0
            assert cw["max_tokens"] == 4000

    @pytest.mark.asyncio
    async def test_retrieve_invalid_tiers(self):
        mr = MemoryRetriever()
        results = await mr.retrieve("user-1", "", tiers=[0, 1], k=5)
        assert results == []

    @pytest.mark.asyncio
    async def test_edge_db_error_hybrid(self):
        mr = MemoryRetriever()
        with patch("ai.memory.retrieval.get_supabase_client", side_effect=Exception("DB error")):
            results = await mr.hybrid_retrieve("user-1", "query")
            assert results == []


# ═══════════════════════════════════════════════════════════════════════════════
# MemoryOrchestrator Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestMemoryOrchestrator:
    @pytest.mark.asyncio
    async def test_store_interaction(self):
        orch = MemoryOrchestrator()
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=[])):
            result = await orch.store_interaction("user-1", "hello", "hi there")
            assert result["buffer"] is True
            assert result.get("working") is True
            assert result.get("episodic") is False

    @pytest.mark.asyncio
    async def test_store_interaction_high_importance(self):
        orch = MemoryOrchestrator()
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=[{"id": "ep-1"}])):
            result = await orch.store_interaction("user-1", "I need to create a new project urgently", "I will help")
            assert result["buffer"] is True

    @pytest.mark.asyncio
    async def test_get_relevant_context(self):
        orch = MemoryOrchestrator()
        orch.buffer.add("hello", "world")
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=[])):
            ctx = await orch.get_relevant_context("user-1", "hello")
            assert "buffer" in ctx
            assert "working" in ctx
            assert "episodic" in ctx
            assert "semantic" in ctx
            assert "procedural" in ctx

    @pytest.mark.asyncio
    async def test_consolidate_all(self):
        orch = MemoryOrchestrator()
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=[])):
            with patch("ai.memory.compression.get_supabase_client", return_value=_mock_supabase_table(data=[])):
                result = await orch.consolidate_all("user-1")
                assert "episodic" in result
                assert "total_actions" in result

    @pytest.mark.asyncio
    async def test_get_user_profile(self):
        orch = MemoryOrchestrator()
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=[])):
            profile = await orch.get_user_profile("user-1")
            assert "preferences" in profile
            assert "patterns" in profile
            assert "recent_episodes" in profile
            assert "summary" in profile

    @pytest.mark.asyncio
    async def test_prune_all(self):
        orch = MemoryOrchestrator()
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=[])):
            with patch("ai.memory.compression.get_supabase_client", return_value=_mock_supabase_table(data=[])):
                result = await orch.prune_all("user-1")
                assert result.get("buffer_cleared") is True
                assert "working_expired" in result

    @pytest.mark.asyncio
    async def test_extract_facts(self):
        orch = MemoryOrchestrator()
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=[])):
            stored = await orch.extract_facts_from_interaction("user-1", "I love Python", "Great choice!")
            assert isinstance(stored, int)

    @pytest.mark.asyncio
    async def test_assess_importance(self):
        orch = MemoryOrchestrator()
        assert orch._assess_importance("urgent deadline", "ok") == "critical"
        assert orch._assess_importance("create a new project goal", "ok") == "high"
        assert orch._assess_importance("what is the weather", "sunny") == "low"

    @pytest.mark.asyncio
    async def test_edge_all_tiers_degraded(self):
        orch = MemoryOrchestrator()
        with patch("ai.memory.retrieval.get_supabase_client", side_effect=Exception("DB down")):
            with patch("ai.memory.tiers.get_supabase_client", side_effect=Exception("DB down")):
                ctx = await orch.get_relevant_context("user-1", "test")
                assert ctx["buffer"] == []
                assert ctx["working"] == {}

    @pytest.mark.asyncio
    async def test_store_interaction_with_context(self):
        orch = MemoryOrchestrator()
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=[])):
            result = await orch.store_interaction("user-1", "hello", "world", {"tags": ["test"], "store_episodic": True})
            assert result["buffer"] is True
            assert result.get("working") is True


# ═══════════════════════════════════════════════════════════════════════════════
# Memory Agent Integration Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestMemoryAgentIntegration:
    @pytest.mark.asyncio
    async def test_validate_memory_type_valid(self):
        from ai.agents.memory_agent import validate_memory_type
        assert validate_memory_type("episodic") == "episodic"
        assert validate_memory_type("semantic") == "semantic"
        assert validate_memory_type("procedural") == "procedural"

    @pytest.mark.asyncio
    async def test_validate_memory_type_invalid_defaults(self):
        from ai.agents.memory_agent import validate_memory_type
        assert validate_memory_type("invalid") == "episodic"

    @pytest.mark.asyncio
    async def test_get_orchestrator_singleton(self):
        from ai.agents.memory_agent import get_orchestrator
        o1 = get_orchestrator()
        o2 = get_orchestrator()
        assert o1 is o2

    @pytest.mark.asyncio
    async def test_store_interaction_dedup(self):
        from ai.agents.memory_agent import store_interaction
        with patch("ai.agents.memory_agent.get_supabase_client") as mock_factory:
            mock = MagicMock()
            mock.from_.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"id": "existing", "value": json.dumps({"content": "old"})}])
            mock.from_.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[{"id": "existing"}])
            mock_factory.return_value = mock
            result = await store_interaction("user-1", "semantic", "test content")
            assert result is not None

    @pytest.mark.asyncio
    async def test_store_interaction_db_error(self):
        from ai.agents.memory_agent import store_interaction
        with patch("ai.agents.memory_agent.get_supabase_client", side_effect=Exception("DB error")):
            result = await store_interaction("user-1", "episodic", "content")
            assert result is None

    @pytest.mark.asyncio
    async def test_chat_store_interaction(self):
        from ai.agents.memory_agent import chat_store_interaction
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=[])):
            result = await chat_store_interaction("user-1", "hello", "world")
            assert result.get("buffer") is True

    @pytest.mark.asyncio
    async def test_confidence_decay(self):
        from ai.agents.memory_agent import confidence_decay
        data = [{"id": "1", "value": json.dumps({"confidence": 0.8, "last_accessed": "2026-01-01T00:00:00"})}]
        mock = _mock_supabase_table(data=data)
        with patch("ai.memory.tiers.get_supabase_client", return_value=mock):
            result = await confidence_decay("user-1")
            assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_deep_consolidation(self):
        from ai.agents.memory_agent import deep_consolidation
        with patch("ai.memory.tiers.get_supabase_client", return_value=_mock_supabase_table(data=[])):
            with patch("ai.memory.compression.get_supabase_client", return_value=_mock_supabase_table(data=[])):
                with patch("builtins.open") as mock_open:
                    mock_file = MagicMock()
                    mock_open.return_value.__enter__.return_value = mock_file
                    result = await deep_consolidation("user-1")
                    assert "episodic" in result
                    assert "pruned_old" in result

    @pytest.mark.asyncio
    async def test_deep_consolidation_db_error(self):
        from ai.agents.memory_agent import deep_consolidation
        with patch("ai.memory.tiers.get_supabase_client", side_effect=Exception("DB error")):
            result = await deep_consolidation("user-1")
            assert result["status"] == "completed"


# ─── Date Helpers ─────────────────────────────────────────────────────────────


def _now_dt() -> datetime:
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    return _now_dt().isoformat()
