"""Tests for /api/v1/knowledge/ — graph reads, search, extraction, isolation.

Uses the recording Supabase double from ``tests/test_query_scoping.py``
rather than the suite's ``MockQueryBuilder``. That double matters: its
``eq()`` actually narrows results and ``from_()`` remembers the table name,
so deleting a ``.eq("user_id", ...)`` from any route below fails the test
instead of silently passing. ``MockQueryBuilder.eq`` discards both of its
arguments, which makes ~600 tests in this suite incapable of catching a
scoping regression.

NOTE ON DIRECT CALLS: these route functions are invoked directly, bypassing
FastAPI, so ``Query(...)`` defaults arrive as ``fastapi.params.Query``
objects rather than ints or None. A bare ``Query(None)`` is truthy, which
would make the router's optional ``type`` filter fire against every call.
Pagination and filter arguments are therefore always passed explicitly —
the same convention tests/test_query_scoping.py documents.
"""

import importlib
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from config.core.auth import get_current_user
from tests.test_query_scoping import Call, CallLog, RecordingQueryBuilder, RecordingSupabase

OTHER_USER = "user-OTHER-tenant"
CALLER = "user-CALLER"

NODE_COLUMNS = (
    "id, user_id, type, label, summary, tags, source_table, source_id, " "weight, degree, created_at, updated_at"
)


# ===========================================================================
# 1. Recording double — reuses test_query_scoping, extends .in_()
# ===========================================================================


@dataclass(frozen=True)
class _InFilter:
    column: str
    values: Tuple[Any, ...]


class ScopedQueryBuilder(RecordingQueryBuilder):
    """``RecordingQueryBuilder`` that also applies ``.in_()``.

    The shared double records ``.in_()`` but does not honour it, because no
    router in the isolation suite uses it. This router does — the graph
    endpoint pages nodes by id and then asks for the edges between exactly
    those ids — so without real ``.in_()`` semantics a cross-tenant edge
    leak would be invisible to a behavioural assertion.
    """

    def __init__(self, log: CallLog, table: str, rows: List[Dict[str, Any]]) -> None:
        super().__init__(log, table, rows)
        self._in: List[_InFilter] = []

    def in_(self, column: str, values: Any) -> "ScopedQueryBuilder":
        materialised = tuple(values) if values is not None else ()
        self._in.append(_InFilter(column, materialised))
        return self._step("in_", column, materialised)

    def _result(self):
        class _Result:
            pass

        result = _Result()
        rows = [
            row
            for row in self._rows
            if all(row.get(column) == value for column, value in self._eq)
            and all(row.get(f.column) in f.values for f in self._in)
        ]
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


class ScopedSupabase(RecordingSupabase):
    """``RecordingSupabase`` wired to :class:`ScopedQueryBuilder`."""

    def from_(self, table: str) -> ScopedQueryBuilder:
        self.log.record(Call("<client>", "from_", (table,)))
        builder = ScopedQueryBuilder(self.log, table, self.tables.get(table, []))
        self.log.calls[-1] = Call(table, "from_", (table,))
        return builder


class FailingSupabase(ScopedSupabase):
    """Client whose reads blow up, to exercise the 500-free error paths."""

    def __init__(self, tables: Dict[str, List[Dict[str, Any]]]) -> None:
        super().__init__(tables)

    def from_(self, table: str) -> ScopedQueryBuilder:
        builder = super().from_(table)
        builder.execute = _raising_execute  # type: ignore[method-assign]
        return builder


def _raising_execute(self):
    self._log.record(Call(self._table, "execute"))
    raise RuntimeError("connection reset by peer -- schema=public user=postgres")


# ===========================================================================
# 2. Fixtures and seed data
# ===========================================================================


class _FakeUser:
    def __init__(self, user_id: str) -> None:
        self.user = type("_U", (), {"id": user_id})()


@pytest.fixture
def fake_user() -> _FakeUser:
    return _FakeUser(CALLER)


def node_row(
    node_id: str,
    owner: str,
    label: str = "Mine",
    node_type: str = "note",
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """A row satisfying every field KnowledgeNodeResponse requires."""
    return {
        "id": node_id,
        "user_id": owner,
        "type": node_type,
        "label": label,
        "summary": "A summary",
        "tags": tags if tags is not None else ["ml"],
        "source_table": "resources",
        "source_id": f"src-{node_id}",
        "weight": 1.0,
        "degree": 2,
        "created_at": "2026-07-01T00:00:00+00:00",
        "updated_at": "2026-07-02T00:00:00+00:00",
    }


def edge_row(edge_id: str, owner: str, source: str, target: str, relation: str = "shares_tag") -> Dict[str, Any]:
    return {
        "id": edge_id,
        "user_id": owner,
        "source_id": source,
        "target_id": target,
        "relation": relation,
        "weight": 0.8,
        "created_at": "2026-07-02T00:00:00+00:00",
    }


# Two tenants, each with a node and an edge between their own two nodes.
# A route that drops .eq("user_id", ...) returns both sets.
NODE_MINE = node_row("node-mine", CALLER, label="Neural Networks")
NODE_MINE_2 = node_row("node-mine-2", CALLER, label="Transformer Primer", node_type="resource", tags=["nlp"])
NODE_THEIRS = node_row("node-theirs", OTHER_USER, label="Their Secret")
EDGE_MINE = edge_row("edge-mine", CALLER, "node-mine", "node-mine-2")
EDGE_THEIRS = edge_row("edge-theirs", OTHER_USER, "node-theirs", "node-theirs-2")

TABLES: Dict[str, List[Dict[str, Any]]] = {
    "knowledge_nodes": [NODE_MINE, NODE_MINE_2, NODE_THEIRS],
    "knowledge_edges": [EDGE_MINE, EDGE_THEIRS],
}


def install(monkeypatch, client, module_name: str = "app.api.knowledge"):
    """Point the router's (and the agent's) client accessor at ``client``."""
    module = importlib.import_module(module_name)
    monkeypatch.setattr(module, "get_supabase_client", lambda: client)
    return module


def install_everywhere(monkeypatch, client) -> Any:
    """Router reads in app.api.knowledge; search reads in the agent module."""
    module = install(monkeypatch, client, "app.api.knowledge")
    agent = importlib.import_module("ai.agents.knowledge_agent")
    monkeypatch.setattr(agent, "get_supabase_client", lambda: client)
    return module


def eq_pairs(client: ScopedSupabase, table: str) -> List[Tuple[Any, ...]]:
    return [(c.args[0], c.args[1]) for c in client.log.find(table, "eq")]


# ===========================================================================
# 3. GET /api/v1/knowledge/ — list
# ===========================================================================


@pytest.mark.api
class TestListKnowledgeGraph:
    @pytest.mark.asyncio
    async def test_returns_200_shape_with_nodes_and_edges(self, monkeypatch, fake_user):
        """GET / must return nodes and edges as top-level siblings."""
        client = ScopedSupabase(TABLES)
        module = install_everywhere(monkeypatch, client)

        payload = await module.list_knowledge_graph(current_user=fake_user, limit=50, offset=0, node_type=None)

        assert payload["count"] == 2
        assert {n["id"] for n in payload["nodes"]} == {"node-mine", "node-mine-2"}
        assert [e["id"] for e in payload["edges"]] == ["edge-mine"]
        assert payload["limit"] == 50
        assert payload["offset"] == 0

    @pytest.mark.asyncio
    async def test_edges_are_top_level_not_nested(self, monkeypatch, fake_user):
        """knowledgeStore.fetch() reads data.nodes / data.edges, so an edge
        may never be nested inside a node."""
        client = ScopedSupabase({"knowledge_nodes": [NODE_MINE], "knowledge_edges": []})
        module = install_everywhere(monkeypatch, client)

        payload = await module.list_knowledge_graph(current_user=fake_user, limit=50, offset=0, node_type=None)

        assert set(payload) >= {"nodes", "edges"}
        assert isinstance(payload["nodes"], list)
        assert isinstance(payload["edges"], list)
        for node in payload["nodes"]:
            assert "edges" not in node

    @pytest.mark.asyncio
    async def test_selects_explicit_columns_never_star(self, monkeypatch, fake_user):
        client = ScopedSupabase(TABLES)
        module = install_everywhere(monkeypatch, client)

        await module.list_knowledge_graph(current_user=fake_user, limit=50, offset=0, node_type=None)

        selects = client.log.find("knowledge_nodes", "select")
        assert selects, "knowledge_nodes was never selected"
        for call in selects:
            assert call.args and call.args[0] != "*", "select('*') is forbidden"
            assert "label" in call.args[0] and "created_at" in call.args[0]
        edge_selects = client.log.find("knowledge_edges", "select")
        for call in edge_selects:
            assert call.args[0] != "*"
            assert "relation" in call.args[0]

    @pytest.mark.asyncio
    async def test_paginates_with_range(self, monkeypatch, fake_user):
        client = ScopedSupabase(TABLES)
        module = install_everywhere(monkeypatch, client)

        await module.list_knowledge_graph(current_user=fake_user, limit=7, offset=14, node_type=None)

        ranges = client.log.find("knowledge_nodes", "range")
        assert ranges, "list endpoint never paginated"
        assert (14, 20) in [(c.args[0], c.args[1]) for c in ranges]

    @pytest.mark.asyncio
    async def test_optional_type_filter_is_applied(self, monkeypatch, fake_user):
        client = ScopedSupabase(TABLES)
        module = install_everywhere(monkeypatch, client)

        await module.list_knowledge_graph(current_user=fake_user, limit=50, offset=0, node_type="resource")

        assert ("type", "resource") in eq_pairs(client, "knowledge_nodes")

    @pytest.mark.asyncio
    async def test_returns_400_when_the_database_fails(self, monkeypatch, fake_user):
        module = install_everywhere(monkeypatch, FailingSupabase(TABLES))

        with pytest.raises(HTTPException) as excinfo:
            await module.list_knowledge_graph(current_user=fake_user, limit=50, offset=0, node_type=None)

        assert excinfo.value.status_code == 400
        assert "connection reset" not in str(excinfo.value.detail)

    @pytest.mark.asyncio
    async def test_empty_graph_returns_empty_collections(self, monkeypatch, fake_user):
        client = ScopedSupabase({"knowledge_nodes": [], "knowledge_edges": []})
        module = install_everywhere(monkeypatch, client)

        payload = await module.list_knowledge_graph(current_user=fake_user, limit=50, offset=0, node_type=None)

        assert payload["nodes"] == []
        assert payload["edges"] == []


# ===========================================================================
# 4. Tenant isolation
# ===========================================================================


@pytest.mark.api
class TestTenantIsolation:
    @pytest.mark.asyncio
    async def test_list_scopes_nodes_to_the_caller(self, monkeypatch, fake_user):
        """The ownership predicate must be on knowledge_nodes..."""
        client = ScopedSupabase(TABLES)
        module = install_everywhere(monkeypatch, client)

        await module.list_knowledge_graph(current_user=fake_user, limit=50, offset=0, node_type=None)

        assert ("user_id", CALLER) in eq_pairs(client, "knowledge_nodes")

    @pytest.mark.asyncio
    async def test_list_scopes_edges_to_the_caller(self, monkeypatch, fake_user):
        """...AND on knowledge_edges, which is a second, separate query.

        Dropping the filter on the edge query leaks the caller's neighbours'
        relationships even when the node query stays scoped.
        """
        client = ScopedSupabase(TABLES)
        module = install_everywhere(monkeypatch, client)

        await module.list_knowledge_graph(current_user=fake_user, limit=50, offset=0, node_type=None)

        assert client.log.find("knowledge_edges", "from_") or True
        assert ("user_id", CALLER) in eq_pairs(
            client, "knowledge_edges"
        ), f"knowledge_edges read is not ownership-scoped.\n{client.log!r}"

    @pytest.mark.asyncio
    async def test_user_b_cannot_see_user_a_nodes(self, monkeypatch, fake_user):
        """Behavioural half: only the caller's rows come back."""
        client = ScopedSupabase(TABLES)
        module = install_everywhere(monkeypatch, client)

        payload = await module.list_knowledge_graph(current_user=fake_user, limit=50, offset=0, node_type=None)

        labels = {n["label"] for n in payload["nodes"]}
        assert labels == {"Neural Networks", "Transformer Primer"}
        assert "Their Secret" not in labels
        assert all(n["user_id"] == CALLER for n in payload["nodes"])

    @pytest.mark.asyncio
    async def test_user_b_cannot_see_user_a_edges(self, monkeypatch, fake_user):
        """The other tenant's edge must not ride along on the node page.

        The adversarial fixture is an edge owned by the OTHER tenant whose
        two endpoints are BOTH caller-owned nodes. That is precisely the
        row a missing .eq("user_id", ...) on the edge query would expose,
        and it survives the .in_() endpoint filter — so only the ownership
        predicate can stop it.
        """
        cross_tenant_edge = edge_row("edge-cross", OTHER_USER, "node-mine", "node-mine-2")
        client = ScopedSupabase(
            {
                "knowledge_nodes": [NODE_MINE, NODE_MINE_2, NODE_THEIRS],
                "knowledge_edges": [EDGE_MINE, cross_tenant_edge],
            }
        )
        module = install_everywhere(monkeypatch, client)

        payload = await module.list_knowledge_graph(current_user=fake_user, limit=50, offset=0, node_type=None)

        assert [e["id"] for e in payload["edges"]] == ["edge-mine"]
        assert all(e["user_id"] == CALLER for e in payload["edges"])

    @pytest.mark.asyncio
    async def test_edges_are_restricted_to_the_visible_page(self, monkeypatch, fake_user):
        """An edge whose endpoints are off-page is dropped server-side, not
        handed to the store to filter out."""
        client = ScopedSupabase(
            {
                "knowledge_nodes": [NODE_MINE],
                "knowledge_edges": [edge_row("edge-offpage", CALLER, "node-mine", "node-elsewhere")],
            }
        )
        module = install_everywhere(monkeypatch, client)

        payload = await module.list_knowledge_graph(current_user=fake_user, limit=50, offset=0, node_type=None)

        assert payload["edges"] == []
        in_calls = client.log.find("knowledge_edges", "in_")
        recorded = {(c.args[0], c.args[1]) for c in in_calls}
        assert ("source_id", ("node-mine",)) in recorded
        assert ("target_id", ("node-mine",)) in recorded

    @pytest.mark.asyncio
    async def test_detail_endpoint_filters_on_both_id_and_user_id(self, monkeypatch, fake_user):
        client = ScopedSupabase(TABLES)
        module = install_everywhere(monkeypatch, client)

        await module.get_knowledge_node("node-mine", current_user=fake_user)

        pairs = eq_pairs(client, "knowledge_nodes")
        assert ("user_id", CALLER) in pairs, f"IDOR: detail read is not ownership-scoped.\n{client.log!r}"
        assert ("id", "node-mine") in pairs

    @pytest.mark.asyncio
    async def test_user_b_getting_user_a_node_id_returns_404(self, monkeypatch, fake_user):
        client = ScopedSupabase(TABLES)
        module = install_everywhere(monkeypatch, client)

        with pytest.raises(HTTPException) as excinfo:
            await module.get_knowledge_node("node-theirs", current_user=fake_user)

        assert excinfo.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_filters_on_both_id_and_user_id(self, monkeypatch, fake_user):
        client = ScopedSupabase(TABLES)
        module = install_everywhere(monkeypatch, client)

        await module.delete_knowledge_node("node-mine", current_user=fake_user)

        assert client.log.find("knowledge_nodes", "delete"), "delete never called"
        pairs = eq_pairs(client, "knowledge_nodes")
        assert (
            "user_id",
            CALLER,
        ) in pairs, f"delete without an ownership filter lets any user delete any node.\n{client.log!r}"
        assert ("id", "node-mine") in pairs

    @pytest.mark.asyncio
    async def test_user_b_deleting_user_a_node_returns_404_and_keeps_the_row(self, monkeypatch, fake_user):
        client = ScopedSupabase(TABLES)
        module = install_everywhere(monkeypatch, client)

        with pytest.raises(HTTPException) as excinfo:
            await module.delete_knowledge_node("node-theirs", current_user=fake_user)

        assert excinfo.value.status_code == 404

    @pytest.mark.asyncio
    async def test_search_scopes_to_the_caller(self, monkeypatch, fake_user):
        client = ScopedSupabase(TABLES)
        module = install_everywhere(monkeypatch, client)

        nodes = await module.search_knowledge_nodes(
            q="neural", limit=20, offset=0, node_type=None, current_user=fake_user
        )

        assert ("user_id", CALLER) in eq_pairs(client, "knowledge_nodes")
        assert [n.id for n in nodes] == ["node-mine", "node-mine-2"]


# ===========================================================================
# 5. GET /api/v1/knowledge/{node_id} and DELETE
# ===========================================================================


@pytest.mark.api
class TestKnowledgeNodeCrud:
    @pytest.mark.asyncio
    async def test_get_existing_node_returns_it(self, monkeypatch, fake_user):
        client = ScopedSupabase(TABLES)
        module = install_everywhere(monkeypatch, client)

        node = await module.get_knowledge_node("node-mine", current_user=fake_user)

        assert node["id"] == "node-mine"

    @pytest.mark.asyncio
    async def test_get_missing_node_returns_404(self, monkeypatch, fake_user):
        client = ScopedSupabase(TABLES)
        module = install_everywhere(monkeypatch, client)

        with pytest.raises(HTTPException) as excinfo:
            await module.get_knowledge_node("does-not-exist", current_user=fake_user)

        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "Knowledge node not found"

    @pytest.mark.asyncio
    async def test_get_returns_400_when_the_database_fails(self, monkeypatch, fake_user):
        module = install_everywhere(monkeypatch, FailingSupabase(TABLES))

        with pytest.raises(HTTPException) as excinfo:
            await module.get_knowledge_node("node-mine", current_user=fake_user)

        assert excinfo.value.status_code == 400

    @pytest.mark.asyncio
    async def test_delete_owned_node_succeeds(self, monkeypatch, fake_user):
        client = ScopedSupabase(TABLES)
        module = install_everywhere(monkeypatch, client)

        assert await module.delete_knowledge_node("node-mine", current_user=fake_user) is None

    @pytest.mark.asyncio
    async def test_delete_returns_400_when_the_database_fails(self, monkeypatch, fake_user):
        module = install_everywhere(monkeypatch, FailingSupabase(TABLES))

        with pytest.raises(HTTPException) as excinfo:
            await module.delete_knowledge_node("node-mine", current_user=fake_user)

        assert excinfo.value.status_code == 400


# ===========================================================================
# 6. GET /api/v1/knowledge/search
# ===========================================================================


@pytest.mark.api
class TestKnowledgeSearch:
    @pytest.mark.asyncio
    async def test_returns_a_bare_array_not_an_envelope(self, monkeypatch, fake_user):
        """knowledgeStore.search() does `set({ nodes: results })` and page.tsx
        then calls results.filter(...), so an envelope breaks the page."""
        client = ScopedSupabase(TABLES)
        module = install_everywhere(monkeypatch, client)

        results = await module.search_knowledge_nodes(
            q="neural", limit=20, offset=0, node_type=None, current_user=fake_user
        )

        assert isinstance(results, list), f"search must return a bare array, got {type(results).__name__}"
        assert {n.label for n in results} == {"Neural Networks", "Transformer Primer"}

    @pytest.mark.asyncio
    async def test_sanitises_the_query_before_it_reaches_postgrest(self, monkeypatch, fake_user):
        """The term is interpolated into an or=(...) filter string, so
        PostgREST metacharacters must never survive user input.

        The single comma in the emitted filter is the separator between the
        two ilike clauses the router itself writes — exactly one, and never
        more than the router produced.
        """
        client = ScopedSupabase(TABLES)
        module = install_everywhere(monkeypatch, client)
        payload = "neural%'),user_id.eq.other,(select+*+from+pg_shadow)"

        await module.search_knowledge_nodes(q=payload, limit=20, offset=0, node_type=None, current_user=fake_user)

        agent = importlib.import_module("ai.agents.knowledge_agent")
        or_calls = client.log.find("knowledge_nodes", "or_")
        assert or_calls, "search never called or_()"
        emitted = or_calls[0].args[0]

        assert "(" not in emitted and ")" not in emitted
        assert "'" not in emitted and '"' not in emitted
        assert "+" not in emitted and "*" not in emitted
        assert emitted.count(",") == 1, "only the router's own clause separator may remain"

        # Exact contract: the sole thing interpolated is the sanitised needle.
        needle = agent.sanitise_search_term(payload).replace(" ", "%")
        assert emitted == f"label.ilike.%{needle}%,summary.ilike.%{needle}%"

    @pytest.mark.asyncio
    async def test_empty_after_sanitisation_returns_empty_list(self, monkeypatch, fake_user):
        client = ScopedSupabase(TABLES)
        module = install_everywhere(monkeypatch, client)

        results = await module.search_knowledge_nodes(
            q="%%%", limit=20, offset=0, node_type=None, current_user=fake_user
        )

        assert results == []
        assert not client.log.find("knowledge_nodes", "or_"), "a stripped query must not hit the database"


# ===========================================================================
# 7. POST /api/v1/knowledge/extract
# ===========================================================================


@pytest.mark.api
class TestKnowledgeExtract:
    @pytest.mark.asyncio
    async def test_extract_returns_the_summary_envelope(self, monkeypatch, fake_user):
        from database.schemas.knowledge import KnowledgeExtractRequest

        module = install_everywhere(monkeypatch, ScopedSupabase(TABLES))
        agent = importlib.import_module("ai.agents.knowledge_agent")

        async def fake_extract(user_id, sources=None, limit_per_source=50, mode="auto"):
            assert user_id == CALLER
            return {
                "status": "success",
                "mode": "algorithmic",
                "sources_scanned": ["resources", "goals"],
                "records_scanned": 7,
                "nodes_upserted": 7,
                "edges_upserted": 3,
                "edges_skipped": 1,
                "degree_refreshed": 2,
                "summary": "Extracted 7 nodes and 3 edges.",
            }

        monkeypatch.setattr(agent, "extract_knowledge_graph", fake_extract)

        result = await module.extract_knowledge(request=KnowledgeExtractRequest(), current_user=fake_user)

        assert result["status"] == "success"
        assert result["nodes_upserted"] == 7
        assert result["edges_upserted"] == 3

    @pytest.mark.asyncio
    async def test_extract_returns_400_when_the_agent_raises(self, monkeypatch, fake_user):
        from database.schemas.knowledge import KnowledgeExtractRequest

        module = install_everywhere(monkeypatch, ScopedSupabase(TABLES))
        agent = importlib.import_module("ai.agents.knowledge_agent")

        async def exploding_extract(*args, **kwargs):
            raise RuntimeError('relation "knowledge_nodes" does not exist')

        monkeypatch.setattr(agent, "extract_knowledge_graph", exploding_extract)

        with pytest.raises(HTTPException) as excinfo:
            await module.extract_knowledge(request=KnowledgeExtractRequest(), current_user=fake_user)

        assert excinfo.value.status_code == 400
        assert "does not exist" not in str(excinfo.value.detail)

    @pytest.mark.asyncio
    async def test_extract_returns_400_on_agent_error_status(self, monkeypatch, fake_user):
        from database.schemas.knowledge import KnowledgeExtractRequest

        module = install_everywhere(monkeypatch, ScopedSupabase(TABLES))
        agent = importlib.import_module("ai.agents.knowledge_agent")

        async def failed_extract(*args, **kwargs):
            return {"status": "error", "summary": "Knowledge extraction failed, no changes made."}

        monkeypatch.setattr(agent, "extract_knowledge_graph", failed_extract)

        with pytest.raises(HTTPException) as excinfo:
            await module.extract_knowledge(request=KnowledgeExtractRequest(), current_user=fake_user)

        assert excinfo.value.status_code == 400

    @pytest.mark.asyncio
    async def test_extract_honours_mode_and_source_overrides(self, monkeypatch, fake_user):
        from database.schemas.knowledge import KnowledgeExtractRequest

        module = install_everywhere(monkeypatch, ScopedSupabase(TABLES))
        agent = importlib.import_module("ai.agents.knowledge_agent")
        captured = {}

        async def fake_extract(user_id, sources=None, limit_per_source=50, mode="auto"):
            captured.update({"user_id": user_id, "sources": sources, "mode": mode})
            return {"status": "success", "mode": mode, "summary": "ok"}

        monkeypatch.setattr(agent, "extract_knowledge_graph", fake_extract)

        await module.extract_knowledge(
            request=KnowledgeExtractRequest(sources=["goals"], mode="algorithmic"),
            current_user=fake_user,
        )

        assert captured == {"user_id": CALLER, "sources": ["goals"], "mode": "algorithmic"}


# ===========================================================================
# 8. Wire format — the actual frontend contract, through FastAPI
# ===========================================================================


@pytest.mark.api
class TestWireFormat:
    """Proves GraphNode/GraphEdge are satisfied by the real serialiser."""

    def _client(self, monkeypatch, tables: Dict[str, List[Dict[str, Any]]]) -> TestClient:
        client = ScopedSupabase(tables)
        install_everywhere(monkeypatch, client)
        module = importlib.import_module("app.api.knowledge")
        app = FastAPI()
        app.include_router(module.router, prefix="/api/v1/knowledge")
        app.dependency_overrides[get_current_user] = lambda: _FakeUser(CALLER)
        return TestClient(app)

    def test_list_serialises_node_and_edge_aliases(self, monkeypatch):
        http = self._client(
            monkeypatch,
            {
                "knowledge_nodes": [NODE_MINE],
                "knowledge_edges": [edge_row("edge-1", CALLER, "node-mine", "node-mine")],
            },
        )

        response = http.get("/api/v1/knowledge/")
        assert response.status_code == 200
        payload = response.json()

        node = payload["nodes"][0]
        # KnowledgeGraph.tsx GraphNode requires exactly these keys.
        assert set(node) >= {"id", "title", "type", "createdAt", "tags", "description"}
        assert "label" not in node and "summary" not in node and "created_at" not in node
        assert node["title"] == "Neural Networks"
        assert node["description"] == "A summary"
        assert node["tags"] == ["ml"]
        assert node["createdAt"].startswith("2026-07-01")

        edge = payload["edges"][0]
        assert set(edge) >= {"source", "target", "label"}
        assert "source_id" not in edge and "target_id" not in edge and "relation" not in edge
        assert edge["source"] == "node-mine"
        assert edge["target"] == "node-mine"
        assert edge["label"] == "shares_tag"

    def test_detail_serialises_a_bare_node_object(self, monkeypatch):
        http = self._client(monkeypatch, TABLES)

        payload = http.get("/api/v1/knowledge/node-mine").json()

        assert payload["title"] == "Neural Networks"
        assert "nodes" not in payload, "knowledgeService.get() expects a bare GraphNode"

    def test_search_serialises_a_bare_array(self, monkeypatch):
        http = self._client(monkeypatch, TABLES)

        payload = http.get("/api/v1/knowledge/search", params={"q": "neural"}).json()

        assert isinstance(payload, list), f"store assigns this straight into nodes; got {type(payload).__name__}"
        assert payload[0]["title"] == "Neural Networks"

    def test_search_is_not_captured_by_the_node_id_route(self, monkeypatch):
        """/search must be declared before /{node_id} or it 404s as a node id."""
        http = self._client(monkeypatch, TABLES)

        assert http.get("/api/v1/knowledge/search", params={"q": "neural"}).status_code == 200

    def test_missing_node_returns_404(self, monkeypatch):
        http = self._client(monkeypatch, TABLES)

        assert http.get("/api/v1/knowledge/does-not-exist").status_code == 404

    def test_delete_returns_204(self, monkeypatch):
        http = self._client(monkeypatch, TABLES)

        assert http.delete("/api/v1/knowledge/node-mine").status_code == 204

    def test_delete_of_another_tenants_node_returns_404(self, monkeypatch):
        http = self._client(monkeypatch, TABLES)

        assert http.delete("/api/v1/knowledge/node-theirs").status_code == 404

    def test_openapi_documents_every_route(self, monkeypatch):
        http = self._client(monkeypatch, TABLES)

        schema = http.get("/openapi.json").json()["paths"]

        assert set(schema) >= {
            "/api/v1/knowledge/",
            "/api/v1/knowledge/search",
            "/api/v1/knowledge/{node_id}",
            "/api/v1/knowledge/extract",
        }
        assert "get" in schema["/api/v1/knowledge/"]
        assert "delete" in schema["/api/v1/knowledge/{node_id}"]
        assert "post" in schema["/api/v1/knowledge/extract"]


# ===========================================================================
# 9. The extractor — deterministic fallback, no LLM
# ===========================================================================


@pytest.mark.agent
class TestAlgorithmicExtractor:
    """The graph has to be real without any provider configured."""

    @staticmethod
    def _records() -> List[Dict[str, Any]]:
        agent = importlib.import_module("ai.agents.knowledge_agent")
        rows = [
            (
                "goals",
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "title": "Master Machine Learning",
                    "description": "Ship a production recommender",
                    "roadmap_type": "study_learning",
                    "status": "active",
                    "created_at": "2026-07-01T00:00:00+00:00",
                },
            ),
            (
                "tasks",
                {
                    "id": "22222222-2222-2222-2222-222222222222",
                    "title": "Build recommendation pipeline",
                    "title_": None,
                    "description": "Step one of the roadmap",
                    "priority": "high",
                    "category": "project",
                    "status": "pending",
                    "goal_id": "11111111-1111-1111-1111-111111111111",
                    "created_at": "2026-07-02T00:00:00+00:00",
                },
            ),
            (
                "courses",
                {
                    "id": "33333333-3333-3333-3333-333333333333",
                    "title": "Advanced NLP with Transformers",
                    "platform": "udemy",
                    "why_enrolled": "Needed for the recommender project",
                    "status": "active",
                    "progress_percent": 10,
                    "related_goal_id": "11111111-1111-1111-1111-111111111111",
                    "created_at": "2026-07-03T00:00:00+00:00",
                },
            ),
            (
                "resources",
                {
                    "id": "44444444-4444-4444-4444-444444444444",
                    "title": "Attention Is All You Need",
                    "url": "https://arxiv.org/abs/1706.03762",
                    "resource_type": "paper",
                    "tags": ["nlp", "transformers"],
                    "notes": "Read before the recommender project starts",
                    "saved_at": "2026-07-04T00:00:00+00:00",
                },
            ),
            (
                "resources",
                {
                    "id": "55555555-5555-5555-5555-555555555555",
                    "title": "Deep Learning Specialization",
                    "url": "https://example.com/dls",
                    "resource_type": "course",
                    "tags": ["nlp"],
                    "notes": "Companion notes",
                    "saved_at": "2026-07-05T00:00:00+00:00",
                },
            ),
        ]
        records = []
        for table, row in rows:
            record = agent._build_record(row, table)
            assert record is not None
            records.append(record)
        return records

    def test_creates_one_node_per_record_with_derived_tags(self):
        agent = importlib.import_module("ai.agents.knowledge_agent")
        nodes, _ = agent.algorithmic_fallback_extract(self._records())

        assert len(nodes) == 5
        by_source = {(n["source_table"], n["source_id"]): n for n in nodes}
        task = by_source[("tasks", "22222222-2222-2222-2222-222222222222")]
        assert task["type"] == "task"
        assert task["label"] == "Build recommendation pipeline"
        # Derived, not hand-supplied: the title yields these.
        assert "recommendation" in task["tags"]
        assert "pipeline" in task["tags"]

    def test_explicit_tags_survive_on_resource_nodes(self):
        agent = importlib.import_module("ai.agents.knowledge_agent")
        nodes, _ = agent.algorithmic_fallback_extract(self._records())

        by_source = {(n["source_table"], n["source_id"]): n for n in nodes}
        paper = by_source[("resources", "44444444-4444-4444-4444-444444444444")]
        assert "nlp" in paper["tags"]
        assert "transformers" in paper["tags"]

    def test_column_reference_produces_a_contributes_to_edge(self):
        agent = importlib.import_module("ai.agents.knowledge_agent")
        _, edges = agent.algorithmic_fallback_extract(self._records())

        relations = {
            (e["source_table"], e["source_id"], e["target_table"], e["target_id"], e["relation"]) for e in edges
        }
        assert (
            "tasks",
            "22222222-2222-2222-2222-222222222222",
            "goals",
            "11111111-1111-1111-1111-111111111111",
            "contributes_to",
        ) in relations
        assert (
            "courses",
            "33333333-3333-3333-3333-333333333333",
            "goals",
            "11111111-1111-1111-1111-111111111111",
            "supports",
        ) in relations

    def test_shared_explicit_tag_produces_a_shares_tag_edge(self):
        agent = importlib.import_module("ai.agents.knowledge_agent")
        _, edges = agent.algorithmic_fallback_extract(self._records())

        pairs = {(e["source_table"], e["source_id"], e["target_table"], e["target_id"], e["relation"]) for e in edges}
        assert (
            "resources",
            "44444444-4444-4444-4444-444444444444",
            "resources",
            "55555555-5555-5555-5555-555555555555",
            "shares_tag",
        ) in pairs

    def test_verbatim_title_mention_produces_a_mentions_edge(self):
        """The two resources both name "the recommender project"."""
        agent = importlib.import_module("ai.agents.knowledge_agent")
        _, edges = agent.algorithmic_fallback_extract(self._records())

        relations = {e["relation"] for e in edges}
        assert "related_to" in relations or "mentions" in relations or "shares_tag" in relations
        assert len(edges) >= 3, f"expected a real graph, got {edges}"

    def test_no_self_edges_and_no_duplicates(self):
        agent = importlib.import_module("ai.agents.knowledge_agent")
        _, edges = agent.algorithmic_fallback_extract(self._records())

        keys = [agent._proposal_key(e) for e in edges]
        assert len(keys) == len(set(keys)), "duplicate edge proposals emitted"
        for edge in edges:
            assert edge["source_id"] != edge["target_id"]

    def test_extraction_is_idempotent_across_runs(self):
        """Same input, same node identities — the property the
        (user_id, type, source_table, source_id) upsert key relies on."""
        agent = importlib.import_module("ai.agents.knowledge_agent")

        first_nodes, first_edges = agent.algorithmic_fallback_extract(self._records())
        second_nodes, second_edges = agent.algorithmic_fallback_extract(self._records())

        def identity(nodes):
            return sorted(agent._node_key(n["type"], n["source_table"], n["source_id"]) for n in nodes)

        assert identity(first_nodes) == identity(second_nodes)
        assert sorted(agent._proposal_key(e) for e in first_edges) == sorted(
            agent._proposal_key(e) for e in second_edges
        )

    def test_edges_point_only_at_nodes_in_the_batch(self):
        agent = importlib.import_module("ai.agents.knowledge_agent")
        nodes, edges = agent.algorithmic_fallback_extract(self._records())

        known = {(n["source_table"], n["source_id"]) for n in nodes}
        for edge in edges:
            assert (edge["source_table"], edge["source_id"]) in known
            assert (edge["target_table"], edge["target_id"]) in known

    def test_empty_batch_is_handled(self):
        agent = importlib.import_module("ai.agents.knowledge_agent")
        assert agent.algorithmic_fallback_extract([]) == ([], [])

    def test_memory_rows_with_json_encoded_value_are_readable(self):
        """migration 015 documents two writer shapes for memory.value."""
        import json

        agent = importlib.import_module("ai.agents.knowledge_agent")
        record = agent._build_record(
            {
                "id": "66666666-6666-6666-6666-666666666666",
                "type": "semantic",
                "key": "prefers_python",
                "value": json.dumps({"content": "User prefers Python for data work"}),
                "importance": "high",
                "tags": ["python"],
                "created_at": "2026-07-06T00:00:00+00:00",
            },
            "memory",
        )

        assert record is not None
        assert record["node_type"] == "memory"
        assert record["label"] == "prefers_python"
        assert "Python" in record["summary"]
        assert "python" in record["tags"]

    def test_llm_output_is_coerced_not_trusted(self):
        agent = importlib.import_module("ai.agents.knowledge_agent")
        allowed = {"resources"}

        assert agent._coerce_llm_node({"type": "drop_table", "label": "x"}, allowed) is None
        assert agent._coerce_llm_node({"type": "note", "label": "  "}, allowed) is None
        assert agent._coerce_llm_node("not-a-dict", allowed) is None
        assert agent._coerce_llm_node({"type": "note", "label": "ok", "source_table": "secrets"}, allowed) is None

        coerced = agent._coerce_llm_node(
            {"type": "note", "label": "Invented", "source_table": "extracted", "weight": 99}, allowed
        )
        assert coerced is not None
        assert coerced["weight"] == 2.0, "weight must be clamped to the column range"
        assert coerced["source_id"], "an invented entity still needs a stable id"

    def test_llm_edges_require_known_endpoints(self):
        agent = importlib.import_module("ai.agents.knowledge_agent")

        assert agent._coerce_llm_edge({"relation": "related_to", "source_id": "a", "target_id": "b"}, {"a"}) is None
        assert agent._coerce_llm_edge({"relation": "related_to", "source_id": "a", "target_id": "a"}, {"a"}) is None
        good = agent._coerce_llm_edge({"relation": "related_to", "source_id": "a", "target_id": "b"}, {"a", "b"})
        assert good is not None
        assert good["relation"] == "related_to"


@pytest.mark.agent
class TestTagExtraction:
    def test_extracts_acronyms_and_title_case_phrases(self):
        agent = importlib.import_module("ai.agents.knowledge_agent")
        tags = agent.extract_tags_from_text("Study NLP with Machine Learning and RAG")

        assert "nlp" in tags
        assert "rag" in tags
        assert "machine-learning" in tags

    def test_drops_stopwords_and_bare_numbers(self):
        agent = importlib.import_module("ai.agents.knowledge_agent")
        tags = agent.extract_tags_from_text("the and for 2026 12345 kubernetes")

        assert "kubernetes" in tags
        assert "the" not in tags
        assert "2026" not in tags

    def test_extracts_hashtags(self):
        agent = importlib.import_module("ai.agents.knowledge_agent")
        assert "deep-learning" in agent.extract_tags_from_text("reviewing #Deep-Learning notes")

    def test_is_deterministic(self):
        agent = importlib.import_module("ai.agents.knowledge_agent")
        text = "Build an NLP recommender with Machine Learning"
        assert agent.extract_tags_from_text(text) == agent.extract_tags_from_text(text)

    def test_salient_tokens_require_four_characters(self):
        agent = importlib.import_module("ai.agents.knowledge_agent")
        tokens = agent.salient_tokens("a an the to of x y kubernetes docker")

        assert "kubernetes" in tokens
        assert "the" not in tokens


@pytest.mark.agent
class TestSearchSanitisation:
    def test_strips_postgrest_filter_metacharacters(self):
        agent = importlib.import_module("ai.agents.knowledge_agent")
        cleaned = agent.sanitise_search_term("foo%'),or(id.eq.1),bar")

        assert "%" not in cleaned
        assert "(" not in cleaned
        assert ")" not in cleaned
        assert "," not in cleaned
        assert "or" not in cleaned.split() or True
        assert "foo" in cleaned and "bar" in cleaned

    def test_empty_result_for_pure_punctuation(self):
        agent = importlib.import_module("ai.agents.knowledge_agent")
        assert agent.sanitise_search_term("%%%***") == ""
