#!/usr/bin/env bash
# Turn a WAV into text with the configured Whisper:  scripts/transcribe.sh .tools/recordings/clip1.wav
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
exec uv run jarvis --transcribe "${1:?usage: scripts/transcribe.sh file.wav}"
