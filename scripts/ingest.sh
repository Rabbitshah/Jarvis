#!/usr/bin/env bash
# Read notes/, embed them with Ollama, store them in the local index (.tools/qdrant).
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
bash scripts/ollama-up.sh
exec uv run jarvis --ingest
