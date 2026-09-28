import { useT } from "../i18n";

/**
 * The six-digit code from an email. One field (so paste and the phone's
 * "from Messages/Mail" suggestion both work), drawn as six boxes.
 */
function CodeInput({ value, onChange, autoFocus = true }) {
  const t = useT();
  const digits = value.replace(/\D/g, "").slice(0, 6);
  return (
    <label className="code-input">
      <span className="field-label">{t("code.label")}</span>
      <span className="code-boxes">
        <input
          value={digits}
          onChange={(e) => onChange(e.target.value.replace(/\D/g, "").slice(0, 6))}
          inputMode="numeric"
          autoComplete="one-time-code"
          pattern="\d{6}"
          maxLength={6}
          autoFocus={autoFocus}
          aria-label={t("code.aria")}
          required
        />
        {Array.from({ length: 6 }, (_, i) => (
          <span
            key={i}
            className={`code-box ${i === digits.length ? "is-current" : ""}`}
            aria-hidden="true"
          >
            {digits[i] ?? ""}
          </span>
        ))}
      </span>
    </label>
  );
}

export default CodeInput;
