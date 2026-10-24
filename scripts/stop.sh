#!/usr/bin/env bash
# Stop the repo-local Ollama server (the only background process Jarvis starts).
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
PIDFILE="$ROOT/.tools/ollama.pid"
if [ -f "$PIDFILE" ] && kill "$(cat "$PIDFILE")" 2>/dev/null; then
  rm -f "$PIDFILE"
  echo "Ollama stopped."
elif pkill -f "$ROOT/.tools/ollama/ollama serve" 2>/dev/null; then
  echo "Ollama stopped."
else
  echo "Nothing running."
fi
