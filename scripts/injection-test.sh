#!/usr/bin/env bash
# Prompt-injection test with made-up notes. Needs Ollama. Writes docs/INJECTION.md.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
bash scripts/ollama-up.sh
exec uv run python scripts/injection_test.py "$@"
