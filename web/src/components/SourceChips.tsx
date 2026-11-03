export function SourceChips({ files }: { files: string[] }) {
  if (files.length === 0) return null;
  return (
    <div className="sources">
      <span>Notes consulted:</span>
      {files.map((f) => (
        <span className="chip" key={f}>
          {f}
        </span>
      ))}
    </div>
  );
}
