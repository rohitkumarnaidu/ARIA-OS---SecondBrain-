import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from config.core.supabase import get_supabase_client
from ai.client import llm, LLMProviderUnavailableError
from ai.prompt_loader import prompts
try:
    from ai.brave_search import fetch_opportunities_from_web
except ImportError:
    fetch_opportunities_from_web = None
from shared.utils.logger import logger
import httpx

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


def calculate_skill_overlap(user_skills: List[str], opportunity_skills: List[str]) -> float:
    if not user_skills or not opportunity_skills:
        return 0.0
    us = set(s.strip().lower() for s in user_skills if s)
    them = set(s.strip().lower() for s in opportunity_skills if s)
    if not us or not them:
        return 0.0
    intersection = us & them
    union = us | them
    return round(len(intersection) / len(union), 4)


def tier_notification_opportunities(opportunities: List[dict]) -> dict:
    urgent = []
    high_match = []
    regular = []
    now = datetime.now()
    for opp in opportunities:
        match_score = opp.get("match_score", 0) or 0
        deadline = opp.get("deadline")
        is_urgent = False
        if deadline:
            try:
                deadline_dt = datetime.fromisoformat(deadline) if isinstance(deadline, str) else deadline
                hours_left = (deadline_dt - now).total_seconds() / 3600
                if 0 < hours_left < 48:
                    is_urgent = True
            except (ValueError, TypeError):
                pass
        if is_urgent:
            urgent.append(opp)
        elif match_score >= 70:
            high_match.append(opp)
        else:
            regular.append(opp)
    return {
        "urgent": urgent,
        "high_match": high_match,
        "regular": regular,
        "counts": {"urgent": len(urgent), "high_match": len(high_match), "regular": len(regular)},
    }


def deduplicate_opportunities(opportunities: List[dict]) -> List[dict]:
    seen: set = set()
    deduped: List[dict] = []
    for opp in opportunities:
        url = (opp.get("url") or "").strip().lower().rstrip("/")
        title = (opp.get("title") or "").strip().lower()
        if url:
            key = url
        else:
            key = hashlib.md5(title.encode()).hexdigest()[:16]
        if key not in seen:
            seen.add(key)
            deduped.append(opp)
    return deduped


async def fetch_rss_feeds(feed_urls: List[str]) -> List[dict]:
    if not feed_urls:
        return []
    items: List[dict] = []
    async with httpx.AsyncClient(timeout=15) as client:
        for url in feed_urls:
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                text = resp.text
                entries = _parse_rss_xml(text, url)
                items.extend(entries)
            except Exception as e:
                logger.warn("RSS fetch failed", url=url, error=str(e))
    return items


def _parse_rss_xml(xml_text: str, source_url: str) -> List[dict]:
    import re
    items: List[dict] = []
    item_pattern = re.compile(r"<item>(.*?)</item>", re.DOTALL)
    title_pattern = re.compile(r"<title>(.*?)</title>", re.DOTALL)
    link_pattern = re.compile(r"<link>(.*?)</link>", re.DOTALL)
    desc_pattern = re.compile(r"<description>(.*?)</description>", re.DOTALL)
    date_pattern = re.compile(r"<pubDate>(.*?)</pubDate>", re.DOTALL)
    for match in item_pattern.finditer(xml_text):
        block = match.group(1)
        title = _unescape_xml(_extract_first(title_pattern, block)) or "Untitled"
        link = _unescape_xml(_extract_first(link_pattern, block)) or ""
        desc = _unescape_xml(_extract_first(desc_pattern, block)) or ""
        pub_date = _extract_first(date_pattern, block) or ""
        try:
            parsed_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
            deadline = parsed_date.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            deadline = (datetime.now() + timedelta(days=30)).isoformat()[:10]
        items.append({
            "title": title,
            "url": link,
            "description": desc[:300],
            "deadline": deadline,
            "category": "rss",
            "source_url": source_url,
            "match_score": 50,
        })
    return items


def _extract_first(pattern, text: str) -> Optional[str]:
    m = pattern.search(text)
    return m.group(1).strip() if m else None


def _unescape_xml(text: Optional[str]) -> Optional[str]:
    if not text:
        return text
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&#39;", "'")
    import re
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()
