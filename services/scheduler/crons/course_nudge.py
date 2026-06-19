from ai.agents.nudge_agent import run_all_nudges
from config.core.supabase import get_supabase_client
from shared.utils.logger import logger
from shared.utils.security import sanitize_input


async def run_course_nudges():
    supabase = get_supabase_client()
    users_resp = supabase.from_("users").select("id").execute()

    for user in users_resp.data or []:
        try:
            result = await run_all_nudges(sanitize_input(user["id"]))
            if result["total_nudges"] > 0:
                logger.info(
                    "Nudges sent",
                    user_id=user["id"],
                    total_nudges=result["total_nudges"],
                    course_nudges=len(result["course_nudges"]),
                    habit_nudges=len(result["habit_nudges"]),
                )
        except Exception as e:
            logger.error("Nudge error", user_id=user["id"], error=str(e))


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_course_nudges())
