import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.server.fastmcp import FastMCP

TARGET = StdioServerParameters(command=sys.executable, args=["demo_server.py"])

proxy = FastMCP("approval-proxy")


async def call_target(tool_name: str, arguments: dict):
    async with stdio_client(TARGET) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return [c.text for c in result.content]


@proxy.tool()
async def list_notes() -> list[str]:
    """List the notes in the sandbox folder."""
    return await call_target("list_notes", {})


@proxy.tool()
async def read_note(name: str) -> list[str]:
    """Read a note by file name."""
    return await call_target("read_note", {"name": name})


@proxy.tool()
async def delete_note(name: str) -> list[str]:
    """Delete a note by file name."""
    return await call_target("delete_note", {"name": name})


@proxy.tool()
async def send_message(to: str, text: str) -> list[str]:
    """Pretend to send a message."""
    return await call_target("send_message", {"to": to, "text": text})


if __name__ == "__main__":
    proxy.run()