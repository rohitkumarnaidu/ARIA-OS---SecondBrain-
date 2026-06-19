from supabase import create_client
from config.core.config import settings

_supabase_client = None


def get_supabase_client():
    global _supabase_client
    if _supabase_client is None:
        if not settings.supabase_url or not settings.supabase_key:
            raise ValueError("Supabase URL and key must be configured")
        _supabase_client = create_client(settings.supabase_url, settings.supabase_key)
    return _supabase_client
