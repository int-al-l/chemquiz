import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import CodeInput from "../components/CodeInput";
import DemoInbox from "../components/DemoInbox";
import PageHeader from "../components/PageHeader";
import { ErrorMessage } from "../components/StatusMessage";
import { forgotPassword, resetPassword } from "../api/client";
import { useAuth } from "../auth/context";

/**
 * Forgotten password, in two steps: ask for a code, then enter it with a new
 * password. Arriving from the link in the email (?token=...) skips straight
 * to choosing the password.
 */
function ResetPasswordPage() {
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
        <PageHeader title="Reset password" backTo="/sign-in" />

        <section className="categories-content narrow">
          {step === "email" ? (
            <form className="sign-in-form" onSubmit={requestCode}>
              <p className="lede">
                Enter your email and we will send you a code to choose a new password.
              </p>
              <label className="field">
                <span className="field-label">Email</span>
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
                {busy ? "Sending..." : "Send code"}
              </button>
            </form>
          ) : (
            <form className="sign-in-form" onSubmit={setNew}>
              {!token && (
                <>
                  <p className="lede">
                    If <strong>{email}</strong> has an account, a code is on its way. Enter it with
                    your new password.
                  </p>
                  <DemoInbox email={email} refresh={step} />
                  <CodeInput value={code} onChange={setCode} />
                </>
              )}
              {token && <p className="lede">Choose a new password.</p>}
              <label className="field">
                <span className="field-label">New password</span>
                <input
                  className="field-input"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="new-password"
                  minLength={8}
                  required
                />
                <span className="field-help">At least 8 characters, mixing letters with numbers or symbols.</span>
              </label>
              {error && <ErrorMessage error={error} />}
              <button
                className="primary-button"
                type="submit"
                disabled={busy || (!token && code.length !== 6)}
              >
                {busy ? "Saving..." : "Save password and sign in"}
              </button>
              {!token && (
                <button className="text-button" onClick={() => setStep("email")} type="button">
                  Use a different email
                </button>
              )}
            </form>
          )}

          <p className="form-links">
            <Link to="/sign-in">Back to sign in</Link>
          </p>
        </section>
      </div>
    </main>
  );
}

export default ResetPasswordPage;
