from datetime import datetime
from typing import Dict, Any
from config.core.supabase import get_supabase_client
from ai.client import llm, LLMProviderUnavailableError
from ai.prompt_loader import prompts


async def generate_daily_briefing(user_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()

    today = datetime.now().date().isoformat()

    tasks_resp = supabase.from_("tasks").select("*").eq("user_id", user_id).execute()
    goals_resp = supabase.from_("goals").select("*").eq("user_id", user_id).eq("status", "active").execute()
    courses_resp = supabase.from_("courses").select("*").eq("user_id", user_id).execute()
    sleep_resp = supabase.from_("sleep_logs").select("*").eq("user_id", user_id).gte("date", today).execute()

    tasks = tasks_resp.data or []
    goals = goals_resp.data or []
    courses = courses_resp.data or []
    sleeps = sleep_resp.data or []

    pending_tasks = [t for t in tasks if t.get("status") == "pending"]
    pending_tasks.sort(
        key=lambda t: (
            {"urgent": 0, "high": 1, "medium": 2, "low": 3}.get(t.get("priority", "medium"), 2),
            t.get("due_date", ""),
        )
    )
    top_3_tasks = pending_tasks[:3]

    sleep_score = 70
    if sleeps:
        avg_quality = sum(t.get("quality", 70) for t in sleeps) / len(sleeps)
        sleep_score = int(avg_quality)

    completed = len([t for t in tasks if t.get("status") == "completed"])
    total_tasks = len(tasks)
    productivity_score = int((completed / total_tasks * 50 if total_tasks else 0) + (sleep_score / 100 * 30))

    briefing_prompt = prompts.get_agent("briefing_agent")
    if briefing_prompt:
        system_prompt = briefing_prompt.system_prompt
        user_prompt = (
            f"Generate a daily briefing with this context:\n"
            f"- {len(pending_tasks)} pending tasks, {len(goals)} active goals\n"
            f"- Sleep score: {sleep_score}/100\n"
            f"- {len(courses)} courses\n"
            f"- Top tasks: {[t['title'] for t in top_3_tasks[:3]]}\n"
            f"- Goals: {[g['title'] for g in goals[:3]]}\n"
            f"Return JSON with: greeting, focus_today, task_reminder, tone, timestamp."
        )
    else:
        system_prompt = "You are ARIA, a personal AI productivity assistant. Be concise and motivating."
        user_prompt = (
            f"User has {len(pending_tasks)} pending tasks, {len(goals)} active goals, "
            f"sleep score {sleep_score}/100, {len(courses)} courses. "
            f"Top tasks: {[t['title'] for t in top_3_tasks[:3]]}. "
            f"Generate a brief JSON response with: aria_pick (title and reason), "
            f"productivity_tip, and focus_area."
        )

    try:
        ai_response = await llm.generate_json(user_prompt, system=system_prompt)
    except LLMProviderUnavailableError:
        ai_response = {}

    brief = {
        "generated_at": datetime.now().isoformat(),
        "top_3_tasks": [
            {"title": t.get("title"), "priority": t.get("priority"), "estimated_minutes": t.get("estimated_minutes")}
            for t in top_3_tasks
        ],
        "sleep_score": sleep_score,
        "productivity_score": productivity_score,
        "active_goals": [{"title": g.get("title"), "progress": g.get("progress", 0)} for g in goals[:3]],
        "aria_pick": ai_response.get(
            "aria_pick",
            {
                "title": top_3_tasks[0]["title"] if top_3_tasks else "Start your day",
                "reason": "Focus on what matters most",
            },
        ),
        "productivity_tip": ai_response.get("productivity_tip", "Break big tasks into smaller chunks"),
        "focus_area": ai_response.get("focus_area", "Clear your pending tasks first"),
    }

    supabase.from_("daily_briefings").insert({"user_id": user_id, "date": today, "data": brief}).execute()
    return brief
