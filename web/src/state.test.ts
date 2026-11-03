import { describe, expect, it } from "vitest";
import type { ChatEvent } from "./sse";
import { initial, reducer, type Action, type Msg } from "./state";

const run = (...actions: Action[]) => actions.reduce(reducer, initial);
const ev = (event: ChatEvent): Action => ({ type: "event", event });
const reply = (s: ReturnType<typeof run>) => s.messages[s.messages.length - 1] as Extract<Msg, { role: "assistant" }>;
const send = (): Action => ({ type: "send", text: "hi" });

describe("reducer", () => {
  it("send adds a user and an empty assistant message and starts streaming", () => {
    const s = run(send());
    expect(s.messages.map((m) => m.role)).toEqual(["user", "assistant"]);
    expect(s.streaming).toBe(true);
  });
  it("token appends to the same text part", () => {
    const s = run(send(), ev({ type: "token", text: "He" }), ev({ type: "token", text: "llo" }));
    expect(reply(s).parts).toEqual([{ kind: "text", text: "Hello" }]);
  });
  it("tool_call then tool_result fills the matching card", () => {
    const s = run(send(), ev({ type: "tool_call", name: "get_time", args: {} }), ev({ type: "tool_result", name: "get_time", result: "noon" }));
    expect(reply(s).parts).toEqual([{ kind: "tool", name: "get_time", args: {}, result: "noon" }]);
  });
  it("text after a tool starts a new part", () => {
    const s = run(send(), ev({ type: "tool_call", name: "x", args: {} }), ev({ type: "token", text: "a" }));
    expect(reply(s).parts.map((p) => p.kind)).toEqual(["tool", "text"]);
  });
  it("sources are stored on the reply", () => {
    expect(reply(run(send(), ev({ type: "sources", files: ["a.md"] }))).sources).toEqual(["a.md"]);
  });
  it("confirm only adds a pending proposal and nothing else", () => {
    const s = run(send(), ev({ type: "confirm", id: "p1", fact: "I like tea", from_context: true }));
    expect(reply(s).proposals).toEqual([{ id: "p1", fact: "I like tea", fromContext: true, status: "pending" }]);
  });
  it("error sets the banner and keeps the page usable", () => {
    const s = run(send(), ev({ type: "error", message: "boom" }), ev({ type: "done" }));
    expect(s.error).toBe("boom");
    expect(s.streaming).toBe(false);
  });
  it("done ends streaming; stopped marks the reply", () => {
    expect(run(send(), ev({ type: "done" })).streaming).toBe(false);
    const s = run(send(), { type: "stopped" });
    expect(reply(s).stopped).toBe(true);
    expect(s.streaming).toBe(false);
  });
  it("reset clears the screen", () => {
    expect(run(send(), { type: "reset" }).messages).toEqual([]);
  });
});
