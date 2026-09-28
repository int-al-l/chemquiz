import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import CodeInput from "../components/CodeInput";
import DemoInbox from "../components/DemoInbox";
import PageHeader from "../components/PageHeader";
import { ErrorMessage, Loading } from "../components/StatusMessage";
import { resendVerification, verifyEmail } from "../api/client";
import { useAuth } from "../auth/context";

/**
 * Confirm an email address: type the code, or arrive here from the link in
 * the email (?token=...), which confirms on its own.
 */
function VerifyEmailPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const { completeSignIn } = useAuth();

  const email = params.get("email") ?? "";
  const token = params.get("token");

  const [code, setCode] = useState("");
  const [busy, setBusy] = useState(Boolean(token));
  const [error, setError] = useState(null);
  const [cooldown, setCooldown] = useState(60);
  const [resent, setResent] = useState(false);
  const tried = useRef(false);

  useEffect(() => {
    if (cooldown <= 0) return undefined;
    const t = window.setTimeout(() => setCooldown((c) => c - 1), 1000);
    return () => window.clearTimeout(t);
  }, [cooldown]);

  // The link from the email: confirm straight away (once, even in StrictMode).
  useEffect(() => {
    if (!token || tried.current) return;
    tried.current = true;
    verifyEmail({ token })
      .then(completeSignIn)
      .then(() => navigate("/", { replace: true }))
      .catch((err) => {
        setError(err);
        setBusy(false);
      });
  }, [token, completeSignIn, navigate]);

  async function submit(event) {
    event?.preventDefault();
    if (code.length !== 6) return;
    setBusy(true);
    setError(null);
    try {
      const fresh = await verifyEmail({ email, code });
      await completeSignIn(fresh);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err);
      setBusy(false);
    }
  }

  async function resend() {
    setError(null);
    try {
      await resendVerification(email);
      setResent(true);
      setCooldown(60);
    } catch (err) {
      setError(err);
    }
  }

  return (
    <main className="categories-page">
      <div className="page-layout">
        <PageHeader title="Check your email" backTo="/sign-in" />

        <section className="categories-content narrow">
          {token && busy ? (
            <Loading label="Confirming your email..." />
          ) : (
            <>
              <div className="mail-illustration" aria-hidden="true">
                <span className="material-symbols-outlined">mark_email_unread</span>
              </div>
              {email ? (
                <p className="lede">
                  We sent a six-digit code to <strong>{email}</strong>. Type it below, or open the
                  link in the email.
                </p>
              ) : (
                <p className="lede">Open the link in the email, or sign in again to get a new code.</p>
              )}

              <DemoInbox email={email} refresh={cooldown === 60} />

              {email && (
                <form className="sign-in-form" onSubmit={submit}>
                  <CodeInput
                    value={code}
                    onChange={(v) => {
                      setCode(v);
                      setError(null);
                    }}
                  />
                  {error && <ErrorMessage error={error} />}
                  <button className="primary-button" type="submit" disabled={busy || code.length !== 6}>
                    {busy ? "Checking..." : "Confirm email"}
                  </button>
                </form>
              )}
              {!email && error && <ErrorMessage error={error} />}

              <p className="form-links">
                {email &&
                  (cooldown > 0 ? (
                    <span className="muted">
                      {resent ? "Sent again. " : ""}Resend in {cooldown}s
                    </span>
                  ) : (
                    <button className="text-button" onClick={resend} type="button">
                      Send a new code
                    </button>
                  ))}
                <Link to="/sign-in" state={{ tab: "register", email }}>
                  Wrong address?
                </Link>
              </p>
              <p className="fine-print">Can not find it? Look in the spam folder.</p>
            </>
          )}
        </section>
      </div>
    </main>
  );
}

export default VerifyEmailPage;
