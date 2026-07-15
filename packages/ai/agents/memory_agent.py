import json
import importlib
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from config.core.supabase import get_supabase_client
from shared.utils.logger import logger
from ai.client import llm, LLMProviderUnavailableError
from ai.prompt_loader import prompts
from ai.memory.orchestrator import MemoryOrchestrator


_orchestrator: Optional[MemoryOrchestrator] = None


def get_orchestrator() -> MemoryOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MemoryOrchestrator()
    return _orchestrator


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


_VALID_MEMORY_TYPES = frozenset({"buffer", "working", "episodic", "semantic", "procedural", "query", "consolidated", "preference", "fact", "pattern", "interaction"})


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
                current_val = json.loads(existing.data[0]["value"]) if isinstance(existing.data[0].get("value"), str) else existing.data[0].get("value", {})
            except (json.JSONDecodeError, TypeError):
                current_val = {}
            current_val["updated_content"] = content
            current_val["metadata"] = metadata or {}
            current_val["reference_count"] = current_val.get("reference_count", 1) + 1
            supabase.from_("memory").update({
                "value": json.dumps(current_val),
            }).eq("id", existing.data[0]["id"]).execute()
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
        return {
            "consolidation_type": "error",
            "memories_created": 0,
            "memories_updated": 0,
            "memories_discarded": 0,
            "patterns_detected": 0,
            "contradictions_found": 0,
            "summary": f"Consolidation failed: {str(e)}",
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
    try:
        supabase = get_supabase_client()
        resp = supabase.from_("memory").select("id, key, value, type").eq("user_id", user_id).execute()
        memories = resp.data or []
        seen: Dict[str, list] = {}
        merged_count = 0
        for mem in memories:
            try:
                val = json.loads(mem["value"]) if isinstance(mem.get("value"), str) else mem.get("value", {})
                content = val.get("content", "") if isinstance(val, dict) else str(val)
            except (json.JSONDecodeError, TypeError):
                content = str(mem.get("value", ""))
            norm_key = content.strip().lower()[:100]
            mtype = mem.get("type", "episodic")
            group_key = f"{mtype}:{hashlib.sha256(norm_key.encode()).hexdigest()[:16]}"
            if group_key in seen:
                primary = seen[group_key][0]
                try:
                    primary_val = json.loads(primary["value"]) if isinstance(primary.get("value"), str) else primary.get("value", {})
                except (json.JSONDecodeError, TypeError):
                    primary_val = {}
                if isinstance(primary_val, dict):
                    primary_val["reference_count"] = primary_val.get("reference_count", 1) + 1
                    supabase.from_("memory").update({"value": json.dumps(primary_val)}).eq("id", primary["id"]).execute()
                supabase.from_("memory").delete().eq("id", mem["id"]).execute()
                merged_count += 1
            else:
                seen[group_key] = [mem]
        if merged_count:
            logger.info("Deduplicated memories", user_id=user_id, merged=merged_count)
        return merged_count
    except Exception as e:
        logger.error("deduplicate_memories failed", user_id=user_id, error=str(e))
        return 0


async def apply_confidence_decay(user_id: str) -> int:
    try:
        supabase = get_supabase_client()
        resp = supabase.from_("memory").select("id, value, type").eq("user_id", user_id).execute()
        memories = resp.data or []
        decayed = 0
        decay_rate = 0.05
        for mem in memories:
            try:
                val = json.loads(mem["value"]) if isinstance(mem.get("value"), str) else mem.get("value", {})
            except (json.JSONDecodeError, TypeError):
                continue
            if isinstance(val, dict):
                old_conf = val.get("confidence", 0.5)
                new_conf = max(0.05, old_conf - decay_rate)
                if new_conf < old_conf:
                    val["confidence"] = round(new_conf, 4)
                    supabase.from_("memory").update({"value": json.dumps(val)}).eq("id", mem["id"]).execute()
                    decayed += 1
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
        decayed = await apply_confidence_decay(user_id)
        summary = result.get("summary", "Weekly deep consolidation completed.")
        return {
            "status": "completed",
            "user_id": user_id,
            "consolidation": result,
            "deduplicated": deduped,
            "confidence_decayed": decayed,
            "summary": summary,
            "week": datetime.now(timezone.utc).strftime("%Y-W%W"),
        }
    except Exception as e:
        logger.error("run_weekly_deep_consolidation failed", user_id=user_id, error=str(e))
        return {
            "status": "failed",
            "user_id": user_id,
            "error": str(e),
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
    orchestrator = get_orchestrator()
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
        orchestrator = get_orchestrator()
        decayed = await orchestrator.semantic.decay_all(user_id)
        logger.info("Confidence decay applied", user_id=user_id, memories_affected=decayed)
        return {"decayed": decayed, "status": "completed"}
    except Exception as e:
        logger.error("confidence_decay failed", user_id=user_id, error=str(e))
        return {"decayed": 0, "status": "failed", "error": str(e)}


async def deep_consolidation(user_id: str) -> Dict[str, Any]:
    try:
        orchestrator = get_orchestrator()
        consolidated = await orchestrator.consolidate_all(user_id)

        pruned = orchestrator.compressor.prune_old_memories(user_id, days=90)
        consolidated["pruned_old"] = pruned

        try:
            supabase = get_supabase_client()
            all_semantic = (
                supabase.from_("memory")
                .select("id, value")
                .eq("user_id", user_id)
                .eq("type", "semantic")
                .execute()
            )
            updated_count = 0
            for mem in all_semantic.data or []:
                try:
                    val = json.loads(mem["value"]) if isinstance(mem.get("value"), str) else mem.get("value", {})
                except (json.JSONDecodeError, TypeError):
                    continue
                if isinstance(val, dict):
                    old_conf = val.get("confidence", 0.5)
                    new_conf = max(0.05, old_conf - 0.05)
                    if new_conf < old_conf:
                        val["confidence"] = round(new_conf, 4)
                        supabase.from_("memory").update({
                            "value": json.dumps(val),
                        }).eq("id", mem["id"]).execute()
                        updated_count += 1
            consolidated["deep_decayed"] = updated_count
        except Exception as inner_e:
            logger.warn("Deep decay step failed", error=str(inner_e))
            consolidated["deep_decayed"] = 0

        temp_dir = str(importlib.import_module("tempfile").gettempdir())
        snapshot_path = f"{temp_dir}/memory_snapshot_{user_id}_{_utc_now().replace(':', '-')}.json"
        profile = await orchestrator.get_user_profile(user_id)
        with open(snapshot_path, "w") as f:
            json.dump(profile, f, indent=2, default=str)
        consolidated["snapshot_path"] = snapshot_path

        consolidated["status"] = "completed"
        logger.info("Deep consolidation completed", user_id=user_id, results=consolidated)
        return consolidated
    except Exception as e:
        logger.error("deep_consolidation failed", user_id=user_id, error=str(e))
        return {
            "status": "failed",
            "error": str(e),
            "episodic_merged": 0,
            "semantic_decayed": 0,
            "pruned_old": 0,
            "deep_decayed": 0,
        }

