import asyncio
import contextlib
import sys

import mcp.server.stdio
import mcp.types as types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.server import Server

TARGET = StdioServerParameters(command=sys.executable, args=["demo_server.py"])

server = Server("approval-proxy")
target_session: ClientSession | None = None


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    result = await target_session.list_tools()
    return result.tools


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    result = await target_session.call_tool(name, arguments)
    return result.content


async def main():
    global target_session
    async with contextlib.AsyncExitStack() as stack:
        read, write = await stack.enter_async_context(stdio_client(TARGET))
        target_session = await stack.enter_async_context(ClientSession(read, write))
        await target_session.initialize()

        async with mcp.server.stdio.stdio_server() as (in_stream, out_stream):
            await server.run(in_stream, out_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())