import asyncio
import sys

from mcp import Client, StdioServerParameters

from jarvis.mcp_server import build_server
from jarvis.tools.builtin import build_registry


def run(coro):
    return asyncio.run(asyncio.wait_for(coro, timeout=30))


def stdio_params(cfg):
    return StdioServerParameters(
        command=sys.executable, args=["-m", "jarvis.mcp_server"],
        env={"JARVIS_NOTES_DIR": str(cfg.notes_dir)},
    )


def test_same_tools_as_agent(cfg):
    async def go():
        async with Client(build_server(cfg)) as client:
            return (await client.list_tools()).tools

    mcp_tools = {t.name: t for t in run(go())}
    registry = build_registry(cfg)
    assert sorted(mcp_tools) == registry.names()
    for tool in registry.tools():
        schema = mcp_tools[tool.name].input_schema
        assert set(schema.get("properties", {})) == set(tool.parameters.get("properties", {})), tool.name
        assert set(schema.get("required", [])) == set(tool.parameters.get("required", [])), tool.name
        assert mcp_tools[tool.name].description == tool.description


def test_stdio_reads_a_note(cfg):
    async def go():
        async with Client(stdio_params(cfg)) as client:
            return await client.call_tool("read_note", {"path": "idea.md"})

    result = run(go())
    assert not result.is_error
    assert "December" in result.content[0].text


def test_stdio_sandbox_error_is_flagged(cfg):
    async def go():
        async with Client(stdio_params(cfg)) as client:
            return await client.call_tool("read_note", {"path": "../secret.md"})

    result = run(go())
    assert result.is_error
    assert "escapes" in result.content[0].text


def test_works_through_mcp_run_like_the_inspector(cfg):
    # `mcp dev` / `mcp run` load the file as a loose script: relative imports would break here.
    from pathlib import Path

    from jarvis import mcp_server

    params = StdioServerParameters(
        command=str(Path(sys.executable).parent / "mcp"), args=["run", mcp_server.__file__],
        env={"JARVIS_NOTES_DIR": str(cfg.notes_dir)},
    )

    async def go():
        async with Client(params) as client:
            return sorted(t.name for t in (await client.list_tools()).tools)

    assert run(go()) == ["get_time", "list_notes", "read_note", "search_notes"]


def test_stdio_bad_input_is_flagged(cfg):
    async def go():
        async with Client(stdio_params(cfg)) as client:
            return [await client.call_tool("read_note", {}), await client.call_tool("read_note", {"path": 5})]

    for result in run(go()):
        assert result.is_error


def test_slow_tool_times_out_over_mcp(cfg):
    import dataclasses
    import time

    from jarvis.tools.registry import Tool

    slow = Tool("slow", "sleeps", {"type": "object", "properties": {}}, lambda: time.sleep(2) or "late")
    cfg2 = dataclasses.replace(cfg, tool_timeout_seconds=0.2)

    from jarvis import mcp_server
    from mcp.server import MCPServer

    server = MCPServer("t")
    server.add_tool(mcp_server._expose(slow.fn, cfg2.tool_timeout_seconds), name="slow", description="x")

    async def go():
        async with Client(server) as client:
            return await client.call_tool("slow", {})

    result = run(go())
    assert result.is_error
    assert "timed out" in result.content[0].text
