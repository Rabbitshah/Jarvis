#!/usr/bin/env bash
# See what the model was sent and what it answered, for one question: scripts/debug-turn.sh "what time is it"
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
bash scripts/ollama-up.sh
exec uv run python scripts/debug_turn.py "$@"
