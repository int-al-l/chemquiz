"""Live classroom games, in the style of Kahoot.

A host (the board at the front of the class) opens a room and gets a short
PIN. Players join from their phones with the PIN and a nickname. The host
starts the game; every question is shown on the board and answered on the
phones, against a clock. Faster right answers score more.

Rooms are short-lived and only matter while a lesson is running, so they live
in this process's memory rather than in the database. That means the backend
must run as a single process (plain `uvicorn app.main:app`, no `--workers N`),
and a server restart ends any game in progress.

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
import threading
import time
from dataclasses import dataclass, field
from typing import Optional

from . import crud, models
from sqlalchemy.orm import Session

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
# A room nobody has touched for this long is dropped.
ROOM_IDLE_SECONDS = 3 * 60 * 60
# A player whose phone has not asked for news for this long is shown as away.
AWAY_SECONDS = 8
LEADERBOARD_SIZE = 5


class LiveError(Exception):
    """A request the game cannot accept. `status` is the HTTP status to send."""

    def __init__(self, message: str, status: int = 409):
        super().__init__(message)
        self.status = status


def _now() -> float:
    return time.time()


# --- state --------------------------------------------------------------------


@dataclass
class Answer:
    choice_id: int
    elapsed: float
    correct: bool
    points: int


@dataclass
class Player:
    id: int
    token: str
    name: str
    joined_at: float
    last_seen: float
    score: int = 0
    streak: int = 0
    answers: dict[int, Answer] = field(default_factory=dict)
    removed: bool = False


@dataclass
class Question:
    position: int
    correct_id: int
    image_url: Optional[str]  # the photo asked about ("choice" mode)
    prompt: Optional[str]  # the name asked for ("inverted" mode)
    choices: list[dict]  # {"id", "name"} or {"id", "image_url"}
    item: dict  # the right answer, revealed after the question


@dataclass
class Room:
    pin: str
    host_token: str
    mode: str
    time_limit: int
    category_name: Optional[str]
    questions: list[Question]
    created_at: float
    touched_at: float
    phase: str = "lobby"
    position: int = 0  # 1-based once the game has started
    starts_at: Optional[float] = None
    deadline: Optional[float] = None
    closed_at: Optional[float] = None  # when the current question stopped taking answers
    players: list[Player] = field(default_factory=list)
    next_player_id: int = 1
    locked: bool = False  # no new players

    # -- lookups --

    @property
    def active_players(self) -> list[Player]:
        return [p for p in self.players if not p.removed]

    @property
    def question(self) -> Optional[Question]:
        if 1 <= self.position <= len(self.questions):
            return self.questions[self.position - 1]
        return None

    def player_by_token(self, token: Optional[str]) -> Optional[Player]:
        if not token:
            return None
        for p in self.players:
            if secrets.compare_digest(p.token, token):
                return p
        return None

    def standings(self) -> list[Player]:
        # Ties go to whoever joined first, so the order never flickers.
        return sorted(self.active_players, key=lambda p: (-p.score, p.joined_at))

    def rank_of(self, player: Player) -> int:
        return self.standings().index(player) + 1

    # -- the clock --

    def tick(self, now: float) -> None:
        """Close the current question if its time is up or everyone answered."""
        if self.phase != "question":
            return
        answered = self.answered_count()
        everyone = self.active_players and answered >= len(self.active_players)
        if now >= (self.deadline or 0) + GRACE_SECONDS or everyone:
            self._close(now)

    def answered_count(self) -> int:
        return sum(1 for p in self.active_players if self.position in p.answers)

    def _close(self, now: float) -> None:
        self.phase = "reveal"
        self.closed_at = now
        # Anyone who did not answer loses their streak.
        for p in self.active_players:
            if self.position not in p.answers:
                p.streak = 0

    # -- host actions --

    def start(self, now: float) -> None:
        if self.phase != "lobby":
            raise LiveError("The game has already started")
        if not self.active_players:
            raise LiveError("Wait for at least one player to join")
        self._open_question(1, now)

    def advance(self, now: float) -> None:
        """The host's Next button, whatever is on screen."""
        self.tick(now)
        if self.phase == "question":
            self._close(now)  # skip the rest of the countdown
        elif self.phase == "reveal":
            self.phase = "scoreboard"
        elif self.phase == "scoreboard":
            if self.position >= len(self.questions):
                self.phase = "finished"
            else:
                self._open_question(self.position + 1, now)
        elif self.phase == "lobby":
            self.start(now)
        else:
            raise LiveError("The game is over")

    def finish(self, now: float) -> None:
        if self.phase == "question":
            self._close(now)
        self.phase = "finished"

    def _open_question(self, position: int, now: float) -> None:
        self.position = position
        self.phase = "question"
        self.starts_at = now + READ_SECONDS
        self.deadline = self.starts_at + self.time_limit
        self.closed_at = None

    # -- player actions --

    def join(self, name: str, now: float) -> Player:
        if self.phase == "finished":
            raise LiveError("This game has finished")
        if self.locked:
            raise LiveError("The host has locked this game")
        clean = clean_name(name)
        taken = {p.name.casefold() for p in self.active_players}
        if clean.casefold() in taken:
            raise LiveError("Someone already has that name -- pick another")
        if len(self.active_players) >= MAX_PLAYERS:
            raise LiveError("The room is full")
        player = Player(
            id=self.next_player_id,
            token=secrets.token_urlsafe(24),
            name=clean,
            joined_at=now,
            last_seen=now,
        )
        self.next_player_id += 1
        self.players.append(player)
        return player

    def answer(self, player: Player, position: int, choice_id: int, now: float) -> Answer:
        self.tick(now)
        question = self.question
        if self.phase != "question" or question is None or position != self.position:
            raise LiveError("Too late -- this question is closed")
        if now < (self.starts_at or 0):
            raise LiveError("Answers are not open yet")
        if position in player.answers:
            raise LiveError("You have already answered")
        if choice_id not in {c["id"] for c in question.choices}:
            raise LiveError("That is not one of the options", status=422)

        elapsed = max(0.0, min(now - self.starts_at, float(self.time_limit)))
        correct = choice_id == question.correct_id
        points = 0
        if correct:
            player.streak += 1
            fraction = elapsed / self.time_limit
            points = round(MAX_POINTS - (MAX_POINTS - MIN_POINTS) * fraction)
            points += min((player.streak - 1) * STREAK_BONUS, STREAK_BONUS_CAP)
        else:
            player.streak = 0
        player.score += points

        result = Answer(choice_id=choice_id, elapsed=elapsed, correct=correct, points=points)
        player.answers[position] = result
        self.tick(now)
        return result


def clean_name(name: str) -> str:
    clean = re.sub(r"\s+", " ", name or "").strip()
    # Control and formatting characters would let a name look empty or odd.
    clean = "".join(ch for ch in clean if ch.isprintable())
    if not clean:
        raise LiveError("Type a name", status=422)
    if len(clean) > NAME_MAX:
        raise LiveError(f"Names can be at most {NAME_MAX} characters", status=422)
    return clean


# --- the registry ---------------------------------------------------------------


class Registry:
    """Every open room, guarded by one lock.

    The endpoints are plain `def`s, so FastAPI runs them on a thread pool and
    two phones can land here at once. The work under the lock is tiny.
    """

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.rooms: dict[str, Room] = {}

    def purge(self, now: float) -> None:
        stale = [pin for pin, r in self.rooms.items() if now - r.touched_at > ROOM_IDLE_SECONDS]
        for pin in stale:
            del self.rooms[pin]

    def new_pin(self, rng: random.Random) -> str:
        for _ in range(1000):
            pin = f"{rng.randint(100000, 999999)}"
            if pin not in self.rooms:
                return pin
        raise LiveError("No free room codes right now", status=503)

    def get(self, pin: str) -> Room:
        room = self.rooms.get((pin or "").strip())
        if room is None:
            raise LiveError("No game with that PIN", status=404)
        return room

    def clear(self) -> None:
        with self.lock:
            self.rooms.clear()


registry = Registry()


def create_room(
    db: Session,
    *,
    mode: str,
    question_count: int,
    time_limit: int,
    category: Optional[models.Category],
    rng: Optional[random.Random] = None,
) -> Room:
    rng = rng or random.SystemRandom()
    pool = list(crud.list_items(db, category.id if category else None))
    if not pool:
        raise LiveError("There are no items to ask about here")
    order = list(pool)
    rng.shuffle(order)
    asked = order[: max(1, min(question_count, len(order)))]

    questions = []
    for position, (item, options, photo, picks) in enumerate(
        crud.draw_questions(db, asked, pool, mode, rng), start=1
    ):
        photo_url = crud.image_url(photo.filename) if photo else crud.image_url(item.cover)
        if mode == "inverted":
            choices = []
            for option, pick in zip(options, picks):
                filename = pick.filename if pick else option.cover
                choices.append({"id": option.id, "image_url": crud.image_url(filename)})
        else:
            choices = [{"id": o.id, "name": o.name} for o in options]
        answer = crud.item_payload(item)
        # Reveal the picture that was actually asked about.
        answer["image_url"] = photo_url
        questions.append(
            Question(
                position=position,
                correct_id=item.id,
                image_url=photo_url if mode == "choice" else None,
                prompt=item.name if mode == "inverted" else None,
                choices=choices,
                item=answer,
            )
        )

    now = _now()
    with registry.lock:
        registry.purge(now)
        room = Room(
            pin=registry.new_pin(rng),
            host_token=secrets.token_urlsafe(24),
            mode=mode,
            time_limit=time_limit,
            category_name=category.name if category else None,
            questions=questions,
            created_at=now,
            touched_at=now,
        )
        registry.rooms[room.pin] = room
    return room


# --- what each side is shown ------------------------------------------------------


def _question_public(q: Question) -> dict:
    """The question without its answer."""
    return {
        "position": q.position,
        "image_url": q.image_url,
        "prompt": q.prompt,
        "choices": q.choices,
    }


def _reveal(room: Room) -> Optional[dict]:
    q = room.question
    if q is None or room.phase not in ("reveal", "scoreboard", "finished") or room.closed_at is None:
        return None
    counts = {c["id"]: 0 for c in q.choices}
    for p in room.active_players:
        a = p.answers.get(q.position)
        if a is not None and a.choice_id in counts:
            counts[a.choice_id] += 1
    right = sum(1 for p in room.active_players if (a := p.answers.get(q.position)) and a.correct)
    return {
        "correct_id": q.correct_id,
        "item": q.item,
        "counts": [{"id": cid, "count": n} for cid, n in counts.items()],
        "right_count": right,
    }


def _clock(room: Room, now: float) -> dict:
    return {
        "now": now,
        "starts_at": room.starts_at if room.phase == "question" else None,
        "deadline": room.deadline if room.phase == "question" else None,
        "time_limit": room.time_limit,
    }


def host_view(room: Room, now: float) -> dict:
    standings = room.standings()
    view = {
        "pin": room.pin,
        "phase": room.phase,
        "mode": room.mode,
        "category_name": room.category_name,
        "question_count": len(room.questions),
        "position": room.position,
        "locked": room.locked,
        **_clock(room, now),
        "players": [
            {
                "id": p.id,
                "name": p.name,
                "score": p.score,
                "away": now - p.last_seen > AWAY_SECONDS,
                "answered": room.phase == "question" and room.position in p.answers,
            }
            for p in sorted(room.active_players, key=lambda p: p.joined_at)
        ],
        "answered_count": room.answered_count() if room.position else 0,
        "question": _question_public(room.question) if room.question and room.phase != "lobby" else None,
        "reveal": _reveal(room),
        "leaderboard": [
            {"id": p.id, "name": p.name, "score": p.score, "streak": p.streak}
            for p in standings[: (len(standings) if room.phase == "finished" else LEADERBOARD_SIZE)]
        ],
    }
    return view


def player_view(room: Room, player: Player, now: float) -> dict:
    q = room.question
    answer = player.answers.get(room.position) if room.position else None
    reveal = _reveal(room)
    you = {
        "id": player.id,
        "name": player.name,
        "score": player.score,
        "streak": player.streak,
        "rank": room.rank_of(player),
        "answered_id": answer.choice_id if answer else None,
    }
    if reveal is not None:
        you["result"] = {
            "answered": answer is not None,
            "correct": bool(answer and answer.correct),
            "points": answer.points if answer else 0,
        }
    return {
        "pin": room.pin,
        "phase": room.phase,
        "mode": room.mode,
        "question_count": len(room.questions),
        "position": room.position,
        **_clock(room, now),
        "player_count": len(room.active_players),
        "question": _question_public(q) if q and room.phase == "question" else None,
        "reveal": reveal,
        "you": you,
    }
