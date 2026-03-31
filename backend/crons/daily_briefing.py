from datetime import datetime, timedelta
from app.core.supabase import get_supabase_client
from agents.briefing_agent import generate_daily_briefing


async def run_daily_briefing():
    supabase = get_supabase_client()
    users_resp = supabase.from_("users").select("id").execute()

    for user in users_resp.data or []:
        try:
            briefing = await generate_daily_briefing(user["id"])
            print(
                f"Briefing generated for user {user['id']}: {briefing.get('productivity_score')}"
            )
        except Exception as e:
            print(f"Error generating briefing for {user['id']}: {e}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_daily_briefing())
