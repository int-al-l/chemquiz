"""A teacher's past class games: the list, the standings, the CSV, and
playing again."""

from __future__ import annotations

from sqlalchemy import func, select, update

from app import live, models
from test_api import auth, client, sign_in  # noqa: F401 -- the seeded test app
from test_live import clock, correct_id, host, join, make_room, teacher  # noqa: F401


def play(client, clock, players, script, headers=None, finish=True):
    """Host a game in the condensers deck and play it out.

    `script` has one entry per question: {player name: "right" | "wrong"}.
    A player left out of an entry does not answer that question.
    Returns the room and each player's join reply.
    """
    room = make_room(client, headers=headers, question_count=len(script))
    pin, token = room["pin"], room["host_token"]
    joined = {name: join(client, pin, name) for name in players}
    for position, marks in enumerate(script, start=1):
        client.post(f"/api/live/{pin}/next", headers=host(token))  # the question opens
        clock.advance(live.READ_SECONDS + 1)
        right = correct_id(client, pin, position)
        me = client.get(f"/api/live/{pin}/me", headers=host(joined[players[0]]["token"])).json()
        wrong = next(c["id"] for c in me["question"]["choices"] if c["id"] != right)
        for name, mark in marks.items():
            client.post(
                f"/api/live/{pin}/answer",
                json={"position": position, "choice_id": right if mark == "right" else wrong},
                headers=host(joined[name]["token"]),
            )
        if client.get(f"/api/live/{pin}/host", headers=host(token)).json()["phase"] == "question":
            client.post(f"/api/live/{pin}/next", headers=host(token))  # close it
        client.post(f"/api/live/{pin}/next", headers=host(token))  # standings
    if finish:
        client.post(f"/api/live/{pin}/next", headers=host(token))
    return room, joined


def only_game(client, headers):
    [game] = client.get("/api/me/live-games", headers=headers).json()
    return game


def test_history_lists_your_started_games_newest_first(client, clock):
    t = teacher(client)
    play(client, clock, ["Ann", "Bob"], [{"Ann": "right", "Bob": "wrong"}], headers=t)
    clock.advance(60)
    play(client, clock, ["Cy"], [{"Cy": "right"}], headers=t, finish=False)
    make_room(client, headers=t)  # never started: not history
    play(client, clock, ["Dee"], [{"Dee": "right"}])  # anonymous: not history

    games = client.get("/api/me/live-games", headers=t).json()
    assert [g["status"] for g in games] == ["live", "finished"]
    older = games[1]
    assert older["winner"] == "Ann" and older["player_count"] == 2
    assert older["category_name"] == "Condensers" and older["mode"] == "choice"
    assert older["question_count"] == 1 and older["asked_count"] == 1
    assert games[0]["played_at"] > older["played_at"]


def test_history_needs_sign_in_and_hides_other_teachers_games(client, clock):
    mine = teacher(client)
    theirs = auth(sign_in(client, name="Bea", email="bea@example.com").json()["token"])
    play(client, clock, ["Ann"], [{"Ann": "right"}], headers=theirs)

    assert client.get("/api/me/live-games").status_code == 401
    assert client.get("/api/me/live-games", headers=mine).json() == []
    game = only_game(client, theirs)
    assert client.get(f"/api/me/live-games/{game['id']}", headers=mine).status_code == 404
    assert client.delete(f"/api/me/live-games/{game['id']}", headers=mine).status_code == 404


def test_a_games_standings(client, clock):
    t = teacher(client)
    play(
        client, clock, ["Ann", "Bob", "Cy"],
        [{"Ann": "right", "Bob": "wrong"}, {"Ann": "right", "Bob": "right"}],
        headers=t,
    )
    game = client.get(f"/api/me/live-games/{only_game(client, t)['id']}", headers=t).json()
    assert game["status"] == "finished" and game["asked_count"] == 2 and game["time_limit"] == 20
    assert [(r["place"], r["name"], r["correct"]) for r in game["standings"]] == [
        (1, "Ann", 2), (2, "Bob", 1), (3, "Cy", 0),
    ]
    assert game["standings"][0]["score"] > game["standings"][1]["score"] > 0


def test_deleting_a_game(client, clock):
    t = teacher(client)
    room, _ = play(client, clock, ["Ann"], [{"Ann": "right"}], headers=t, finish=False)
    game = only_game(client, t)
    assert client.delete(f"/api/me/live-games/{game['id']}", headers=t).status_code == 409

    client.delete(f"/api/live/{room['pin']}", headers=host(room["host_token"]))  # close the room
    assert only_game(client, t)["status"] == "unfinished"
    assert client.delete(f"/api/me/live-games/{game['id']}", headers=t).status_code == 204
    assert client.get("/api/me/live-games", headers=t).json() == []
    with client.session_factory() as db:
        assert db.scalar(select(func.count()).select_from(models.LiveAnswer)) == 0
        assert db.scalar(select(func.count()).select_from(models.LivePlayer)) == 0
