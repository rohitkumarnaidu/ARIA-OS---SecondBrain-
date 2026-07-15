from datetime import datetime, timedelta, timezone
from uuid import uuid4

from config.core.supabase import get_supabase_client
from shared.utils.logger import logger


async def run_deadline_alert():
    supabase = get_supabase_client()
    now = datetime.now(timezone.utc)
    deadline_cutoff = now + timedelta(hours=48)

    try:
        result = (
            supabase.from_("opportunities")
            .select("id, title, deadline, match_score, user_id")
            .not_.is_("deadline", "null")
            .lte("deadline", deadline_cutoff.isoformat())
            .execute()
        )
    except Exception as e:
        logger.error("Failed to fetch opportunities for deadline alerts", error=str(e))
        return 0

    opportunities = result.data or []
    if not opportunities:
        logger.info("Deadline alert: no opportunities closing within 48h")
        return 0

    opportunities = [
        o for o in opportunities
        if o.get("deadline") and datetime.fromisoformat(o["deadline"]) > now
    ]

    if not opportunities:
        logger.info("Deadline alert: no upcoming deadlines within 48h")
        return 0

    alerts_sent = 0
    for opp in opportunities:
        try:
            existing = (
                supabase.from_("notifications")
                .select("id, action_url")
                .eq("user_id", opp["user_id"])
                .eq("category", "deadline_alert")
                .execute()
            )

            already_alerted = any(
                opp["id"] in (n.get("action_url") or "")
                for n in existing.data or []
            )
            if already_alerted:
                continue

            hours_left = (datetime.fromisoformat(opp["deadline"]) - now).total_seconds() / 3600
            urgency = "critical" if hours_left < 24 else "warning"

            notification = {
                "id": str(uuid4()),
                "user_id": opp["user_id"],
                "title": f"Opportunity Closing Soon: {opp['title']}",
                "message": f"'{opp['title']}' closes in {int(hours_left)}h. Match score: {opp.get('match_score', 'N/A')}%.",
                "category": "deadline_alert",
                "priority": "high" if urgency == "critical" else "medium",
                "read": False,
                "action_url": f"/opportunities?id={opp['id']}",
                "icon": "alert-triangle",
                "created_at": now.isoformat(),
            }
            supabase.from_("notifications").insert(notification).execute()
            alerts_sent += 1

        except Exception as e:
            logger.error(
                "Failed to create deadline alert",
                opportunity_id=opp["id"],
                user_id=opp["user_id"],
                error=str(e),
            )

    logger.info("Deadline alert complete", alerts_sent=alerts_sent)
    return alerts_sent


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_deadline_alert())
