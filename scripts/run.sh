#!/usr/bin/env bash
# Terminal chat (default) or API server: scripts/run.sh --api
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
bash scripts/ollama-up.sh
if [ "${1:-}" = "--api" ]; then exec uv run jarvis-api; fi
exec uv run jarvis
