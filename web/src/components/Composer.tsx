import { useEffect, useRef } from "react";

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
          rows={2}
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
            Stop
          </button>
        ) : (
          <button type="submit" className="primary" disabled={!ready}>
            Send
          </button>
        )}
      </div>
    </form>
  );
}
