from ai.agents.weekly_review_agent import generate_weekly_review
from config.core.supabase import get_supabase_client
from shared.utils.logger import logger
from shared.utils.security import sanitize_input


async def run_weekly_review():
    supabase = get_supabase_client()
    users_resp = supabase.from_("users").select("id").execute()

    for user in users_resp.data or []:
        try:
            review = await generate_weekly_review(sanitize_input(user["id"]))
            logger.info("Weekly review generated", user_id=user["id"], completion_rate=review.get("completion_rate", 0))
        except Exception as e:
            logger.error("Weekly review error", user_id=user["id"], error=str(e))


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_weekly_review())
