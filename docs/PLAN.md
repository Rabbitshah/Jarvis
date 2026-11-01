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
| 19 | Wed Nov 11 | Incremental ingest (hash files) | DONE early (Oct 25): on the Mac the first run embedded 73 chunks, the second run embedded 0 (21 notes unchanged) |
| 20 | Thu Nov 12 | Prompt injection test | DONE early (Oct 25), result in docs/INJECTION.md: 1 of 15 valid trials manipulated (read-secret: the model read the secret note because a note told it to; it did not paste it). 0 writes without approval |
| 21 | Fri Nov 13 | Memory tests on a temp store | DONE early (Oct 25): the guard passes on the Mac (all tests passed) and fails on a deliberately bad test |
| 22 | Sat Nov 14 | Checkpoint and cleanup | DONE (Oct 25): 126 tests pass, clean-clone test PASS, citations work ("Notes consulted"), injection 1/50 manipulated and 0 writes. Still open for you: fix the voice line in notes/06-jarvis-project.md (Piper only), re-run ingest.sh, push docs/INJECTION.md |

## Week 5 (Nov 15-21): Voice
| Day | Date | Task | Done when |
| --- | --- | --- | --- |
| 23 | Sun Nov 15 | Push-to-talk recording to WAV (Enter starts, Enter stops) | DONE (Oct 26) on the Mac: 133 tests, MacBook Pro Microphone, 6.3 s clip saved, peak 11644/32767, played back |
| 24 | Mon Nov 16 | Whisper transcription; pick faster-whisper or mlx-whisper by measuring | DONE and pushed (verified on the Mac, Oct 27). Chosen: mlx-whisper small (config [voice] stt). 3 clips, 0 wrong words with both small models; time per clip 0.07 s (mlx) vs 0.87 s (faster-whisper). Base models made mistakes ("Rewind me", "Valladara"). `scripts/transcribe.sh clip.wav` runs it. 140 tests |
| 25 | Tue Nov 17 | Voice into the agent | DONE and pushed (Oct 27): spoken question gets a text answer; wake phrase stripped; JSON-wrapped answers unwrapped |
| 26 | Wed Nov 18 | Piper reply | DONE (Oct 27) on the Mac: Piper runs as its own server (GPL kept apart from MIT code), `scripts/say.sh` and voice mode speak replies; first synth 0.49 s, short lines 0.06-0.21 s. 157 tests. Fixed on the way: the answer round after a tool gets no tools, so the model stops answering in JSON |
| 27 | Thu Nov 19 | Speak sentence by sentence; measure time to first audio | DONE (Oct 27) on the Mac, 167 tests. First sound 1.65-3.3 s after the question is understood, almost all of it model time (first word 1.5-3.2 s); Piper adds 0.02-0.2 s. Speed 0.82 approved. Bugs found: made-up tool call spoken, invented meeting, notes used for a general question |
| 27b | (inserted Oct 27) | Model reliability check | DONE (Oct 27). qwen2.5:7b chosen (answers 42/42, strict 40/42 vs llama3.1:8b 33/42, 27/42). Time/date now in the system message; memory.md indexed as facts only; 'remember ...' decided by code. Injection 0/50 on qwen. Details: docs/MODELS.md, docs/TOOLEVAL-*.md |
| 28 | Fri Nov 20 | Wake word (openwakeword, check the "hey jarvis" model exists first) starts the same recording; push-to-talk stays | Saying the phrase starts listening | CODE DONE (Oct 27), needs Mac check: `scripts/wake-test.sh` then `scripts/listen.sh`. Hands-free: wake word, speak, pause (loudness-based end of speech), answer spoken; Enter still works.
| 29 | Thu Oct 29 | Day 28 closed: wake word FROZEN at threshold 0.35 (no more tuning). Known limits go in the README | Day 28 pushed |

## Final stretch (decided Oct 28): finish and prove, no new features
Out of scope, on purpose: online lookups (weather, web search), calendar or mail links, calculator, more apps, more voice tuning. Reason: the repo already shows an agent loop, tools, RAG with measured eval, injection testing, MCP server and a voice pipeline. More tools add risk and no new resume signal. What is missing is proof and polish.

| Day | Date | Task | Done when |
| --- | --- | --- | --- |
| 30 | Fri Oct 30 | One results table at the top of the README (retrieval top-1/MRR, tool check, injection 0/50, voice latency) and an architecture diagram | Table and diagram render on GitHub DONE (Nov 1, code side): README top table, Mermaid diagram, Known limits. Needs your read-through |
| 31 | Sat Oct 31 | Honest limits section (Whisper mishears, wake word misses and false triggers, 8B model limits, no calendar or internet) and fix README wording ("local, no cloud") | A reader knows what does NOT work DONE (Nov 1, code side): README top table, Mermaid diagram, Known limits. Needs your read-through |
| 32 | Sun Nov 1 | Clean install in a new folder from the README (clean-clone-test.sh) | No undocumented steps DONE (Nov 1): fresh clone, full setup with model pull, ingest, text question with sources and spoken voice answer all worked with no undocumented step. Not tested from a fresh clone: wake word (listen.sh) |
| 33 | Mon Nov 2 | 2 minute demo video (voice question, notes answer with sources, remember with typed y) | Recorded, linked in README |
| 34 | Tue Nov 3 | Resume: 3 bullets with real numbers, GitHub pin, repo description, topics, tag v0.1 | Bullets written, tag pushed |
| 35 | Wed Nov 4 | Someone else runs it from the README | They get a working reply |
| 36 | Thu Nov 5 | OPTIONAL: minimal React chat page on the existing API (only for full-stack roles; skip if days 30 to 35 slipped) | Streams a reply in the browser |

Everything after Nov 5 is buffer. Deadline: Fri Dec 4.

## Cut order if 2 or more days behind
1. SRT export  2. UI source panel  3. React UI  4. Incremental ingest  5. Injection test.
Never cut: tools, MCP, Qdrant with eval numbers, README, demo video.
