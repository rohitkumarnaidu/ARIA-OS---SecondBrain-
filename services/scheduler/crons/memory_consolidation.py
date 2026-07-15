from config.core.supabase import get_supabase_client
from ai.agents.memory_agent import run_weekly_deep_consolidation
from shared.utils.logger import logger


async def run_memory_consolidation():
    supabase = get_supabase_client()
    users_resp = supabase.from_("users").select("id").execute()

    for user in users_resp.data or []:
        try:
            result = await run_weekly_deep_consolidation(user["id"])
            logger.info(
                "Memory consolidation completed",
                user_id=user["id"],
                status=result.get("status"),
                deduplicated=result.get("deduplicated"),
                decayed=result.get("confidence_decayed"),
            )
        except Exception as e:
            logger.error("Error in memory consolidation", user_id=user["id"], error=str(e))


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_memory_consolidation())
