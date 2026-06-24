from datetime import datetime
from config.core.supabase import get_supabase_client
from shared.utils.logger import logger


async def run_skill_evidence_expiry():
    supabase = get_supabase_client()
    now_ms = int(datetime.now().timestamp() * 1000)

    expired_resp = supabase.from_("user_skill_evidence").select("evidence_id").lt("expires_at", now_ms).neq("state", "expired").execute()
    expired = expired_resp.data or []

    if expired:
        ids = [e["evidence_id"] for e in expired]
        result = supabase.from_("user_skill_evidence").update({"state": "expired"}).in_("evidence_id", ids).execute()
        logger.info("Evidence expiry check completed", expired_count=len(ids), updated=len(result.data or []))
    else:
        logger.info("Evidence expiry check completed", expired_count=0)


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_skill_evidence_expiry())
