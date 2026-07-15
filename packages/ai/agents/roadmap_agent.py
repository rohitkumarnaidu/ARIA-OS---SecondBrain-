from datetime import datetime
from typing import Dict, Any, List
from config.core.supabase import get_supabase_client
from ai.client import llm, LLMProviderUnavailableError
from ai.prompt_loader import prompts


def detect_stale_nodes(roadmap: dict, threshold_days: int = 30) -> List[str]:
    stale: List[str] = []
    milestones = roadmap.get("milestones", roadmap.get("nodes", []))
    now = datetime.now()
    for node in milestones:
        title = node.get("title", node.get("name", "unknown"))
        last_activity = node.get("last_activity") or node.get("last_reviewed") or node.get("updated_at")
        if last_activity:
            try:
                last_dt = datetime.fromisoformat(last_activity) if isinstance(last_activity, str) else last_activity
                days_since = (now - last_dt).days
                if days_since > threshold_days:
                    stale.append(title)
            except (ValueError, TypeError):
                stale.append(title)
        else:
            stale.append(title)
    return stale


def validate_prerequisites(roadmap: dict) -> List[dict]:
    issues: List[dict] = []
    milestones = roadmap.get("milestones", roadmap.get("nodes", []))
    title_map: Dict[str, dict] = {}
    for m in milestones:
        t = m.get("title", m.get("name", ""))
        if t:
            title_map[t.lower()] = m
    for m in milestones:
        pre_reqs = m.get("prerequisites", [])
        if not pre_reqs:
            continue
        for pr in pre_reqs:
            pr_lower = pr.lower() if isinstance(pr, str) else ""
            if pr_lower and pr_lower not in title_map:
                issues.append({
                    "node": m.get("title", m.get("name", "unknown")),
                    "missing_prerequisite": pr,
                    "issue": f"Prerequisite '{pr}' not found in roadmap",
                    "severity": "error",
                })
    for i, m in enumerate(milestones):
        pre_reqs = m.get("prerequisites", [])
        for pr in pre_reqs:
            pr_lower = pr.lower() if isinstance(pr, str) else ""
            for j, other in enumerate(milestones):
                if other.get("title", "").lower() == pr_lower and j >= i:
                    issues.append({
                        "node": m.get("title", "unknown"),
                        "prerequisite": pr,
                        "issue": f"Prerequisite '{pr}' comes after or at same position as this node",
                        "severity": "warning",
                    })
    return issues


def detect_circular_dependencies(roadmap: dict) -> List[List[str]]:
    milestones = roadmap.get("milestones", roadmap.get("nodes", []))
    dep_graph: Dict[str, List[str]] = {}
    for m in milestones:
        title = m.get("title", m.get("name", ""))
        pre_reqs = m.get("prerequisites", [])
        dep_graph[title] = [p for p in pre_reqs if isinstance(p, str)] if pre_reqs else []
    circular: List[List[str]] = []
    visited_global: set = set()

    def dfs(node: str, path: list, visited: set):
        if node in visited:
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            circular.append(cycle)
            return
        if node in visited_global:
            return
        visited.add(node)
        visited_global.add(node)
        path.append(node)
        for dep in dep_graph.get(node, []):
            dfs(dep, path, visited)
        path.pop()
        visited.discard(node)

    for node in dep_graph:
        if node not in visited_global:
            dfs(node, [], set())

    return circular


def enrich_with_external_data(roadmap: dict) -> dict:
    enriched = dict(roadmap)
    skills = roadmap.get("skills", [])
    milestones = roadmap.get("milestones", roadmap.get("nodes", []))

    trend_data = {}
    for skill in skills:
        skill_name = skill if isinstance(skill, str) else skill.get("name", "")
        if skill_name:
            trend_data[skill_name] = {
                "salaries": _estimate_salary(skill_name),
                "demand": _estimate_demand(skill_name),
                "market_trend": _estimate_trend(skill_name),
            }

    enriched["external_data"] = trend_data
    enriched["skills_analyzed"] = len(skills)
    enriched["external_updated"] = datetime.now().isoformat()
    return enriched


def _estimate_salary(skill: str) -> dict:
    skill_lower = skill.lower()
    if any(k in skill_lower for k in ("python", "javascript", "typescript", "react")):
        return {"range": "$80k-$150k", "median": "$115k", "currency": "USD"}
    elif any(k in skill_lower for k in ("machine learning", "ai", "deep learning", "data science")):
        return {"range": "$100k-$180k", "median": "$140k", "currency": "USD"}
    elif any(k in skill_lower for k in ("devops", "cloud", "aws", "docker", "kubernetes")):
        return {"range": "$90k-$160k", "median": "$125k", "currency": "USD"}
    elif any(k in skill_lower for k in ("java", "c++", "rust", "golang")):
        return {"range": "$85k-$155k", "median": "$120k", "currency": "USD"}
    return {"range": "$60k-$120k", "median": "$90k", "currency": "USD"}


def _estimate_demand(skill: str) -> str:
    skill_lower = skill.lower()
    if any(k in skill_lower for k in ("ai", "machine learning", "python", "react", "typescript")):
        return "high"
    elif any(k in skill_lower for k in ("java", "c++", "rust", "golang", "devops")):
        return "medium"
    return "moderate"


def _estimate_trend(skill: str) -> str:
    skill_lower = skill.lower()
    if any(k in skill_lower for k in ("ai", "machine learning", "rust", "typescript", "blockchain")):
        return "growing"
    elif any(k in skill_lower for k in ("python", "react", "golang", "cloud")):
        return "stable"
    return "stable"


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
            f"Return JSON with: milestones (array of {{title, deadline_estimate, skills_gained, priority}}), "
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

    try:
        roadmap = await llm.generate_json(user_prompt, system=system_prompt)
    except LLMProviderUnavailableError:
        roadmap = {}

    result = {
        "generated_at": datetime.now().isoformat(),
        "user_id": user_id,
        "milestones": roadmap.get("milestones", []),
        "recommended_path": roadmap.get("recommended_path", []),
        "estimated_completion": roadmap.get("estimated_completion", "6 months"),
        "active_courses": len(courses),
        "active_goals": len(goals),
    }

    supabase.from_("roadmaps").insert(
        {
            "user_id": user_id,
            "data": result,
            "generated_at": datetime.now().isoformat(),
        }
    ).execute()

    return result
