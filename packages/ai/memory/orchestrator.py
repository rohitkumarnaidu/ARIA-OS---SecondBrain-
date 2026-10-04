from datetime import datetime, timezone
from typing import Dict, Any, Optional

from shared.utils.logger import logger
from ai.memory.tiers import BufferMemory, WorkingMemory, EpisodicMemory, SemanticMemory, ProceduralMemory
from ai.memory.compression import MemoryCompressor
from ai.memory.retrieval import MemoryRetriever
from ai.client import llm, LLMProviderUnavailableError
from ai.prompt_loader import prompts


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MemoryOrchestrator:
    """Single entry point coordinating all 5 memory tiers with graceful degradation.

    TENANCY: an orchestrator belongs to exactly one user. Its in-memory tiers
    (``buffer`` holding raw conversation turns, ``working`` holding live
    context) are bound to that user at construction, so one instance can never
    serve another user's conversation history and ``prune_all()`` can never
    clear another user's buffer. ``memory_agent.get_orchestrator(user_id)``
    resolves one instance per user.

    The in-memory tiers honour ``self.user_id``; the persisted tiers
    (episodic / semantic / procedural) still take ``user_id`` per call because
    every query they issue is explicitly scoped to the caller.
    """

    def __init__(self, user_id: str):
        if not user_id or not isinstance(user_id, str):
            raise ValueError("MemoryOrchestrator requires a non-empty user_id")
        self.user_id = user_id
        self.buffer = BufferMemory()
        self.working = WorkingMemory(user_id=user_id)
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.procedural = ProceduralMemory()
        self.compressor = MemoryCompressor()
        self.retriever = MemoryRetriever()

    def _owns(self, user_id: str) -> bool:
        """True when ``user_id`` is this orchestrator's bound tenant."""
        return user_id == self.user_id

    async def store_interaction(
        self,
        user_id: str,
        user_msg: str,
        ai_msg: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        results: Dict[str, Any] = {"buffer": False, "working": False, "episodic": False}

        # In-memory tiers are bound to self.user_id. If a caller hands us a
        # different tenant we must not write their turns into this owner's
        # buffer or working cache — fail closed instead.
        if self._owns(user_id):
            self.buffer.add(user_msg, ai_msg, metadata=context)
            results["buffer"] = True
            results["working"] = True
            if context:
                for key, value in context.items():
                    if isinstance(value, (str, int, float, bool)):
                        self.working.set(f"ctx:{key}", value, ttl=43200, user_id=self.user_id)
                results["working"] = True
        else:
            logger.error(
                "Rejected interaction for a foreign tenant",
                owner_user_id=self.user_id,
                requested_user_id=user_id,
            )

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
                    tags=context.get("tags") or ["chat"],
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

        if self._owns(user_id):
            result["buffer"] = self.buffer.get_context(k=min(k, 5))
            result["working"] = self.working.get_all(user_id=self.user_id)
        else:
            logger.error(
                "Refused context read for a foreign tenant",
                owner_user_id=self.user_id,
                requested_user_id=user_id,
            )
            return result

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

        total = sum(v if isinstance(v, int) else v.get("merged", 0) for v in results.values())
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
            if self._owns(user_id):
                self.buffer.clear()
                results["buffer_cleared"] = True
            else:
                logger.error(
                    "Refused buffer clear for a foreign tenant",
                    owner_user_id=self.user_id,
                    requested_user_id=user_id,
                )
                results["buffer_cleared"] = False
        except Exception as e:
            logger.warn("Buffer clear failed", error=str(e))
            results["buffer_cleared"] = False
        try:
            expired = self.working.clear_expired(user_id=self.user_id)
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
        loaded = prompts.get_agent("memory_agent")
        if loaded:
            system_prompt = loaded.system_prompt
        else:
            system_prompt = "You are a fact extraction system. Output only valid JSON arrays."
        prompt = (
            "Extract factual statements from this conversation that should be remembered. "
            "Return a JSON array of objects with keys: 'fact', 'category', 'confidence' (0-1). "
            "Only extract clear, useful facts. Return [] if nothing to extract.\n\n"
            f"User: {user_msg[:500]}\nAI: {ai_msg[:500]}"
        )
        try:
            response = await llm.generate_json(prompt, system=system_prompt, max_tokens=1024, temperature=0.2)
        except LLMProviderUnavailableError:
            logger.warn("LLM unavailable, skipping fact extraction", user_id=user_id)
            response = {}
        except Exception as e:
            logger.error("Fact extraction failed", user_id=user_id, error=str(e))
            response = {}

        if not isinstance(response, (list, dict)):
            response = {}
        items = response.get("items", response.get("facts", [])) if isinstance(response, dict) else response
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
