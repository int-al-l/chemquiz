import { useNavigate } from "react-router-dom";

import { useT } from "../i18n";

/**
 * The title bar shared by every screen.
 *
 * `backTo` names an explicit destination. Without it the button walks the
 * browser's history, which is right when a page can be reached from more than
 * one place -- a quiz can start from a category or from the main menu.
 */
function PageHeader({ title, backTo, onBack }) {
  const navigate = useNavigate();
  const t = useT();

  const showBack = backTo !== undefined || onBack !== undefined;

  function handleBack() {
    if (onBack) {
      onBack();
    } else if (backTo) {
      navigate(backTo);
    } else {
      navigate(-1);
    }
  }

  return (
    <header className="page-header">
      {showBack && (
        <button
          className="back-icon-button"
          onClick={handleBack}
          aria-label={t("common.goBack")}
          type="button"
        >
          <span className="material-symbols-outlined">arrow_back</span>
        </button>
      )}

      <h1 className="page-title">{title}</h1>
    </header>
  );
}

export default PageHeader;
