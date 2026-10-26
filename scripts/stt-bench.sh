#!/usr/bin/env bash
# Compare faster-whisper and mlx-whisper on your clips in .tools/recordings (downloads models into models/hf).
#   scripts/stt-bench.sh                      -> default 4 engines
#   scripts/stt-bench.sh --spec faster:small  -> only the ones you name
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
exec uv run --group bench python scripts/stt_bench.py "$@"
