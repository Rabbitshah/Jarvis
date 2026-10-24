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
