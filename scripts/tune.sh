#!/usr/bin/env bash
# Compare chunk sizes / prefixes on the search test cases. Uses a throw-away index.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
bash scripts/ollama-up.sh
exec uv run python scripts/tune.py
