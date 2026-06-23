from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from config.core.supabase import get_supabase_client
from shared.utils.logger import logger
from ai.client import llm, LLMProviderUnavailableError
from ai.prompt_loader import prompts


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def store_interaction(
    user_id: str,
    interaction_type: str,
    content: str,
    metadata: Dict[str, Any] = None,
) -> Optional[dict]:
    try:
        supabase = get_supabase_client()
        data = {
            "user_id": user_id,
            "type": interaction_type,
            "key": f"{interaction_type}:{_utc_now()}",
            "value": {"content": content, "metadata": metadata or {}},
            "importance": "medium",
            "tags": [interaction_type],
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

        tasks_resp = (
            supabase.from_("tasks")
            .select("category, priority, status")
            .eq("user_id", user_id)
            .execute()
        )
        tasks = tasks_resp.data or []

        habits_resp = (
            supabase.from_("habits")
            .select("frequency, streak")
            .eq("user_id", user_id)
            .execute()
        )
        habits = habits_resp.data or []

        goals_resp = (
            supabase.from_("goals")
            .select("id, status")
            .eq("user_id", user_id)
            .neq("status", "completed")
            .execute()
        )
        goals = goals_resp.data or []

        courses_resp = (
            supabase.from_("courses")
            .select("status, progress")
            .eq("user_id", user_id)
            .execute()
        )
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
                                "critical" if updates["confidence"] >= 0.8
                                else "high" if updates["confidence"] >= 0.6
                                else "medium" if updates["confidence"] >= 0.3
                                else "low"
                            )
                        if "content" in updates:
                            existing = supabase.from_("memory").select("value").eq("id", memory_id).eq("user_id", user_id).execute()
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


async def _rule_based_consolidation(user_id: str, interactions: List[dict], preferences: Dict[str, Any]) -> Dict[str, Any]:
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
        response = (
            supabase.from_("memory")
            .delete()
            .eq("user_id", user_id)
            .lt("expires_at", now)
            .execute()
        )
        return len(response.data or [])
    except Exception as e:
        logger.error("prune_expired_memories failed", user_id=user_id, error=str(e))
        return 0
