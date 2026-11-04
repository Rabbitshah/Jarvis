const EXAMPLES = ["What did I write about my projects?", "What time is it?"];

export function EmptyState({ onPick }: { onPick: (text: string) => void }) {
  return (
    <div className="empty">
      <span className="mark big" aria-hidden="true">J</span>
      <h2>How can I help?</h2>
      <p>Ask about your notes, or ask for the time. Everything runs on this computer.</p>
      <div className="examples">
        {EXAMPLES.map((q) => (
          <button type="button" key={q} className="example" onClick={() => onPick(q)}>
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
