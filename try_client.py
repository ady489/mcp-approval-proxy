import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

params = StdioServerParameters(command=sys.executable, args=["proxy.py"])


async def main():
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("tools:", [t.name for t in tools.tools])

            result = await session.call_tool("list_notes", {})
            print("notes:", [c.text for c in result.content])

            result = await session.call_tool("read_note", {"name": "todo.txt"})
            print("todo.txt:", [c.text for c in result.content])


asyncio.run(main())