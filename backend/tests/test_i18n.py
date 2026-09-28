"""Server-side language: the request's language, localised errors."""

from __future__ import annotations

import pytest

from app import messages
from app.i18n import normalize_lang
from test_api import client  # noqa: F401 -- the seeded test app


@pytest.mark.parametrize(
    "header, lang",
    [
        (None, "en"),
        ("", "en"),
        ("ru", "ru"),
        ("RU-ru", "ru"),
        ("ru-RU,ru;q=0.9,en;q=0.8", "ru"),
        ("en-US,ru;q=0.5", "en"),
        ("de-DE", "en"),
    ],
)
def test_the_first_language_in_the_header_decides(header, lang):
    assert normalize_lang(header) == lang


def test_every_message_has_both_languages():
    for key, texts in messages.MESSAGES.items():
        assert set(texts) == {"en", "ru"}, key
        assert texts["en"].strip() and texts["ru"].strip(), key


def test_errors_come_in_the_request_language_with_a_code(client):
    res = client.get("/api/categories/nope")
    assert res.status_code == 404
    assert res.json() == {"detail": "No category 'nope'", "code": "no_category"}

    res = client.get("/api/categories/nope", headers={"Accept-Language": "ru"})
    assert res.status_code == 404
    assert res.json() == {"detail": "Колоды «nope» нет", "code": "no_category"}


def test_sign_in_errors_are_localised(client):
    res = client.get("/api/me/list", headers={"Accept-Language": "ru"})
    assert res.status_code == 401
    assert res.json()["code"] == "sign_in_required"
    assert res.json()["detail"] == "Войдите, чтобы пользоваться списком."
