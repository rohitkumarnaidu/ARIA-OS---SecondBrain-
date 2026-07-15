import json
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from config.core.supabase import get_supabase_client
from shared.utils.logger import logger


def _utc_dt() -> datetime:
    return datetime.now(timezone.utc)


def _estimate_tokens(text: str) -> int:
    return len(text.split())


class MemoryCompressor:
    """Memory compression using age-based strategies — summarization, temporal binning, key-value extraction, and pruning."""

    def __init__(self):
        self._lossless_days = 7
        self._light_days = 30
        self._aggressive_days = 90

    def compress_episodes(self, episodes: List[Dict[str, Any]], max_tokens: int = 2048) -> List[Dict[str, Any]]:
        if not episodes:
            return []
        compressed: List[Dict[str, Any]] = []
        total_tokens = 0
        for ep in sorted(episodes, key=lambda e: e.get("created_at", ""), reverse=True):
            age_days = self._get_age_days(ep)
            processed = self._compress_single(ep, age_days)
            tokens = _estimate_tokens(json.dumps(processed))
            if total_tokens + tokens > max_tokens:
                processed = self._emergency_truncate(processed, max_tokens - total_tokens)
                if processed is not None:
                    compressed.append(processed)
                break
            compressed.append(processed)
            total_tokens += tokens
        return compressed

    def summarize_memories(self, memories: List[Dict[str, Any]]) -> str:
        if not memories:
            return "No memories to summarize."
        total = len(memories)
        types: Dict[str, int] = {}
        categories: Dict[str, int] = {}
        total_confidence = 0.0
        for mem in memories:
            mtype = mem.get("type", "unknown")
            types[mtype] = types.get(mtype, 0) + 1
            try:
                val = json.loads(mem.get("value", "{}")) if isinstance(mem.get("value"), str) else mem.get("value", {})
            except (json.JSONDecodeError, TypeError):
                val = {}
            cat = val.get("category", "general") if isinstance(val, dict) else "general"
            categories[cat] = categories.get(cat, 0) + 1
            total_confidence += val.get("confidence", 0.5) if isinstance(val, dict) else 0.5
        avg_conf = round(total_confidence / max(total, 1), 2)
        type_summary = ", ".join(f"{k}: {v}" for k, v in sorted(types.items(), key=lambda x: x[1], reverse=True))
        cat_summary = ", ".join(
            f"{k}: {v}" for k, v in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
        )
        summary = (
            f"Memory summary: {total} items across {len(types)} types ({type_summary}). "
            f"Top categories: {cat_summary}. "
            f"Average confidence: {avg_conf}."
        )
        return summary

    def prune_old_memories(self, user_id: str, days: int = 90) -> int:
        try:
            supabase = get_supabase_client()
            cutoff = (_utc_dt() - timedelta(days=days)).isoformat()
            result = (
                supabase.from_("memory")
                .delete()
                .eq("user_id", user_id)
                .lt("created_at", cutoff)
                .execute()
            )
            pruned = len(result.data or [])
            if pruned:
                logger.info("Pruned old memories", user_id=user_id, days=days, count=pruned)
            return pruned
        except Exception as e:
            logger.error("prune_old_memories failed", user_id=user_id, error=str(e))
            return 0

    def compress_temporal(self, memories: List[Dict[str, Any]], bin_days: int = 7) -> List[Dict[str, Any]]:
        if not memories:
            return []
        binned: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        for mem in memories:
            try:
                created = mem.get("created_at", "")
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                bucket = int(dt.timestamp() // (bin_days * 86400))
                binned[bucket].append(mem)
            except (ValueError, TypeError):
                continue
        result: List[Dict[str, Any]] = []
        for bucket, group in sorted(binned.items()):
            start_ts = bucket * bin_days * 86400
            end_ts = (bucket + 1) * bin_days * 86400
            compressed_summary = self.summarize_memories(group)
            types = list(set(m.get("type", "unknown") for m in group))
            result.append({
                "bucket_start": datetime.fromtimestamp(start_ts, tz=timezone.utc).isoformat(),
                "bucket_end": datetime.fromtimestamp(end_ts, tz=timezone.utc).isoformat(),
                "count": len(group),
                "types": types,
                "summary": compressed_summary,
            })
        return result

    def _compress_single(self, entry: Dict[str, Any], age_days: float) -> Dict[str, Any]:
        try:
            val = json.loads(entry.get("value", "{}")) if isinstance(entry.get("value"), str) else entry.get("value", {})
        except (json.JSONDecodeError, TypeError):
            val = {}
        if age_days < self._lossless_days:
            return entry
        elif age_days < self._light_days:
            return self._light_compress(entry, val)
        elif age_days < self._aggressive_days:
            return self._aggressive_compress(entry, val)
        else:
            return self._archive_compress(entry, val)

    def _light_compress(self, entry: Dict[str, Any], val: Any) -> Dict[str, Any]:
        if isinstance(val, dict):
            if "summary" in val and len(val.get("summary", "")) > 200:
                val["summary"] = val["summary"][:200]
            if "session_data" in val and isinstance(val["session_data"], dict):
                for k in list(val["session_data"].keys()):
                    if isinstance(val["session_data"][k], str) and len(val["session_data"][k]) > 500:
                        val["session_data"][k] = val["session_data"][k][:200] + "..."
        return {**entry, "value": json.dumps(val) if isinstance(val, dict) else val}

    def _aggressive_compress(self, entry: Dict[str, Any], val: Any) -> Dict[str, Any]:
        if isinstance(val, dict):
            compressed = {
                "type": entry.get("type", "unknown"),
                "confidence": val.get("confidence", 0.5),
                "category": val.get("category", "general"),
            }
            if "summary" in val:
                compressed["summary"] = val["summary"][:100]
            if "fact" in val:
                compressed["fact"] = val["fact"][:100]
            return {**entry, "value": json.dumps(compressed)}
        return {**entry, "value": json.dumps({"compressed": str(val)[:100]})}

    def _archive_compress(self, entry: Dict[str, Any], val: Any) -> Dict[str, Any]:
        if isinstance(val, dict):
            compressed = {
                "type": entry.get("type", "unknown"),
                "confidence": val.get("confidence", 0.5),
                "category": val.get("category", "general"),
            }
            return {**entry, "value": json.dumps(compressed)}
        return {**entry, "value": json.dumps({"archived": True})}

    def _emergency_truncate(self, entry: Dict[str, Any], budget: int) -> Optional[Dict[str, Any]]:
        if budget <= 0:
            return None
        try:
            val = json.loads(entry.get("value", "{}")) if isinstance(entry.get("value"), str) else entry.get("value", {})
        except (json.JSONDecodeError, TypeError):
            val = {}
        if isinstance(val, dict):
            for k in list(val.keys()):
                if isinstance(val[k], str) and _estimate_tokens(val[k]) > budget:
                    val[k] = val[k][:budget * 4]
            return {**entry, "value": json.dumps(val)}
        return entry

    def _get_age_days(self, entry: Dict[str, Any]) -> float:
        try:
            created = entry.get("created_at", _utc_dt().isoformat())
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            return (_utc_dt() - dt).total_seconds() / 86400.0
        except (ValueError, TypeError):
            return 0.0
