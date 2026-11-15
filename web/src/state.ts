import type { ChatEvent } from "./sse";

export type Part =
  | { kind: "text"; text: string }
  | { kind: "tool"; name: string; args: Record<string, unknown>; result?: string };

export type Proposal = {
  id: string;
  fact: string;
  fromContext: boolean;
  status: "pending" | "saving" | "done";
  message?: string;
};

export type Undo = { status: "ready" | "working" | "done"; message?: string };

export type Msg =
  | { id: number; role: "user"; text: string }
  | { id: number; role: "assistant"; parts: Part[]; sources: string[]; proposals: Proposal[]; stopped: boolean; undo?: Undo };

export type State = { messages: Msg[]; streaming: boolean; error: string | null; nextId: number };

export type Action =
  | { type: "send"; text: string }
  | { type: "event"; event: ChatEvent }
  | { type: "stopped" }
  | { type: "failed"; message: string }
  | { type: "dismiss_error" }
  | { type: "proposal"; id: string; patch: Partial<Proposal> }
  | { type: "undo"; id: number; undo: Undo }
  | { type: "reset" };

export const initial: State = { messages: [], streaming: false, error: null, nextId: 1 };

function lastAssistant(s: State, f: (m: Extract<Msg, { role: "assistant" }>) => Msg): State {
  const i = s.messages.length - 1;
  const m = s.messages[i];
  if (!m || m.role !== "assistant") return s;
  return { ...s, messages: [...s.messages.slice(0, i), f(m)] };
}

function applyEvent(s: State, ev: ChatEvent): State {
  switch (ev.type) {
    case "token":
      return lastAssistant(s, (m) => {
        const last = m.parts[m.parts.length - 1];
        const parts: Part[] =
          last?.kind === "text"
            ? [...m.parts.slice(0, -1), { kind: "text", text: last.text + ev.text }]
            : [...m.parts, { kind: "text", text: ev.text }];
        return { ...m, parts };
      });
    case "tool_call":
      return lastAssistant(s, (m) => ({ ...m, parts: [...m.parts, { kind: "tool", name: ev.name, args: ev.args }] }));
    case "tool_result":
      return lastAssistant(s, (m) => {
        const i = m.parts.findLastIndex((p) => p.kind === "tool" && p.name === ev.name && p.result === undefined);
        const p = m.parts[i];
        if (!p || p.kind !== "tool") return m;
        return { ...m, parts: [...m.parts.slice(0, i), { ...p, result: ev.result }, ...m.parts.slice(i + 1)] };
      });
    case "sources":
      return lastAssistant(s, (m) => ({ ...m, sources: ev.files }));
    case "confirm":
      return lastAssistant(s, (m) => ({
        ...m,
        proposals: [...m.proposals, { id: ev.id, fact: ev.fact, fromContext: ev.from_context, status: "pending" }],
      }));
    case "saved": // the reply that says "Saved to memory.md." gets an Undo button
      return lastAssistant(s, (m) => ({ ...m, undo: { status: "ready" } }));
    case "error":
      return { ...s, error: ev.message };
    case "done":
      return { ...s, streaming: false };
  }
}

export function reducer(s: State, a: Action): State {
  switch (a.type) {
    case "send":
      return {
        ...s,
        streaming: true,
        error: null,
        nextId: s.nextId + 2,
        messages: [
          // sending the next message removes any Undo button still on screen (a finished one keeps its note)
          ...s.messages.map((m) => (m.role === "assistant" && m.undo && m.undo.status !== "done" ? { ...m, undo: undefined } : m)),
          { id: s.nextId, role: "user", text: a.text },
          { id: s.nextId + 1, role: "assistant", parts: [], sources: [], proposals: [], stopped: false },
        ],
      };
    case "event":
      return applyEvent(s, a.event);
    case "stopped":
      return { ...lastAssistant(s, (m) => ({ ...m, stopped: true })), streaming: false };
    case "failed":
      return { ...s, streaming: false, error: a.message };
    case "dismiss_error":
      return { ...s, error: null };
    case "proposal":
      // Only the Save / Don't save buttons dispatch this; a `confirm` event never does.
      return {
        ...s,
        messages: s.messages.map((m) =>
          m.role === "assistant"
            ? { ...m, proposals: m.proposals.map((p) => (p.id === a.id ? { ...p, ...a.patch } : p)) }
            : m,
        ),
      };
    case "undo":
      return { ...s, messages: s.messages.map((m) => (m.id === a.id && m.role === "assistant" ? { ...m, undo: a.undo } : m)) };
    case "reset":
      return { ...initial, nextId: s.nextId };
  }
}
