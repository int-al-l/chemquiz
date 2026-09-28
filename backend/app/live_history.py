"""A teacher's past class games: the list, the standings, a CSV of the
results, and what to play next.

Only games hosted while signed in, and that got past the lobby, are kept
(see `live.keeps`); these are the same rows the game was played on.
"""

from __future__ import annotations

import csv
import datetime as dt
import io
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from . import live, models

# An item goes into "Work on mistakes" when fewer than this share of the class
# got it right. Not answering counts as getting it wrong.
MISTAKE_THRESHOLD = 0.8


def status(game: models.LiveGame) -> str:
    if game.finished_at is not None:
        return "finished"
    if game.pin is not None:
        return "live"
    return "unfinished"


def asked(game: models.LiveGame) -> list[dict]:
    """The questions actually put to the class: an unfinished game never
    reached the later ones."""
    return game.questions[: game.position]


class Results:
    """A game's active players in standings order, and all their answers."""

    def __init__(self, db: Session, game: models.LiveGame):
        self.game = game
        players = db.scalars(
            select(models.LivePlayer).where(
                models.LivePlayer.game_id == game.id,
                models.LivePlayer.removed.is_(False),
            )
        ).all()
        # The same order as the board's standings.
        self.players = sorted(players, key=lambda p: (-p.score, p.joined_at, p.id))
        # player id -> position -> answer
        self.answers: dict[int, dict[int, models.LiveAnswer]] = {p.id: {} for p in self.players}
        for a in db.scalars(select(models.LiveAnswer).where(models.LiveAnswer.game_id == game.id)):
            if a.player_id in self.answers:  # removed players are left out
                self.answers[a.player_id][a.position] = a

    def correct_count(self, player: models.LivePlayer) -> int:
        return sum(1 for a in self.answers[player.id].values() if a.correct)

    def mistake_item_ids(self) -> list[int]:
        """The items fewer than MISTAKE_THRESHOLD of the class got right."""
        if not self.players:
            return []
        ids = []
        for q in asked(self.game):
            right = sum(
                1 for p in self.players
                if (a := self.answers[p.id].get(q["position"])) is not None and a.correct
            )
            if right < MISTAKE_THRESHOLD * len(self.players):
                ids.append(q["correct_id"])
        return ids


def _summary(game: models.LiveGame, results: Results) -> dict:
    return {
        "id": game.id,
        "played_at": game.started_at,
        "category_name": game.category_name,
        "mode": game.mode,
        "question_count": len(game.questions),
        "asked_count": len(asked(game)),
        "player_count": len(results.players),
        "winner": results.players[0].name if results.players else None,
        "status": status(game),
        "has_mistakes": bool(results.mistake_item_ids()),
    }


def summary(db: Session, game: models.LiveGame) -> dict:
    return _summary(game, Results(db, game))


def detail(db: Session, game: models.LiveGame) -> dict:
    results = Results(db, game)
    return {
        **_summary(game, results),
        "time_limit": game.time_limit,
        "standings": [
            {
                "place": place,
                "id": p.id,
                "name": p.name,
                "score": p.score,
                "correct": results.correct_count(p),
            }
            for place, p in enumerate(results.players, start=1)
        ],
    }


# A spreadsheet runs a cell starting with one of these as a formula, and a
# nickname is typed by a student.
_FORMULA_START = ("=", "+", "-", "@", "\t", "\r")


def _cell(text: str) -> str:
    return "'" + text if text.startswith(_FORMULA_START) else text


def results_csv(db: Session, game: models.LiveGame) -> str:
    """One row per player: place, name, score, right answers, then + / − /
    blank for each question asked.

    Semicolons and a byte-order mark, so Excel set up for Russian (or most of
    Europe) opens it with a double click; Google Sheets reads it too.
    """
    results = Results(db, game)
    questions = asked(game)
    out = io.StringIO()
    writer = csv.writer(out, delimiter=";", lineterminator="\r\n")
    writer.writerow(
        ["Place", "Name", "Score", "Correct",
         *(_cell(f"Q{q['position']} {q['item']['name']}") for q in questions)]
    )
    for place, p in enumerate(results.players, start=1):
        mine = results.answers[p.id]
        marks = []
        for q in questions:
            a = mine.get(q["position"])
            marks.append("" if a is None else "+" if a.correct else "−")
        writer.writerow([place, _cell(p.name), p.score, results.correct_count(p), *marks])
    return "﻿" + out.getvalue()


def csv_filename(game: models.LiveGame) -> str:
    day = dt.datetime.fromtimestamp(game.started_at, dt.timezone.utc).strftime("%Y-%m-%d")
    return f"chemquiz-class-game-{day}.csv"


def _deck(db: Session, game: models.LiveGame) -> Optional[models.Category]:
    """The deck to play again from; None means the whole library."""
    if game.category_slug is None:
        return None
    category = db.get(models.Category, game.category_id) if game.category_id else None
    if category is None:
        raise live.LiveError("deck_gone")
    return category


def replay(db: Session, game: models.LiveGame, kind: str, user: models.User) -> live.Room:
    """A new room from a past game: "same" draws afresh with the same
    settings; "mistakes" asks only what the class got wrong."""
    category = _deck(db, game)
    if kind == "same":
        return live.create_room(
            db,
            mode=game.mode,
            question_count=game.question_count,
            time_limit=game.time_limit,
            category=category,
            host_user=user,
            lang=game.lang,
        )
    ids = Results(db, game).mistake_item_ids()
    if not ids:
        raise live.LiveError("no_mistakes")
    items = db.scalars(
        select(models.Item)
        .where(models.Item.id.in_(ids))
        .options(selectinload(models.Item.photos), selectinload(models.Item.category))
    ).all()
    if not items:
        raise live.LiveError("items_gone")
    return live.create_room(
        db,
        mode=game.mode,
        question_count=len(items),
        time_limit=game.time_limit,
        category=category,
        host_user=user,
        items=list(items),
        lang=game.lang,
    )
