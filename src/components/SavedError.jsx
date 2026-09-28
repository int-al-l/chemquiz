import { useSaved } from "../saved/context";

/**
 * Tells the person when saving failed.
 *
 * Without this a failed save was invisible: the bookmark filled in, then
 * quietly emptied again when the request came back, which reads as the button
 * simply not working. Renders nothing when there is nothing wrong, so it can
 * sit at the top of any page that has save buttons.
 */
function SavedError() {
  const { error, dismissError } = useSaved();
  if (!error) return null;

  return (
    <div className="status-message status-error saved-error" role="alert">
      <p>{error.message}</p>
      <button className="text-button" onClick={dismissError} type="button">
        Dismiss
      </button>
    </div>
  );
}

export default SavedError;
