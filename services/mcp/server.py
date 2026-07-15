"""MCP Server for ARIA OS — exposes tools, resources, and prompts via Model Context Protocol."""

import asyncio
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "packages"))

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from services.mcp.tools import MCPToolRegistry
from services.mcp.resources import MCPResourceRegistry
from services.mcp.prompts import MCPPromptRegistry
from shared.utils.logger import logger


class ARIAServer:
    """MCP server for ARIA OS tools, resources, and prompts."""

    def __init__(self):
        self.server = Server("aria-os")
        self.tool_registry = MCPToolRegistry()
        self.resource_registry = MCPResourceRegistry()
        self.prompt_registry = MCPPromptRegistry()
        self._started_at = time.time()
        self._request_count = 0
        self._setup_handlers()

    @property
    def uptime_seconds(self) -> float:
        return time.time() - self._started_at

    def _setup_handlers(self):
        self.tool_registry.discover()
        self.resource_registry.discover()
        self.prompt_registry.discover()

        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            return self.tool_registry.list_tools()

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any]
        ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            self._request_count += 1
            start = time.time()
            logger.info("MCP tool call", tool=name, arguments=list(arguments.keys()))

            try:
                result = await self.tool_registry.execute_tool(name, arguments)
                duration_ms = int((time.time() - start) * 1000)
                logger.info("MCP tool completed", tool=name, duration_ms=duration_ms)
                return result
            except Exception as e:
                duration_ms = int((time.time() - start) * 1000)
                logger.error("MCP tool error", tool=name, error=str(e), duration_ms=duration_ms)
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error executing tool '{name}': {e}",
                    )
                ]

        @self.server.list_resources()
        async def handle_list_resources() -> list[types.Resource]:
            return self.resource_registry.list_resources()

        @self.server.read_resource()
        async def handle_read_resource(
            uri: str,
        ) -> list[types.ResourceContents]:
            return await self.resource_registry.read_resource(uri)

        @self.server.list_prompts()
        async def handle_list_prompts() -> list[types.Prompt]:
            return self.prompt_registry.list_prompts()

        @self.server.get_prompt()
        async def handle_get_prompt(
            name: str, arguments: Optional[dict[str, str]] = None
        ) -> types.GetPromptResult:
            return self.prompt_registry.get_prompt(name, arguments or {})

    async def run(self):
        """Run the server with stdio transport."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("MCP server starting with stdio transport")
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="aria-os",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )


async def main():
    server = ARIAServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
