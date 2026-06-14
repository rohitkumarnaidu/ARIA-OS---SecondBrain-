from ai.agents.nudge_agent import run_all_nudges
from config.core.supabase import get_supabase_client


async def run_course_nudges():
    supabase = get_supabase_client()
    users_resp = supabase.from_("users").select("id").execute()

    for user in users_resp.data or []:
        try:
            result = await run_all_nudges(user["id"])
            if result["total_nudges"] > 0:
                print(f"Nudges for {user['id']}: {result['total_nudges']} total "
                      f"({len(result['course_nudges'])} course, {len(result['habit_nudges'])} habit)")
        except Exception as e:
            print(f"Nudge error for {user['id']}: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_course_nudges())
