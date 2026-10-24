# Design tokens (draft)

No brand or reference was supplied. These are neutral, accessible defaults the owner can replace. Do not copy another product's look.

## Principles
1. Plain and readable first. The content is text.
2. Show what the system did (tool calls, sources) without clutter.
3. Works in light and dark.

## Colour (CSS variables)
| Token | Light | Dark | Use |
| --- | --- | --- | --- |
| `--bg` | #ffffff | #121212 | page |
| `--surface` | #f4f4f2 | #1c1c1c | cards, tool cards |
| `--text` | #1a1a1a | #ececec | body |
| `--muted` | #5f5f5f | #a0a0a0 | labels, tool args |
| `--accent` | #2a5bd7 | #7aa2ff | links, send button, focus ring |
| `--ok` | #1e7a46 | #5fcf8e | online dot |
| `--bad` | #b3261e | #ff8a80 | error banner |

Contrast: body text and accent on `--bg` must be at least 4.5:1. Check with a contrast tool before shipping; these values are not yet measured.

## Type
- UI: system font stack (`system-ui, -apple-system, Segoe UI, sans-serif`).
- Code and tool args: system monospace stack.
- Sizes: 15px body, 13px labels, 20px page title. Line height 1.5.

## Spacing and shape
4px base grid (4, 8, 12, 16, 24, 32). Radius 8px for cards, 6px for inputs. 1px borders in `--muted` at 25% opacity. Max message width 72ch.

## Motion
Only a blinking cursor while streaming and a 150ms fade for the tool card expand. Disabled under `prefers-reduced-motion`.

## Voice-state indicator (week 5)
Four states shown as text + icon: idle, listening, thinking, speaking. Colour is secondary.
