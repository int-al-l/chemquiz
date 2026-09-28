"""Password hashing and one-time codes, standard library only.

Passwords are hashed with scrypt, a memory-hard KDF, and stored as
``scrypt$n$r$p$salt$hash`` so the cost can be raised later without breaking
existing hashes.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

_N, _R, _P = 2**14, 8, 1


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=_N, r=_R, p=_P, dklen=32)
    b64 = lambda b: base64.b64encode(b).decode()  # noqa: E731
    return f"scrypt${_N}${_R}${_P}${b64(salt)}${b64(digest)}"


def verify_password(password: str, stored: str | None) -> bool:
    if not stored:
        return False
    try:
        scheme, n, r, p, salt, digest = stored.split("$")
        if scheme != "scrypt":
            return False
        expected = base64.b64decode(digest)
        actual = hashlib.scrypt(
            password.encode(),
            salt=base64.b64decode(salt),
            n=int(n), r=int(r), p=int(p),
            dklen=len(expected),
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(actual, expected)


def new_code() -> str:
    """Six digits, uniformly random, leading zeros kept."""
    return f"{secrets.randbelow(1_000_000):06d}"


def new_link_token() -> str:
    return secrets.token_urlsafe(32)


def new_session_token() -> str:
    return secrets.token_urlsafe(32)[:43]


def digest(value: str) -> str:
    """Hash for storing codes and link tokens (they are short-lived and random)."""
    return hashlib.sha256(value.encode()).hexdigest()
