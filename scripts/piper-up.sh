#!/usr/bin/env bash
# Install (first run only) and start Piper, the local voice, on 127.0.0.1:5500.
# Piper lives in its own folder (.tools/piper-venv) and its own process: it is GPL-3.0, Jarvis is MIT.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
VOICE="${JARVIS_TTS_VOICE:-en_US-lessac-medium}"
PORT=5500
PY="$ROOT/.tools/piper-venv/bin/python"
if curl -fs "http://127.0.0.1:$PORT/voices" >/dev/null 2>&1; then echo "Piper already running."; exit 0; fi
if [ ! -x "$PY" ]; then
  echo "==> Piper (into .tools/piper-venv)"
  uv venv "$ROOT/.tools/piper-venv" --python 3.12
  uv pip install --python "$PY" "piper-tts[http]"
fi
mkdir -p "$ROOT/models/piper"
if [ ! -f "$ROOT/models/piper/$VOICE.onnx" ]; then
  echo "==> Voice $VOICE (into models/piper)"
  "$PY" -m piper.download_voices "$VOICE" --data-dir "$ROOT/models/piper"
fi
nohup "$PY" -m piper.http_server -m "$VOICE" --data-dir "$ROOT/models/piper" --host 127.0.0.1 --port "$PORT" \
  > "$ROOT/.tools/piper.log" 2>&1 &
echo $! > "$ROOT/.tools/piper.pid"
for _ in $(seq 1 60); do
  curl -fs "http://127.0.0.1:$PORT/voices" >/dev/null 2>&1 && { echo "Piper ready on 127.0.0.1:$PORT"; exit 0; }
  sleep 0.5
done
echo "Piper did not start. See .tools/piper.log" >&2
exit 1
