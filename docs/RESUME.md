# Resume material (every number is from this repo's own scripts; see README and docs/LOG.md)

## Project line
**Jarvis: local voice assistant** | Python, Ollama (qwen2.5:7b), Qdrant, mlx-whisper, Piper, openWakeWord, FastAPI, MCP | github.com/Rabbitshah/Jarvis

## Bullets (pick 3)
- Built a fully local voice assistant in Python (wake word, Whisper speech-to-text, tool-calling LLM agent, Piper speech) with no cloud services or API keys; first spoken sound within about 3 s on a MacBook.
- Added retrieval over personal notes (embedded Qdrant, nomic-embed-text). Chose a 400-character chunk size by experiment, lifting a 20-question test from 16/20 to 18/20 right-note-first (MRR 0.875 to 0.950); every answer lists the notes used, added by code and not by the model.
- Hardened a small model against prompt injection: wrote a harness with 5 attack types x 10 runs (0/50 obeyed, 0 unapproved saves), an approval gate for memory facts the model proposes (only the user's own "remember" command saves directly), and private notes that are never indexed. 191 unit tests; same tools also exposed through an MCP server.
- Picked the chat model by measurement (14 questions x 3 runs: qwen2.5:7b 42/42 correct vs llama3.1:8b 33/42) and fixed failures in code (clock in the prompt, tool-free answer round, rule-based "remember") instead of prompt tweaks.

## What to say if asked (limits)
- The 20 search questions were written from the notes themselves, so real questions will score lower.
- The injection result is on one small model with 5 hand-written attacks; it shows the safeguards work, not that attacks are impossible.
- The wake word works but its miss and false-trigger rates were not measured.
- Tested on one Apple Silicon Mac.

## GitHub repo settings
Description: Fully local voice assistant: wake word, Whisper, tool-calling LLM (Ollama), search over your notes (Qdrant), Piper voice, MCP server. No cloud, no API keys. Measured, with a prompt-injection test.
Topics: local-llm, ollama, rag, qdrant, voice-assistant, whisper, piper-tts, openwakeword, mcp, prompt-injection, python, fastapi, tool-calling, privacy
