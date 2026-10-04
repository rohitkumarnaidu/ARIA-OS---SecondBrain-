"""Query-scoping contract tests — real detection power for tenant isolation.

Why this module exists
----------------------
The suite's established double (``MockQueryBuilder`` in
``tests/test_api_endpoints.py:170`` and its verbatim copy in
``tests/test_api_routes_advanced.py:28``) is tautological:

    def eq(self, col, val):
        return self          # both arguments are discarded

    def from_(self, table):  # returns the same builder for ANY table name
        return self

Because ``eq`` throws its arguments away, a route that filters by the wrong
column, forgets ``.eq("user_id", ...)`` entirely, or reads the wrong table
produces the *exact same* observable behaviour as a correct route. Those ~600
tests cannot fail on scoping regressions. Worse, ``from_`` returning one
builder for every table name means a typo like ``from_("tsaks")`` is
invisible, and ``range()`` discarding its arguments means broken pagination is
invisible too.

This module replaces the double with a *recording* builder that:

1. appends every chained call — method name, positional args and keyword args —
   to a shared call log, tagged with the table it belongs to; and
2. actually applies ``eq`` / ``range`` / ``order`` semantics when ``execute()``
   runs, so the assertions hold on behaviour as well as on the call trace.

Every router test below asserts the real call sequence. Delete an
``.eq("user_id", ...)`` from any of them and the matching test fails.
"""

import importlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import pytest

# ===========================================================================
# Recording test double
# ===========================================================================


@dataclass(frozen=True)
class Call:
    """One recorded query-builder invocation."""

    table: str
    method: str
    args: Tuple[Any, ...] = ()
    kwargs: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"{self.table}.{self.method}({self.args!r}, {self.kwargs!r})"


class CallLog:
    """Ordered log of every query-builder call made during one route call."""

    def __init__(self) -> None:
        self.calls: List[Call] = []

    def record(self, call: Call) -> None:
        self.calls.append(call)

    # -- inspection helpers -------------------------------------------------

    @property
    def tables(self) -> List[str]:
        """Table names passed to ``from_()``, in call order, with duplicates."""
        return [c.args[0] for c in self.calls if c.method == "from_"]

    def chains(self, table: Optional[str] = None) -> List[List[Call]]:
        """Split the flat log into one list of calls per ``from_()``.

        A "chain" is ``from_(t)`` plus every fluent call made on the builder it
        returned, up to (and including) the terminal ``execute()``/``insert()``.
        """
        result: List[List[Call]] = []
        current: Optional[List[Call]] = None
        for call in self.calls:
            if call.method == "from_":
                current = [call]
                result.append(current)
            elif current is not None:
                current.append(call)
        if table is not None:
            result = [c for c in result if c[0].args[0] == table]
        return result

    def find(self, table: str, method: str) -> List[Call]:
        return [c for c in self.calls if c.table == table and c.method == method]

    def sequence(self, table: Optional[str] = None) -> List[Tuple[str, Tuple[Any, ...]]]:
        """Compact ``[(method, args), ...]`` view, optionally for one table."""
        return [(c.method, c.args) for c in self.calls if table is None or c.table == table]

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return "\n".join(f"  {c!r}" for c in self.calls)


class RecordingQueryBuilder:
    """Supabase-style fluent builder that records calls AND honours filters.

    Unlike ``MockQueryBuilder``, nothing here is a no-op: ``eq`` narrows the
    result set, ``range`` slices it, and both leave their fingerprints on the
    call log.
    """

    def __init__(self, log: CallLog, table: str, rows: List[Dict[str, Any]]) -> None:
        self._log = log
        self._table = table
        self._rows = list(rows)
        self._eq: List[Tuple[str, Any]] = []
        self._order: Optional[Tuple[str, bool]] = None
        self._range: Optional[Tuple[int, int]] = None
        self._limit: Optional[int] = None
        self._mutated: List[Dict[str, Any]] = []

    # -- fluent methods -----------------------------------------------------

    def _step(self, method: str, *args: Any, **kwargs: Any) -> "RecordingQueryBuilder":
        self._log.record(Call(self._table, method, args, kwargs))
        return self

    def select(self, *args: Any, **kwargs: Any) -> "RecordingQueryBuilder":
        return self._step("select", *args, **kwargs)

    def eq(self, column: str, value: Any) -> "RecordingQueryBuilder":
        self._eq.append((column, value))
        return self._step("eq", column, value)

    def neq(self, column: str, value: Any) -> "RecordingQueryBuilder":
        self._eq.append((column, value))
        return self._step("neq", column, value)

    def gte(self, column: str, value: Any) -> "RecordingQueryBuilder":
        self._eq.append((column, value))
        return self._step("gte", column, value)

    def lte(self, column: str, value: Any) -> "RecordingQueryBuilder":
        return self._step("lte", column, value)

    def gt(self, column: str, value: Any) -> "RecordingQueryBuilder":
        return self._step("gt", column, value)

    def lt(self, column: str, value: Any) -> "RecordingQueryBuilder":
        return self._step("lt", column, value)

    def in_(self, column: str, values: Any) -> "RecordingQueryBuilder":
        return self._step("in_", column, tuple(values) if values is not None else values)

    def text_search(self, column: str, query: str, **kwargs: Any) -> "RecordingQueryBuilder":
        return self._step("text_search", column, query, **kwargs)

    def order(self, column: str, **kwargs: Any) -> "RecordingQueryBuilder":
        # Supabase uses `ascending=`; supabase-py/postgrest uses `desc=`.
        descending = kwargs.get("descending", kwargs.get("desc", False))
        self._order = (column, bool(descending))
        return self._step("order", column, **kwargs)

    def range(self, start: int, end: int) -> "RecordingQueryBuilder":
        self._range = (start, end)
        return self._step("range", start, end)

    def limit(self, count: int) -> "RecordingQueryBuilder":
        self._limit = count
        return self._step("limit", count)

    def or_(self, *args: Any, **kwargs: Any) -> "RecordingQueryBuilder":
        return self._step("or_", *args, **kwargs)

    def not_(self, *args: Any, **kwargs: Any) -> "RecordingQueryBuilder":
        return self._step("not_", *args, **kwargs)

    def is_(self, column: str, value: Any) -> "RecordingQueryBuilder":
        return self._step("is_", column, value)

    # -- mutations ----------------------------------------------------------

    def insert(self, data: Any) -> "RecordingQueryBuilder":
        self._mutated.append(data)
        return self._step("insert", data)

    def update(self, data: Any) -> "RecordingQueryBuilder":
        self._mutated.append(data)
        return self._step("update", data)

    def upsert(self, data: Any, **kwargs: Any) -> "RecordingQueryBuilder":
        self._mutated.append(data)
        return self._step("upsert", data, **kwargs)

    def delete(self) -> "RecordingQueryBuilder":
        return self._step("delete")

    # -- terminals ----------------------------------------------------------

    def _result(self):
        class _Result:
            pass

        result = _Result()
        rows = [r for r in self._rows if all(r.get(k) == v for k, v in self._eq)]
        if self._order:
            column, descending = self._order
            rows = sorted(
                rows,
                key=lambda r: (r.get(column) is None, r.get(column)),
                reverse=descending,
            )
        if self._range is not None:
            start, end = self._range
            rows = rows[start : end + 1]
        if self._limit is not None:
            rows = rows[: self._limit]
        result.data = rows
        result.count = len(rows)
        result.error = None
        return result

    def execute(self):
        self._log.record(Call(self._table, "execute"))
        return self._result()

    def single(self):
        self._log.record(Call(self._table, "single"))
        result = self._result()
        result.data = result.data[0] if result.data else None
        return result

    def maybe_single(self):
        return self.single()


class RecordingSupabase:
    """Stand-in for the Supabase client that keeps a per-table call log."""

    def __init__(self, tables: Dict[str, List[Dict[str, Any]]]) -> None:
        self.tables = {name: list(rows) for name, rows in tables.items()}
        self.log = CallLog()

    def from_(self, table: str) -> RecordingQueryBuilder:
        # A brand new builder per table, and the table name is recorded. This
        # is the single most important difference from MockQueryBuilder, whose
        # from_() ignores its argument entirely.
        self.log.record(Call("<client>", "from_", (table,)))
        builder = RecordingQueryBuilder(self.log, table, self.tables.get(table, []))
        # Re-tag the from_ entry so per-table helpers can see it.
        self.log.calls[-1] = Call(table, "from_", (table,))
        return builder


# ===========================================================================
# Fixtures / helpers
# ===========================================================================

OTHER_USER = "user-OTHER-tenant"
CALLER = "user-CALLER"

# Rows owned by two different tenants. A route that forgets
# .eq("user_id", ...) returns BOTH sets; one that filters wrongly returns the
# wrong set. Either way these rows make the leak observable.
TWO_TENANT_ROWS = [
    {"id": "row-mine", "user_id": CALLER, "title": "Mine"},
    {"id": "row-theirs", "user_id": OTHER_USER, "title": "Theirs"},
]


def task_row(task_id: str, owner: str, title: str) -> Dict[str, Any]:
    """A row that satisfies TaskResponse's required fields.

    TaskResponse (packages/database/schemas/task.py:63-70) requires id, user_id,
    status, completed_at, missed_count, created_at and updated_at on top of
    TaskBase's title.
    """
    return {
        "id": task_id,
        "user_id": owner,
        "title": title,
        "status": "pending",
        "completed_at": None,
        "missed_count": 0,
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
    }


# GET /api/v1/tasks/ declares response_model=TaskListResponse[TaskResponse], so
# task rows must carry the non-null fields TaskResponse requires. The generic
# two-tenant rows above are not enough for that router.
TWO_TENANT_TASK_ROWS = [
    task_row("row-mine", CALLER, "Mine"),
    task_row("row-theirs", OTHER_USER, "Theirs"),
]


def seed_rows(table: str) -> List[Dict[str, Any]]:
    """Rows appropriate for `table`'s response_model."""
    return TWO_TENANT_TASK_ROWS if table == "tasks" else TWO_TENANT_ROWS


class _FakeUser:
    def __init__(self, user_id: str) -> None:
        self.user = type("_U", (), {"id": user_id})()


@pytest.fixture
def fake_user() -> _FakeUser:
    return _FakeUser(CALLER)


def make_client(**tables: List[Dict[str, Any]]) -> RecordingSupabase:
    """Build a RecordingSupabase, seeding any table not given explicit rows."""
    return RecordingSupabase({name: list(rows) if rows else list(seed_rows(name)) for name, rows in tables.items()})


def install(monkeypatch, module_name: str, client: RecordingSupabase) -> Any:
    """Point `module_name`'s get_supabase_client at `client`; return the module."""
    module = importlib.import_module(module_name)
    monkeypatch.setattr(module, "get_supabase_client", lambda: client)
    return module


# (module, router module attr, list-endpoint callable name, table, default limit)
LIST_ROUTES = [
    ("app.api.memory", "list_memories", "memory", 50),
    ("app.api.tasks", "get_tasks", "tasks", 20),
    ("app.api.courses", "get_courses", "courses", 20),
    ("app.api.goals", "get_goals", "goals", 20),
    ("app.api.habits", "get_habits", "habits", 20),
    ("app.api.sleep", "get_sleep", "sleep_logs", 30),
    ("app.api.income", "get_income", "income_entries", 20),
    ("app.api.opportunities", "get_opportunities", "opportunities", 20),
    ("app.api.projects", "get_projects", "projects", 20),
    ("app.api.ideas", "get_ideas", "ideas", 20),
    ("app.api.resources", "get_resources", "resources", 20),
    ("app.api.time", "get_time_entries", "time_entries", 20),
]

# (module, detail-endpoint callable name, table, id kwarg)
DETAIL_ROUTES = [
    ("app.api.memory", "get_memory", "memory", "memory_id"),
    ("app.api.tasks", "get_task", "tasks", "task_id"),
    ("app.api.courses", "get_course", "courses", "course_id"),
    ("app.api.goals", "get_goal", "goals", "goal_id"),
    ("app.api.habits", "get_habit", "habits", "habit_id"),
    ("app.api.sleep", "get_sleep_entry", "sleep_logs", "sleep_id"),
    ("app.api.income", "get_income_entry", "income_entries", "income_id"),
    ("app.api.opportunities", "get_opportunity", "opportunities", "opportunity_id"),
    ("app.api.projects", "get_project", "projects", "project_id"),
    ("app.api.ideas", "get_idea", "ideas", "idea_id"),
    ("app.api.resources", "get_resource", "resources", "resource_id"),
    ("app.api.time", "get_time_entry", "time_entries", "entry_id"),
]


def ids_in(payload: Any) -> List[str]:
    """Normalise a route return value into a list of row ids.

    Three shapes occur:
      * a pydantic model -- GET /tasks/ returns TaskListResponse (a BaseModel, so
        it must NOT be subscripted or iterated: iterating a BaseModel yields
        (field_name, value) pairs);
      * a dict envelope containing "data";
      * the raw `response.data` list of dicts the other routers return.
    """
    if hasattr(payload, "data") and not isinstance(payload, dict):
        rows = payload.data
    elif isinstance(payload, dict) and "data" in payload:
        rows = payload["data"]
    else:
        rows = payload
    return [row["id"] if isinstance(row, dict) else row.id for row in (rows or [])]


# ===========================================================================
# 1. Tenant isolation on LIST endpoints
# ===========================================================================


@pytest.mark.api
@pytest.mark.parametrize(
    "module_name,func_name,table,default_limit",
    LIST_ROUTES,
    ids=[r[0] for r in LIST_ROUTES],
)
@pytest.mark.asyncio
async def test_list_endpoint_scopes_query_to_current_user(
    monkeypatch, fake_user, module_name, func_name, table, default_limit
):
    """Every list endpoint MUST chain .eq("user_id", caller) on the right table."""
    client = make_client(**{table: seed_rows(table)})
    module = install(monkeypatch, module_name, client)

    # NOTE: these route functions are called directly, bypassing FastAPI, so the
    # `Query(20, ge=1, le=100)` defaults are `fastapi.params.Query` objects,
    # not ints -- `offset + limit - 1` would raise TypeError. Pagination
    # arguments must always be passed explicitly.
    await getattr(module, func_name)(current_user=fake_user, limit=default_limit, offset=0)

    log = client.log

    # (1) the route read the table we expect -- a typo'd table name fails here
    assert table in log.tables, (
        f"{module_name}.{func_name} never called from_({table!r}); " f"it called from_() with {log.tables!r}"
    )

    # (2) the ownership predicate is present, with the CALLER's id as its value
    eq_calls = log.find(table, "eq")
    assert ("user_id", CALLER) in [(c.args[0], c.args[1]) for c in eq_calls], (
        f"{module_name}.{func_name} did not scope by user_id.\n" f"Recorded calls:\n{log!r}"
    )

    # (3) it must be an equality on user_id, not something else entirely
    user_id_eqs = [c for c in eq_calls if c.args and c.args[0] == "user_id"]
    assert user_id_eqs, f"no .eq() call on the user_id column at all:\n{log!r}"
    for call in user_id_eqs:
        assert call.args[1] == CALLER, (
            f".eq('user_id', {call.args[1]!r}) does not match the authenticated " f"user {CALLER!r}"
        )

    # (4) behavioural half: the response must contain only the caller's rows
    result = await getattr(module, func_name)(current_user=fake_user, limit=default_limit, offset=0)
    assert ids_in(result) == ["row-mine"], f"{module_name}.{func_name} leaked another tenant's rows: {ids_in(result)}"


@pytest.mark.api
@pytest.mark.parametrize(
    "module_name,func_name,table,default_limit",
    LIST_ROUTES,
    ids=[r[0] for r in LIST_ROUTES],
)
@pytest.mark.asyncio
async def test_list_endpoint_reads_exactly_one_table(
    monkeypatch, fake_user, module_name, func_name, table, default_limit
):
    """A list endpoint must not touch any table other than its own."""
    client = make_client(**{table: seed_rows(table)})
    module = install(monkeypatch, module_name, client)

    await getattr(module, func_name)(current_user=fake_user, limit=default_limit, offset=0)

    unexpected = set(client.log.tables) - {table}
    assert not unexpected, (
        f"{module_name}.{func_name} queried unexpected table(s) {sorted(unexpected)}.\n"
        f"Recorded calls:\n{client.log!r}"
    )


# ===========================================================================
# 2. Pagination contract
# ===========================================================================


@pytest.mark.api
@pytest.mark.parametrize(
    "module_name,func_name,table,default_limit",
    LIST_ROUTES,
    ids=[r[0] for r in LIST_ROUTES],
)
@pytest.mark.asyncio
async def test_list_endpoint_paginates_with_offset_and_limit(
    monkeypatch, fake_user, module_name, func_name, table, default_limit
):
    """`.range(offset, offset + limit - 1)` must be passed through verbatim."""
    client = make_client(**{table: seed_rows(table)})
    module = install(monkeypatch, module_name, client)

    await getattr(module, func_name)(current_user=fake_user, limit=7, offset=14)

    ranges = client.log.find(table, "range")
    assert ranges, f"{module_name}.{func_name} never called .range():\n{client.log!r}"
    assert (14, 20) in [(c.args[0], c.args[1]) for c in ranges], (
        f"expected .range(14, 20) for offset=14 limit=7, got " f"{[c.args for c in ranges]}"
    )


@pytest.mark.api
@pytest.mark.asyncio
async def test_tasks_pagination_is_honoured_end_to_end(monkeypatch, fake_user):
    """Beyond call tracing: the page the route returns must honour limit/offset."""
    rows = [task_row(f"t{i}", CALLER, f"T{i}") for i in range(10)]
    client = RecordingSupabase({"tasks": rows})
    module = install(monkeypatch, "app.api.tasks", client)

    payload = await module.get_tasks(current_user=fake_user, limit=3, offset=6)

    assert ids_in(payload) == ["t6", "t7", "t8"]
    assert payload.limit == 3
    assert payload.offset == 6
    assert payload.total == 10


# ===========================================================================
# 3. Detail endpoints: IDOR protection
# ===========================================================================


@pytest.mark.api
@pytest.mark.parametrize(
    "module_name,func_name,table,id_kwarg",
    DETAIL_ROUTES,
    ids=[r[0] for r in DETAIL_ROUTES],
)
@pytest.mark.asyncio
async def test_detail_endpoint_scopes_by_both_id_and_user(
    monkeypatch, fake_user, module_name, func_name, table, id_kwarg
):
    """`GET /{id}` must filter on id AND user_id -- the IDOR contract."""
    client = make_client(**{table: seed_rows(table)})
    module = install(monkeypatch, module_name, client)

    try:
        await getattr(module, func_name)(**{id_kwarg: "row-mine"}, current_user=fake_user)
    except Exception:
        # A 404 for a row the seeded schema cannot satisfy is fine; what matters
        # is the recorded call trace, asserted below.
        pass

    log = client.log
    eq_pairs = [(c.args[0], c.args[1]) for c in log.find(table, "eq")]

    assert ("user_id", CALLER) in eq_pairs, (
        f"{module_name}.{func_name} looks up a row by id WITHOUT checking "
        f"ownership -- classic IDOR / cross-tenant read.\nRecorded calls:\n{log!r}"
    )
    assert any(
        column == "id" for column, _ in eq_pairs
    ), f"{module_name}.{func_name} never filtered on the id column:\n{log!r}"


@pytest.mark.api
@pytest.mark.asyncio
async def test_detail_endpoint_hides_other_tenants_rows(monkeypatch, fake_user):
    """Asking for the other tenant's id must NOT return their row."""
    client = RecordingSupabase({"tasks": [task_row("task-secret", OTHER_USER, "Secret")]})
    module = install(monkeypatch, "app.api.tasks", client)

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as excinfo:
        await module.get_task("task-secret", current_user=fake_user)

    assert excinfo.value.status_code == 404, "another tenant's task was returned instead of 404"


# ===========================================================================
# 4. Mutation endpoints: writes must be ownership-scoped too
# ===========================================================================


@pytest.mark.api
@pytest.mark.parametrize(
    "module_name,table,delete_name,update_name,id_kwarg",
    [
        ("app.api.tasks", "tasks", "delete_task", "update_task", "task_id"),
        ("app.api.courses", "courses", "delete_course", "update_course", "course_id"),
        ("app.api.goals", "goals", "delete_goal", "update_goal", "goal_id"),
        ("app.api.habits", "habits", "delete_habit", "update_habit", "habit_id"),
        ("app.api.income", "income_entries", "delete_income", "update_income", "income_id"),
        (
            "app.api.opportunities",
            "opportunities",
            "delete_opportunity",
            "update_opportunity",
            # NB: this router names the path param `opp_id`, not `opportunity_id`
            # (apps/api/app/api/opportunities.py:81).
            "opp_id",
        ),
        ("app.api.projects", "projects", "delete_project", "update_project", "project_id"),
        ("app.api.ideas", "ideas", "delete_idea", "update_idea", "idea_id"),
        ("app.api.resources", "resources", "delete_resource", "update_resource", "resource_id"),
        ("app.api.time", "time_entries", "delete_time_entry", "update_time_entry", "entry_id"),
        ("app.api.memory", "memory", "delete_memory", "update_memory", "memory_id"),
    ],
    ids=[
        "app.api.tasks",
        "app.api.courses",
        "app.api.goals",
        "app.api.habits",
        "app.api.income",
        "app.api.opportunities",
        "app.api.projects",
        "app.api.ideas",
        "app.api.resources",
        "app.api.time",
        "app.api.memory",
    ],
)
@pytest.mark.asyncio
async def test_delete_endpoint_scopes_to_current_user(
    monkeypatch, fake_user, module_name, table, delete_name, update_name, id_kwarg
):
    """DELETE must be `from_(table).delete().eq(id).eq(user_id)` -- not id alone.

    A delete that filters only on id lets any authenticated user delete any
    other user's row.
    """
    client = make_client(**{table: seed_rows(table)})
    module = install(monkeypatch, module_name, client)

    try:
        await getattr(module, delete_name)(**{id_kwarg: "row-mine"}, current_user=fake_user)
    except Exception:
        pass

    log = client.log
    eq_pairs = [(c.args[0], c.args[1]) for c in log.find(table, "eq")]

    assert log.find(table, "delete"), f"{module_name}.{delete_name} never called .delete()"
    assert ("user_id", CALLER) in eq_pairs, (
        f"{module_name}.{delete_name} deletes without an ownership filter -- "
        f"any user can delete any row.\nRecorded calls:\n{log!r}"
    )


# ===========================================================================
# 5. Exact call-sequence assertions (regression fingerprints)
# ===========================================================================


@pytest.mark.api
@pytest.mark.asyncio
async def test_tasks_list_emits_count_query_then_paginated_data_query(monkeypatch, fake_user):
    """Pin the exact two-query shape of GET /api/v1/tasks/."""
    client = make_client(tasks=TWO_TENANT_TASK_ROWS)
    module = install(monkeypatch, "app.api.tasks", client)

    await module.get_tasks(current_user=fake_user, limit=5, offset=0)

    assert client.log.sequence() == [
        ("from_", ("tasks",)),
        ("select", ("*",)),
        ("eq", ("user_id", CALLER)),
        ("execute", ()),
        ("from_", ("tasks",)),
        (
            "select",
            (
                "id, user_id, title, status, priority, due_date, created_at, "
                "updated_at, completed_at, estimated_minutes, category, "
                "description, project_id, goal_id, is_recurring, "
                "recurring_frequency, dependency_id, missed_count",
            ),
        ),
        ("eq", ("user_id", CALLER)),
        ("range", (0, 4)),
        ("execute", ()),
    ], f"unexpected call sequence:\n{client.log!r}"


@pytest.mark.api
@pytest.mark.asyncio
async def test_memory_list_orders_by_created_at_descending(monkeypatch, fake_user):
    """GET /api/v1/memory/ must order newest-first."""
    client = make_client(memory=TWO_TENANT_ROWS)
    module = install(monkeypatch, "app.api.memory", client)

    await module.list_memories(current_user=fake_user, limit=50, offset=0)

    orders = client.log.find("memory", "order")
    assert orders, f"memory list does not order its results:\n{client.log!r}"
    call = orders[0]
    assert call.args[0] == "created_at"
    assert (
        call.kwargs.get("ascending") is False or call.kwargs.get("desc") is True
    ), f"memory list must be newest-first, got kwargs={call.kwargs}"


# ===========================================================================
# 6. Harness self-tests -- prove the double can actually fail
# ===========================================================================


@pytest.mark.api
def test_recorder_detects_a_missing_user_id_filter():
    """Sanity check on the harness: an unscoped builder trips the assertion.

    Without this, a bug in `assert` logic above could make the whole module
    vacuously pass -- the exact failure mode this file exists to eliminate.
    """
    log = CallLog()
    client = RecordingSupabase({"tasks": TWO_TENANT_TASK_ROWS})
    builder = client.from_("tasks")
    builder.select("*").execute()  # deliberately no .eq("user_id", ...)

    eq_pairs = [(c.args[0], c.args[1]) for c in log.find("tasks", "eq")]
    assert ("user_id", CALLER) not in eq_pairs, "harness failed to notice the missing filter"

    # ...and the leak is visible in the returned rows.
    unscoped = RecordingSupabase({"tasks": TWO_TENANT_TASK_ROWS})
    rows = unscoped.from_("tasks").select("*").execute().data
    assert {r["user_id"] for r in rows} == {CALLER, OTHER_USER}


@pytest.mark.api
def test_recorder_detects_a_wrong_table_name():
    """`from_` must remember which table it was asked for."""
    client = RecordingSupabase({"tasks": TWO_TENANT_TASK_ROWS})
    client.from_("tsaks")  # typo
    assert "tsaks" in client.log.tables
    assert "tasks" not in client.log.tables


@pytest.mark.api
def test_recorder_detects_broken_pagination():
    """`.range()` must be observable; a dropped/incorrect range changes the rows."""
    rows = [{"id": f"t{i}", "user_id": CALLER} for i in range(10)]

    client = RecordingSupabase({"tasks": rows})
    page = client.from_("tasks").select("*").eq("user_id", CALLER).range(6, 8).execute()
    assert [r["id"] for r in page.data] == ["t6", "t7", "t8"]
    assert client.log.find("tasks", "range")[0].args == (6, 8)

    # Dropping .range() returns the whole table -- observably different.
    unpaged = client.from_("tasks").select("*").eq("user_id", CALLER).execute()
    assert len(unpaged.data) == 10
    assert len(page.data) == 3
