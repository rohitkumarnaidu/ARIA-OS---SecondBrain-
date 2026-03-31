from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.supabase import get_supabase_client
from app.core.auth import get_current_user

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    action_taken: Optional[str] = None

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user = Depends(get_current_user)):
    supabase = get_supabase_client()
    
    # Get user context
    tasks_response = supabase.from_("tasks").select("*").eq("user_id", current_user.user.id).eq("status", "pending").execute()
    goals_response = supabase.from_("goals").select("*").eq("user_id", current_user.user.id).eq("status", "active").execute()
    courses_response = supabase.from_("courses").select("*").eq("user_id", current_user.user.id).execute()
    
    pending_tasks = tasks_response.data or []
    active_goals = goals_response.data or []
    courses = courses_response.data or []
    
    # Build context
    context = f"""
User has {len(pending_tasks)} pending tasks, {len(active_goals)} active goals, and {len(courses)} courses.
"""
    
    # Simple rule-based response for now
    message_lower = request.message.lower()
    
    if "task" in message_lower or "todo" in message_lower:
        if pending_tasks:
            top_task = pending_tasks[0]
            response = f"You have {len(pending_tasks)} pending tasks. Your top priority is: '{top_task.get('title', 'Untitled')}'. Would you like me to help you complete it?"
        else:
            response = "You have no pending tasks! Great job. Would you like to add a new task?"
    
    elif "goal" in message_lower:
        if active_goals:
            response = f"You have {len(active_goals)} active goals. Your goals are: {', '.join([g.get('title', '') for g in active_goals[:3]])}. Keep pushing towards them!"
        else =="""You don't have any active goals. Setting goals helps you stay focused. Would you like to create one?""
    
    elif "course" in message_lower or "learn" in message_lower:
        in_progress = [c for c in courses if c.get("status") == "in_progress"]
        if in_progress:
            response = f"You're currently taking {len(in_progress)} courses. Keep up the good work! What's your focus right now?"
        else:
            response = "Start learning! Add courses from Udemy, Coursera, NPTEL, or YouTube to track your progress."
    
    elif "help" in message_lower:
        response = "I'm here to help! Ask me about your tasks, goals, courses, or ideas. I can also help you plan your day or suggest what to focus on."
    
    else:
        response = f"I understand you're asking about: '{request.message}'. To get personalized help, ask me about your tasks, goals, courses, or ideas!"
    
    # Save message to chat_history
    supabase.from_("chat_messages").insert({
        "user_id": current_user.user.id,
        "role": "user",
        "content": request.message
    })
    supabase.from_("chat_messages").insert({
        "user_id": current_user.user.id,
        "role": "assistant",
        "content": response
    })
    
    return ChatResponse(response=response, action_taken=None)