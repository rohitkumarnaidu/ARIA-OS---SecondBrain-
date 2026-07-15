"""Tests for EmbeddingService: generation, caching, batching, error handling, edge cases."""

import pytest
from unittest.mock import AsyncMock, patch
from typing import List


@pytest.fixture
def embedder():
    from ai.embeddings import EmbeddingService

    svc = EmbeddingService(
        ollama_base_url="http://localhost:11434",
        openai_api_key=None,
        use_local=True,
        model="nomic-embed-text",
        cache_size=10,
        cache_ttl=3600,
    )
    svc._cache = {}
    svc._stats = {"hits": 0, "misses": 0, "ollama_calls": 0, "openai_calls": 0, "fallbacks": 0}
    return svc


class TestGenerateEmbedding:
    @pytest.mark.asyncio
    async def test_generates_768d_vector(self, embedder):
        with patch.object(embedder, "_call_ollama", new=AsyncMock(return_value=[0.1] * 768)):
            result = await embedder.generate_embedding("test text")
            assert len(result) == 768
            assert all(isinstance(v, float) for v in result)

    @pytest.mark.asyncio
    async def test_returns_cached_result(self, embedder):
        cached_vec = [0.5] * 768
        embedder._cache[embedder._cache_key("hello", embedder.model)] = {
            "embedding": cached_vec, "time": __import__("time").time()
        }
        with patch.object(embedder, "_call_ollama", new=AsyncMock()) as mock:
            result = await embedder.generate_embedding("hello")
            assert result == cached_vec
            mock.assert_not_called()
            assert embedder._stats["hits"] == 1

    @pytest.mark.asyncio
    async def test_empty_text_returns_zero_vector(self, embedder):
        result = await embedder.generate_embedding("")
        assert len(result) == 768
        assert all(v == 0.0 for v in result)

        result = await embedder.generate_embedding("   ")
        assert len(result) == 768
        assert all(v == 0.0 for v in result)

    @pytest.mark.asyncio
    async def test_ollama_failure_falls_to_openai(self, embedder):
        embedder.openai_key = "sk-test"
        embedder.use_local = True
        ollama_mock = AsyncMock(side_effect=Exception("Ollama down"))
        openai_mock = AsyncMock(return_value=[0.2] * 768)

        with patch.object(embedder, "_call_ollama", ollama_mock):
            with patch.object(embedder, "_call_openai", openai_mock):
                result = await embedder.generate_embedding("fallback test")
                assert len(result) == 768
                assert embedder._stats["fallbacks"] >= 1

    @pytest.mark.asyncio
    async def test_all_providers_exhausted_returns_zero(self, embedder):
        with patch.object(embedder, "_call_ollama", new=AsyncMock(side_effect=Exception("fail"))):
            result = await embedder.generate_embedding("failing text")
            assert len(result) == 768
            assert all(v == 0.0 for v in result)

    @pytest.mark.asyncio
    async def test_long_text_truncated_gracefully(self, embedder):
        long_text = "word " * 10000
        with patch.object(embedder, "_call_ollama", new=AsyncMock(return_value=[0.3] * 768)):
            result = await embedder.generate_embedding(long_text)
            assert len(result) == 768

    @pytest.mark.asyncio
    async def test_respects_preferred_model(self, embedder):
        embedder.openai_key = "sk-test"
        with patch.object(embedder, "_call_openai", new=AsyncMock(return_value=[0.4] * 1536)) as mock:
            result = await embedder.generate_embedding("openai test", preferred_model="text-embedding-ada-002")
            assert len(result) == 1536

    @pytest.mark.asyncio
    async def test_cache_expires(self, embedder):
        embedder._cache_ttl = -1
        embedder._cache[embedder._cache_key("stale", embedder.model)] = {
            "embedding": [0.9] * 768, "time": 0
        }
        with patch.object(embedder, "_call_ollama", new=AsyncMock(return_value=[0.1] * 768)) as mock:
            result = await embedder.generate_embedding("stale")
            mock.assert_called_once()
            assert embedder._stats["misses"] >= 1


class TestGenerateEmbeddings:
    @pytest.mark.asyncio
    async def test_batch_generates_all(self, embedder):
        texts = ["hello", "world", "test"]
        vec = [0.1] * 768

        with patch.object(embedder, "_ollama_embed_batch", new=AsyncMock(return_value=[vec, vec, vec])):
            results = await embedder.generate_embeddings(texts)
            assert len(results) == 3
            assert all(len(r) == 768 for r in results)

    @pytest.mark.asyncio
    async def test_batch_empty_list(self, embedder):
        results = await embedder.generate_embeddings([])
        assert results == []

    @pytest.mark.asyncio
    async def test_batch_uses_cache(self, embedder):
        cached = [0.5] * 768
        embedder._cache[embedder._cache_key("cached_text", embedder.model)] = {
            "embedding": cached, "time": __import__("time").time()
        }
        texts = ["cached_text", "new_text"]
        new_vec = [0.2] * 768

        with patch.object(embedder, "_ollama_embed_batch", new=AsyncMock(return_value=[new_vec])):
            results = await embedder.generate_embeddings(texts)
            assert len(results) == 2
            assert results[0] == cached
            assert results[1] == new_vec

    @pytest.mark.asyncio
    async def test_batch_mixed_cache_and_new(self, embedder):
        embedder._cache[embedder._cache_key("a", embedder.model)] = {
            "embedding": [0.1] * 768, "time": __import__("time").time()
        }
        with patch.object(embedder, "_ollama_embed_batch", new=AsyncMock(return_value=[[0.2] * 768])):
            results = await embedder.generate_embeddings(["a", "b"])
            assert len(results) == 2
            assert results[0] == [0.1] * 768
            assert results[1] == [0.2] * 768

    @pytest.mark.asyncio
    async def test_batch_fallback_on_failure(self, embedder):
        with patch.object(embedder, "_ollama_embed_batch", new=AsyncMock(return_value=[[0.0] * 768, [0.0] * 768])):
            results = await embedder.generate_embeddings(["x", "y"])
            assert len(results) == 2
            assert all(v == 0.0 for v in results[0])


class TestCacheManagement:
    def test_clear_cache(self, embedder):
        embedder._cache["test"] = {"embedding": [0.1] * 768, "time": 0}
        embedder.clear_cache()
        assert len(embedder._cache) == 0

    def test_invalidate_specific(self, embedder):
        embedder._cache[embedder._cache_key("specific", embedder.model)] = {
            "embedding": [0.1] * 768, "time": 0
        }
        embedder.invalidate_cache(text="specific", model=embedder.model)
        assert embedder._cache_key("specific", embedder.model) not in embedder._cache

    def test_cache_max_size_eviction(self, embedder):
        embedder._cache_max = 2
        embedder._cache["a"] = {"embedding": [0.1] * 768, "time": 1}
        embedder._cache["b"] = {"embedding": [0.2] * 768, "time": 2}
        embedder._set_cache("c", embedder.model, [0.3] * 768)
        assert len(embedder._cache) <= 2

    def test_stats_cache_hit_rate(self, embedder):
        embedder._stats["hits"] = 80
        embedder._stats["misses"] = 20
        stats = embedder.stats
        assert stats["cache_hit_rate"] == 80.0


class TestProviderSelection:
    @pytest.mark.asyncio
    async def test_use_local_ollama(self, embedder):
        embedder.use_local = True
        embedder.openai_key = None
        providers = embedder._get_providers()
        assert len(providers) == 1
        assert providers[0][0] == "ollama"

    @pytest.mark.asyncio
    async def test_use_openai_when_configured(self, embedder):
        embedder.use_local = False
        embedder.openai_key = "sk-test"
        providers = embedder._get_providers()
        assert any(p[0] == "openai" for p in providers)

    @pytest.mark.asyncio
    async def test_both_providers_available(self, embedder):
        embedder.use_local = True
        embedder.openai_key = "sk-test"
        providers = embedder._get_providers()
        assert len(providers) == 2
        assert providers[0][0] == "ollama"
        assert providers[1][0] == "openai"


class TestEdgeCases:
    @pytest.mark.asyncio
    async def test_unicode_text(self, embedder):
        with patch.object(embedder, "_call_ollama", new=AsyncMock(return_value=[0.1] * 768)):
            result = await embedder.generate_embedding("你好世界 ñoño  🔥")
            assert len(result) == 768

    @pytest.mark.asyncio
    async def test_very_short_text(self, embedder):
        with patch.object(embedder, "_call_ollama", new=AsyncMock(return_value=[0.1] * 768)):
            result = await embedder.generate_embedding("a")
            assert len(result) == 768

    @pytest.mark.asyncio
    async def test_concurrent_requests_dont_corrupt_cache(self, embedder):
        import asyncio

        async def embed_task(t: str) -> List[float]:
            return await embedder.generate_embedding(t)

        texts = ["t1", "t2", "t3", "t1", "t2"]
        with patch.object(embedder, "_call_ollama", new=AsyncMock(return_value=[0.1] * 768)):
            tasks = [embed_task(t) for t in texts]
            results = await asyncio.gather(*tasks)
            assert len(results) == 5
            assert all(len(r) == 768 for r in results)
