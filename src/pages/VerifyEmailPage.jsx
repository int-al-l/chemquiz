import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import CodeInput from "../components/CodeInput";
import DemoInbox from "../components/DemoInbox";
import PageHeader from "../components/PageHeader";
import { ErrorMessage, Loading } from "../components/StatusMessage";
import { resendVerification, verifyEmail } from "../api/client";
import { useAuth } from "../auth/context";
import { rich, useT } from "../i18n";

/**
 * Confirm an email address: type the code, or arrive here from the link in
 * the email (?token=...), which confirms on its own.
 */
function VerifyEmailPage() {
  const t = useT();
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
    const timer = window.setTimeout(() => setCooldown((c) => c - 1), 1000);
    return () => window.clearTimeout(timer);
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
        <PageHeader title={t("verify.title")} backTo="/sign-in" />

        <section className="categories-content narrow">
          {token && busy ? (
            <Loading label={t("verify.confirming")} />
          ) : (
            <>
              <div className="mail-illustration" aria-hidden="true">
                <span className="material-symbols-outlined">mark_email_unread</span>
              </div>
              {email ? (
                <p className="lede">
                  {rich(t("verify.sent"), { email: <strong>{email}</strong> })}
                </p>
              ) : (
                <p className="lede">{t("verify.noEmail")}</p>
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
                    {busy ? t("verify.checking") : t("verify.confirm")}
                  </button>
                </form>
              )}
              {!email && error && <ErrorMessage error={error} />}

              <p className="form-links">
                {email &&
                  (cooldown > 0 ? (
                    <span className="muted">
                      {t(resent ? "verify.resentResendIn" : "verify.resendIn", { n: cooldown })}
                    </span>
                  ) : (
                    <button className="text-button" onClick={resend} type="button">
                      {t("verify.resend")}
                    </button>
                  ))}
                <Link to="/sign-in" state={{ tab: "register", email }}>
                  {t("verify.wrongAddress")}
                </Link>
              </p>
              <p className="fine-print">{t("verify.spam")}</p>
            </>
          )}
        </section>
      </div>
    </main>
  );
}

export default VerifyEmailPage;
