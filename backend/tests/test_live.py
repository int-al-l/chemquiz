"""Live classroom game: rooms, joining, the clock, scoring and secrecy."""

from __future__ import annotations

import random

import pytest
from sqlalchemy import func, select

from app import live, models
from test_api import auth, client, sign_in  # noqa: F401 -- the seeded test app


class Clock:
    def __init__(self):
        self.t = 1_000_000.0

    def __call__(self):
        return self.t

    def advance(self, seconds):
        self.t += seconds


@pytest.fixture()
def clock(monkeypatch):
    c = Clock()
    monkeypatch.setattr(live, "_now", c)
    yield c


def host(token):
    return {"X-Live-Token": token}


def make_room(client, headers=None, **kw):
    body = {"category_slug": "condensers", "mode": "choice", "question_count": 3, "time_limit": 20}
    body.update(kw)
    res = client.post("/api/live", json=body, headers=headers or {})
    assert res.status_code == 201, res.text
    return res.json()


def join(client, pin, name):
    res = client.post(f"/api/live/{pin}/join", json={"name": name})
    assert res.status_code == 201, res.text
    return res.json()


def correct_id(client, pin, position):
    with client.session_factory() as db:
        game = db.scalars(select(models.LiveGame).where(models.LiveGame.pin == pin)).one()
        return game.questions[position - 1]["correct_id"]


class SamePins(random.Random):
    """Hands out the given PINs in order; everything else stays random."""

    def __init__(self, pins):
        super().__init__()
        self.pins = list(pins)

    def randint(self, a, b):
        return int(self.pins.pop(0))


def test_create_and_join(client, clock):
    room = make_room(client)
    assert len(room["pin"]) == 6 and room["phase"] == "lobby"
    assert room["question_count"] == 3

    peek = client.get(f"/api/live/{room['pin']}").json()
    assert peek["joinable"] and peek["player_count"] == 0

    ann = join(client, room["pin"], "  Ann  ")
    assert ann["you"]["name"] == "Ann" and ann["token"]

    # Names are unique, ignoring case.
    res = client.post(f"/api/live/{room['pin']}/join", json={"name": "ann"})
    assert res.status_code == 409
    res = client.post(f"/api/live/{room['pin']}/join", json={"name": "   "})
    assert res.status_code == 422
    res = client.post(f"/api/live/{room['pin']}/join", json={"name": "x" * 21})
    assert res.status_code == 422

    view = client.get(f"/api/live/{room['pin']}/host", headers=host(room["host_token"])).json()
    assert [p["name"] for p in view["players"]] == ["Ann"]

    assert client.get("/api/live/000000").status_code == 404


def test_host_actions_need_the_host_token(client, clock):
    room = make_room(client)
    ann = join(client, room["pin"], "Ann")
    pin = room["pin"]
    assert client.get(f"/api/live/{pin}/host").status_code == 403
    assert client.post(f"/api/live/{pin}/next", headers=host(ann["token"])).status_code == 403
    assert client.delete(f"/api/live/{pin}", headers=host("nope")).status_code == 403


def test_cannot_start_empty(client, clock):
    room = make_room(client)
    res = client.post(f"/api/live/{room['pin']}/next", headers=host(room["host_token"]))
    assert res.status_code == 409


def test_full_game(client, clock):
    room = make_room(client)
    pin, token = room["pin"], room["host_token"]
    ann = join(client, pin, "Ann")
    bob = join(client, pin, "Bob")

    view = client.post(f"/api/live/{pin}/next", headers=host(token)).json()
    assert view["phase"] == "question" and view["position"] == 1
    assert view["starts_at"] - view["now"] == live.READ_SECONDS
    # The answer is not in what either side sees yet.
    assert view["reveal"] is None and "correct_id" not in view["question"]
    me = client.get(f"/api/live/{pin}/me", headers=host(ann["token"])).json()
    assert me["question"]["choices"] and me["reveal"] is None

    right = correct_id(client, pin, 1)
    wrong = next(c["id"] for c in me["question"]["choices"] if c["id"] != right)

    # Too early: still reading time.
    res = client.post(f"/api/live/{pin}/answer", json={"position": 1, "choice_id": right},
                      headers=host(ann["token"]))
    assert res.status_code == 409

    clock.advance(live.READ_SECONDS)  # answers open, full marks
    res = client.post(f"/api/live/{pin}/answer", json={"position": 1, "choice_id": right},
                      headers=host(ann["token"]))
    assert res.status_code == 200
    assert res.json()["phase"] == "question"  # Bob has not answered

    # Answering twice is refused.
    res = client.post(f"/api/live/{pin}/answer", json={"position": 1, "choice_id": wrong},
                      headers=host(ann["token"]))
    assert res.status_code == 409

    clock.advance(10)  # halfway
    res = client.post(f"/api/live/{pin}/answer", json={"position": 1, "choice_id": wrong},
                      headers=host(bob["token"]))
    # Everyone has answered, so the question closes at once.
    body = res.json()
    assert body["phase"] == "reveal"
    assert body["you"]["result"] == {"answered": True, "correct": False, "points": 0}

    view = client.get(f"/api/live/{pin}/host", headers=host(token)).json()
    assert view["reveal"]["correct_id"] == right and view["reveal"]["right_count"] == 1
    counts = {c["id"]: c["count"] for c in view["reveal"]["counts"]}
    assert counts[right] == 1 and counts[wrong] == 1
    assert view["leaderboard"][0] == {"id": ann["you"]["id"], "name": "Ann", "score": 1000, "streak": 1}

    # Question 2: Ann right halfway through, Bob never answers.
    client.post(f"/api/live/{pin}/next", headers=host(token))  # scoreboard
    view = client.post(f"/api/live/{pin}/next", headers=host(token)).json()
    assert view["phase"] == "question" and view["position"] == 2
    clock.advance(live.READ_SECONDS + 10)
    client.post(f"/api/live/{pin}/answer", json={"position": 2, "choice_id": correct_id(client, pin, 2)},
                headers=host(ann["token"]))
    clock.advance(10 + live.GRACE_SECONDS)  # time up
    view = client.get(f"/api/live/{pin}/host", headers=host(token)).json()
    assert view["phase"] == "reveal"
    # 750 for speed plus a streak bonus of 100.
    assert view["leaderboard"][0]["score"] == 1000 + 750 + 100

    me = client.get(f"/api/live/{pin}/me", headers=host(bob["token"])).json()
    assert me["you"]["result"]["answered"] is False and me["you"]["rank"] == 2

    # A late answer is refused.
    res = client.post(f"/api/live/{pin}/answer", json={"position": 2, "choice_id": correct_id(client, pin, 2)},
                      headers=host(bob["token"]))
    assert res.status_code == 409

    # Host skips question 3's countdown, then the game ends.
    client.post(f"/api/live/{pin}/next", headers=host(token))
    client.post(f"/api/live/{pin}/next", headers=host(token))
    view = client.post(f"/api/live/{pin}/next", headers=host(token)).json()
    assert view["phase"] == "reveal" and view["position"] == 3
    client.post(f"/api/live/{pin}/next", headers=host(token))
    view = client.post(f"/api/live/{pin}/next", headers=host(token)).json()
    assert view["phase"] == "finished"
    assert [p["name"] for p in view["leaderboard"]] == ["Ann", "Bob"]

    assert client.post(f"/api/live/{pin}/join", json={"name": "Late"}).status_code == 409


def test_remove_and_lock(client, clock):
    room = make_room(client)
    pin, token = room["pin"], room["host_token"]
    ann = join(client, pin, "Ann")
    join(client, pin, "Bob")

    view = client.post(f"/api/live/{pin}/players/{ann['you']['id']}/remove", headers=host(token)).json()
    assert [p["name"] for p in view["players"]] == ["Bob"]
    assert client.get(f"/api/live/{pin}/me", headers=host(ann["token"])).status_code == 410

    client.post(f"/api/live/{pin}/lock", json={"locked": True}, headers=host(token))
    assert client.post(f"/api/live/{pin}/join", json={"name": "Cy"}).status_code == 409
    assert client.get(f"/api/live/{pin}").json()["joinable"] is False


def test_removing_last_answerer_closes_question(client, clock):
    room = make_room(client)
    pin, token = room["pin"], room["host_token"]
    ann = join(client, pin, "Ann")
    bob = join(client, pin, "Bob")
    client.post(f"/api/live/{pin}/next", headers=host(token))
    clock.advance(live.READ_SECONDS + 1)
    client.post(f"/api/live/{pin}/answer", json={"position": 1, "choice_id": correct_id(client, pin, 1)},
                headers=host(ann["token"]))
    view = client.post(f"/api/live/{pin}/players/{bob['you']['id']}/remove", headers=host(token)).json()
    assert view["phase"] == "reveal"


def test_inverted_mode_shows_photos(client, clock):
    room = make_room(client, mode="inverted")
    pin, token = room["pin"], room["host_token"]
    join(client, pin, "Ann")
    view = client.post(f"/api/live/{pin}/next", headers=host(token)).json()
    q = view["question"]
    assert q["prompt"] and q["image_url"] is None
    assert all("image_url" in c and "name" not in c for c in q["choices"])


def test_rejects_bad_settings(client, clock):
    assert client.post("/api/live", json={"mode": "typed"}).status_code == 422
    assert client.post("/api/live", json={"time_limit": 7}).status_code == 422
    assert client.post("/api/live", json={"category_slug": "nope"}).status_code == 404
    assert client.post("/api/live", json={"category_slug": "amino-acids"}).status_code == 409


def test_idle_rooms_are_dropped(client, clock):
    old = make_room(client)
    clock.advance(live.ROOM_IDLE_SECONDS + 1)
    make_room(client)
    assert client.get(f"/api/live/{old['pin']}").status_code == 404


def test_a_taken_pin_is_skipped(client, clock):
    first = make_room(client)
    with client.session_factory() as db:
        room = live.create_room(
            db, mode="choice", question_count=1, time_limit=20, category=None,
            rng=SamePins([first["pin"], "654321"]),
        )
        db.commit()
        assert room.game.pin == "654321"


def teacher(client):
    """Sign-in headers for a teacher account."""
    return auth(sign_in(client).json()["token"])


def stored(client, **where):
    with client.session_factory() as db:
        return db.scalars(select(models.LiveGame).filter_by(**where)).all()


def start_one_question(client, room):
    pin, token = room["pin"], room["host_token"]
    join(client, pin, "Ann")
    client.post(f"/api/live/{pin}/next", headers=host(token))
    return pin, token


def test_a_signed_in_host_owns_the_game(client, clock):
    assert make_room(client, headers=teacher(client))["owned"] is True
    assert make_room(client)["owned"] is False


def test_an_expired_sign_in_still_hosts(client, clock):
    room = make_room(client, headers=auth("not-a-real-token"))
    assert room["owned"] is False


def test_closing_an_owned_started_game_keeps_it(client, clock):
    room = make_room(client, headers=teacher(client))
    pin, token = start_one_question(client, room)
    assert client.delete(f"/api/live/{pin}", headers=host(token)).status_code == 204
    assert client.get(f"/api/live/{pin}").status_code == 404  # the PIN is free again
    [game] = stored(client, host_token=token)
    assert game.pin is None and game.started_at is not None


def test_closing_an_owned_game_still_in_the_lobby_drops_it(client, clock):
    room = make_room(client, headers=teacher(client))
    client.delete(f"/api/live/{room['pin']}", headers=host(room["host_token"]))
    assert stored(client, host_token=room["host_token"]) == []


def test_idle_games_are_archived_or_dropped(client, clock):
    t = teacher(client)
    kept = make_room(client, headers=t)
    start_one_question(client, kept)
    lobby = make_room(client, headers=t)
    anonymous = make_room(client)
    start_one_question(client, anonymous)

    clock.advance(live.ROOM_IDLE_SECONDS + 1)
    make_room(client)  # creating a game runs the purge

    [game] = stored(client, host_token=kept["host_token"])
    assert game.pin is None
    assert stored(client, host_token=lobby["host_token"]) == []
    assert stored(client, host_token=anonymous["host_token"]) == []
    with client.session_factory() as db:
        # Only the kept game's player is left.
        assert db.scalar(select(func.count()).select_from(models.LivePlayer)) == 1


def test_an_archived_games_pin_can_be_reused(client, clock):
    room = make_room(client, headers=teacher(client))
    pin, token = start_one_question(client, room)
    client.delete(f"/api/live/{pin}", headers=host(token))
    with client.session_factory() as db:
        again = live.create_room(
            db, mode="choice", question_count=1, time_limit=20, category=None,
            rng=SamePins([pin]),
        )
        db.commit()
        assert again.game.pin == pin


# --- custom quizzes -------------------------------------------------------------

CUSTOM = {
    "title": "Mixed",
    "lang": "en",
    "questions": [
        {"type": "quiz", "text": "Pick B", "time_limit": 10,
         "options": [{"text": "A"}, {"text": "B", "correct": True}]},
        {"type": "tf", "text": "Water is wet", "time_limit": 5, "answer": True},
        {"type": "type", "text": "Symbol of gold?", "time_limit": 30, "accepted": ["Au"]},
        {"type": "slider", "text": "Boiling point", "time_limit": 20, "min": 0, "max": 200, "step": 1,
         "answer": 100, "tolerance": 2, "unit": "°C"},
    ],
}
RIGHT = [{"choice_id": 1}, {"choice_id": 0}, {"text": " au "}, {"value": 101}]


def custom_room(client, headers, quiz=CUSTOM, lang="en"):
    quiz_id = client.post("/api/quizzes", json=quiz, headers=headers).json()["id"]
    res = client.post("/api/live", json={"custom_quiz_id": quiz_id, "lang": lang}, headers=headers)
    assert res.status_code == 201, res.text
    return res.json()


def test_a_custom_quiz_plays_every_question_type(client, clock):
    t = teacher(client)
    room = custom_room(client, t)
    pin, token = room["pin"], room["host_token"]
    assert (room["mode"], room["question_count"], room["category_name"]) == ("custom", 4, "Mixed")
    ann = join(client, pin, "Ann")["token"]
    for position, (given, limit) in enumerate(zip(RIGHT, [10, 5, 30, 20]), start=1):
        board = client.post(f"/api/live/{pin}/next", headers=host(token)).json()
        assert board["time_limit"] == limit and board["deadline"] - board["starts_at"] == limit
        assert board["question"]["type"] == CUSTOM["questions"][position - 1]["type"]
        clock.advance(live.READ_SECONDS)
        me = client.post(f"/api/live/{pin}/answer", json={"position": position, **given}, headers=host(ann))
        assert me.status_code == 200, me.text
        assert me.json()["you"]["result"]["correct"] is True  # the only player answered: revealed
        assert me.json()["reveal"]["answer_text"]
        client.post(f"/api/live/{pin}/next", headers=host(token))  # standings
    # Instant right answers: 1000 each, plus 100, 200 and 300 for the streak.
    assert client.get(f"/api/live/{pin}/me", headers=host(ann)).json()["you"]["score"] == 4600


def test_points_shrink_over_the_questions_own_time(client, clock):
    t = teacher(client)
    room = custom_room(client, t)
    pin, token = room["pin"], room["host_token"]
    ann = join(client, pin, "Ann")["token"]
    client.post(f"/api/live/{pin}/next", headers=host(token))
    clock.advance(live.READ_SECONDS + 5)  # half of question 1's 10 seconds
    me = client.post(f"/api/live/{pin}/answer", json={"position": 1, "choice_id": 1}, headers=host(ann)).json()
    assert me["you"]["result"]["points"] == 750


def test_a_custom_question_does_not_give_its_answer_away(client, clock):
    t = teacher(client)
    room = custom_room(client, t)
    pin, token = room["pin"], room["host_token"]
    ann = join(client, pin, "Ann")["token"]
    secret = {"correct_ids", "correct_id", "accepted", "answer", "tolerance", "item"}
    for _ in CUSTOM["questions"]:
        board = client.post(f"/api/live/{pin}/next", headers=host(token)).json()
        phone = client.get(f"/api/live/{pin}/me", headers=host(ann)).json()
        for view in (board["question"], phone["question"]):
            assert not secret & set(view), view
        assert board["reveal"] is None and phone["reveal"] is None
        client.post(f"/api/live/{pin}/next", headers=host(token))  # close
        client.post(f"/api/live/{pin}/next", headers=host(token))  # standings


@pytest.mark.parametrize("position, given", [
    (1, {"choice_id": 7}), (1, {"text": "B"}), (3, {"text": "   "}), (3, {"choice_id": 0}),
    (4, {"value": 201}), (4, {}),
])
def test_answers_that_do_not_fit_the_question(client, clock, position, given):
    t = teacher(client)
    room = custom_room(client, t)
    pin, token = room["pin"], room["host_token"]
    ann = join(client, pin, "Ann")["token"]
    for _ in range(position - 1):
        for _ in range(3):
            client.post(f"/api/live/{pin}/next", headers=host(token))  # open, close, standings
    client.post(f"/api/live/{pin}/next", headers=host(token))
    clock.advance(live.READ_SECONDS)
    res = client.post(f"/api/live/{pin}/answer", json={"position": position, **given}, headers=host(ann))
    assert res.status_code == 422 and res.json()["code"] == "not_an_option"


def test_true_false_speaks_the_games_language(client, clock):
    t = teacher(client)
    room = custom_room(client, t, lang="ru")
    pin, token = room["pin"], room["host_token"]
    join(client, pin, "Ann")
    for _ in range(3):
        client.post(f"/api/live/{pin}/next", headers=host(token))
    board = client.post(f"/api/live/{pin}/next", headers=host(token)).json()
    assert [c["name"] for c in board["question"]["choices"]] == ["Верно", "Неверно"]


def test_a_custom_game_needs_your_own_quiz(client, clock):
    mine = teacher(client)
    quiz_id = client.post("/api/quizzes", json=CUSTOM, headers=mine).json()["id"]
    theirs = auth(sign_in(client, name="Bea", email="bea@example.com").json()["token"])
    assert client.post("/api/live", json={"custom_quiz_id": quiz_id}).status_code == 401
    assert client.post("/api/live", json={"custom_quiz_id": quiz_id}, headers=theirs).status_code == 404


def test_a_game_frozen_before_question_types_still_plays(client, clock):
    room = make_room(client, question_count=1)
    pin, token = room["pin"], room["host_token"]
    with client.session_factory() as db:
        game = db.scalars(select(models.LiveGame).where(models.LiveGame.pin == pin)).one()
        game.questions = [{k: v for k, v in q.items() if k not in ("type", "correct_ids", "time_limit")}
                          for q in game.questions]
        db.commit()
    ann = join(client, pin, "Ann")["token"]
    board = client.post(f"/api/live/{pin}/next", headers=host(token)).json()
    assert board["time_limit"] == 20 and board["question"]["type"] == "quiz"
    clock.advance(live.READ_SECONDS)
    right = correct_id(client, pin, 1)
    me = client.post(f"/api/live/{pin}/answer", json={"position": 1, "choice_id": right}, headers=host(ann)).json()
    assert me["you"]["result"]["correct"] is True
    assert me["reveal"]["correct_ids"] == [right] and me["reveal"]["item"]["id"] == right
