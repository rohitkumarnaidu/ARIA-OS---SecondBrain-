from datetime import datetime, timedelta
from typing import List, Dict, Any
from config.core.supabase import get_supabase_client
from ai.client import llm, LLMProviderUnavailableError
from ai.prompt_loader import prompts
from ai.brave_search import fetch_opportunities_from_web

CATEGORIES = {
    "internships": ["LinkedIn", "Internshala", "AngelList", "HackerEarth"],
    "hackathons": ["Devfolio", "MLH", "HackerEarth", "Devpost"],
    "open_source": ["GitHub Good First Issues", "GSoC", "GSOC", "Outreachy"],
    "startup_competitions": ["NASSCOM", "Startup India", "TiE"],
    "fellowships": ["Buddy4Study", "Vidyasaarathi", "Fellowships"],
    "freelance": ["Fiverr", "Upwork", "Toptal"],
}


async def run_opportunity_radar(user_id: str) -> List[Dict[str, Any]]:
    supabase = get_supabase_client()
    user_resp = supabase.from_("users").select("skills, interests").eq("id", user_id).execute()
    user_data = user_resp.data[0] if user_resp.data else {}
    user_skills = user_data.get("skills", [])
    user_interests = user_data.get("interests", [])

    opp_prompt = prompts.get_agent("opportunity_radar_agent")
    web_opps = await fetch_opportunities_from_web(user_skills, user_interests)
    web_context = (
        "\n".join(f"- {o['title']} ({o['category']}) - {o['description'][:100]}" for o in web_opps[:5])
        if web_opps
        else "No web results found."
    )

    if opp_prompt:
        system_prompt = opp_prompt.system_prompt
        user_prompt = (
            f"Scan for opportunities matching:\n"
            f"Skills: {user_skills}\n"
            f"Interests: {user_interests}\n"
            f"Web search results:\n{web_context}\n"
            f"Return JSON array of objects with: title, category, url, deadline (ISO date), "
            f"description, skills_needed (array), match_score (0-100)."
        )
    else:
        system_prompt = "You are a career opportunity scout for CS students. Return only valid JSON."
        user_prompt = (
            f"Student skills: {user_skills}, interests: {user_interests}. "
            f"Web results:\n{web_context}\n"
            f"Suggest 5 relevant opportunities (internships, hackathons, open source programs). "
            f"Return JSON array of objects with: title, category, url, deadline (ISO date 30-90 days from now), "
            f"description, skills_needed (array), match_score (0-100)."
        )

    try:
        opportunities = await llm.generate_json(user_prompt, system=system_prompt)
    except LLMProviderUnavailableError:
        opportunities = []

    opp_list = opportunities if isinstance(opportunities, list) else opportunities.get("opportunities", [])
    if not opp_list:
        opp_list = scan_default_opportunities(user_skills)

    for opp in opp_list:
        opp["user_id"] = user_id
        opp["discovered_at"] = datetime.now().isoformat()
        supabase.from_("opportunities").insert(opp).execute()

    return opp_list[:10]


def scan_default_opportunities(skills: List[str]) -> List[Dict[str, Any]]:
    now = datetime.now()
    return [
        {
            "title": "Google Summer of Code 2026",
            "category": "open_source",
            "url": "https://summerofcode.withgoogle.com/",
            "deadline": (now + timedelta(days=60)).isoformat(),
            "description": "Get paid to contribute to open source",
            "skills_needed": ["Python", "Java", "Go"],
            "match_score": 80,
        },
        {
            "title": "MLH Fellowship",
            "category": "open_source",
            "url": "https://mlh.io",
            "deadline": (now + timedelta(days=30)).isoformat(),
            "description": "Remote fellowship for developers",
            "skills_needed": ["JavaScript", "Python", "React"],
            "match_score": 75,
        },
        {
            "title": "Microsoft Explore Internship",
            "category": "internships",
            "url": "https://careers.microsoft.com",
            "deadline": (now + timedelta(days=20)).isoformat(),
            "description": "Summer internship for students",
            "skills_needed": ["C++", "Python", "Problem Solving"],
            "match_score": 85,
        },
    ]


def calculate_match_score(opp: Dict[str, Any], user_skills: List[str], user_interests: List[str]) -> float:
    return opp.get("match_score", 50)
