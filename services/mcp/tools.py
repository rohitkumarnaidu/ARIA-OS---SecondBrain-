"""MCP tool definitions — bridges ARIA OS ToolRegistry with MCP tool format."""

import json
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "packages"))

import mcp.types as types
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from ai.tool_registry import get_registry
from ai.tool_calling import ToolExecutor, ToolNotFoundError
from shared.utils.logger import logger


class MCPToolRegistry:
    """Bridges ARIA OS ToolRegistry with MCP tool format.

    Discovers all registered agent tools and wraps them as MCP Tool objects.
    Provides caching and execution routing.
    """

    def __init__(self):
        self._executor: Optional[ToolExecutor] = None
        self._aria_registry = None
        self._tool_cache: list[Tool] = []
        self._cache_valid = False

    @property
    def executor(self) -> ToolExecutor:
        if self._executor is None:
            self._executor = ToolExecutor()
        return self._executor

    @property
    def aria_registry(self):
        if self._aria_registry is None:
            self._aria_registry = get_registry()
        return self._aria_registry

    def discover(self):
        """Discover all tools from ARIA OS ToolRegistry and cache MCP Tool objects."""
        aria_tools = self.aria_registry.list()
        self._tool_cache = []
        for tool_def in aria_tools:
            mcp_tool = self._convert_to_mcp_tool(tool_def)
            self._tool_cache.append(mcp_tool)
        self._cache_valid = True
        logger.info("MCP tools discovered", count=len(self._tool_cache))

    def _convert_to_mcp_tool(self, tool_def) -> Tool:
        """Convert a ToolDefinition to an MCP Tool."""
        return Tool(
            name=tool_def.name,
            description=tool_def.description,
            inputSchema=tool_def.parameters or {"type": "object", "properties": {}},
        )

    def list_tools(self) -> list[Tool]:
        """Return cached list of MCP Tool objects."""
        if not self._cache_valid:
            self.discover()
        return self._tool_cache

    async def execute_tool(
        self, name: str, arguments: dict[str, Any]
    ) -> list[TextContent | ImageContent | EmbeddedResource]:
        """Execute a tool via ARIA OS ToolExecutor and return MCP content."""
        aria_tool = self.aria_registry.get(name)
        if aria_tool is None:
            return [
                TextContent(
                    type="text",
                    text=f"Unknown tool: {name}",
                )
            ]

        result = await self.executor.execute(
            tool_name=name,
            parameters=arguments,
            user_id=arguments.pop("user_id", "mcp-client"),
            request_id=str(uuid.uuid4()),
        )

        if result.success and result.data is not None:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(result.data, indent=2, default=str),
                )
            ]
        elif result.error:
            return [
                TextContent(
                    type="text",
                    text=f"Tool '{name}' failed: {result.error}",
                )
            ]

        return [
            TextContent(
                type="text",
                text=f"Tool '{name}' completed (no data returned)",
            )
        ]
