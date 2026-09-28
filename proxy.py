import asyncio
import contextlib
import json
import sys
import uuid
from pathlib import Path

import mcp.server.stdio
import mcp.types as types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.server import Server

from policy import Policy

TARGET = StdioServerParameters(command=sys.executable, args=["demo_server.py"])

server = Server("approval-proxy")
target_session: ClientSession | None = None
policy = Policy("policy.yaml")

APPROVALS_DIR = Path(__file__).parent / "approvals"
APPROVALS_DIR.mkdir(exist_ok=True)


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    result = await target_session.list_tools()
    return result.tools


async def ask_human(name: str, arguments: dict) -> bool:
    request_id = uuid.uuid4().hex[:8]
    request_path = APPROVALS_DIR / f"{request_id}.request.json"
    response_path = APPROVALS_DIR / f"{request_id}.response.json"

    request_path.write_text(json.dumps({"tool": name, "arguments": arguments}))

    while not response_path.exists():
        await asyncio.sleep(0.5)

    response = json.loads(response_path.read_text())
    request_path.unlink(missing_ok=True)
    response_path.unlink(missing_ok=True)
    return response.get("approved", False)


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    decision = policy.decide(name)

    if decision == "deny":
        return [types.TextContent(type="text", text=f"blocked by policy: {name}")]

    if decision == "ask":
        if not await ask_human(name, arguments):
            return [types.TextContent(type="text", text=f"denied by user: {name}")]

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