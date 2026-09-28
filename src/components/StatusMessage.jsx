/**
 * The three states every data-loading screen has to show: waiting, broken, or
 * working-but-empty. Keeping them here means each page handles them the same
 * way instead of inventing its own.
 */

export function Loading({ label = "Loading..." }) {
  return (
    <p className="status-message" role="status">
      {label}
    </p>
  );
}

export function ErrorMessage({ error, onRetry }) {
  return (
    <div className="status-message status-error" role="alert">
      <p>{error?.message ?? "Something went wrong."}</p>
      {onRetry && (
        <button className="text-button" onClick={onRetry} type="button">
          Try again
        </button>
      )}
    </div>
  );
}

export function EmptyMessage({ children }) {
  return <p className="status-message">{children}</p>;
}
