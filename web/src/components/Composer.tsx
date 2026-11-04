import { useEffect, useRef } from "react";
import { Icon } from "./Icon";

export const MAX = 4000;

type Props = {
  value: string;
  onChange: (v: string) => void;
  onSend: () => void;
  onStop: () => void;
  streaming: boolean;
  disabled: boolean;
};

export function Composer({ value, onChange, onSend, onStop, streaming, disabled }: Props) {
  const ta = useRef<HTMLTextAreaElement>(null);
  const was = useRef(false);

  useEffect(() => {
    if (was.current && !streaming) ta.current?.focus(); // back to the composer after a reply
    was.current = streaming;
  }, [streaming]);

  useEffect(() => {
    if (value && !streaming) ta.current?.focus(); // an example question was picked
  }, [value, streaming]);

  useEffect(() => {
    const el = ta.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = Math.min(el.scrollHeight, 160) + "px";
    }
  }, [value]);

  const ready = !disabled && value.trim().length > 0 && value.length <= MAX;
  return (
    <form
      className="composer"
      onSubmit={(e) => {
        e.preventDefault();
        if (streaming) onStop();
        else if (ready) onSend();
      }}
    >
      <div className="column composer-row">
        <textarea
          ref={ta}
          aria-label="Message to Jarvis"
          placeholder="Ask Jarvis…"
          rows={1}
          maxLength={MAX}
          value={value}
          disabled={disabled || streaming}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
              e.preventDefault();
              if (ready) onSend();
            }
          }}
        />
        {value.length > MAX - 500 && (
          <span className="counter" aria-live="polite">
            {value.length} / {MAX}
          </span>
        )}
        {streaming ? (
          <button type="button" className="primary" onClick={onStop}>
            <Icon name="stop" size={14} /> Stop
          </button>
        ) : (
          <button type="submit" className="primary" disabled={!ready}>
            Send <Icon name="send" size={16} />
          </button>
        )}
      </div>
      <p className="column hint">Enter to send · Shift+Enter for a new line</p>
    </form>
  );
}
