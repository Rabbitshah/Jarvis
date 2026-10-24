"""MCP server (stdio). Day 2: one hello tool. Days 3-4 swap in the real notes tools."""
from __future__ import annotations

from mcp.server import MCPServer

mcp = MCPServer("Jarvis")


@mcp.tool()
def hello(name: str = "world") -> str:
    """Say hello. Used only to check that the MCP connection works."""
    return f"Hello, {name}! Jarvis MCP is working."


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
