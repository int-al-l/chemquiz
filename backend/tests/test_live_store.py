"""The constraints the live game leans on when several processes share the
database."""

from __future__ import annotations

import secrets

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app import models
from test_api import client, db_session  # noqa: F401 -- the seeded test app


def game(pin="123456"):
    return models.LiveGame(
        pin=pin,
        host_token=secrets.token_urlsafe(24),
        host_user_id=None,
        mode="choice",
        time_limit=20,
        question_count=1,
        category_id=None,
        category_slug=None,
        category_name=None,
        questions=[],
        phase="lobby",
        position=0,
        locked=False,
        created_at=0.0,
        touched_at=0.0,
    )


def test_pins_are_unique_among_live_games(db_session):
    db_session.add(game("123456"))
    db_session.commit()
    db_session.add(game("123456"))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_archived_games_release_their_pin(db_session):
    db_session.add_all([game(None), game(None), game("123456")])
    db_session.commit()
    assert db_session.scalar(select(func.count()).select_from(models.LiveGame)) == 3


def test_a_player_answers_each_question_once(db_session):
    g = game()
    db_session.add(g)
    db_session.flush()
    player = models.LivePlayer(
        game_id=g.id, token="t", name="Ann", joined_at=0.0, last_seen=0.0,
        score=0, streak=0, removed=False,
    )
    db_session.add(player)
    db_session.flush()

    def answer():
        return models.LiveAnswer(
            game_id=g.id, player_id=player.id, position=1, choice_id=1,
            elapsed=1.0, correct=True, points=1000,
        )

    db_session.add(answer())
    db_session.commit()
    db_session.add(answer())
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
