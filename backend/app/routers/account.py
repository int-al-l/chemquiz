"""Accounts, the saved-items list and learning progress.

Accounts are email + password. A new account must verify its email before it
can sign in: registration mails a six-digit code and a link, and either one
completes it (see `models.EmailCode`). The same machinery resets a forgotten
password -- which is also how accounts from before passwords existed get one.

Every /me endpoint takes the session token in an `Authorization: Bearer`
header.
"""

import datetime as dt
import json
import re

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .. import config, crud, mailer, models, progress, schemas, security
from ..database import get_db

router = APIRouter(prefix="/api", tags=["account"])

# Deliberately permissive: this is a typo check; the emailed code is the real check.
EMAIL = re.compile(r"^[^@\s]+@[^@\s.]+(\.[^@\s.]+)+$")


def normalise_email(value: str) -> str:
    return value.strip().lower()


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _aware(value: dt.datetime) -> dt.datetime:
    # SQLite hands datetimes back naive; they were stored as UTC.
    return value if value.tzinfo else value.replace(tzinfo=dt.timezone.utc)


def current_user(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
) -> models.User:
    """Resolve the bearer token, or refuse."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Sign in to use your list.")

    token = authorization.split(" ", 1)[1].strip()
    user = db.execute(
        select(models.User)
        .where(models.User.token == token)
        .options(selectinload(models.User.saved))
    ).scalar_one_or_none()

    if user is None or not user.email_verified:
        raise HTTPException(status_code=401, detail="That sign-in has expired.")

    user.last_seen_at = models.utcnow()
    db.commit()
    return user


def _signed_in(user: models.User) -> dict:
    return {"token": user.token, "email": user.email, "name": user.name,
            "saved_count": len(user.saved)}


def _check_email(value: str) -> str:
    email = normalise_email(value)
    if not EMAIL.match(email):
        raise HTTPException(status_code=422, detail="That does not look like an email address.")
    return email


def _check_password(password: str) -> None:
    if len(password) < config.PASSWORD_MIN_LENGTH:
        raise HTTPException(
            status_code=422,
            detail=f"Use at least {config.PASSWORD_MIN_LENGTH} characters for the password.",
        )
    if password.isdigit() or password.isalpha():
        raise HTTPException(
            status_code=422, detail="Mix letters with numbers or symbols in the password."
        )


def _find_user(db: Session, email: str) -> models.User | None:
    return db.execute(
        select(models.User).where(models.User.email == email)
    ).scalar_one_or_none()


def _send_code(db: Session, user: models.User, purpose: str) -> None:
    """Mail a fresh code + link, replacing any earlier unused one.

    Rate limited per user and purpose: a second request inside the cooldown is
    accepted silently without sending, so the earlier email stays valid.
    """
    latest = db.execute(
        select(models.EmailCode)
        .where(models.EmailCode.user_id == user.id, models.EmailCode.purpose == purpose)
        .order_by(models.EmailCode.created_at.desc())
    ).scalars().first()
    if latest is not None and latest.used_at is None:
        age = (_now() - _aware(latest.created_at)).total_seconds()
        if age < config.CODE_RESEND_SECONDS:
            return

    # Only the newest code for a purpose is valid.
    for old in db.execute(
        select(models.EmailCode).where(
            models.EmailCode.user_id == user.id,
            models.EmailCode.purpose == purpose,
            models.EmailCode.used_at.is_(None),
        )
    ).scalars():
        old.used_at = _now()

    code = security.new_code()
    link_token = security.new_link_token()
    db.add(models.EmailCode(
        user_id=user.id,
        purpose=purpose,
        code_hash=security.digest(f"{user.id}:{code}"),
        link_hash=security.digest(link_token),
        expires_at=_now() + dt.timedelta(minutes=config.CODE_TTL_MINUTES),
    ))
    db.commit()

    path = "verify-email" if purpose == "verify" else "reset-password"
    link = f"{config.PUBLIC_URL}/{path}?token={link_token}"
    subject, text, html = mailer.code_email(purpose, user.name, code, link)
    try:
        mailer.send(user.email, subject, text, html)
    except Exception as exc:  # noqa: BLE001
        print(f"Could not send email to {user.email}: {exc}", flush=True)
        raise HTTPException(
            status_code=503, detail="Could not send the email right now. Try again in a minute."
        ) from exc


def _redeem(db: Session, payload: schemas.VerifyIn, purpose: str) -> models.User:
    """Check a code (with its email) or a link token; mark it used."""
    bad = HTTPException(status_code=400, detail="That code is wrong or has expired.")

    if payload.token:
        row = db.execute(
            select(models.EmailCode).where(
                models.EmailCode.link_hash == security.digest(payload.token.strip()),
                models.EmailCode.purpose == purpose,
            )
        ).scalar_one_or_none()
        if row is None or row.used_at is not None or _aware(row.expires_at) < _now():
            raise HTTPException(status_code=400, detail="That link is no longer valid. Ask for a new one.")
    else:
        if not payload.email or not payload.code:
            raise HTTPException(status_code=422, detail="Enter the code from the email.")
        user = _find_user(db, normalise_email(payload.email))
        if user is None:
            raise bad
        row = db.execute(
            select(models.EmailCode)
            .where(
                models.EmailCode.user_id == user.id,
                models.EmailCode.purpose == purpose,
                models.EmailCode.used_at.is_(None),
            )
            .order_by(models.EmailCode.created_at.desc())
        ).scalars().first()
        if row is None or _aware(row.expires_at) < _now():
            raise bad
        if row.attempts >= config.CODE_MAX_ATTEMPTS:
            raise HTTPException(
                status_code=429, detail="Too many wrong codes. Ask for a new email."
            )
        code = re.sub(r"\D", "", payload.code)
        if security.digest(f"{user.id}:{code}") != row.code_hash:
            row.attempts += 1
            db.commit()
            raise bad

    row.used_at = _now()
    user = db.get(models.User, row.user_id)
    user.email_verified = True
    db.commit()
    return user


# --- auth -------------------------------------------------------------------


@router.post("/auth/register", response_model=schemas.PendingOut, status_code=202)
def register(payload: schemas.RegisterIn, db: Session = Depends(get_db)):
    """Create an account and mail a verification code.

    An address that registered but never verified can register again -- the
    name and password are replaced and a new code is sent -- so a typo in the
    first attempt's password is not a dead end.
    """
    email = _check_email(payload.email)
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Please enter a name.")
    _check_password(payload.password)

    user = _find_user(db, email)
    if user is not None and user.email_verified and user.password_hash:
        raise HTTPException(
            status_code=409,
            detail="There is already an account with this email. Sign in instead.",
        )
    if user is not None and user.email_verified and not user.password_hash:
        # An account from before passwords: it must prove the address again.
        raise HTTPException(
            status_code=409,
            detail="This email already has an account. Use \u201cForgot password\u201d to set a password.",
        )

    if user is None:
        user = models.User(email=email, name=name, token=security.new_session_token())
        db.add(user)
    user.name = name
    user.password_hash = security.hash_password(payload.password)
    user.email_verified = False
    db.commit()
    db.refresh(user)

    _send_code(db, user, "verify")
    return {"email": email, "purpose": "verify"}


@router.post("/auth/verify", response_model=schemas.SignedInUser)
def verify(payload: schemas.VerifyIn, db: Session = Depends(get_db)):
    user = _redeem(db, payload, "verify")
    db.refresh(user)
    return _signed_in(user)


@router.post("/auth/resend", response_model=schemas.PendingOut, status_code=202)
def resend(payload: schemas.EmailIn, db: Session = Depends(get_db)):
    email = _check_email(payload.email)
    user = _find_user(db, email)
    if user is not None and not user.email_verified:
        _send_code(db, user, "verify")
    return {"email": email, "purpose": "verify"}


@router.post("/auth/login", response_model=schemas.SignedInUser)
def login(payload: schemas.LoginIn, db: Session = Depends(get_db)):
    email = _check_email(payload.email)
    user = _find_user(db, email)

    if user is not None and user.password_hash is None:
        raise HTTPException(
            status_code=409,
            detail="This account was made before passwords existed. "
            "Use \u201cForgot password\u201d to set one.",
        )
    if user is None or not security.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Wrong email or password.")

    if not user.email_verified:
        _send_code(db, user, "verify")
        raise HTTPException(
            status_code=403,
            detail="Please verify your email first. We have sent you a new code.",
        )

    user.last_seen_at = models.utcnow()
    db.commit()
    db.refresh(user)
    return _signed_in(user)


@router.post("/auth/forgot", response_model=schemas.PendingOut, status_code=202)
def forgot(payload: schemas.EmailIn, db: Session = Depends(get_db)):
    """Mail a reset code. Answers the same whether or not the account exists,
    so this cannot be used to find out who has an account."""
    email = _check_email(payload.email)
    user = _find_user(db, email)
    if user is not None:
        _send_code(db, user, "reset")
    return {"email": email, "purpose": "reset"}


@router.post("/auth/reset", response_model=schemas.SignedInUser)
def reset(payload: schemas.ResetIn, db: Session = Depends(get_db)):
    _check_password(payload.password)
    user = _redeem(db, payload, "reset")
    user.password_hash = security.hash_password(payload.password)
    # A new password signs every other device out.
    user.token = security.new_session_token()
    db.commit()
    db.refresh(user)
    return _signed_in(user)


@router.get("/auth/me", response_model=schemas.SignedInUser)
def me(user: models.User = Depends(current_user)):
    return _signed_in(user)


# --- progress ---------------------------------------------------------------


def _progress_row(db: Session, user: models.User) -> models.UserProgress:
    row = db.get(models.UserProgress, user.id)
    if row is None:
        row = models.UserProgress(user_id=user.id, data="{}")
        db.add(row)
        db.flush()
    return row


@router.get("/me/progress", response_model=schemas.ProgressOut)
def get_progress(user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    row = db.get(models.UserProgress, user.id)
    data = json.loads(row.data) if row else {}
    return {"data": progress.normalise(data)}


@router.put("/me/progress", response_model=schemas.ProgressOut)
def put_progress(payload: schemas.ProgressIn,
                 user: models.User = Depends(current_user),
                 db: Session = Depends(get_db)):
    """Merge the browser's copy into the stored one and return the result."""
    body = json.dumps(payload.data)
    if len(body) > 1_000_000:
        raise HTTPException(status_code=413, detail="Progress document too large.")
    row = _progress_row(db, user)
    merged = progress.merge(json.loads(row.data or "{}"), payload.data)
    row.data = json.dumps(merged)
    row.updated_at = models.utcnow()
    db.commit()
    return {"data": merged}


# --- saved list -------------------------------------------------------------


@router.get("/me/list", response_model=list[schemas.ItemOut])
def my_list(user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.execute(
        select(models.SavedItem)
        .where(models.SavedItem.user_id == user.id)
        .options(
            selectinload(models.SavedItem.item).selectinload(models.Item.photos)
        )
        .order_by(models.SavedItem.created_at.desc())
    ).scalars().all()
    return [crud.item_payload(row.item) for row in rows]


@router.put("/me/list/{slug}", response_model=schemas.SavedOut, status_code=201)
def save_item(slug: str, user: models.User = Depends(current_user),
              db: Session = Depends(get_db)):
    item = db.execute(
        select(models.Item).where(models.Item.slug == slug)
    ).scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail=f"No item '{slug}'")

    existing = db.execute(
        select(models.SavedItem).where(
            models.SavedItem.user_id == user.id,
            models.SavedItem.item_id == item.id,
        )
    ).scalar_one_or_none()

    # Saving twice is not an error; the request describes a desired state.
    if existing is None:
        db.add(models.SavedItem(user_id=user.id, item_id=item.id))
        db.commit()

    return {"slug": slug, "saved": True}


@router.delete("/me/list/{slug}", response_model=schemas.SavedOut)
def unsave_item(slug: str, user: models.User = Depends(current_user),
                db: Session = Depends(get_db)):
    item = db.execute(
        select(models.Item).where(models.Item.slug == slug)
    ).scalar_one_or_none()
    if item is not None:
        db.execute(
            models.SavedItem.__table__.delete().where(
                (models.SavedItem.user_id == user.id)
                & (models.SavedItem.item_id == item.id)
            )
        )
        db.commit()
    return {"slug": slug, "saved": False}


@router.post("/me/list/import", response_model=list[schemas.ItemOut])
def import_list(payload: schemas.ImportListIn,
                user: models.User = Depends(current_user),
                db: Session = Depends(get_db)):
    """Adopt a list that was saved in the browser before signing in.

    Adds rather than replaces, so signing in on a second device cannot wipe
    what is already on the account. Unknown slugs are skipped quietly -- they
    are old bookmarks, not an error the person can act on.
    """
    items = db.execute(
        select(models.Item).where(models.Item.slug.in_(payload.slugs))
    ).scalars().all()

    owned = {
        row.item_id
        for row in db.execute(
            select(models.SavedItem).where(models.SavedItem.user_id == user.id)
        ).scalars()
    }

    for item in items:
        if item.id not in owned:
            db.add(models.SavedItem(user_id=user.id, item_id=item.id))
    db.commit()

    return my_list(user=user, db=db)
