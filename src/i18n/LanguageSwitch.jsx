import { LANGUAGES, useLang, useT } from "./index";

const LABELS = { en: "EN", ru: "RU" };

/** Two small buttons, EN | RU. */
function LanguageSwitch() {
  const { lang, setLang } = useLang();
  const t = useT();
  return (
    <div className="lang-switch" role="group" aria-label={t("lang.switch")}>
      {LANGUAGES.map((code) => (
        <button
          key={code}
          type="button"
          className={`lang-switch-button ${lang === code ? "is-selected" : ""}`}
          aria-pressed={lang === code}
          onClick={() => setLang(code)}
        >
          {LABELS[code]}
        </button>
      ))}
    </div>
  );
}

export default LanguageSwitch;
