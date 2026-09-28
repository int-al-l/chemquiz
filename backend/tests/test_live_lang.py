"""A class game speaks the teacher's language on every screen."""

from sqlalchemy import select

from app import live, models
from test_api import client, db_session  # noqa: F401
from test_i18n import russian
from test_live import clock, correct_id, host, join, make_room, teacher  # noqa: F401


def test_a_russian_game_is_russian_on_every_phone(client, db_session, clock):
    russian(db_session)
    room = make_room(client, lang="ru", question_count=5)
    assert room["lang"] == "ru"
    assert client.get(f"/api/live/{room['pin']}").json()["lang"] == "ru"
    ann = join(client, room["pin"], "Ann")
    assert ann["lang"] == "ru"
    view = client.post(f"/api/live/{room['pin']}/next", headers=host(room["host_token"])).json()
    with client.session_factory() as db:
        game = db.scalars(select(models.LiveGame).where(models.LiveGame.pin == room["pin"])).one()
        names = {c["name"] for q in game.questions for c in q["choices"]}
    assert "Холодильник 0" in names
    assert view["category_name"] == "Холодильники"

    # The phone asks in English; the game answers in Russian.
    res = client.post(f"/api/live/{room['pin']}/answer", json={"position": 1, "choice_id": -1},
                      headers={**host(ann["token"]), "Accept-Language": "en"})
    assert res.json()["code"] == "not_open_yet"
    assert res.json()["detail"] == "Отвечать пока нельзя"


def test_english_is_the_default(client, clock):
    room = make_room(client)
    assert room["lang"] == "en"


def test_an_unknown_language_is_refused(client, clock):
    res = client.post("/api/live", json={"category_slug": "condensers", "lang": "de"})
    assert res.status_code == 422


def test_playing_again_keeps_the_language(client, db_session, clock):
    t = teacher(client)
    room = make_room(client, headers=t, lang="ru", question_count=1)
    pin, token = room["pin"], room["host_token"]
    ann = join(client, pin, "Ann")
    client.post(f"/api/live/{pin}/next", headers=host(token))
    clock.advance(live.READ_SECONDS + 1)
    client.post(f"/api/live/{pin}/answer", json={"position": 1, "choice_id": correct_id(client, pin, 1)},
                headers=host(ann["token"]))
    [game] = client.get("/api/me/live-games", headers=t).json()
    again = client.post(f"/api/me/live-games/{game['id']}/replay", json={"kind": "same"}, headers=t).json()
    assert again["lang"] == "ru"
