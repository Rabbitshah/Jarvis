#!/usr/bin/env bash
# Proves a stranger can run the project: clones what is on GitHub into a new folder, installs everything
# there, runs the tests. Pushed commits only, so push first.
# Skips the 5 GB model download and the running Ollama (set up and doctor are not part of this check).
# Usage: bash scripts/clean-clone-test.sh [folder]     Delete the folder afterwards.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIR="${1:-$HOME/jarvis-clean-test}"
REPO="$(git -C "$HERE" remote get-url origin)"
[ ! -e "$DIR" ] || { echo "$DIR already exists. Delete it first: rm -rf \"$DIR\""; exit 1; }

echo "==> Cloning $REPO into $DIR"
git clone --quiet "$REPO" "$DIR"
cd "$DIR"
echo "==> Installing (SKIP_MODELS=1)"
SKIP_MODELS=1 bash scripts/setup.sh
echo "==> Tests"
bash scripts/test.sh
echo "==> Repo must still be clean (nothing generated outside .gitignore)"
if [ -n "$(git status --short)" ]; then echo "FAIL: untracked or changed files:"; git status --short; exit 1; fi
echo "==> Root folder contents"
ls -A | tr '\n' ' '; echo
echo "PASS: a fresh clone installs and passes its tests. Delete it: rm -rf \"$DIR\""
