#!/usr/bin/env bash
# Hands-free Jarvis: say "Hey Jarvis" (or press Enter), ask, pause. Answers out loud. Ctrl+C quits.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
mkdir -p .tools/recordings
bash scripts/ollama-up.sh
bash scripts/piper-up.sh || echo "(Piper not started: replies will be text only)"
exec uv run jarvis --listen "$@"
