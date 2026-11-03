import { describe, expect, it } from "vitest";
import { parseSSE, type ChatEvent } from "./sse";

function stream(chunks: (string | Uint8Array)[]) {
  const enc = new TextEncoder();
  return new ReadableStream<Uint8Array>({
    start(c) {
      for (const x of chunks) c.enqueue(typeof x === "string" ? enc.encode(x) : x);
      c.close();
    },
  });
}
async function collect(chunks: (string | Uint8Array)[]) {
  const out: ChatEvent[] = [];
  for await (const e of parseSSE(stream(chunks))) out.push(e);
  return out;
}

describe("parseSSE", () => {
  it("reads several events in one chunk", async () => {
    const r = await collect(['data: {"type":"token","text":"a"}\n\ndata: {"type":"done"}\n\n']);
    expect(r).toEqual([{ type: "token", text: "a" }, { type: "done" }]);
  });
  it("joins a line split across chunks", async () => {
    const r = await collect(['data: {"type":"tok', 'en","text":"hi"}\n', "\n"]);
    expect(r).toEqual([{ type: "token", text: "hi" }]);
  });
  it("keeps a multi-byte character split across chunks", async () => {
    const bytes = new TextEncoder().encode('data: {"type":"token","text":"é€"}\n\n');
    const cut = bytes.indexOf(0xe2) + 1; // inside the 3-byte euro sign
    const r = await collect([bytes.slice(0, cut), bytes.slice(cut)]);
    expect(r).toEqual([{ type: "token", text: "é€" }]);
  });
  it("skips bad lines and keeps going", async () => {
    const r = await collect(["data: {oops\n\n", ": comment\n\n", 'data: {"type":"nope"}\n\n', 'data: {"type":"done"}\n\n']);
    expect(r).toEqual([{ type: "done" }]);
  });
  it("handles CRLF and a last line with no newline", async () => {
    const r = await collect(['data: {"type":"done"}\r\n\r\n', 'data: {"type":"token","text":"x"}']);
    expect(r).toEqual([{ type: "done" }, { type: "token", text: "x" }]);
  });
});
