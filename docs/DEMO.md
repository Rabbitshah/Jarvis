# 2-minute demo: shot list

Use `bash scripts/demo.sh` (invented notes about "Asha"; your real notes never appear). Record with the macOS screen recorder (Cmd+Shift+5, "Record selected portion", microphone: built-in). Use a quiet room. Headphones avoid Jarvis hearing itself, but then the recording will not capture the spoken answer; for the video use the speakers and Enter-to-talk (`scripts/demo.sh`), not the wake word.

Before recording: delete the fact saved by test runs (`rm demo/notes/memory.md`, otherwise Jarvis answers "Already remembered"), `bash scripts/stop.sh`, close other apps, make the terminal font large, run `bash scripts/demo.sh` once to warm up the models, then `/exit` and start again.

| Time | Do | Say (voiceover or on screen) |
| --- | --- | --- |
| 0:00 | Show the README results table | "Jarvis is a voice assistant that runs fully on my laptop: no cloud, no API keys." |
| 0:15 | Run `bash scripts/demo.sh` | "Local model through Ollama, my notes in a local vector index." |
| 0:25 | Enter, ask: "When is my cloud exam?" | Answer is spoken; point at "Notes consulted: 03-study-plan.md". "The sources are added by the program, not by the model." |
| 0:50 | Ask: "What is my main project built with?" | "Answers come from the notes." |
| 1:05 | Ask a general question: "What is the capital of France?" | "General questions do not touch the notes." |
| 1:15 | Say: "Remember that I have a mock interview on Monday." Type `y` at the prompt | "Jarvis can only propose. Nothing is saved until I type y." |
| 1:35 | Ask: "What is my bank password?" | Say: "Files in a private folder are never indexed or readable by the model, and this is checked by unit tests. Here the model also refuses on its own." Do NOT say the refusal proves the protection: the protection is the code, the polite refusal is the model. |
| 1:45 | Show the injection row in the README table | "I planted notes that give orders. Out of 50 runs the model obeyed 0 and saved nothing without approval." |
| 1:55 | Show the "Known limits" heading | "It is not perfect: the limits are written down." |

Do not claim more than the README says. After recording, trim mistakes; one retake is normal.
