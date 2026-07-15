from datetime import datetime, timezone
from config.core.supabase import get_supabase_client
from shared.utils.logger import logger


async def run_missed_task_checker():
    supabase = get_supabase_client()
    now = datetime.now(timezone.utc).isoformat()
    users_resp = supabase.from_("users").select("id").execute()

    for user in users_resp.data or []:
        try:
            overdue_resp = (
                supabase.from_("tasks")
                .select("*")
                .eq("user_id", user["id"])
                .eq("status", "pending")
                .lt("due_date", now)
                .execute()
            )
            overdue = overdue_resp.data or []

            for task in overdue:
                supabase.from_("tasks").update(
                    {
                        "status": "missed",
                        "missed_count": (task.get("missed_count") or 0) + 1,
                    }
                ).eq("id", task["id"]).execute()

            if overdue:
                logger.info("Missed tasks marked", user_id=user["id"], count=len(overdue))
        except Exception as e:
            logger.error("Error checking missed tasks", user_id=user["id"], error=str(e))


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_missed_task_checker())
