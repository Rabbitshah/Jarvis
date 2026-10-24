# Architecture

## Overview
```
 Terminal (cli.py) ──┐
 Web UI (week 6) ────┼──► API (api.py, FastAPI, SSE) ──► Agent (agent.py)
 MCP client/Inspector ┘         │                           │
   (local MCP, stdio)           │                           ├──► OllamaClient (llm.py) ──► Ollama :11500
                                │                           │         └─ weights in models/ollama
                                │                           └──► Tool Registry (tools/registry.py)
                                │                                   ├─ get_time
                                │                                   ├─ list_notes / read_note ──► notes/ (sandbox)
                                │                                   ├─ search_notes ──► Qdrant (week 3)
                                │                                   └─ remember (week 4, confirm first)
                                └──► Voice (week 5): mic → Whisper → Agent → Piper → speaker
```
The CLI and API call the same `Agent`. The MCP server (`mcp_server.py`) registers the same tool functions from `tools/builtin.py`; `tests/test_mcp.py` fails if the two schemas drift apart.

## Components
| Module | Job | Notes |
| --- | --- | --- |
| `config.py` | Load `config/jarvis.toml` + env overrides | Frozen dataclass |
| `llm.py` | Stream chat from Ollama; list models; ping | Raises `LLMError` with a human message |
| `agent.py` | History, tool loop, event stream | Yields `token`, `tool_call`, `tool_result`, `done`, `error` |
| `tools/registry.py` | Register tools, build schemas, call safely | Errors become strings for the model, never crashes |
| `tools/notes.py` | Sandboxed note access | Resolves symlinks, blocks `..`, absolute paths, bad extensions |
| `tools/builtin.py` | Chooses the tool set | Keep to 4-5 tools |
| `cli.py` | Terminal chat + `--doctor` | |
| `api.py` | `/chat` (SSE), `/health` | Per-session agents, max 20 sessions, localhost only |

## Agent loop
1. Append user message, trim history (always restart at a user message so tool pairs stay intact).
2. Stream the model's reply. Collect text and any `tool_calls`.
3. If no tool calls: emit `done`.
4. Else run each tool, append `tool` messages, go to step 2 (max `max_tool_rounds`).
5. On `LLMError`, emit an `error` event.

## API contract
`POST /chat` body `{"message": str (1-4000), "session_id": str (default "default")}` returns `text/event-stream`, each line `data: {json}`:
| type | fields |
| --- | --- |
| `token` | `text` |
| `tool_call` | `name`, `args` |
| `tool_result` | `name`, `result` |
| `done` | none |
| `error` | `message` |

`GET /health` returns `{status, ollama, model, tools}`.

## Planned additions
| Week | Addition | Design note |
| --- | --- | --- |
| 2 | MCP server (stdio, `mcp[cli]` 2.x `MCPServer`) | Imports `build_registry`. Exposes only `list_notes`, `read_note`, later `search_notes` |
| 3 | Memory | Chunk markdown → Ollama embeddings → embedded Qdrant (`.tools/qdrant`, rebuildable). Payload: file, chunk id, hash |
| 4 | Eval + `remember` | hit@3 script; writes need y/n confirmation |
| 5 | Voice | push-to-talk → WAV → Whisper → agent; reply split by sentence → Piper |

## Decisions
| Decision | Why |
| --- | --- |
| Raw httpx to Ollama, no LLM framework | Fewer dependencies, easier to explain in interviews |
| Own Ollama on port 11500 | Does not clash with a system Ollama; models stay in the repo |
| Qdrant embedded mode instead of Docker | Docker is not installed; keeps everything in the repo. API verified Oct 24 (qdrant-client 1.20). It locks its folder to one process, so the store opens per call |
| SSE for streaming | Simple, works with `curl` and browsers |
| Tests use a fake LLM | Fast, deterministic, no model needed in CI |

## Threat model (short)
| Risk | Mitigation |
| --- | --- |
| Path traversal / symlink escape via `read_note` | `resolve()` + `is_relative_to` check, tests for each case |
| Prompt injection inside a note | Tool output is data; write tools need confirmation (week 4); injection test documented |
| API exposed on network | Bound to 127.0.0.1, no auth, documented |
| Huge notes flood context | 20,000 character cap |
