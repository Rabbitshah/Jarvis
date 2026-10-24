#!/usr/bin/env bash
# Open the MCP Inspector (a Node app) against the Jarvis MCP server.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
command -v npx >/dev/null || bash scripts/install-node.sh
exec uv run mcp dev src/jarvis/mcp_server.py
