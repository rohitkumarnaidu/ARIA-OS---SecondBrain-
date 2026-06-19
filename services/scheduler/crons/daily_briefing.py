from config.core.supabase import get_supabase_client
from ai.agents.briefing_agent import generate_daily_briefing
from shared.utils.logger import logger
from shared.utils.security import sanitize_input


async def run_daily_briefing():
    supabase = get_supabase_client()
    users_resp = supabase.from_("users").select("id").execute()

    for user in users_resp.data or []:
        try:
            briefing = await generate_daily_briefing(sanitize_input(user["id"]))
            logger.info("Briefing generated", user_id=user["id"], productivity_score=briefing.get("productivity_score"))
        except Exception as e:
            logger.error("Error generating briefing", user_id=user["id"], error=str(e))


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_daily_briefing())
