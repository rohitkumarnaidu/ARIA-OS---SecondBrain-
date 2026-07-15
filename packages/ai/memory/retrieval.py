import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from config.core.supabase import get_supabase_client
from shared.utils.logger import logger


def _utc_dt() -> datetime:
    return datetime.now(timezone.utc)


def _estimate_tokens(text: str) -> int:
    return len(text.split())


class MemoryRetriever:
    """Memory retrieval with 4 modes: semantic, temporal, keyword, and hybrid."""

    def __init__(self):
        self._table = "memory"

    async def retrieve(
        self,
        user_id: str,
        query: str,
        tiers: Optional[List[int]] = None,
        k: int = 5,
    ) -> List[Dict[str, Any]]:
        if tiers is None:
            tiers = [2, 3, 4]
        type_map = {2: "episodic", 3: "semantic", 4: "procedural"}
        target_types = [type_map[t] for t in tiers if t in type_map]
        if not target_types:
            return []
        try:
            supabase = get_supabase_client()
            all_results: List[Tuple[float, Dict[str, Any]]] = []
            for mtype in target_types:
                result = (
                    supabase.from_(self._table)
                    .select("*")
                    .eq("user_id", user_id)
                    .eq("type", mtype)
                    .order("created_at", desc=True)
                    .limit(50)
                    .execute()
                )
                scored = self._rank_results(result.data or [], query)
                all_results.extend(scored)
            all_results.sort(key=lambda x: x[0], reverse=True)
            return [r for _, r in all_results[:k]]
        except Exception as e:
            logger.error("retrieve failed", user_id=user_id, query=query[:50], error=str(e))
            return []

    async def semantic_search(self, user_id: str, query: str, k: int = 5) -> List[Dict[str, Any]]:
        return await self.retrieve(user_id, query, tiers=[3], k=k)

    async def temporal_search(
        self,
        user_id: str,
        since: Optional[str] = None,
        until: Optional[str] = None,
        k: int = 10,
    ) -> List[Dict[str, Any]]:
        try:
            supabase = get_supabase_client()
            q = supabase.from_(self._table).select("*").eq("user_id", user_id)
            if since:
                q = q.gte("created_at", since)
            if until:
                q = q.lte("created_at", until)
            result = q.order("created_at", desc=True).limit(k).execute()
            return result.data or []
        except Exception as e:
            logger.error("temporal_search failed", user_id=user_id, error=str(e))
            return []

    async def hybrid_retrieve(self, user_id: str, query: str, k: int = 5) -> List[Dict[str, Any]]:
        try:
            supabase = get_supabase_client()
            result = (
                supabase.from_(self._table)
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(100)
                .execute()
            )
            all_memories = result.data or []
            surfaced: List[Tuple[float, Dict[str, Any]]] = []

            for mem in all_memories:
                score = 0.0
                mem_type = mem.get("type", "")
                mem_text = json.dumps(mem.get("value", {})).lower() + " " + " ".join(mem.get("tags", [])).lower()
                mem_text += " " + mem.get("key", "").lower()

                keywords = [w.lower() for w in query.split() if len(w) > 2]
                for kw in keywords:
                    if kw in mem_text:
                        score += 2.0

                try:
                    created = mem.get("created_at", "")
                    created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    hours_ago = (_utc_dt() - created_dt).total_seconds() / 3600.0
                    recency_score = max(0, 1.0 - hours_ago / 720.0)
                except (ValueError, TypeError):
                    recency_score = 0.0
                score += recency_score * 1.5

                importance_map = {"low": 0.3, "medium": 0.6, "high": 0.8, "critical": 1.0}
                score += importance_map.get(mem.get("importance", "medium"), 0.5)

                if score > 0:
                    surfaced.append((score, mem))

            surfaced.sort(key=lambda x: x[0], reverse=True)
            return [m for _, m in surfaced[:k]]
        except Exception as e:
            logger.error("hybrid_retrieve failed", user_id=user_id, error=str(e))
            return []

    async def get_context_window(self, user_id: str, query: str, max_tokens: int = 4000) -> Dict[str, Any]:
        memories = await self.hybrid_retrieve(user_id, query, k=20)
        sections: Dict[str, List[Dict[str, Any]]] = {}
        total_tokens = 0
        for mem in memories:
            mtype = mem.get("type", "unknown")
            if mtype not in sections:
                sections[mtype] = []
            tokens = _estimate_tokens(json.dumps(mem))
            if total_tokens + tokens > max_tokens:
                break
            sections[mtype].append(mem)
            total_tokens += tokens
        return {
            "sections": sections,
            "total_memories": sum(len(v) for v in sections.values()),
            "total_tokens": total_tokens,
            "max_tokens": max_tokens,
        }

    def _rank_results(self, memories: List[Dict[str, Any]], query: str) -> List[Tuple[float, Dict[str, Any]]]:
        if not memories:
            return []
        keywords = [w.lower() for w in query.split() if len(w) > 2]
        if not keywords:
            return [(1.0, m) for m in memories]
        scored: List[Tuple[float, Dict[str, Any]]] = []
        for mem in memories:
            score = 0.0
            value_str = json.dumps(mem.get("value", {})).lower()
            key_str = mem.get("key", "").lower()
            tags = [t.lower() for t in mem.get("tags", [])]
            importance_map = {"low": 0.3, "medium": 0.6, "high": 0.8, "critical": 1.0}
            importance_bonus = importance_map.get(mem.get("importance", "medium"), 0.5)
            for kw in keywords:
                if kw in value_str:
                    score += 1.5
                if kw in key_str:
                    score += 2.0
                if kw in tags:
                    score += 2.5
            try:
                created = mem.get("created_at", "")
                created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                hours_ago = (_utc_dt() - created_dt).total_seconds() / 3600.0
                recency_boost = max(0, 1.0 - hours_ago / 168.0)
                score += recency_boost
            except (ValueError, TypeError):
                pass
            score += importance_bonus * 0.5
            if score > 0:
                scored.append((score, mem))
        return scored
