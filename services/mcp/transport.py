"""Transport layer for ARIA OS MCP server — stdio and HTTP/SSE transports."""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "packages"))

from mcp.server import NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from services.mcp.server import ARIAServer
from shared.utils.logger import logger


class StdioTransport:
    """Run MCP server over standard input/output."""

    async def serve(self):
        server = ARIAServer()
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("MCP stdio transport started")
            await server.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="aria-os",
                    server_version="1.0.0",
                    capabilities=server.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )


class SSETransport:
    """Run MCP server over Server-Sent Events (HTTP)."""

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.server = ARIAServer()

    async def serve(self):
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Route, Mount
        from starlette.responses import JSONResponse
        import uvicorn

        sse_transport = SseServerTransport("/mcp/")

        async def handle_sse(scope, receive, send):
            async with sse_transport.connect_sse(
                scope, receive, send
            ) as (read_stream, write_stream):
                await self.server.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="aria-os",
                        server_version="1.0.0",
                        capabilities=self.server.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    ),
                )

        async def handle_health(request):
            return JSONResponse({
                "status": "healthy",
                "server": "aria-os-mcp",
                "transport": "sse",
                "uptime_seconds": self.server.uptime_seconds,
                "tools_count": len(self.server.tool_registry.list_tools()),
            })

        async def handle_tools_list(request):
            tools = self.server.tool_registry.list_tools()
            return JSONResponse({
                "tools": [
                    {
                        "name": t.name,
                        "description": t.description,
                        "input_schema": t.inputSchema,
                    }
                    for t in tools
                ]
            })

        async def handle_tool_call(request):
            try:
                body = await request.json()
            except Exception:
                return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

            name = body.get("name")
            arguments = body.get("arguments", {})
            if not name:
                return JSONResponse({"error": "Missing 'name' field"}, status_code=400)

            result = await self.server.tool_registry.execute_tool(name, arguments)
            return JSONResponse({
                "content": [
                    {"type": r.type, "text": r.text}
                    for r in result
                ]
            })

        routes = [
            Mount("/mcp", routes=[
                Route("/sse", endpoint=handle_sse),
            ]),
            Route("/health", endpoint=handle_health),
            Route("/tools", endpoint=handle_tools_list),
            Route("/tools/{name}", endpoint=handle_tool_call, methods=["POST"]),
        ]

        app = Starlette(routes=routes)

        config = uvicorn.Config(app, host=self.host, port=self.port, log_level="info")
        server = uvicorn.Server(config)
        logger.info("MCP SSE transport starting", host=self.host, port=self.port)
        await server.serve()


def create_transport(transport_type: str = "stdio", host: str = "localhost", port: int = 8765):
    """Factory function to create the appropriate transport.

    Args:
        transport_type: "stdio" or "sse"
        host: Host to bind for SSE transport
        port: Port to bind for SSE transport

    Returns:
        A transport instance with a serve() method
    """
    if transport_type == "stdio":
        return StdioTransport()
    elif transport_type == "sse":
        return SSETransport(host=host, port=port)
    else:
        raise ValueError(f"Unsupported transport type: {transport_type}")
