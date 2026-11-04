import { Icon } from "./Icon";

type Props = { message: string; onDismiss?: () => void };

export function ErrorBanner({ message, onDismiss }: Props) {
  return (
    <div className="banner" role="alert">
      <span>{message}</span>
      {onDismiss && (
        <button type="button" className="ghost icon-btn" onClick={onDismiss} aria-label="Dismiss error">
          <Icon name="close" size={16} />
        </button>
      )}
    </div>
  );
}
