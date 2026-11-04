import { useState } from "react";
import { Icon } from "./Icon";

const LIMIT = 500;

type Props = { name: string; args: Record<string, unknown>; result?: string; running: boolean };

export function ToolCard({ name, args, result, running }: Props) {
  const [all, setAll] = useState(false);
  const argText = Object.entries(args)
    .map(([k, v]) => `${k}=${JSON.stringify(v)}`)
    .join(", ");
  const long = result !== undefined && result.length > LIMIT;
  return (
    <details className="tool">
      <summary>
        <span className="chev"><Icon name="chevron" size={14} /></span>
        <span className="tool-name">{name}</span>
        <span className="tool-args">({argText})</span>
        {result !== undefined ? (
          <span className="tool-done" role="img" aria-label="done"><Icon name="check" size={14} /></span>
        ) : (
          running && <span className="spinner" role="img" aria-label="running" />
        )}
      </summary>
      <div className="tool-body">
        {result === undefined ? (
          <em>{running ? "Running…" : "No result."}</em>
        ) : (
          <>
            <pre>{all || !long ? result : result.slice(0, LIMIT) + "…"}</pre>
            {long && (
              <button type="button" className="link" onClick={() => setAll(!all)}>
                {all ? "show less" : "show more"}
              </button>
            )}
          </>
        )}
      </div>
    </details>
  );
}
