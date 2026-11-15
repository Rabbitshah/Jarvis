import { motion } from "motion/react";
import { Icon } from "./Icon";

type Props = { message: string; onDismiss?: () => void };

export function ErrorBanner({ message, onDismiss }: Props) {
  return (
    <motion.div className="banner" role="alert" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} transition={{ duration: 0.2 }}>
      <span>{message}</span>
      {onDismiss && (
        <button type="button" className="ghost icon-btn" onClick={onDismiss} aria-label="Dismiss error">
          <Icon name="close" size={16} />
        </button>
      )}
    </motion.div>
  );
}
