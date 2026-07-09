from datetime import datetime
from fastapi import APIRouter, Depends, Request, HTTPException
from typing import List, Dict, Any
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from database.schemas.chat import ChatRequest, ChatResponse
from shared.utils.rate_limiter import endpoint_limiter
from shared.utils.security import sanitize_input
from shared.utils.logger import logger
from ai.client import llm, LLMProviderUnavailableError
from ai.prompt_loader import prompts
from ai.agents.memory_agent import store_interaction, get_memory_summary

router = APIRouter()


def build_context(
    pending_tasks: List[Dict],
    active_goals: List[Dict],
    courses: List[Dict],
    habits: List[Dict],
    sleep_logs: List[Dict],
    time_entries: List[Dict],
    recent_messages: List[Dict],
    memory_summary: Dict[str, Any],
) -> str:
    lines = ["## Current Context", ""]

    if pending_tasks:
        lines.append(f"### Pending Tasks ({len(pending_tasks)})")
        for t in pending_tasks[:5]:
            title = t.get("title", "Untitled")
            priority = t.get("priority", "medium")
            due = t.get("due_date", "No due date")
            lines.append(f"- {title} (Priority: {priority}, Due: {due})")
        if len(pending_tasks) > 5:
            lines.append(f"  ... and {len(pending_tasks) - 5} more")
        lines.append("")

    if active_goals:
        lines.append(f"### Active Goals ({len(active_goals)})")
        for g in active_goals[:3]:
            lines.append(f"- {g.get('title', 'Untitled')} ({g.get('progress', 0)}% complete)")
        lines.append("")

    if courses:
        in_progress = [c for c in courses if c.get("status") == "in_progress"]
        if in_progress:
            lines.append(f"### Courses In Progress ({len(in_progress)})")
            for c in in_progress[:3]:
                lines.append(f"- {c.get('title', 'Untitled')} ({c.get('progress_percent', 0)}%)")
            lines.append("")

    if habits:
        active_habits = [h for h in habits if h.get("is_active")]
        if active_habits:
            lines.append(f"### Habits ({len(active_habits)} active)")
            for h in active_habits[:3]:
                lines.append(f"- {h.get('name', 'Unnamed')} (streak: {h.get('current_streak', 0)} days)")
            lines.append("")

    if sleep_logs:
        latest = sleep_logs[0]
        lines.append("### Last Sleep")
        lines.append(f"- Score: {latest.get('sleep_score', 'N/A')}/100, Duration: {latest.get('duration_hours', 0)}h")
        lines.append("")

    if time_entries:
        total_minutes = sum(t.get("duration_minutes", 0) for t in time_entries)
        lines.append("### Today's Time Tracking")
        lines.append(f"- Total tracked: {total_minutes // 60}h {total_minutes % 60}m")
        categories = {}
        for t in time_entries:
            cat = t.get("category", "work")
            categories[cat] = categories.get(cat, 0) + (t.get("duration_minutes") or 0)
        if categories:
            lines.append(
                f"- Breakdown: {', '.join(f'{cat}: {mins // 60}h {mins % 60}m' for cat, mins in categories.items())}"
            )
        lines.append("")

    if memory_summary and memory_summary.get("summary"):
        lines.append("### Memory Context")
        lines.append(f"- {memory_summary['summary']}")
        lines.append(
            f"- Preferred category: {memory_summary.get('preferences', {}).get('preferred_category', 'general')}"
        )
        lines.append("")

    if recent_messages:
        lines.append(f"### Recent Conversation History (last {len(recent_messages)} messages)")
        for msg in recent_messages[-6:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            truncated = content[:150] + "..." if len(content) > 150 else content
            lines.append(f"- {role}: {truncated}")
        lines.append("")

    return "\n".join(lines)


@router.get("/", summary="List chat conversations", response_model=List[dict])
async def list_conversations(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    try:
        data = (
            supabase.from_("chat_messages")
            .select("conversation_id, created_at, content, role")
            .eq("user_id", current_user.user.id)
            .order("created_at", ascending=False)
            .execute()
        )

        messages = data.data or []
        conv_map: Dict[str, dict] = {}
        for msg in messages:
            cid = msg.get("conversation_id") or "default"
            if cid not in conv_map:
                conv_map[cid] = {
                    "id": cid,
                    "title": msg.get("content", "Chat")[:60],
                    "lastMessage": msg.get("content", ""),
                    "timestamp": msg.get("created_at", ""),
                    "messageCount": 0,
                }
            conv_map[cid]["messageCount"] += 1
            if msg.get("role") == "user":
                conv_map[cid]["title"] = msg.get("content", "Chat")[:60]
            conv_map[cid]["lastMessage"] = msg.get("content", "")
            conv_map[cid]["timestamp"] = msg.get("created_at", "")

        conversations = sorted(conv_map.values(), key=lambda c: c["timestamp"], reverse=True)
        return conversations
    except Exception as e:
        logger.error("Failed to list conversations", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list conversations")


@router.post("/", summary="Send a chat message", status_code=201, response_model=ChatResponse)
async def chat(request: Request, request_body: ChatRequest, current_user=Depends(get_current_user)):
    client_ip = request.client.host if request.client else "unknown"
    if not endpoint_limiter.check(client_ip, "/api/v1/chat"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Max 30 requests per minute for chat.")

    supabase = get_supabase_client()
    message = sanitize_input(request_body.message)

    try:
        tasks_resp = (
            supabase.from_("tasks")
            .select(
                "id, user_id, title, status, priority, due_date, created_at, updated_at, completed_at, estimated_minutes, category, description, project_id, goal_id, is_recurring, recurring_frequency, dependency_id, missed_count"
            )
            .eq("user_id", current_user.user.id)
            .eq("status", "pending")
            .order("priority", ascending=True)
            .execute()
        )
        goals_resp = (
            supabase.from_("goals")
            .select("id, user_id, title, description, status, progress, target_date, category, created_at, updated_at")
            .eq("user_id", current_user.user.id)
            .eq("status", "active")
            .execute()
        )
        courses_resp = (
            supabase.from_("courses")
            .select(
                "id, user_id, title, platform, url, status, progress_percent, total_videos, completed_videos, deadline, created_at, updated_at"
            )
            .eq("user_id", current_user.user.id)
            .execute()
        )
        habits_resp = (
            supabase.from_("habits")
            .select(
                "id, user_id, name, frequency, is_active, current_streak, best_streak, consistency_percentage, created_at"
            )
            .eq("user_id", current_user.user.id)
            .execute()
        )
        sleep_resp = (
            supabase.from_("sleep_logs")
            .select(
                "id, user_id, date, bedtime, wake_time, duration_hours, sleep_score, sleep_debt, quality_rating, created_at"
            )
            .eq("user_id", current_user.user.id)
            .order("date", ascending=False)
            .limit(1)
            .execute()
        )
        time_resp = (
            supabase.from_("time_entries")
            .select(
                "id, user_id, start_time, end_time, duration_minutes, category, is_deep_work, description, created_at"
            )
            .eq("user_id", current_user.user.id)
            .gte("start_time", datetime.now().strftime("%Y-%m-%d"))
            .execute()
        )
        history_resp = (
            supabase.from_("chat_messages")
            .select("role, content")
            .eq("user_id", current_user.user.id)
            .order("created_at", ascending=False)
            .limit(10)
            .execute()
        )

        pending_tasks = tasks_resp.data or []
        active_goals = goals_resp.data or []
        courses = courses_resp.data or []
        habits = habits_resp.data or []
        sleep_logs = sleep_resp.data or []
        time_entries = time_resp.data or []
        recent_messages = list(reversed(history_resp.data or []))
        memory = {}
        try:
            memory = await get_memory_summary(current_user.user.id)
        except Exception as e:
            logger.warn("Memory summary unavailable for chat", error=str(e))

        system_override = request_body.context or ""
        aria_prompt = prompts.get_system("aria_system")
        if aria_prompt:
            system = aria_prompt.system_prompt
            if system_override:
                system = system + "\n" + system_override
        else:
            system = "You are ARIA, an AI assistant for a BTech CSE student's productivity system."

        context_block = build_context(
            pending_tasks, active_goals, courses, habits, sleep_logs, time_entries, recent_messages, memory
        )
        user_prompt = f"""Based on the user's current context, respond to their message.

{context_block}

User message: {message}

Respond conversationally and helpfully. Be concise but thorough. If they ask about tasks, suggest specific actions. If they ask about their day, provide a brief overview. Always be supportive and direct."""

        response_text = await llm.generate(user_prompt, system=system, max_tokens=1024, temperature=0.7)

    except LLMProviderUnavailableError:
        logger.warn("LLM unavailable, falling back to keyword routing for chat", user_id=current_user.user.id)
        message_lower = message.lower()
        if "task" in message_lower or "todo" in message_lower:
            if pending_tasks:
                top_task = pending_tasks[0]
                response_text = f"You have {len(pending_tasks)} pending tasks. Your top priority is: '{top_task.get('title', 'Untitled')}'. Would you like me to help you complete it?"
            else:
                response_text = "You have no pending tasks! Great job. Would you like to add a new task?"
        elif "goal" in message_lower:
            if active_goals:
                response_text = f"You have {len(active_goals)} active goals. Your goals are: {', '.join([g.get('title', '') for g in active_goals[:3]])}. Keep pushing towards them!"
            else:
                response_text = "You don't have any active goals. Setting goals helps you stay focused. Would you like to create one?"
        elif "course" in message_lower or "learn" in message_lower:
            in_progress = [c for c in courses if c.get("status") == "in_progress"]
            if in_progress:
                response_text = f"You're currently taking {len(in_progress)} courses. Keep up the good work! What's your focus right now?"
            else:
                response_text = (
                    "Start learning! Add courses from Udemy, Coursera, NPTEL, or YouTube to track your progress."
                )
        elif "help" in message_lower:
            response_text = "I'm here to help! Ask me about your tasks, goals, courses, habits, or projects. I can also help you plan your day or suggest what to focus on."
        elif "habit" in message_lower:
            active_habits = [h for h in habits if h.get("is_active")] if habits else []
            if active_habits:
                response_text = f"You have {len(active_habits)} active habits. Best streak: {max(h.get('current_streak', 0) for h in active_habits)} days. Keep it going!"
            else:
                response_text = (
                    "No habits tracked yet. Start with something small like 'Code for 30 minutes' or 'Read before bed'."
                )
        else:
            response_text = f"I understand you're asking about: '{message}'. To get personalized help, ask me about your tasks, goals, courses, habits, or projects."

    supabase.from_("chat_messages").insert(
        {"user_id": current_user.user.id, "role": "user", "content": message}
    ).execute()
    supabase.from_("chat_messages").insert(
        {"user_id": current_user.user.id, "role": "assistant", "content": response_text}
    ).execute()

    try:
        await store_interaction(current_user.user.id, "chat", message, {"response_preview": response_text[:200]})
    except Exception as e:
        logger.warn("Failed to store memory interaction", error=str(e))

    return ChatResponse(response=response_text, action_taken=None)
