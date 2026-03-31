from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.core.supabase import get_supabase_client


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

    user_resp = (
        supabase.from_("users").select("skills, interests").eq("id", user_id).execute()
    )
    user_data = user_resp.data[0] if user_resp.data else {}
    user_skills = user_data.get("skills", [])
    user_interests = user_data.get("interests", [])

    opportunities = scan_all_categories(user_skills, user_interests)

    scored_opportunities = []
    for opp in opportunities:
        score = calculate_match_score(opp, user_skills, user_interests)
        opp["match_score"] = score
        if score >= 40:
            scored_opportunities.append(opp)

    scored_opportunities.sort(
        key=lambda x: (x.get("match_score", 0), x.get("deadline_priority", 0)),
        reverse=True,
    )

    for opp in scored_opportunities[:20]:
        opp["user_id"] = user_id
        opp["discovered_at"] = datetime.now().isoformat()
        supabase.from_("opportunities").insert(opp).execute()

    return scored_opportunities[:10]


def scan_all_categories(
    skills: List[str], interests: List[str]
) -> List[Dict[str, Any]]:
    opportunities = []
    now = datetime.now()

    mock_opportunities = [
        {
            "title": "Google Summer of Code 2026",
            "category": "open_source",
            "url": "https://summerofcode.withgoogle.com/",
            "deadline": (now + timedelta(days=60)).isoformat(),
            "description": "Get paid to contribute to open source",
            "skills_needed": ["Python", "Java", "Go"],
        },
        {
            "title": "MLH Fellowship",
            "category": "open_source",
            "url": "https://mlh.io",
            "deadline": (now + timedelta(days=30)).isoformat(),
            "description": "Remote fellowship for developers",
            "skills_needed": ["JavaScript", "Python", "React"],
        },
        {
            "title": "Startup India Fellowship",
            "category": "startup_competitions",
            "url": "https://startupindia.gov.in",
            "deadline": (now + timedelta(days=45)).isoformat(),
            "description": "Fellowship for student entrepreneurs",
            "skills_needed": ["Business", "Tech"],
        },
        {
            "title": "Microsoft Explore Internship",
            "category": "internships",
            "url": "https://careers.microsoft.com",
            "deadline": (now + timedelta(days=20)).isoformat(),
            "description": "Summer internship for students",
            "skills_needed": ["C++", "Python", "Problem Solving"],
        },
        {
            "title": "Devfolio Hackathon Season",
            "category": "hackathons",
            "url": "https://devfolio.co",
            "deadline": (now + timedelta(days=15)).isoformat(),
            "description": "Monthly hackathons with prizes",
            "skills_needed": ["Any"],
        },
    ]

    for opp in mock_opportunities:
        if (
            any(
                skill.lower() in [s.lower() for s in opp["skills_needed"]]
                for skill in skills
            )
            or not skills
        ):
            opportunities.append(opp)
        elif any(
            interest.lower() in opp["description"].lower() for interest in interests
        ):
            opportunities.append(opp)

    return opportunities


def calculate_match_score(
    opp: Dict[str, Any], user_skills: List[str], user_interests: List[str]
) -> float:
    score = 50

    required_skills = [s.lower() for s in opp.get("skills_needed", [])]
    if required_skills and required_skills != ["any"]:
        matched = sum(1 for skill in user_skills if skill.lower() in required_skills)
        skill_match = (matched / len(required_skills)) * 40 if required_skills else 0
        score = min(100, score + skill_match)

    deadline = (
        datetime.fromisoformat(opp.get("deadline", ""))
        if opp.get("deadline")
        else datetime.now() + timedelta(days=30)
    )
    days_until = (deadline - datetime.now()).days
    if days_until < 2:
        score += 30
    elif days_until < 7:
        score += 20
    elif days_until < 14:
        score += 10

    return min(100, score)
