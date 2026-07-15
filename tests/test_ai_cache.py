"""Tests for AI response semantic cache."""

import time
import pytest
from shared.utils.ai_cache import AICache


class TestAICache:

    def test_exact_match_hit(self):
        cache = AICache(max_size=100, ttl_seconds=3600)
        cache.set("system1", "user1", "model1", "response1", estimated_tokens=50)
        result = cache.get("system1", "user1", "model1")
        assert result == "response1"
        assert cache._hits == 1
        assert cache._misses == 0

    def test_exact_match_miss(self):
        cache = AICache(max_size=100, ttl_seconds=3600)
        result = cache.get("system1", "nonexistent", "model1")
        assert result is None
        assert cache._hits == 0
        assert cache._misses == 1

    def test_ttl_expiration(self):
        cache = AICache(max_size=100, ttl_seconds=0)
        cache.set("s", "u", "m", "response")
        time.sleep(0.01)
        result = cache.get("s", "u", "m")
        assert result is None

    def test_max_size_eviction(self):
        cache = AICache(max_size=2, ttl_seconds=3600)
        cache.set("s1", "u1", "m", "r1")
        cache.set("s2", "u2", "m", "r2")
        cache.set("s3", "u3", "m", "r3")
        assert len(cache._exact_cache) == 2
        assert cache.get("s1", "u1", "m") is None
        assert cache.get("s3", "u3", "m") == "r3"

    def test_semantic_similarity_match(self):
        cache = AICache(max_size=100, ttl_seconds=3600)
        cache.set("system prompt", "what is the weather in paris today", "m", "sunny")
        result = cache.get("system prompt", "what is weather in Paris today", "m", similarity_threshold=0.7)
        assert result == "sunny"
        assert cache._hits == 1

    def test_semantic_similarity_below_threshold(self):
        cache = AICache(max_size=100, ttl_seconds=3600)
        cache.set("system prompt", "weather in paris", "m", "sunny")
        result = cache.get("system prompt", "quantum physics explained", "m", similarity_threshold=0.9)
        assert result is None
        assert cache._misses == 1

    def test_semantic_model_mismatch(self):
        cache = AICache(max_size=100, ttl_seconds=3600)
        cache.set("s", "hello world", "model_a", "response_a")
        result = cache.get("s", "hello world", "model_b", similarity_threshold=0.5)
        assert result is None

    def test_cache_clear(self):
        cache = AICache(max_size=100, ttl_seconds=3600)
        cache.set("s", "u", "m", "r")
        assert len(cache._exact_cache) == 1
        cache.clear()
        assert len(cache._exact_cache) == 0
        assert len(cache._semantic_cache) == 0
        assert cache._hits == 0
        assert cache._misses == 0
        assert cache._token_savings == 0

    def test_stats_calculation(self):
        cache = AICache(max_size=100, ttl_seconds=3600)
        cache._hits = 75
        cache._misses = 25
        cache._token_savings = 10000
        stats = cache.stats
        assert stats["hit_rate"] == 75.0
        assert stats["token_savings"] == 10000
        assert stats["estimated_cost_saved"] == pytest.approx(0.03, rel=0.01)
        assert stats["exact_entries"] == 0
        assert stats["semantic_entries"] == 0

    def test_stats_empty(self):
        cache = AICache(max_size=100, ttl_seconds=3600)
        stats = cache.stats
        assert stats["hit_rate"] == 0.0
        assert stats["hits"] == 0
        assert stats["misses"] == 0

    def test_invalidate_by_prefix(self):
        cache = AICache(max_size=100, ttl_seconds=3600)
        cache.set("s", "create task: buy groceries", "m", "ok")
        cache.set("s", "create task: do homework", "m", "ok")
        cache.set("s", "what is the weather", "m", "sunny")
        assert len(cache._semantic_cache) == 3
        cache.invalidate("create task")
        assert len(cache._semantic_cache) == 1
        assert cache._semantic_cache[0]["user_prompt"] == "what is the weather"

    def test_invalidate_clears_exact_cache(self):
        cache = AICache(max_size=100, ttl_seconds=3600)
        cache.set("s", "u", "m", "r")
        cache.invalidate("s")
        assert len(cache._exact_cache) == 0

    def test_invalidate_all(self):
        cache = AICache(max_size=100, ttl_seconds=3600)
        cache.set("s", "u", "m", "r")
        cache.invalidate()
        assert len(cache._exact_cache) == 0
        assert len(cache._semantic_cache) == 0

    def test_estimated_tokens_tracking(self):
        cache = AICache(max_size=100, ttl_seconds=3600)
        cache.set("s", "hello world", "m", "hi there", estimated_tokens=20)
        assert cache._token_savings == 20
        cache.set("s", "another", "m", "response", estimated_tokens=15)
        assert cache._token_savings == 35

    def test_get_returns_none_on_empty_cache(self):
        cache = AICache(max_size=100, ttl_seconds=3600)
        assert cache.get("s", "u", "m") is None

    def test_set_does_not_duplicate_on_same_key(self):
        cache = AICache(max_size=100, ttl_seconds=3600)
        cache.set("s", "u", "m", "r1")
        cache.set("s", "u", "m", "r2")
        assert len(cache._exact_cache) == 1
        assert cache.get("s", "u", "m") == "r2"

    def test_similarity_edge_empty_strings(self):
        cache = AICache(max_size=100, ttl_seconds=3600)
        sim = cache._get_similarity("", "")
        assert sim == 0.0
        sim = cache._get_similarity("hello", "")
        assert sim == 0.0
        sim = cache._get_similarity("", "world")
        assert sim == 0.0

    def test_similarity_exact(self):
        cache = AICache(max_size=100, ttl_seconds=3600)
        sim = cache._get_similarity("hello world", "hello world")
        assert sim == 1.0

    def test_similarity_partial(self):
        cache = AICache(max_size=100, ttl_seconds=3600)
        sim = cache._get_similarity("hello world foo", "hello world bar")
        assert sim == 2 / 4  # intersection=2 (hello, world), union=4

    def test_set_empty_response(self):
        cache = AICache(max_size=100, ttl_seconds=3600)
        cache.set("s", "u", "m", "", estimated_tokens=0)
        result = cache.get("s", "u", "m")
        assert result == ""

    def test_move_to_end_on_hit(self):
        cache = AICache(max_size=3, ttl_seconds=3600)
        cache.set("s1", "u1", "m", "r1")
        cache.set("s2", "u2", "m", "r2")
        cache.set("s3", "u3", "m", "r3")
        cache.get("s1", "u1", "m")
        cache.set("s4", "u4", "m", "r4")
        assert cache.get("s2", "u2", "m") is None
        assert cache.get("s1", "u1", "m") == "r1"

    def test_max_semantic_eviction(self):
        cache = AICache(max_size=4, ttl_seconds=3600)
        cache.set("s1", "u1", "m", "r1")
        cache.set("s2", "u2", "m", "r2")
        cache.set("s3", "u3", "m", "r3")
        cache.set("s4", "u4", "m", "r4")
        cache.set("s5", "u5", "m", "r5")
        # semantic cap = max_size // 2 = 2, after 5 inserts only last 2 remain
        assert cache._semantic_cache[0]["user_prompt"] == "u4"
        assert len(cache._semantic_cache) == 2

    def test_semantic_cache_ttl_skip(self):
        cache = AICache(max_size=100, ttl_seconds=0)
        cache.set("s", "long user query about something important", "m", "response")
        time.sleep(0.01)
        result = cache.get("s", "long user query about something", "m", similarity_threshold=0.7)
        assert result is None
