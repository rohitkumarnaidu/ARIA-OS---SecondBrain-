from datetime import date
from ai.agents.sleep_agent import analyze_sleep, suggest_bedtime
from config.core.supabase import get_supabase_client


async def run_sleep_reminder():
    supabase = get_supabase_client()
    today = date.today().isoformat()
    users_resp = supabase.from_("users").select("id, sleep_goal_bedtime").execute()

    for user in users_resp.data or []:
        try:
            log_resp = (
                supabase.from_("sleep_logs")
                .select("*")
                .eq("user_id", user["id"])
                .gte("created_at", today)
                .execute()
            )
            if not log_resp.data:
                bedtime = await suggest_bedtime(user["id"])
                goal = user.get("sleep_goal_bedtime") or "23:00"
                print(f"Sleep nudge for {user['id']}: bedtime {bedtime['suggested_bedtime']} (goal: {goal})")
        except Exception as e:
            print(f"Sleep reminder error for {user['id']}: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_sleep_reminder())
