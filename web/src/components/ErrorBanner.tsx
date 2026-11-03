type Props = { message: string; onDismiss?: () => void };

export function ErrorBanner({ message, onDismiss }: Props) {
  return (
    <div className="banner" role="alert">
      <span>{message}</span>
      {onDismiss && (
        <button type="button" className="ghost" onClick={onDismiss} aria-label="Dismiss error">
          ✕
        </button>
      )}
    </div>
  );
}
