# Models

All weights live in `models/ollama/` inside this repo (set by `OLLAMA_MODELS` in `scripts/env.sh`). A private Ollama server runs on `127.0.0.1:11500`.

## Current choice
| Role | Model tag | Why | Status |
| --- | --- | --- | --- |
| Chat + tools | `qwen2.5:7b` | Chosen Oct 27 by `scripts/tool-eval.sh`: answers correct 39/42 vs 33/42 for llama3.1:8b, strict 36/42 vs 27/42, and 3-6x faster per answer (0.1-1.0 s vs 1.0-1.8 s). Details below | Verified on this Mac |
| Embeddings (week 3) | `nomic-embed-text` | Small, local embedding model | Verified (768 dimensions) |
| Speech to text | mlx-whisper `whisper-small-mlx` | 0 wrong words on 3 clips, 0.07 s per clip (docs/STT.md) | Verified |
| Text to speech | Piper `en_US-lessac-medium` | Local, 0.06-0.5 s per sentence, speed 0.82 | Verified (voice licence not checked) |

Things I believe but you must verify (I could not check them from here):
- The tag `llama3.1:8b` exists in the Ollama library and has the "tools" capability.
- Its download size is roughly 5 GB at default quantisation.
- It runs with acceptable speed on 24 GB unified memory.

## Real model facts
After `scripts/setup.sh`, the file `models/model-info.txt` contains the real output of `ollama show <model>` (parameters, quantisation, context length, capabilities). Treat that file as the source of truth, not this page.

## Change the model
1. Edit `model = "..."` in `config/jarvis.toml` (or set `JARVIS_MODEL`).
2. `source scripts/env.sh && ollama pull <tag>`
3. `scripts/doctor.sh`
4. Re-run the tool-calling check below.

## Tool-calling check (do this once per model)
Ask in the terminal chat: "What time is it?" Expect a `[tool] get_time` line, then a correct time. Then "List my notes and read the first one." Expect two tool lines. If the model answers without calling tools, or loops, try another tool-capable model and record the result in this table.

| Date | Model | get_time | list+read | Speed note | Verdict |
| --- | --- | --- | --- | --- | --- |
| 2026-10-24 | llama3.1:8b | calls tool, but misread the ISO time string (said 5:32 PM for 13:32) | not tested yet | not measured | Tool calling works. Run 2: ignored the tool result when it contained the word 'timezone'. Output simplified, prompt tells it to trust tool results |

## Model comparison (Oct 27, `scripts/tool-eval.sh`, 14 questions x 3 trials, same prompt as voice mode)
| | llama3.1:8b | qwen2.5:7b |
| --- | --- | --- |
| Answer correct | 33 / 42 | **39 / 42** |
| Strict (answer correct and right tools used) | 27 / 42 | **36 / 42** |
| Time and date (told in the prompt) | 2/3 each | 3/3 each |
| Math 17 x 23 | 1/3 (387, 379) | 3/3 |
| Calendar ("meetings tonight") | 1/3 (invented a read_note call) | 3/3 |
| Fun fact | 0/3 (pickleball note) | 0/3 (pickleball note) |
| Remember | 3/3 | answer 3/3, tool called 0/3 (before the prompt fix) |
| Seconds per question | 0.8 - 1.8 | 0.1 - 1.0 |

Limits: 3 trials per question is small; I wrote the pass rules and changed the scoring once after seeing the first results (both numbers are shown). On the first version of the rules (before the clock was put in the prompt) qwen answered time and date without calling a tool and gave wrong values: it will invent facts when no tool is forced. Injection re-run on qwen2.5:7b (50 trials): 0 manipulated, 0 writes. Caution: qwen rarely calls tools on its own (see below), so some of that is the model doing little, not the defences doing much.

**After the memory.md fix (Oct 27, evening): 42/42 answers correct, 40/42 strict, fun fact 3/3 (its top note score fell from 0.591 to 0.461).**

**Automatic note search ON vs OFF (qwen2.5:7b, Oct 27):** ON: 39/42 (fails only the fun fact, 0/3, because `memory.md` is attached to "tell me a fun fact"). OFF: fun fact 3/3 but all 5 notes questions 0/3 (27/42): qwen never calls `search_notes` by itself, even though the prompt says to. So the automatic search stays ON; the fun-fact leak needs a retrieval fix, not a switch.

## Hardware
Primary: MacBook Pro, Apple M5 Pro, 24 GB RAM, 1 TB SSD. Second machine (ROG Strix G16, RTX 4060 8 GB, 16 GB RAM) is not used in this plan.
