"""Tests for ToolCalling System — ToolRegistry, ToolExecutor, ToolCallingAgent, auto-discovery."""

import asyncio
import json
import os
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Set required env vars before any project imports to prevent ValueError
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-key")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-service-key")

# Mock supabase create_client before any project imports use it
with patch("supabase.create_client") as mock_create_client:
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.execute.return_value = MagicMock(data=[])
    mock_client.from_.return_value.select.return_value.execute.return_value = MagicMock(data=[])
    mock_client.rpc.return_value.execute.return_value = MagicMock(data=[])
    mock_create_client.return_value = mock_client

    from ai.tool_calling import (
        ToolDefinition,
        ToolRegistry,
        ToolExecutionContext,
        ToolResult,
        ToolExecutor,
        ToolCallingAgent,
        ToolExecutionError,
    )
    from ai.tool_registry import discover_agent_tools, _infer_parameter_schema
    from database.schemas.tool_calling import (
        ToolCallRequest,
        ToolCallResponse,
        ToolDefinitionSchema,
        ToolExecutionLog,
        ToolAuditEntry,
    )


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def registry():
    r = ToolRegistry()
    r.clear()
    yield r
    r.clear()


@pytest.fixture
def sample_tool():
    return ToolDefinition(
        name="test_tool",
        description="A test tool",
        parameters={
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "User ID"},
                "count": {"type": "integer", "description": "Count of items"},
            },
            "required": ["user_id"],
        },
        handler="ai.agents.task_agent.check_missed_tasks",
        required_permissions=["user"],
        timeout=30,
        audit=True,
    )


@pytest.fixture
def executor(registry, sample_tool):
    registry.register(sample_tool)
    return ToolExecutor(registry=registry)


@pytest.fixture
def agent(executor):
    return ToolCallingAgent(executor=executor)


# ─── ToolDefinition Tests ────────────────────────────────────────────────────


class TestToolDefinition:
    def test_validate_parameters_required_present(self):
        td = ToolDefinition(
            name="test",
            description="test",
            parameters={"type": "object", "properties": {"x": {"type": "string"}}, "required": ["x"]},
            handler="test.handler",
        )
        errors = td.validate_parameters({"x": "hello"})
        assert errors == []

    def test_validate_parameters_required_missing(self):
        td = ToolDefinition(
            name="test",
            description="test",
            parameters={"type": "object", "properties": {"x": {"type": "string"}}, "required": ["x"]},
            handler="test.handler",
        )
        errors = td.validate_parameters({})
        assert "Missing required parameter: x" in errors

    def test_validate_parameters_type_mismatch(self):
        td = ToolDefinition(
            name="test",
            description="test",
            parameters={"type": "object", "properties": {"age": {"type": "integer"}}},
            handler="test.handler",
        )
        errors = td.validate_parameters({"age": "not_a_number"})
        assert any("expected integer" in e for e in errors)

    def test_validate_parameters_type_match(self):
        td = ToolDefinition(
            name="test",
            description="test",
            parameters={"type": "object", "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "score": {"type": "number"},
                "active": {"type": "boolean"},
                "tags": {"type": "array"},
                "meta": {"type": "object"},
            }},
            handler="test.handler",
        )
        errors = td.validate_parameters({
            "name": "Alice",
            "age": 30,
            "score": 95.5,
            "active": True,
            "tags": ["a", "b"],
            "meta": {"key": "val"},
        })
        assert errors == []

    def test_validate_parameters_no_schema(self):
        td = ToolDefinition(name="test", description="test", handler="test.handler")
        errors = td.validate_parameters({"anything": "goes"})
        assert errors == []

    def test_validate_parameters_nested_object(self):
        td = ToolDefinition(
            name="test",
            description="test",
            parameters={
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string"},
                        },
                    },
                },
            },
            handler="test.handler",
        )
        errors = td.validate_parameters({"filter": {"status": "active"}})
        assert errors == []


# ─── ToolDefinition Pydantic Schema Tests ───────────────────────────────────


class TestToolDefinitionSchema:
    def test_tool_definition_schema_valid(self):
        schema = ToolDefinitionSchema(
            name="test", description="test", handler="test.handler"
        )
        assert schema.name == "test"
        assert schema.timeout == 30
        assert schema.audit is True

    def test_tool_definition_schema_defaults(self):
        schema = ToolDefinitionSchema(
            name="test", description="test", handler="test.handler"
        )
        assert schema.parameters == {}
        assert schema.required_permissions == []
        assert schema.timeout == 30
        assert schema.audit is True


# ─── ToolCallRequest / ToolCallResponse Tests ────────────────────────────────


class TestToolCallSchemas:
    def test_tool_call_request(self):
        req = ToolCallRequest(tool_name="test", user_id="user1")
        assert req.tool_name == "test"
        assert req.user_id == "user1"
        assert req.parameters == {}
        assert req.request_id is None

    def test_tool_call_response(self):
        resp = ToolCallResponse(
            success=True, data={"result": "ok"}, tool_name="test", request_id="rid1"
        )
        assert resp.success is True
        assert resp.data == {"result": "ok"}

    def test_tool_call_response_error(self):
        resp = ToolCallResponse(
            success=False, error="fail", tool_name="test", request_id="rid1"
        )
        assert resp.success is False
        assert resp.error == "fail"


# ─── ToolRegistry Tests ──────────────────────────────────────────────────────


class TestToolRegistry:
    def test_singleton(self):
        r1 = ToolRegistry()
        r2 = ToolRegistry()
        assert r1 is r2

    def test_register_and_get(self, registry, sample_tool):
        registry.register(sample_tool)
        retrieved = registry.get("test_tool")
        assert retrieved is not None
        assert retrieved.name == "test_tool"
        assert retrieved.description == "A test tool"

    def test_register_duplicate_raises(self, registry, sample_tool):
        registry.register(sample_tool)
        with pytest.raises(ValueError, match="already registered"):
            registry.register(sample_tool)

    def test_unregister(self, registry, sample_tool):
        registry.register(sample_tool)
        registry.unregister("test_tool")
        assert registry.get("test_tool") is None

    def test_unregister_missing_raises(self, registry):
        with pytest.raises(KeyError, match="not found"):
            registry.unregister("nonexistent")

    def test_list_all(self, registry, sample_tool):
        registry.register(sample_tool)
        t2 = ToolDefinition(
            name="tool2", description="Second tool", handler="test.handler"
        )
        registry.register(t2)
        tools = registry.list()
        assert len(tools) == 2

    def test_list_by_category(self, registry):
        t1 = ToolDefinition(
            name="t1", description="a", handler="test.handler", required_permissions=["user"]
        )
        t2 = ToolDefinition(
            name="t2", description="b", handler="test.handler", required_permissions=["admin"]
        )
        t3 = ToolDefinition(
            name="t3", description="c", handler="test.handler", required_permissions=["user"]
        )
        registry.register(t1)
        registry.register(t2)
        registry.register(t3)
        user_tools = registry.list(category="user")
        assert len(user_tools) == 2
        admin_tools = registry.list(category="admin")
        assert len(admin_tools) == 1

    def test_search_by_name(self, registry):
        registry.register(ToolDefinition(
            name="generate_briefing", description="Daily briefing", handler="test.handler"
        ))
        registry.register(ToolDefinition(
            name="check_missed_tasks", description="Find overdue", handler="test.handler"
        ))
        results = registry.search("briefing")
        assert len(results) == 1
        assert results[0].name == "generate_briefing"

    def test_search_by_description(self, registry):
        registry.register(ToolDefinition(
            name="tb", description="tool for briefing generation", handler="test.handler"
        ))
        results = registry.search("briefing")
        assert len(results) == 1

    def test_get_categories(self, registry):
        registry.register(ToolDefinition(
            name="a", description="a", handler="test.handler", required_permissions=["user", "admin"]
        ))
        registry.register(ToolDefinition(
            name="b", description="b", handler="test.handler", required_permissions=["system"]
        ))
        cats = registry.get_categories()
        assert "user" in cats
        assert "admin" in cats
        assert "system" in cats

    def test_count(self, registry):
        assert registry.count() == 0
        registry.register(ToolDefinition(name="a", description="a", handler="test.handler"))
        assert registry.count() == 1

    def test_has(self, registry, sample_tool):
        assert registry.has("test_tool") is False
        registry.register(sample_tool)
        assert registry.has("test_tool") is True

    def test_clear(self, registry, sample_tool):
        registry.register(sample_tool)
        registry.clear()
        assert registry.count() == 0
        assert registry.loaded is False

    def test_loaded_flag(self, registry):
        assert registry.loaded is False
        registry.loaded = True
        assert registry.loaded is True


# ─── ToolExecutionContext Tests ──────────────────────────────────────────────


class TestToolExecutionContext:
    def test_initialization(self):
        ctx = ToolExecutionContext(
            tool_name="test", parameters={"key": "val"}, user_id="user1", timeout=10
        )
        assert ctx.tool_name == "test"
        assert ctx.parameters == {"key": "val"}
        assert ctx.user_id == "user1"
        assert ctx.timeout == 10
        assert ctx.request_id is not None

    def test_check_timeout_not_expired(self):
        ctx = ToolExecutionContext(
            tool_name="test", parameters={}, user_id="user1", timeout=30
        )
        ctx.check_timeout()

    def test_check_timeout_expired(self):
        ctx = ToolExecutionContext(
            tool_name="test", parameters={}, user_id="user1", timeout=0.01
        )
        time.sleep(0.02)
        with pytest.raises(TimeoutError, match="exceeded timeout"):
            ctx.check_timeout()

    def test_to_dict(self):
        ctx = ToolExecutionContext(
            tool_name="test", parameters={"x": 1}, user_id="user1", request_id="rid1", timeout=15
        )
        d = ctx.to_dict()
        assert d["tool_name"] == "test"
        assert d["parameters"] == {"x": 1}
        assert d["user_id"] == "user1"
        assert d["request_id"] == "rid1"
        assert d["timeout"] == 15
        assert "started_at" in d


# ─── ToolResult Tests ────────────────────────────────────────────────────────


class TestToolResult:
    def test_success(self):
        tr = ToolResult(
            success=True,
            data={"result": "ok"},
            duration_ms=100,
            tool_name="test",
            request_id="rid1",
        )
        assert tr.to_dict() == {
            "success": True,
            "data": {"result": "ok"},
            "duration_ms": 100,
            "tool_name": "test",
            "request_id": "rid1",
        }

    def test_error_excludes_none(self):
        tr = ToolResult(
            success=False,
            error="fail",
            duration_ms=0,
            tool_name="test",
            request_id="rid1",
        )
        d = tr.to_dict()
        assert "data" not in d
        assert d["error"] == "fail"

    def test_to_llm_format_success(self):
        tr = ToolResult(
            success=True,
            data={"completed": True},
            duration_ms=50,
            tool_name="check",
            request_id="rid1",
        )
        formatted = tr.to_llm_format()
        assert "completed successfully" in formatted
        assert "check" in formatted
        assert "50ms" in formatted

    def test_to_llm_format_error(self):
        tr = ToolResult(
            success=False,
            error="Something broke",
            duration_ms=200,
            tool_name="fail_tool",
            request_id="rid1",
        )
        formatted = tr.to_llm_format()
        assert "failed" in formatted
        assert "Something broke" in formatted
        assert "fail_tool" in formatted


# ─── ToolExecutor Tests ──────────────────────────────────────────────────────


class TestToolExecutor:
    def test_execute_success(self, executor):
        result = asyncio.run(executor.execute(
            "test_tool", {"user_id": "u1"}, "u1"
        ))
        assert result.success is True
        assert result.tool_name == "test_tool"
        assert result.duration_ms >= 0
        assert result.data is not None

    def test_execute_tool_not_found(self, registry):
        ex = ToolExecutor(registry=registry)
        result = asyncio.run(ex.execute("nonexistent", {}, "u1"))
        assert result.success is False
        assert "not found" in (result.error or "")

    def test_execute_validation_error(self, executor):
        result = asyncio.run(executor.execute(
            "test_tool", {}, "u1"
        ))
        assert result.success is False
        assert "Parameter validation failed" in (result.error or "")

    def test_execute_invalid_handler(self, registry):
        td = ToolDefinition(
            name="bad_handler",
            description="bad",
            handler="nonexistent.module.func",
        )
        registry.register(td)
        ex = ToolExecutor(registry=registry)
        result = asyncio.run(ex.execute("bad_handler", {}, "u1"))
        assert result.success is False
        assert "Cannot import" in (result.error or "")

    @pytest.mark.asyncio
    async def test_execute_batch_mixed(self, executor, registry):
        td2 = ToolDefinition(
            name="tool2",
            description="second tool",
            handler="ai.agents.memory_agent.prune_expired_memories",
            parameters={
                "type": "object",
                "properties": {"user_id": {"type": "string"}},
                "required": ["user_id"],
            },
        )
        registry.register(td2)
        calls = [
            {"tool_name": "test_tool", "parameters": {"user_id": "u1"}},
            {"tool_name": "tool2", "parameters": {"user_id": "u1"}},
        ]
        results = await executor.execute_batch(calls, "u1")
        assert len(results) == 2
        assert results[0].success is True
        assert results[1].success is True

    @pytest.mark.asyncio
    async def test_execute_batch_with_error(self, executor):
        calls = [
            {"tool_name": "test_tool", "parameters": {"user_id": "u1"}},
            {"tool_name": "nonexistent", "parameters": {}},
        ]
        results = await executor.execute_batch(calls, "u1")
        assert len(results) == 2
        assert results[0].success is True
        assert results[1].success is False

    @pytest.mark.asyncio
    async def test_execute_with_retry_success(self, executor):
        result = await executor.execute_with_retry(
            "test_tool", {"user_id": "u1"}, "u1", max_retries=1
        )
        assert result.success is True

    @pytest.mark.asyncio
    async def test_execute_with_retry_not_found(self, registry):
        ex = ToolExecutor(registry=registry)
        result = await ex.execute_with_retry("nonexistent", {}, "u1")
        assert result.success is False
        assert "not found" in (result.error or "")

    @pytest.mark.asyncio
    async def test_execute_tool_call_success(self, executor):
        result = await executor.execute_tool_call(
            "test_tool", {"user_id": "u1"}, "u1"
        )
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_execute_tool_call_error(self, executor):
        with pytest.raises(ToolExecutionError):
            await executor.execute_tool_call("nonexistent", {}, "u1")


class TestToolExecutorWithMock:
    @pytest.mark.asyncio
    async def test_execute_timeout(self, registry):
        async def slow_handler(user_id: str) -> dict:
            await asyncio.sleep(10)
            return {"done": True}

        td = ToolDefinition(
            name="slow_tool",
            description="slow",
            handler="tests.test_tool_calling.slow_handler",
            timeout=0.05,
        )
        registry.register(td)

        import tests.test_tool_calling as this_mod
        this_mod.slow_handler = slow_handler

        ex = ToolExecutor(registry=registry)
        result = await ex.execute("slow_tool", {"user_id": "u1"}, "u1")
        assert result.success is False
        assert "timed out" in (result.error or "")

    @pytest.mark.asyncio
    async def test_execute_audit_logging(self, registry):
        with patch("ai.tool_calling.log_audit", new_callable=AsyncMock) as mock_audit:
            td = ToolDefinition(
                name="audit_tool",
                description="test audit",
                handler="ai.agents.memory_agent.prune_expired_memories",
                parameters={
                    "type": "object",
                    "properties": {"user_id": {"type": "string"}},
                    "required": ["user_id"],
                },
                audit=True,
            )
            registry.register(td)
            ex = ToolExecutor(registry=registry)
            await ex.execute("audit_tool", {"user_id": "u1"}, "u1")
            mock_audit.assert_called_once()


# ─── ToolCallingAgent Tests ──────────────────────────────────────────────────


class TestToolCallingAgent:
    def test_get_tool_schemas(self, agent):
        schemas = agent.get_tool_schemas()
        assert len(schemas) == 1
        assert schemas[0]["name"] == "test_tool"
        assert "parameters" in schemas[0]

    def test_format_tools_for_llm(self, agent):
        formatted = agent.format_tools_for_llm()
        assert "test_tool" in formatted
        assert "A test tool" in formatted

    def test_format_tools_for_llm_empty(self, registry):
        agent = ToolCallingAgent(registry=registry)
        formatted = agent.format_tools_for_llm()
        assert "No tools available" in formatted

    def test_format_for_openai(self, agent):
        tools = agent.format_for_openai()
        assert len(tools) == 1
        assert tools[0]["type"] == "function"
        assert tools[0]["function"]["name"] == "test_tool"

    def test_format_for_claude(self, agent):
        tools = agent.format_for_claude()
        assert len(tools) == 1
        assert tools[0]["name"] == "test_tool"
        assert "input_schema" in tools[0]

    def test_parse_tool_calls_from_openai(self, agent):
        response = {
            "choices": [{
                "message": {
                    "tool_calls": [{
                        "id": "call_1",
                        "function": {
                            "name": "test_tool",
                            "arguments": json.dumps({"user_id": "u1"}),
                        },
                    }],
                },
            }],
        }
        calls = agent.parse_tool_calls_from_openai(response)
        assert len(calls) == 1
        assert calls[0]["tool_name"] == "test_tool"
        assert calls[0]["parameters"] == {"user_id": "u1"}

    def test_parse_tool_calls_from_claude(self, agent):
        response = {
            "content": [
                {"type": "tool_use", "name": "test_tool", "input": {"user_id": "u1"}, "id": "tu_1"},
            ],
        }
        calls = agent.parse_tool_calls_from_claude(response)
        assert len(calls) == 1
        assert calls[0]["tool_name"] == "test_tool"
        assert calls[0]["parameters"] == {"user_id": "u1"}


# ─── Parameter Schema Inference Tests ────────────────────────────────────────


class TestParameterInference:
    def test_infer_simple_params(self):
        async def sample_func(user_id: str, count: int = 10) -> dict:
            return {}

        schema = _infer_parameter_schema(sample_func)
        assert schema["type"] == "object"
        assert "user_id" in schema["properties"]
        assert schema["properties"]["user_id"]["type"] == "string"
        assert "count" in schema["properties"]
        assert schema["properties"]["count"]["type"] == "integer"
        assert "user_id" in schema.get("required", [])
        assert "count" not in schema.get("required", [])

    def test_infer_optional_params(self):
        async def func(name: str, description: str = None) -> dict:
            return {}

        schema = _infer_parameter_schema(func)
        assert "description" not in schema.get("required", [])


# ─── Auto-Discovery Tests ────────────────────────────────────────────────────


class TestAutoDiscovery:
    def test_discover_agent_tools_populates_registry(self):
        reg = ToolRegistry()
        reg.clear()
        discover_agent_tools(reg)
        assert reg.count() > 0
        assert reg.has("generate_daily_briefing")
        assert reg.has("store_interaction")
        assert reg.has("consolidate_memories")
        assert reg.has("track_user_progress")
        assert reg.has("run_opportunity_radar")
        assert reg.has("breakdown_task")
        assert reg.has("check_missed_tasks")
        assert reg.has("analyze_sleep")
        assert reg.has("check_course_nudges")
        assert reg.has("generate_weekly_review")
        assert reg.has("optimize_roadmap")
        assert reg.has("match_opportunities")
        assert reg.has("assess_user_skill")
        assert reg.has("recommend_skills")
        assert reg.has("refresh_skill_intelligence")
        assert reg.has("generate_skill_roadmap")
        assert reg.has("verify_evidence")
        assert reg.has("analyze_career_readiness")
        assert reg.has("analyze_market_trends")
        assert reg.has("explore_skill_graph")
        assert reg.has("match_skill_opportunities")

    def test_discovery_sets_loaded_flag(self):
        reg = ToolRegistry()
        reg.clear()
        assert reg.loaded is False
        discover_agent_tools(reg)
        assert reg.loaded is True

    def test_discovery_skips_duplicates(self):
        reg = ToolRegistry()
        reg.clear()
        discover_agent_tools(reg)
        count1 = reg.count()
        discover_agent_tools(reg)
        count2 = reg.count()
        assert count1 == count2

    def test_all_tools_have_handler(self):
        reg = ToolRegistry()
        reg.clear()
        discover_agent_tools(reg)
        for tool in reg.list():
            assert tool.handler, f"Tool {tool.name} has no handler"
            assert "." in tool.handler, f"Tool {tool.name} handler not dotted"

    def test_all_tools_have_description(self):
        reg = ToolRegistry()
        reg.clear()
        discover_agent_tools(reg)
        for tool in reg.list():
            assert tool.description, f"Tool {tool.name} has no description"

    def test_tool_names_are_snake_case(self):
        reg = ToolRegistry()
        reg.clear()
        discover_agent_tools(reg)
        for tool in reg.list():
            assert "_" in tool.name or tool.name.islower(), f"Tool {tool.name} not snake_case"

    def test_discovery_no_tools_with_none_handler(self):
        reg = ToolRegistry()
        reg.clear()
        discover_agent_tools(reg)
        for tool in reg.list():
            assert tool.handler is not None


# ─── Edge Case Tests ─────────────────────────────────────────────────────────


class TestEdgeCases:
    def test_empty_registry_execute(self):
        reg = ToolRegistry()
        reg.clear()
        ex = ToolExecutor(registry=reg)
        result = asyncio.run(ex.execute("anything", {}, "u1"))
        assert result.success is False

    def test_registry_persists_across_instances(self):
        ToolRegistry().clear()
        r1 = ToolRegistry()
        r2 = ToolRegistry()
        r1.register(ToolDefinition(name="persist_test", description="x", handler="test.handler"))
        assert r2.has("persist_test")

    def test_tool_with_unknown_param_type(self):
        td = ToolDefinition(
            name="weird",
            description="weird params",
            parameters={"type": "object", "properties": {"data": {"type": "weird_type"}}},
            handler="test.handler",
        )
        errors = td.validate_parameters({"data": "anything"})
        assert errors == []

    def test_execute_with_additional_params(self, executor):
        result = asyncio.run(executor.execute(
            "test_tool", {"user_id": "u1", "extra": "ignored"}, "u1"
        ))
        assert result.success is True

    def test_tool_result_llm_format_with_none_data(self):
        tr = ToolResult(
            success=True, data=None, duration_ms=0, tool_name="t", request_id="r"
        )
        formatted = tr.to_llm_format()
        assert "completed successfully" in formatted

    def test_tool_result_llm_format_none_error(self):
        tr = ToolResult(
            success=True, data={"ok": True}, duration_ms=10, tool_name="t", request_id="r"
        )
        fmt = tr.to_llm_format()
        assert "ok" in fmt

    def test_tool_execution_log_schema(self):
        log = ToolExecutionLog(
            tool_name="t", user_id="u", request_id="r"
        )
        assert log.tool_name == "t"
        assert log.duration_ms == 0
        assert log.success is False

    def test_tool_audit_entry_schema(self):
        entry = ToolAuditEntry(details={"tool": "test"})
        assert entry.action == "tool_execute"
        assert entry.resource == "tool"
        assert entry.details == {"tool": "test"}


# ─── CallTool Agent Tests ────────────────────────────────────────────────────


class TestCallTool:
    @pytest.mark.asyncio
    async def test_call_tool_success(self, agent):
        result = await agent.call_tool("test_tool", user_id="u1")
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_call_tool_not_found(self, agent):
        with pytest.raises(ToolExecutionError):
            await agent.call_tool("nonexistent", user_id="u1")

    @pytest.mark.asyncio
    async def test_call_tools(self, agent, registry):
        td2 = ToolDefinition(
            name="tool_b",
            description="b",
            handler="ai.agents.memory_agent.prune_expired_memories",
            parameters={
                "type": "object",
                "properties": {"user_id": {"type": "string"}},
                "required": ["user_id"],
            },
        )
        registry.register(td2)
        calls = [
            {"tool_name": "test_tool", "parameters": {"user_id": "u1"}, "user_id": "u1"},
            {"tool_name": "tool_b", "parameters": {"user_id": "u1"}, "user_id": "u1"},
        ]
        results = await agent.call_tools(calls)
        assert len(results) == 2
        assert results[0]["success"] is True
        assert results[1]["success"] is True


# ─── Integration Test ────────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestIntegration:
    async def test_full_flow(self):
        reg = ToolRegistry()
        reg.clear()
        discover_agent_tools(reg)

        assert reg.count() > 20
        assert reg.loaded is True

        ex = ToolExecutor(registry=reg)
        result = await ex.execute(
            "prune_expired_memories",
            {"user_id": "test_user"},
            "test_user",
        )
        assert result.success is True
        assert result.tool_name == "prune_expired_memories"

    async def test_multiple_tool_integration(self):
        reg = ToolRegistry()
        reg.clear()
        discover_agent_tools(reg)

        ex = ToolExecutor(registry=reg)
        calls = [
            {"tool_name": "prune_expired_memories", "parameters": {"user_id": "u1"}},
            {"tool_name": "check_missed_tasks", "parameters": {"user_id": "u1"}},
            {"tool_name": "suggest_bedtime", "parameters": {"user_id": "u1"}},
        ]
        results = await ex.execute_batch(calls, "u1")
        assert len(results) == 3
        for r in results:
            assert r.success is True

    async def test_discover_and_call_via_agent(self):
        reg = ToolRegistry()
        reg.clear()
        discover_agent_tools(reg)

        agent = ToolCallingAgent(registry=reg)
        schemas = agent.get_tool_schemas()
        assert len(schemas) > 0

        result = await agent.call_tool("suggest_bedtime", user_id="test_user")
        assert "suggested_bedtime" in result or isinstance(result, dict)

    async def test_tool_registry_search_categories(self):
        reg = ToolRegistry()
        reg.clear()
        discover_agent_tools(reg)

        search_fn = reg.search("briefing")
        assert len(search_fn) >= 1
        assert any("briefing" in t.name or "briefing" in t.description for t in search_fn)

        cats = reg.get_categories()
        assert "user" in cats

    async def test_all_tools_executable(self):
        reg = ToolRegistry()
        reg.clear()
        discover_agent_tools(reg)

        ex = ToolExecutor(registry=reg)
        results = await ex.execute_batch([
            {"tool_name": "prune_expired_memories", "parameters": {"user_id": "test"}},
            {"tool_name": "check_missed_tasks", "parameters": {"user_id": "test"}},
            {"tool_name": "suggest_bedtime", "parameters": {"user_id": "test"}},
            {"tool_name": "auto_reschedule_overdue", "parameters": {"user_id": "test"}},
        ], "test")
        for r in results:
            assert r.success is True, f"Tool {r.tool_name} failed: {r.error}"


# ─── LLMClient Tool Formatting Tests ─────────────────────────────────────────


class TestLLMClientToolFormatting:
    def test_format_tools_empty(self):
        from ai.client import llm as client
        result = client.format_tools([])
        assert result == ""

    def test_format_tools_with_tools(self):
        from ai.client import llm as client
        tools = [{
            "name": "test_tool",
            "description": "A test",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"},
                },
                "required": ["user_id"],
            },
        }]
        result = client.format_tools(tools)
        assert "test_tool" in result
        assert "User ID" in result

    def test_format_tools_for_openai(self):
        from ai.client import llm as client
        tools = [{"name": "test", "description": "desc", "parameters": {"type": "object"}}]
        formatted = client.format_tools_for_openai(tools)
        assert formatted[0]["type"] == "function"
        assert formatted[0]["function"]["name"] == "test"

    def test_format_tools_for_claude(self):
        from ai.client import llm as client
        tools = [{"name": "test", "description": "desc"}]
        formatted = client.format_tools_for_claude(tools)
        assert formatted[0]["name"] == "test"
        assert "input_schema" in formatted[0]

    def test_parse_openai_tool_calls(self):
        from ai.client import llm as client
        response = {
            "choices": [{
                "message": {
                    "tool_calls": [{
                        "id": "call_1",
                        "function": {
                            "name": "my_tool",
                            "arguments": '{"key": "val"}',
                        },
                    }],
                },
            }],
        }
        calls = client._parse_openai_tool_calls(response)
        assert len(calls) == 1
        assert calls[0]["tool_name"] == "my_tool"

    def test_parse_claude_tool_calls(self):
        from ai.client import llm as client
        response = {
            "content": [
                {"type": "tool_use", "name": "claude_tool", "input": {"x": 1}, "id": "tu_1"},
            ],
        }
        calls = client._parse_claude_tool_calls(response)
        assert len(calls) == 1
        assert calls[0]["tool_name"] == "claude_tool"

    def test_parse_openai_tool_calls_invalid_json(self):
        from ai.client import llm as client
        response = {
            "choices": [{
                "message": {
                    "tool_calls": [{
                        "id": "call_1",
                        "function": {
                            "name": "my_tool",
                            "arguments": "not valid json",
                        },
                    }],
                },
            }],
        }
        calls = client._parse_openai_tool_calls(response)
        assert calls[0]["parameters"] == {}

    def test_parse_tool_calls_from_response_openai(self):
        from ai.client import llm as client
        response = {
            "choices": [{
                "message": {
                    "tool_calls": [{
                        "id": "c1",
                        "function": {"name": "t1", "arguments": '{}'},
                    }],
                },
            }],
        }
        calls = client.parse_tool_calls_from_response(response, provider="openai")
        assert len(calls) == 1

    def test_parse_tool_calls_from_response_claude(self):
        from ai.client import llm as client
        response = {
            "content": [
                {"type": "tool_use", "name": "ct1", "input": {}, "id": "tu1"},
            ],
        }
        calls = client.parse_tool_calls_from_response(response, provider="claude")
        assert len(calls) == 1

    def test_parse_tool_calls_from_response_generic(self):
        from ai.client import llm as client
        response = {
            "response": '{"tool_calls": [{"tool_name": "gt1", "parameters": {"a": 1}}]}',
        }
        calls = client.parse_tool_calls_from_response(response, provider="ollama")
        assert len(calls) == 1
        assert calls[0]["tool_name"] == "gt1"

    def test_parse_generic_tool_calls_no_match(self):
        from ai.client import llm as client
        calls = client._parse_generic_tool_calls({"response": "just text"})
        assert calls == []
