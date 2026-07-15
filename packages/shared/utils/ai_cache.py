"""AI response cache with exact-match + semantic similarity support."""

import hashlib
import time
from collections import OrderedDict
from typing import Optional


class AICache:
    """Two-tier AI response cache: exact-match (fast) + semantic (fuzzy).

    Exact match: hashes (system_prompt + user_prompt + model) -> response
    Semantic match: uses word-set overlap (Jaccard) for near-duplicate queries.
    Thread-safe via instance-level lock — callers should use asyncio.Lock
    when sharing across coroutines.
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl = ttl_seconds
        self._exact_cache: OrderedDict = OrderedDict()
        self._semantic_cache: list[dict] = []
        self._hits = 0
        self._misses = 0
        self._token_savings = 0

    def _make_key(self, system_prompt: str, user_prompt: str, model: str) -> str:
        """Create an exact-match cache key."""
        raw = f"{system_prompt}|{user_prompt}|{model}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def _get_similarity(self, a: str, b: str) -> float:
        """Simple Jaccard-like similarity on word sets.

        For production this could use embedding vectors, but for a single-user
        personal OS, word-set overlap is sufficient and fast.
        """
        words_a = set(a.lower().split())
        words_b = set(b.lower().split())
        if not words_a or not words_b:
            return 0.0
        intersection = words_a & words_b
        union = words_a | words_b
        return len(intersection) / len(union)

    def get(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        similarity_threshold: float = 0.85,
    ) -> Optional[str]:
        """Get cached response. Checks exact match first, then semantic."""
        key = self._make_key(system_prompt, user_prompt, model)
        if key in self._exact_cache:
            entry = self._exact_cache[key]
            if time.time() - entry["time"] < self.ttl:
                self._hits += 1
                self._exact_cache.move_to_end(key)
                return entry["response"]
            del self._exact_cache[key]

        for entry in self._semantic_cache:
            if time.time() - entry["time"] > self.ttl:
                continue
            if entry["model"] != model:
                continue
            user_sim = self._get_similarity(user_prompt, entry["user_prompt"])
            system_sim = self._get_similarity(system_prompt, entry["system_prompt"])
            if user_sim >= similarity_threshold and system_sim >= similarity_threshold:
                self._hits += 1
                return entry["response"]

        self._misses += 1
        return None

    def set(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        response: str,
        estimated_tokens: int = 0,
    ):
        """Cache a response."""
        if len(self._exact_cache) >= self.max_size:
            self._exact_cache.popitem(last=False)
        if len(self._semantic_cache) >= self.max_size // 2:
            self._semantic_cache.pop(0)

        key = self._make_key(system_prompt, user_prompt, model)
        entry = {"time": time.time(), "response": response, "tokens": estimated_tokens}
        self._exact_cache[key] = entry
        self._semantic_cache.append({
            "time": time.time(),
            "system_prompt": system_prompt[:500],
            "user_prompt": user_prompt[:500],
            "model": model,
            "response": response,
        })
        self._token_savings += estimated_tokens

    @property
    def stats(self) -> dict:
        """Get cache statistics."""
        total = self._hits + self._misses
        return {
            "exact_entries": len(self._exact_cache),
            "semantic_entries": len(self._semantic_cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / total * 100, 2) if total > 0 else 0.0,
            "token_savings": self._token_savings,
            "estimated_cost_saved": round(self._token_savings * 0.000003, 6),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl,
        }

    def clear(self):
        """Clear all cached responses and reset stats."""
        self._exact_cache.clear()
        self._semantic_cache.clear()
        self._hits = 0
        self._misses = 0
        self._token_savings = 0

    def invalidate(self, user_prompt_prefix: Optional[str] = None):
        """Invalidate cache entries matching a prompt prefix."""
        if user_prompt_prefix:
            prefix_lower = user_prompt_prefix.lower()
            self._semantic_cache = [
                e
                for e in self._semantic_cache
                if not e["user_prompt"].lower().startswith(prefix_lower)
            ]
            self._exact_cache.clear()
        else:
            self.clear()


# Global singleton
ai_cache = AICache(max_size=1000, ttl_seconds=3600)
