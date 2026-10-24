# Daily log

Claude adds a row here after each session. `scripts/sync_tracker.py` copies it into the tracker page.
Hours marked ? are not confirmed yet. Correct them if you like.

| Date | Hours | Did | Broke | Next session |
| --- | --- | --- | --- | --- |
| 2026-10-24 | ? | Set up the repo and local model. Chat, tools, notes sandbox and API work. 33 tests pass on the Mac | The 8B model wrote a tool call as text and guessed file names. Fixed in code | Day 2: read MCP docs, build a hello server |
| 2026-10-24 | ? | Pushed to GitHub. Day 2 done early: read current MCP docs, hello MCP server, SDK client test. 35 tests pass. Inspector on the Mac runs hello | MCP SDK is now v2 (MCPServer, not FastMCP). My memory of the old API was wrong, so I checked the docs first | Day 3: share tool functions between agent and MCP |
| 2026-10-24 | ? | Day 3 done early: MCP server now exposes the agent's real tools (get_time, list_notes, read_note) from one shared place. Drift test added. 36 tests pass | The SDK hides non-MCP error text, so sandbox errors came back blank. Fixed with a small wrapper | Day 4: expose notes tools and check them in the Inspector |
| 2026-10-24 | ? | Day 4 done early: Inspector on the Mac runs get_time, list_notes, read_note and blocks ../ . 37 tests pass | Nothing new | Day 5: input checks, errors, timeouts |
| 2026-10-24 | ? | Dropped the Claude Desktop step (Jarvis stays fully local) and removed its files. Moved CONTEXT.md and PRD.md into docs/. Kept caches out of the repo root | Nothing | Day 5: input checks, errors, timeouts |
| 2026-10-24 | ? | Day 5 done early: tools check missing, extra and wrong-type arguments. Slow tools time out after 10 s (agent and MCP share the same limit, set in config). read_note reads at most 20,000 characters from disk. Bad session_id is rejected. 50 tests pass | An old test expected the old error text; updated | Day 6: MCP smoke test, README "run MCP locally" section |
| 2026-10-24 | ? | Day 6 done early: scripts/mcp-smoke.sh starts the MCP server and calls every tool (6 checks, all pass). Added MCP tests for bad input and timeout. README has a "Run the MCP server locally" section. 52 tests pass | The SDK shows its own validation text for wrong arguments (long but still an error); left as is | Day 7 is spare. Suggest: pick the week 3 memory approach, or add more real notes (need about 20 by Nov 3) |
| 2026-10-24 | ? | Week 3 started early. Day 9: verified embedded Qdrant API in the docs and probed it. Added memory/store.py (VectorStore). Day 10 code: OllamaClient.embed (/api/embed), setup.sh now pulls nomic-embed-text, doctor prints the vector size. 20 real notes now in notes/. 61 tests pass | Embedded Qdrant locks its folder to one process, so the store opens per call, not at startup. Matters for Day 14 (agent + MCP at the same time). Not yet tested with the real embedding model | Pull the embedding model on the Mac, run doctor (Day 10 check), then Day 11: chunk and ingest the 20 notes |
