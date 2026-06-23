from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import hashlib
import json
import os
import threading
from shared.utils.logger import logger
from config.core.supabase import get_supabase_client


class FeatureFlag:
    def __init__(
        self,
        key: str,
        enabled: bool = False,
        rollout_percentage: int = 0,
        user_segments: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.key = key
        self.enabled = enabled
        self.rollout_percentage = min(100, max(0, rollout_percentage))
        self.user_segments = user_segments or []
        self.metadata = metadata or {}
        self.updated_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "enabled": self.enabled,
            "rollout_percentage": self.rollout_percentage,
            "user_segments": self.user_segments,
            "metadata": self.metadata,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeatureFlag":
        return cls(
            key=data.get("key", ""),
            enabled=data.get("enabled", False),
            rollout_percentage=data.get("rollout_percentage", 0),
            user_segments=data.get("user_segments", []),
            metadata=data.get("metadata", {}),
        )


class FeatureFlagStore:
    def __init__(self, refresh_interval_seconds: int = 60):
        self._flags: Dict[str, FeatureFlag] = {}
        self._refresh_interval = refresh_interval_seconds
        self._last_refresh: float = 0
        self._lock = threading.Lock()
        self._load_from_env()

    def _load_from_env(self) -> None:
        for key, value in os.environ.items():
            if key.startswith("FF_"):
                flag_key = key[3:].lower().replace("_", ".")
                enabled = value.lower() in ("true", "1", "yes")
                self._flags[flag_key] = FeatureFlag(flag_key, enabled=enabled, rollout_percentage=100 if enabled else 0)

    def _user_bucket(self, user_id: str, key: str) -> int:
        hash_input = f"{user_id}:{key}"
        hash_val = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16)
        return hash_val % 100

    def get(self, key: str, user_id: Optional[str] = None, default: bool = False) -> bool:
        flag = self._flags.get(key)
        if flag is None:
            return default
        if not flag.enabled:
            return False
        if flag.rollout_percentage >= 100:
            return True
        if user_id:
            if flag.user_segments and user_id in flag.user_segments:
                return True
            bucket = self._user_bucket(user_id, key)
            return bucket < flag.rollout_percentage
        return flag.rollout_percentage > 0

    def get_variant(self, key: str, user_id: str, default: str = "control") -> str:
        flag = self._flags.get(key)
        if not flag or not flag.enabled:
            return default
        if flag.rollout_percentage >= 100:
            return "treatment"
        if flag.user_segments and user_id in flag.user_segments:
            return "treatment"
        bucket = self._user_bucket(user_id, key)
        if bucket < flag.rollout_percentage:
            return "treatment"
        return "control"

    def set(self, key: str, flag: FeatureFlag) -> None:
        with self._lock:
            self._flags[key] = flag

    def delete(self, key: str) -> bool:
        with self._lock:
            return self._flags.pop(key, None) is not None

    def all_flags(self) -> Dict[str, FeatureFlag]:
        with self._lock:
            return dict(self._flags)

    async def refresh(self) -> None:
        now = datetime.utcnow().timestamp()
        if now - self._last_refresh < self._refresh_interval:
            return
        try:
            supabase = get_supabase_client()
            response = (
                supabase.from_("feature_flags")
                .select("key, enabled, rollout_percentage, user_segments, metadata")
                .execute()
            )
            if response.data:
                with self._lock:
                    for item in response.data:
                        self._flags[item["key"]] = FeatureFlag.from_dict(item)
                logger.info("Feature flags refreshed", count=len(response.data))
            self._last_refresh = now
        except Exception as e:
            logger.warn("Failed to refresh feature flags", error=str(e))


flags = FeatureFlagStore()
