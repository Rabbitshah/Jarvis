#!/usr/bin/env bash
# Show the top note matches and their scores for one or more questions:
#   scripts/search.sh "tell me a fun fact" "what is the capital of France"
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
bash scripts/ollama-up.sh
for q in "$@"; do
  echo "== $q"
  uv run jarvis --search "$q" -k 3
done
