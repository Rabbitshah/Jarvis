#!/usr/bin/env bash
# Try the wake word: live scores for "Hey Jarvis". Leave it running while you talk or play music to count false triggers.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
exec uv run jarvis --wake-test
