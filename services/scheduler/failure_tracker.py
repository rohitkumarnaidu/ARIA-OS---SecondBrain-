"""Tracks cron job failures with thread-safe counters"""

import asyncio
import time
from datetime import date
from collections import defaultdict


class FailureTracker:
    def __init__(self):
        self._lock = asyncio.Lock()
        self._consecutive_failures: dict[str, int] = defaultdict(int)
        self._last_failure_time: dict[str, float] = {}
        self._last_success_time: dict[str, float] = {}
        self._daily_failures: dict[str, int] = defaultdict(int)
        self._current_date: str = ""

    async def record_failure(self, job_name: str, error: str):
        async with self._lock:
            today = date.today().isoformat()
            if self._current_date != today:
                self._daily_failures.clear()
                self._current_date = today
            self._consecutive_failures[job_name] += 1
            self._last_failure_time[job_name] = time.time()
            self._daily_failures[job_name] += 1

    async def record_success(self, job_name: str):
        async with self._lock:
            self._consecutive_failures[job_name] = 0
            self._last_success_time[job_name] = time.time()

    async def get_consecutive_failures(self, job_name: str) -> int:
        async with self._lock:
            return self._consecutive_failures.get(job_name, 0)

    async def get_failing_jobs(self, threshold: int = 3) -> list[dict]:
        async with self._lock:
            return [
                {
                    "job_name": name,
                    "consecutive_failures": count,
                    "last_failure": self._last_failure_time.get(name),
                }
                for name, count in self._consecutive_failures.items()
                if count >= threshold
            ]

    async def get_daily_failure_count(self) -> int:
        async with self._lock:
            return sum(self._daily_failures.values())

    async def is_circuit_open(self, job_name: str) -> bool:
        async with self._lock:
            return self._consecutive_failures.get(job_name, 0) >= 5

    async def get_summary(self) -> dict:
        async with self._lock:
            return {
                "consecutive_failures": dict(self._consecutive_failures),
                "daily_failures": dict(self._daily_failures),
                "total_daily_failures": sum(self._daily_failures.values()),
                "failing_jobs": [
                    {"job_name": name, "consecutive_failures": count}
                    for name, count in self._consecutive_failures.items()
                    if count > 0
                ],
                "open_circuits": [
                    name
                    for name, count in self._consecutive_failures.items()
                    if count >= 5
                ],
            }


failure_tracker = FailureTracker()
