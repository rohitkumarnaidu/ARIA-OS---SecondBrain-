"""Enhanced context engine with Fetch → Filter → Rank → Assemble pipeline, token budgets, agent-specific tailoring, and sub-100ms assembly target."""

import time
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from config.core.supabase import get_supabase_client
from shared.utils.logger import logger
from ai.prompt_loader import prompts


@dataclass
class ContextSectionConfig:
    name: str
    max_tokens: int
    priority: int
    order: int
    table: str
    fields: str = "*"
    filter: Dict[str, Any] = field(default_factory=dict)
    order_by: Optional[str] = None
    limit: int = 10
    fallback: str = ""
    truncation_strategy: str = "drop_lowest"
    ttl_seconds: int = 0
    agent_allowlist: Optional[List[str]] = None


AGENT_SECTION_CONFIGS: Dict[str, List[str]] = {
    "briefing_agent": ["tasks_pending", "tasks_overdue", "habits_today", "sleep_recent", "courses_active", "goals_active", "projects_active"],
    "weekly_review_agent": ["tasks_pending", "tasks_overdue", "goals_active", "courses_active", "habits_today", "sleep_recent", "income_recent", "time_today", "projects_active", "opportunities_open"],
    "memory_agent": ["memory_relevant"],
    "learning_agent": ["courses_active", "goals_active", "tasks_pending", "projects_active"],
    "task_agent": ["tasks_pending", "tasks_overdue", "tasks_today", "goals_active"],
    "opportunity_agent": ["opportunities_open", "memory_relevant"],
    "sleep_agent": ["sleep_recent", "tasks_today"],
    "nudge_agent": ["courses_active", "habits_today", "tasks_pending"],
    "roadmap_agent": ["goals_active", "courses_active", "projects_active"],
    "opportunity_matching_agent": ["opportunities_open", "memory_relevant"],
}


NEEDS_MAP: Dict[str, Dict[str, Any]] = {
    "tasks_pending": {"table": "tasks", "filter": {"status": "pending"}, "limit": 10, "order": "priority desc, due_date asc"},
    "tasks_overdue": {"table": "tasks", "filter": {"status": "overdue"}, "limit": 5, "order": "due_date asc"},
    "tasks_today": {"table": "tasks", "filter": {"due_date": "today"}, "limit": 10, "order": "priority desc"},
    "habits_today": {"table": "habit_logs", "filter": {"date": "today"}, "limit": 10},
    "courses_active": {"table": "courses", "filter": {"status": "in_progress"}, "limit": 10, "order": "deadline asc"},
    "goals_active": {"table": "goals", "filter": {"status": "active"}, "limit": 10, "order": "target_date asc"},
    "sleep_recent": {"table": "sleep_logs", "filter": {}, "limit": 7, "order": "date desc"},
    "income_recent": {"table": "income_entries", "filter": {}, "limit": 10, "order": "date desc"},
    "memory_relevant": {"table": "memory", "filter": {}, "limit": 20, "order": "updated_at desc"},
    "projects_active": {"table": "projects", "filter": {"status": "active"}, "limit": 10, "order": "created_at desc"},
    "time_today": {"table": "time_entries", "filter": {"date": "today"}, "limit": 20, "order": "start_time asc"},
    "opportunities_open": {"table": "opportunities", "filter": {"status": "open"}, "limit": 10, "order": "match_score desc"},
    "habits_streaks": {"table": "habits", "filter": {"active": True}, "limit": 15, "order": "streak desc"},
}


NEEDS_METADATA: Dict[str, ContextSectionConfig] = {
    "tasks_pending": ContextSectionConfig(name="tasks_pending", max_tokens=1000, priority=9, order=4, table="tasks", filter={"status": "pending"}, limit=25, fields="id,title,priority,due_date,status,goal_id", fallback="No pending tasks.", ttl_seconds=0),
    "tasks_overdue": ContextSectionConfig(name="tasks_overdue", max_tokens=400, priority=8, order=5, table="tasks", filter={"status": "overdue"}, limit=10, fields="id,title,priority,due_date", fallback="No overdue tasks.", ttl_seconds=0),
    "tasks_today": ContextSectionConfig(name="tasks_today", max_tokens=600, priority=9, order=3, table="tasks", filter={"due_date": "today"}, limit=15, fields="id,title,priority,status", fallback="No tasks due today.", ttl_seconds=0),
    "habits_today": ContextSectionConfig(name="habits_today", max_tokens=300, priority=6, order=8, table="habit_logs", filter={"date": "today"}, limit=10, fields="id,habit_id,completed,notes", fallback="No habits logged today.", ttl_seconds=60),
    "courses_active": ContextSectionConfig(name="courses_active", max_tokens=400, priority=7, order=6, table="courses", filter={"status": "in_progress"}, limit=10, fields="id,title,progress_pct,deadline", fallback="No active courses.", ttl_seconds=0),
    "goals_active": ContextSectionConfig(name="goals_active", max_tokens=600, priority=8, order=5, table="goals", filter={"status": "active"}, limit=10, fields="id,title,progress_pct,target_date,intensity,category", fallback="No active goals.", ttl_seconds=0),
    "sleep_recent": ContextSectionConfig(name="sleep_recent", max_tokens=300, priority=5, order=7, table="sleep_logs", filter={}, limit=7, fields="date,score,duration_hours,quality", fallback="No sleep data available.", ttl_seconds=300, truncation_strategy="aggregate"),
    "income_recent": ContextSectionConfig(name="income_recent", max_tokens=300, priority=4, order=10, table="income_entries", filter={}, limit=10, fields="date,amount,source,hourly_rate", fallback="No income entries.", ttl_seconds=300),
    "memory_relevant": ContextSectionConfig(name="memory_relevant", max_tokens=500, priority=7, order=9, table="memory", filter={}, limit=20, fields="context_key,context_value,category", fallback="No stored memories.", ttl_seconds=60),
    "projects_active": ContextSectionConfig(name="projects_active", max_tokens=500, priority=6, order=8, table="projects", filter={"status": "active"}, limit=10, fields="id,name,phase,blockers", fallback="No active projects.", ttl_seconds=0),
    "time_today": ContextSectionConfig(name="time_today", max_tokens=400, priority=5, order=9, table="time_entries", filter={"date": "today"}, limit=20, fields="category,duration_minutes,description", fallback="No time entries today.", ttl_seconds=60),
    "opportunities_open": ContextSectionConfig(name="opportunities_open", max_tokens=400, priority=6, order=10, table="opportunities", filter={"status": "open"}, limit=10, fields="id,title,source,match_score,deadline", fallback="No open opportunities.", ttl_seconds=60),
    "habits_streaks": ContextSectionConfig(name="habits_streaks", max_tokens=300, priority=5, order=8, table="habits", filter={"active": True}, limit=15, fields="id,name,streak,consistency_pct,category", fallback="No active habits.", ttl_seconds=60, truncation_strategy="top_k"),
}


class ContextEngine:
    def __init__(
        self,
        supabase_client=None,
        default_cache_ttl: int = 30,
        max_budget_tokens: int = 7800,
        hard_cap_tokens: int = 8192,
        assembly_timeout_ms: int = 200,
    ):
        self.supabase = supabase_client or get_supabase_client()
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = default_cache_ttl
        self.max_budget_tokens = max_budget_tokens
        self.hard_cap_tokens = hard_cap_tokens
        self.assembly_timeout = assembly_timeout_ms / 1000.0

        self._prompt_config: Optional[Dict[str, Any]] = None

    async def _load_prompt_config(self):
        if self._prompt_config is not None:
            return
        entry = prompts.get_template("context_assembly")
        if entry:
            fm = entry.frontmatter
            self.max_budget_tokens = fm.get("max_tokens", self.max_budget_tokens)
            self._cache_ttl = fm.get("cache_ttl_seconds", self._cache_ttl)
            budget_ms = fm.get("assembly_time_budget_ms", 250)
            self.assembly_timeout = budget_ms / 1000.0

    async def assemble_context(
        self,
        user_id: str,
        needs: List[str],
        agent_name: Optional[str] = None,
    ) -> str:
        start = time.time()
        await self._load_prompt_config()

        if agent_name and agent_name in AGENT_SECTION_CONFIGS:
            allowed = AGENT_SECTION_CONFIGS[agent_name]
            needs = [n for n in needs if n in allowed]
        else:
            needs = [n for n in needs if n in NEEDS_MAP]

        sections: List[str] = []
        total_tokens = 0
        truncated: List[str] = []

        sorted_needs = sorted(
            [(n, NEEDS_METADATA.get(n)) for n in needs if n in NEEDS_MAP],
            key=lambda x: x[1].priority if x[1] else 0,
            reverse=True,
        )

        fetch_tasks = []
        need_list = []
        for need_name, config in sorted_needs:
            if total_tokens >= self.max_budget_tokens:
                truncated.append(need_name)
                continue
            fetch_tasks.append(self._fetch_with_cache(user_id, need_name))
            need_list.append(need_name)

        fetch_results = await asyncio.gather(*fetch_tasks, return_exceptions=True)

        for i, need_name in enumerate(need_list):
            result = fetch_results[i]
            config = NEEDS_METADATA.get(need_name)
            if isinstance(result, Exception):
                logger.warn("Context fetch failed", need=need_name, error=str(result))
                formatted = config.fallback if config else ""
            else:
                formatted = self._format_section(need_name, result or [], config)

            if not formatted:
                continue

            tokens = self.estimate_tokens(formatted)
            if config:
                if tokens > config.max_tokens:
                    formatted = self._truncate_to_budget(formatted, config.max_tokens, config.truncation_strategy)
                    tokens = self.estimate_tokens(formatted)

            if total_tokens + tokens > self.hard_cap_tokens:
                truncated.append(need_name)
                continue

            sections.append(formatted)
            total_tokens += tokens

        elapsed = (time.time() - start) * 1000
        result = "\n\n".join(sections)

        if truncated:
            result += "\n\n## TRUNCATED\n- " + "\n- ".join(truncated)

        logger.info(
            "Context assembled",
            needs=len(needs),
            sections=len(sections),
            truncated=len(truncated),
            total_tokens=total_tokens,
            elapsed_ms=round(elapsed, 1),
        )
        return result

    async def assemble_context_dict(
        self,
        user_id: str,
        needs: List[str],
        agent_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        if agent_name and agent_name in AGENT_SECTION_CONFIGS:
            allowed = AGENT_SECTION_CONFIGS[agent_name]
            needs = [n for n in needs if n in allowed]

        result: Dict[str, Any] = {}
        fetch_tasks = []
        valid_needs = []

        for need in needs:
            if need in NEEDS_MAP:
                fetch_tasks.append(self._fetch_with_cache(user_id, need))
                valid_needs.append(need)

        fetch_results = await asyncio.gather(*fetch_tasks, return_exceptions=True)

        for i, need_name in enumerate(valid_needs):
            data = fetch_results[i]
            if isinstance(data, Exception):
                result[need_name] = []
            else:
                result[need_name] = data or []

        return result

    async def _fetch_with_cache(self, user_id: str, need: str) -> List[Dict[str, Any]]:
        config = NEEDS_METADATA.get(need)
        if config and config.ttl_seconds > 0:
            now = time.time()
            cached = self._cache.get(need)
            if cached and now - cached["time"] < config.ttl_seconds:
                logger.debug("Context cache hit", need=need)
                return cached["data"]

        data = await self._fetch(user_id, need)
        if config and config.ttl_seconds > 0:
            self._cache[need] = {"data": data, "time": time.time()}
        return data

    async def _fetch(self, user_id: str, need: str) -> List[Dict[str, Any]]:
        cfg = NEEDS_MAP.get(need)
        if not cfg:
            return []

        try:
            meta = NEEDS_METADATA.get(need)
            query = self.supabase.from_(cfg["table"]).select(meta.fields if meta else "*").eq("user_id", user_id)

            raw_filter = cfg.get("filter", {})
            for key, value in raw_filter.items():
                if value == "today":
                    today_str = datetime.now().strftime("%Y-%m-%d")
                    query = query.eq(key, today_str)
                elif isinstance(value, bool):
                    query = query.eq(key, value)
                else:
                    query = query.eq(key, value)

            order = cfg.get("order")
            if order:
                parts = order.split(",")
                for part in parts:
                    part = part.strip()
                    if not part:
                        continue
                    tokens = part.split()
                    field = tokens[0]
                    desc = len(tokens) > 1 and tokens[1].lower() == "desc"
                    query = query.order(field, desc=desc)

            limit_val = cfg.get("limit")
            if limit_val:
                query = query.limit(limit_val)

            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error("Context fetch failed", table=cfg.get("table", "unknown"), need=need, error=str(e))
            return []

    def _format_section(
        self, need: str, data: List[Dict[str, Any]], config: Optional[ContextSectionConfig] = None
    ) -> str:
        if not data:
            return (config.fallback if config else "") or ""

        header = need.replace("_", " ").title()
        lines = [f"=== {header} ==="]

        table_name = (config.table if config else NEEDS_MAP.get(need, {}).get("table", "")).replace("_", " ").title()

        for item in data[:5]:
            label = item.get("title") or item.get("name") or item.get("context_key") or "entry"
            status = item.get("status") or item.get("category") or ""
            priority = item.get("priority") or ""
            details = f" [{status}]" if status else ""
            details += f" (P:{priority})" if priority else ""
            lines.append(f"  - {label}{details}")

        if len(data) > 5:
            lines.append(f"  ... and {len(data) - 5} more")

        return "\n".join(lines)

    def _truncate_to_budget(self, text: str, budget: int, strategy: str = "drop_lowest") -> str:
        while self.estimate_tokens(text) > budget and len(text) > 50:
            text = text[: int(len(text) * 0.8)] + "\n[...truncated]"
        return text

    @staticmethod
    def estimate_tokens(text: str) -> int:
        return max(1, len(text) // 4)

    def get_cache_stats(self) -> Dict[str, Any]:
        now_ts = time.time()
        return {
            "size": len(self._cache),
            "entries": {
                k: {
                    "age_seconds": int(now_ts - v["time"]),
                    "item_count": len(v["data"]) if isinstance(v.get("data"), list) else 0,
                }
                for k, v in self._cache.items()
            },
        }

    def invalidate_cache(self, need: Optional[str] = None):
        if need:
            self._cache.pop(need, None)
        else:
            self._cache.clear()
