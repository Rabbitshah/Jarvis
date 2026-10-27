#!/usr/bin/env bash
# Make Piper say something:  scripts/say.sh "Hello, I am Jarvis"
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
mkdir -p .tools/recordings
bash scripts/piper-up.sh
exec uv run jarvis --say "${1:?usage: scripts/say.sh \"text to say\"}"
