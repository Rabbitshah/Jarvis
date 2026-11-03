#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
cd "$ROOT"
uv run pytest -q "$@"
# Web tests only when node and web/node_modules exist; the Python path works without them.
if [ $# -eq 0 ]; then
  if [ -d web/node_modules ] && command -v node >/dev/null; then (cd web && npm test --silent)
  else echo "web tests skipped: run scripts/web.sh once to install node and web/node_modules"; fi
fi
