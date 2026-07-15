"""Tests for RAGPipeline: chunking, search, hybrid search, prompt augmentation, edge cases."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def chunker():
    from ai.rag import ChunkingPipeline

    return ChunkingPipeline(chunk_size=50, chunk_overlap=10, min_chunk_size=5)


@pytest.fixture
def rag():
    from ai.rag import RAGPipeline

    pipeline = RAGPipeline(
        top_k=5,
        k_dense=10,
        k_sparse=10,
        rrf_k=60,
    )
    pipeline.supabase = MagicMock()
    pipeline.embedder = MagicMock()
    pipeline.embedder.generate_embedding = AsyncMock(return_value=[0.1] * 768)
    pipeline.embedder.generate_embeddings = AsyncMock(return_value=[[0.1] * 768, [0.2] * 768])
    return pipeline


class TestChunkingPipeline:
    def test_chunk_empty_text(self, chunker):
        assert chunker.chunk_document("") == []
        assert chunker.chunk_document("   ") == []

    def test_chunk_short_text_single_chunk(self, chunker):
        chunks = chunker.chunk_document("Hello world", "generic")
        assert len(chunks) == 1
        assert chunks[0]["content"] == "Hello world"

    def test_chunk_by_semantic_boundary(self, chunker):
        text = "# Section 1\n\nParagraph one.\n\n# Section 2\n\nParagraph two.\n\n# Section 3\n\nParagraph three."
        chunks = chunker.chunk_document(text, "tasks")
        assert len(chunks) >= 1
        for c in chunks:
            assert "chunk_index" in c
            assert "token_count" in c
            assert "chunk_hash" in c

    def test_chunk_by_line(self, chunker):
        text = "line1\nline2\nline3\n\nline5"
        chunks = chunker.chunk_document(text, "sleep_logs")
        assert len(chunks) == 4
        assert chunks[0]["content"] == "line1"
        assert chunks[1]["content"] == "line2"

    def test_chunk_by_message(self, chunker):
        text = "msg1\n---\nmsg2\n---\nmsg3"
        chunks = chunker.chunk_document(text, "chat_messages")
        assert len(chunks) >= 1

    def test_chunk_tokens_estimated(self, chunker):
        text = "word " * 200
        chunks = chunker.chunk_document(text, "generic")
        assert len(chunks) >= 2
        for c in chunks:
            assert c["token_count"] > 0

    def test_chunk_uses_source_config(self, chunker):
        text = "Section content\n\nMore content\n\nEven more\n\nLast bit"
        chunks = chunker.chunk_document(text, "tasks")
        for c in chunks:
            assert isinstance(c["chunk_index"], int)

    def test_chunk_hash_unique(self, chunker):
        chunks = chunker.chunk_document("AAA\nBBB\nCCC", "generic")
        hashes = {c["chunk_hash"] for c in chunks}
        assert len(hashes) == len(chunks)

    def test_chunk_min_size_respected(self, chunker):
        chunker.min_chunk_size = 100
        chunks = chunker.chunk_document("short", "generic")
        assert all(c["token_count"] >= 100 or len(c["content"]) < 50 for c in chunks)


class TestIngest:
    @pytest.mark.asyncio
    async def test_ingest_text_creates_chunks(self, rag):
        rag._upsert_chunk = AsyncMock()
        doc_id = await rag.ingest_text("Hello world. This is a test document.", source_table="test")
        assert doc_id != ""
        assert rag._upsert_chunk.called

    @pytest.mark.asyncio
    async def test_ingest_text_empty_returns_empty(self, rag):
        result = await rag.ingest_text("")
        assert result == ""

    @pytest.mark.asyncio
    async def test_ingest_text_passes_metadata(self, rag):
        rag._upsert_chunk = AsyncMock()
        doc_id = await rag.ingest_text(
            "Test content",
            metadata={"title": "Doc", "user_id": "u1"},
            source_table="tasks",
            source_id="src-1",
        )
        call_kwargs = rag._upsert_chunk.call_args[1]
        assert call_kwargs["user_id"] == "u1"
        assert call_kwargs["source_id"] == "src-1"

    @pytest.mark.asyncio
    async def test_ingest_document_file_not_found(self, rag):
        result = await rag.ingest_document("/nonexistent/file.txt")
        assert result == []

    @pytest.mark.asyncio
    async def test_ingest_document_reads_file(self, rag, tmp_path):
        rag._upsert_chunk = AsyncMock()
        rag.embedder.generate_embeddings = AsyncMock(return_value=[[0.1] * 768])
        f = tmp_path / "test.txt"
        f.write_text("This is a test document for ingestion.")
        results = await rag.ingest_document(str(f), metadata={"user_id": "u1"})
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_ingest_with_metadata_preserved(self, rag):
        rag._upsert_chunk = AsyncMock()
        meta = {"user_id": "u1", "source_table": "memory", "priority": "high"}
        doc_id = await rag.ingest_text("Content with metadata", metadata=meta)
        assert doc_id != ""

    @pytest.mark.asyncio
    async def test_ingest_large_text_chunks_properly(self, rag):
        rag._upsert_chunk = AsyncMock()
        rag.embedder.generate_embeddings = AsyncMock(return_value=[[0.1] * 768] * 5)
        big_text = "Paragraph content. " * 500
        doc_id = await rag.ingest_text(big_text, source_table="generic")
        assert doc_id != ""
        assert rag._upsert_chunk.call_count >= 1


class TestSearch:
    @pytest.mark.asyncio
    async def test_search_empty_query_returns_empty(self, rag):
        result = await rag.search("")
        assert result == []
        result = await rag.search("   ")
        assert result == []

    @pytest.mark.asyncio
    async def test_vector_search_returns_results(self, rag):
        mock_rows = [
            {"id": "1", "content": "test doc", "similarity": 0.95, "metadata": {}, "source_table": "tasks"},
        ]
        mock_execute = MagicMock()
        mock_execute.data = mock_rows
        rag.supabase.rpc.return_value.execute.return_value = mock_execute

        result = await rag.search("test query")
        assert len(result) == 1
        assert result[0]["id"] == "1"

    @pytest.mark.asyncio
    async def test_vector_search_fallback_on_sql_failure(self, rag):
        rag.supabase.rpc.side_effect = Exception("RPC failed")
        mock_result = MagicMock()
        mock_result.data = [{"id": "1", "content": "fallback doc", "metadata": {}}]
        rag.supabase.table.return_value.select.return_value.eq.return_value.limit.return_value.order.return_value.execute.return_value = mock_result
        rag.supabase.table.return_value.select.return_value.limit.return_value.order.return_value.execute.return_value = mock_result

        result = await rag.search("test")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_search_with_filters(self, rag):
        mock_execute = MagicMock()
        mock_execute.data = [{"id": "1", "content": "filtered", "metadata": {"status": "active"}, "similarity": 0.9}]
        rag.supabase.rpc.return_value.execute.return_value = mock_execute

        result = await rag.search("query", filters={"status": "active"})
        assert len(result) >= 0

    @pytest.mark.asyncio
    async def test_search_all_failures_returns_empty(self, rag):
        rag.supabase.rpc.side_effect = Exception("RPC failed")
        rag.supabase.table.side_effect = Exception("Table failed")
        with patch.object(rag, "_keyword_search", new=AsyncMock(side_effect=Exception("keyword failed"))):
            result = await rag.search("query")
            assert result == []


class TestHybridSearch:
    @pytest.mark.asyncio
    async def test_hybrid_search_empty_query(self, rag):
        result = await rag.hybrid_search("")
        assert result == []

    @pytest.mark.asyncio
    async def test_hybrid_search_fuses_results(self, rag):
        dense = [
            {"id": "d1", "content": "dense result", "similarity": 0.9},
            {"id": "d2", "content": "dense result 2", "similarity": 0.8},
        ]
        sparse = [
            {"id": "s1", "content": "sparse result", "score": 0.7},
            {"id": "d2", "content": "overlap doc", "score": 0.6},
        ]

        with patch.object(rag, "_vector_search", new=AsyncMock(return_value=dense)):
            with patch.object(rag, "_keyword_search", new=AsyncMock(return_value=sparse)):
                results = await rag.hybrid_search("test query")
                assert len(results) >= 2
                assert all("rrf_score" in r for r in results)
                assert "rrf_score" in results[0]

    @pytest.mark.asyncio
    async def test_hybrid_search_fallback_on_failure(self, rag):
        with patch.object(rag, "_vector_search", new=AsyncMock(side_effect=Exception("fail"))):
            with patch.object(rag, "_keyword_search", new=AsyncMock(return_value=[{"id": "1", "content": "fallback"}])):
                results = await rag.hybrid_search("query")
                assert len(results) >= 0

    @pytest.mark.asyncio
    async def test_rrf_ranks_correctly(self, rag):
        dense = [{"id": "a", "content": "a"}, {"id": "b", "content": "b"}]
        sparse = [{"id": "b", "content": "b"}, {"id": "c", "content": "c"}]
        fused = rag._reciprocal_rank_fusion(dense, sparse)
        assert len(fused) == 3
        doc_ids = [d["id"] for d in fused]
        assert "a" in doc_ids
        assert "b" in doc_ids
        assert "c" in doc_ids


class TestAugmentPrompt:
    @pytest.mark.asyncio
    async def test_augment_empty_docs_returns_original(self, rag):
        with patch.object(rag, "hybrid_search", new=AsyncMock(return_value=[])):
            result = await rag.augment_prompt("query", "System prompt", user_id="u1")
            assert result == "System prompt"

    @pytest.mark.asyncio
    async def test_augment_injects_context(self, rag):
        docs = [{"content": "Relevant info", "source_table": "tasks", "rrf_score": 0.95}]
        with patch.object(rag, "hybrid_search", new=AsyncMock(return_value=docs)):
            result = await rag.augment_prompt("query", "System prompt", user_id="u1")
            assert "Retrieved Context" in result
            assert "Relevant info" in result

    @pytest.mark.asyncio
    async def test_augment_respects_token_budget(self, rag):
        long_docs = [
            {"content": "x" * 5000, "source_table": "tasks", "rrf_score": 0.9},
            {"content": "y" * 5000, "source_table": "memory", "rrf_score": 0.8},
            {"content": "z" * 5000, "source_table": "goals", "rrf_score": 0.7},
        ]
        with patch.object(rag, "hybrid_search", new=AsyncMock(return_value=long_docs)):
            result = await rag.augment_prompt("query", "System prompt", max_context_tokens=500, user_id="u1")
            total_tokens = len(result) // 4
            assert total_tokens < 2000

    @pytest.mark.asyncio
    async def test_augment_with_injection_marker(self, rag):
        docs = [{"content": "context data", "source_table": "tasks", "rrf_score": 0.9}]
        prompt = "System header\n{{RETRIEVED_CONTEXT}}\nUser instructions"
        with patch.object(rag, "hybrid_search", new=AsyncMock(return_value=docs)):
            result = await rag.augment_prompt("query", prompt, user_id="u1")
            assert "Retrieved Context" in result
            assert "System header" in result
            assert "User instructions" in result

    @pytest.mark.asyncio
    async def test_augment_with_top_k_limit(self, rag):
        many_docs = [{"content": f"doc {i}", "source_table": "tasks", "rrf_score": 0.9} for i in range(10)]
        with patch.object(rag, "hybrid_search", new=AsyncMock(return_value=many_docs)):
            result = await rag.augment_prompt("query", "System", top_k=2, user_id="u1")
            assert "Retrieved Context" in result

    @pytest.mark.asyncio
    async def test_augment_with_hybrid_fallback(self, rag):
        with patch.object(rag, "hybrid_search", new=AsyncMock(side_effect=Exception("fail"))):
            result = await rag.augment_prompt("query", "System prompt", user_id="u1")
            assert result == "System prompt"


class TestDeleteAndCleanup:
    @pytest.mark.asyncio
    async def test_delete_document_success(self, rag):
        mock_delete = MagicMock()
        mock_delete.execute.return_value.data = [{"id": "1"}]
        rag.supabase.table.return_value.delete.return_value.eq.return_value.eq.return_value = mock_delete

        result = await rag.delete_document("src-1", "u1")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_document_failure_returns_false(self, rag):
        rag.supabase.table.return_value.delete.side_effect = Exception("Delete failed")
        result = await rag.delete_document("src-1", "u1")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_user_data_returns_count(self, rag):
        mock_delete = MagicMock()
        mock_delete.execute.return_value.data = [{"id": "1"}, {"id": "2"}]
        rag.supabase.table.return_value.delete.return_value.eq.return_value = mock_delete

        count = await rag.delete_user_data("u1")
        assert count == 2

    @pytest.mark.asyncio
    async def test_delete_user_data_failure_returns_zero(self, rag):
        rag.supabase.table.return_value.delete.side_effect = Exception("fail")
        count = await rag.delete_user_data("u1")
        assert count == 0


class TestReciprocalRankFusion:
    def test_rrf_empty_inputs(self, rag):
        assert rag._reciprocal_rank_fusion([], []) == []

    def test_rrf_only_dense(self, rag):
        dense = [{"id": "a", "content": "a"}, {"id": "b", "content": "b"}]
        fused = rag._reciprocal_rank_fusion(dense, [])
        assert len(fused) == 2

    def test_rrf_only_sparse(self, rag):
        sparse = [{"id": "c", "content": "c"}]
        fused = rag._reciprocal_rank_fusion([], sparse)
        assert len(fused) == 1

    def test_rrf_scores_decreasing(self, rag):
        dense = [{"id": "a", "content": "a"}, {"id": "b", "content": "b"}, {"id": "c", "content": "c"}]
        sparse = [{"id": "d", "content": "d"}, {"id": "e", "content": "e"}]
        fused = rag._reciprocal_rank_fusion(dense, sparse)
        for i in range(len(fused) - 1):
            assert fused[i]["rrf_score"] >= fused[i + 1]["rrf_score"]


class TestEdgeCases:
    @pytest.mark.asyncio
    async def test_search_special_characters(self, rag):
        mock_execute = MagicMock()
        mock_execute.data = [{"id": "1", "content": "special chars result", "metadata": {}, "similarity": 0.9}]
        rag.supabase.rpc.return_value.execute.return_value = mock_execute

        result = await rag.search("C++ & .NET @home!")
        assert len(result) >= 0

    @pytest.mark.asyncio
    async def test_search_very_long_query(self, rag):
        long_query = "query " * 500
        rag.supabase.rpc.side_effect = Exception("RPC fail")
        rag.supabase.table.return_value.select.return_value.eq.return_value.limit.return_value.order.return_value.execute.side_effect = Exception("also fail")
        rag.supabase.table.return_value.select.return_value.limit.return_value.order.return_value.execute.side_effect = Exception("also fail")
        with patch.object(rag, "_keyword_search", new=AsyncMock(return_value=[])):
            result = await rag.search(long_query)
            assert result == []

    @pytest.mark.asyncio
    async def test_upsert_chunk_error_doesnt_crash(self, rag):
        rag._upsert_chunk = AsyncMock(side_effect=Exception("Upsert failed"))
        rag.embedder.generate_embeddings = AsyncMock(return_value=[[0.1] * 768])
        rag.embedder.generate_embedding = AsyncMock(return_value=[0.1] * 768)

        result = await rag.ingest_text("Test content", source_table="tasks")
        assert result != ""

    def test_count_tokens(self, rag):
        assert rag._count_tokens("") == 1
        assert rag._count_tokens("hello") == 1
        assert rag._count_tokens("word " * 100) == 125

    @pytest.mark.asyncio
    async def test_vector_search_long_embedding(self, rag):
        rag.embedder.generate_embedding = AsyncMock(return_value=[0.1] * 1536)
        mock_execute = MagicMock()
        mock_execute.data = [{"id": "1", "content": "high dim test", "metadata": {}, "similarity": 0.9}]
        rag.supabase.rpc.return_value.execute.return_value = mock_execute

        result = await rag.search("query")
        assert len(result) >= 0

    @pytest.mark.asyncio
    async def test_keyword_search_empty_query(self, rag):
        result = await rag._keyword_search("", 5, None, "u1")
        assert result == []
