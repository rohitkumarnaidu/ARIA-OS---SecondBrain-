from datetime import datetime, timedelta
from config.core.supabase import get_supabase_client


async def run_missed_task_checker():
    supabase = get_supabase_client()
    now = datetime.now().isoformat()
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
                supabase.from_("tasks").update({
                    "status": "missed",
                    "missed_count": (task.get("missed_count") or 0) + 1,
                }).eq("id", task["id"]).execute()

            if overdue:
                print(f"Marked {len(overdue)} missed tasks for user {user['id']}")
        except Exception as e:
            print(f"Error checking missed tasks for {user['id']}: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_missed_task_checker())
