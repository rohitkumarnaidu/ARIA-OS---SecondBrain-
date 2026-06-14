from typing import Dict, Any, List
from datetime import datetime, timedelta
from config.core.supabase import get_supabase_client
from ai.client import llm
from ai.prompt_loader import prompts


async def track_user_progress(user_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()
    tasks_resp = supabase.from_("tasks").select("*").eq("user_id", user_id).execute()
    courses_resp = supabase.from_("courses").select("*").eq("user_id", user_id).execute()
    habits_resp = supabase.from_("habits").select("*").eq("user_id", user_id).execute()

    tasks = tasks_resp.data or []
    courses = courses_resp.data or []
    habits = habits_resp.data or []

    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    recent_tasks = [t for t in tasks if t.get("created_at", "") >= week_ago]
    completed_tasks = [t for t in tasks if t.get("status") == "completed" and t.get("completed_at", "") >= week_ago]

    learning_progress = {
        "tasks_created": len(recent_tasks),
        "tasks_completed": len(completed_tasks),
        "completion_rate": round(len(completed_tasks) / len(recent_tasks) * 100, 1) if recent_tasks else 0,
        "courses_enrolled": len([c for c in courses if c.get("status") in ["not_started", "in_progress"]]),
        "courses_completed": len([c for c in courses if c.get("status") == "completed"]),
        "active_habits": len([h for h in habits if h.get("is_active")]),
    }

    supabase.from_("learning_progress").insert({"user_id": user_id, "date": datetime.now().date().isoformat(), "data": learning_progress}).execute()
    return learning_progress


async def detect_learning_patterns(user_id: str) -> List[str]:
    progress = await track_user_progress(user_id)
    learning_prompt = prompts.get_agent("learning_agent")
    if learning_prompt:
        system = learning_prompt.system_prompt
        prompt = (
            f"Analyze this student learning data and identify patterns:\n"
            f"Progress data: {progress}\n"
            f"Return a JSON array of pattern strings."
        )
    else:
        system = "You are a learning analytics AI. Be concise."
        prompt = (
            f"Student learning data: {progress}. "
            f"Identify 1-3 learning patterns or insights. Return as a JSON array of strings."
        )
    result = await llm.generate_json(prompt, system=system)
    if isinstance(result, list):
        return result
    return result.get("patterns", ["Keep up the consistent work"])


async def suggest_learning_focus(user_id: str) -> Dict[str, Any]:
    patterns = await detect_learning_patterns(user_id)
    learning_prompt = prompts.get_agent("learning_agent")
    system = learning_prompt.system_prompt if learning_prompt else "You are a learning coach."
    prompt = f"Based on these learning patterns: {patterns}, suggest 2 concrete recommendations. Return JSON with 'recommendations' array."
    result = await llm.generate_json(prompt, system=system)
    return {"patterns": patterns, "recommendations": result.get("recommendations", ["Stay consistent with your study routine"])}
