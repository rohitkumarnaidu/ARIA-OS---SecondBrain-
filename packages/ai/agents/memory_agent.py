import json
import hashlib
import threading
from collections import OrderedDict
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from config.core.supabase import get_supabase_client
from shared.utils.logger import logger
from ai.client import llm, LLMProviderUnavailableError
from ai.prompt_loader import prompts
from ai.memory.orchestrator import MemoryOrchestrator
from ai.memory.tiers import SemanticMemory

# Per-user orchestrator cache. An orchestrator owns the raw conversation
# buffer and the live working-memory cache for exactly one tenant, so a single
# process-global instance would serve one user's chat history to everyone else
# (and prune_all() would wipe every user's buffer). Bounded LRU: the least
# recently used tenant's in-memory state is dropped when the bound is reached,
# which forgets a conversation — it never cross-contaminates one.
MAX_CACHED_ORCHESTRATORS = 256
_orchestrators: "OrderedDict[str, MemoryOrchestrator]" = OrderedDict()
_orchestrators_lock = threading.Lock()


def get_orchestrator(user_id: str) -> MemoryOrchestrator:
    """Return the MemoryOrchestrator bound to ``user_id``, creating it if needed.

    Raises ValueError for a missing user_id rather than falling back to a
    shared instance — an unscoped orchestrator is the cross-tenant leak.
    """
    if not user_id or not isinstance(user_id, str):
        raise ValueError("get_orchestrator requires a non-empty user_id")
    with _orchestrators_lock:
        existing = _orchestrators.get(user_id)
        if existing is not None:
            _orchestrators.move_to_end(user_id)
            return existing
        orchestrator = MemoryOrchestrator(user_id=user_id)
        _orchestrators[user_id] = orchestrator
        while len(_orchestrators) > MAX_CACHED_ORCHESTRATORS:
            evicted_user_id, _ = _orchestrators.popitem(last=False)
            logger.info("Evicted memory orchestrator from cache", user_id=evicted_user_id)
        return orchestrator


def reset_orchestrator_cache() -> None:
    """Drop every cached orchestrator. Test hook and shutdown helper."""
    with _orchestrators_lock:
        _orchestrators.clear()


# Upper bound on rows a single batched write fan-out will touch.
_DEDUP_MAX_ROWS = 500
_WRITE_CHUNK = 50


def _decode_value(row: Dict[str, Any]) -> Dict[str, Any]:
    """Decode a memory row's ``value`` column, tolerating both writer shapes."""
    raw = row.get("value", "{}")
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return raw if isinstance(raw, dict) else {}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


_VALID_MEMORY_TYPES = frozenset(
    {
        "buffer",
        "working",
        "episodic",
        "semantic",
        "procedural",
        "query",
        "consolidated",
        "preference",
        "fact",
        "pattern",
        "interaction",
    }
)


def validate_memory_type(mtype: str) -> str:
    if mtype not in _VALID_MEMORY_TYPES:
        logger.warn("Invalid memory type, defaulting to episodic", provided=mtype)
        return "episodic"
    return mtype


async def store_interaction(
    user_id: str,
    interaction_type: str,
    content: str,
    metadata: Dict[str, Any] = None,
) -> Optional[dict]:
    try:
        mtype = validate_memory_type(interaction_type)
        supabase = get_supabase_client()
        import hashlib

        dedup_key = hashlib.sha256(f"{user_id}:{mtype}:{content[:200]}".encode()).hexdigest()[:24]
        existing = (
            supabase.from_("memory")
            .select("id, value")
            .eq("user_id", user_id)
            .eq("type", mtype)
            .eq("key", dedup_key)
            .execute()
        )
        if existing.data:
            try:
                current_val = (
                    json.loads(existing.data[0]["value"])
                    if isinstance(existing.data[0].get("value"), str)
                    else existing.data[0].get("value", {})
                )
            except (json.JSONDecodeError, TypeError):
                current_val = {}
            current_val["updated_content"] = content
            current_val["metadata"] = metadata or {}
            current_val["reference_count"] = current_val.get("reference_count", 1) + 1
            supabase.from_("memory").update(
                {
                    "value": json.dumps(current_val),
                }
            ).eq(
                "id", existing.data[0]["id"]
            ).eq("user_id", user_id).execute()
            logger.debug("Dedup: updated existing memory", user_id=user_id, key=dedup_key)
            return existing.data[0]
        data = {
            "user_id": user_id,
            "type": mtype,
            "key": dedup_key,
            "value": json.dumps({"content": content, "metadata": metadata or {}, "reference_count": 1}),
            "importance": "medium",
            "tags": [mtype],
        }
        response = supabase.from_("memory").insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error("store_interaction failed", user_id=user_id, error=str(e))
        return None


async def get_recent_interactions(user_id: str, limit: int = 50) -> List[dict]:
    try:
        supabase = get_supabase_client()
        response = (
            supabase.from_("memory")
            .select("id, user_id, type, key, value, importance, tags, expires_at, created_at, updated_at")
            .eq("user_id", user_id)
            .order("created_at", ascending=False)
            .limit(limit)
            .execute()
        )
        return response.data or []
    except Exception as e:
        logger.error("get_recent_interactions failed", user_id=user_id, error=str(e))
        return []


async def get_user_preferences(user_id: str) -> Dict[str, Any]:
    prefs = {
        "preferred_category": "personal",
        "preferred_priority": "medium",
        "work_hours_pattern": "not_enough_data",
        "active_goal_count": 0,
        "course_progress_avg": 0.0,
        "habit_streak_avg": 0,
        "total_tasks": 0,
        "total_habits": 0,
        "total_courses": 0,
    }
    try:
        supabase = get_supabase_client()

        tasks_resp = supabase.from_("tasks").select("category, priority, status").eq("user_id", user_id).execute()
        tasks = tasks_resp.data or []

        habits_resp = supabase.from_("habits").select("frequency, streak").eq("user_id", user_id).execute()
        habits = habits_resp.data or []

        goals_resp = (
            supabase.from_("goals").select("id, status").eq("user_id", user_id).neq("status", "completed").execute()
        )
        goals = goals_resp.data or []

        courses_resp = supabase.from_("courses").select("status, progress").eq("user_id", user_id).execute()
        courses = courses_resp.data or []

        if tasks:
            category_counts = {}
            priority_counts = {}
            for task in tasks:
                cat = task.get("category", "personal")
                pri = task.get("priority", "medium")
                category_counts[cat] = category_counts.get(cat, 0) + 1
                priority_counts[pri] = priority_counts.get(pri, 0) + 1
            prefs["preferred_category"] = max(category_counts, key=category_counts.get)
            prefs["preferred_priority"] = max(priority_counts, key=priority_counts.get)
            prefs["total_tasks"] = len(tasks)
            work_tasks = sum(
                1 for t in tasks if t.get("category", "").lower() in ("study", "work", "coding", "project")
            )
            prefs["work_hours_pattern"] = "high_workload" if work_tasks > len(tasks) * 0.6 else "balanced"

        if habits:
            prefs["total_habits"] = len(habits)
            streaks = [h.get("streak", 0) or 0 for h in habits]
            prefs["habit_streak_avg"] = int(sum(streaks) / len(streaks)) if streaks else 0

        if goals:
            prefs["active_goal_count"] = len(goals)

        if courses:
            prefs["total_courses"] = len(courses)
            progresses = [c.get("progress", 0) or 0 for c in courses]
            prefs["course_progress_avg"] = round(sum(progresses) / len(progresses), 1) if progresses else 0.0

    except Exception as e:
        logger.error("get_user_preferences failed", user_id=user_id, error=str(e))

    return prefs


async def get_session_context(user_id: str) -> Dict[str, Any]:
    try:
        supabase = get_supabase_client()
        chats_resp = (
            supabase.from_("chat_messages")
            .select("conversation_id, role, content, created_at")
            .eq("user_id", user_id)
            .order("created_at", ascending=False)
            .limit(20)
            .execute()
        )
        messages = chats_resp.data or []
        conversations = {}
        for msg in messages:
            cid = msg.get("conversation_id", "unknown")
            if cid not in conversations:
                conversations[cid] = {"message_count": 0, "last_message": msg.get("content", "")[:200]}
            conversations[cid]["message_count"] += 1

        active_conversations = [v for v in conversations.values() if v["message_count"] > 1]
        session_context = {
            "active_conversations": len(active_conversations),
            "recent_topics": [c["last_message"][:100] for c in list(conversations.values())[:3]],
            "total_recent_messages": len(messages),
            "last_interaction": messages[0].get("created_at") if messages else None,
        }
        return session_context
    except Exception as e:
        logger.error("get_session_context failed", user_id=user_id, error=str(e))
        return {"active_conversations": 0, "recent_topics": [], "total_recent_messages": 0}


async def consolidate_memories(user_id: str) -> Dict[str, Any]:
    try:
        interactions = await get_recent_interactions(user_id, 50)
        preferences = await get_user_preferences(user_id)
        session_context = await get_session_context(user_id)

        loaded = prompts.get_agent("memory_agent")
        if loaded:
            system_prompt = loaded.system_prompt
            conversation_history = [
                {
                    "id": m["id"],
                    "type": m["type"],
                    "key": m["key"],
                    "value": m.get("value", ""),
                    "importance": m.get("importance", "medium"),
                    "tags": m.get("tags", []),
                    "created_at": m.get("created_at"),
                }
                for m in interactions[:50]
            ]
            user_prompt = (
                "## Consolidation Request\n\n"
                "Process the following data and produce structured memory consolidation output "
                "following the output schema defined in your instructions.\n\n"
                "### User Preferences\n"
                f"{preferences}\n\n"
                "### Session Context\n"
                f"{session_context}\n\n"
                "### Conversation History (Recent Interactions)\n"
                f"{conversation_history}\n\n"
                "Respond ONLY with a valid JSON object matching the output schema."
            )
        else:
            system_prompt = (
                "You are ARIA's Memory Agent. Consolidate user interactions into structured memory. "
                "Output JSON with: memories_to_create, memories_to_update, memories_to_discard, "
                "analysis, pattern_detected, contradictions, confidence_level, processing_notes."
            )
            user_prompt = (
                "Consolidate these interactions and preferences into memories.\n\n"
                f"Preferences: {preferences}\n"
                f"Session: {session_context}\n"
                f"Interactions: {interactions[:20]}"
            )

        try:
            llm_result = await llm.generate_json(user_prompt, system=system_prompt, max_tokens=4096, temperature=0.4)

            memories_created = []
            for mc in llm_result.get("memories_to_create", []):
                created = await store_interaction(
                    user_id=user_id,
                    interaction_type=mc.get("memory_type", mc.get("type", "consolidated")),
                    content=mc.get("content", ""),
                    metadata={
                        "domain": mc.get("domain"),
                        "confidence": mc.get("confidence"),
                        "source": mc.get("source"),
                        "requires_confirmation": mc.get("requires_confirmation", False),
                        "ttl_days": mc.get("ttl_days"),
                    },
                )
                if created:
                    memories_created.append(created["id"])

            memories_updated = []
            for mu in llm_result.get("memories_to_update", []):
                memory_id = mu.get("memory_id")
                updates = mu.get("updates", {})
                if memory_id and updates:
                    try:
                        supabase = get_supabase_client()
                        update_payload = {}
                        if "confidence" in updates:
                            update_payload["importance"] = (
                                "critical"
                                if updates["confidence"] >= 0.8
                                else (
                                    "high"
                                    if updates["confidence"] >= 0.6
                                    else "medium" if updates["confidence"] >= 0.3 else "low"
                                )
                            )
                        if "content" in updates:
                            existing = (
                                supabase.from_("memory")
                                .select("value")
                                .eq("id", memory_id)
                                .eq("user_id", user_id)
                                .execute()
                            )
                            if existing.data:
                                current_value = existing.data[0].get("value", {})
                                if isinstance(current_value, dict):
                                    current_value["updated_content"] = updates["content"]
                                    update_payload["value"] = current_value
                        if update_payload:
                            result = (
                                supabase.from_("memory")
                                .update(update_payload)
                                .eq("id", memory_id)
                                .eq("user_id", user_id)
                                .execute()
                            )
                            if result.data:
                                memories_updated.append(memory_id)
                    except Exception as e:
                        logger.error("Failed to update memory", memory_id=memory_id, error=str(e))

            memories_discarded = []
            for md_entry in llm_result.get("memories_to_discard", []):
                memory_id = md_entry.get("memory_id")
                if memory_id:
                    try:
                        supabase = get_supabase_client()
                        supabase.from_("memory").delete().eq("id", memory_id).eq("user_id", user_id).execute()
                        memories_discarded.append(memory_id)
                    except Exception as e:
                        logger.error("Failed to discard memory", memory_id=memory_id, error=str(e))

            analysis = llm_result.get("analysis", {})
            pattern = llm_result.get("pattern_detected")
            contradictions = llm_result.get("contradictions")

            return {
                "consolidation_type": "llm_driven",
                "memories_created": len(memories_created),
                "memories_updated": len(memories_updated),
                "memories_discarded": len(memories_discarded),
                "patterns_detected": 1 if pattern else 0,
                "contradictions_found": len(contradictions) if contradictions else 0,
                "summary": analysis.get("summary", "LLM consolidation completed."),
                "details": {
                    "created_ids": memories_created,
                    "updated_ids": memories_updated,
                    "discarded_ids": memories_discarded,
                    "pattern": pattern,
                    "contradictions": contradictions,
                    "key_observation": analysis.get("key_observation"),
                    "actionable": analysis.get("actionable", False),
                    "confidence_level": llm_result.get("confidence_level"),
                    "processing_notes": llm_result.get("processing_notes"),
                },
            }

        except LLMProviderUnavailableError:
            logger.warn("LLM unavailable, falling back to rule-based consolidation", user_id=user_id)
            return await _rule_based_consolidation(user_id, interactions, preferences)

    except Exception as e:
        logger.error("consolidate_memories failed", user_id=user_id, error=str(e))
        # The client-safe message must not embed str(e): apps/api/app/api/memory.py
        # returns this dict straight to the HTTP client, and exception text can
        # carry SQL, table names, or connection details.
        return {
            "consolidation_type": "error",
            "memories_created": 0,
            "memories_updated": 0,
            "memories_discarded": 0,
            "patterns_detected": 0,
            "contradictions_found": 0,
            "summary": "Consolidation failed, no changes made.",
            "details": None,
        }


async def _rule_based_consolidation(
    user_id: str, interactions: List[dict], preferences: Dict[str, Any]
) -> Dict[str, Any]:
    try:
        by_type: Dict[str, List[dict]] = {}
        for m in interactions:
            t = m.get("type", "unknown")
            by_type.setdefault(t, []).append(m)

        patterns_detected = 0
        for t, items in by_type.items():
            if len(items) >= 3:
                patterns_detected += 1

        stale_count = 0
        now = datetime.now(timezone.utc)
        for m in interactions:
            expires = m.get("expires_at")
            if expires:
                try:
                    expires_dt = datetime.fromisoformat(expires.replace("Z", "+00:00"))
                    if expires_dt < now:
                        supabase = get_supabase_client()
                        supabase.from_("memory").delete().eq("id", m["id"]).eq("user_id", user_id).execute()
                        stale_count += 1
                except (ValueError, KeyError):
                    continue

        return {
            "consolidation_type": "rule_based",
            "memories_created": 0,
            "memories_updated": 0,
            "memories_discarded": stale_count,
            "patterns_detected": patterns_detected,
            "contradictions_found": 0,
            "summary": (
                f"Rule-based consolidation: {len(interactions)} memories processed, "
                f"{stale_count} expired discarded, {patterns_detected} patterns detected."
            ),
            "details": {
                "total_memories": len(interactions),
                "by_type": {t: len(items) for t, items in by_type.items()},
                "preferences": preferences,
                "stale_discarded": stale_count,
            },
        }
    except Exception as e:
        logger.error("_rule_based_consolidation failed", user_id=user_id, error=str(e))
        return {
            "consolidation_type": "rule_based",
            "memories_created": 0,
            "memories_updated": 0,
            "memories_discarded": 0,
            "patterns_detected": 0,
            "contradictions_found": 0,
            "summary": "Rule-based consolidation completed with minimal processing.",
            "details": None,
        }


async def get_memory_summary(user_id: str, max_interactions: int = 20) -> Dict[str, Any]:
    try:
        interactions = await get_recent_interactions(user_id, max_interactions)
        preferences = await get_user_preferences(user_id)
        session_context = await get_session_context(user_id)

        loaded = prompts.get_agent("memory_agent")
        if loaded and interactions:
            system_prompt = loaded.system_prompt
            recent = [
                {"type": m["type"], "value": str(m.get("value", ""))[:200], "importance": m.get("importance", "medium")}
                for m in interactions[:5]
            ]
            user_prompt = (
                "Summarize these user interactions in 1-2 concise sentences. "
                "Focus on what matters most about this user right now.\n\n"
                f"Recent interactions: {recent}\n"
                f"Preferences: {preferences}\n"
                f"Session context: {session_context}"
            )
            try:
                summary = await llm.generate(user_prompt, system=system_prompt, max_tokens=256, temperature=0.3)
            except LLMProviderUnavailableError:
                summary = await _rule_based_summary(interactions, preferences)
        else:
            summary = await _rule_based_summary(interactions, preferences)

        return {
            "recent_interactions": len(interactions),
            "preferences": preferences,
            "summary": summary,
            "memory_type": "long_term" if len(interactions) > 50 else "short_term",
            "session_context": session_context,
        }
    except Exception as e:
        logger.error("get_memory_summary failed", user_id=user_id, error=str(e))
        return {
            "recent_interactions": 0,
            "preferences": {},
            "summary": "Unable to generate memory summary at this time.",
            "memory_type": "unknown",
            "session_context": {},
        }


async def _rule_based_summary(interactions: List[dict], preferences: Dict[str, Any]) -> str:
    if not interactions:
        return "No recent interactions to summarize."
    types = set(m.get("type", "unknown") for m in interactions)
    high_imp = sum(1 for m in interactions if m.get("importance") in ("high", "critical"))
    return (
        f"User has {len(interactions)} recent interactions across {len(types)} types "
        f"({high_imp} high importance). "
        f"Primary category: {preferences.get('preferred_category', 'personal')}, "
        f"preferred priority: {preferences.get('preferred_priority', 'medium')}."
    )


async def prune_expired_memories(user_id: str) -> int:
    try:
        supabase = get_supabase_client()
        now = _utc_now()
        response = supabase.from_("memory").delete().eq("user_id", user_id).lt("expires_at", now).execute()
        return len(response.data or [])
    except Exception as e:
        logger.error("prune_expired_memories failed", user_id=user_id, error=str(e))
        return 0


async def extract_memory_from_chat(user_msg: str, ai_msg: str) -> Optional[dict]:
    try:
        loaded = prompts.get_agent("memory_agent")
        if loaded:
            system_prompt = loaded.system_prompt
            user_prompt = (
                "Extract any user preferences, facts, or patterns from this chat exchange. "
                "Return JSON with 'memory_type' (preference|fact|pattern), 'content', "
                "'confidence' (0-1), and 'domain' (general|work|study|health|social). "
                "If nothing extractable, return null.\n\n"
                f"User: {user_msg}\nAI: {ai_msg}"
            )
        else:
            system_prompt = "You are a memory extraction assistant. Extract structured memories from conversations."
            user_prompt = (
                f"Extract preferences, facts, or patterns from:\nUser: {user_msg}\nAI: {ai_msg}\n"
                "Return JSON with memory_type, content, confidence, domain or null."
            )
        try:
            result = await llm.generate_json(user_prompt, system=system_prompt, max_tokens=512, temperature=0.3)
        except LLMProviderUnavailableError:
            result = {}
        if not result or result.get("content") is None:
            return None
        return {
            "memory_type": result.get("memory_type", "fact"),
            "content": result["content"],
            "confidence": result.get("confidence", 0.5),
            "domain": result.get("domain", "general"),
        }
    except Exception as e:
        logger.error("extract_memory_from_chat failed", error=str(e))
        return None


async def deduplicate_memories(user_id: str) -> int:
    """Fold duplicate memories into a primary row and drop the duplicates.

    Bounded select (``_DEDUP_MAX_ROWS``), one aggregated update per primary
    rather than one per duplicate, and chunked deletes. Every write is scoped
    to ``user_id``. Content is written to the primary BEFORE any duplicate is
    deleted, so a mid-run failure can duplicate content but never lose it.
    """
    try:
        supabase = get_supabase_client()
        resp = (
            supabase.from_("memory")
            .select("id, user_id, type, key, value")
            .eq("user_id", user_id)
            .order("created_at", ascending=True)
            .limit(_DEDUP_MAX_ROWS)
            .execute()
        )
        memories = resp.data or []

        groups: Dict[str, List[Dict[str, Any]]] = {}
        for mem in memories:
            content = _decode_value(mem).get("content", "")
            norm_key = str(content).strip().lower()[:100]
            mtype = mem.get("type", "episodic")
            group_key = f"{mtype}:{hashlib.sha256(norm_key.encode()).hexdigest()[:16]}"
            groups.setdefault(group_key, []).append(mem)

        primary_updates: List[Dict[str, Any]] = []
        # (duplicate_id, primary_id) — the primary link decides whether the
        # duplicate may be deleted once the primary write is confirmed.
        duplicate_pairs: List[tuple] = []
        for group in groups.values():
            if len(group) < 2:
                continue
            primary = group[0]
            duplicates = group[1:]
            primary_row_key = primary.get("key")
            if not primary_row_key:
                # Without the unique key the chunk cannot be targeted safely;
                # skip the whole group rather than risk inserting a new row.
                logger.warn(
                    "Skipped dedup group — primary row has no key",
                    user_id=user_id,
                    memory_id=primary.get("id"),
                )
                continue

            primary_val = _decode_value(primary)
            # Aggregate every duplicate into the primary in a single write.
            primary_val["reference_count"] = primary_val.get("reference_count", 1) + len(duplicates)
            merged_source_ids = list(primary_val.get("merged_source_ids") or [])
            for dup in duplicates:
                dup_val = _decode_value(dup)
                carried = dup_val.get("content") or dup_val.get("summary")
                if carried and str(carried)[:200] not in merged_source_ids:
                    merged_source_ids.append(str(carried)[:200])
                if dup.get("id"):
                    duplicate_pairs.append((dup["id"], primary["id"]))
            primary_val["merged_source_ids"] = merged_source_ids
            primary_updates.append(
                {
                    "id": primary["id"],
                    "user_id": user_id,
                    "type": primary.get("type", "episodic"),
                    "key": primary_row_key,
                    "value": json.dumps(primary_val),
                }
            )

        if not primary_updates:
            return 0

        updated_ids: List[str] = []
        for start in range(0, len(primary_updates), _WRITE_CHUNK):
            chunk = primary_updates[start : start + _WRITE_CHUNK]
            try:
                supabase.from_("memory").upsert(chunk, on_conflict="user_id,type,key").execute()
                updated_ids.extend(u["id"] for u in chunk)
            except Exception as chunk_e:
                logger.warn(
                    "Dedup primary upsert chunk failed", user_id=user_id, chunk_size=len(chunk), error=str(chunk_e)
                )
                for update_row in chunk:
                    try:
                        result = (
                            supabase.from_("memory")
                            .update({"value": update_row["value"]})
                            .eq("id", update_row["id"])
                            .eq("user_id", user_id)
                            .execute()
                        )
                        if result.data:
                            updated_ids.append(update_row["id"])
                    except Exception as row_e:
                        logger.error(
                            "Dedup primary update failed",
                            user_id=user_id,
                            memory_id=update_row["id"],
                            error=str(row_e),
                        )

        # Delete a duplicate only once its primary is confirmed written.
        confirmed = set(updated_ids)
        deletable = [dup_id for dup_id, primary_id in duplicate_pairs if primary_id in confirmed]
        merged_count = 0
        for start in range(0, len(deletable), _WRITE_CHUNK):
            chunk = deletable[start : start + _WRITE_CHUNK]
            try:
                supabase.from_("memory").delete().eq("user_id", user_id).in_("id", chunk).execute()
                merged_count += len(chunk)
            except Exception as chunk_e:
                logger.warn("Dedup delete chunk failed", user_id=user_id, chunk_size=len(chunk), error=str(chunk_e))

        if merged_count:
            logger.info("Deduplicated memories", user_id=user_id, merged=merged_count)
        return merged_count
    except Exception as e:
        logger.error("deduplicate_memories failed", user_id=user_id, error=str(e))
        return 0


async def apply_confidence_decay(user_id: str) -> int:
    """Decay memory confidence for a user.

    Delegates to :meth:`SemanticMemory.decay_all` — the single confidence-decay
    implementation. This previously applied a second, independent -0.05 pass on
    top of ``decay_all`` (and ``deep_consolidation`` applied a third), so facts
    decayed roughly three times faster than intended.
    """
    try:
        semantic = SemanticMemory()
        decayed = await semantic.decay_all(user_id)
        if decayed:
            logger.info("Confidence decay applied", user_id=user_id, memories=decayed)
        return decayed
    except Exception as e:
        logger.error("apply_confidence_decay failed", user_id=user_id, error=str(e))
        return 0


async def run_weekly_deep_consolidation(user_id: str) -> dict:
    try:
        result = await deep_consolidation(user_id)
        deduped = await deduplicate_memories(user_id)
        summary = result.get("summary", "Weekly deep consolidation completed.")
        return {
            "status": "completed",
            "user_id": user_id,
            "consolidation": result,
            "deduplicated": deduped,
            "confidence_decayed": result.get("deep_decayed", 0),
            "summary": summary,
            "week": datetime.now(timezone.utc).strftime("%Y-W%W"),
        }
    except Exception as e:
        logger.error("run_weekly_deep_consolidation failed", user_id=user_id, error=str(e))
        return {
            "status": "failed",
            "user_id": user_id,
            "error": "Weekly deep consolidation failed.",
            "deduplicated": 0,
            "confidence_decayed": 0,
        }


WEEKLY_DEEP_CONSOLIDATION_SCHEDULE = {"day_of_week": "sun", "hour": 2, "minute": 0}


async def chat_store_interaction(
    user_id: str,
    user_msg: str,
    ai_msg: str,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    orchestrator = get_orchestrator(user_id)
    result = await orchestrator.store_interaction(user_id, user_msg, ai_msg, context)

    try:
        extracted = await orchestrator.extract_facts_from_interaction(user_id, user_msg, ai_msg)
        if extracted:
            result["facts_extracted"] = extracted
    except Exception as e:
        logger.warn("Fact extraction failed (degraded)", user_id=user_id, error=str(e))
        result["facts_extracted"] = 0

    return result


async def confidence_decay(user_id: str) -> Dict[str, Any]:
    try:
        orchestrator = get_orchestrator(user_id)
        decayed = await orchestrator.semantic.decay_all(user_id)
        logger.info("Confidence decay applied", user_id=user_id, memories_affected=decayed)
        return {"decayed": decayed, "status": "completed"}
    except Exception as e:
        logger.error("confidence_decay failed", user_id=user_id, error=str(e))
        return {"decayed": 0, "status": "failed", "error": "Confidence decay failed."}


async def deep_consolidation(user_id: str) -> Dict[str, Any]:
    try:
        orchestrator = get_orchestrator(user_id)
        consolidated = await orchestrator.consolidate_all(user_id)

        pruned = orchestrator.compressor.prune_old_memories(user_id, days=90)
        consolidated["pruned_old"] = pruned

        # Confidence decay already ran once inside consolidate_all()
        # (SemanticMemory.decay_all — the single decay implementation). This
        # used to apply a second, independent -0.05 pass on top of it.
        consolidated["deep_decayed"] = consolidated.get("semantic_decayed", 0)

        # No on-disk snapshot. The previous implementation dumped the user's
        # entire memory profile to %TEMP% in plaintext under their raw UUID with
        # default permissions, no TTL and no cleanup. The profile summary is
        # returned in the response instead.
        profile = await orchestrator.get_user_profile(user_id)
        consolidated["profile_summary"] = profile.get("summary", "")

        consolidated["status"] = "completed"
        logger.info("Deep consolidation completed", user_id=user_id, results=consolidated)
        return consolidated
    except Exception as e:
        logger.error("deep_consolidation failed", user_id=user_id, error=str(e))
        return {
            "status": "failed",
            "error": "Deep consolidation failed.",
            "episodic_merged": 0,
            "semantic_decayed": 0,
            "pruned_old": 0,
            "deep_decayed": 0,
        }
