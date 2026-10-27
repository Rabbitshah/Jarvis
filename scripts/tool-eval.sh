#!/usr/bin/env bash
# Score a model on the questions Jarvis must get right (time, date, general knowledge, "cannot see your calendar", notes).
#   scripts/tool-eval.sh llama3.1:8b
#   scripts/tool-eval.sh qwen2.5:7b      (pulls it first if missing, ~5 GB)
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
MODEL="${1:?usage: scripts/tool-eval.sh <model> [--trials N]}"
bash scripts/ollama-up.sh
if ! ollama list | awk 'NR>1{print $1}' | grep -qx "$MODEL"; then ollama pull "$MODEL"; fi
shift
exec uv run python scripts/tool_eval.py "$MODEL" "$@"
