"""The language of a request, and errors that know how to say themselves.

A request is in Russian when its Accept-Language header starts with `ru`;
a live game overrides that with its own `lang`. Everything else is English.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import Request
from fastapi.responses import JSONResponse

from . import messages

LANGS = ("en", "ru")


def normalize_lang(value: Optional[str]) -> str:
    """"ru-RU,ru;q=0.9" -> "ru"; anything not Russian first -> "en"."""
    first = (value or "").split(",")[0].strip().lower()
    return "ru" if first.startswith("ru") else "en"


def request_lang(request: Request) -> str:
    """FastAPI dependency: the language the client asked for."""
    return normalize_lang(request.headers.get("accept-language"))


def localized(obj: Any, field: str, lang: str) -> Optional[str]:
    """`obj.<field>_ru` in Russian when it is set, otherwise `obj.<field>`."""
    if lang == "ru":
        value = getattr(obj, f"{field}_ru", None)
        if value:
            return value
    return getattr(obj, field)


class AppError(Exception):
    """A request the site refuses, with a message key rather than a text.

    `lang` may be set before raising (a live game's language); otherwise the
    exception handler uses the request's language.
    """

    def __init__(self, key: str, status: int = 409, **values):
        super().__init__(messages.text(key, "en", **values))
        self.key = key
        self.status = status
        self.values = values
        self.lang: Optional[str] = None

    def response(self, lang: str) -> JSONResponse:
        return JSONResponse(
            status_code=self.status,
            content={"detail": messages.text(self.key, lang, **self.values), "code": self.key},
        )
