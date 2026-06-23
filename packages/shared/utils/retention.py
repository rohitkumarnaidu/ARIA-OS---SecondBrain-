from datetime import datetime, timedelta, timezone
from shared.utils.logger import logger
from config.core.supabase import get_supabase_client


async def cleanup_old_audit_logs(retention_days: int = 90) -> int:
    supabase = get_supabase_client()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=retention_days)).isoformat()
    result = supabase.from_("audit_logs").delete().lt("created_at", cutoff).execute()
    count = len(result.data) if result.data else 0
    if count:
        logger.info("Cleaned up old audit logs", count=count, older_than_days=retention_days)
    return count


async def cleanup_old_chat_messages(retention_days: int = 90) -> int:
    supabase = get_supabase_client()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=retention_days)).isoformat()
    result = supabase.from_("chat_messages").delete().lt("created_at", cutoff).execute()
    count = len(result.data) if result.data else 0
    if count:
        logger.info("Cleaned up old chat messages", count=count, older_than_days=retention_days)
    return count


async def cleanup_old_notifications(retention_days: int = 30) -> int:
    supabase = get_supabase_client()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=retention_days)).isoformat()
    result = supabase.from_("notifications").delete().lt("created_at", cutoff).execute()
    count = len(result.data) if result.data else 0
    if count:
        logger.info("Cleaned up old notifications", count=count, older_than_days=retention_days)
    return count


async def run_data_retention_cleanup(
    audit_days: int = 90,
    chat_days: int = 90,
    notification_days: int = 30,
) -> dict:
    return {
        "audit_logs_removed": await cleanup_old_audit_logs(audit_days),
        "chat_messages_removed": await cleanup_old_chat_messages(chat_days),
        "notifications_removed": await cleanup_old_notifications(notification_days),
    }
