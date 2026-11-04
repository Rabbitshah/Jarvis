import type { Health } from "../api";
import { Icon } from "./Icon";

type Props = { health: Health | null; online: boolean; onNewChat: () => void };

export function Header({ health, online, onNewChat }: Props) {
  return (
    <header className="header">
      <div className="column header-row">
        <span className="mark" aria-hidden="true">J</span>
        <div className="title">
          <h1>Jarvis</h1>
          <span className="model">{health?.model ?? "local assistant"}</span>
        </div>
        <span className={`status ${online ? "on" : "off"}`} role="status">
          <span className="dot" aria-hidden="true" />
          {online ? "online" : "Ollama not reachable"}
        </span>
        <button type="button" className="ghost" onClick={onNewChat}>
          <Icon name="plus" size={16} /> New chat
        </button>
      </div>
    </header>
  );
}
