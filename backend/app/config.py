"""Application settings.

Everything is overridable through environment variables so the same code runs
locally against SQLite and later against Postgres without edits.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- database -------------------------------------------------------------

# SQLite lives in backend/chemquiz.db by default. Swapping to Postgres is a
# matter of setting CHEMQUIZ_DATABASE_URL, nothing else changes.
DATABASE_URL = os.getenv(
    "CHEMQUIZ_DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'chemquiz.db'}",
)

# --- static images --------------------------------------------------------

STATIC_DIR = Path(os.getenv("CHEMQUIZ_STATIC_DIR", BASE_DIR / "static"))
IMAGES_DIR = STATIC_DIR / "images"
IMAGES_URL_PREFIX = "/static/images"
# Pictures teachers upload for their own quizzes (served from STATIC_DIR too).
UPLOADS_DIR = STATIC_DIR / "uploads"
UPLOADS_URL_PREFIX = "/static/uploads"

# --- the built site --------------------------------------------------------

# Where `npm run build` put the site (dist/). When set, the backend serves it
# too, so the whole thing runs on one port without Vite -- on a laptop in the
# classroom, or behind a tunnel. Unset in development, where Vite serves it.
FRONTEND_DIR = Path(os.environ["CHEMQUIZ_FRONTEND_DIR"]) if os.getenv("CHEMQUIZ_FRONTEND_DIR") else None

# --- cors -----------------------------------------------------------------

# Vite dev server origins.
CORS_ORIGINS = os.getenv(
    "CHEMQUIZ_CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")

# --- quiz tuning ----------------------------------------------------------

DEFAULT_QUESTION_COUNT = 10
MAX_QUESTION_COUNT = 50
CHOICES_PER_QUESTION = 4

# A quiz session is disposable state; drop stale ones so the table cannot grow
# without bound now that there are no user accounts to own them.
SESSION_TTL_HOURS = 24

# --- quiz modes -------------------------------------------------------------

QUIZ_MODES = ("choice", "inverted")

# --- accounts and email -----------------------------------------------------

# Where links in emails point: the address of the *frontend*.
PUBLIC_URL = os.getenv("CHEMQUIZ_PUBLIC_URL", "http://localhost:5173").rstrip("/")

# Outgoing mail. With no SMTP host set, emails are printed to the server
# console instead of sent -- enough to develop and test the flows locally.
SMTP_HOST = os.getenv("CHEMQUIZ_SMTP_HOST", "")
SMTP_PORT = int(os.getenv("CHEMQUIZ_SMTP_PORT", "587"))
SMTP_USER = os.getenv("CHEMQUIZ_SMTP_USER", "")
SMTP_PASSWORD = os.getenv("CHEMQUIZ_SMTP_PASSWORD", "")
# "starttls" (port 587), "ssl" (port 465) or "none".
SMTP_SECURITY = os.getenv("CHEMQUIZ_SMTP_SECURITY", "starttls").lower()
MAIL_FROM = os.getenv("CHEMQUIZ_MAIL_FROM", SMTP_USER or "ChemQuiz <no-reply@localhost>")

CODE_TTL_MINUTES = 15
CODE_MAX_ATTEMPTS = 5
# Minimum gap between two emails of the same kind to the same user.
CODE_RESEND_SECONDS = 60
PASSWORD_MIN_LENGTH = 8
