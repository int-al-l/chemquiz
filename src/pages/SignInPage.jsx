import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { ErrorMessage } from "../components/StatusMessage";
import { login, register } from "../api/client";
import { useAuth } from "../auth/context";
import { useT } from "../i18n";
import { readLocal } from "../saved/localList";

/**
 * Sign in, or create an account. Creating one emails a six-digit code (and a
 * link) to confirm the address; the next screen takes the code.
 */
function SignInPage() {
  const t = useT();
  const navigate = useNavigate();
  const location = useLocation();
  const { user, completeSignIn } = useAuth();

  const [tab, setTab] = useState(location.state?.tab ?? "signin");
  const [name, setName] = useState("");
  const [email, setEmail] = useState(location.state?.email ?? "");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const pending = readLocal();

  if (user) return <Navigate to="/profile" replace />;

  async function handleSubmit(event) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      if (tab === "signin") {
        const fresh = await login({ email, password });
        await completeSignIn(fresh);
        navigate("/", { replace: true });
      } else {
        const sent = await register({ name, email, password });
        navigate(`/verify-email?email=${encodeURIComponent(sent.email)}`, { replace: true });
      }
    } catch (err) {
      if (err.status === 403) {
        // Registered but never verified: a fresh code has just been sent.
        navigate(`/verify-email?email=${encodeURIComponent(email.trim().toLowerCase())}`);
        return;
      }
      setError(err);
      setBusy(false);
    }
  }

  const isRegister = tab === "register";

  return (
    <main className="categories-page">
      <div className="page-layout">
        <PageHeader title={isRegister ? t("signin.create") : t("common.signIn")} backTo="/" />

        <section className="categories-content narrow">
          <div className="tabs" role="tablist">
            <button
              role="tab"
              aria-selected={!isRegister}
              className={!isRegister ? "is-selected" : ""}
              onClick={() => {
                setTab("signin");
                setError(null);
              }}
              type="button"
            >
              {t("common.signIn")}
            </button>
            <button
              role="tab"
              aria-selected={isRegister}
              className={isRegister ? "is-selected" : ""}
              onClick={() => {
                setTab("register");
                setError(null);
              }}
              type="button"
            >
              {t("signin.create")}
            </button>
          </div>

          <p className="lede">
            {isRegister
              ? t("signin.registerLede")
              : t("signin.lede")}
          </p>

          <form className="sign-in-form" onSubmit={handleSubmit}>
            {isRegister && (
              <label className="field">
                <span className="field-label">{t("signin.name")}</span>
                <input
                  className="field-input"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder={t("signin.namePlaceholder")}
                  autoComplete="name"
                  required
                />
              </label>
            )}

            <label className="field">
              <span className="field-label">{t("common.email")}</span>
              <input
                className="field-input"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@university.edu"
                autoComplete="email"
                required
              />
            </label>

            <label className="field">
              <span className="field-label">{t("signin.password")}</span>
              <span className="password-wrap">
                <input
                  className="field-input"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete={isRegister ? "new-password" : "current-password"}
                  minLength={isRegister ? 8 : undefined}
                  required
                />
                <button
                  className="icon-button password-eye"
                  onClick={() => setShowPassword((v) => !v)}
                  aria-label={t(showPassword ? "signin.hidePassword" : "signin.showPassword")}
                  type="button"
                >
                  <span className="material-symbols-outlined">
                    {showPassword ? "visibility_off" : "visibility"}
                  </span>
                </button>
              </span>
              {isRegister && (
                <span className="field-help">{t("common.passwordHelp")}</span>
              )}
            </label>

            {pending.length > 0 && (
              <p className="section-note">
                {t("signin.pending", { n: pending.length })}
              </p>
            )}

            {error && <ErrorMessage error={error} />}

            <button className="primary-button" type="submit" disabled={busy}>
              {busy ? t("signin.busy") : isRegister ? t("signin.create") : t("common.signIn")}
            </button>
          </form>

          {!isRegister && (
            <p className="form-links">
              <Link to={`/reset-password${email ? `?email=${encodeURIComponent(email)}` : ""}`}>
                {t("signin.forgot")}
              </Link>
            </p>
          )}
        </section>
      </div>
    </main>
  );
}

export default SignInPage;
