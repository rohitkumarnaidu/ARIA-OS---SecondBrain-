"""Cron job to refresh materialized views for skills analytics.

Runs daily to refresh summary/aggregation materialized views
that power the skills dashboard, market intelligence, and career readiness.
"""

from shared.utils.logger import logger


async def run_skill_mv_refresh():
    logger.info("Starting skill materialized view refresh")

    supabase = None
    try:
        from config.core.supabase import get_supabase_client
        supabase = get_supabase_client()
    except Exception:
        logger.error("Failed to get Supabase client for MV refresh")
        return

    views = [
        "mv_skill_health_summary",
        "mv_skill_market_trends",
        "mv_user_skill_progress",
        "mv_skill_career_readiness",
    ]

    for view in views:
        try:
            result = supabase.rpc("refresh_materialized_view", {"view_name": view}).execute()
            if result.error:
                logger.warn(f"Failed to refresh {view}: {result.error.message}")
            else:
                logger.info(f"Refreshed materialized view: {view}")
        except Exception as e:
            logger.warn(f"Failed to refresh {view}: {e}")

    logger.info("Skill materialized view refresh complete")
