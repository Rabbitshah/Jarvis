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
| 4 | Tue Oct 27 | Expose list_notes and read_note | Inspector reads a note |
| 5 | Wed Oct 28 | Connect Claude Desktop | Claude Desktop lists your notes |
| 6 | Thu Oct 29 | Input checks, errors, timeouts | Bad input gives a clear error |
| 7 | Fri Oct 30 | MCP smoke test and pytest | scripts/test.sh passes |
| 8 | Sat Oct 31 | Catch-up | n/a |

## Week 3 (Nov 1-7): Note memory
Needs about 20 real notes in notes/ before Nov 3.

| Day | Date | Task | Done when |
| --- | --- | --- | --- |
| 9 | Sun Nov 1 | Embedded Qdrant, create collection | One vector goes in and comes back |
| 10 | Mon Nov 2 | Embeddings through Ollama | Vector size is logged and constant |
| 11 | Tue Nov 3 | Chunk and ingest 20 real notes | Count matches |
| 12 | Wed Nov 4 | search_notes(query, k) | 5 test queries hit the right note |
| 13 | Thu Nov 5 | Feed chunks into answers, cite filename | Answers from an old note and names it |
| 14 | Fri Nov 6 | search_notes as agent and MCP tool | Claude Desktop searches notes |
| 15 | Sat Nov 7 | Catch-up | n/a |

## Week 4 (Nov 8-14): Measure and harden
| Day | Date | Task | Done when |
| --- | --- | --- | --- |
| 16 | Sun Nov 8 | 20 question test set and script | Prints hit@3 |
| 17 | Mon Nov 9 | Tune chunk size and k | Before and after table with real numbers |
| 18 | Tue Nov 10 | remember tool with y/n confirm | Fact survives a restart |
| 19 | Wed Nov 11 | Incremental ingest (hash files) | Second ingest embeds 0 new chunks |
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
