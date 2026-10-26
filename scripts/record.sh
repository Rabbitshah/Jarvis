#!/usr/bin/env bash
# Record the microphone (Enter starts, Enter stops), then play it back.
#   scripts/record.sh            -> .tools/recordings/test.wav
#   scripts/record.sh --devices  -> list microphones
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
mkdir -p .tools/recordings
if [ "${1:-}" = "--devices" ]; then exec uv run jarvis --devices; fi
exec uv run jarvis --record "${1:-.tools/recordings/test.wav}"
