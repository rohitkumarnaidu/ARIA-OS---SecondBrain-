from datetime import datetime, timezone
from typing import Dict, Any, Optional

from shared.utils.logger import logger
from ai.memory.tiers import BufferMemory, WorkingMemory, EpisodicMemory, SemanticMemory, ProceduralMemory
from ai.memory.compression import MemoryCompressor
from ai.memory.retrieval import MemoryRetriever
from ai.client import llm


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MemoryOrchestrator:
    """Single entry point coordinating all 5 memory tiers with graceful degradation."""

    def __init__(self):
        self.buffer = BufferMemory()
        self.working = WorkingMemory()
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.procedural = ProceduralMemory()
        self.compressor = MemoryCompressor()
        self.retriever = MemoryRetriever()

    async def store_interaction(
        self,
        user_id: str,
        user_msg: str,
        ai_msg: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        results: Dict[str, Any] = {"buffer": False, "working": False, "episodic": False}

        self.buffer.add(user_msg, ai_msg, metadata=context)
        results["buffer"] = True
        results["working"] = True

        if context:
            for key, value in context.items():
                if isinstance(value, (str, int, float, bool)):
                    self.working.set(f"ctx:{key}", value, ttl=43200)
            results["working"] = True

        try:
            importance = self._assess_importance(user_msg, ai_msg)
            if importance in ("high", "critical"):
                episode_id = await self.episodic.store_episode(
                    user_id=user_id,
                    session_data={"user_msg": user_msg, "ai_msg": ai_msg, "context": context or {}},
                    summary=user_msg[:200] if user_msg else "No user message",
                    tags=context.get("tags", ["chat"]) if context else ["chat"],
                )
                if episode_id:
                    results["episodic"] = True
            elif context and context.get("store_episodic", False):
                episode_id = await self.episodic.store_episode(
                    user_id=user_id,
                    session_data={"user_msg": user_msg, "ai_msg": ai_msg, "context": context},
                    summary=user_msg[:200],
                )
                if episode_id:
                    results["episodic"] = True
        except Exception as e:
            logger.warn("Episodic storage failed (degraded)", user_id=user_id, error=str(e))

        logger.info("Interaction stored", user_id=user_id, results=results)
        return results

    async def get_relevant_context(
        self,
        user_id: str,
        query: str,
        k: int = 10,
    ) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "buffer": [],
            "working": {},
            "episodic": [],
            "semantic": [],
            "procedural": [],
        }

        result["buffer"] = self.buffer.get_context(k=min(k, 5))
        result["working"] = self.working.get_all()

        try:
            retrieved = await self.retriever.hybrid_retrieve(user_id, query, k=k)
            for mem in retrieved:
                mtype = mem.get("type", "unknown")
                if mtype == "episodic" and len(result["episodic"]) < k:
                    result["episodic"].append(mem)
                elif mtype == "semantic" and len(result["semantic"]) < k:
                    result["semantic"].append(mem)
                elif mtype == "procedural" and len(result["procedural"]) < k:
                    result["procedural"].append(mem)
        except Exception as e:
            logger.warn("Retrieval failed (degraded)", user_id=user_id, error=str(e))

        return result

    async def consolidate_all(self, user_id: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        try:
            ep_results = await self.episodic.consolidate(user_id)
            results["episodic"] = ep_results
        except Exception as e:
            logger.warn("Episodic consolidation failed", user_id=user_id, error=str(e))
            results["episodic"] = {"merged": 0, "groups_found": 0}
        try:
            decayed = await self.semantic.decay_all(user_id)
            results["semantic_decayed"] = decayed
        except Exception as e:
            logger.warn("Semantic decay failed", user_id=user_id, error=str(e))
            results["semantic_decayed"] = 0
        try:
            pruned = self.compressor.prune_old_memories(user_id, days=90)
            results["pruned"] = pruned
        except Exception as e:
            logger.warn("Memory pruning failed", user_id=user_id, error=str(e))
            results["pruned"] = 0
        try:
            patterns = await self.procedural.get_patterns(user_id)
            results["procedural_patterns"] = len(patterns)
        except Exception as e:
            logger.warn("Procedural pattern check failed", user_id=user_id, error=str(e))
            results["procedural_patterns"] = 0

        total = sum(
            v if isinstance(v, int) else v.get("merged", 0) for v in results.values()
        )
        results["total_actions"] = total
        logger.info("Consolidation complete", user_id=user_id, results=results)
        return results

    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        profile: Dict[str, Any] = {
            "preferences": [],
            "patterns": [],
            "recent_episodes": [],
            "summary": "",
        }
        try:
            prefs = await self.semantic.get_user_preferences(user_id)
            profile["preferences"] = prefs[:10]
        except Exception as e:
            logger.warn("Failed to get preferences", user_id=user_id, error=str(e))
        try:
            patterns = await self.procedural.get_patterns(user_id)
            profile["patterns"] = patterns[:10]
        except Exception as e:
            logger.warn("Failed to get patterns", user_id=user_id, error=str(e))
        try:
            recent = await self.episodic.get_recent(user_id, days=7)
            profile["recent_episodes"] = recent[:5]
        except Exception as e:
            logger.warn("Failed to get recent episodes", user_id=user_id, error=str(e))
        try:
            all_memories = []
            if profile["preferences"]:
                all_memories.extend(profile["preferences"])
            if profile["patterns"]:
                all_memories.extend(profile["patterns"])
            if profile["recent_episodes"]:
                all_memories.extend(profile["recent_episodes"])
            profile["summary"] = self.compressor.summarize_memories(all_memories)
        except Exception as e:
            logger.warn("Failed to build summary", error=str(e))

        return profile

    async def prune_all(self, user_id: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        try:
            self.buffer.clear()
            results["buffer_cleared"] = True
        except Exception as e:
            logger.warn("Buffer clear failed", error=str(e))
            results["buffer_cleared"] = False
        try:
            expired = self.working.clear_expired()
            results["working_expired"] = expired
        except Exception as e:
            logger.warn("Working memory clear failed", error=str(e))
            results["working_expired"] = 0
        try:
            pruned = self.compressor.prune_old_memories(user_id, days=90)
            results["persisted_pruned"] = pruned
        except Exception as e:
            logger.warn("Persisted memory prune failed", error=str(e))
            results["persisted_pruned"] = 0
        return results

    async def extract_facts_from_interaction(
        self,
        user_id: str,
        user_msg: str,
        ai_msg: str,
    ) -> int:
        try:
            prompt = (
                "Extract factual statements from this conversation that should be remembered. "
                "Return a JSON array of objects with keys: 'fact', 'category', 'confidence' (0-1). "
                "Only extract clear, useful facts. Return [] if nothing to extract.\n\n"
                f"User: {user_msg[:500]}\nAI: {ai_msg[:500]}"
            )
            system = "You are a fact extraction system. Output only valid JSON arrays."
            response = await llm.generate_json(prompt, system=system, max_tokens=1024, temperature=0.2)
        except Exception:
            response = {}

        items = response if isinstance(response, list) else response.get("items", response.get("facts", []))
        if not isinstance(items, list):
            items = []

        stored = 0
        for item in items:
            if isinstance(item, dict) and item.get("fact"):
                fact_id = await self.semantic.store_fact(
                    user_id=user_id,
                    fact=item["fact"],
                    source="chat_extraction",
                    confidence=float(item.get("confidence", 0.6)),
                    category=item.get("category", "general"),
                    tags=["extracted", item.get("category", "general")],
                )
                if fact_id:
                    stored += 1
        return stored

    def _assess_importance(self, user_msg: str, ai_msg: str) -> str:
        combined = (user_msg + " " + ai_msg).lower()
        critical_signals = ["urgent", "critical", "emergency", "important", "deadline"]
        high_signals = ["goal", "task", "create", "project", "course", "habit", "plan", "milestone"]
        critical_count = sum(1 for s in critical_signals if s in combined)
        high_count = sum(1 for s in high_signals if s in combined)
        if critical_count > 0:
            return "critical"
        if high_count >= 2:
            return "high"
        if high_count == 1:
            return "medium"
        return "low"
