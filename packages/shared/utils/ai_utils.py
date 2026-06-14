import os
import json
from typing import Optional, Dict, Any


def get_ai_response(prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
    use_local = os.getenv("USE_LOCAL_AI", "true").lower() == "true"

    if use_local:
        return get_ollama_response(prompt, context)
    else:
        return get_claude_response(prompt, context)


def get_ollama_response(prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
    import httpx

    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    try:
        response = httpx.post(
            f"{ollama_url}/api/generate",
            json={"model": "llama2", "prompt": prompt, "stream": False},
            timeout=30,
        )
        if response.status_code == 200:
            return response.json().get("response", "No response")
    except Exception as e:
        print(f"Ollama error: {e}")

    return "AI response unavailable. Please try again later."


def get_claude_response(prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
    import anthropic

    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        return "Claude API key not configured."

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
    except Exception as e:
        print(f"Claude error: {e}")
        return "AI response unavailable."


def generate_task_summary(tasks: list) -> str:
    urgent = [t for t in tasks if t.get("priority") == "urgent"]
    high = [t for t in tasks if t.get("priority") == "high"]

    summary = f"You have {len(tasks)} pending tasks."
    if urgent:
        summary += f" {len(urgent)} are urgent."
    if high:
        summary += f" {len(high)} are high priority."

    return summary


def generate_course_recommendation(skills: list, goals: list) -> list:
    recommendations = []

    skill_keywords = {
        "python": ["Python for Everybody", "Complete Python Bootcamp"],
        "javascript": ["JavaScript Fundamentals", "React.js Course"],
        "react": ["React - The Complete Guide", "React Native Course"],
        "machine learning": ["Machine Learning A-Z", "Deep Learning Course"],
        "web development": ["Full Stack Web Development", "Web Design Course"],
    }

    for skill in skills:
        skill_lower = skill.lower()
        for keyword, courses in skill_keywords.items():
            if keyword in skill_lower:
                recommendations.extend(courses)

    return recommendations[:5]


def summarize_video(video_title: str, transcript: str) -> str:
    prompt = f"Summarize this video in 3 sentences:\n\nTitle: {video_title}\n\nContent: {transcript[:2000]}"
    return get_ai_response(prompt)
