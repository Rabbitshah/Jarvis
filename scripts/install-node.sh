#!/usr/bin/env bash
# Install the current Node.js LTS into .tools/node (only needed for the MCP Inspector).
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/env.sh"
[ -x "$ROOT/.tools/node/bin/npx" ] && exit 0
mkdir -p "$ROOT/.tools/node"
V="$(curl -fsS https://nodejs.org/dist/index.json | "$ROOT/.venv/bin/python" -c 'import json,sys; print(next(x["version"] for x in json.load(sys.stdin) if x["lts"]))')"
echo "==> Node $V into .tools/node"
curl -fL "https://nodejs.org/dist/$V/node-$V-darwin-arm64.tar.gz" | tar -xz -C "$ROOT/.tools/node" --strip-components=1
"$ROOT/.tools/node/bin/node" --version
