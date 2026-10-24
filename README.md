# Jarvis

A personal AI assistant that runs **fully on your own machine**: local LLM through Ollama, tools it can call, and (in later weeks) an MCP server, Qdrant note memory and voice.

> Status: **v0.1 scaffold** (plan days 1-6). Terminal chat, tool calling, sandboxed notes tools and a streaming API are written and unit-tested. Not yet verified end-to-end with a real model on the Mac: run `scripts/doctor.sh` after setup.

## Quick start (macOS, Apple Silicon)

```bash
git clone https://github.com/Rabbitshah/Jarvis.git && cd Jarvis
scripts/setup.sh        # installs uv, Python, Ollama, deps and the model INSIDE this folder
scripts/run.sh          # terminal chat
scripts/run.sh --api    # HTTP API on 127.0.0.1:8000
scripts/test.sh         # unit tests (no model needed)
scripts/doctor.sh       # checks Ollama, model and notes folder
```

Nothing is installed outside this folder (see "Where things live"). Deleting the folder removes everything.

## What it does today

| Feature | Status |
| --- | --- |
| Terminal chat with streaming + history | built, unit-tested |
| Tool calling loop (`get_time`, `list_notes`, `read_note`) | built, unit-tested |
| Notes sandbox (blocks `../`, absolute paths, symlink escape) | built, unit-tested |
| Streaming API (`POST /chat`, `GET /health`) | built, unit-tested |
| MCP server, Qdrant memory, voice, web UI | planned, see `docs/PLAN.md` |

## Where things live

| Thing | Path |
| --- | --- |
| Python venv | `.venv/` |
| Python interpreter (managed by uv) | `.tools/python/` |
| uv, Ollama binary, logs | `.tools/` |
| LLM weights | `models/ollama/` |
| Model facts (generated) | `models/model-info.txt`, `docs/MODELS.md` |
| Your notes | `notes/` |
| Settings | `config/jarvis.toml` |

All of the heavy folders are git-ignored.

## Docs

- `docs/CONTEXT.md` project context, stack, requirements, design references, constraints
- `docs/PRD.md` scoped spec for Claude Code (stories + acceptance criteria)
- `CLAUDE.md` rules Claude Code follows in this repo
- `docs/ARCHITECTURE.md`, `docs/UI.md`, `docs/DESIGN.md`, `docs/MODELS.md`, `docs/PLAN.md`
- `tracker/jarvis-sprint.html` daily log (open in a browser)

## Security

- API binds to `127.0.0.1` only. There is no auth, so do not expose it.
- Tools can only read `.md` / `.txt` files inside `notes/`.
- Text from notes is treated as data, never as instructions (full injection test planned for week 4).

## License

Not chosen yet (open item).
