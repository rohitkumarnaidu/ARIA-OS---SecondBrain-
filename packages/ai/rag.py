"""RAG Pipeline with text chunking, embedding, vector storage, hybrid search, and prompt augmentation."""

import asyncio
import hashlib
import json
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from uuid import uuid4
from config.core.supabase import get_supabase_client
from shared.utils.logger import logger
from ai.embeddings import EmbeddingService, get_embedding_service


DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 64
DEFAULT_MIN_CHUNK_SIZE = 100
DEFAULT_TOP_K = 5
DEFAULT_RRF_K = 60


SOURCES_TABLE = "documents"

SOURCES_SCHEMA = {
    "tasks": {"chunk_size": 256, "overlap": 32},
    "courses": {"chunk_size": 512, "overlap": 64},
    "goals": {"chunk_size": 512, "overlap": 64},
    "habits": {"chunk_size": 256, "overlap": 32},
    "chat_messages": {"chunk_size": 1024, "overlap": 0},
    "ideas": {"chunk_size": 512, "overlap": 0},
    "sleep_logs": {"chunk_size": 128, "overlap": 0},
    "habit_logs": {"chunk_size": 128, "overlap": 0},
    "memory": {"chunk_size": 512, "overlap": 64},
    "daily_briefings": {"chunk_size": 1024, "overlap": 128},
    "weekly_reviews": {"chunk_size": 2048, "overlap": 256},
}


class ChunkingPipeline:
    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        min_chunk_size: int = DEFAULT_MIN_CHUNK_SIZE,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

    def chunk_document(self, content: str, source_type: str = "generic") -> List[Dict[str, Any]]:
        if not content or not content.strip():
            return []
        config = SOURCES_SCHEMA.get(source_type, {})
        cs = config.get("chunk_size", self.chunk_size)
        ov = config.get("overlap", self.chunk_overlap)

        if source_type in ("chat_messages", "ideas", "notes"):
            return self._chunk_by_message(content, cs)
        if source_type in ("tasks", "courses", "goals", "memory"):
            return self._chunk_by_semantic_boundary(content, cs, ov)
        if source_type in ("sleep_logs", "habit_logs", "time_entries"):
            return self._chunk_by_line(content)
        return self._chunk_recursive(content, cs, ov)

    def _chunk_by_semantic_boundary(
        self, content: str, chunk_size: int, overlap: int
    ) -> List[Dict[str, Any]]:
        chunks: List[Dict[str, Any]] = []
        paragraphs = re.split(r"\n#{1,3}\s|\n\n+", content)
        current_chunk = ""
        current_tokens = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            para_tokens = self._count_tokens(para)
            if current_tokens + para_tokens > chunk_size and current_chunk:
                chunks.append(self._make_chunk(current_chunk.strip(), len(chunks)))
                overlap_text = self._get_tail(current_chunk, overlap)
                current_chunk = overlap_text + " " + para if overlap_text else para
                current_tokens = self._count_tokens(current_chunk)
            else:
                current_chunk = (current_chunk + "\n\n" + para) if current_chunk else para
                current_tokens += para_tokens

        if current_chunk:
            chunks.append(self._make_chunk(current_chunk.strip(), len(chunks)))
        return chunks

    def _chunk_by_message(self, content: str, chunk_size: int) -> List[Dict[str, Any]]:
        messages = content.split("\n---\n")
        chunks: List[Dict[str, Any]] = []
        current_buffer = ""
        for msg in messages:
            combined = (current_buffer + "\n---\n" + msg) if current_buffer else msg
            if self._count_tokens(combined) <= chunk_size:
                current_buffer = combined
            else:
                if current_buffer:
                    chunks.append(self._make_chunk(current_buffer.strip(), len(chunks)))
                current_buffer = msg
        if current_buffer:
            chunks.append(self._make_chunk(current_buffer.strip(), len(chunks)))
        return chunks

    def _chunk_by_line(self, content: str) -> List[Dict[str, Any]]:
        lines = content.strip().split("\n")
        return [
            self._make_chunk(line.strip(), i)
            for i, line in enumerate(lines)
            if line.strip()
        ]

    def _chunk_recursive(
        self, content: str, chunk_size: int, overlap: int
    ) -> List[Dict[str, Any]]:
        chunks: List[Dict[str, Any]] = []
        separators = ["\n\n", "\n", ". ", " ", ""]
        for separator in separators:
            parts = content.split(separator) if separator else list(content)
            if len(parts) <= 1:
                continue
            current_chunk = ""
            for part in parts:
                if not part:
                    continue
                candidate = (current_chunk + separator + part) if current_chunk else part
                if self._count_tokens(candidate) <= chunk_size:
                    current_chunk = candidate
                else:
                    if current_chunk:
                        chunks.append(self._make_chunk(current_chunk.strip(), len(chunks)))
                    current_chunk = part
            if current_chunk:
                chunks.append(self._make_chunk(current_chunk.strip(), len(chunks)))
            if chunks:
                break
        if not chunks:
            chunks.append(self._make_chunk(content.strip(), 0))
        return chunks

    def _make_chunk(self, text: str, index: int) -> Dict[str, Any]:
        return {
            "content": text,
            "chunk_index": index,
            "token_count": self._count_tokens(text),
            "chunk_hash": self._hash(text),
        }

    @staticmethod
    def _count_tokens(text: str) -> int:
        return max(1, len(text) // 4)

    @staticmethod
    def _hash(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    @staticmethod
    def _get_tail(text: str, target_tokens: int) -> str:
        words = text.split()
        target_words = max(1, target_tokens * 4)
        return " ".join(words[-target_words:]) if len(words) > target_words else text


class RAGPipeline:
    def __init__(
        self,
        embedder: Optional[EmbeddingService] = None,
        chunker: Optional[ChunkingPipeline] = None,
        supabase_client=None,
        table_name: str = SOURCES_TABLE,
        top_k: int = DEFAULT_TOP_K,
        rrf_k: int = DEFAULT_RRF_K,
        k_dense: int = 20,
        k_sparse: int = 20,
    ):
        self.embedder = embedder or get_embedding_service()
        self.chunker = chunker or ChunkingPipeline()
        if supabase_client is None:
            try:
                self.supabase = get_supabase_client()
            except (ValueError, Exception):
                self.supabase = None
        else:
            self.supabase = supabase_client
        self.table = table_name
        self.top_k = top_k
        self.rrf_k = rrf_k
        self.k_dense = k_dense
        self.k_sparse = k_sparse

    async def ingest_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        source_table: str = "generic",
        source_id: Optional[str] = None,
    ) -> str:
        metadata = metadata or {}
        chunks = self.chunker.chunk_document(text, source_table)
        if not chunks:
            return ""

        if not user_id:
            user_id = metadata.get("user_id", "anonymous")

        doc_id = str(uuid4())
        texts_to_embed = [c["content"] for c in chunks]
        embeddings = await self.embedder.generate_embeddings(texts_to_embed)

        for i, chunk_data in enumerate(chunks):
            embedding = embeddings[i] if i < len(embeddings) else [0.0] * 768
            content = chunk_data["content"]
            try:
                await self._upsert_chunk(
                    user_id=user_id,
                    source_table=source_table or metadata.get("source_table", "generic"),
                    source_id=source_id or metadata.get("source_id", doc_id),
                    chunk_index=chunk_data["chunk_index"],
                    content=content,
                    embedding=embedding,
                    metadata={
                        **(metadata or {}),
                        "title": metadata.get("title", ""),
                        "document_id": doc_id,
                    },
                    token_count=chunk_data["token_count"],
                    chunk_hash=chunk_data["chunk_hash"],
                )
            except Exception as e:
                logger.warn("Failed to upsert chunk", error=str(e), chunk_index=i)

        logger.info(
            "Ingested text",
            chunks=len(chunks),
            user_id=user_id,
            source_table=source_table,
        )
        return doc_id

    async def ingest_document(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> List[str]:
        metadata = metadata or {}
        path = Path(file_path)
        if not path.exists():
            logger.error("Document not found", file_path=file_path)
            return []

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            logger.error("Failed to read document", file_path=file_path, error=str(e))
            return []

        ext = path.suffix.lower()
        source_table = metadata.get("source_table", ext.lstrip(".") if ext else "document")
        doc_ids: List[str] = []

        if ext in (".md", ".txt", ".py", ".js", ".ts", ".html", ".css", ".json", ".yaml", ".yml"):
            if self._count_tokens(content) > DEFAULT_CHUNK_SIZE * 4:
                sections = content.split("\n---\n")
                for section in sections:
                    if section.strip():
                        sid = await self.ingest_text(
                            section.strip(),
                            metadata={**metadata, "file_path": file_path},
                            user_id=user_id,
                            source_table=source_table,
                        )
                        if sid:
                            doc_ids.append(sid)
            else:
                sid = await self.ingest_text(
                    content,
                    metadata={**metadata, "file_path": file_path},
                    user_id=user_id,
                    source_table=source_table,
                )
                if sid:
                    doc_ids.append(sid)
        else:
            sid = await self.ingest_text(
                content,
                metadata={**metadata, "file_path": file_path, "format": ext},
                user_id=user_id,
                source_table=source_table,
            )
            if sid:
                doc_ids.append(sid)

        return doc_ids

    async def search(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        filters: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            return []

        try:
            results = await self._vector_search(query, top_k, filters, user_id)
            if results:
                return results
        except Exception as e:
            logger.warn("Vector search failed, falling back to keyword search", error=str(e))

        try:
            return await self._keyword_search(query, top_k, filters, user_id)
        except Exception as e:
            logger.warn("Keyword search also failed", error=str(e))
            return []

    async def hybrid_search(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        user_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            return []

        try:
            dense_task = self._vector_search(query, self.k_dense, None, user_id)
            sparse_task = self._keyword_search(query, self.k_sparse, None, user_id)
            dense_results, sparse_results = await asyncio.gather(dense_task, sparse_task)
        except Exception as e:
            logger.warn("Hybrid search parallel fetch failed", error=str(e))
            return await self.search(query, top_k, user_id=user_id)

        fused = self._reciprocal_rank_fusion(dense_results, sparse_results)
        return fused[:top_k]

    async def augment_prompt(
        self,
        query: str,
        system_prompt: str,
        top_k: int = 3,
        user_id: Optional[str] = None,
        max_context_tokens: int = 2048,
    ) -> str:
        try:
            docs = await self.hybrid_search(query, top_k=top_k, user_id=user_id)
        except Exception:
            docs = []
        if not docs:
            return system_prompt

        context_parts: List[str] = []
        total_tokens = 0
        injection_marker = "{{RETRIEVED_CONTEXT}}"

        for doc in docs:
            content = doc.get("content", "")
            if not content:
                continue
            source = doc.get("source_table", "unknown").replace("_", " ").title()
            score = doc.get("rrf_score", doc.get("score", 0))
            block = f"[Source: {source} | Relevance: {score:.2f}]\n{content}"
            block_tokens = len(block) // 4
            if total_tokens + block_tokens > max_context_tokens:
                remaining = max_context_tokens - total_tokens
                if remaining > 20:
                    block = block[: remaining * 4] + "\n[...truncated]"
                else:
                    break
            context_parts.append(block)
            total_tokens += block_tokens

        context_block = "## Retrieved Context\n\n" + "\n\n---\n\n".join(context_parts)

        if injection_marker in system_prompt:
            return system_prompt.replace(injection_marker, context_block)

        marker_alternatives = ["## User Query", "## Input", "## Instructions", "---"]
        for marker in marker_alternatives:
            if marker in system_prompt:
                return system_prompt.replace(marker, f"{context_block}\n\n{marker}")
        return context_block + "\n\n" + system_prompt

    async def _vector_search(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]],
        user_id: Optional[str],
    ) -> List[Dict[str, Any]]:
        query_embedding = await self.embedder.generate_embedding(query)
        dim = len(query_embedding)
        emb_col = "embedding" if dim <= 768 else "embedding_openai"
        emb_col_qualified = f"{emb_col}::vector({dim})"

        sql_parts = [
            "SELECT id, content, metadata, source_table, source_id, chunk_index,",
            f"  1 - ({emb_col_qualified} <=> $1::vector) AS similarity",
            f"FROM {self.table}",
        ]
        params: List[Any] = [query_embedding]
        param_idx = 2

        if user_id:
            sql_parts.append(f"WHERE user_id = ${param_idx}")
            params.append(user_id)
            param_idx += 1

        if filters:
            where_parts = []
            for key, value in filters.items():
                where_parts.append(f"metadata->>'{key}' = ${param_idx}")
                params.append(value)
                param_idx += 1
            prefix = "AND" if (user_id) else "WHERE"
            if where_parts:
                sql_parts.append(f"{prefix} {' AND '.join(where_parts)}")

        sql_parts.append(f"ORDER BY similarity DESC LIMIT ${param_idx}")
        params.append(top_k)
        sql = " ".join(sql_parts)

        try:
            result = self.supabase.rpc("execute_sql", {"query": sql, "params": params}).execute()
            rows = result.data or []
            for row in rows:
                row["retrieval_source"] = "dense"
                row["score"] = row.pop("similarity", 0)
                row["rrf_score"] = row["score"]
            return rows
        except Exception as e:
            logger.warn("Vector search SQL failed, trying Supabase query builder", error=str(e))
            return await self._vector_search_fallback(query_embedding, emb_col, top_k, filters, user_id)

    async def _vector_search_fallback(
        self,
        query_embedding: List[float],
        emb_col: str,
        top_k: int,
        filters: Optional[Dict[str, Any]],
        user_id: Optional[str],
    ) -> List[Dict[str, Any]]:
        try:
            query = self.supabase.table(self.table).select("*")
            if user_id:
                query = query.eq("user_id", user_id)
            if filters:
                for key, value in filters.items():
                    query = query.filter("metadata->>" + key, "eq", value)
            query = query.limit(top_k).order(emb_col, desc=True)
            result = query.execute()
            rows = result.data or []
            for row in rows:
                row["retrieval_source"] = "dense"
                row["score"] = 0.0
                row["rrf_score"] = 0.0
            return rows
        except Exception as e:
            logger.error("Vector search fallback also failed", error=str(e))
            return []

    async def _keyword_search(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]],
        user_id: Optional[str],
    ) -> List[Dict[str, Any]]:
        tokens = query.strip().split()
        if not tokens:
            return []

        tsquery = " & ".join(tokens)
        sql_parts = [
            "SELECT id, content, metadata, source_table, source_id, chunk_index,",
            "  ts_rank(to_tsvector('english', content), to_tsquery('english', $1)) AS score",
            f"FROM {self.table}",
            "WHERE to_tsvector('english', content) @@ to_tsquery('english', $1)",
        ]
        params: List[Any] = [tsquery]
        param_idx = 2

        if user_id:
            sql_parts.append(f"AND user_id = ${param_idx}")
            params.append(user_id)
            param_idx += 1

        if filters:
            for key, value in filters.items():
                sql_parts.append(f"AND metadata->>'{key}' = ${param_idx}")
                params.append(value)
                param_idx += 1

        sql_parts.append(f"ORDER BY score DESC LIMIT ${param_idx}")
        params.append(top_k)
        sql = " ".join(sql_parts)

        try:
            result = self.supabase.rpc("execute_sql", {"query": sql, "params": params}).execute()
            rows = result.data or []
            for row in rows:
                row["retrieval_source"] = "sparse"
                row["rrf_score"] = row.get("score", 0)
            return rows
        except Exception as e:
            logger.warn("Keyword search SQL failed, trying text_search", error=str(e))

        try:
            query_builder = self.supabase.table(self.table).select("*").text_search("content", query)
            if user_id:
                query_builder = query_builder.eq("user_id", user_id)
            if filters:
                for key, value in filters.items():
                    query_builder = query_builder.filter("metadata->>" + key, "eq", value)
            result = query_builder.limit(top_k).execute()
            rows = result.data or []
            for row in rows:
                row["retrieval_source"] = "sparse"
                row["score"] = 0.5
                row["rrf_score"] = 0.5
            return rows
        except Exception as e:
            logger.error("Keyword search fallback also failed", error=str(e))
            return []

    def _reciprocal_rank_fusion(
        self, dense_results: List[Dict[str, Any]], sparse_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        scores: Dict[str, float] = {}
        doc_map: Dict[str, Dict[str, Any]] = {}

        for idx, doc in enumerate(dense_results):
            doc_id = doc.get("id", str(idx))
            scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (self.rrf_k + idx + 1)
            doc_map[doc_id] = doc

        for idx, doc in enumerate(sparse_results):
            doc_id = doc.get("id", str(len(dense_results) + idx))
            scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (self.rrf_k + idx + 1)
            if doc_id not in doc_map:
                doc_map[doc_id] = doc

        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        results: List[Dict[str, Any]] = []
        for doc_id, score in sorted_docs:
            doc = doc_map[doc_id]
            doc["rrf_score"] = round(score, 4)
            results.append(doc)
        return results

    async def _upsert_chunk(
        self,
        user_id: str,
        source_table: str,
        source_id: str,
        chunk_index: int,
        content: str,
        embedding: List[float],
        metadata: Dict[str, Any],
        token_count: int,
        chunk_hash: str,
    ):
        row = {
            "user_id": user_id,
            "source_table": source_table,
            "source_id": source_id,
            "chunk_index": chunk_index,
            "content": content,
            "metadata": json.dumps(metadata) if isinstance(metadata, dict) else metadata,
            "embedding": embedding,
            "token_count": token_count,
            "chunk_hash": chunk_hash,
        }
        try:
            self.supabase.table(self.table).upsert(
                row,
                on_conflict="user_id, source_table, source_id, chunk_index",
            ).execute()
        except Exception as e:
            logger.error(
                "Failed to upsert chunk",
                error=str(e),
                source_table=source_table,
                chunk_index=chunk_index,
            )

    async def delete_document(self, source_id: str, user_id: str) -> bool:
        try:
            self.supabase.table(self.table)\
                .delete()\
                .eq("source_id", source_id)\
                .eq("user_id", user_id)\
                .execute()
            logger.info("Deleted document chunks", source_id=source_id, user_id=user_id)
            return True
        except Exception as e:
            logger.error("Failed to delete document", source_id=source_id, error=str(e))
            return False

    async def delete_user_data(self, user_id: str) -> int:
        try:
            result = self.supabase.table(self.table)\
                .delete()\
                .eq("user_id", user_id)\
                .execute()
            count = len(result.data or [])
            logger.info("Deleted all user document chunks", user_id=user_id, count=count)
            return count
        except Exception as e:
            logger.error("Failed to delete user data", user_id=user_id, error=str(e))
            return 0

    @staticmethod
    def _count_tokens(text: str) -> int:
        return max(1, len(text) // 4)


_rag_instance: Optional[RAGPipeline] = None


def get_rag() -> RAGPipeline:
    global _rag_instance
    if _rag_instance is None:
        try:
            _rag_instance = RAGPipeline()
        except Exception:
            _rag_instance = RAGPipeline(
                supabase_client=None,
            )
            _rag_instance.supabase = None
    return _rag_instance
