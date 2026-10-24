# Models

All weights live in `models/ollama/` inside this repo (set by `OLLAMA_MODELS` in `scripts/env.sh`). A private Ollama server runs on `127.0.0.1:11500`.

## Current choice
| Role | Model tag | Why | Status |
| --- | --- | --- | --- |
| Chat + tools | `llama3.1:8b` | Widely used 8B model with tool-calling support in Ollama | **Not yet verified on this Mac** |
| Embeddings (week 3) | `nomic-embed-text` | Small, local embedding model | Not pulled yet |
| Speech to text (week 5) | Whisper via faster-whisper or mlx-whisper | Decide by measuring on the Mac | Not chosen |
| Text to speech (week 5) | Piper voice | Your stated default | Not chosen |

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

## Hardware
Primary: MacBook Pro, Apple M5 Pro, 24 GB RAM, 1 TB SSD. Second machine (ROG Strix G16, RTX 4060 8 GB, 16 GB RAM) is not used in this plan.
