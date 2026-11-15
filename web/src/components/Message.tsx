import { motion } from "motion/react";
import type { Msg, Proposal } from "../state";
import { ConfirmCard } from "./ConfirmCard";
import { SourceChips } from "./SourceChips";
import { ToolCard } from "./ToolCard";

type Props = {
  msg: Msg;
  live: boolean;
  onDecide: (p: Proposal, approve: boolean) => void;
  onUndo: (id: number) => void;
};

export function Message({ msg, live, onDecide, onUndo }: Props) {
  if (msg.role === "user") {
    return (
      <motion.div className="msg user" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }}>
        <div className="bubble">{msg.text}</div>
      </motion.div>
    );
  }
  const lastIsText = msg.parts[msg.parts.length - 1]?.kind === "text";
  return (
    <motion.div className="msg assistant" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }}>
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
      {msg.undo?.status === "done" ? (
        <p className="muted" role="status">{msg.undo.message}</p>
      ) : (
        msg.undo && !live && (
          <button type="button" className="undo" disabled={msg.undo.status === "working"} onClick={() => onUndo(msg.id)}>
            Undo
          </button>
        )
      )}
      <SourceChips files={msg.sources} />
      {msg.proposals.map((p) => (
        <ConfirmCard key={p.id} proposal={p} onDecide={(a) => onDecide(p, a)} />
      ))}
    </motion.div>
  );
}
