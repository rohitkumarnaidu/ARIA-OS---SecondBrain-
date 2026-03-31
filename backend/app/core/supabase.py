import supabase
from app.core.config import settings

_supabase_client = None


def get_supabase_client():
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = supabase.create_client(
            settings.supabase_url, settings.supabase_key
        )
    return _supabase_client
