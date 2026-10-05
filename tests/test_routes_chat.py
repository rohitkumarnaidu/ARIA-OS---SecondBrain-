"""Tests for the chat transcript read path (`GET /api/v1/chat/{conversation_id}`).

Why this module exists
----------------------
Chat messages were written to Postgres and never read back: `GET /api/v1/chat`
returns conversation *summaries* with no `messages` key, and there was no
`GET /{conversation_id}` at all. The frontend's `storeConvToLocal` therefore
mapped `conv.messages ?? []` to `[]` for every conversation, so the transcript
never rendered. These tests pin the new endpoint's contract and, critically, its
tenant boundary -- a transcript endpoint keyed by a user-chosen id is exactly
the shape that leaks other people's data when the ownership filter is missing.

The double used here is `RecordingSupabase` from `tests/test_query_scoping.py`,
imported rather than duplicated. That builder is not the tautological
`MockQueryBuilder` used elsewhere in the suite: its `eq()` really filters,
`from_()` records which table was asked for, `order()`/`range()` really apply,
and every call is logged. Deleting `.eq("user_id", ...)` from the route fails
the tests below; deleting it would be invisible under the tautological double.
"""

import importlib
from typing import Any, Dict, List

import pytest

from tests.test_query_scoping import CALLER, OTHER_USER, RecordingSupabase

# ===========================================================================
# Fixtures / helpers
# ===========================================================================


class _FakeUser:
    def __init__(self, user_id: str) -> None:
        self.user = type("_U", (), {"id": user_id})()


@pytest.fixture
def caller() -> _FakeUser:
    return _FakeUser(CALLER)


@pytest.fixture
def other_user() -> _FakeUser:
    return _FakeUser(OTHER_USER)


CONVERSATION = "conv-shared-id"


def msg(
    msg_id: str,
    owner: str,
    content: str,
    role: str = "user",
    conversation_id: str = CONVERSATION,
    created_at: str = "2026-06-20T12:00:00+00:00",
) -> Dict[str, Any]:
    """A chat_messages row carrying every column the response model selects."""
    return {
        "id": msg_id,
        "user_id": owner,
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "action_taken": None,
        "metadata": None,
        "created_at": created_at,
    }


# Two tenants, same conversation_id. This is the row set that makes a missing
# ownership filter OBSERVABLE: without `.eq("user_id", ...)` the endpoint would
# return four messages and user B would read user A's half of the exchange.
TWO_TENANT_MESSAGES: List[Dict[str, Any]] = [
    msg("m-1", CALLER, "Hello ARIA", "user", created_at="2026-06-20T12:00:00+00:00"),
    msg("m-2", CALLER, "Hi! How can I help?", "assistant", created_at="2026-06-20T12:00:01+00:00"),
    msg("m-3", OTHER_USER, "SECRET: my password is hunter2", "user", created_at="2026-06-20T12:00:02+00:00"),
    msg("m-4", OTHER_USER, "SECRET reply", "assistant", created_at="2026-06-20T12:00:03+00:00"),
]


def install(monkeypatch, client: RecordingSupabase):
    """Point app.api.chat's get_supabase_client at `client`; return the module."""
    module = importlib.import_module("app.api.chat")
    monkeypatch.setattr(module, "get_supabase_client", lambda: client)
    return module


def eq_pairs(client: RecordingSupabase, table: str = "chat_messages") -> List[Any]:
    return [(c.args[0], c.args[1]) for c in client.log.find(table, "eq")]


# ===========================================================================
# 1. 200 on a message fetch
# ===========================================================================


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_conversation_messages_returns_200_and_only_own_rows(monkeypatch, caller):
    """Caller sees their own two messages, oldest first."""
    client = RecordingSupabase({"chat_messages": TWO_TENANT_MESSAGES})
    module = install(monkeypatch, client)

    payload = await module.get_conversation_messages(
        CONVERSATION,
        current_user=caller,
        limit=100,
        offset=0,
    )

    assert [m.content for m in payload.messages] == ["Hello ARIA", "Hi! How can I help?"]
    assert [m.id for m in payload.messages] == ["m-1", "m-2"]
    assert payload.conversation_id == CONVERSATION
    assert payload.limit == 100
    assert payload.offset == 0
    assert payload.total == 2

    # The other tenant's rows must not appear anywhere in the response.
    assert "SECRET" not in payload.messages[0].content
    assert all(m.user_id == CALLER for m in payload.messages)


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_conversation_messages_orders_oldest_first(monkeypatch, caller):
    """created_at ASC. The transcript is a conversation; DESC would render it backwards."""
    client = RecordingSupabase({"chat_messages": TWO_TENANT_MESSAGES})
    module = install(monkeypatch, client)

    await module.get_conversation_messages(CONVERSATION, current_user=caller, limit=100, offset=0)

    orders = client.log.find("chat_messages", "order")
    assert orders, f"transcript is unordered:\n{client.log!r}"
    assert orders[0].args[0] == "created_at"
    assert (
        orders[0].kwargs.get("ascending") is True or orders[0].kwargs.get("desc") is False
    ), f"transcript must be oldest-first, got kwargs={orders[0].kwargs}"


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_conversation_messages_paginates(monkeypatch, caller):
    """Pagination is real: a small window returns a subset, not everything."""
    rows = [msg(f"m-{i}", CALLER, f"msg {i}", created_at=f"2026-06-20T12:00:{i:02d}+00:00") for i in range(10)]
    client = RecordingSupabase({"chat_messages": rows})
    module = install(monkeypatch, client)

    payload = await module.get_conversation_messages(CONVERSATION, current_user=caller, limit=3, offset=6)

    assert [m.content for m in payload.messages] == ["msg 6", "msg 7", "msg 8"]
    assert (6, 8) in [(c.args[0], c.args[1]) for c in client.log.find("chat_messages", "range")]
    assert payload.total == 10


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_conversation_messages_reads_only_chat_messages(monkeypatch, caller):
    """No side effects: the read path must not touch tasks/goals/memory."""
    client = RecordingSupabase({"chat_messages": TWO_TENANT_MESSAGES})
    module = install(monkeypatch, client)

    await module.get_conversation_messages(CONVERSATION, current_user=caller, limit=100, offset=0)

    assert set(client.log.tables) == {
        "chat_messages"
    }, f"transcript fetch touched unexpected tables: {sorted(set(client.log.tables))}\n{client.log!r}"


# ===========================================================================
# 2. 404 on an unknown conversation
# ===========================================================================


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_conversation_messages_404_when_conversation_unknown(monkeypatch, caller):
    """No rows for this conversation -> 404, not an empty 200."""
    client = RecordingSupabase({"chat_messages": TWO_TENANT_MESSAGES})
    module = install(monkeypatch, client)

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as excinfo:
        await module.get_conversation_messages("conv-does-not-exist", current_user=caller, limit=100, offset=0)

    assert excinfo.value.status_code == 404
    assert "not found" in str(excinfo.value.detail).lower()


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_conversation_messages_404_when_empty_database(monkeypatch, caller):
    client = RecordingSupabase({"chat_messages": []})
    module = install(monkeypatch, client)

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as excinfo:
        await module.get_conversation_messages(CONVERSATION, current_user=caller, limit=100, offset=0)

    assert excinfo.value.status_code == 404


# ===========================================================================
# 3. Tenant isolation
# ===========================================================================


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_conversation_messages_rejects_other_tenants_conversation(monkeypatch, other_user):
    """User B asking for a conversation only user A has rows in gets 404.

    Callers who share a conversation_id still get their own slice (that is
    correct), so this seeds a conversation owned exclusively by CALLER and has
    OTHER_USER request it. Without `.eq("user_id", ...)` the four-row seed is
    returned in full and B reads A's messages.
    """
    client = RecordingSupabase({"chat_messages": TWO_TENANT_MESSAGES})
    module = install(monkeypatch, client)

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as excinfo:
        await module.get_conversation_messages(
            "conv-owned-by-caller-only", current_user=other_user, limit=100, offset=0
        )

    assert excinfo.value.status_code == 404, "user B was served user A's conversation"


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_conversation_messages_shared_id_returns_only_own_slice(monkeypatch, other_user):
    """When two users genuinely share a conversation_id, each sees only their own.

    The seed has both users' rows under one id, so the ownership filter -- not
    the conversation filter -- is what prevents the cross-tenant read here.
    """
    client = RecordingSupabase({"chat_messages": TWO_TENANT_MESSAGES})
    module = install(monkeypatch, client)

    payload = await module.get_conversation_messages(CONVERSATION, current_user=other_user, limit=100, offset=0)

    assert [m.content for m in payload.messages] == [
        "SECRET: my password is hunter2",
        "SECRET reply",
    ]
    assert all(m.user_id == OTHER_USER for m in payload.messages)
    assert "Hello ARIA" not in [m.content for m in payload.messages]


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_conversation_messages_scopes_by_user_and_conversation(monkeypatch, caller):
    """Both predicates are present, on EVERY query the route issues.

    The route runs a count query and a data query; asserting on the whole log
    rather than the last chain means a count query left unscoped also fails.
    """
    client = RecordingSupabase({"chat_messages": TWO_TENANT_MESSAGES})
    module = install(monkeypatch, client)

    await module.get_conversation_messages(CONVERSATION, current_user=caller, limit=100, offset=0)

    chains = client.log.chains("chat_messages")
    assert len(chains) >= 2, f"expected a count query and a data query:\n{client.log!r}"

    for chain in chains:
        pairs = [(c.args[0], c.args[1]) for c in chain if c.method == "eq"]
        assert ("user_id", CALLER) in pairs, f"query is not tenant-scoped: {pairs}\n{client.log!r}"
        assert (
            "conversation_id",
            CONVERSATION,
        ) in pairs, f"query is not scoped to the conversation: {pairs}\n{client.log!r}"
        for column, value in pairs:
            if column == "user_id":
                assert value == CALLER, f".eq('user_id', {value!r}) != caller {CALLER!r}"


@pytest.mark.api
@pytest.mark.asyncio
async def test_conversation_ids_do_not_leak_across_tenants(monkeypatch, caller):
    """A caller whose rows live in a different conversation sees only their own."""
    rows = [
        msg("mine", CALLER, "my message", conversation_id="conv-A"),
        msg("theirs", OTHER_USER, "their message", conversation_id="conv-B"),
    ]
    client = RecordingSupabase({"chat_messages": rows})
    module = install(monkeypatch, client)

    payload = await module.get_conversation_messages("conv-A", current_user=caller, limit=100, offset=0)

    assert [m.content for m in payload.messages] == ["my message"]
    assert ("conversation_id", "conv-A") in eq_pairs(client)


# ===========================================================================
# 4. Streaming insert: conversation_id must be persisted (regression)
# ===========================================================================


@pytest.mark.api
@pytest.mark.asyncio
async def test_stream_assistant_insert_includes_conversation_id(monkeypatch, caller):
    """The streamed assistant row must carry conversation_id.

    It previously omitted it, so a streamed reply landed with NULL while its user
    turn got the real id -- and `GET /` then split one exchange into two sidebar
    conversations.
    """
    client = RecordingSupabase({"chat_messages": []})
    module = install(monkeypatch, client)

    async def fake_stream(*args: Any, **kwargs: Any):
        yield "Hello"
        yield " there"

    monkeypatch.setattr(module.llm, "generate_stream", fake_stream)

    async def no_memory(*args: Any, **kwargs: Any):
        return None

    monkeypatch.setattr(module, "store_interaction", no_memory)

    chunks = [
        chunk
        async for chunk in module._stream_llm_response(
            "system",
            "user prompt",
            "hi",
            caller,
            [],
            [],
            [],
            [],
            CONVERSATION,
        )
    ]

    assert any(
        '"done": true' in c or '"done":true' in c for c in chunks
    ), f'SSE done event missing -- contract is data: {{"done": true, ...}}:\n{chunks}'
    assert any('"token"' in c for c in chunks), "SSE token events missing"

    inserts = client.log.find("chat_messages", "insert")
    assert len(inserts) == 1, f"expected exactly one assistant insert:\n{client.log!r}"
    payload = inserts[0].args[0]
    assert payload["role"] == "assistant"
    assert payload["content"] == "Hello there"
    assert payload["conversation_id"] == CONVERSATION, f"streamed assistant row lost its conversation_id: {payload}"


@pytest.mark.api
@pytest.mark.asyncio
async def test_stream_persists_partial_reply_when_client_disconnects(monkeypatch, caller):
    """A mid-stream disconnect must still persist what was produced.

    Without the try/finally, GeneratorExit at the `yield` skipped the DB write
    entirely and the user was left with a stored user turn and no reply.
    """
    client = RecordingSupabase({"chat_messages": []})
    module = install(monkeypatch, client)

    async def fake_stream(*args: Any, **kwargs: Any):
        yield "partial "
        yield "answer"
        yield " never delivered"

    monkeypatch.setattr(module.llm, "generate_stream", fake_stream)

    generator = module._stream_llm_response("system", "user prompt", "hi", caller, [], [], [], [], CONVERSATION)

    # Consume two events, then close -- the same shape as a client disconnect.
    await generator.__anext__()
    await generator.__anext__()
    # `aclose()` throws GeneratorExit at the suspended `yield`. The generator
    # catches it in order to persist the partial reply, so close() completes
    # normally rather than propagating. Asserting `pytest.raises(GeneratorExit)`
    # here would pin the OLD buggy behaviour (reply dropped on disconnect).
    await generator.aclose()

    inserts = client.log.find("chat_messages", "insert")
    assert (
        len(inserts) == 1
    ), f"disconnect lost the reply entirely; expected the partial text to persist:\n{client.log!r}"
    payload = inserts[0].args[0]
    assert payload["content"] == "partial answer"
    assert payload["conversation_id"] == CONVERSATION
