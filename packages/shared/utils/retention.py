"""Data retention cleanup.

`user_id` scoping was added because `POST /api/v1/automation/trigger/cleanup`
called this with no scope at all: any authenticated user could delete every
other user's `chat_messages`, `notifications` and `audit_logs` rows older than
the cutoff. Every route now passes the caller's id.

`user_id=None` still means global, and is the pre-existing behaviour. It is
kept because the scheduler legitimately needs a global sweep, and because
`run_data_retention_cleanup`'s existing callers pass no scope. The
user-facing route does not use it.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from config.core.supabase import get_supabase_client
from shared.utils.logger import logger


def _scoped(query, user_id: Optional[str]):
    """Add the tenant filter when a user id is supplied.

    Returns the query unchanged when `user_id` is None so the global path stays
    byte-identical to the previous behaviour.
    """
    if user_id:
        return query.eq("user_id", user_id)
    return query


async def cleanup_old_audit_logs(retention_days: int = 90, user_id: Optional[str] = None) -> int:
    supabase = get_supabase_client()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=retention_days)).isoformat()
    query = supabase.from_("audit_logs").delete().lt("created_at", cutoff)
    result = _scoped(query, user_id).execute()
    count = len(result.data) if result.data else 0
    if count:
        logger.info("Cleaned up old audit logs", count=count, older_than_days=retention_days, user_id=user_id)
    return count


async def cleanup_old_chat_messages(retention_days: int = 90, user_id: Optional[str] = None) -> int:
    supabase = get_supabase_client()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=retention_days)).isoformat()
    query = supabase.from_("chat_messages").delete().lt("created_at", cutoff)
    result = _scoped(query, user_id).execute()
    count = len(result.data) if result.data else 0
    if count:
        logger.info("Cleaned up old chat messages", count=count, older_than_days=retention_days, user_id=user_id)
    return count


async def cleanup_old_notifications(retention_days: int = 30, user_id: Optional[str] = None) -> int:
    supabase = get_supabase_client()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=retention_days)).isoformat()
    query = supabase.from_("notifications").delete().lt("created_at", cutoff)
    result = _scoped(query, user_id).execute()
    count = len(result.data) if result.data else 0
    if count:
        logger.info("Cleaned up old notifications", count=count, older_than_days=retention_days, user_id=user_id)
    return count


async def run_data_retention_cleanup(
    audit_days: int = 90,
    chat_days: int = 90,
    notification_days: int = 30,
    user_id: Optional[str] = None,
) -> dict:
    # The scope is only forwarded when there is one, so the global path calls
    # each helper with exactly the argument list it always used.
    if user_id:
        return {
            "audit_logs_removed": await cleanup_old_audit_logs(audit_days, user_id=user_id),
            "chat_messages_removed": await cleanup_old_chat_messages(chat_days, user_id=user_id),
            "notifications_removed": await cleanup_old_notifications(notification_days, user_id=user_id),
        }
    return {
        "audit_logs_removed": await cleanup_old_audit_logs(audit_days),
        "chat_messages_removed": await cleanup_old_chat_messages(chat_days),
        "notifications_removed": await cleanup_old_notifications(notification_days),
    }
