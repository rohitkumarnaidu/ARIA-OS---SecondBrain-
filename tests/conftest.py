"""Test configuration — adds project paths to sys.path for imports."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

# Add packages/ so tests can import ai.*, config.*, database.*, shared.*
packages_path = str(ROOT / "packages")
if packages_path not in sys.path:
    sys.path.insert(0, packages_path)

# Add apps/api/ so tests can import app.api.*
api_path = str(ROOT / "apps" / "api")
if api_path not in sys.path:
    sys.path.insert(0, api_path)

# Add services/scheduler/ so tests can import crons.*
scheduler_path = str(ROOT / "services" / "scheduler")
if scheduler_path not in sys.path:
    sys.path.insert(0, scheduler_path)


# ---------------------------------------------------------------------------
# Module-singleton isolation
# ---------------------------------------------------------------------------
# services/scheduler/main.py and services/scheduler/alerting.py each expose a
# module-level singleton: `scheduler` (AsyncIOScheduler) and `alerting`
# (Alerting, which owns an AlertRateLimiter with its own _last_alert dict).
# Roughly 20 tests across test_scheduler*.py rebind attributes on those objects
# directly -- `main.scheduler = MagicMock()`, `main.asyncio = asyncio`,
# `alerting._webhook_url = ...` -- with no teardown.
#
# Because the modules stay in sys.modules for the whole session, those writes
# outlive the test that made them, so the damage only shows up when the files
# are run TOGETHER. Concretely, before this fixture:
#   * tests/test_scheduler.py passes 79/79 on its own, but
#     test_all_fifteen_jobs_registered sees zero jobs after test_scheduler_full.py
#     replaces `main.scheduler` with a MagicMock.
#   * test_main_function_setup_and_start fails for the same reason.
# This restores the singletons after every test. It adds no skips and weakens no
# assertion; it only makes each test start from the state it assumes.
_ISOLATED_MODULES = ("main", "alerting")


@pytest.fixture(autouse=True)
def _isolate_scheduler_module_singletons():
    """Snapshot and restore scheduler/alerting module-level singletons."""

    def targets():
        found = []
        for name in _ISOLATED_MODULES:
            module = sys.modules.get(name)
            if module is None:
                continue
            found.append(module)
            instance = getattr(module, name, None)
            if instance is not None and hasattr(instance, "__dict__"):
                found.append(instance)
        return found

    objects = targets()
    snapshots = [(obj, dict(vars(obj))) for obj in objects]

    # AlertRateLimiter._last_alert is mutated in place, so restoring the
    # containing object's __dict__ is not enough -- snapshot the dict itself.
    limiter_states = [
        (getattr(obj, "_rate_limiter"), dict(obj._rate_limiter._last_alert))
        for obj in objects
        if hasattr(getattr(obj, "_rate_limiter", None), "_last_alert")
    ]

    try:
        yield
    finally:
        for obj, snapshot in snapshots:
            current = vars(obj)
            for key in [k for k in current if k not in snapshot]:
                del current[key]
            for key, value in snapshot.items():
                if current.get(key) is not value:
                    current[key] = value

        for limiter, state in limiter_states:
            limiter._last_alert.clear()
            limiter._last_alert.update(state)
