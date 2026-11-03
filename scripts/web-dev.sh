#!/usr/bin/env bash
# Dev mode: API in the background, Vite (hot reload) on http://127.0.0.1:5173
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
bash scripts/install-node.sh
bash scripts/ollama-up.sh
uv run jarvis-api &
API=$!
trap 'kill $API 2>/dev/null || true' EXIT
cd web
if [ -f package-lock.json ]; then npm ci; else npm install; fi
npm run dev
