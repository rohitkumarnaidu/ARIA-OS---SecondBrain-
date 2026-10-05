"""Test configuration — adds project paths to sys.path for imports."""

import os
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Deterministic environment BEFORE any project import
# ---------------------------------------------------------------------------
# `packages/config/core/supabase.py` does `from config.core.config import
# settings` at module scope, so the moment ANY test module imports a project
# module, a pydantic `Settings` singleton is constructed from the process
# environment *and* the repo-root `.env`. That singleton is then frozen for the
# whole session.
#
# Several test modules used to paper over this with import-time
# `os.environ.setdefault("SUPABASE_URL", ...)`. That is order-dependent: pytest
# imports test modules alphabetically, so `test_routes_knowledge.py` triggered
# the `config` import and froze `settings` with whatever `.env` held BEFORE
# `test_tool_calling.py` got to run its `setdefault`. Isolated, those tests
# passed; in a batch, `get_supabase_client()` raised
# "Supabase URL and key must be configured" and 11 tool-calling tests failed.
#
# Fix: pin the Supabase credential trio here, in conftest, which pytest imports
# before any test module. Real environment variables take precedence over
# `.env` in pydantic-settings, so these win deterministically regardless of
# what a developer's local `.env` contains.
#
# Scope is deliberately minimal. Only these three are pinned, because only
# these three are required for `get_supabase_client()` to return a client at
# all. Pinning more (ENVIRONMENT, USE_LOCAL_AI, SENTRY_DSN, ...) changes real
# `Settings` defaults and real health-check behaviour, which several tests
# assert against -- so those are left to the test that owns them.
_TEST_ENV = {
    "SUPABASE_URL": "https://test.supabase.co",
    "SUPABASE_KEY": "test-anon-key",
    "SUPABASE_SERVICE_KEY": "test-service-role-key",
}
for _key, _value in _TEST_ENV.items():
    os.environ[_key] = _value

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
# Single-app-module guard
# ---------------------------------------------------------------------------
# `apps/api` is on sys.path above, so route modules import as `app.api.<name>`
# (e.g. `app.api.chat`). The FastAPI application itself lives one level higher,
# at `apps/api/main.py`.
#
# It must NOT be imported as bare `main`: `services/scheduler/main.py` is also
# on sys.path, so the two collide and only one wins per session. It must NOT be
# imported as `app.main` either -- there is no `apps/api/app/main.py`.
#
# The collision-free canonical key is therefore `apps.api.main` (namespace
# package, since `apps/__init__.py` is intentionally absent).
#
# Note that bare `main` is legitimately in sys.modules for the scheduler tests:
# `services/scheduler` is also on sys.path and its entrypoint is `main.py`. So
# this guard does not ban the name `main` -- it bans `main` resolving to the
# *API* application, which is the actual split-brain failure.
_CANONICAL_APP_MODULE = "apps.api.main"
_BAD_APP_ALIASES = ("main", "app.main")


def _is_api_app(module: Any) -> bool:
    """True when a module object looks like the FastAPI API application."""
    app_obj = getattr(module, "app", None)
    return app_obj.__class__.__name__ == "FastAPI"


@pytest.fixture(autouse=True, scope="session")
def _assert_single_app_module():
    """Fail loudly if the API app got imported under a second module key."""
    yield
    offenders = [name for name in _BAD_APP_ALIASES if name in sys.modules and _is_api_app(sys.modules[name])]
    assert not offenders, (
        f"the FastAPI app was imported as {offenders} in addition to "
        f"{_CANONICAL_APP_MODULE!r}. Each spelling re-executes main.py and builds a "
        f"second app with its own middleware stack and router registry, which makes "
        f"results order-dependent. Import it as {_CANONICAL_APP_MODULE!r}; bare 'main' "
        f"is the scheduler entrypoint."
    )


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
def _isolate_settings_singleton():
    """Snapshot/restore the ``settings`` singleton and the Supabase client cache.

    Two process-wide singletons leak between test files:

    1. ``config.core.config.settings`` -- a module-level pydantic instance.
       Many tests rebind its fields directly (``settings.supabase_url = ...``)
       and a good number have no teardown, so the mutation leaks into whichever
       file runs next. ``test_integration_llm.py::TestBriefingsIntegration`` has
       no settings fixture of its own (unlike its sibling
       ``TestAutomationIntegration``, which does), so it inherited whatever an
       earlier file left behind.

    2. ``config.core.supabase._supabase_client`` -- a module-level cache in
       ``get_supabase_client()``. ``test_integration.py`` patches
       ``config.core.supabase.create_client`` with a ``MagicMock``; the first
       call inside the patch populates the cache, and because nothing ever
       clears it, every LATER test in the session silently receives the
       MagicMock. Its ``.data[0]`` yields MagicMock attributes, which then fail
       Pydantic response validation and surface as an opaque HTTP 500 -- e.g.
       ``GET /api/v1/briefings/today`` returned 500 instead of 200 in a full run
       while passing in isolation.

    Resetting both makes each test start from the state it assumes.
    """
    config = sys.modules.get("config.core.config")
    supabase_mod = sys.modules.get("config.core.supabase")

    settings = getattr(config, "settings", None) if config is not None else None
    snapshot = dict(vars(settings)) if settings is not None else None
    cached_client = getattr(supabase_mod, "_supabase_client", None) if supabase_mod is not None else None
    had_client_attr = supabase_mod is not None and hasattr(supabase_mod, "_supabase_client")

    try:
        yield
    finally:
        if settings is not None and snapshot is not None:
            current = vars(settings)
            for key in [k for k in current if k not in snapshot]:
                del current[key]
            for key, value in snapshot.items():
                current[key] = value

        if supabase_mod is not None and had_client_attr:
            supabase_mod._supabase_client = cached_client


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
