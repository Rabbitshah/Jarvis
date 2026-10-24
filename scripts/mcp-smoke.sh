#!/usr/bin/env bash
# Start the MCP server over stdio and call every tool once. Needs Ollama (for search_notes), not Node.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
bash scripts/ollama-up.sh   # search_notes needs the embedding model
exec uv run python scripts/mcp_smoke.py
