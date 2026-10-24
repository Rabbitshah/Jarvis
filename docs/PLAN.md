# Plan: Sat Oct 24 to Fri Dec 4, 2026

1 hour per day, 6 task days + 1 catch-up day per week. If you skip a day, drop the lowest-value task of that week. Do not stack a backlog.
Each day ends with one line: `Next session: ___`, and a `git push`.

## Week 1 (Oct 24-30): Core agent
| Day | Date | Task | Done when |
| --- | --- | --- | --- |
| 1 | Sat Oct 24 | Setup: run `scripts/setup.sh`, confirm repo pushes to GitHub | Model answers in terminal; `scripts/test.sh` passes |
| 2 | Sun Oct 25 | Real-model chat check (history, `/reset`) | It remembers your previous message |
| 3 | Mon Oct 26 | Config + logging + more tests | Changing model needs no code edit |
| 4 | Tue Oct 27 | Tool calling with `get_time` on the real model | Model calls `get_time` by itself |
| 5 | Wed Oct 28 | `list_notes`, `read_note` on real notes | Test proves `../` blocked; model reads a note |
| 6 | Thu Oct 29 | API `/chat` streaming | `curl -N` returns a streamed reply |
| 7 | Fri Oct 30 | Catch-up | n/a |

## Week 2 (Oct 31-Nov 6): MCP
| Day | Date | Task | Done when |
| --- | --- | --- | --- |
| 8 | Sat Oct 31 | Read current MCP docs; hello server, 1 tool | Inspector lists and calls it |
| 9 | Sun Nov 1 | Share tool functions between agent and MCP | Both call the same function |
| 10 | Mon Nov 2 | Expose `list_notes`, `read_note` | Inspector reads a note |
| 11 | Tue Nov 3 | Connect Claude Desktop | Claude Desktop lists your notes |
| 12 | Wed Nov 4 | Validation, errors, timeouts | Bad input returns clear error |
| 13 | Thu Nov 5 | MCP smoke test + pytest | `scripts/test.sh` passes |
| 14 | Fri Nov 6 | Catch-up | n/a |

## Week 3 (Nov 7-13): Note memory
| Day | Date | Task | Done when |
| --- | --- | --- | --- |
| 15 | Sat Nov 7 | Embedded Qdrant, create collection | Insert one vector and read it back |
| 16 | Sun Nov 8 | Embeddings via Ollama | Vector size logged and constant |
| 17 | Mon Nov 9 | Chunk + ingest 20 real notes | Count matches |
| 18 | Tue Nov 10 | `search_notes(query, k)` | 5 hand-picked queries hit the right note |
| 19 | Wed Nov 11 | Feed chunks into answers, cite filename | Answers from an old note and names it |
| 20 | Thu Nov 12 | `search_notes` as agent + MCP tool | Claude Desktop searches notes |
| 21 | Fri Nov 13 | Catch-up | n/a |

## Week 4 (Nov 14-20): Measure and harden
| Day | Date | Task | Done when |
| --- | --- | --- | --- |
| 22 | Sat Nov 14 | 20-question eval set + script | Prints hit@3 |
| 23 | Sun Nov 15 | Tune chunk size and k | Before/after table with real numbers |
| 24 | Mon Nov 16 | `remember` with y/n confirm | Fact survives a restart |
| 25 | Tue Nov 17 | Incremental ingest (hash files) | Second ingest embeds 0 new chunks |
| 26 | Wed Nov 18 | Prompt-injection test | Documented result, no unconfirmed write |
| 27 | Thu Nov 19 | Memory tests on temp store | Tests never touch real data |
| 28 | Fri Nov 20 | Catch-up + checkpoint | n/a |

## Week 5 (Nov 21-27): Voice
| Day | Date | Task | Done when |
| --- | --- | --- | --- |
| 29 | Sat Nov 21 | Push-to-talk recording to WAV | WAV plays back |
| 30 | Sun Nov 22 | Whisper transcription; choose faster-whisper vs mlx-whisper by measuring | 3 clips transcribed correctly |
| 31 | Mon Nov 23 | Voice into agent | Spoken question gets a text answer |
| 32 | Tue Nov 24 | Piper reply | Reply is spoken |
| 33 | Wed Nov 25 | Sentence-by-sentence speech; measure time to first audio | Number in README |
| 34 | Thu Nov 26 | SRT export (cuttable) | SRT plays in VLC |
| 35 | Fri Nov 27 | Catch-up | n/a |

## Week 6 (Nov 28-Dec 4): Ship
| Day | Date | Task | Done when |
| --- | --- | --- | --- |
| 36 | Sat Nov 28 | Minimal React chat page (cuttable) | Streams a reply in browser |
| 37 | Sun Nov 29 | Show tool calls + sources (cuttable) | Source filename visible |
| 38 | Mon Nov 30 | Diagram + README draft | Diagram renders on GitHub |
| 39 | Tue Dec 1 | Clean install from README in a fresh folder | Zero undocumented steps |
| 40 | Wed Dec 2 | 2-minute demo video | Recorded |
| 41 | Thu Dec 3 | Someone else runs it from the README; tag v0.1 | They reach a working reply |
| 42 | Fri Dec 4 | Buffer / deadline | n/a |

## Cut order if 2+ days behind
1. SRT export  2. UI source panel  3. React UI  4. Incremental ingest  5. Injection test.
Never cut: tools, MCP, Qdrant + eval numbers, README.
