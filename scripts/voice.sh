#!/usr/bin/env bash
# Talk to Jarvis: Enter, speak, Enter. Jarvis answers in text and out loud (Piper). --no-speak = text only.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
mkdir -p .tools/recordings
bash scripts/ollama-up.sh
bash scripts/piper-up.sh || echo "(Piper not started: replies will be text only)"
exec uv run jarvis --voice "$@"
