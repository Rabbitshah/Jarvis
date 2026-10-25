# Plan: Sat Oct 24 to Fri Dec 4, 2026

Week 2 was pulled forward on Oct 24. Deadline stays Fri Dec 4, so Nov 29 to Dec 4 is spare buffer.
1 hour a day. Each week has 6 task days and 1 catch-up day. If you skip a day, drop the least useful task of that week.
End each day with `Next session: ___` and a `git push`.

## Week 1 (Oct 24-24): Core agent
| Day | Date | Task | Done when |
| --- | --- | --- | --- |
| 1 | Sat Oct 24 | Setup, chat, tools, notes sandbox, API (old days 1 to 6) | DONE: 33 tests pass, API streams a correct answer |

## Week 2 (Oct 25-31): MCP
| Day | Date | Task | Done when |
| --- | --- | --- | --- |
| 2 | Sun Oct 25 | Read current MCP docs; hello server with 1 tool | DONE early (Oct 24): Inspector on the Mac lists and runs hello; SDK client test passes |
| 3 | Mon Oct 26 | Share tool functions between agent and MCP | DONE early (Oct 24): MCP registers the agent's own functions; a test fails if schemas drift |
| 4 | Tue Oct 27 | Expose list_notes and read_note | DONE early (Oct 24): Inspector on the Mac lists tools, reads a note, blocks ../ |
| 5 | Wed Oct 28 | Input checks, errors, timeouts | DONE early (Oct 24): wrong or missing arguments give a clear error; slow tools time out at 10 s; 50 tests pass |
| 6 | Thu Oct 29 | MCP smoke test, pytest, short "run MCP locally" section in the README | DONE early (Oct 24): scripts/mcp-smoke.sh passes (6 checks); 52 tests pass; README section added |
| 7 | Fri Oct 30 | Spare (Claude Desktop step dropped: Jarvis stays fully local) | n/a |
| 8 | Sat Oct 31 | Catch-up | n/a |

## Week 3 (Nov 1-7): Note memory
Needs about 20 real notes in notes/ before Nov 3.

| Day | Date | Task | Done when |
| --- | --- | --- | --- |
| 9 | Sun Nov 1 | Embedded Qdrant, create collection | DONE early (Oct 24): checked the docs and probed the API; VectorStore tests put a vector in and get it back, and survive a reopen |
| 10 | Mon Nov 2 | Embeddings through Ollama | DONE early (Oct 24): doctor on the Mac prints vector size 768 (constant) |
| 11 | Tue Nov 3 | Chunk and ingest 20 real notes | DONE early (Oct 24): scripts/ingest.sh on the Mac: 20 notes, 38 chunks in the index, MATCH |
| 12 | Wed Nov 4 | search_notes(query, k) | DONE early (Oct 24): search-eval on the Mac: top-3 5/5, top-1 4/5 (the miss ranked 2nd) |
| 13 | Thu Nov 5 | Feed chunks into answers, cite filename | DONE early (Oct 24): on the Mac, 2 note questions answered correctly and named the file; the time question used no notes |
| 14 | Fri Nov 6 | search_notes as agent and MCP tool | DONE early (Oct 24): mcp-smoke passes with the search check (4 tools); the Inspector returns search_notes answers |
| 15 | Sat Nov 7 | Catch-up | Not needed: week 3 finished early (Oct 24) |

## Week 4 (Nov 8-14): Measure and harden
| Day | Date | Task | Done when |
| --- | --- | --- | --- |
| 16 | Sun Nov 8 | 20 question test set and script | DONE early (Oct 24): 20 cases; baseline on the Mac: top-1 16/20, hit@3 19/20, MRR 0.875 |
| 17 | Mon Nov 9 | Tune chunk size and k | Table DONE (Oct 24, docs/TUNING.md): 400-char chunks beat 800 and 1200 (MRR 0.95-0.98 vs 0.87-0.90 vs 0.76-0.87). Config set to 400. Header and task prefix: no clear effect, left unchanged. Verified on the Mac after re-ingest (72 chunks): top-1 16/20 -> 18/20, hit@3 19/20 -> 20/20, MRR 0.875 -> 0.950. min_score set to 0.51 |
| 18 | Tue Nov 10 | remember tool with y/n confirm | DONE early (Oct 25): on the Mac, remembered a fact with y, restarted, it was found; an n answer saved nothing |
| 19 | Wed Nov 11 | Incremental ingest (hash files) | Code done (Oct 25), 110 tests pass. NOT yet run on the Mac: bash scripts/ingest.sh twice; the second run must say embedded now: 0 |
| 20 | Thu Nov 12 | Prompt injection test | Result written down, no write without confirm |
| 21 | Fri Nov 13 | Memory tests on a temp store | Tests never touch real data |
| 22 | Sat Nov 14 | Catch-up and checkpoint | n/a |

## Week 5 (Nov 15-21): Voice
| Day | Date | Task | Done when |
| --- | --- | --- | --- |
| 23 | Sun Nov 15 | Push-to-talk recording to WAV | WAV plays back |
| 24 | Mon Nov 16 | Whisper transcription; pick faster-whisper or mlx-whisper by measuring | 3 clips transcribed correctly |
| 25 | Tue Nov 17 | Voice into the agent | Spoken question gets a text answer |
| 26 | Wed Nov 18 | Piper reply | Reply is spoken |
| 27 | Thu Nov 19 | Speak sentence by sentence; measure time to first audio | Number is in the README |
| 28 | Fri Nov 20 | SRT export (cuttable) | SRT plays in VLC |
| 29 | Sat Nov 21 | Catch-up | n/a |

## Week 6 (Nov 22-28): Ship
| Day | Date | Task | Done when |
| --- | --- | --- | --- |
| 30 | Sun Nov 22 | Minimal React chat page (cuttable) | Streams a reply in the browser |
| 31 | Mon Nov 23 | Show tool calls and sources (cuttable) | Source filename is visible |
| 32 | Tue Nov 24 | Diagram and README draft | Diagram shows on GitHub |
| 33 | Wed Nov 25 | Clean install from the README in a new folder | No undocumented steps |
| 34 | Thu Nov 26 | 2 minute demo video | Recorded |
| 35 | Fri Nov 27 | Someone else runs it from the README; tag v0.1 | They get a working reply |
| 36 | Sat Nov 28 | Spare day | n/a |

Nov 29 to Dec 4 is buffer. Deadline: Fri Dec 4.

## Cut order if 2 or more days behind
1. SRT export  2. UI source panel  3. React UI  4. Incremental ingest  5. Injection test.
Never cut: tools, MCP, Qdrant with eval numbers, README.
