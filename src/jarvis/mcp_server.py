"""MCP server (stdio). Absolute imports on purpose: `mcp run file.py` loads this as a loose script.

Registers the SAME tool functions the agent uses (see tools/builtin.py)."""
from __future__ import annotations

import functools

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError as McpToolError

from jarvis.config import Config, load_config
from jarvis.tools.builtin import build_registry
from jarvis.tools.registry import ToolError


def _expose(fn):
    """Same function, but our expected errors become MCP errors the client can read.

    The SDK hides every other exception's text on purpose; that stays as is.
    """
    @functools.wraps(fn)  # keeps the signature, so the SDK still builds the schema from it
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ToolError as exc:
            raise McpToolError(str(exc)) from exc

    return wrapper


def build_server(cfg: Config | None = None) -> MCPServer:
    server = MCPServer("Jarvis")
    for tool in build_registry(cfg or load_config()).tools():
        server.add_tool(_expose(tool.fn), name=tool.name, description=tool.description)
    return server


mcp = build_server()  # module-level name lets `mcp dev` / `mcp run` find it


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
