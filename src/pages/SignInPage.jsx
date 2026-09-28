import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { ErrorMessage } from "../components/StatusMessage";
import { login, register } from "../api/client";
import { useAuth } from "../auth/context";
import { readLocal } from "../saved/localList";

/**
 * Sign in, or create an account. Creating one emails a six-digit code (and a
 * link) to confirm the address; the next screen takes the code.
 */
function SignInPage() {
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
        <PageHeader title={isRegister ? "Create account" : "Sign in"} backTo="/" />

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
              Sign in
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
              Create account
            </button>
          </div>

          <p className="lede">
            {isRegister
              ? "Your level, streak, progress and saved cards will follow you to any device."
              : "Welcome back. Pick up where you left off."}
          </p>

          <form className="sign-in-form" onSubmit={handleSubmit}>
            {isRegister && (
              <label className="field">
                <span className="field-label">Name</span>
                <input
                  className="field-input"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Anton"
                  autoComplete="name"
                  required
                />
              </label>
            )}

            <label className="field">
              <span className="field-label">Email</span>
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
              <span className="field-label">Password</span>
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
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  type="button"
                >
                  <span className="material-symbols-outlined">
                    {showPassword ? "visibility_off" : "visibility"}
                  </span>
                </button>
              </span>
              {isRegister && (
                <span className="field-help">At least 8 characters, mixing letters with numbers or symbols.</span>
              )}
            </label>

            {pending.length > 0 && (
              <p className="section-note">
                The {pending.length} card{pending.length === 1 ? "" : "s"} saved in this browser, and
                your progress so far, will be added to your account.
              </p>
            )}

            {error && <ErrorMessage error={error} />}

            <button className="primary-button" type="submit" disabled={busy}>
              {busy ? "One moment..." : isRegister ? "Create account" : "Sign in"}
            </button>
          </form>

          {!isRegister && (
            <p className="form-links">
              <Link to={`/reset-password${email ? `?email=${encodeURIComponent(email)}` : ""}`}>
                Forgot password?
              </Link>
            </p>
          )}
        </section>
      </div>
    </main>
  );
}

export default SignInPage;
