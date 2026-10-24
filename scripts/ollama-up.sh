#!/usr/bin/env bash
# Start the repo-local Ollama server if it is not already running.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
if curl -fs "http://$OLLAMA_HOST/api/tags" >/dev/null 2>&1; then exit 0; fi
mkdir -p "$ROOT/.tools"
nohup "$ROOT/.tools/ollama/ollama" serve > "$ROOT/.tools/ollama.log" 2>&1 &
echo $! > "$ROOT/.tools/ollama.pid"
for _ in $(seq 1 40); do
  curl -fs "http://$OLLAMA_HOST/api/tags" >/dev/null 2>&1 && exit 0
  sleep 0.5
done
echo "Ollama did not start. See .tools/ollama.log" >&2
exit 1
