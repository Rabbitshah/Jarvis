#!/usr/bin/env bash
# Talk to Jarvis: Enter, speak, Enter. The answer prints as text (voice reply comes on Day 26).
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
mkdir -p .tools/recordings
bash scripts/ollama-up.sh
exec uv run jarvis --voice
