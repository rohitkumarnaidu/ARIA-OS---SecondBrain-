from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from config.core.supabase import get_supabase_client
from shared.utils.logger import logger
from ai.client import llm, LLMProviderUnavailableError
from ai.prompt_loader import prompts


async def orchestrate_plan(user_id: str, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    try:
        supabase = get_supabase_client()
        tasks = supabase.from_("tasks").select("id, title, status, priority, category, due_date").eq("user_id", user_id).order("created_at", ascending=False).limit(20).execute().data or []
        goals = supabase.from_("goals").select("id, title, status, target_date").eq("user_id", user_id).order("created_at", ascending=False).limit(10).execute().data or []
        courses = supabase.from_("courses").select("id, name, status").eq("user_id", user_id).order("created_at", ascending=False).limit(10).execute().data or []
    except Exception as e:
        logger.error("Failed to fetch user data for planning", error=str(e))
        tasks, goals, courses = [], [], []

    try:
        prompt_entry = prompts.get_agent("planner_agent")
        if prompt_entry:
            system = prompt_entry.system_prompt
        else:
            system = "You are a planning AI. Break down user queries into actionable steps. Return a JSON object with 'steps' (array of {action, target, reasoning, confidence}) and 'summary' (string)."

        user_prompt = f"""User query: {query}

Current context:
- Tasks ({len(tasks)}): {[t['title'] for t in tasks[:5]]}
- Goals ({len(goals)}): {[g['title'] for g in goals[:5]]}
- Courses ({len(courses)}): {[c['name'] for c in courses[:5]]}

Break this query down into a step-by-step plan."""

        result = await llm.generate_json(user_prompt, system=system, max_tokens=2048)
        steps = result.get("steps", [])
        summary = result.get("summary", "Plan generated")
        if not isinstance(steps, list):
            steps = []
    except (LLMProviderUnavailableError, Exception) as e:
        logger.warn("LLM unavailable for planning, using fallback", error=str(e))
        steps = [{"action": "search", "target": "all", "reasoning": "Fallback: search across all modules", "confidence": 0.5}]
        summary = "Search across all modules"

    return {
        "plan_id": f"plan_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{user_id[:8]}",
        "steps": steps,
        "summary": summary,
    }


async def search_memory(user_id: str, query: str) -> Dict[str, Any]:
    try:
        supabase = get_supabase_client()
        memories = (
            supabase.from_("memory")
            .select("id, type, key, value, importance, tags, created_at")
            .eq("user_id", user_id)
            .order("created_at", ascending=False)
            .limit(50)
            .execute()
            .data or []
        )
    except Exception as e:
        logger.error("Failed to fetch memories", error=str(e))
        memories = []

    preferences = {"preferred_category": "personal", "preferred_priority": "medium"}
    try:
        supabase = get_supabase_client()
        from ai.agents.memory_agent import get_user_preferences
        preferences = await get_user_preferences(user_id)
    except Exception as e:
        logger.warn("Failed to fetch user preferences", error=str(e))

    try:
        prompt_entry = prompts.get_agent("memory_agent")
        if prompt_entry:
            system = prompt_entry.system_prompt
        else:
            system = "You are a memory AI. Summarize relevant memory entries based on a user query. Be concise."

        user_prompt = f"""User query: {query}

Recent memories ({len(memories)}):
{[(m.get('type', ''), m.get('key', ''), str(m.get('value', ''))[:200]) for m in memories[:10]]}

User preferences: {preferences}

Summarize what the system knows about the user related to this query."""

        summary = await llm.generate(user_prompt, system=system, max_tokens=512)
    except (LLMProviderUnavailableError, Exception) as e:
        logger.warn("LLM unavailable for memory search, using fallback", error=str(e))
        summary = ""

    filtered = [m for m in memories if query.lower() in str(m.get("key", "")).lower() or query.lower() in str(m.get("value", "")).lower()]
    if not filtered:
        filtered = memories[:20]

    return {
        "memories": filtered,
        "preferences": preferences,
        "summary": summary,
    }


async def detect_patterns(user_id: str, query: str) -> Dict[str, Any]:
    try:
        supabase = get_supabase_client()
        today = datetime.utcnow()
        thirty_days_ago = (today - timedelta(days=30)).isoformat()

        tasks = supabase.from_("tasks").select("id, title, status, priority, category, created_at, completed_at").eq("user_id", user_id).gte("created_at", thirty_days_ago).execute().data or []
        habits = supabase.from_("habits").select("id, name, is_active, current_streak, best_streak, consistency_percentage").eq("user_id", user_id).execute().data or []
        sleep_logs = supabase.from_("sleep_logs").select("date, sleep_score, duration_hours").eq("user_id", user_id).gte("date", thirty_days_ago[:10]).order("date", ascending=False).execute().data or []
        time_entries = supabase.from_("time_entries").select("duration_minutes, is_deep_work, category, start_time").eq("user_id", user_id).gte("start_time", thirty_days_ago).execute().data or []
    except Exception as e:
        logger.error("Failed to fetch user data for pattern detection", error=str(e))
        tasks, habits, sleep_logs, time_entries = [], [], [], []

    total_tasks = len(tasks)
    completed = len([t for t in tasks if t.get("status") == "completed"])
    completion_rate = round(completed / total_tasks * 100, 1) if total_tasks else 0

    by_category = {}
    for t in tasks:
        cat = t.get("category", "uncategorized")
        by_category.setdefault(cat, {"total": 0, "completed": 0})
        by_category[cat]["total"] += 1
        if t.get("status") == "completed":
            by_category[cat]["completed"] += 1

    active_habits = [h for h in habits if h.get("is_active")]
    avg_consistency = round(sum(h.get("consistency_percentage", 0) for h in active_habits) / len(active_habits), 1) if active_habits else 0

    sleep_scores = [s.get("sleep_score", 0) for s in sleep_logs if s.get("sleep_score")]
    avg_sleep_score = round(sum(sleep_scores) / len(sleep_scores), 1) if sleep_scores else 0
    avg_duration = round(sum(s.get("duration_hours", 0) for s in sleep_logs) / len(sleep_logs), 1) if sleep_logs else 0

    deep_work_minutes = sum(t.get("duration_minutes", 0) for t in time_entries if t.get("is_deep_work"))
    total_minutes = sum(t.get("duration_minutes", 0) for t in time_entries)

    patterns = [
        {"type": "task_completion", "description": f"Task completion rate: {completion_rate}%", "confidence": 0.8, "data": {"rate": completion_rate, "total": total_tasks, "completed": completed}},
        {"type": "task_category_breakdown", "description": f"Tasks by category: {dict((k, v['total']) for k, v in by_category.items())}", "confidence": 0.7, "data": by_category},
        {"type": "habit_consistency", "description": f"Habit consistency: {avg_consistency}% across {len(active_habits)} active habits", "confidence": 0.75, "data": {"consistency": avg_consistency, "active_count": len(active_habits)}},
        {"type": "sleep_quality", "description": f"Avg sleep score: {avg_sleep_score}, avg duration: {avg_duration}h", "confidence": 0.6, "data": {"avg_score": avg_sleep_score, "avg_duration": avg_duration}},
        {"type": "focus_time", "description": f"Deep work: {deep_work_minutes}m of {total_minutes}m tracked", "confidence": 0.7, "data": {"deep_work_minutes": deep_work_minutes, "total_minutes": total_minutes}},
    ]

    try:
        prompt_entry = prompts.get_agent("learning_agent")
        if prompt_entry:
            system = prompt_entry.system_prompt
        else:
            system = "You are a pattern detection AI. Analyze user behavior data and return insights. Be concise."

        user_prompt = f"""User query: {query}

Pattern data:
- Task completion rate: {completion_rate}% ({completed}/{total_tasks})
- Category breakdown: {by_category}
- Habit consistency: {avg_consistency}%
- Sleep: avg {avg_sleep_score}/100 score, {avg_duration}h duration
- Focus: {deep_work_minutes}m deep work out of {total_minutes}m

Provide key insights about the user's patterns."""

        insights_raw = await llm.generate_json(user_prompt, system=system, max_tokens=1024)
        insight_items = insights_raw.get("insights", [])
        if isinstance(insight_items, str):
            insight_items = [{"type": "llm_insight", "description": insight_items, "confidence": 0.5, "data": {}}]
        elif not isinstance(insight_items, list):
            insight_items = []
    except (LLMProviderUnavailableError, Exception) as e:
        logger.warn("LLM unavailable for pattern detection, using fallback", error=str(e))
        insight_items = []

    if completion_rate < 50:
        insight_items.append({"type": "productivity_warning", "description": "Task completion rate is below 50% — consider reducing workload or breaking tasks down", "confidence": 0.6, "data": {"completion_rate": completion_rate}})
    if avg_consistency < 60 and active_habits:
        insight_items.append({"type": "habit_improvement", "description": "Habit consistency is low — focus on building smaller daily habits", "confidence": 0.6, "data": {"consistency": avg_consistency}})
    if avg_sleep_score < 70 and sleep_scores:
        insight_items.append({"type": "sleep_improvement", "description": "Sleep quality is below optimal — consider a consistent bedtime routine", "confidence": 0.5, "data": {"avg_score": avg_sleep_score}})

    return {
        "patterns": patterns,
        "insights": insight_items,
        "summary": f"Detected {len(patterns)} patterns and {len(insight_items)} insights for query: {query}",
    }


async def match_opportunities(user_id: str, query: str) -> Dict[str, Any]:
    try:
        supabase = get_supabase_client()
        opportunities = (
            supabase.from_("opportunities")
            .select("id, title, url, match_score, status, category, created_at")
            .eq("user_id", user_id)
            .in_("status", ["new", "considering"])
            .order("created_at", ascending=False)
            .limit(50)
            .execute()
            .data or []
        )
    except Exception as e:
        logger.error("Failed to fetch opportunities", error=str(e))
        opportunities = []

    skills = []
    try:
        supabase = get_supabase_client()
        courses = supabase.from_("courses").select("name, skills, status").eq("user_id", user_id).eq("status", "completed").limit(20).execute().data or []
        for c in courses:
            course_skills = c.get("skills")
            if isinstance(course_skills, list):
                skills.extend(course_skills)
            elif isinstance(course_skills, str):
                skills.append(course_skills)

        roadmap = supabase.from_("roadmap").select("skill_name, status").eq("user_id", user_id).limit(20).execute().data or []
        for r in roadmap:
            skills.append(r.get("skill_name", ""))
    except Exception as e:
        logger.warn("Failed to fetch skills data", error=str(e))

    skills = list(set(s for s in skills if s))
    unique_skills = skills[:20]

    try:
        prompt_entry = prompts.get_agent("opportunity_matching_agent")
        if prompt_entry:
            system = prompt_entry.system_prompt
        else:
            system = "You are an opportunity matching AI. Score opportunities against user skills and interests. Return a JSON object with 'matches' array of {id, title, score, reasoning}."

        user_prompt = f"""User query: {query}
User skills: {unique_skills}
Available opportunities ({len(opportunities)}):
{[{'id': o['id'], 'title': o['title'], 'category': o.get('category', 'general'), 'current_score': o.get('match_score', 0)} for o in opportunities[:20]]}

Score each opportunity by relevance to the user's skills and query."""

        result = await llm.generate_json(user_prompt, system=system, max_tokens=2048)
        matches = result.get("matches", [])
        if not isinstance(matches, list):
            matches = []
    except (LLMProviderUnavailableError, Exception) as e:
        logger.warn("LLM unavailable for opportunity matching, using fallback", error=str(e))
        matches = [
            {"id": o["id"], "title": o["title"], "score": o.get("match_score", 0.5), "reasoning": "Fallback scoring based on stored match_score"}
            for o in sorted(opportunities, key=lambda x: x.get("match_score", 0), reverse=True)[:10]
        ]

    return {
        "matches": matches,
        "summary": f"Matched {len(matches)} opportunities for query: {query}",
    }


async def execute_action(user_id: str, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    action_type = "create_task"
    task_title = query.strip()
    context_data = context or {}

    if context_data.get("action"):
        action_type = context_data["action"]
    elif query.lower().startswith("update "):
        action_type = "update_task"
    elif query.lower().startswith("complete "):
        action_type = "complete_task"
    elif query.lower().startswith("log habit "):
        action_type = "create_habit_log"
    elif query.lower().startswith("delete "):
        action_type = "delete_task"

    try:
        supabase = get_supabase_client()

        if action_type == "create_task":
            data = {
                "user_id": user_id,
                "title": context_data.get("title", task_title),
                "status": "pending",
                "priority": context_data.get("priority", "medium"),
                "category": context_data.get("category", "general"),
                "due_date": context_data.get("due_date"),
            }
            result = supabase.from_("tasks").insert(data).execute()
            if result.error:
                raise Exception(result.error.message)
            action_summary = f"Created task: {data['title']}"

        elif action_type == "update_task":
            task_id = context_data.get("task_id")
            if not task_id:
                return await execute_action(user_id, query, {**context_data, "action": "create_task"})
            update_data = {}
            if context_data.get("title"):
                update_data["title"] = context_data["title"]
            if context_data.get("status"):
                update_data["status"] = context_data["status"]
            if context_data.get("priority"):
                update_data["priority"] = context_data["priority"]
            if not update_data:
                update_data["title"] = task_title
            result = supabase.from_("tasks").update(update_data).eq("id", task_id).eq("user_id", user_id).execute()
            if result.error:
                raise Exception(result.error.message)
            action_summary = f"Updated task {task_id}"

        elif action_type == "complete_task":
            task_id = context_data.get("task_id")
            if not task_id:
                search = supabase.from_("tasks").select("id").eq("user_id", user_id).ilike("title", f"%{task_title}%").limit(1).execute()
                task_id = search.data[0]["id"] if search.data else None
            if not task_id:
                return {"action": "complete_task", "result": {"error": "No matching task found"}, "summary": "Task not found"}
            result = supabase.from_("tasks").update({"status": "completed", "completed_at": datetime.utcnow().isoformat()}).eq("id", task_id).eq("user_id", user_id).execute()
            if result.error:
                raise Exception(result.error.message)
            action_summary = f"Completed task {task_id}"

        elif action_type == "create_habit_log":
            habit_name = context_data.get("habit_name", task_title.replace("log habit ", "").strip())
            habit_search = supabase.from_("habits").select("id").eq("user_id", user_id).ilike("name", f"%{habit_name}%").limit(1).execute()
            habit_id = habit_search.data[0]["id"] if habit_search.data else None
            if not habit_id:
                return {"action": "create_habit_log", "result": {"error": "No matching habit found"}, "summary": "Habit not found"}
            data = {
                "user_id": user_id,
                "habit_id": habit_id,
                "date": datetime.utcnow().strftime("%Y-%m-%d"),
                "completed": True,
            }
            result = supabase.from_("habit_logs").insert(data).execute()
            if result.error:
                raise Exception(result.error.message)
            action_summary = f"Logged habit: {habit_name}"

        elif action_type == "delete_task":
            task_id = context_data.get("task_id")
            if not task_id:
                search = supabase.from_("tasks").select("id").eq("user_id", user_id).ilike("title", f"%{task_title}%").limit(1).execute()
                task_id = search.data[0]["id"] if search.data else None
            if not task_id:
                return {"action": "delete_task", "result": {"error": "No matching task found"}, "summary": "Task not found"}
            result = supabase.from_("tasks").delete().eq("id", task_id).eq("user_id", user_id).execute()
            if result.error:
                raise Exception(result.error.message)
            action_summary = f"Deleted task {task_id}"

        else:
            return await execute_action(user_id, query, {**context_data, "action": "create_task"})

        return {
            "action": action_type,
            "result": result.data[0] if result.data else {},
            "summary": action_summary,
        }

    except Exception as e:
        logger.error("Action execution failed", error=str(e))
        return {"action": "noop", "result": {"error": str(e)}, "summary": "Action failed"}
