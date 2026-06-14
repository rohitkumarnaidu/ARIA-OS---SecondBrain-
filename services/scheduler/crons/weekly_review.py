from ai.agents.weekly_review_agent import generate_weekly_review
from config.core.supabase import get_supabase_client


async def run_weekly_review():
    supabase = get_supabase_client()
    users_resp = supabase.from_("users").select("id").execute()

    for user in users_resp.data or []:
        try:
            review = await generate_weekly_review(user["id"])
            print(f"Weekly review: {user['id']} — {review.get('completion_rate', 0)}%")
        except Exception as e:
            print(f"Weekly review error for {user['id']}: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_weekly_review())
