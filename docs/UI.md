# UI spec

Scope: **one chat page** (Story 11, cuttable). Terminal is the primary interface until then. No design references were supplied, so this is a functional spec, not a visual copy of any product.

## Stack
React + Vite + Tailwind. Talks to `POST /chat` (SSE) on `127.0.0.1:8000`. TanStack Query only if a second endpoint is needed; otherwise plain `fetch` with a stream reader.

## Layout (desktop)
```
┌──────────────────────────────────────────────────────────┐
│ Jarvis                    model: llama3.1:8b   ● online  │  header
├──────────────────────────────────────────────────────────┤
│                                                          │
│  you:    What did I write about the deadline?            │
│                                                          │
│  ▸ tool: list_notes()                  (collapsed card)  │
│  ▸ tool: read_note("idea.md")                            │
│                                                          │
│  jarvis: You planned to ship by December.                │
│          Source: idea.md                                 │  message list
│                                                          │
├──────────────────────────────────────────────────────────┤
│ [ Ask Jarvis…                                  ] [Send]  │  composer
└──────────────────────────────────────────────────────────┘
```
Mobile: same single column; composer sticks to the bottom.

## Components
| Component | Behaviour |
| --- | --- |
| `Header` | Model name from `/health`; status dot (green = Ollama reachable, red = not) |
| `MessageList` | Auto-scroll to newest; stop auto-scroll if the user scrolled up |
| `Message` | Role label, streamed text; source filenames shown as chips |
| `ToolCard` | Collapsed by default: name + args; expand shows the result (truncate at 500 chars) |
| `Composer` | Enter sends, Shift+Enter newline; disabled while streaming; Stop button aborts the request |
| `ErrorBanner` | Shows `error` events and "Ollama not reachable: run scripts/run.sh" |

## States
| State | What the user sees |
| --- | --- |
| Empty | One-line hint and two example questions |
| Streaming | Cursor at end of text, Send becomes Stop |
| Tool running | ToolCard with a spinner |
| Error | Red banner above the composer, input stays usable |
| Offline | Header dot red, composer disabled |

## Accessibility
Keyboard-only use works; focus returns to the composer after a reply; colour is never the only signal (status dot has text); respects `prefers-color-scheme` and `prefers-reduced-motion`.

## Out of scope
Auth, multi-user, file upload, settings screen, markdown editor, animations beyond a streaming cursor.
