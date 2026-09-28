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


from sqlalchemy import select  # noqa: E402

from app import models  # noqa: E402
from test_api import db_session  # noqa: E402,F401

RU = {"Accept-Language": "ru"}


def russian(db_session):
    """Give two condensers and their deck Russian texts; leave the rest English."""
    deck = db_session.scalars(select(models.Category).where(models.Category.slug == "condensers")).one()
    deck.name_ru = "Холодильники"
    deck.description_ru = "Охлаждают пар"
    for slug, name in (("condenser-0", "Холодильник 0"), ("condenser-1", "Альфа-холодильник")):
        item = db_session.scalars(select(models.Item).where(models.Item.slug == slug)).one()
        item.name_ru = name
        item.description_ru = f"Описание: {name}"
    db_session.commit()


def test_cards_and_decks_in_russian_with_english_fallback(client, db_session):
    russian(db_session)
    deck = client.get("/api/categories/condensers", headers=RU).json()
    assert deck["name"] == "Холодильники"
    names = [i["name"] for i in deck["items"]]
    assert "Холодильник 0" in names
    assert "Condenser 2" in names  # no Russian text: English, not blank
    assert client.get("/api/categories/condensers").json()["name"] == "Condensers"


def test_lists_sort_by_the_shown_name(client, db_session):
    russian(db_session)
    names = [i["name"] for i in client.get("/api/items?category=condensers", headers=RU).json()]
    assert names.index("Альфа-холодильник") < names.index("Холодильник 0")


def test_a_quiz_speaks_the_request_language(client, db_session):
    russian(db_session)
    quiz = client.post("/api/quiz/start", json={"category_slug": "condensers", "mode": "choice",
                                                "question_count": 5}, headers=RU).json()
    assert quiz["category_name"] == "Холодильники"
    shown = {c["name"] for q in quiz["questions"] for c in q["choices"]}
    assert "Холодильник 0" in shown
    # the same quiz read in English
    again = client.get(f"/api/quiz/{quiz['token']}").json()
    assert again["category_name"] == "Condensers"


from app import mailer  # noqa: E402


def test_the_email_follows_the_request_language(client):
    res = client.post("/api/auth/register", headers=RU,
                      json={"name": "Аня", "email": "anya@example.com", "password": "flask-2024"})
    assert res.status_code == 202
    mail = next(m for m in reversed(mailer.OUTBOX) if m["to"] == "anya@example.com")
    assert "ChemQuiz" in mail["subject"] and "код" in mail["subject"]
    assert "Ваш код: " in mail["text"]

    client.post("/api/auth/register",
                json={"name": "Ann", "email": "ann@example.com", "password": "flask-2024"})
    mail = next(m for m in reversed(mailer.OUTBOX) if m["to"] == "ann@example.com")
    assert mail["text"].startswith("Hi Ann,\n\n")
    assert "Your code: " in mail["text"]
    assert "The code and the link expire in " in mail["text"]
