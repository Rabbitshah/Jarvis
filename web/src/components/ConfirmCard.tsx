import type { Proposal } from "../state";

type Props = { proposal: Proposal; onDecide: (approve: boolean) => void };

/** Nothing is saved until the user clicks a real button here. */
export function ConfirmCard({ proposal: p, onDecide }: Props) {
  return (
    <section className="confirm" aria-label="Save to memory?">
      <h2>Save to memory?</h2>
      <p className="fact">{p.fact}</p>
      {p.status === "done" ? (
        <p role="status">{p.message}</p>
      ) : (
        <>
          {p.fromContext && (
            <p className="warn">Notes were in Jarvis's context this turn. Check this fact is really yours.</p>
          )}
          <div className="row">
            <button type="button" className="primary" disabled={p.status === "saving"} onClick={() => onDecide(true)}>
              Save
            </button>
            <button type="button" disabled={p.status === "saving"} onClick={() => onDecide(false)}>
              Don't save
            </button>
          </div>
        </>
      )}
    </section>
  );
}
