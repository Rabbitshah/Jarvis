export type ChatEvent =
  | { type: "token"; text: string }
  | { type: "tool_call"; name: string; args: Record<string, unknown> }
  | { type: "tool_result"; name: string; result: string }
  | { type: "sources"; files: string[] }
  | { type: "confirm"; id: string; fact: string; from_context: boolean }
  | { type: "error"; message: string }
  | { type: "done" };

const KINDS = new Set(["token", "tool_call", "tool_result", "sources", "confirm", "error", "done"]);

function parseLine(line: string): ChatEvent | null {
  if (!line.startsWith("data:")) return null;
  try {
    const ev = JSON.parse(line.slice(5).trim());
    return ev && typeof ev === "object" && KINDS.has(ev.type) ? (ev as ChatEvent) : null;
  } catch {
    return null; // a bad line is skipped, the stream goes on
  }
}

/** Turns a byte stream of `data: <json>` lines into events. */
export async function* parseSSE(body: ReadableStream<Uint8Array>): AsyncGenerator<ChatEvent> {
  const reader = body.getReader();
  const decoder = new TextDecoder(); // stream:true below keeps split multi-byte characters whole
  let buf = "";
  try {
    for (;;) {
      const { done, value } = await reader.read();
      buf += decoder.decode(value, { stream: !done });
      const lines = buf.split("\n");
      buf = done ? "" : (lines.pop() ?? "");
      for (const raw of lines) {
        const ev = parseLine(raw.replace(/\r$/, ""));
        if (ev) yield ev;
      }
      if (done) return;
    }
  } finally {
    reader.releaseLock();
  }
}
