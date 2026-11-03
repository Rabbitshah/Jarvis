import type { Health } from "../api";

type Props = { health: Health | null; online: boolean; onNewChat: () => void };

export function Header({ health, online, onNewChat }: Props) {
  return (
    <header className="header">
      <h1>Jarvis</h1>
      <span className="model">{health?.model ?? ""}</span>
      <span className={`status ${online ? "on" : "off"}`} role="status">
        <span className="dot" aria-hidden="true" />
        {online ? "online" : "Ollama not reachable"}
      </span>
      <button type="button" className="ghost" onClick={onNewChat}>
        New chat
      </button>
    </header>
  );
}
