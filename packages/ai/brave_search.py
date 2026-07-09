import aiohttp
from typing import List, Dict, Any
from config.core.config import settings

BRAVE_API_BASE = "https://api.search.brave.com/res/v1/web/search"


async def brave_search(query: str, count: int = 5) -> List[Dict[str, Any]]:
    if not settings.brave_api_key:
        return []
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": settings.brave_api_key,
    }
    params = {
        "q": query,
        "count": min(count, 10),
        "text_format": "raw",
        "safe": "off",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                BRAVE_API_BASE, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                results = data.get("web", {}).get("results", [])
                return [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "description": r.get("description", ""),
                        "age": r.get("age", ""),
                    }
                    for r in results
                ]
    except Exception:
        return []


OPPORTUNITY_QUERIES = {
    "internships": [
        "software engineering internship 2026 students",
        "CS internship apply now 2026",
        "tech internship hiring students",
    ],
    "hackathons": [
        "hackathon 2026 online apply",
        "student hackathon upcoming",
        "college hackathon register",
    ],
    "open_source": [
        "open source programs 2026 students",
        "GSoC organizations 2026",
        "Outreachy internships open source",
    ],
    "startup_competitions": [
        "startup competition 2026 students",
        "business plan competition college",
        "entrepreneurship contest for students",
    ],
    "fellowships": [
        "fellowship 2026 computer science students",
        "tech fellowship apply now",
        "research internship fellowship students",
    ],
    "freelance": [
        "freelance developer remote jobs 2026",
        "freelance coding projects beginners",
    ],
}


async def fetch_opportunities_from_web(skills: List[str], interests: List[str]) -> List[Dict[str, Any]]:
    opportunities: List[Dict[str, Any]] = []
    seen_urls: set = set()

    for category, queries in OPPORTUNITY_QUERIES.items():
        for query in queries:
            enriched = f"{query} {' '.join(skills[:3])} {' '.join(interests[:2])}"
            results = await brave_search(enriched, count=3)
            for r in results:
                url = r.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    opportunities.append(
                        {
                            "title": r.get("title", "Untitled"),
                            "category": category,
                            "url": url,
                            "description": r.get("description", ""),
                            "source": "brave_search",
                            "skills_needed": skills[:3],
                            "match_score": 50,
                        }
                    )
    return opportunities[:20]
