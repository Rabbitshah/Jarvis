#!/usr/bin/env bash
# Check that questions find the right note (cases live in notes/eval-cases.toml, which is private).
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
bash scripts/ollama-up.sh
exec uv run python scripts/search_eval.py
