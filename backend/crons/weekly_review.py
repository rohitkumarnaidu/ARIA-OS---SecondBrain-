from datetime import datetime, timedelta
from app.core.supabase import get_supabase_client


async def generate_weekly_review(user_id: str) -> dict:
    supabase = get_supabase_client()

    week_ago = (datetime.now() - timedelta(days=7)).isoformat()

    tasks_resp = (
        supabase.from_("tasks")
        .select("*")
        .eq("user_id", user_id)
        .gte("created_at", week_ago)
        .execute()
    )
    completed_resp = (
        supabase.from_("tasks")
        .select("*")
        .eq("user_id", user_id)
        .eq("status", "completed")
        .gte("completed_at", week_ago)
        .execute()
    )
    courses_resp = (
        supabase.from_("courses").select("*").eq("user_id", user_id).execute()
    )
    income_resp = (
        supabase.from_("income")
        .select("*")
        .eq("user_id", user_id)
        .gte("date", week_ago)
        .execute()
    )
    goals_resp = (
        supabase.from_("goals")
        .select("*")
        .eq("user_id", user_id)
        .eq("status", "active")
        .execute()
    )

    tasks = tasks_resp.data or []
    completed = completed_resp.data or []
    courses = courses_resp.data or []
    incomes = income_resp.data or []
    goals = goals_resp.data or []

    total_income = sum(i.get("amount", 0) for i in incomes)
    avg_progress = sum(g.get("progress", 0) for g in goals) / len(goals) if goals else 0

    review = {
        "generated_at": datetime.now().isoformat(),
        "period": f"{(datetime.now() - timedelta(days=7)).date()} to {datetime.now().date()}",
        "tasks": {
            "created": len(tasks),
            "completed": len(completed),
            "completion_rate": round((len(completed) / len(tasks) * 100), 1)
            if tasks
            else 0,
        },
        "courses": {
            "active": len([c for c in courses if c.get("status") == "in_progress"]),
            "completed": len([c for c in courses if c.get("status") == "completed"]),
        },
        "income": {"total": total_income, "sources": len(incomes)},
        "goals": {"active": len(goals), "avg_progress": round(avg_progress, 1)},
        "insight": generate_insight(tasks, completed, courses, goals),
    }

    supabase.from_("weekly_reviews").insert(
        {"user_id": user_id, "data": review, "week_start": week_ago}
    ).execute()

    return review


def generate_insight(tasks: list, completed: list, courses: list, goals: list) -> str:
    if not completed:
        return "You didn't complete any tasks this week. Try breaking big tasks into smaller ones."

    completion_rate = len(completed) / len(tasks) * 100 if tasks else 0

    if completion_rate >= 80:
        return "Excellent week! You're completing tasks at a high rate. Keep this momentum going!"
    elif completion_rate >= 50:
        return "Good progress this week. Focus on finishing pending tasks before starting new ones."
    else:
        return "You started many tasks but didn't finish them. Try completing one task before starting another."


async def run_weekly_review():
    supabase = get_supabase_client()
    users_resp = supabase.from_("users").select("id").execute()

    for user in users_resp.data or []:
        try:
            review = await generate_weekly_review(user["id"])
            print(
                f"Weekly review generated for {user['id']}: {review['tasks']['completion_rate']}% completion"
            )
        except Exception as e:
            print(f"Error generating review for {user['id']}: {e}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_weekly_review())
