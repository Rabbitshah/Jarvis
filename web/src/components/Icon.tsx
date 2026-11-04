const PATHS = {
  send: "M5 12h14M13 6l6 6-6 6",
  stop: "M7 7h10v10H7z",
  plus: "M12 5v14M5 12h14",
  chevron: "M9 6l6 6-6 6",
  check: "M5 12.5l4.5 4.5L19 7.5",
  down: "M12 5v14M6 13l6 6 6-6",
  close: "M6 6l12 12M18 6L6 18",
  shield: "M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z",
  file: "M7 3h7l4 4v14H7zM14 3v4h4",
} as const;

export type IconName = keyof typeof PATHS;

export function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  return (
    <svg className="icon" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={PATHS[name]} />
    </svg>
  );
}
