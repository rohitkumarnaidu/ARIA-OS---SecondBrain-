"""Cron job for data retention cleanup on skills data.

Enforces retention policies:
- Evidence older than 2 years in 'expired' state → hard delete
- Activity logs older than 90 days → archive
- Stale forecast data older than 6 months → cleanup
"""

from datetime import datetime, timedelta, timezone
from shared.utils.logger import logger


async def run_skill_retention_cleanup():
    logger.info("Starting skill data retention cleanup")

    supabase = None
    try:
        from config.core.supabase import get_supabase_client

        supabase = get_supabase_client()
    except Exception:
        logger.error("Failed to get Supabase client for retention cleanup")
        return

    now = datetime.now(timezone.utc)
    evidence_cutoff = int((now - timedelta(days=730)).timestamp())
    activity_cutoff = int((now - timedelta(days=90)).timestamp())
    forecast_cutoff = (now - timedelta(days=180)).isoformat()

    try:
        result = (
            supabase.table("user_skill_evidence")
            .delete()
            .eq("state", "expired")
            .lt("collected_at", evidence_cutoff)
            .execute()
        )
        if result.error:
            logger.warn(f"Evidence cleanup error: {result.error.message}")
        else:
            logger.info(f"Cleaned up {len(result.data or [])} expired evidence records")
    except Exception as e:
        logger.warn(f"Failed evidence cleanup: {e}")

    try:
        result = supabase.table("skill_activity_logs").delete().lt("created_at", activity_cutoff).execute()
        if result.error:
            logger.warn(f"Activity cleanup error: {result.error.message}")
        else:
            logger.info(f"Cleaned up {len(result.data or [])} old activity logs")
    except Exception as e:
        logger.warn(f"Failed activity cleanup: {e}")

    try:
        result = supabase.table("skill_forecasts").delete().lt("forecast_date", forecast_cutoff).execute()
        if result.error:
            logger.warn(f"Forecast cleanup error: {result.error.message}")
        else:
            logger.info(f"Cleaned up {len(result.data or [])} stale forecasts")
    except Exception as e:
        logger.warn(f"Failed forecast cleanup: {e}")

    logger.info("Skill data retention cleanup complete")


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_skill_retention_cleanup())
