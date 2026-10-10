"""Live classroom games, in the style of Kahoot.

A host (the board at the front of the class) opens a room and gets a short
PIN. Players join from their phones with the PIN and a nickname. The host
starts the game; every question is shown on the board and answered on the
phones, against a clock. Faster right answers score more.

Games live in the database (`models.LiveGame`, `LivePlayer`, `LiveAnswer`),
not in this process: a restart is only a pause, and the backend may run as
several processes. Every change to a game happens with the game locked (see
`find_game`), so two processes never act on one game at once. Polls only
read, apart from closing a question whose time is up and noting who is still
there.

Time is kept by the server. Every snapshot carries the server's `now`, and the
clients count down against `starts_at` / `deadline` corrected by the
difference between their clock and that `now`.

Phases:

    lobby  ->  question  ->  reveal  ->  scoreboard  ->  question ... -> finished
                  (answers)   (right answer   (standings)
                               and counts)

`question` turns into `reveal` by itself when the time runs out or everyone
has answered; every other step is the host pressing Next.
"""

from __future__ import annotations

import random
import re
import secrets
import time
from typing import Optional

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import crud, grading, models
from .database import begin_write
from .i18n import AppError, localized

# --- tuning -------------------------------------------------------------------

TIME_LIMITS = (10, 20, 30, 60)
DEFAULT_TIME_LIMIT = 20
# The question is on the board for this long before answers open, so the class
# can read it and nobody wins by tapping blind.
READ_SECONDS = 3
# Accept an answer this late, to cover the phone-to-server trip.
GRACE_SECONDS = 0.5

MAX_POINTS = 1000
# A right answer at the very last moment still earns half.
MIN_POINTS = 500
STREAK_BONUS = 100
STREAK_BONUS_CAP = 500

MAX_PLAYERS = 80
NAME_MAX = 20
# A room nobody has touched for this long is archived or dropped.
ROOM_IDLE_SECONDS = 3 * 60 * 60
# A player whose phone has not asked for news for this long is shown as away.
AWAY_SECONDS = 8
LEADERBOARD_SIZE = 5
# A poll records that a phone is still there at most this often, so a class of
# eighty polling every second is not eighty writes a second...
SEEN_EVERY_SECONDS = 3
# ...and that the game is still in use at most this often (only the purge reads it).
TOUCH_EVERY_SECONDS = 60
PIN_TRIES = 1000


class LiveError(AppError):
    """A request the game cannot accept (see i18n.AppError)."""


def _now() -> float:
    return time.time()


# --- one game, as loaded for one request -----------------------------------------


class Room:
    """A game's row, its players, and the answers to the question on screen.

    Three queries whatever the size of the class. Rules change these objects;
    the endpoint saves them when it commits.
    """

    def __init__(self, db: Session, game: models.LiveGame):
        self.db = db
        self.game = game
        self.players: list[models.LivePlayer] = list(
            db.scalars(
                select(models.LivePlayer)
                .where(models.LivePlayer.game_id == game.id)
                .order_by(models.LivePlayer.joined_at, models.LivePlayer.id)
                .execution_options(populate_existing=True)
            )
        )
        # player id -> their answer to the question at `game.position`
        self.answers: dict[int, models.LiveAnswer] = {}
        if game.position:
            for answer in db.scalars(
                select(models.LiveAnswer)
                .where(
                    models.LiveAnswer.game_id == game.id,
                    models.LiveAnswer.position == game.position,
                )
                .execution_options(populate_existing=True)
            ):
                self.answers[answer.player_id] = answer

    # -- lookups --

    def time_limit(self) -> int:
        """Seconds for the question on screen: its own (custom quizzes) or the game's."""
        q = self.question
        return (q or {}).get("time_limit") or self.game.time_limit

    @property
    def active_players(self) -> list[models.LivePlayer]:
        return [p for p in self.players if not p.removed]

    @property
    def question(self) -> Optional[dict]:
        questions = self.game.questions
        if 1 <= self.game.position <= len(questions):
            return questions[self.game.position - 1]
        return None

    def player_by_token(self, token: Optional[str]) -> Optional[models.LivePlayer]:
        if not token:
            return None
        for p in self.players:
            if secrets.compare_digest(p.token, token):
                return p
        return None

    def standings(self) -> list[models.LivePlayer]:
        # Ties go to whoever joined first, so the order never flickers.
        return sorted(self.active_players, key=lambda p: (-p.score, p.joined_at, p.id))

    def rank_of(self, player: models.LivePlayer) -> int:
        return self.standings().index(player) + 1

    def answered_count(self) -> int:
        return sum(1 for p in self.active_players if p.id in self.answers)

    # -- the clock --

    def due(self, now: float) -> bool:
        """Should the question on screen close: time up, or everyone answered?"""
        game = self.game
        if game.phase != "question":
            return False
        active = self.active_players
        everyone = bool(active) and self.answered_count() >= len(active)
        return now >= (game.deadline or 0) + GRACE_SECONDS or everyone

    def tick(self, now: float) -> None:
        if self.due(now):
            self._close(now)

    def _close(self, now: float) -> None:
        self.game.phase = "reveal"
        self.game.closed_at = now
        # Anyone who did not answer loses their streak.
        for p in self.active_players:
            if p.id not in self.answers:
                p.streak = 0

    # -- host actions --

    def start(self, now: float) -> None:
        if self.game.phase != "lobby":
            raise LiveError("game_started")
        if not self.active_players:
            raise LiveError("need_player")
        self._open_question(1, now)

    def advance(self, now: float) -> None:
        """The host's Next button, whatever is on screen."""
        self.tick(now)
        game = self.game
        if game.phase == "question":
            self._close(now)  # skip the rest of the countdown
        elif game.phase == "reveal":
            game.phase = "scoreboard"
        elif game.phase == "scoreboard":
            if game.position >= len(game.questions):
                self._finish(now)
            else:
                self._open_question(game.position + 1, now)
        elif game.phase == "lobby":
            self.start(now)
        else:
            raise LiveError("game_over")

    def finish(self, now: float) -> None:
        if self.game.phase == "question":
            self._close(now)
        self._finish(now)

    def _finish(self, now: float) -> None:
        self.game.phase = "finished"
        if self.game.finished_at is None:
            self.game.finished_at = now

    def _open_question(self, position: int, now: float) -> None:
        game = self.game
        game.position = position
        game.phase = "question"
        game.starts_at = now + READ_SECONDS
        game.deadline = game.starts_at + self.time_limit()
        game.closed_at = None
        if game.started_at is None:
            game.started_at = now
        self.answers = {}

    def remove(self, player_id: int, now: float) -> None:
        for p in self.players:
            if p.id == player_id:
                p.removed = True
                self.tick(now)  # they may have been the last one to answer
                return
        raise LiveError("no_such_player", status=404)

    # -- player actions --

    def join(self, name: str, now: float) -> models.LivePlayer:
        game = self.game
        if game.phase == "finished":
            raise LiveError("game_finished")
        if game.locked:
            raise LiveError("room_locked")
        clean = clean_name(name)
        taken = {p.name.casefold() for p in self.active_players}
        if clean.casefold() in taken:
            raise LiveError("name_taken")
        if len(self.active_players) >= MAX_PLAYERS:
            raise LiveError("room_full")
        player = models.LivePlayer(
            game_id=game.id,
            token=secrets.token_urlsafe(24),
            name=clean,
            joined_at=now,
            last_seen=now,
            score=0,
            streak=0,
            removed=False,
        )
        self.db.add(player)
        self.db.flush()  # the id goes into the reply
        self.players.append(player)
        return player

    def answer(
        self, player: models.LivePlayer, position: int, given: dict, now: float
    ) -> models.LiveAnswer:
        """`given` is {"choice_id"}, {"text"} or {"value"}, whichever the question asks for."""
        self.tick(now)
        game = self.game
        question = self.question
        if game.phase != "question" or question is None or position != game.position:
            raise LiveError("too_late")
        if now < (game.starts_at or 0):
            raise LiveError("not_open_yet")
        if player.id in self.answers:
            raise LiveError("already_answered")
        try:
            correct = grading.grade(question, given)
        except ValueError:
            raise LiveError("not_an_option", status=422) from None

        limit = self.time_limit()
        elapsed = max(0.0, min(now - game.starts_at, float(limit)))
        points = 0
        if correct:
            player.streak += 1
            fraction = elapsed / limit
            points = round(MAX_POINTS - (MAX_POINTS - MIN_POINTS) * fraction)
            points += min((player.streak - 1) * STREAK_BONUS, STREAK_BONUS_CAP)
        else:
            player.streak = 0
        player.score += points

        choice = grading.kind(question) in grading.CHOICE_TYPES
        typed = given.get("text") if "text" in given else given.get("value")
        answer = models.LiveAnswer(
            game_id=game.id,
            player_id=player.id,
            position=position,
            choice_id=given["choice_id"] if choice else -1,
            answer=None if choice else str(typed).strip()[:100],
            elapsed=elapsed,
            correct=correct,
            points=points,
        )
        self.db.add(answer)
        self.answers[player.id] = answer
        self.tick(now)
        return answer


def clean_name(name: str) -> str:
    clean = re.sub(r"\s+", " ", name or "").strip()
    # Control and formatting characters would let a name look empty or odd.
    clean = "".join(ch for ch in clean if ch.isprintable())
    if not clean:
        raise LiveError("type_a_name", status=422)
    if len(clean) > NAME_MAX:
        raise LiveError("name_too_long", status=422, n=NAME_MAX)
    return clean


# --- finding and locking games ------------------------------------------------------


def find_game(db: Session, pin: Optional[str], *, lock: bool = False) -> models.LiveGame:
    """The game with this PIN.

    With `lock`, the transaction becomes the game's only writer until it
    commits or rolls back: FOR UPDATE on the row (Postgres), or the database's
    write lock (SQLite, see `database.begin_write`). Rows are always read
    afresh, never taken from the session's cache.
    """
    pin = (pin or "").strip()
    if not pin:
        raise LiveError("game_not_found", status=404)
    if lock:
        begin_write(db)
    stmt = (
        select(models.LiveGame)
        .where(models.LiveGame.pin == pin)
        .execution_options(populate_existing=True)
    )
    if lock:
        stmt = stmt.with_for_update()
    game = db.scalars(stmt).first()
    if game is None:
        raise LiveError("game_not_found", status=404)
    return game


def open_room(db: Session, pin: Optional[str], *, lock: bool = False) -> Room:
    return Room(db, find_game(db, pin, lock=lock))


def poll(db: Session, room: Room, now: float) -> Room:
    """The room a poll should show, closing the question first if it is due.

    Only then does a poll take the lock. It checks again once it holds it:
    another process may have closed the question in between.
    """
    if not room.due(now):
        return room
    locked = open_room(db, room.game.pin, lock=True)
    locked.tick(now)
    db.flush()
    return locked


def check_host(room: Room, token: Optional[str]) -> None:
    if not token or not secrets.compare_digest(room.game.host_token, token):
        raise LiveError("host_only", status=403)


def mark_seen(db: Session, room: Room, player: models.LivePlayer, now: float) -> None:
    """Note that this phone is still here -- at most every few seconds."""
    # Touch the game row before the player row: every other writer locks
    # live_games first and live_players second, and taking them in the
    # opposite order here would let two transactions deadlock on Postgres.
    mark_touched(db, room, now)
    if now - player.last_seen >= SEEN_EVERY_SECONDS:
        db.execute(
            update(models.LivePlayer)
            .where(models.LivePlayer.id == player.id)
            .values(last_seen=now)
        )


def mark_touched(db: Session, room: Room, now: float) -> None:
    """Note that the game is still in use, for the purge."""
    if now - room.game.touched_at >= TOUCH_EVERY_SECONDS:
        db.execute(
            update(models.LiveGame)
            .where(models.LiveGame.id == room.game.id)
            .values(touched_at=now)
        )


# --- creating, archiving, dropping -------------------------------------------------------


def create_room(
    db: Session,
    *,
    mode: str,
    question_count: int,
    time_limit: int,
    category: Optional[models.Category],
    host_user: Optional[models.User] = None,
    items: Optional[list[models.Item]] = None,
    rng: Optional[random.Random] = None,
    lang: str = "en",
) -> Room:
    """Draw the questions, in `lang`, and open a room for them.

    `items` fixes which items are asked (work on mistakes); otherwise
    `question_count` of the deck's items are drawn at random. The caller
    builds its reply from the returned room, then commits.
    """
    rng = rng or random.SystemRandom()
    pool = list(crud.list_items(db, category.id if category else None))
    if not pool:
        raise LiveError("no_items")
    if items is None:
        asked = list(pool)
        rng.shuffle(asked)
        asked = asked[: max(1, min(question_count, len(asked)))]
    else:
        asked = list(items)
        rng.shuffle(asked)
    questions = _draw(db, asked, pool, mode, rng, lang)

    # Read everything needed from these objects now: the purge commits, and
    # a commit expires them.
    settings = dict(
        host_user_id=host_user.id if host_user else None,
        mode=mode,
        time_limit=time_limit,
        question_count=len(questions),
        category_id=category.id if category else None,
        category_slug=category.slug if category else None,
        category_name=localized(category, "name", lang) if category else None,
        lang=lang,
        questions=questions,
    )
    return _open(db, settings, rng)


def _open(db: Session, settings: dict, rng: random.Random) -> Room:
    """A new room with these settings and a free PIN."""
    now = _now()
    purge(db, now)

    for _ in range(PIN_TRIES):
        pin = f"{rng.randint(100000, 999999)}"
        begin_write(db)
        if db.scalar(select(models.LiveGame.id).where(models.LiveGame.pin == pin)) is not None:
            db.rollback()
            continue
        game = models.LiveGame(
            pin=pin,
            host_token=secrets.token_urlsafe(24),
            phase="lobby",
            position=0,
            locked=False,
            created_at=now,
            touched_at=now,
            **settings,
        )
        db.add(game)
        try:
            db.flush()
        except IntegrityError:
            # Another process took this PIN a moment ago (possible on Postgres;
            # SQLite's single writer rules it out).
            db.rollback()
            continue
        return Room(db, game)
    raise LiveError("no_free_pins", status=503)


def create_custom_room(
    db: Session,
    *,
    questions: list[dict],
    title: str,
    quiz_id: Optional[int],
    host_user: Optional[models.User] = None,
    lang: str = "en",
    rng: Optional[random.Random] = None,
) -> Room:
    """Open a room for frozen questions from a teacher's own quiz (see
    quizzes.freeze), in order. Also used by "Work on mistakes" with a subset."""
    if not questions:
        raise LiveError("no_items")
    questions = [{**q, "position": n} for n, q in enumerate(questions, start=1)]
    settings = dict(
        host_user_id=host_user.id if host_user else None,
        mode="custom",
        time_limit=max(q.get("time_limit") or DEFAULT_TIME_LIMIT for q in questions),
        question_count=len(questions),
        category_id=None,
        category_slug=None,
        category_name=title,
        custom_quiz_id=quiz_id,
        lang=lang,
        questions=questions,
    )
    return _open(db, settings, rng or random.SystemRandom())


def _draw(db: Session, asked, pool, mode: str, rng: random.Random, lang: str = "en") -> list[dict]:
    """The frozen questions: what is shown, the options, and the answer."""
    questions = []
    for position, (item, options, photo, picks) in enumerate(
        crud.draw_questions(db, asked, pool, mode, rng), start=1
    ):
        photo_url = crud.image_url(photo.filename) if photo else crud.image_url(item.cover)
        if mode == "inverted":
            choices = [
                {"id": option.id, "image_url": crud.image_url(pick.filename if pick else option.cover)}
                for option, pick in zip(options, picks)
            ]
        else:
            choices = [{"id": o.id, "name": localized(o, "name", lang)} for o in options]
        answer = crud.item_payload(item, lang)
        # Reveal the picture that was actually asked about.
        answer["image_url"] = photo_url
        questions.append(
            {
                "type": "quiz",
                "position": position,
                "correct_id": item.id,
                "correct_ids": [item.id],
                "image_url": photo_url if mode == "choice" else None,
                "prompt": localized(item, "name", lang) if mode == "inverted" else None,
                "choices": choices,
                "item": answer,
            }
        )
    return questions


def keeps(game: models.LiveGame) -> bool:
    """Is this game kept once it is over: a signed-in host's, past the lobby?"""
    return game.host_user_id is not None and game.started_at is not None


def retire(db: Session, game: models.LiveGame) -> None:
    """End a game's life as a room: into its host's history, or gone."""
    if keeps(game):
        game.pin = None
    else:
        delete_game(db, game.id)


def delete_game(db: Session, game_id: int) -> None:
    """A game and everything in it.

    Deleted explicitly rather than left to ON DELETE CASCADE, which SQLite
    only honours with foreign keys switched on.
    """
    db.execute(delete(models.LiveAnswer).where(models.LiveAnswer.game_id == game_id))
    db.execute(delete(models.LivePlayer).where(models.LivePlayer.game_id == game_id))
    db.execute(delete(models.LiveGame).where(models.LiveGame.id == game_id))


def purge(db: Session, now: Optional[float] = None) -> None:
    """Archive or drop the games nobody has touched for ROOM_IDLE_SECONDS."""
    now = _now() if now is None else now
    begin_write(db)
    stale = db.scalars(
        select(models.LiveGame)
        .where(
            models.LiveGame.pin.is_not(None),
            models.LiveGame.touched_at < now - ROOM_IDLE_SECONDS,
        )
        .with_for_update()
    ).all()
    for game in stale:
        retire(db, game)
    db.commit()


# --- what each side is shown ------------------------------------------------------


def _question_public(q: dict) -> dict:
    """The question without its answer."""
    kind = grading.kind(q)
    out = {
        "position": q["position"],
        "type": kind,
        "image_url": q["image_url"],
        "prompt": q["prompt"],
        "time_limit": q.get("time_limit"),
    }
    if kind in grading.CHOICE_TYPES:
        out["choices"] = q["choices"]
    if kind == "slider":
        out.update({k: q[k] for k in ("min", "max", "step", "unit")})
    return out


def _reveal(room: Room) -> Optional[dict]:
    game = room.game
    q = room.question
    if q is None or game.phase not in ("reveal", "scoreboard", "finished") or game.closed_at is None:
        return None
    counts = {c["id"]: 0 for c in q.get("choices", [])}
    right = 0
    for p in room.active_players:
        a = room.answers.get(p.id)
        if a is None:
            continue
        if a.choice_id in counts:
            counts[a.choice_id] += 1
        if a.correct:
            right += 1
    return {
        "type": grading.kind(q),
        "correct_id": q.get("correct_id"),
        "correct_ids": grading.correct_ids(q) if q.get("choices") else [],
        "item": q.get("item"),
        "answer_text": grading.answer_text(q),
        "counts": [{"id": cid, "count": n} for cid, n in counts.items()],
        "right_count": right,
    }


def _clock(room: Room, now: float) -> dict:
    game = room.game
    return {
        "now": now,
        "starts_at": game.starts_at if game.phase == "question" else None,
        "deadline": game.deadline if game.phase == "question" else None,
        "time_limit": room.time_limit(),
    }


def host_view(room: Room, now: float) -> dict:
    game = room.game
    standings = room.standings()
    return {
        "pin": game.pin,
        "lang": game.lang,
        "phase": game.phase,
        "mode": game.mode,
        "category_name": game.category_name,
        "question_count": len(game.questions),
        "position": game.position,
        "locked": game.locked,
        # Signed in when the room was opened: the game goes into their history.
        "owned": game.host_user_id is not None,
        **_clock(room, now),
        "players": [
            {
                "id": p.id,
                "name": p.name,
                "score": p.score,
                "away": now - p.last_seen > AWAY_SECONDS,
                "answered": game.phase == "question" and p.id in room.answers,
            }
            for p in sorted(room.active_players, key=lambda p: (p.joined_at, p.id))
        ],
        "answered_count": room.answered_count() if game.position else 0,
        "question": _question_public(room.question) if room.question and game.phase != "lobby" else None,
        "reveal": _reveal(room),
        "leaderboard": [
            {"id": p.id, "name": p.name, "score": p.score, "streak": p.streak}
            for p in standings[: (len(standings) if game.phase == "finished" else LEADERBOARD_SIZE)]
        ],
    }


def player_view(room: Room, player: models.LivePlayer, now: float) -> dict:
    game = room.game
    q = room.question
    answer = room.answers.get(player.id) if game.position else None
    reveal = _reveal(room)
    you = {
        "id": player.id,
        "name": player.name,
        "score": player.score,
        "streak": player.streak,
        "rank": room.rank_of(player),
        "answered_id": answer.choice_id if answer else None,
        "answered": answer is not None,
        "answer": answer.answer if answer else None,
    }
    if reveal is not None:
        you["result"] = {
            "answered": answer is not None,
            "correct": bool(answer and answer.correct),
            "points": answer.points if answer else 0,
        }
    return {
        "pin": game.pin,
        "lang": game.lang,
        "phase": game.phase,
        "mode": game.mode,
        "question_count": len(game.questions),
        "position": game.position,
        **_clock(room, now),
        "player_count": len(room.active_players),
        "question": _question_public(q) if q and game.phase == "question" else None,
        "reveal": reveal,
        "you": you,
    }
