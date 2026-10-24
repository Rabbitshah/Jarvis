# Sourced by the other scripts. Keeps every install INSIDE this repo folder.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export JARVIS_ROOT="$ROOT"
export UV_CACHE_DIR="$ROOT/.tools/uv-cache"
export UV_PYTHON_INSTALL_DIR="$ROOT/.tools/python"
export UV_PROJECT_ENVIRONMENT="$ROOT/.venv"
export UV_PYTHON_PREFERENCE=only-managed
export OLLAMA_MODELS="$ROOT/models/ollama"
export OLLAMA_HOST="127.0.0.1:11500"
export HF_HOME="$ROOT/models/hf"
export PATH="$ROOT/.tools/bin:$ROOT/.tools/ollama:$PATH"
export NPM_CONFIG_CACHE="$ROOT/.tools/npm-cache"
export PATH="$ROOT/.tools/node/bin:$PATH"
