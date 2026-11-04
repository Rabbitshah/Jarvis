# PRD / System Specification: Jarvis

## 1. Outcome & Users
- **Target Outcome:** the owner can ask a local assistant questions by text or voice and get answers grounded in their own notes, and the same tools are available through a local MCP server, with nothing leaving the machine.
- **Target Users:** the owner (CS student, comfortable with full-stack web, beginner in ML). Secondary: a recruiter or engineer who clones the repo and runs it from the README.

## 2. Technical Constraints & Conventions
- **Stack:** Python 3.12, Ollama, FastAPI, httpx, pytest, uv. Later: Qdrant (embedded), MCP SDK, Whisper, Piper, React + Vite + Tailwind.
- **Code Conventions:** type hints everywhere; one module per concern; tools are plain functions registered in `tools/builtin.py`; no global state outside `create_app`; tests use `FakeLLM`, never a real model; config only via `config/jarvis.toml`.
- **Libraries allowed:** those listed in `docs/CONTEXT.md` section 2 only. Adding any other library needs the owner's approval. Never invent a package or version.
- **Install location:** inside the repo root only (see `scripts/env.sh`).

## 3. Data Model & Architecture
- **State to persist:** notes (plain files in `notes/`); later vectors + metadata (file, chunk id, content hash) in embedded Qdrant under `data/qdrant`; `remember` facts as markdown in `notes/memory/`. Chat history is in memory only for now.
- **Crucial APIs:** Ollama REST (`/api/chat`, `/api/tags`, later `/api/embed`), MCP stdio. No external services.
- Diagram and flows: `docs/ARCHITECTURE.md`.

## 4. Release 1 (The Scope)
*Build ONLY the stories below, in order. One story per session (about 1 hour).*

### Story 1: Terminal chat  [implemented, needs real-model check]
- **User Intent:** As the owner, I want to chat in a terminal, so that I can use the model without a UI.
- **Acceptance Criteria:**
  - WHEN I type a message THE SYSTEM SHALL stream the reply token by token.
  - WHEN I send a follow-up THE SYSTEM SHALL use earlier messages as context.
  - WHEN I type `/reset` THE SYSTEM SHALL clear history.
  - WHEN Ollama is not running THE SYSTEM SHALL show a clear error and not crash.

### Story 2: Tool calling + `get_time`  [implemented]
- **User Intent:** As the owner, I want the model to call tools, so that it can act, not only talk.
- **Acceptance Criteria:**
  - WHEN the model requests a tool THE SYSTEM SHALL run it and return the result to the model.
  - WHEN the tool name is unknown or arguments are bad THE SYSTEM SHALL return an error string to the model and continue.
  - WHEN tool rounds exceed `max_tool_rounds` THE SYSTEM SHALL stop with an error event.

### Story 3: Notes tools (sandboxed)  [implemented]
- **User Intent:** As the owner, I want Jarvis to list and read my notes, so that it can answer from them.
- **Acceptance Criteria:**
  - WHEN a path contains `..`, is absolute, or resolves outside `notes/` THE SYSTEM SHALL refuse it.
  - WHEN a file is not `.md` or `.txt` THE SYSTEM SHALL refuse it.
  - WHEN a note exceeds 20,000 characters THE SYSTEM SHALL truncate and say so.

### Story 4: Streaming API  [implemented]
- **User Intent:** As a developer, I want an HTTP endpoint, so that a UI or script can use Jarvis.
- **Acceptance Criteria:**
  - WHEN I `POST /chat` with a message THE SYSTEM SHALL stream server-sent events (`token`, `tool_call`, `tool_result`, `done` or `error`).
  - WHEN `session_id` differs THE SYSTEM SHALL keep separate history.
  - WHEN the message is empty or over 4000 characters THE SYSTEM SHALL return 422.
  - THE SYSTEM SHALL bind to `127.0.0.1` only.

### Story 5: MCP server (local only)
- **User Intent:** As the owner, I want my tools behind a standard local interface (MCP), so that any local MCP client can use them.
- **Acceptance Criteria:**
  - WHEN the MCP Inspector connects THE SYSTEM SHALL list `get_time`, `list_notes` and `read_note` using the same functions as the agent.
  - WHEN input is invalid or a path escapes `notes/` THE SYSTEM SHALL return a clear error without crashing.
  - THE SYSTEM SHALL NOT be connected to any cloud app (no Claude Desktop). Notes never leave the machine.
- **Note:** read the current official MCP docs first. Do not rely on memory for SDK or config syntax.

### Story 6: Note memory (Qdrant)
- **User Intent:** As the owner, I want Jarvis to search my notes by meaning, so that it finds old information.
- **Acceptance Criteria:**
  - WHEN notes are ingested THE SYSTEM SHALL chunk them, embed them locally and store file name + chunk id.
  - WHEN I ask a question THE SYSTEM SHALL retrieve top-k chunks and answer citing the filename.
  - WHEN ingest runs twice THE SYSTEM SHALL embed zero new chunks for unchanged files.
  - WHEN tests run THE SYSTEM SHALL use a temporary store, never real data.

### Story 7: Retrieval eval
- **User Intent:** As an engineer, I want a measured score, so that I can prove retrieval works.
- **Acceptance Criteria:**
  - WHEN `eval` runs THE SYSTEM SHALL print hit@3 on a 20-question set built from real notes.
  - THE SYSTEM SHALL record a before/after table when chunk size or k changes.

### Story 8: `remember` with confirmation
- **Acceptance Criteria:**
  - WHEN the model calls `remember` THE SYSTEM SHALL ask the user y/n before writing. (Changed Nov 4: a message the user types that starts with "remember" is saved at once by rule, no y/n.)
  - WHEN a note contains instructions like "ignore previous instructions" THE SYSTEM SHALL NOT write without confirmation.

### Story 9: Voice in and out
- **Acceptance Criteria:**
  - WHEN I hold the push-to-talk key THE SYSTEM SHALL record, transcribe locally, and answer.
  - WHEN a reply is ready THE SYSTEM SHALL speak it sentence by sentence with Piper.
  - THE SYSTEM SHALL log time-to-first-audio.

### Story 10: SRT export  (cuttable)
- WHEN given an audio file THE SYSTEM SHALL write an `.srt` that plays correctly in VLC.

### Story 11: Web chat page  (cuttable)
- WHEN I open the page THE SYSTEM SHALL stream replies from `/chat` and show tool calls and source filenames. Follow `docs/UI.md`.

### Story 12: Ship
- README with diagram and measured numbers, clean-install check, 2-minute demo video, tag `v0.1`.

## 5. Explicit Out of Scope
- ElevenLabs or any paid / cloud service, cloud LLMs
- Calendar, email, screen watching, multi-agent systems, workflow builders
- Wake word, user accounts / auth, mobile app, Docker packaging of the app
- Running on the Windows laptop
- Summary mode (add only if everything else is done early)
- Any library or tool not listed in `docs/CONTEXT.md`

## 6. Open Questions [NEEDS CLARIFICATION]
- Does `llama3.1:8b` call tools reliably on this Mac? Decide after the first real run (see `docs/MODELS.md`).
- Whisper on Apple Silicon: `faster-whisper` (CPU) vs `mlx-whisper`. Decide on plan day 30 by measuring.
- Which 20 real notes will be used for the eval? Owner must supply them by plan day 17.
- Licence for the repo (MIT or Apache-2.0)?
