from typing import List, Dict, Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ContextSection:
    name: str
    max_tokens: int
    priority: int
    source: Callable[[str], List[Dict]]
    formatter: Callable[[List[Dict]], str]
    fallback: str = ""
    ttl_seconds: int = 30


@dataclass
class AssembledContext:
    sections: Dict[str, str]
    total_tokens: int
    max_budget: int
    truncated: List[str]
    assembled_at: str


SECTIONS: List[ContextSection] = []


class ContextAssembly:
    def __init__(self, max_budget: int = 7800, hard_cap: int = 8192):
        self.max_budget = max_budget
        self.hard_cap = hard_cap

    @staticmethod
    def estimate_tokens(text: str) -> int:
        return len(text) // 4 + 1

    async def assemble(self, user_id: str) -> AssembledContext:
        sections: Dict[str, str] = {}
        truncated: List[str] = []
        total = 0

        for section in SECTIONS:
            if total >= self.max_budget:
                truncated.append(section.name)
                continue

            section_data = await self._fetch_section(section, user_id)
            formatted = section.formatter(section_data)
            tokens = self.estimate_tokens(formatted)

            if tokens > section.max_tokens:
                formatted = self._truncate_to_budget(formatted, section.max_tokens)
                tokens = self.estimate_tokens(formatted)

            if total + tokens > self.hard_cap:
                truncated.append(section.name)
                continue

            sections[section.name] = formatted
            total += tokens

        return AssembledContext(
            sections=sections,
            total_tokens=total,
            max_budget=self.max_budget,
            truncated=truncated,
            assembled_at=datetime.now().isoformat(),
        )

    async def _fetch_section(self, section: ContextSection, user_id: str) -> List[Dict]:
        try:
            data = await section.source(user_id)
            return data or []
        except Exception:
            return []

    def _truncate_to_budget(self, text: str, budget: int) -> str:
        while self.estimate_tokens(text) > budget and len(text) > 50:
            text = text[: int(len(text) * 0.8)] + "\n[...truncated]"
        return text

    def flatten(self, ctx: AssembledContext) -> str:
        parts = [f"## {name.upper()}\n{content}" for name, content in ctx.sections.items()]
        if ctx.truncated:
            parts.append(f"\n## TRUNCATED\n- {'\\n- '.join(ctx.truncated)}")
        return "\n\n".join(parts)
