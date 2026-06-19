from typing import Dict, Any, List
from datetime import datetime
from config.core.supabase import get_supabase_client
from ai.client import llm, LLMProviderUnavailableError
from ai.prompt_loader import prompts


async def store_interaction(user_id: str, interaction_type: str, content: str, metadata: Dict[str, Any] = None) -> dict:
    supabase = get_supabase_client()
    data = {
        "user_id": user_id,
        "interaction_type": interaction_type,
        "content": content,
        "metadata": metadata or {},
        "timestamp": datetime.now().isoformat(),
    }
    response = supabase.from_("memory").insert(data).execute()
    return response.data[0] if response.data else None


async def get_recent_interactions(user_id: str, limit: int = 10) -> List[dict]:
    supabase = get_supabase_client()
    response = (
        supabase.from_("memory")
        .select("*")
        .eq("user_id", user_id)
        .order("timestamp", ascending=False)
        .limit(limit)
        .execute()
    )
    return response.data or []


async def get_user_preferences(user_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()
    tasks_resp = supabase.from_("tasks").select("category, priority").eq("user_id", user_id).execute()
    tasks = tasks_resp.data or []
    if not tasks:
        return {"preferred_category": "personal", "preferred_priority": "medium", "total_tasks": 0}

    category_counts, priority_counts = {}, {}
    for task in tasks:
        cat = task.get("category", "personal")
        pri = task.get("priority", "medium")
        category_counts[cat] = category_counts.get(cat, 0) + 1
        priority_counts[pri] = priority_counts.get(pri, 0) + 1

    return {
        "preferred_category": max(category_counts, key=category_counts.get),
        "preferred_priority": max(priority_counts, key=priority_counts.get),
        "total_tasks": len(tasks),
    }


async def update_memory_context(user_id: str, context: Dict[str, Any]) -> None:
    supabase = get_supabase_client()
    existing = supabase.from_("user_context").select("*").eq("user_id", user_id).execute()
    if existing.data:
        supabase.from_("user_context").update({"context": context, "updated_at": datetime.now().isoformat()}).eq(
            "user_id", user_id
        ).execute()
    else:
        supabase.from_("user_context").insert({"user_id": user_id, "context": context}).execute()


async def get_memory_summary(user_id: str) -> Dict[str, Any]:
    interactions = await get_recent_interactions(user_id, 20)
    preferences = await get_user_preferences(user_id)

    if interactions:
        memory_prompt = prompts.get_agent("memory_agent")
        if memory_prompt:
            system = memory_prompt.system_prompt
            user = f"Summarize these user interactions: {[i.get('content', '')[:200] for i in interactions[:5]]}"
        else:
            system = "You are a memory summarization AI. Be very concise."
            user = f"Summarize these user interactions in 1-2 sentences: {[i.get('content', '')[:100] for i in interactions[:5]]}"
        try:
            summary = await llm.generate(user, system=system)
        except LLMProviderUnavailableError:
            summary = "Unable to generate memory summary at this time."
    else:
        summary = "No recent interactions to summarize."

    return {
        "recent_interactions": len(interactions),
        "preferences": preferences,
        "summary": summary,
        "memory_type": "long_term" if len(interactions) > 50 else "short_term",
    }
