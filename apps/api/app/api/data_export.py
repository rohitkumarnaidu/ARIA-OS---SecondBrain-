from fastapi import APIRouter, Depends
from config.core.supabase import get_supabase_client
from config.core.auth import get_current_user
from shared.utils.logger import logger
from database.schemas.data_export import ExportResponse

router = APIRouter()

EXPORTABLE_TABLES = [
    "tasks", "courses", "goals", "habits", "habit_logs",
    "sleep_logs", "income_entries", "projects", "ideas",
    "resources", "opportunities", "time_entries", "chat_messages",
    "daily_briefings", "weekly_reviews", "memory", "learning_progress",
    "feedback", "notifications",
]


@router.get("/export", response_model=ExportResponse, summary="Export all user data (GDPR)")
async def export_user_data(current_user=Depends(get_current_user)):
    supabase = get_supabase_client()
    user_id = current_user.user.id
    from datetime import datetime, timezone

    result_data = {}
    total_records = 0

    for table in EXPORTABLE_TABLES:
        try:
            resp = supabase.from_(table).select("*").eq("user_id", user_id).execute()
            rows = resp.data or []
            if rows:
                result_data[table] = rows
                total_records += len(rows)
        except Exception as e:
            logger.warn("Data export skipped table", table=table, error=str(e))

    return ExportResponse(
        user_id=user_id,
        exported_at=datetime.now(timezone.utc).isoformat(),
        data=result_data,
        table_count=len(result_data),
        record_count=total_records,
    )
