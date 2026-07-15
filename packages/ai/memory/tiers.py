import hashlib
import json
import uuid
from collections import OrderedDict
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List, Tuple

from config.core.supabase import get_supabase_client
from shared.utils.logger import logger


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _utc_dt() -> datetime:
    return datetime.now(timezone.utc)


def _estimate_tokens(text: str) -> int:
    return len(text.split())


def _make_key(*parts: str) -> str:
    raw = ":".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()[:24]


class BufferMemory:
    """Tier 0: Session-level ephemeral ring buffer of recent conversation turns."""

    def __init__(self, capacity: int = 20, token_budget: int = 2000):
        self.capacity = capacity
        self.token_budget = token_budget
        self._messages: List[Dict[str, Any]] = []

    def add(self, user_msg: str, ai_msg: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        now = _utc_now()
        self._messages.append({
            "role": "user",
            "content": user_msg,
            "metadata": metadata or {},
            "timestamp": now,
        })
        self._messages.append({
            "role": "assistant",
            "content": ai_msg,
            "metadata": metadata or {},
            "timestamp": now,
        })
        while len(self._messages) > self.capacity * 2:
            removed = self._messages.pop(0)
            logger.debug("Buffer evicted oldest message", role=removed.get("role"), preview=removed.get("content", "")[:50])

    def get_context(self, k: int = 10) -> List[Dict[str, Any]]:
        if k <= 0:
            return []
        return list(self._messages[-k * 2:])

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
    """Tier 1: Day-level key-value store with TTL, backed by Supabase."""

    def __init__(self, default_ttl: int = 43200):
        self.default_ttl = default_ttl
        self._local: Dict[str, Tuple[Any, float]] = OrderedDict()
        self._dirty_keys: set = set()

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = ttl or self.default_ttl
        expires_at = _utc_dt() + timedelta(seconds=ttl)
        self._local[key] = (value, expires_at.timestamp())
        self._dirty_keys.add(key)
        try:
            supabase = get_supabase_client()
            supabase.from_("working_memory").upsert({
                "key": _make_key("wm", key),
                "user_id": "system",
                "type": "working",
                "value": json.dumps({"key": key, "value": value}),
                "expires_at": expires_at.isoformat(),
            }).execute()
        except Exception as e:
            logger.warn("WorkingMemory.set supabase failed", key=key, error=str(e))

    def get(self, key: str) -> Optional[Any]:
        if key in self._local:
            value, expires = self._local[key]
            if datetime.fromtimestamp(expires, tz=timezone.utc) > _utc_dt():
                return value
            del self._local[key]
        try:
            supabase = get_supabase_client()
            result = supabase.from_("working_memory").select("value").eq("key", _make_key("wm", key)).execute()
            if result.data:
                parsed = json.loads(result.data[0]["value"])
                self._local[key] = (parsed["value"], _utc_dt().timestamp() + self.default_ttl)
                return parsed["value"]
        except Exception as e:
            logger.warn("WorkingMemory.get supabase failed", key=key, error=str(e))
        return None

    def get_all(self) -> Dict[str, Any]:
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

    def clear_expired(self) -> int:
        now = _utc_dt()
        expired = [k for k, (_, e) in self._local.items() if datetime.fromtimestamp(e, tz=timezone.utc) <= now]
        for k in expired:
            del self._local[k]
        try:
            supabase = get_supabase_client()
            supabase.from_("working_memory").delete().lt("expires_at", _utc_now()).execute()
        except Exception as e:
            logger.warn("WorkingMemory.clear_expired supabase failed", error=str(e))
        return len(expired)

    def snapshot(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        now = _utc_dt()
        for key, (value, expires) in self._local.items():
            if datetime.fromtimestamp(expires, tz=timezone.utc) > now:
                result[key] = value
        return result

    def clear(self) -> None:
        self._local.clear()
        self._dirty_keys.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "default_ttl": self.default_ttl,
            "entries": self.snapshot(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkingMemory":
        instance = cls(default_ttl=data.get("default_ttl", 43200))
        for key, value in data.get("entries", {}).items():
            instance.set(key, value)
        return instance

    def __repr__(self) -> str:
        return f"WorkingMemory(entries={len(self._local)}, dirty={len(self._dirty_keys)})"


class EpisodicMemory:
    """Tier 2: User journey episodes stored in Supabase memory table with type='episodic'."""

    def __init__(self):
        self._table = "memory"

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
                "tags": tags or ["episodic"],
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

            groups: Dict[str, List[Dict[str, Any]]] = {}
            for ep in episodes:
                tags = tuple(sorted(ep.get("tags", [])))
                key_summary = str(ep.get("value", {})).lower()[:200]
                group_key = tags if tags else (key_summary[:50],)
                if group_key not in groups:
                    groups[group_key] = []
                groups[group_key].append(ep)

            merged_count = 0
            supabase = get_supabase_client()
            for group_key, group in groups.items():
                if len(group) < 2:
                    continue
                keep = group[0]
                summaries = []
                for ep in group[1:]:
                    try:
                        val = json.loads(ep.get("value", "{}")) if isinstance(ep.get("value"), str) else ep.get("value", {})
                        summaries.append(val.get("summary", ""))
                        supabase.from_(self._table).delete().eq("id", ep["id"]).eq("user_id", user_id).execute()
                        merged_count += 1
                    except Exception as inner_e:
                        logger.warn("Failed to delete duplicate episode", episode_id=ep.get("id"), error=str(inner_e))
                if summaries:
                    try:
                        existing_val = json.loads(keep.get("value", "{}")) if isinstance(keep.get("value"), str) else keep.get("value", {})
                        existing_val["consolidated_summaries"] = summaries
                        supabase.from_(self._table).update({"value": json.dumps(existing_val)}).eq("id", keep["id"]).execute()
                    except Exception as inner_e:
                        logger.warn("Failed to update consolidated episode", error=str(inner_e))

            return {"merged": merged_count, "groups_found": len(groups)}
        except Exception as e:
            logger.error("consolidate episodes failed", user_id=user_id, error=str(e))
            return {"merged": 0, "groups_found": 0}


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
                    existing_val = json.loads(existing.data[0]["value"]) if isinstance(existing.data[0].get("value"), str) else existing.data[0].get("value", {})
                except (json.JSONDecodeError, TypeError):
                    existing_val = {}
                existing_val.update(value)
                existing_val["confidence"] = max(existing_val.get("confidence", confidence), confidence)
                existing_val["reference_count"] = existing_val.get("reference_count", 1) + 1
                supabase.from_(self._table).update({
                    "value": json.dumps(existing_val),
                    "importance": self._confidence_to_importance(existing_val["confidence"]),
                }).eq("id", existing.data[0]["id"]).execute()
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
                    val = json.loads(fact.get("value", "{}")) if isinstance(fact.get("value"), str) else fact.get("value", {})
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
                val = json.loads(result.data[0]["value"]) if isinstance(result.data[0].get("value"), str) else result.data[0].get("value", {})
            except (json.JSONDecodeError, TypeError):
                val = {}
            new_confidence = max(0.0, min(1.0, val.get("confidence", 0.5) + delta))
            val["confidence"] = new_confidence
            supabase.from_(self._table).update({
                "value": json.dumps(val),
                "importance": self._confidence_to_importance(new_confidence),
            }).eq("id", fact_id).execute()
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
                    val = json.loads(fact.get("value", "{}")) if isinstance(fact.get("value"), str) else fact.get("value", {})
                except (json.JSONDecodeError, TypeError):
                    val = {}
                category = val.get("category", "general")
                if category not in seen_categories:
                    cat_id = _make_key("kg_cat", category)
                    seen_categories[category] = cat_id
                    nodes.append({"id": cat_id, "label": category, "type": "category"})
                fact_id = fact.get("id", _make_key("kg_fact", str(fact.get("key", ""))))
                nodes.append({
                    "id": fact_id,
                    "label": val.get("fact", fact.get("key", ""))[:60],
                    "type": "fact",
                    "confidence": val.get("confidence", 0.5),
                    "category": category,
                })
                edges.append({"source": seen_categories[category], "target": fact_id, "label": "contains"})
            return {"nodes": nodes, "edges": edges}
        except Exception as e:
            logger.error("get_knowledge_graph failed", user_id=user_id, error=str(e))
            return {"nodes": [], "edges": []}

    async def decay_all(self, user_id: str) -> int:
        try:
            supabase = get_supabase_client()
            facts = (
                supabase.from_(self._table)
                .select("id, value, importance")
                .eq("user_id", user_id)
                .eq("type", "semantic")
                .execute()
            )
            decayed = 0
            for fact in facts.data or []:
                try:
                    val = json.loads(fact.get("value", "{}")) if isinstance(fact.get("value"), str) else fact.get("value", {})
                except (json.JSONDecodeError, TypeError):
                    continue
                old_conf = val.get("confidence", 0.5)
                days_since = 1
                try:
                    accessed = val.get("last_accessed", _utc_now())
                    accessed_dt = datetime.fromisoformat(accessed.replace("Z", "+00:00"))
                    days_since = max(1, (_utc_dt() - accessed_dt).days)
                except (ValueError, TypeError):
                    pass
                new_conf = max(0.05, old_conf - self._decay_rate * days_since)
                if new_conf < old_conf:
                    val["confidence"] = round(new_conf, 4)
                    supabase.from_(self._table).update({
                        "value": json.dumps(val),
                        "importance": self._confidence_to_importance(new_conf),
                    }).eq("id", fact["id"]).execute()
                    decayed += 1
            return decayed
        except Exception as e:
            logger.error("decay_all failed", user_id=user_id, error=str(e))
            return 0

    def _confidence_to_importance(self, confidence: float) -> str:
        if confidence >= 0.8:
            return "high"
        elif confidence >= 0.5:
            return "medium"
        elif confidence >= 0.2:
            return "low"
        return "critical" if confidence > 0 else "low"


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
                    existing_val = json.loads(existing.data[0]["value"]) if isinstance(existing.data[0].get("value"), str) else existing.data[0].get("value", {})
                except (json.JSONDecodeError, TypeError):
                    existing_val = {}
                existing_val["observation_count"] = existing_val.get("observation_count", 0) + 1
                existing_val["last_observed"] = _utc_now()
                existing_val["confidence"] = min(1.0, existing_val.get("confidence", 0.5) + 0.05)
                supabase.from_(self._table).update({
                    "value": json.dumps(existing_val),
                    "importance": "high" if existing_val["confidence"] >= 0.7 else "medium",
                }).eq("id", existing.data[0]["id"]).execute()
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
            query = (
                supabase.from_(self._table)
                .select("*")
                .eq("user_id", user_id)
                .eq("type", "procedural")
            )
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
                    val = json.loads(pat.get("value", "{}")) if isinstance(pat.get("value"), str) else pat.get("value", {})
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
                    matches.append((
                        match_score * val.get("confidence", 0.5),
                        val,
                    ))

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
