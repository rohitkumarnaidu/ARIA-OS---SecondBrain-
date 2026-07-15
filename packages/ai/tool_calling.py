"""ToolCalling System — ToolDefinition, ToolRegistry, ToolExecutor, ToolCallingAgent."""

import asyncio
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Optional
from pydantic import BaseModel, Field

from shared.utils.logger import logger
from shared.utils.retry import retry_with_backoff
from shared.utils.audit import log_audit


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    handler: str
    required_permissions: list[str] = Field(default_factory=list)
    timeout: float = 30
    audit: bool = True

    def validate_parameters(self, params: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        if not self.parameters:
            return errors
        schema = self.parameters
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        for req in required:
            if req not in params:
                errors.append(f"Missing required parameter: {req}")
        for key, value in params.items():
            if key in properties:
                prop = properties[key]
                prop_type = prop.get("type")
                if prop_type == "string" and not isinstance(value, str):
                    errors.append(f"Parameter '{key}' expected string, got {type(value).__name__}")
                elif prop_type == "integer" and not isinstance(value, int):
                    errors.append(f"Parameter '{key}' expected integer, got {type(value).__name__}")
                elif prop_type == "number" and not isinstance(value, (int, float)):
                    errors.append(f"Parameter '{key}' expected number, got {type(value).__name__}")
                elif prop_type == "boolean" and not isinstance(value, bool):
                    errors.append(f"Parameter '{key}' expected boolean, got {type(value).__name__}")
                elif prop_type == "array" and not isinstance(value, list):
                    errors.append(f"Parameter '{key}' expected array, got {type(value).__name__}")
                elif prop_type == "object" and not isinstance(value, dict):
                    errors.append(f"Parameter '{key}' expected object, got {type(value).__name__}")
        return errors


class ToolRegistry:
    _instance: Optional["ToolRegistry"] = None
    _tools: dict[str, ToolDefinition] = {}
    _loaded: bool = False

    def __new__(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools = {}
            cls._instance._loaded = False
        return cls._instance

    def register(self, tool: ToolDefinition) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")
        self._tools[tool.name] = tool
        logger.debug("Tool registered", name=tool.name, handler=tool.handler)

    def unregister(self, name: str) -> None:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found in registry")
        del self._tools[name]
        logger.debug("Tool unregistered", name=name)

    def get(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list(self, category: Optional[str] = None) -> list[ToolDefinition]:
        if category is None:
            return list(self._tools.values())
        return [t for t in self._tools.values() if category in t.required_permissions]

    def search(self, query: str) -> list[ToolDefinition]:
        q = query.lower()
        return [
            t
            for t in self._tools.values()
            if q in t.name.lower() or q in t.description.lower()
        ]

    def get_categories(self) -> list[str]:
        cats: set[str] = set()
        for t in self._tools.values():
            cats.update(t.required_permissions)
        return sorted(cats)

    def count(self) -> int:
        return len(self._tools)

    def has(self, name: str) -> bool:
        return name in self._tools

    def clear(self) -> None:
        self._tools.clear()
        self._loaded = False
        logger.debug("Tool registry cleared")

    @property
    def loaded(self) -> bool:
        return self._loaded

    @loaded.setter
    def loaded(self, value: bool) -> None:
        self._loaded = value


class ToolExecutionContext:
    def __init__(
        self,
        tool_name: str,
        parameters: dict[str, Any],
        user_id: str,
        request_id: Optional[str] = None,
        timeout: float = 30,
    ):
        self.tool_name = tool_name
        self.parameters = parameters
        self.user_id = user_id
        self.request_id = request_id or str(uuid.uuid4())
        self.started_at = time.time()
        self.timeout = timeout

    def check_timeout(self) -> None:
        elapsed = time.time() - self.started_at
        if elapsed > self.timeout:
            raise TimeoutError(
                f"Tool '{self.tool_name}' exceeded timeout of {self.timeout}s "
                f"(elapsed: {elapsed:.2f}s)"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "user_id": self.user_id,
            "request_id": self.request_id,
            "started_at": datetime.fromtimestamp(self.started_at, tz=timezone.utc).isoformat(),
            "timeout": self.timeout,
        }


class ToolResult(BaseModel):
    success: bool
    data: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: int = 0
    tool_name: str
    request_id: str

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)

    def to_llm_format(self) -> str:
        if self.success:
            formatted = json.dumps(self.data or {}, indent=2, default=str)
            return f"Tool '{self.tool_name}' completed successfully in {self.duration_ms}ms:\n{formatted}"
        return (
            f"Tool '{self.tool_name}' failed after {self.duration_ms}ms: "
            f"{self.error or 'Unknown error'}"
        )


class ToolNotFoundError(Exception):
    pass


class ToolExecutionError(Exception):
    pass


class ToolPermissionError(Exception):
    pass


def _resolve_handler(handler_path: str) -> Callable:
    parts = handler_path.split(".")
    module_name = ".".join(parts[:-1])
    func_name = parts[-1]
    try:
        import importlib
        module = importlib.import_module(module_name)
        handler = getattr(module, func_name, None)
        if handler is None:
            raise ToolNotFoundError(f"Handler '{func_name}' not found in module '{module_name}'")
        return handler
    except ImportError as e:
        raise ToolNotFoundError(f"Cannot import handler module '{module_name}': {e}")


class ToolExecutor:
    def __init__(self, registry: Optional[ToolRegistry] = None):
        self.registry = registry or ToolRegistry()

    async def execute(
        self,
        tool_name: str,
        parameters: dict[str, Any],
        user_id: str,
        request_id: Optional[str] = None,
    ) -> ToolResult:
        tool = self.registry.get(tool_name)
        if tool is None:
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' not found in registry",
                duration_ms=0,
                tool_name=tool_name,
                request_id=request_id or str(uuid.uuid4()),
            )

        rid = request_id or str(uuid.uuid4())
        ctx = ToolExecutionContext(
            tool_name=tool_name,
            parameters=parameters,
            user_id=user_id,
            request_id=rid,
            timeout=tool.timeout,
        )

        validation_errors = tool.validate_parameters(parameters)
        if validation_errors:
            return ToolResult(
                success=False,
                error=f"Parameter validation failed: {'; '.join(validation_errors)}",
                duration_ms=0,
                tool_name=tool_name,
                request_id=rid,
            )

        try:
            handler = _resolve_handler(tool.handler)
        except ToolNotFoundError as e:
            return ToolResult(
                success=False,
                error=str(e),
                duration_ms=0,
                tool_name=tool_name,
                request_id=rid,
            )

        start = time.time()
        try:
            import inspect
            sig = inspect.signature(handler)
            filtered_params = {k: v for k, v in parameters.items() if k in sig.parameters}
            result = await asyncio.wait_for(
                handler(**filtered_params),
                timeout=tool.timeout,
            )
            duration_ms = int((time.time() - start) * 1000)

            if tool.audit:
                try:
                    await log_audit(
                        user_id=user_id,
                        action="tool_execute",
                        resource=f"tool:{tool_name}",
                        resource_id=rid,
                        details={"parameters": {k: v for k, v in parameters.items() if k != "password"}},
                    )
                except Exception as audit_err:
                    logger.warn("Audit log failed for tool execution", tool=tool_name, error=str(audit_err))

            logger.info(
                "Tool executed successfully",
                tool=tool_name,
                duration_ms=duration_ms,
                user_id=user_id,
            )

            return ToolResult(
                success=True,
                data=result if isinstance(result, dict) else {"result": result},
                duration_ms=duration_ms,
                tool_name=tool_name,
                request_id=rid,
            )

        except asyncio.TimeoutError:
            duration_ms = int((time.time() - start) * 1000)
            logger.error("Tool execution timed out", tool=tool_name, timeout=tool.timeout)
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' timed out after {tool.timeout}s",
                duration_ms=duration_ms,
                tool_name=tool_name,
                request_id=rid,
            )
        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            logger.error("Tool execution failed", tool=tool_name, error=str(e), error_type=type(e).__name__)
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' failed: {e}",
                duration_ms=duration_ms,
                tool_name=tool_name,
                request_id=rid,
            )

    async def execute_batch(
        self,
        tool_calls: list[dict[str, Any]],
        user_id: str,
    ) -> list[ToolResult]:
        tasks = []
        for call in tool_calls:
            tasks.append(
                self.execute(
                    tool_name=call["tool_name"],
                    parameters=call.get("parameters", {}),
                    user_id=user_id,
                    request_id=call.get("request_id"),
                )
            )
        results = await asyncio.gather(*tasks, return_exceptions=True)
        final: list[ToolResult] = []
        for i, result in enumerate(results):
            if isinstance(result, ToolResult):
                final.append(result)
            elif isinstance(result, Exception):
                call = tool_calls[i]
                final.append(
                    ToolResult(
                        success=False,
                        error=f"Batch execution failed: {result}",
                        duration_ms=0,
                        tool_name=call["tool_name"],
                        request_id=call.get("request_id", str(uuid.uuid4())),
                    )
                )
            else:
                call = tool_calls[i]
                final.append(
                    ToolResult(
                        success=True,
                        data={"result": result},
                        duration_ms=0,
                        tool_name=call["tool_name"],
                        request_id=call.get("request_id", str(uuid.uuid4())),
                    )
                )
        return final

    async def execute_with_retry(
        self,
        tool_name: str,
        parameters: dict[str, Any],
        user_id: str,
        max_retries: int = 2,
    ) -> ToolResult:
        tool = self.registry.get(tool_name)
        if tool is None:
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' not found in registry",
                duration_ms=0,
                tool_name=tool_name,
                request_id=str(uuid.uuid4()),
            )

        rid = str(uuid.uuid4())
        start = time.time()

        async def attempt() -> dict[str, Any]:
            handler = _resolve_handler(tool.handler)
            result = await asyncio.wait_for(handler(**parameters), timeout=tool.timeout)
            return result if isinstance(result, dict) else {"result": result}

        try:
            data = await retry_with_backoff(
                attempt,
                max_retries=max_retries,
                base_delay=1.0,
                exceptions=(TimeoutError, ToolExecutionError, ConnectionError),
            )
            duration_ms = int((time.time() - start) * 1000)
            return ToolResult(
                success=True,
                data=data,
                duration_ms=duration_ms,
                tool_name=tool_name,
                request_id=rid,
            )
        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' failed after {max_retries} retries: {e}",
                duration_ms=duration_ms,
                tool_name=tool_name,
                request_id=rid,
            )

    async def execute_tool_call(
        self,
        tool_name: str,
        parameters: dict[str, Any],
        user_id: str,
        request_id: Optional[str] = None,
    ) -> dict[str, Any]:
        result = await self.execute(tool_name, parameters, user_id, request_id)
        if result.success and result.data is not None:
            return result.data
        if result.error:
            raise ToolExecutionError(result.error)
        raise ToolExecutionError(f"Tool '{tool_name}' returned no data")


class ToolCallingAgent:
    def __init__(
        self,
        executor: Optional[ToolExecutor] = None,
        registry: Optional[ToolRegistry] = None,
    ):
        self.executor = executor or ToolExecutor(registry=registry or ToolRegistry())
        self.registry = self.executor.registry

    async def call_tool(self, tool_name: str, **kwargs: Any) -> dict[str, Any]:
        user_id = kwargs.pop("user_id", "system")
        kwargs["user_id"] = user_id
        result = await self.executor.execute(tool_name, kwargs, user_id)
        if result.success and result.data is not None:
            return result.data
        if result.error:
            raise ToolExecutionError(result.error)
        return {"error": result.error or "Unknown error"}

    async def call_tools(self, tool_calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
        user_id = tool_calls[0].get("user_id", "system") if tool_calls else "system"
        results = await self.executor.execute_batch(tool_calls, user_id)
        return [r.to_dict() for r in results]

    def get_tool_schemas(self) -> list[dict[str, Any]]:
        schemas: list[dict[str, Any]] = []
        for tool in self.registry.list():
            schema = {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            }
            schemas.append(schema)
        return schemas

    def format_tools_for_llm(self) -> str:
        tools = self.registry.list()
        if not tools:
            return "No tools available."
        lines: list[str] = ["## Available Tools", ""]
        for tool in tools:
            lines.append(f"### {tool.name}")
            lines.append(f"**Description:** {tool.description}")
            if tool.parameters:
                lines.append(f"**Parameters:** {json.dumps(tool.parameters, indent=2)}")
            lines.append("")
        return "\n".join(lines)

    def format_for_openai(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in self.registry.list()
        ]

    def format_for_claude(self) -> list[dict[str, Any]]:
        tools: list[dict[str, Any]] = []
        for tool in self.registry.list():
            entry: dict[str, Any] = {
                "name": tool.name,
                "description": tool.description,
            }
            if tool.parameters:
                entry["input_schema"] = tool.parameters
            else:
                entry["input_schema"] = {"type": "object", "properties": {}}
            tools.append(entry)
        return tools

    def parse_tool_calls_from_openai(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        calls: list[dict[str, Any]] = []
        choices = response.get("choices", [])
        for choice in choices:
            message = choice.get("message", {})
            tool_calls = message.get("tool_calls", [])
            for tc in tool_calls:
                function = tc.get("function", {})
                try:
                    arguments = json.loads(function.get("arguments", "{}"))
                except (json.JSONDecodeError, TypeError):
                    arguments = {}
                calls.append({
                    "tool_name": function.get("name", ""),
                    "parameters": arguments,
                    "request_id": tc.get("id"),
                })
        return calls

    def parse_tool_calls_from_claude(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        calls: list[dict[str, Any]] = []
        content = response.get("content", [])
        for block in content:
            if block.get("type") == "tool_use":
                calls.append({
                    "tool_name": block.get("name", ""),
                    "parameters": block.get("input", {}),
                    "request_id": block.get("id"),
                })
        return calls


tool_agent = ToolCallingAgent()
