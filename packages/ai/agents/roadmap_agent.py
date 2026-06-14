from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from config.core.supabase import get_supabase_client
from ai.client import llm
from ai.prompt_loader import prompts


async def optimize_roadmap(user_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()

    user_resp = supabase.from_("users").select("skills, interests, career_goal").eq("id", user_id).execute()
    user_data = user_resp.data[0] if user_resp.data else {}

    courses_resp = supabase.from_("courses").select("*").eq("user_id", user_id).execute()
    courses = courses_resp.data or []

    goals_resp = supabase.from_("goals").select("*").eq("user_id", user_id).eq("status", "active").execute()
    goals = goals_resp.data or []

    completed_tasks = supabase.from_("tasks").select("count").eq("user_id", user_id).eq("status", "completed").execute()
    completed_count = completed_tasks.data[0].get("count", 0) if completed_tasks.data else 0

    roadmap_prompt = prompts.get_agent("roadmap_agent")
    if roadmap_prompt:
        system_prompt = roadmap_prompt.system_prompt
        user_prompt = (
            f"Optimize learning roadmap for:\n"
            f"Skills: {user_data.get('skills', [])}\n"
            f"Interests: {user_data.get('interests', [])}\n"
            f"Career Goal: {user_data.get('career_goal', 'Not specified')}\n"
            f"Active Courses: {len(courses)}\n"
            f"Active Goals: {len(goals)}\n"
            f"Tasks Completed: {completed_count}\n"
            f"Return JSON with: milestones (array of {title, deadline_estimate, skills_gained, priority}), "
            f"recommended_path (ordered course/goal sequence), and estimated_completion."
        )
    else:
        system_prompt = "You are a career roadmap optimizer for CS students. Return only valid JSON."
        user_prompt = (
            f"User skills: {user_data.get('skills', [])}, "
            f"interests: {user_data.get('interests', [])}, "
            f"career goal: {user_data.get('career_goal', 'Not specified')}. "
            f"They have {len(courses)} active courses and {len(goals)} goals. "
            f"Suggest a 6-month learning roadmap with milestones. "
            f"Return JSON with: milestones array, recommended_path array, estimated_completion string."
        )

    roadmap = await llm.generate_json(user_prompt, system=system_prompt)

    result = {
        "generated_at": datetime.now().isoformat(),
        "user_id": user_id,
        "milestones": roadmap.get("milestones", []),
        "recommended_path": roadmap.get("recommended_path", []),
        "estimated_completion": roadmap.get("estimated_completion", "6 months"),
        "active_courses": len(courses),
        "active_goals": len(goals),
    }

    supabase.from_("roadmaps").insert({
        "user_id": user_id,
        "data": result,
        "generated_at": datetime.now().isoformat(),
    }).execute()

    return result
