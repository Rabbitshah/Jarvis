#!/usr/bin/env bash
# Build the chat page and serve it with the API: scripts/web.sh, then open http://127.0.0.1:8000
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
bash scripts/install-node.sh
cd web
if [ -f package-lock.json ]; then npm ci; else npm install; fi
npm run build
cd "$ROOT"
echo "Open http://127.0.0.1:8000"
exec bash scripts/run.sh --api
