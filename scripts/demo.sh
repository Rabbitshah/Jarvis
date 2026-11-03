#!/usr/bin/env bash
# Try Jarvis on invented notes (demo/notes), with a separate index. Your real notes and index are not touched.
#   bash scripts/demo.sh          voice mode (Enter, speak, Enter)
#   bash scripts/demo.sh --text   typed chat
#   bash scripts/demo.sh --listen hands-free ("Hey Jarvis")
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
export JARVIS_NOTES_DIR="$ROOT/demo/notes"
export JARVIS_INDEX_DIR="$ROOT/.tools/qdrant-demo"
mkdir -p .tools/recordings
bash scripts/ollama-up.sh
uv run jarvis --ingest
case "${1:-}" in
  --text)   exec uv run jarvis ;;
  --listen) bash scripts/piper-up.sh || true; exec uv run jarvis --listen ;;
  *)        bash scripts/piper-up.sh || true; exec uv run jarvis --voice ;;
esac
