import { Icon } from "./Icon";

export function SourceChips({ files }: { files: string[] }) {
  if (files.length === 0) return null;
  return (
    <div className="sources">
      <span>Notes consulted:</span>
      {files.map((f) => (
        <span className="chip" key={f}>
          <Icon name="file" size={12} /> {f}
        </span>
      ))}
    </div>
  );
}
