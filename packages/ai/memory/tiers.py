"""Memory tier implementations (tiers 0-4) for the Second Brain memory system.

PERFORMANCE WARNING — blocking I/O inside ``async def``
--------------------------------------------------------
Every coroutine in this module is declared ``async`` but drives the
SYNCHRONOUS ``postgrest-py`` client, whose ``.execute()`` is a blocking HTTP
round trip. There is no awaitable PostgREST/Supabase client in this project's
dependency set, so these calls cannot simply be awaited. Invoked directly from
a FastAPI route they block the event loop: one slow query stalls every other
concurrent request served by the same worker for the duration of the round
trip.

Migration path — do NOT do this piecemeal, it changes error semantics:
wrap each Supabase interaction in ``await asyncio.to_thread(...)`` (or
``loop.run_in_executor``), or migrate to an async PostgREST client. Until
then, treat this as a latency/scalability issue rather than a correctness one:
the results are correct, they just occupy the loop while in flight. The write
sites below are additionally bounded (``_DECAY_MAX_ROWS``) so no single
request can fan out into an unbounded number of round trips.
"""

import hashlib
import json
import re
import uuid
from collections import OrderedDict
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List, Tuple

from config.core.supabase import get_supabase_client
from shared.utils.logger import logger

# Upper bound on rows any single batched write fan-out will touch. Bounds the
# worst-case round-trip count of decay_all() to (_DECAY_MAX_ROWS / _WRITE_CHUNK).
_DECAY_MAX_ROWS = 500
_WRITE_CHUNK = 50
# Confidence never decays below this floor.
_CONFIDENCE_FLOOR = 0.05
# Cap on the number of source summaries folded onto a single episodic survivor.
# Bounded so the survivor's JSONB payload cannot grow without limit while no
# summary is ever discarded — overflow simply starts a new survivor.
_EPISODIC_MERGE_BATCH = 25

_EPISODIC_TAG_STOPWORDS = frozenset(
    {
        "about",
        "after",
        "again",
        "also",
        "been",
        "before",
        "being",
        "between",
        "both",
        "does",
        "doing",
        "done",
        "each",
        "from",
        "have",
        "having",
        "here",
        "into",
        "just",
        "like",
        "make",
        "more",
        "most",
        "much",
        "must",
        "need",
        "only",
        "other",
        "over",
        "same",
        "should",
        "some",
        "such",
        "than",
        "that",
        "them",
        "then",
        "there",
        "these",
        "they",
        "this",
        "those",
        "through",
        "under",
        "very",
        "want",
        "were",
        "what",
        "when",
        "where",
        "which",
        "while",
        "will",
        "with",
        "would",
        "your",
        "yours",
    }
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _utc_dt() -> datetime:
    return datetime.now(timezone.utc)


def _estimate_tokens(text: str) -> int:
    return len(text.split())


def _make_key(*parts: str) -> str:
    raw = ":".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()[:24]


def _make_working_key(user_id: str, key: str) -> str:
    """Storage key for a working-memory entry.

    ``user_id`` is part of the digest so two tenants can never collide on the
    ``working_memory`` PRIMARY KEY, and so the row a user reads back is always
    the row they wrote.
    """
    return _make_key("wm", user_id, key)


def _decode_value(row: Dict[str, Any]) -> Dict[str, Any]:
    """Decode a memory row's ``value`` column, tolerating both writer shapes."""
    raw = row.get("value", "{}")
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return raw if isinstance(raw, dict) else {}


def _derive_episodic_tags(text: str, limit: int = 4) -> List[str]:
    """Derive stable topical tags from episode content.

    ``store_episode`` used to force ``tags = ["episodic"]`` on every row, so
    ``consolidate()``'s tag-tuple grouping collapsed the whole episodic tier
    into one group and deleted all but a single row. Tags are now derived from
    the episode text (caller-supplied tags still win) so genuinely related
    episodes group together and unrelated ones do not.
    """
    if not text:
        return []
    counts: Dict[str, int] = {}
    first_seen: List[str] = []
    for word in re.findall(r"[a-z0-9']+", text.lower()):
        if len(word) < 4 or len(word) > 24 or word in _EPISODIC_TAG_STOPWORDS:
            continue
        if word not in counts:
            first_seen.append(word)
        counts[word] = counts.get(word, 0) + 1
    # Stable sort: ties keep first-occurrence order, so tags are deterministic.
    ranked = sorted(first_seen, key=lambda w: -counts[w])
    return ranked[:limit]


class BufferMemory:
    """Tier 0: Session-level ephemeral ring buffer of recent conversation turns."""

    def __init__(self, capacity: int = 20, token_budget: int = 2000):
        self.capacity = capacity
        self.token_budget = token_budget
        self._messages: List[Dict[str, Any]] = []

    def add(self, user_msg: str, ai_msg: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        now = _utc_now()
        self._messages.append(
            {
                "role": "user",
                "content": user_msg,
                "metadata": metadata or {},
                "timestamp": now,
            }
        )
        self._messages.append(
            {
                "role": "assistant",
                "content": ai_msg,
                "metadata": metadata or {},
                "timestamp": now,
            }
        )
        while len(self._messages) > self.capacity * 2:
            removed = self._messages.pop(0)
            logger.debug(
                "Buffer evicted oldest message", role=removed.get("role"), preview=removed.get("content", "")[:50]
            )

    def get_context(self, k: int = 10) -> List[Dict[str, Any]]:
        if k <= 0:
            return []
        return list(self._messages[-k * 2 :])

    def get_token_count(self) -> int:
        total = 0
        for m in self._messages:
            total += _estimate_tokens(m.get("content", ""))
        return total

    def trim_to_budget(self, budget: Optional[int] = None) -> List[Dict[str, Any]]:
        budget = budget or self.token_budget
        trimmed: List[Dict[str, Any]] = []
        total = 0
        for m in reversed(self._messages):
            tokens = _estimate_tokens(m.get("content", ""))
            if total + tokens > budget:
                break
            trimmed.insert(0, m)
            total += tokens
        return trimmed

    def clear(self) -> None:
        self._messages.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capacity": self.capacity,
            "token_budget": self.token_budget,
            "messages": list(self._messages),
            "message_count": len(self._messages),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BufferMemory":
        instance = cls(capacity=data.get("capacity", 20), token_budget=data.get("token_budget", 2000))
        instance._messages = list(data.get("messages", []))
        return instance

    def __len__(self) -> int:
        return len(self._messages)

    def __repr__(self) -> str:
        return f"BufferMemory(capacity={self.capacity}, messages={len(self._messages)})"


class WorkingMemory:
    """Tier 1: Day-level key-value store with TTL, backed by Supabase.

    Every method is tenant-scoped. ``user_id`` is mandatory: it is bound at
    construction *and* threaded into the storage key digest and the query
    filter, so no two users can read, overwrite, or expire each other's
    entries. An explicit per-call ``user_id`` that disagrees with the bound
    owner is rejected rather than silently honoured — a mismatch is precisely
    the cross-tenant access this class must never perform.
    """

    def __init__(self, user_id: str, default_ttl: int = 43200):
        if not user_id or not isinstance(user_id, str):
            raise ValueError("WorkingMemory requires a non-empty user_id")
        self.user_id = user_id
        self.default_ttl = default_ttl
        self._local: Dict[str, Tuple[Any, float]] = OrderedDict()
        self._dirty_keys: set = set()

    def _resolve_owner(self, user_id: Optional[str]) -> str:
        owner = user_id if user_id is not None else self.user_id
        if not owner or not isinstance(owner, str):
            raise ValueError("WorkingMemory requires a non-empty user_id")
        if owner != self.user_id:
            raise ValueError("WorkingMemory user_id does not match the bound owner")
        return owner

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        user_id: Optional[str] = None,
    ) -> None:
        owner = self._resolve_owner(user_id)
        ttl = ttl or self.default_ttl
        expires_at = _utc_dt() + timedelta(seconds=ttl)
        self._local[key] = (value, expires_at.timestamp())
        self._dirty_keys.add(key)
        try:
            supabase = get_supabase_client()
            supabase.from_("working_memory").upsert(
                {
                    "key": _make_working_key(owner, key),
                    "user_id": owner,
                    "type": "working",
                    "value": json.dumps({"key": key, "value": value}),
                    "expires_at": expires_at.isoformat(),
                }
            ).execute()
        except Exception as e:
            logger.warn("WorkingMemory.set supabase failed", key=key, user_id=owner, error=str(e))

    def get(self, key: str, user_id: Optional[str] = None) -> Optional[Any]:
        owner = self._resolve_owner(user_id)
        if key in self._local:
            value, expires = self._local[key]
            if datetime.fromtimestamp(expires, tz=timezone.utc) > _utc_dt():
                return value
            del self._local[key]
        try:
            supabase = get_supabase_client()
            result = (
                supabase.from_("working_memory")
                .select("value")
                .eq("user_id", owner)
                .eq("key", _make_working_key(owner, key))
                .execute()
            )
            if result.data:
                parsed = json.loads(result.data[0]["value"])
                self._local[key] = (parsed["value"], _utc_dt().timestamp() + self.default_ttl)
                return parsed["value"]
        except Exception as e:
            logger.warn("WorkingMemory.get supabase failed", key=key, user_id=owner, error=str(e))
        return None

    def get_all(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        self._resolve_owner(user_id)
        result: Dict[str, Any] = {}
        now = _utc_dt()
        expired_keys = []
        for key, (value, expires) in self._local.items():
            if datetime.fromtimestamp(expires, tz=timezone.utc) > now:
                result[key] = value
            else:
                expired_keys.append(key)
        for k in expired_keys:
            del self._local[k]
        return result

    def clear_expired(self, user_id: Optional[str] = None) -> int:
        owner = self._resolve_owner(user_id)
        now = _utc_dt()
        expired = [k for k, (_, e) in self._local.items() if datetime.fromtimestamp(e, tz=timezone.utc) <= now]
        for k in expired:
            del self._local[k]
        try:
            supabase = get_supabase_client()
            supabase.from_("working_memory").delete().eq("user_id", owner).lt("expires_at", _utc_now()).execute()
        except Exception as e:
            logger.warn("WorkingMemory.clear_expired supabase failed", user_id=owner, error=str(e))
        return len(expired)

    def snapshot(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        self._resolve_owner(user_id)
        result: Dict[str, Any] = {}
        now = _utc_dt()
        for key, (value, expires) in self._local.items():
            if datetime.fromtimestamp(expires, tz=timezone.utc) > now:
                result[key] = value
        return result

    def clear(self, user_id: Optional[str] = None) -> None:
        self._resolve_owner(user_id)
        self._local.clear()
        self._dirty_keys.clear()

    def to_dict(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "default_ttl": self.default_ttl,
            "entries": self.snapshot(user_id),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], user_id: Optional[str] = None) -> "WorkingMemory":
        owner = user_id or data.get("user_id")
        if not owner:
            raise ValueError("WorkingMemory.from_dict requires a user_id")
        instance = cls(user_id=owner, default_ttl=data.get("default_ttl", 43200))
        for key, value in data.get("entries", {}).items():
            instance.set(key, value)
        return instance

    def __repr__(self) -> str:
        return f"WorkingMemory(entries={len(self._local)}, dirty={len(self._dirty_keys)})"


class EpisodicMemory:
    """Tier 2: User journey episodes stored in Supabase memory table with type='episodic'."""

    def __init__(self):
        self._table = "memory"

    @staticmethod
    def _resolve_tags(
        tags: Optional[List[str]],
        summary: str,
        session_data: Dict[str, Any],
    ) -> List[str]:
        """Build the tag set for an episode.

        The ``"episodic"`` tier marker is always present so ``consolidate()``
        can exclude it from the grouping key. Caller-supplied topical tags win;
        otherwise tags are derived from the episode content. Falling back to the
        bare marker alone (the previous behaviour) is what made every episode
        land in one consolidation group.
        """
        resolved: List[str] = ["episodic"]
        for tag in tags or []:
            normalised = str(tag).strip().lower()
            if normalised and normalised not in resolved:
                resolved.append(normalised)
        if len(resolved) == 1:
            try:
                content = json.dumps(session_data, default=str)
            except (TypeError, ValueError):
                content = str(session_data)
            for derived in _derive_episodic_tags(f"{summary or ''} {content}"):
                if derived not in resolved:
                    resolved.append(derived)
        return resolved

    async def store_episode(
        self,
        user_id: str,
        session_data: Dict[str, Any],
        summary: str,
        tags: Optional[List[str]] = None,
    ) -> Optional[str]:
        try:
            supabase = get_supabase_client()
            key = f"episode:{uuid.uuid4().hex[:12]}"
            data = {
                "user_id": user_id,
                "type": "episodic",
                "key": key,
                "value": json.dumps({"session_data": session_data, "summary": summary}),
                "importance": "medium",
                "tags": self._resolve_tags(tags, summary, session_data),
            }
            result = supabase.from_(self._table).insert(data).execute()
            if result.data:
                episode_id = result.data[0]["id"]
                logger.info("Episode stored", user_id=user_id, episode_id=episode_id)
                return episode_id
            return None
        except Exception as e:
            logger.error("store_episode failed", user_id=user_id, error=str(e))
            return None

    async def search_episodes(
        self,
        user_id: str,
        query: str,
        k: int = 5,
    ) -> List[Dict[str, Any]]:
        try:
            supabase = get_supabase_client()
            keywords = [w.lower() for w in query.split() if len(w) > 2]
            result = (
                supabase.from_(self._table)
                .select("*")
                .eq("user_id", user_id)
                .eq("type", "episodic")
                .order("created_at", desc=True)
                .limit(50)
                .execute()
            )
            episodes = result.data or []
            if not keywords:
                return episodes[:k]

            scored: List[Tuple[float, Dict[str, Any]]] = []
            for ep in episodes:
                score = 0.0
                value_str = json.dumps(ep.get("value", {})).lower()
                tags = [t.lower() for t in ep.get("tags", [])]
                for kw in keywords:
                    if kw in value_str:
                        score += 1.0
                    if kw in str(ep.get("key", "")).lower():
                        score += 1.5
                    if kw in tags:
                        score += 2.0
                if score > 0:
                    scored.append((score, ep))

            scored.sort(key=lambda x: x[0], reverse=True)
            return [ep for _, ep in scored[:k]]
        except Exception as e:
            logger.error("search_episodes failed", user_id=user_id, error=str(e))
            return []

    async def get_recent(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        try:
            supabase = get_supabase_client()
            since = (_utc_dt() - timedelta(days=days)).isoformat()
            result = (
                supabase.from_(self._table)
                .select("*")
                .eq("user_id", user_id)
                .eq("type", "episodic")
                .gte("created_at", since)
                .order("created_at", desc=True)
                .limit(50)
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.error("get_recent episodes failed", user_id=user_id, error=str(e))
            return []

    async def consolidate(self, user_id: str) -> Dict[str, Any]:
        try:
            episodes = await self.get_recent(user_id, days=7)
            if len(episodes) < 2:
                return {"merged": 0, "summary": "Not enough episodes to consolidate"}

            groups = self._group_episodes(episodes)

            merged_count = 0
            for group in groups.values():
                if len(group) < 2:
                    continue
                for start in range(0, len(group), _EPISODIC_MERGE_BATCH):
                    batch = group[start : start + _EPISODIC_MERGE_BATCH]
                    if len(batch) < 2:
                        continue
                    merged_count += self._merge_episode_batch(user_id, batch)

            return {"merged": merged_count, "groups_found": len(groups)}
        except Exception as e:
            logger.error("consolidate episodes failed", user_id=user_id, error=str(e))
            return {"merged": 0, "groups_found": 0}

    @staticmethod
    def _group_episodes(episodes: List[Dict[str, Any]]) -> Dict[Tuple[str, ...], List[Dict[str, Any]]]:
        """Bucket episodes by their topical tag set (the tier marker excluded).

        An episode with no topical tag gets a key derived from its own id, so
        it can never be grouped with another untagged episode. That guarantee is
        what stops an all-``["episodic"]`` tier from collapsing into one group.
        """
        groups: Dict[Tuple[str, ...], List[Dict[str, Any]]] = {}
        for ep in episodes:
            raw_tags = ep.get("tags") or []
            if isinstance(raw_tags, str):
                try:
                    raw_tags = json.loads(raw_tags)
                except (json.JSONDecodeError, TypeError):
                    raw_tags = []
            if not isinstance(raw_tags, list):
                raw_tags = []
            topical = sorted(
                {str(t).strip().lower() for t in raw_tags if str(t).strip() and str(t).strip().lower() != "episodic"}
            )
            group_key: Tuple[str, ...] = tuple(topical) if topical else (f"__ungrouped__:{ep.get('id')}",)
            groups.setdefault(group_key, []).append(ep)
        return groups

    def _merge_episode_batch(self, user_id: str, batch: List[Dict[str, Any]]) -> int:
        """Fold ``batch`` into ``batch[0]`` (the survivor) without losing content.

        Crash-safe ordering: the survivor is written FIRST carrying every source
        summary, then re-read to prove the content actually landed, and only
        then are the source rows deleted. A crash at any point leaves each
        summary either on the survivor or still on its original row — never
        neither. An unverifiable write aborts the merge for that batch.
        """
        keep = batch[0]
        sources = batch[1:]
        summaries = [str(_decode_value(ep).get("summary", "") or "") for ep in batch]

        merged_val = _decode_value(keep)
        merged_summaries: List[str] = list(merged_val.get("consolidated_summaries") or [])
        merged_ids: List[str] = list(merged_val.get("consolidated_source_ids") or [])
        for ep, summary in zip(batch, summaries):
            if summary and summary not in merged_summaries:
                merged_summaries.append(summary)
            ep_id = ep.get("id")
            if ep_id and ep_id not in merged_ids:
                merged_ids.append(ep_id)
        merged_val["consolidated_summaries"] = merged_summaries
        merged_val["consolidated_source_ids"] = merged_ids
        merged_val["consolidated_at"] = _utc_now()

        supabase = get_supabase_client()
        try:
            supabase.from_(self._table).update(
                {
                    "value": json.dumps(merged_val),
                }
            ).eq(
                "id", keep["id"]
            ).eq("user_id", user_id).execute()
        except Exception as inner_e:
            logger.warn(
                "Failed to write consolidated episode", user_id=user_id, episode_id=keep.get("id"), error=str(inner_e)
            )
            return 0

        if not self._summaries_present(user_id, keep["id"], [s for s in summaries if s]):
            logger.warn(
                "Episodic merge aborted — survivor does not carry the merged content",
                user_id=user_id,
                episode_id=keep.get("id"),
            )
            return 0

        deleted = 0
        for ep in sources:
            try:
                supabase.from_(self._table).delete().eq("id", ep["id"]).eq("user_id", user_id).execute()
                deleted += 1
            except Exception as inner_e:
                logger.warn(
                    "Failed to delete merged episode",
                    user_id=user_id,
                    episode_id=ep.get("id"),
                    error=str(inner_e),
                )
        return deleted

    def _summaries_present(self, user_id: str, survivor_id: str, summaries: List[str]) -> bool:
        """Verify every summary is readable on the survivor before deleting sources."""
        if not summaries:
            return False
        try:
            supabase = get_supabase_client()
            result = supabase.from_(self._table).select("value").eq("id", survivor_id).eq("user_id", user_id).execute()
            if not result.data:
                return False
            present = _decode_value(result.data[0]).get("consolidated_summaries") or []
            return all(s in present for s in summaries)
        except Exception as e:
            logger.warn("Failed to verify consolidated episode", user_id=user_id, episode_id=survivor_id, error=str(e))
            return False


class SemanticMemory:
    """Tier 3: Facts, preferences, patterns stored in Supabase memory table with type='semantic'."""

    def __init__(self):
        self._table = "memory"
        self._default_confidence = 0.8
        self._decay_rate = 0.01

    async def store_fact(
        self,
        user_id: str,
        fact: str,
        source: str = "inference",
        confidence: Optional[float] = None,
        category: str = "general",
        tags: Optional[List[str]] = None,
    ) -> Optional[str]:
        try:
            supabase = get_supabase_client()
            semantic_key = _make_key("sem", user_id, fact.lower().strip())
            confidence = confidence if confidence is not None else self._default_confidence
            value = {
                "fact": fact,
                "source": source,
                "confidence": confidence,
                "category": category,
                "last_accessed": _utc_now(),
            }
            existing = (
                supabase.from_(self._table)
                .select("id, value")
                .eq("user_id", user_id)
                .eq("type", "semantic")
                .eq("key", semantic_key)
                .execute()
            )
            if existing.data:
                try:
                    existing_val = (
                        json.loads(existing.data[0]["value"])
                        if isinstance(existing.data[0].get("value"), str)
                        else existing.data[0].get("value", {})
                    )
                except (json.JSONDecodeError, TypeError):
                    existing_val = {}
                existing_val.update(value)
                existing_val["confidence"] = max(existing_val.get("confidence", confidence), confidence)
                existing_val["reference_count"] = existing_val.get("reference_count", 1) + 1
                supabase.from_(self._table).update(
                    {
                        "value": json.dumps(existing_val),
                        "importance": self._confidence_to_importance(existing_val["confidence"]),
                    }
                ).eq("id", existing.data[0]["id"]).eq("user_id", user_id).execute()
                logger.info("Semantic fact updated", user_id=user_id, fact=fact[:80])
                return existing.data[0]["id"]
            else:
                data = {
                    "user_id": user_id,
                    "type": "semantic",
                    "key": semantic_key,
                    "value": json.dumps(value),
                    "importance": self._confidence_to_importance(confidence),
                    "tags": tags or [category, source],
                }
                result = supabase.from_(self._table).insert(data).execute()
                if result.data:
                    logger.info("Semantic fact stored", user_id=user_id, fact=fact[:80])
                    return result.data[0]["id"]
                return None
        except Exception as e:
            logger.error("store_fact failed", user_id=user_id, error=str(e))
            return None

    async def query(self, user_id: str, query: str, k: int = 10) -> List[Dict[str, Any]]:
        try:
            supabase = get_supabase_client()
            result = (
                supabase.from_(self._table)
                .select("*")
                .eq("user_id", user_id)
                .eq("type", "semantic")
                .order("importance", desc=True)
                .limit(50)
                .execute()
            )
            facts = result.data or []
            keywords = [w.lower() for w in query.split() if len(w) > 2]
            if not keywords:
                return facts[:k]

            scored: List[Tuple[float, Dict[str, Any]]] = []
            for fact in facts:
                score = 0.0
                try:
                    val = (
                        json.loads(fact.get("value", "{}"))
                        if isinstance(fact.get("value"), str)
                        else fact.get("value", {})
                    )
                except (json.JSONDecodeError, TypeError):
                    val = {}
                fact_text = json.dumps(val).lower()
                importance_map = {"low": 0.3, "medium": 0.6, "high": 0.8, "critical": 1.0}
                importance_bonus = importance_map.get(fact.get("importance", "medium"), 0.5) * 0.5
                tags = [t.lower() for t in fact.get("tags", [])]
                for kw in keywords:
                    if kw in fact_text:
                        score += 1.0
                    if kw in tags:
                        score += 1.5
                score += importance_bonus
                if score > 0:
                    scored.append((score, fact))

            scored.sort(key=lambda x: x[0], reverse=True)
            return [f for _, f in scored[:k]]
        except Exception as e:
            logger.error("semantic query failed", user_id=user_id, error=str(e))
            return []

    async def update_confidence(self, user_id: str, fact_id: str, delta: float) -> bool:
        try:
            supabase = get_supabase_client()
            result = (
                supabase.from_(self._table)
                .select("value")
                .eq("id", fact_id)
                .eq("user_id", user_id)
                .eq("type", "semantic")
                .execute()
            )
            if not result.data:
                return False
            try:
                val = (
                    json.loads(result.data[0]["value"])
                    if isinstance(result.data[0].get("value"), str)
                    else result.data[0].get("value", {})
                )
            except (json.JSONDecodeError, TypeError):
                val = {}
            new_confidence = max(0.0, min(1.0, val.get("confidence", 0.5) + delta))
            val["confidence"] = new_confidence
            supabase.from_(self._table).update(
                {
                    "value": json.dumps(val),
                    "importance": self._confidence_to_importance(new_confidence),
                }
            ).eq("id", fact_id).eq("user_id", user_id).execute()
            return True
        except Exception as e:
            logger.error("update_confidence failed", user_id=user_id, fact_id=fact_id, error=str(e))
            return False

    async def get_user_preferences(self, user_id: str) -> List[Dict[str, Any]]:
        try:
            supabase = get_supabase_client()
            result = (
                supabase.from_(self._table)
                .select("*")
                .eq("user_id", user_id)
                .eq("type", "semantic")
                .contains("tags", ["preference"])
                .order("importance", desc=True)
                .limit(30)
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.error("get_user_preferences failed", user_id=user_id, error=str(e))
            return []

    async def get_knowledge_graph(self, user_id: str) -> Dict[str, Any]:
        try:
            facts = await self.query(user_id, "", k=100)
            nodes: List[Dict[str, Any]] = []
            edges: List[Dict[str, str]] = []
            seen_categories: Dict[str, str] = {}
            for fact in facts:
                try:
                    val = (
                        json.loads(fact.get("value", "{}"))
                        if isinstance(fact.get("value"), str)
                        else fact.get("value", {})
                    )
                except (json.JSONDecodeError, TypeError):
                    val = {}
                category = val.get("category", "general")
                if category not in seen_categories:
                    cat_id = _make_key("kg_cat", category)
                    seen_categories[category] = cat_id
                    nodes.append({"id": cat_id, "label": category, "type": "category"})
                fact_id = fact.get("id", _make_key("kg_fact", str(fact.get("key", ""))))
                nodes.append(
                    {
                        "id": fact_id,
                        "label": val.get("fact", fact.get("key", ""))[:60],
                        "type": "fact",
                        "confidence": val.get("confidence", 0.5),
                        "category": category,
                    }
                )
                edges.append({"source": seen_categories[category], "target": fact_id, "label": "contains"})
            return {"nodes": nodes, "edges": edges}
        except Exception as e:
            logger.error("get_knowledge_graph failed", user_id=user_id, error=str(e))
            return {"nodes": [], "edges": []}

    async def decay_all(self, user_id: str, batch_size: int = _WRITE_CHUNK) -> int:
        """Decay every semantic fact's confidence by time since last access.

        This is the single confidence-decay implementation for the whole
        subsystem (``memory_agent.apply_confidence_decay`` delegates here).

        The select is bounded by ``_DECAY_MAX_ROWS`` and the writes are issued in
        ``batch_size`` chunks via a multi-row upsert on the table's
        ``UNIQUE (user_id, type, key)`` constraint, so one request issues a
        handful of round trips instead of one per row. If a chunk upsert fails
        the chunk's rows are retried individually with an id- and user-scoped
        update, so a partial failure never silently skips a row.
        """
        try:
            supabase = get_supabase_client()
            facts = (
                supabase.from_(self._table)
                .select("id, user_id, type, key, value, importance")
                .eq("user_id", user_id)
                .eq("type", "semantic")
                .order("created_at", ascending=True)
                .limit(_DECAY_MAX_ROWS)
                .execute()
            )
            updates: List[Dict[str, Any]] = []
            for fact in facts.data or []:
                row_id = fact.get("id")
                row_key = fact.get("key")
                if not row_id or not row_key:
                    # Without both the id and the unique key the chunk cannot be
                    # targeted safely; leave the row untouched this pass.
                    continue
                val = _decode_value(fact)
                old_conf = val.get("confidence", 0.5)
                days_since = 1
                try:
                    accessed = val.get("last_accessed", _utc_now())
                    accessed_dt = datetime.fromisoformat(str(accessed).replace("Z", "+00:00"))
                    days_since = max(1, (_utc_dt() - accessed_dt).days)
                except (ValueError, TypeError):
                    pass
                new_conf = max(_CONFIDENCE_FLOOR, old_conf - self._decay_rate * days_since)
                if new_conf >= old_conf:
                    continue
                val["confidence"] = round(new_conf, 4)
                updates.append(
                    {
                        "id": row_id,
                        "user_id": fact.get("user_id") or user_id,
                        "type": "semantic",
                        "key": row_key,
                        "value": json.dumps(val),
                        "importance": self._confidence_to_importance(new_conf),
                    }
                )

            if not updates:
                return 0

            decayed = 0
            for start in range(0, len(updates), batch_size):
                chunk = updates[start : start + batch_size]
                chunk_ids = [u["id"] for u in chunk]
                landed: List[Dict[str, Any]] = []
                try:
                    supabase.from_(self._table).upsert(chunk, on_conflict="user_id,type,key").execute()
                    landed = chunk
                except Exception as chunk_e:
                    logger.warn(
                        "decay_all chunk upsert failed", user_id=user_id, chunk_size=len(chunk), error=str(chunk_e)
                    )
                if landed:
                    decayed += len(landed)
                    continue
                for update_row in chunk:
                    try:
                        result = (
                            supabase.from_(self._table)
                            .update({"value": update_row["value"], "importance": update_row["importance"]})
                            .eq("id", update_row["id"])
                            .eq("user_id", user_id)
                            .execute()
                        )
                        if result.data:
                            decayed += 1
                    except Exception as row_e:
                        logger.error(
                            "decay_all row update failed",
                            user_id=user_id,
                            memory_id=update_row["id"],
                            error=str(row_e),
                        )
                logger.warn(
                    "decay_all fell back to per-row updates",
                    user_id=user_id,
                    chunk_size=len(chunk_ids),
                )
            return decayed
        except Exception as e:
            logger.error("decay_all failed", user_id=user_id, error=str(e))
            return 0

    def _confidence_to_importance(self, confidence: float) -> str:
        """Map confidence to a retrieval weight, monotonically.

        Previously a confidence below 0.2 (down to and including 0) mapped to
        ``"critical"``, which every consumer ranks highest
        (``retrieval.py`` importance_map) — so the least-trusted memories were
        surfaced first. ``"critical"`` is now reserved for values written
        directly by the consolidation LLM and never derived from confidence.
        """
        if confidence >= 0.8:
            return "high"
        elif confidence >= 0.5:
            return "medium"
        return "low"


class ProceduralMemory:
    """Tier 4: Learned behavioral patterns stored in Supabase memory table with type='procedural'."""

    def __init__(self):
        self._table = "memory"

    async def store_pattern(
        self,
        user_id: str,
        pattern_type: str,
        data: Dict[str, Any],
        confidence: float = 0.6,
        tags: Optional[List[str]] = None,
    ) -> Optional[str]:
        try:
            supabase = get_supabase_client()
            proc_key = _make_key("proc", user_id, pattern_type, str(data.get("signature", "")))
            value = {
                "pattern_type": pattern_type,
                "data": data,
                "confidence": confidence,
                "observation_count": 1,
                "last_observed": _utc_now(),
            }
            existing = (
                supabase.from_(self._table)
                .select("id, value")
                .eq("user_id", user_id)
                .eq("type", "procedural")
                .eq("key", proc_key)
                .execute()
            )
            if existing.data:
                try:
                    existing_val = (
                        json.loads(existing.data[0]["value"])
                        if isinstance(existing.data[0].get("value"), str)
                        else existing.data[0].get("value", {})
                    )
                except (json.JSONDecodeError, TypeError):
                    existing_val = {}
                existing_val["observation_count"] = existing_val.get("observation_count", 0) + 1
                existing_val["last_observed"] = _utc_now()
                existing_val["confidence"] = min(1.0, existing_val.get("confidence", 0.5) + 0.05)
                supabase.from_(self._table).update(
                    {
                        "value": json.dumps(existing_val),
                        "importance": "high" if existing_val["confidence"] >= 0.7 else "medium",
                    }
                ).eq("id", existing.data[0]["id"]).eq("user_id", user_id).execute()
                return existing.data[0]["id"]
            else:
                data_payload = {
                    "user_id": user_id,
                    "type": "procedural",
                    "key": proc_key,
                    "value": json.dumps(value),
                    "importance": "medium" if confidence < 0.7 else "high",
                    "tags": tags or [pattern_type, "procedural"],
                }
                result = supabase.from_(self._table).insert(data_payload).execute()
                if result.data:
                    logger.info("Procedural pattern stored", user_id=user_id, pattern_type=pattern_type)
                    return result.data[0]["id"]
                return None
        except Exception as e:
            logger.error("store_pattern failed", user_id=user_id, error=str(e))
            return None

    async def get_patterns(
        self,
        user_id: str,
        pattern_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        try:
            supabase = get_supabase_client()
            query = supabase.from_(self._table).select("*").eq("user_id", user_id).eq("type", "procedural")
            if pattern_type:
                query = query.contains("tags", [pattern_type])
            result = query.order("importance", desc=True).limit(50).execute()
            return result.data or []
        except Exception as e:
            logger.error("get_patterns failed", user_id=user_id, error=str(e))
            return []

    async def update_from_observation(self, user_id: str, observation: Dict[str, Any]) -> Optional[str]:
        obs_type = observation.get("type", "general")
        obs_data = observation.get("data", {})
        signature = observation.get("signature", str(hash(json.dumps(obs_data, sort_keys=True)) % 10**10))
        obs_data["signature"] = signature
        return await self.store_pattern(user_id, obs_type, obs_data, confidence=0.5)

    async def predict(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            patterns = await self.get_patterns(user_id)
            if not patterns:
                return {"prediction": None, "confidence": 0.0, "matched_patterns": 0}

            context_str = json.dumps(context).lower()
            matches: List[Tuple[float, Dict[str, Any]]] = []
            for pat in patterns:
                try:
                    val = (
                        json.loads(pat.get("value", "{}"))
                        if isinstance(pat.get("value"), str)
                        else pat.get("value", {})
                    )
                except (json.JSONDecodeError, TypeError):
                    continue
                pat_data = val.get("data", {})
                pat_str = json.dumps(pat_data).lower()
                match_score = 0.0
                for kw in context_str.split():
                    kw = kw.strip(",.!?\"'")
                    if len(kw) > 3 and kw in pat_str:
                        match_score += 1.0 / max(1, len(pat_str))
                if match_score > 0:
                    matches.append(
                        (
                            match_score * val.get("confidence", 0.5),
                            val,
                        )
                    )

            if not matches:
                return {"prediction": None, "confidence": 0.0, "matched_patterns": 0}

            matches.sort(key=lambda x: x[0], reverse=True)
            best = matches[0]
            return {
                "prediction": best[1],
                "confidence": best[0],
                "matched_patterns": len(matches),
            }
        except Exception as e:
            logger.error("predict failed", user_id=user_id, error=str(e))
            return {"prediction": None, "confidence": 0.0, "matched_patterns": 0}
