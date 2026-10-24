"""Smoke test: start the Jarvis MCP server over stdio and use it like a real client.

Uses your real notes/ folder. Prints PASS/FAIL per step, exits 1 on any failure.
Run: bash scripts/mcp-smoke.sh
"""
import asyncio
import sys

from mcp import Client, StdioServerParameters

EXPECTED = {"get_time", "list_notes", "read_note", "search_notes"}
failed = False


def check(label: str, ok: bool, detail: str = "") -> None:
    global failed
    failed = failed or not ok
    print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f"  ({detail})" if detail else ""))


async def main() -> None:
    params = StdioServerParameters(command=sys.executable, args=["-m", "jarvis.mcp_server"])
    async with Client(params) as client:
        names = {t.name for t in (await client.list_tools()).tools}
        check("lists the 4 tools", names == EXPECTED, ", ".join(sorted(names)))

        r = await client.call_tool("get_time", {})
        check("get_time works", not r.is_error and "local time" in r.content[0].text, r.content[0].text)

        r = await client.call_tool("list_notes", {})
        listing = r.content[0].text
        check("list_notes works", not r.is_error, listing.splitlines()[0] if listing else "empty")

        r = await client.call_tool("search_notes", {"query": "which schools still need a statement of purpose"})
        text = r.content[0].text
        check("search_notes finds notes by meaning (needs Ollama + ingest)",
              not r.is_error and ".md" in text, text.splitlines()[1] if text.count("\n") else text[:80])

        r = await client.call_tool("search_notes", {"query": ""})
        check("empty search gives an error", r.is_error, r.content[0].text[:60])

        r = await client.call_tool("read_note", {"path": "../README.md"})
        check("../ is blocked", r.is_error and "escapes" in r.content[0].text, r.content[0].text)

        r = await client.call_tool("read_note", {})
        check("missing path gives an error", r.is_error, r.content[0].text[:80])

        r = await client.call_tool("read_note", {"path": 5})
        check("wrong type gives an error", r.is_error, r.content[0].text[:80])


try:
    asyncio.run(asyncio.wait_for(main(), timeout=60))
except Exception as exc:  # noqa: BLE001
    print(f"FAIL  smoke test crashed: {exc!r}")
    failed = True
print("\nALL GOOD" if not failed else "\nSOMETHING FAILED")
sys.exit(1 if failed else 0)
