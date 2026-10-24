import asyncio
import sys

from mcp import Client, StdioServerParameters


def run_client(coro):
    return asyncio.run(asyncio.wait_for(coro, timeout=30))


SERVER = StdioServerParameters(command=sys.executable, args=["-m", "jarvis.mcp_server"])


def test_lists_hello_tool():
    async def go():
        async with Client(SERVER) as client:
            return [t.name for t in (await client.list_tools()).tools]

    assert run_client(go()) == ["hello"]


def test_calls_hello_tool():
    async def go():
        async with Client(SERVER) as client:
            return await client.call_tool("hello", {"name": "Maanav"})

    result = run_client(go())
    assert not result.is_error
    assert "Hello, Maanav" in result.content[0].text
