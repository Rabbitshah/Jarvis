import { useEffect, useReducer, useRef, useState } from "react";
import { chat, confirm, forget, health as getHealth, type Health } from "./api";
import { Composer } from "./components/Composer";
import { ErrorBanner } from "./components/ErrorBanner";
import { Header } from "./components/Header";
import { MessageList } from "./components/MessageList";
import { initial, reducer, type Proposal } from "./state";
import { loadSessionId, newSessionId, saveSessionId } from "./session";

const OFFLINE = "Ollama not reachable. Start it with scripts/run.sh --api";

export function App() {
  const [state, dispatch] = useReducer(reducer, initial);
  const [draft, setDraft] = useState("");
  const [health, setHealth] = useState<Health | null>(null);
  const [online, setOnline] = useState(true);
  const session = useRef(loadSessionId());
  const abort = useRef<AbortController | null>(null);

  useEffect(() => {
    const poll = () =>
      getHealth().then(
        (h) => {
          setHealth(h);
          setOnline(h.ollama);
        },
        () => setOnline(false),
      );
    poll();
    const t = setInterval(poll, 15000);
    return () => clearInterval(t);
  }, []);

  async function send() {
    const text = draft.trim();
    if (!text || state.streaming) return;
    setDraft("");
    dispatch({ type: "send", text });
    const ac = new AbortController();
    abort.current = ac;
    try {
      for await (const event of chat(text, session.current, ac.signal)) dispatch({ type: "event", event });
      dispatch({ type: "event", event: { type: "done" } }); // also covers a stream that ends without `done`
    } catch (e) {
      if (ac.signal.aborted) dispatch({ type: "stopped" });
      else dispatch({ type: "failed", message: e instanceof Error ? e.message : "Network error." });
    }
  }

  async function decide(p: Proposal, approve: boolean) {
    dispatch({ type: "proposal", id: p.id, patch: { status: "saving" } });
    try {
      const message = await confirm(session.current, p.id, approve);
      dispatch({ type: "proposal", id: p.id, patch: { status: "done", message } });
    } catch (e) {
      dispatch({ type: "proposal", id: p.id, patch: { status: "pending" } });
      dispatch({ type: "failed", message: e instanceof Error ? e.message : "Network error." });
    }
  }

  async function undo(id: number) {
    dispatch({ type: "undo", id, undo: { status: "working" } });
    try {
      const message = await forget(session.current);
      dispatch({ type: "undo", id, undo: { status: "done", message } });
    } catch (e) {
      dispatch({ type: "undo", id, undo: { status: "ready" } });
      dispatch({ type: "failed", message: e instanceof Error ? e.message : "Network error." });
    }
  }

  function newChat() {
    abort.current?.abort();
    session.current = saveSessionId(newSessionId());
    dispatch({ type: "reset" });
    setDraft("");
  }

  return (
    <div className="app">
      <Header health={health} online={online} onNewChat={newChat} />
      <MessageList messages={state.messages} streaming={state.streaming} onPick={setDraft} onDecide={decide} onUndo={undo} />
      <div className="column banners">
        {!online && <ErrorBanner message={OFFLINE} />}
        {state.error && <ErrorBanner message={state.error} onDismiss={() => dispatch({ type: "dismiss_error" })} />}
      </div>
      <Composer
        value={draft}
        onChange={setDraft}
        onSend={send}
        onStop={() => abort.current?.abort()}
        streaming={state.streaming}
        disabled={!online}
      />
    </div>
  );
}
