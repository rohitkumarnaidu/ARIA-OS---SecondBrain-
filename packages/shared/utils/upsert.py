from typing import Any, Dict, List
from config.core.supabase import get_supabase_client
from shared.utils.logger import logger


def upsert(table: str, data: Dict[str, Any], conflict_columns: List[str]) -> Dict[str, Any]:
    supabase = get_supabase_client()
    try:
        where = {}
        for col in conflict_columns:
            if col in data:
                where[col] = data[col]
        if where:
            existing = supabase.from_(table).select("*").match(where).execute()
            if existing.data:
                supabase.from_(table).update(data).match(where).execute()
                logger.debug("Upsert updated existing row", table=table, match=where)
                return existing.data[0]
        result = supabase.from_(table).insert(data).execute()
        if result.data:
            logger.debug("Upsert inserted new row", table=table, id=result.data[0].get("id"))
            return result.data[0]
        return {}
    except Exception as e:
        logger.error("Upsert failed", table=table, error=str(e))
        raise
