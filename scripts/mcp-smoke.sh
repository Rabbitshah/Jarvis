#!/usr/bin/env bash
# Start the MCP server over stdio and call every tool once. No model or Node needed.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
exec uv run python scripts/mcp_smoke.py
