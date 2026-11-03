import { parseSSE, type ChatEvent } from "./sse";

export type Health = { ollama: boolean; model: string };

export async function health(): Promise<Health> {
  const r = await fetch("/health");
  if (!r.ok) throw new Error(`health ${r.status}`);
  return r.json();
}

export async function* chat(message: string, sessionId: string, signal: AbortSignal): AsyncGenerator<ChatEvent> {
  const r = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
    signal,
  });
  if (!r.ok || !r.body) throw new Error(`The server answered ${r.status}.`);
  yield* parseSSE(r.body);
}

export async function confirm(sessionId: string, id: string, approve: boolean): Promise<string> {
  const r = await fetch("/confirm", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, id, approve }),
  });
  if (!r.ok) throw new Error(`The server answered ${r.status}.`);
  return (await r.json()).message;
}
