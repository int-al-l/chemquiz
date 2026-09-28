/**
 * The three states every data-loading screen has to show: waiting, broken, or
 * working-but-empty. Keeping them here means each page handles them the same
 * way instead of inventing its own.
 */

import { useT } from "../i18n";

export function Loading({ label }) {
  const t = useT();
  return (
    <p className="status-message" role="status">
      {label ?? t("common.loading")}
    </p>
  );
}

export function ErrorMessage({ error, onRetry }) {
  const t = useT();
  return (
    <div className="status-message status-error" role="alert">
      <p>{error?.message ?? t("common.error")}</p>
      {onRetry && (
        <button className="text-button" onClick={onRetry} type="button">
          {t("common.retry")}
        </button>
      )}
    </div>
  );
}

export function EmptyMessage({ children }) {
  return <p className="status-message">{children}</p>;
}
