import { useEffect } from "react";

/** A panel that slides up from the bottom; closes on the backdrop or Escape. */
function BottomSheet({ open, onClose, title, children }) {
  useEffect(() => {
    if (!open) return undefined;
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  return (
    <div className={`sheet-root ${open ? "is-open" : ""}`} aria-hidden={!open}>
      <div className="sheet-backdrop" onClick={onClose} />
      <section className="sheet" role="dialog" aria-modal="true" aria-label={title}>
        <div className="sheet-handle" aria-hidden="true" />
        <header className="sheet-header">
          <h2>{title}</h2>
          <button className="icon-button" onClick={onClose} aria-label="Close" type="button">
            <span className="material-symbols-outlined">close</span>
          </button>
        </header>
        <div className="sheet-body">{children}</div>
      </section>
    </div>
  );
}

export default BottomSheet;
