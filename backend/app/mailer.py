"""Sending email.

Configured through the CHEMQUIZ_SMTP_* variables in config.py. Works with any
SMTP provider -- Gmail (an app password, port 587), Yandex, Mail.ru, Resend,
SendGrid, Mailgun all offer one. With no host configured, messages are printed
to the console, and every message is also appended to OUTBOX so tests can read
the codes.
"""

from __future__ import annotations

import smtplib
import ssl
from email.message import EmailMessage

from . import config

OUTBOX: list[dict] = []


def send(to: str, subject: str, text: str, html: str | None = None) -> None:
    OUTBOX.append({"to": to, "subject": subject, "text": text})
    del OUTBOX[:-50]

    if not config.SMTP_HOST:
        print(f"\n--- email to {to} (SMTP not configured, printed instead) ---")
        print(f"Subject: {subject}\n\n{text}\n--- end of email ---\n", flush=True)
        return

    msg = EmailMessage()
    msg["From"] = config.MAIL_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(text)
    if html:
        msg.add_alternative(html, subtype="html")

    context = ssl.create_default_context()
    if config.SMTP_SECURITY == "ssl":
        server = smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT, context=context, timeout=20)
    else:
        server = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=20)
    with server:
        if config.SMTP_SECURITY == "starttls":
            server.starttls(context=context)
        if config.SMTP_USER:
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.send_message(msg)


def code_email(purpose: str, name: str, code: str, link: str) -> tuple[str, str, str]:
    """Subject, plain text and HTML for a verification or reset email."""
    if purpose == "verify":
        subject = f"{code} is your ChemQuiz verification code"
        intro = "Welcome to ChemQuiz! Confirm your email address to finish creating your account."
        action = "Verify my email"
    else:
        subject = f"{code} is your ChemQuiz password reset code"
        intro = "Someone (hopefully you) asked to reset your ChemQuiz password."
        action = "Choose a new password"

    minutes = config.CODE_TTL_MINUTES
    text = (
        f"Hi {name},\n\n{intro}\n\n"
        f"Your code: {code}\n\n"
        f"Or open this link:\n{link}\n\n"
        f"The code and the link expire in {minutes} minutes. "
        "If you did not ask for this, ignore this email.\n"
    )
    html = f"""\
<div style="font-family:Roboto,Arial,sans-serif;max-width:480px;margin:auto;color:#1D1B20">
  <h2 style="color:#6750A4;font-weight:500">ChemQuiz</h2>
  <p>Hi {name},</p>
  <p>{intro}</p>
  <p style="font-size:34px;letter-spacing:8px;font-weight:700;margin:24px 0">{code}</p>
  <p><a href="{link}" style="display:inline-block;background:#6750A4;color:#fff;
     padding:12px 22px;border-radius:20px;text-decoration:none">{action}</a></p>
  <p style="color:#49454F;font-size:13px">The code and the link expire in {minutes} minutes.
  If you did not ask for this, ignore this email.</p>
</div>"""
    return subject, text, html
