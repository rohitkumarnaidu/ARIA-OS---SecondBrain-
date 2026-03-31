from datetime import datetime
from app.core.supabase import get_supabase_client
from agents.opportunity_agent import run_opportunity_radar


async def run_radar():
    supabase = get_supabase_client()
    users_resp = supabase.from_("users").select("id").execute()

    for user in users_resp.data or []:
        try:
            opportunities = await run_opportunity_radar(user["id"])
            print(f"Found {len(opportunities)} opportunities for user {user['id']}")
        except Exception as e:
            print(f"Error scanning opportunities for {user['id']}: {e}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_radar())
