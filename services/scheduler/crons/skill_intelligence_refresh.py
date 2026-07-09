from config.core.supabase import get_supabase_client
from shared.utils.logger import logger


async def run_skill_intelligence_refresh():
    supabase = get_supabase_client()

    stale_resp = supabase.from_("skill_market_data").select("skill_id").eq("data_freshness", "stale").execute()
    stale_skills = stale_resp.data or []

    marked = (
        supabase.from_("skill_market_data")
        .update({"data_freshness": "refreshing"})
        .eq("data_freshness", "stale")
        .execute()
    )
    logger.info(
        "Skill intelligence refresh started",
        stale_count=len(stale_skills),
        marked_count=len(marked.data or []),
    )

    for skill in stale_skills[:50]:
        try:
            supabase.from_("skill_market_history").insert(
                {
                    "skill_id": skill["skill_id"],
                    "demand_score": None,
                    "growth_score": None,
                    "salary_median": None,
                    "competition_score": None,
                    "future_relevance": None,
                    "snapshot_source": "scheduled_refresh",
                }
            ).execute()
        except Exception as e:
            logger.error("Skill intelligence refresh error", skill_id=skill["skill_id"], error=str(e))

    if stale_skills:
        supabase.from_("skill_market_data").update({"data_freshness": "current"}).eq(
            "data_freshness", "refreshing"
        ).execute()

    logger.info("Skill intelligence refresh completed", processed=min(len(stale_skills), 50))


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_skill_intelligence_refresh())
