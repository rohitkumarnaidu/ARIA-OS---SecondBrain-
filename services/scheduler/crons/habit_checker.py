from datetime import date
from config.core.supabase import get_supabase_client
from shared.utils.logger import logger


async def run_habit_checker():
    supabase = get_supabase_client()
    today = date.today().isoformat()
    users_resp = supabase.from_("users").select("id").execute()

    for user in users_resp.data or []:
        try:
            habits_resp = supabase.from_("habits").select("*").eq("user_id", user["id"]).eq("is_active", True).execute()
            habits = habits_resp.data or []

            for habit in habits:
                logs_resp = (
                    supabase.from_("habit_logs").select("*").eq("habit_id", habit["id"]).eq("date", today).execute()
                )
                if not logs_resp.data:
                    logger.info("Habit not logged today", user_id=user["id"], habit_name=habit["name"])
        except Exception as e:
            logger.error("Error checking habits", user_id=user["id"], error=str(e))


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_habit_checker())
