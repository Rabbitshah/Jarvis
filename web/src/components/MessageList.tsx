import { useEffect, useRef, useState } from "react";
import type { Msg, Proposal } from "../state";
import { Icon } from "./Icon";
import { EmptyState } from "./EmptyState";
import { Message } from "./Message";

type Props = {
  messages: Msg[];
  streaming: boolean;
  onPick: (text: string) => void;
  onDecide: (p: Proposal, approve: boolean) => void;
};

export function MessageList({ messages, streaming, onPick, onDecide }: Props) {
  const box = useRef<HTMLDivElement>(null);
  const stick = useRef(true);
  const [away, setAway] = useState(false);

  const toBottom = () => {
    const el = box.current;
    if (el) el.scrollTop = el.scrollHeight;
  };

  useEffect(() => {
    if (stick.current) toBottom();
  }, [messages]);

  const onScroll = () => {
    const el = box.current;
    if (!el) return;
    stick.current = el.scrollHeight - el.scrollTop - el.clientHeight < 40;
    setAway(!stick.current);
  };

  return (
    <div className="list-wrap">
      <div className="list" ref={box} onScroll={onScroll}>
        <div className="column">
          {messages.length === 0 ? (
            <EmptyState onPick={onPick} />
          ) : (
            messages.map((m, i) => (
              <Message key={m.id} msg={m} live={streaming && i === messages.length - 1} onDecide={onDecide} />
            ))
          )}
        </div>
      </div>
      {away && (
        <button
          type="button"
          className="jump"
          onClick={() => {
            stick.current = true;
            setAway(false);
            toBottom();
          }}
        >
          <Icon name="down" size={16} /> Jump to latest
        </button>
      )}
    </div>
  );
}
