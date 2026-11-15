import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";

const SCRIPT = [
  { type: "token", text: "Let me check. " },
  { type: "tool_call", name: "get_time", args: {} },
  { type: "tool_result", name: "get_time", result: "12:00" },
  { type: "token", text: "<b>It is noon</b>" },
  { type: "sources", files: ["a.md", "b.md"] },
  { type: "confirm", id: "p1", fact: "I like tea", from_context: true },
  { type: "done" },
];

let calls: string[];
beforeEach(() => {
  calls = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string) => {
      calls.push(url);
      if (url === "/health") return Response.json({ status: "ok", ollama: true, model: "m1", tools: [] });
      if (url === "/confirm") return Response.json({ message: "Saved." });
      const body = SCRIPT.map((e) => `data: ${JSON.stringify(e)}\n\n`).join("");
      return new Response(body, { headers: { "content-type": "text/event-stream" } });
    }),
  );
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

async function ask() {
  render(<App />);
  fireEvent.change(screen.getByLabelText("Message to Jarvis"), { target: { value: "time?" } });
  fireEvent.click(screen.getByRole("button", { name: "Send" }));
  await screen.findByText("Save to memory?");
}

describe("Undo after a direct save", () => {
  const SAVED = [
    { type: "token", text: "Saved to memory.md." },
    { type: "saved", fact: "You like tea" },
    { type: "done" },
  ];
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string) => {
        calls.push(url);
        if (url === "/health") return Response.json({ status: "ok", ollama: true, model: "m1", tools: [] });
        if (url === "/forget") return Response.json({ message: "Removed: You like tea" });
        return new Response(SAVED.map((e) => `data: ${JSON.stringify(e)}\n\n`).join(""), { headers: { "content-type": "text/event-stream" } });
      }),
    );
  });
  const say = (text: string) => {
    fireEvent.change(screen.getByLabelText("Message to Jarvis"), { target: { value: text } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));
  };

  it("shows a real Undo button, calls /forget only on click, then shows the answer instead", async () => {
    render(<App />);
    say("remember that I like tea");
    const btn = await screen.findByRole("button", { name: "Undo" });
    await new Promise((r) => setTimeout(r, 50));
    expect(calls).not.toContain("/forget"); // never clicked by itself
    fireEvent.click(btn);
    await screen.findByText("Removed: You like tea");
    expect(calls.filter((c) => c === "/forget")).toHaveLength(1);
    expect(screen.queryByRole("button", { name: "Undo" })).toBeNull();
  });
  it("removes the Undo button when the next message is sent", async () => {
    render(<App />);
    say("remember that I like tea");
    await screen.findByRole("button", { name: "Undo" });
    say("what time is it");
    await waitFor(() => expect(calls.filter((c) => c === "/chat")).toHaveLength(2));
    await new Promise((r) => setTimeout(r, 50)); // second reply finished streaming
    expect(screen.getAllByRole("button", { name: "Undo" })).toHaveLength(1); // only the new reply has one: the old one is gone
    expect(calls.filter((c) => c === "/forget")).toHaveLength(0);
  });
});

describe("App with a scripted stream", () => {
  it("shows reply as plain text, tool card, sources and the confirm card", async () => {
    await ask();
    expect(screen.getByText(/<b>It is noon<\/b>/)).toBeTruthy(); // not rendered as HTML
    expect(document.querySelector("b")).toBeNull();
    expect(screen.getByText("get_time")).toBeTruthy();
    expect(screen.getByText("a.md")).toBeTruthy();
    expect(screen.getByText(/Check this fact is really yours/)).toBeTruthy();
  });
  it("calls /confirm only when the user clicks a button", async () => {
    await ask();
    await new Promise((r) => setTimeout(r, 50));
    expect(calls).not.toContain("/confirm");
    fireEvent.click(screen.getByRole("button", { name: "Save" }));
    await screen.findByText("Saved.");
    expect(calls.filter((c) => c === "/confirm")).toHaveLength(1);
  });
  it("disables the composer when Ollama is offline", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => Response.json({ status: "ok", ollama: false, model: "m1", tools: [] })));
    render(<App />);
    await waitFor(() => expect(screen.getByText(/Start it with scripts\/run.sh --api/)).toBeTruthy());
    expect((screen.getByLabelText("Message to Jarvis") as HTMLTextAreaElement).disabled).toBe(true);
  });
});
