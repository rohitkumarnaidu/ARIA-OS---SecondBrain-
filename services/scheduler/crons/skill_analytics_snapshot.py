from datetime import date, datetime
from config.core.supabase import get_supabase_client
from shared.utils.logger import logger


async def run_skill_analytics_snapshot():
    supabase = get_supabase_client()
    today = date.today().isoformat()
    now_ms = int(datetime.now().timestamp() * 1000)

    users_resp = supabase.from_("users").select("id").execute()
    users = users_resp.data or []

    snapshot_count = 0
    for user in users:
        try:
            user_id = user["id"]
            us_resp = supabase.from_("user_skills").select("level, state").eq("user_id", user_id).execute()
            user_skills = us_resp.data or []

            if not user_skills:
                continue

            levels = [s["level"] for s in user_skills]
            active = [s for s in user_skills if s["state"] in ("active", "practicing")]
            emerging = [s for s in user_skills if s.get("is_emerging")]

            snapshot = {
                "user_id": user_id,
                "snapshot_date": today,
                "avg_skill_level": round(sum(levels) / len(levels), 2) if levels else 0,
                "skill_count": len(user_skills),
                "readiness_score": round(sum(levels) / (len(levels) * 5) * 100, 1) if levels else 0,
                "learning_velocity": 0,
                "diversification_score": round(len(active) / max(len(user_skills), 1), 2),
                "emerging_coverage": len(emerging),
                "evidence_ratio": 0,
                "created_at": now_ms,
            }

            result = supabase.from_("skill_analytics_snapshots").upsert(
                snapshot,
                on_conflict="user_id, snapshot_date",
            ).execute()
            if result.data:
                snapshot_count += 1

        except Exception as e:
            logger.error("Analytics snapshot error", user_id=user.get("id"), error=str(e))

    logger.info("Daily skill analytics snapshot completed", users_processed=len(users), snapshots_created=snapshot_count)


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_skill_analytics_snapshot())
