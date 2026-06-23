from typing import Any, Dict, List, Optional, Callable, TypeVar
from dataclasses import dataclass, field
from datetime import datetime, timezone

T = TypeVar("T")


@dataclass
class BatchResult:
    results: Dict[str, Any] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    @property
    def duration_ms(self) -> float:
        end = self.completed_at or datetime.now(timezone.utc)
        return (end - self.started_at).total_seconds() * 1000

    @property
    def success_count(self) -> int:
        return len(self.results)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    def fail(self, key: str, error: str):
        self.errors[key] = error

    def ok(self, key: str, value: Any):
        self.results[key] = value

    def finish(self):
        self.completed_at = datetime.now(timezone.utc)


class BatchExecutor:
    """Execute multiple async queries in parallel with error isolation."""

    def __init__(self, concurrency: int = 5):
        self.concurrency = concurrency
        self._queries: List[tuple] = []

    def add(self, key: str, fn: Callable, *args, **kwargs):
        self._queries.append((key, fn, args, kwargs))

    async def execute(self) -> BatchResult:
        import asyncio

        result = BatchResult()
        semaphore = asyncio.Semaphore(self.concurrency)

        async def run(key: str, fn: Callable, args: tuple, kwargs: dict):
            async with semaphore:
                try:
                    value = await fn(*args, **kwargs) if asyncio.iscoroutinefunction(fn) else fn(*args, **kwargs)
                    result.ok(key, value)
                except Exception as e:
                    result.fail(key, str(e))

        tasks = [run(k, fn, a, kw) for k, fn, a, kw in self._queries]
        await asyncio.gather(*tasks)
        result.finish()
        return result


async def batch_supabase_queries(queries: Dict[str, Callable], concurrency: int = 5) -> Dict[str, Any]:
    """Batch multiple supabase queries and return combined results.

    Usage:
        data = await batch_supabase_queries({
            "tasks": lambda: supabase.table("tasks").select("*").eq("user_id", uid).execute(),
            "habits": lambda: supabase.table("habits").select("*").eq("user_id", uid).execute(),
        })
    """
    executor = BatchExecutor(concurrency=concurrency)
    for key, fn in queries.items():
        executor.add(key, fn)
    batch_result = await executor.execute()
    return {
        "data": batch_result.results,
        "errors": batch_result.errors,
        "duration_ms": batch_result.duration_ms,
    }
