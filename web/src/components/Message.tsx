import type { Msg, Proposal } from "../state";
import { ConfirmCard } from "./ConfirmCard";
import { SourceChips } from "./SourceChips";
import { ToolCard } from "./ToolCard";

type Props = { msg: Msg; live: boolean; onDecide: (p: Proposal, approve: boolean) => void };

export function Message({ msg, live, onDecide }: Props) {
  if (msg.role === "user") {
    return (
      <div className="msg user">
        <div className="bubble">{msg.text}</div>
      </div>
    );
  }
  const lastIsText = msg.parts[msg.parts.length - 1]?.kind === "text";
  return (
    <div className="msg assistant">
      <div className="label"><span className="mark small" aria-hidden="true">J</span> Jarvis</div>
      <div aria-live="polite">
        {msg.parts.map((p, i) =>
          p.kind === "text" ? (
            <p className="text" key={i}>
              {p.text}
              {live && i === msg.parts.length - 1 && <span className="cursor" aria-hidden="true" />}
            </p>
          ) : (
            <ToolCard key={i} name={p.name} args={p.args} result={p.result} running={live} />
          ),
        )}
        {live && !lastIsText && (
          <span className="typing" role="img" aria-label="Jarvis is thinking">
            <i /><i /><i />
          </span>
        )}
        {msg.stopped && <p className="muted">(stopped)</p>}
      </div>
      <SourceChips files={msg.sources} />
      {msg.proposals.map((p) => (
        <ConfirmCard key={p.id} proposal={p} onDecide={(a) => onDecide(p, a)} />
      ))}
    </div>
  );
}
