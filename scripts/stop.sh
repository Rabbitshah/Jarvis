#!/usr/bin/env bash
# Stop the background servers Jarvis starts: Ollama and Piper.
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
stop_one() {  # name pidfile pattern
  if [ -f "$2" ] && kill "$(cat "$2")" 2>/dev/null; then
    rm -f "$2"; echo "$1 stopped."
  elif pkill -f "$3" 2>/dev/null; then
    echo "$1 stopped."
  else
    echo "$1: nothing running."
  fi
}
stop_one Ollama "$ROOT/.tools/ollama.pid" "$ROOT/.tools/ollama/ollama serve"
stop_one Piper "$ROOT/.tools/piper.pid" "piper.http_server"
