import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import CodeInput from "../components/CodeInput";
import DemoInbox from "../components/DemoInbox";
import PageHeader from "../components/PageHeader";
import { ErrorMessage } from "../components/StatusMessage";
import { forgotPassword, resetPassword } from "../api/client";
import { useAuth } from "../auth/context";
import { rich, useT } from "../i18n";

/**
 * Forgotten password, in two steps: ask for a code, then enter it with a new
 * password. Arriving from the link in the email (?token=...) skips straight
 * to choosing the password.
 */
function ResetPasswordPage() {
  const t = useT();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const { completeSignIn } = useAuth();

  const token = params.get("token");
  const [email, setEmail] = useState(params.get("email") ?? "");
  const [step, setStep] = useState(token ? "password" : "email");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  async function requestCode(event) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const sent = await forgotPassword(email);
      setEmail(sent.email);
      setStep("password");
    } catch (err) {
      setError(err);
    }
    setBusy(false);
  }

  async function setNew(event) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const fresh = await resetPassword(
        token ? { token, password } : { email, code, password },
      );
      await completeSignIn(fresh);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err);
      setBusy(false);
    }
  }

  return (
    <main className="categories-page">
      <div className="page-layout">
        <PageHeader title={t("reset.title")} backTo="/sign-in" />

        <section className="categories-content narrow">
          {step === "email" ? (
            <form className="sign-in-form" onSubmit={requestCode}>
              <p className="lede">
                {t("reset.lede")}
              </p>
              <label className="field">
                <span className="field-label">{t("common.email")}</span>
                <input
                  className="field-input"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="email"
                  required
                />
              </label>
              {error && <ErrorMessage error={error} />}
              <button className="primary-button" type="submit" disabled={busy}>
                {busy ? t("reset.sending") : t("reset.send")}
              </button>
            </form>
          ) : (
            <form className="sign-in-form" onSubmit={setNew}>
              {!token && (
                <>
                  <p className="lede">
                    {rich(t("reset.sent"), { email: <strong>{email}</strong> })}
                  </p>
                  <DemoInbox email={email} refresh={step} />
                  <CodeInput value={code} onChange={setCode} />
                </>
              )}
              {token && <p className="lede">{t("reset.choose")}</p>}
              <label className="field">
                <span className="field-label">{t("reset.newPassword")}</span>
                <input
                  className="field-input"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="new-password"
                  minLength={8}
                  required
                />
                <span className="field-help">{t("common.passwordHelp")}</span>
              </label>
              {error && <ErrorMessage error={error} />}
              <button
                className="primary-button"
                type="submit"
                disabled={busy || (!token && code.length !== 6)}
              >
                {busy ? t("reset.saving") : t("reset.save")}
              </button>
              {!token && (
                <button className="text-button" onClick={() => setStep("email")} type="button">
                  {t("reset.otherEmail")}
                </button>
              )}
            </form>
          )}

          <p className="form-links">
            <Link to="/sign-in">{t("reset.backToSignIn")}</Link>
          </p>
        </section>
      </div>
    </main>
  );
}

export default ResetPasswordPage;
