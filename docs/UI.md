# UI spec

One chat page in `web/`, built on the existing API. The terminal stays the primary interface. No design references were supplied, so this is a functional spec.

## Stack
React 19 + Vite + TypeScript + plain CSS. No router, no state library, no UI kit, no CDN, no external fonts. Tests: Vitest (+ testing-library).

## Serving
- **Production:** `scripts/web.sh` builds `web/dist`; `create_app` mounts it at `/` after the API routes (only if `web/dist` exists), so `/health`, `/chat`, `/confirm` still win. Same origin, so no CORS middleware.
- **Dev:** `scripts/web-dev.sh` runs Vite on `127.0.0.1:5173` with a proxy for `/chat`, `/confirm`, `/health` to `127.0.0.1:8000`.

## Layout
```
Jarvis  qwen2.5:7b                ● online   [New chat]   header
────────────────────────────────────────────────────────
                         you: What did I write ...       message list
 JARVIS  ▸ search_notes(query="...")   (collapsed card)  (column max 760 px)
         Answer text with a cursor while streaming
         Notes consulted: a.md  b.md
         ┌ Save to memory? ────────────┐
         │ fact text      [Save] [Don't save]
────────────────────────────────────────────────────────
[ Ask Jarvis…                                  ] [Send]  composer (sticks to bottom)
```

## Files (`web/src`)
`sse.ts` (byte stream to events) · `api.ts` (`health`, `chat`, `confirm`) · `state.ts` (pure reducer) · `session.ts` · `App.tsx` · `components/` Header, MessageList, Message, ToolCard, SourceChips, ConfirmCard, Composer, ErrorBanner, EmptyState.

## Behaviour
| Area | Rule |
| --- | --- |
| Session | Random 32-char id (no dashes) kept in `sessionStorage` inside try/catch; "New chat" makes a new one and clears the screen. Works without storage. |
| Health | `GET /health` on load and every 15 s. Offline: red "Ollama not reachable" text, composer disabled, banner "Ollama not reachable. Start it with scripts/run.sh --api". |
| Streaming | `POST /chat` as SSE. Cursor while streaming, auto-scroll unless the user scrolled up ("Jump to latest"), `aria-live="polite"` on the reply. Bad SSE lines are ignored. |
| Tool card | Collapsed; name + args; spinner while running; result truncated at 500 chars with "show more". |
| Sources | "Notes consulted: ..." chips under the reply (added by the server). |
| **Memory confirm** | A `confirm` event only shows a card with the fact. If `from_context` is true, a warning is shown above the buttons. Only a click on Save / Don't save calls `POST /confirm`. No timers, no auto-click, nothing from model text. |
| Composer | Enter sends, Shift+Enter newline, max 4000 with a counter near the limit, disabled while streaming, Send becomes Stop (abort, "(stopped)"), focus returns after a reply. |
| Errors | Network failure, non-200 and `error` events show a red banner above the composer; input stays usable. |
| Empty | One line and two example questions; clicking fills the composer, does not send. |

## Design system
Tokens live at the top of `web/src/styles.css`; components use only tokens.
| Group | Tokens |
| --- | --- |
| Color | neutral (`--bg`, `--surface`, `--text`, `--muted`, `--line`), one accent (`--accent`, `--accent-hover`, `--accent-soft`), semantic (`--ok`, `--danger`, `--warn`); light and dark sets |
| Space | `--s1` 4 px to `--s6` 40 px |
| Radius | `--r-sm` 8, `--r-md` 12, `--r-lg` 18, `--r-full` |
| Type | system font stack, `--fs-sm` to `--fs-xl`, `--mono` for tool names and results |
| Motion | `--t` 160 ms; entrance 200 ms; all disabled under `prefers-reduced-motion` |
| Elevation | `--shadow-1` (cards), `--shadow-2` (confirm card, jump button) |
Icons are inline SVG (`components/Icon.tsx`, no emoji). Touch targets are at least 44 px. Hover changes color or border only, never layout.

## Safety
Model and tool text is rendered as React text nodes (no `dangerouslySetInnerHTML`, no markdown to HTML). The page only requests its own origin.

## Accessibility
Keyboard-only use works, visible focus, labelled controls, status shown as text not only colour, `prefers-color-scheme` and `prefers-reduced-motion` respected, works from 360 px width.

## Out of scope
Auth, multi-user, file upload, settings screen, voice in the browser, markdown rendering.
