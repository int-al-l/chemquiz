"""A live game survives a backend restart, and several backend processes can
serve one game without trampling each other."""

from __future__ import annotations

import threading

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app import live, models
from app.database import get_db
from app.main import app
from test_api import client  # noqa: F401 -- the seeded test app
from test_live import SamePins, clock, correct_id, host, join, make_room  # noqa: F401


def restart(client):
    """Point the app at a brand-new engine on the same database file, as a
    restarted backend process would be. Returns the engine to dispose."""
    path = client.session_factory.kw["bind"].url.database
    engine = create_engine(f"sqlite:///{path}", connect_args={"check_same_thread": False})
    fresh = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def fresh_db():
        db = fresh()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = fresh_db
    return engine


def answer(client, pin, token, position, choice_id):
    return client.post(
        f"/api/live/{pin}/answer",
        json={"position": position, "choice_id": choice_id},
        headers=host(token),
    )


def open_question(client, clock, names=("Ann", "Bob")):
    room = make_room(client)
    pin = room["pin"]
    players = {name: join(client, pin, name) for name in names}
    client.post(f"/api/live/{pin}/next", headers=host(room["host_token"]))
    clock.advance(live.READ_SECONDS + 1)
    return room, players


def test_a_restart_is_only_a_pause(client, clock):
    room, players = open_question(client, clock)
    pin = room["pin"]
    right = correct_id(client, pin, 1)
    assert answer(client, pin, players["Ann"]["token"], 1, right).status_code == 200

    engine = restart(client)
    try:
        me = client.get(f"/api/live/{pin}/me", headers=host(players["Bob"]["token"])).json()
        assert me["phase"] == "question" and me["position"] == 1
        wrong = next(c["id"] for c in me["question"]["choices"] if c["id"] != right)
        assert answer(client, pin, players["Bob"]["token"], 1, wrong).json()["phase"] == "reveal"

        view = client.get(f"/api/live/{pin}/host", headers=host(room["host_token"])).json()
        assert view["reveal"]["right_count"] == 1
        assert view["leaderboard"][0]["name"] == "Ann"
    finally:
        engine.dispose()


def test_a_question_that_ran_out_during_a_restart_closes_on_the_next_poll(client, clock):
    room, players = open_question(client, clock)
    pin = room["pin"]
    clock.advance(20 + live.GRACE_SECONDS + 30)  # the server was down past the deadline

    engine = restart(client)
    try:
        view = client.get(f"/api/live/{pin}/host", headers=host(room["host_token"])).json()
        assert view["phase"] == "reveal" and view["reveal"]["right_count"] == 0
        me = client.get(f"/api/live/{pin}/me", headers=host(players["Ann"]["token"])).json()
        assert me["you"]["result"]["answered"] is False
    finally:
        engine.dispose()


def run_together(*jobs):
    """Start every job at the same moment, each on its own thread."""
    barrier = threading.Barrier(len(jobs))

    def go(job):
        barrier.wait()
        job()

    threads = [threading.Thread(target=go, args=(job,)) for job in jobs]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def test_two_taps_at_once_store_one_answer(client, clock):
    room, players = open_question(client, clock)
    pin = room["pin"]
    right = correct_id(client, pin, 1)
    outcomes = []

    def tap():
        # Its own session, as a second backend process would have.
        with client.session_factory() as db:
            try:
                r = live.open_room(db, pin, lock=True)
                r.answer(r.player_by_token(players["Ann"]["token"]), 1, {"choice_id": right}, clock())
                db.commit()
                outcomes.append("ok")
            except live.LiveError:
                db.rollback()
                outcomes.append("refused")

    run_together(tap, tap)

    assert sorted(outcomes) == ["ok", "refused"]
    with client.session_factory() as db:
        [stored] = db.scalars(select(models.LiveAnswer)).all()
        ann = db.scalars(
            select(models.LivePlayer).where(models.LivePlayer.token == players["Ann"]["token"])
        ).one()
        assert ann.score == stored.points > 0


def test_next_racing_an_answer_leaves_scores_consistent(client, clock):
    room, players = open_question(client, clock)
    pin = room["pin"]
    right = correct_id(client, pin, 1)

    def bob_answers():
        with client.session_factory() as db:
            try:
                r = live.open_room(db, pin, lock=True)
                r.answer(r.player_by_token(players["Bob"]["token"]), 1, {"choice_id": right}, clock())
                db.commit()
            except live.LiveError:
                db.rollback()  # too late: the host closed it first

    def host_skips():
        with client.session_factory() as db:
            r = live.open_room(db, pin, lock=True)
            r.advance(clock())
            db.commit()

    run_together(bob_answers, host_skips)

    with client.session_factory() as db:
        game = db.scalars(select(models.LiveGame).where(models.LiveGame.pin == pin)).one()
        assert game.phase == "reveal"
        answers = db.scalars(select(models.LiveAnswer)).all()
        for p in db.scalars(select(models.LivePlayer)).all():
            mine = [a for a in answers if a.player_id == p.id]
            assert p.score == sum(a.points for a in mine)
            assert p.streak == (1 if any(a.correct for a in mine) else 0)


def test_two_games_created_at_once_get_different_pins(client, clock):
    pins = []

    def create():
        with client.session_factory() as db:
            room = live.create_room(
                db, mode="choice", question_count=1, time_limit=20, category=None,
                rng=SamePins(["111111", "222222"]),
            )
            pins.append(room.game.pin)
            db.commit()

    run_together(create, create)
    assert sorted(pins) == ["111111", "222222"]
