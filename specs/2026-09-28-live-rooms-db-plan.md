# Live Rooms in the Database + History of Past Games — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move live classroom game rooms from process memory into the database (so a game survives a restart and the backend can run several workers), then give signed-in teachers a history of their games with standings, CSV export and two replay buttons.

**Architecture:** Three new tables (`live_games`, `live_players`, `live_answers`). The game rules stay in `backend/app/live.py`, reworked from dataclasses to a `Room` object that loads one game's rows per request; every change runs under `lock_game` (`BEGIN IMMEDIATE` on SQLite, `SELECT … FOR UPDATE` on Postgres). History lives in a separate module `backend/app/live_history.py` with its own router under `/api/me/live-games`, and two React screens under `/live/history`.

**Tech Stack:** FastAPI (plain `def` endpoints), SQLAlchemy 2.0 ORM, SQLite (WAL), pytest; React + react-router, vitest, eslint.

**Spec:** [`specs/2026-09-28-live-rooms-db-design.md`](2026-09-28-live-rooms-db-design.md)

## Global Constraints

- Branch `nik/live-rooms-db`; never commit to `main`. Draft PR: int-al-l/chemquiz#2.
- Do not edit or commit `docs/` or `src/demo/data.json` (generated; see CLAUDE.md).
- No SQLite-only SQL: everything must also work with `CHEMQUIZ_DATABASE_URL` pointing at Postgres (partial index via `sqlite_where` + `postgresql_where`; `with_for_update()`).
- Existing `/api/live/...` request and response shapes stay the same; the only addition is the `owned` field in host views.
- All live-game times are floats (epoch seconds) read from `live._now()` (tests replace it with a fake clock).
- `ROOM_IDLE_SECONDS` = 3 hours; "away" after `AWAY_SECONDS` = 8; `last_seen` written at most every 3 s; `touched_at` at most every 60 s.
- "Work on mistakes": an item qualifies when fewer than 80% of active players answered it right; no answer counts as wrong; only questions actually asked count.
- CSV: UTF-8 with BOM, `;` separator, `Place;Name;Score;Correct;Q<n> <item name>...`, marks `+`, `−` (U+2212) or empty; English headers.
- UI copy is English, like the rest of the site.
- Before every push: `npm run lint && npm test` and `cd backend && python -m pytest -q`.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. A student's nickname that starts with `=`, `+`, `-` or `@` ends up in the teacher's CSV — Excel must show it as text, not run it as a formula (test in Task 7).
2. A teacher whose sign-in has expired opens a room — the game must still open, just without being kept (test in Task 4).
3. The server is down past a question's deadline — the first poll after the restart must show the question closed with the right counts (test in Task 5).
4. A player the host removed must not appear in history standings, the CSV or the mistakes count (test in Task 7).
5. An unfinished game (closed mid-way) — its CSV and "Work on mistakes" must only consider questions actually asked (test in Task 7 and Task 8).

## File Structure

| File | Responsibility |
| --- | --- |
| `backend/app/database.py` (modify) | WAL for SQLite files; `begin_write(db)` — open a transaction as the writer |
| `backend/app/models.py` (modify) | `LiveGame`, `LivePlayer`, `LiveAnswer` |
| `backend/app/live.py` (rewrite) | Rules of a running game over the DB rows: `Room`, `open_room`, `create_room`, `poll`, `purge`, `retire`, views |
| `backend/app/routers/live.py` (rewrite) | `/api/live/...` endpoints on top of `live.py` |
| `backend/app/routers/account.py` (modify) | `optional_user` dependency |
| `backend/app/live_history.py` (create) | Past games: `Results`, summaries, standings, CSV, replay |
| `backend/app/routers/live_history.py` (create) | `/api/me/live-games/...` endpoints |
| `backend/app/main.py` (modify) | purge live games at startup; include the history router |
| `backend/tests/test_database.py` (create) | WAL and writer serialisation |
| `backend/tests/test_live_store.py` (create) | table constraints |
| `backend/tests/test_live.py` (modify) | existing scenarios on the DB; owners, archive, PIN reuse |
| `backend/tests/test_live_durable.py` (create) | restart and concurrency |
| `backend/tests/test_live_history.py` (create) | history, CSV, replay |
| `src/api/client.js` (modify) | history calls, CSV fetch |
| `src/live/history.js` + `history.test.js` (create) | plain helpers for the history screens |
| `src/live/LiveHistoryPage.jsx`, `src/live/LiveGamePage.jsx` (create) | the two screens |
| `src/live/components.jsx` (modify) | `SignInToKeep` |
| `src/live/LiveSetupPage.jsx`, `src/live/LiveHostPage.jsx`, `src/pages/ProfilePage.jsx`, `src/App.jsx`, `src/live/live.css` (modify) | links, routes, styles |
| `README.md` (modify) | docs |

---

# Stage 1 — Rooms in the database

### Task 1: SQLite writer lock and WAL

**Files:**
- Modify: `backend/app/database.py`
- Test: `backend/tests/test_database.py`

**Interfaces:**
- Produces: `app.database.begin_write(db: Session) -> None` — call first in a transaction that will read-then-write; on SQLite issues `BEGIN IMMEDIATE` (no-op on other databases, and when the driver is already in a transaction). A `connect` listener puts every SQLite connection in WAL mode.

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_database.py`:

```python
"""The SQLite settings the live game relies on when several processes share
one database file."""

from __future__ import annotations

import os
import tempfile
import threading
import time
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import begin_write


@pytest.fixture()
def factory():
    handle, path = tempfile.mkstemp(suffix=".db")
    os.close(handle)
    engine = create_engine(f"sqlite:///{path}", connect_args={"check_same_thread": False})
    with engine.begin() as conn:
        conn.exec_driver_sql("CREATE TABLE counter (n INTEGER)")
        conn.exec_driver_sql("INSERT INTO counter VALUES (0)")
    yield sessionmaker(bind=engine)
    engine.dispose()
    for suffix in ("", "-wal", "-shm"):
        Path(path + suffix).unlink(missing_ok=True)


def test_sqlite_files_use_wal(factory):
    with factory() as db:
        assert db.execute(text("PRAGMA journal_mode")).scalar() == "wal"


def test_writers_take_turns(factory):
    """Read-then-write from many threads at once loses no update."""

    def bump():
        with factory() as db:
            begin_write(db)
            n = db.execute(text("SELECT n FROM counter")).scalar()
            time.sleep(0.01)  # widen the window a lost update would need
            db.execute(text("UPDATE counter SET n = :n"), {"n": n + 1})
            db.commit()

    threads = [threading.Thread(target=bump) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    with factory() as db:
        assert db.execute(text("SELECT n FROM counter")).scalar() == 10
```

- [ ] **Step 2: Run to verify they fail**

Run: `cd backend && python -m pytest tests/test_database.py -q`
Expected: FAIL — `ImportError: cannot import name 'begin_write'`.

- [ ] **Step 3: Implement**

Replace `backend/app/database.py` with:

```python
"""SQLAlchemy engine, session factory and declarative base."""

import sqlite3
from collections.abc import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import DATABASE_URL

# check_same_thread is a SQLite-only quirk: FastAPI serves requests from a
# thread pool, and without this SQLite refuses connections reused across
# threads. It is ignored by every other driver.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


@event.listens_for(Engine, "connect")
def _sqlite_wal(dbapi_connection, _record) -> None:
    """Put SQLite files in WAL mode, so readers never wait for the writer.

    Live games are polled every second by every phone while answers are being
    written, possibly from several backend processes sharing the file. Other
    databases are left alone.
    """
    if isinstance(dbapi_connection, sqlite3.Connection):
        dbapi_connection.execute("PRAGMA journal_mode=WAL")


def begin_write(db: Session) -> None:
    """Open this session's transaction as a writer, before it reads.

    A read-check-write sequence (is the question still open? then record the
    answer) is only safe if nobody writes in between. Postgres gets that from
    `SELECT ... FOR UPDATE`, which the caller adds to its query. SQLite has no
    row locks, so the transaction starts with BEGIN IMMEDIATE: one writer for
    the whole file at a time, which is plenty for writes this small.

    Call it before anything else in the transaction has written.
    """
    connection = db.connection()
    if connection.dialect.name != "sqlite":
        return
    raw = connection.connection.dbapi_connection
    if not raw.in_transaction:
        connection.exec_driver_sql("BEGIN IMMEDIATE")


def get_db() -> Iterator[Session]:
    """FastAPI dependency yielding a request-scoped session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 4: Run to verify they pass, and nothing else broke**

Run: `cd backend && python -m pytest -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add backend/app/database.py backend/tests/test_database.py
git commit -m "SQLite in WAL mode, and begin_write for read-check-write transactions

Groundwork for keeping live games in the database: several backend
processes can then share the file, and a transaction that must not be
interleaved opens as the writer (BEGIN IMMEDIATE on SQLite).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: The three live-game tables

**Files:**
- Modify: `backend/app/models.py` (imports at top; module docstring; append three classes at the end)
- Test: `backend/tests/test_live_store.py`

**Interfaces:**
- Produces: `models.LiveGame`, `models.LivePlayer`, `models.LiveAnswer` with exactly these columns:
  - `LiveGame`: `id`, `pin: Optional[str]`, `host_token: str`, `host_user_id: Optional[int]`, `mode: str`, `time_limit: int`, `question_count: int`, `category_id: Optional[int]`, `category_slug: Optional[str]`, `category_name: Optional[str]`, `questions: list[dict]` (JSON), `phase: str`, `position: int`, `starts_at`, `deadline`, `closed_at: Optional[float]`, `locked: bool`, `created_at: float`, `touched_at: float`, `started_at: Optional[float]`, `finished_at: Optional[float]`.
  - `LivePlayer`: `id`, `game_id`, `token`, `name`, `joined_at`, `last_seen`, `score`, `streak`, `removed`.
  - `LiveAnswer`: `id`, `game_id`, `player_id`, `position`, `choice_id`, `elapsed`, `correct`, `points`.
  - No ORM relationships: `live.py` loads rows with explicit queries. Always pass every column when constructing (ORM defaults only apply at flush).

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_live_store.py`:

```python
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
```

- [ ] **Step 2: Run to verify they fail**

Run: `cd backend && python -m pytest tests/test_live_store.py -q`
Expected: FAIL — `AttributeError: module 'app.models' has no attribute 'LiveGame'`.

- [ ] **Step 3: Implement**

In `backend/app/models.py`, extend the module docstring (after the accounts paragraph) with:

```python
Live classroom games live in LiveGame, LivePlayer and LiveAnswer (the rules
are in app/live.py). A game hosted while signed in stays after it ends, as the
host's history.
```

Change the sqlalchemy import to:

```python
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
```

Append at the end of the file:

```python
class LiveGame(Base):
    """A live classroom game (the rules are in `app/live.py`).

    `pin` is how the class finds the game while it runs. It is cleared when the
    game is archived, so the six digits can go to a new game; the partial
    unique index keeps PINs unique among games that still have one, even when
    two backend processes create games at the same moment.

    `questions` is frozen when the game is created -- what the board shows, the
    options, which one is right, and the card revealed afterwards -- so a game
    in someone's history reads the same after the content changes.

    Times are epoch seconds, the clock `live._now()` reads.
    """

    __tablename__ = "live_games"
    __table_args__ = (
        Index(
            "uq_live_games_pin",
            "pin",
            unique=True,
            sqlite_where=text("pin IS NOT NULL"),
            postgresql_where=text("pin IS NOT NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    pin: Mapped[Optional[str]] = mapped_column(String(6), default=None)
    host_token: Mapped[str] = mapped_column(String(43), unique=True)
    # Null when the host was not signed in; such games are never kept.
    host_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), default=None, index=True
    )

    # "choice" or "inverted", as in QuizSession.
    mode: Mapped[str] = mapped_column(String(16))
    time_limit: Mapped[int] = mapped_column(Integer)
    question_count: Mapped[int] = mapped_column(Integer)
    # A null slug means the game drew from the whole library.
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), default=None
    )
    category_slug: Mapped[Optional[str]] = mapped_column(String(80), default=None)
    category_name: Mapped[Optional[str]] = mapped_column(String(160), default=None)
    questions: Mapped[list] = mapped_column(JSON)

    phase: Mapped[str] = mapped_column(String(16), default="lobby")
    position: Mapped[int] = mapped_column(Integer, default=0)
    starts_at: Mapped[Optional[float]] = mapped_column(Float, default=None)
    deadline: Mapped[Optional[float]] = mapped_column(Float, default=None)
    closed_at: Mapped[Optional[float]] = mapped_column(Float, default=None)
    locked: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[float] = mapped_column(Float)
    touched_at: Mapped[float] = mapped_column(Float)
    started_at: Mapped[Optional[float]] = mapped_column(Float, default=None)
    finished_at: Mapped[Optional[float]] = mapped_column(Float, default=None)


class LivePlayer(Base):
    """A phone in a live game, known by a nickname and a secret token."""

    __tablename__ = "live_players"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(
        ForeignKey("live_games.id", ondelete="CASCADE"), index=True
    )
    token: Mapped[str] = mapped_column(String(43), unique=True)
    name: Mapped[str] = mapped_column(String(40))
    joined_at: Mapped[float] = mapped_column(Float)
    last_seen: Mapped[float] = mapped_column(Float)
    score: Mapped[int] = mapped_column(Integer, default=0)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    # Removed by the host: kept, but left out of everything anyone is shown.
    removed: Mapped[bool] = mapped_column(Boolean, default=False)


class LiveAnswer(Base):
    """One player's answer to one question.

    The unique constraint has the last word on "you have already answered":
    whichever backend process a second tap reaches, the database refuses it.
    """

    __tablename__ = "live_answers"
    __table_args__ = (
        UniqueConstraint("player_id", "position", name="uq_live_answer_once"),
        Index("ix_live_answers_game_position", "game_id", "position"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("live_games.id", ondelete="CASCADE"))
    player_id: Mapped[int] = mapped_column(ForeignKey("live_players.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer)
    choice_id: Mapped[int] = mapped_column(Integer)
    elapsed: Mapped[float] = mapped_column(Float)
    correct: Mapped[bool] = mapped_column(Boolean)
    points: Mapped[int] = mapped_column(Integer)
```

- [ ] **Step 4: Run to verify they pass**

Run: `cd backend && python -m pytest -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add backend/app/models.py backend/tests/test_live_store.py
git commit -m "Tables for live games, players and answers

A partial unique index keeps PINs unique among games that still have
one; a unique (player, question) pair refuses a second answer whichever
process it reaches.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Run the game on the database

**Files:**
- Rewrite: `backend/app/live.py`
- Rewrite: `backend/app/routers/live.py`
- Modify: `backend/app/main.py` (lifespan)
- Modify: `backend/tests/test_live.py` (helpers + one new test)

**Interfaces:**
- Consumes: `begin_write` (Task 1); `models.LiveGame/LivePlayer/LiveAnswer` (Task 2).
- Produces (used by Tasks 4–8):
  - `live.LiveError(message, status=409)`; `live._now() -> float`; the tuning constants (unchanged) plus `SEEN_EVERY_SECONDS = 3`, `TOUCH_EVERY_SECONDS = 60`.
  - `live.Room(db, game)` with `.game`, `.players`, `.answers: dict[player_id, LiveAnswer]` (current question), `.active_players`, `.question -> Optional[dict]`, `.player_by_token(token)`, `.standings()`, `.rank_of(p)`, `.answered_count()`, `.due(now)`, `.tick(now)`, `.start(now)`, `.advance(now)`, `.finish(now)`, `.join(name, now) -> LivePlayer`, `.answer(player, position, choice_id, now) -> LiveAnswer`, `.remove(player_id, now)`.
  - `live.find_game(db, pin, *, lock=False) -> LiveGame`; `live.open_room(db, pin, *, lock=False) -> Room`; `live.poll(db, room, now) -> Room`; `live.check_host(room, token)`; `live.mark_seen(db, room, player, now)`; `live.mark_touched(db, room, now)`.
  - `live.create_room(db, *, mode, question_count, time_limit, category, host_user=None, items=None, rng=None) -> Room` (caller builds its reply, then commits).
  - `live.purge(db, now=None)` (commits); `live.keeps(game) -> bool`; `live.retire(db, game)`; `live.delete_game(db, game_id)`.
  - `live.host_view(room, now) -> dict`; `live.player_view(room, player, now) -> dict`.
  - Test helpers in `test_live.py`: `Clock`, `clock` fixture, `host(token)`, `make_room(client, headers=None, **kw)`, `join(client, pin, name)`, `correct_id(client, pin, position)`, `SamePins`.

- [ ] **Step 1: Update the test helpers and add the PIN-retry test**

In `backend/tests/test_live.py`:

Replace the imports block with:

```python
from __future__ import annotations

import random

import pytest
from sqlalchemy import select

from app import live, models
from test_api import client  # noqa: F401 -- the seeded test app
```

Replace the `clock` fixture with (the registry is gone; each test already gets a fresh database):

```python
@pytest.fixture()
def clock(monkeypatch):
    c = Clock()
    monkeypatch.setattr(live, "_now", c)
    yield c
```

Replace `make_room` and `correct_id` with:

```python
def make_room(client, headers=None, **kw):
    body = {"category_slug": "condensers", "mode": "choice", "question_count": 3, "time_limit": 20}
    body.update(kw)
    res = client.post("/api/live", json=body, headers=headers or {})
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
```

Then change every call `correct_id(pin, N)` in the file to `correct_id(client, pin, N)` (four places: in `test_full_game` twice plus the late-answer line, and in `test_removing_last_answerer_closes_question`).

Append:

```python
def test_a_taken_pin_is_skipped(client, clock):
    first = make_room(client)
    with client.session_factory() as db:
        room = live.create_room(
            db, mode="choice", question_count=1, time_limit=20, category=None,
            rng=SamePins([first["pin"], "654321"]),
        )
        db.commit()
        assert room.game.pin == "654321"
```

- [ ] **Step 2: Run to verify they fail**

Run: `cd backend && python -m pytest tests/test_live.py -q`
Expected: FAIL — `correct_id` finds no `LiveGame` row (`NoResultFound`), and `create_room` has no `host_user`/DB-backed `Room`.

- [ ] **Step 3: Rewrite `backend/app/live.py`**

Replace the whole file with:

```python
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

from . import crud, models
from .database import begin_write

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


class LiveError(Exception):
    """A request the game cannot accept. `status` is the HTTP status to send."""

    def __init__(self, message: str, status: int = 409):
        super().__init__(message)
        self.status = status


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
            raise LiveError("The game has already started")
        if not self.active_players:
            raise LiveError("Wait for at least one player to join")
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
            raise LiveError("The game is over")

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
        game.deadline = game.starts_at + game.time_limit
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
        raise LiveError("No such player", status=404)

    # -- player actions --

    def join(self, name: str, now: float) -> models.LivePlayer:
        game = self.game
        if game.phase == "finished":
            raise LiveError("This game has finished")
        if game.locked:
            raise LiveError("The host has locked this game")
        clean = clean_name(name)
        taken = {p.name.casefold() for p in self.active_players}
        if clean.casefold() in taken:
            raise LiveError("Someone already has that name -- pick another")
        if len(self.active_players) >= MAX_PLAYERS:
            raise LiveError("The room is full")
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
        self, player: models.LivePlayer, position: int, choice_id: int, now: float
    ) -> models.LiveAnswer:
        self.tick(now)
        game = self.game
        question = self.question
        if game.phase != "question" or question is None or position != game.position:
            raise LiveError("Too late -- this question is closed")
        if now < (game.starts_at or 0):
            raise LiveError("Answers are not open yet")
        if player.id in self.answers:
            raise LiveError("You have already answered")
        if choice_id not in {c["id"] for c in question["choices"]}:
            raise LiveError("That is not one of the options", status=422)

        elapsed = max(0.0, min(now - game.starts_at, float(game.time_limit)))
        correct = choice_id == question["correct_id"]
        points = 0
        if correct:
            player.streak += 1
            fraction = elapsed / game.time_limit
            points = round(MAX_POINTS - (MAX_POINTS - MIN_POINTS) * fraction)
            points += min((player.streak - 1) * STREAK_BONUS, STREAK_BONUS_CAP)
        else:
            player.streak = 0
        player.score += points

        answer = models.LiveAnswer(
            game_id=game.id,
            player_id=player.id,
            position=position,
            choice_id=choice_id,
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
        raise LiveError("Type a name", status=422)
    if len(clean) > NAME_MAX:
        raise LiveError(f"Names can be at most {NAME_MAX} characters", status=422)
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
        raise LiveError("No game with that PIN", status=404)
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
        raise LiveError("No game with that PIN", status=404)
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
        raise LiveError("Only the host can do that", status=403)


def mark_seen(db: Session, room: Room, player: models.LivePlayer, now: float) -> None:
    """Note that this phone is still here -- at most every few seconds."""
    if now - player.last_seen >= SEEN_EVERY_SECONDS:
        db.execute(
            update(models.LivePlayer)
            .where(models.LivePlayer.id == player.id)
            .values(last_seen=now)
        )
    mark_touched(db, room, now)


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
) -> Room:
    """Draw the questions and open a room for them.

    `items` fixes which items are asked (work on mistakes); otherwise
    `question_count` of the deck's items are drawn at random. The caller
    builds its reply from the returned room, then commits.
    """
    rng = rng or random.SystemRandom()
    pool = list(crud.list_items(db, category.id if category else None))
    if not pool:
        raise LiveError("There are no items to ask about here")
    if items is None:
        asked = list(pool)
        rng.shuffle(asked)
        asked = asked[: max(1, min(question_count, len(asked)))]
    else:
        asked = list(items)
        rng.shuffle(asked)
    questions = _draw(db, asked, pool, mode, rng)

    # Read everything needed from these objects now: the purge commits, and
    # a commit expires them.
    settings = dict(
        host_user_id=host_user.id if host_user else None,
        mode=mode,
        time_limit=time_limit,
        question_count=len(questions),
        category_id=category.id if category else None,
        category_slug=category.slug if category else None,
        category_name=category.name if category else None,
        questions=questions,
    )
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
    raise LiveError("No free room codes right now", status=503)


def _draw(db: Session, asked, pool, mode: str, rng: random.Random) -> list[dict]:
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
            choices = [{"id": o.id, "name": o.name} for o in options]
        answer = crud.item_payload(item)
        # Reveal the picture that was actually asked about.
        answer["image_url"] = photo_url
        questions.append(
            {
                "position": position,
                "correct_id": item.id,
                "image_url": photo_url if mode == "choice" else None,
                "prompt": item.name if mode == "inverted" else None,
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
    return {
        "position": q["position"],
        "image_url": q["image_url"],
        "prompt": q["prompt"],
        "choices": q["choices"],
    }


def _reveal(room: Room) -> Optional[dict]:
    game = room.game
    q = room.question
    if q is None or game.phase not in ("reveal", "scoreboard", "finished") or game.closed_at is None:
        return None
    counts = {c["id"]: 0 for c in q["choices"]}
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
        "correct_id": q["correct_id"],
        "item": q["item"],
        "counts": [{"id": cid, "count": n} for cid, n in counts.items()],
        "right_count": right,
    }


def _clock(room: Room, now: float) -> dict:
    game = room.game
    return {
        "now": now,
        "starts_at": game.starts_at if game.phase == "question" else None,
        "deadline": game.deadline if game.phase == "question" else None,
        "time_limit": game.time_limit,
    }


def host_view(room: Room, now: float) -> dict:
    game = room.game
    standings = room.standings()
    return {
        "pin": game.pin,
        "phase": game.phase,
        "mode": game.mode,
        "category_name": game.category_name,
        "question_count": len(game.questions),
        "position": game.position,
        "locked": game.locked,
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
    }
    if reveal is not None:
        you["result"] = {
            "answered": answer is not None,
            "correct": bool(answer and answer.correct),
            "points": answer.points if answer else 0,
        }
    return {
        "pin": game.pin,
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
```

- [ ] **Step 4: Rewrite `backend/app/routers/live.py`**

Replace the whole file with:

```python
"""Live classroom game endpoints (see app/live.py for the rules).

The host and each player hold a secret token, sent in the X-Live-Token
header. The PIN only finds the room; it grants nothing on its own.

Each endpoint builds its reply before it commits: after a commit, every row
would be read again one at a time.
"""

from __future__ import annotations

import socket
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import crud, live, models
from ..config import MAX_QUESTION_COUNT, QUIZ_MODES
from ..database import get_db

router = APIRouter(prefix="/api/live", tags=["live"])


class CreateIn(BaseModel):
    category_slug: Optional[str] = None
    mode: str = "choice"
    question_count: int = Field(10, ge=1, le=MAX_QUESTION_COUNT)
    time_limit: int = live.DEFAULT_TIME_LIMIT


class JoinIn(BaseModel):
    name: str = Field(..., max_length=200)


class AnswerIn(BaseModel):
    position: int
    choice_id: int


class LockIn(BaseModel):
    locked: bool


def _fail(db: Session, exc: live.LiveError) -> HTTPException:
    """Undo whatever the request started, and say why."""
    db.rollback()
    return HTTPException(status_code=exc.status, detail=str(exc))


@router.get("/network")
def network():
    """This machine's addresses on the local network.

    A teacher who opens the site as http://localhost cannot hand that address
    to the class; the board uses these to show one the phones can reach.
    """
    addresses: list[str] = []
    try:
        # No packet is sent: connecting a UDP socket only picks the interface
        # that would be used, which is the one facing the local network.
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))
            addresses.append(s.getsockname()[0])
    except OSError:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if ip not in addresses:
                addresses.append(ip)
    except OSError:
        pass
    return {"addresses": [a for a in addresses if not a.startswith("127.")]}


@router.post("", status_code=201)
def create(payload: CreateIn, db: Session = Depends(get_db)):
    if payload.mode not in QUIZ_MODES:
        raise HTTPException(status_code=422, detail=f"Unknown mode '{payload.mode}'")
    if payload.time_limit not in live.TIME_LIMITS:
        raise HTTPException(status_code=422, detail="Unsupported time limit")
    category = None
    if payload.category_slug:
        category = crud.get_category_by_slug(db, payload.category_slug)
        if category is None:
            raise HTTPException(status_code=404, detail=f"No category '{payload.category_slug}'")
    try:
        room = live.create_room(
            db,
            mode=payload.mode,
            question_count=payload.question_count,
            time_limit=payload.time_limit,
            category=category,
        )
    except live.LiveError as exc:
        raise _fail(db, exc) from exc
    view = {"host_token": room.game.host_token, **live.host_view(room, live._now())}
    db.commit()
    return view


@router.get("/{pin}")
def peek(pin: str, db: Session = Depends(get_db)):
    """Is there a game with this PIN, and can it still be joined?"""
    try:
        room = live.open_room(db, pin)
    except live.LiveError as exc:
        raise _fail(db, exc) from exc
    game = room.game
    return {
        "pin": game.pin,
        "phase": game.phase,
        "joinable": game.phase != "finished" and not game.locked,
        "player_count": len(room.active_players),
    }


# --- host -----------------------------------------------------------------------


@router.get("/{pin}/host")
def host_state(pin: str, x_live_token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    now = live._now()
    try:
        room = live.open_room(db, pin)
        live.check_host(room, x_live_token)
        room = live.poll(db, room, now)
    except live.LiveError as exc:
        raise _fail(db, exc) from exc
    view = live.host_view(room, now)
    live.mark_touched(db, room, now)
    db.commit()
    return view


def _host_action(pin: str, token: Optional[str], db: Session, action):
    now = live._now()
    try:
        room = live.open_room(db, pin, lock=True)
        live.check_host(room, token)
        room.game.touched_at = now
        action(room, now)
        db.flush()
    except live.LiveError as exc:
        raise _fail(db, exc) from exc
    view = live.host_view(room, now)
    db.commit()
    return view


@router.post("/{pin}/next")
def host_next(pin: str, x_live_token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    return _host_action(pin, x_live_token, db, lambda room, now: room.advance(now))


@router.post("/{pin}/finish")
def host_finish(pin: str, x_live_token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    return _host_action(pin, x_live_token, db, lambda room, now: room.finish(now))


@router.post("/{pin}/lock")
def host_lock(
    pin: str, payload: LockIn, x_live_token: Optional[str] = Header(None), db: Session = Depends(get_db)
):
    def lock(room, now):
        room.game.locked = payload.locked

    return _host_action(pin, x_live_token, db, lock)


@router.post("/{pin}/players/{player_id}/remove")
def host_remove(
    pin: str, player_id: int, x_live_token: Optional[str] = Header(None), db: Session = Depends(get_db)
):
    return _host_action(pin, x_live_token, db, lambda room, now: room.remove(player_id, now))


@router.delete("/{pin}", status_code=204)
def host_close(pin: str, x_live_token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Close the room: into the host's history if it is kept, otherwise gone."""
    try:
        room = live.open_room(db, pin, lock=True)
        live.check_host(room, x_live_token)
    except live.LiveError as exc:
        raise _fail(db, exc) from exc
    live.retire(db, room.game)
    db.commit()
    return None


# --- players ----------------------------------------------------------------------


def _player(room: live.Room, token: Optional[str]) -> models.LivePlayer:
    player = room.player_by_token(token)
    if player is None:
        raise live.LiveError("You are not in this game", status=403)
    if player.removed:
        raise live.LiveError("The host removed you from this game", status=410)
    return player


@router.post("/{pin}/join", status_code=201)
def join(pin: str, payload: JoinIn, db: Session = Depends(get_db)):
    now = live._now()
    try:
        room = live.open_room(db, pin, lock=True)
        player = room.join(payload.name, now)
        room.game.touched_at = now
        db.flush()
    except live.LiveError as exc:
        raise _fail(db, exc) from exc
    view = {"token": player.token, **live.player_view(room, player, now)}
    db.commit()
    return view


@router.get("/{pin}/me")
def player_state(pin: str, x_live_token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    now = live._now()
    try:
        room = live.open_room(db, pin)
        player = _player(room, x_live_token)
        room = live.poll(db, room, now)
    except live.LiveError as exc:
        raise _fail(db, exc) from exc
    view = live.player_view(room, player, now)
    live.mark_seen(db, room, player, now)
    db.commit()
    return view


@router.post("/{pin}/answer")
def answer(
    pin: str, payload: AnswerIn, x_live_token: Optional[str] = Header(None), db: Session = Depends(get_db)
):
    now = live._now()
    try:
        room = live.open_room(db, pin, lock=True)
        player = _player(room, x_live_token)
        player.last_seen = now
        room.answer(player, payload.position, payload.choice_id, now)
        room.game.touched_at = now
        db.flush()
    except live.LiveError as exc:
        raise _fail(db, exc) from exc
    except IntegrityError as exc:
        # The database's own guard against a second answer (see LiveAnswer).
        db.rollback()
        raise HTTPException(status_code=409, detail="You have already answered") from exc
    view = live.player_view(room, player, now)
    db.commit()
    return view
```

- [ ] **Step 5: Purge live games at startup**

In `backend/app/main.py`, add after the other `from . import ...` line:

```python
from .live import purge as purge_live_games
```

and in `lifespan`, right after `crud.purge_stale_sessions(db)`:

```python
        purge_live_games(db)
```

- [ ] **Step 6: Run the whole backend suite**

Run: `cd backend && python -m pytest -q`
Expected: all pass, including the 9 original `test_live.py` scenarios and `test_a_taken_pin_is_skipped`.

- [ ] **Step 7: Commit**

```bash
git add backend/app/live.py backend/app/routers/live.py backend/app/main.py backend/tests/test_live.py
git commit -m "Run live games on the database instead of process memory

The rules keep their shape but work on LiveGame/LivePlayer/LiveAnswer
rows, loaded per request. Every change locks the game first; polls only
read, apart from closing a question whose time is up and noting who is
still there (at most every 3 s). The in-memory registry is gone.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Signed-in hosts own their games; closing keeps them

**Files:**
- Modify: `backend/app/routers/account.py` (add `optional_user` after `current_user`)
- Modify: `backend/app/routers/live.py` (`create`)
- Modify: `backend/app/live.py` (`host_view`)
- Test: `backend/tests/test_live.py` (append)

**Interfaces:**
- Consumes: `live.create_room(..., host_user=...)`, `live.retire`, `live.purge` (Task 3).
- Produces: `routers.account.optional_user(db, authorization) -> Optional[models.User]` (read-only); host views gain `"owned": bool`; test helpers `teacher(client) -> dict` (auth headers), `stored(client, **where) -> list[LiveGame]`, `start_one_question(client, room)`.

- [ ] **Step 1: Write the failing tests**

In `backend/tests/test_live.py`, add to the imports:

```python
from sqlalchemy import func
from test_api import auth, sign_in
```

Append:

```python
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
```

- [ ] **Step 2: Run to verify they fail**

Run: `cd backend && python -m pytest tests/test_live.py -q`
Expected: FAIL — `KeyError: 'owned'`, and the kept games are deleted instead of archived.

- [ ] **Step 3: Implement**

In `backend/app/routers/account.py`, right after `current_user`, add:

```python
def optional_user(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
) -> models.User | None:
    """The signed-in user, or None -- never a refusal.

    For endpoints anyone may use, where signing in only adds something (a
    class game goes into the host's history). A stale token simply counts as
    signed out. Read-only, unlike `current_user`.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    user = db.execute(
        select(models.User).where(models.User.token == token)
    ).scalar_one_or_none()
    if user is None or not user.email_verified:
        return None
    return user
```

In `backend/app/routers/live.py`, add the import:

```python
from .account import optional_user
```

and change `create`'s signature and the `create_room` call:

```python
@router.post("", status_code=201)
def create(
    payload: CreateIn,
    db: Session = Depends(get_db),
    user: Optional[models.User] = Depends(optional_user),
):
```

```python
        room = live.create_room(
            db,
            mode=payload.mode,
            question_count=payload.question_count,
            time_limit=payload.time_limit,
            category=category,
            host_user=user,
        )
```

In `backend/app/live.py`, `host_view`, add after `"locked": game.locked,`:

```python
        # Signed in when the room was opened: the game goes into their history.
        "owned": game.host_user_id is not None,
```

- [ ] **Step 4: Run to verify they pass**

Run: `cd backend && python -m pytest -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add backend/app/routers/account.py backend/app/routers/live.py backend/app/live.py backend/tests/test_live.py
git commit -m "Signed-in hosts own their class games; closing or idling archives them

A game opened while signed in records its host; once it has got past
the lobby, closing the room or the 3-hour purge only releases the PIN.
Everything else is deleted as before. Host views say whether the game
is owned.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Prove restarts and several processes are safe; update docs

**Files:**
- Create: `backend/tests/test_live_durable.py`
- Modify: `README.md` (the paragraph "Rooms live in the backend's memory…")

**Interfaces:**
- Consumes: `live.open_room`, `Room.answer`, `Room.advance`, `live.create_room` (Task 3); helpers from `test_live.py`.

- [ ] **Step 1: Write the tests**

Create `backend/tests/test_live_durable.py`:

```python
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
                r.answer(r.player_by_token(players["Ann"]["token"]), 1, right, clock())
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
                r.answer(r.player_by_token(players["Bob"]["token"]), 1, right, clock())
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
```

- [ ] **Step 2: Run them**

Run: `cd backend && python -m pytest tests/test_live_durable.py -q`
Expected: all pass (Tasks 1–3 already provide the behaviour; these tests pin it down). If `test_next_racing_an_answer_leaves_scores_consistent` or `test_two_games_created_at_once_get_different_pins` fails, a write path is missing `lock=True` / `begin_write` — fix there, not in the test.

- [ ] **Step 3: Update README and run the full suite**

In `README.md`, replace the paragraph:

```
Rooms live in the backend's memory (`backend/app/live.py`), so run it as a
single process (no `--workers`); restarting it ends the game. The browser-only
demo on GitHub Pages cannot connect phones, so it explains that instead.
```

with:

```
Games are kept in the database, so restarting the backend is only a pause:
the board and the phones pick the game up again by themselves. The backend
can also run as several processes (`uvicorn app.main:app --workers 4`). The
browser-only demo on GitHub Pages cannot connect phones, so it explains that
instead.
```

Run: `cd backend && python -m pytest -q`
Expected: all pass.

- [ ] **Step 4: Commit**

```bash
git add backend/tests/test_live_durable.py README.md
git commit -m "Tests: a live game survives a restart and races between processes

Covers a restart mid-question, a deadline passing while the server is
down, a double tap, Next racing an answer, and two games created at once.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

# Stage 2 — History of past games

### Task 6: History list, detail and delete

**Files:**
- Create: `backend/app/live_history.py`
- Create: `backend/app/routers/live_history.py`
- Modify: `backend/app/main.py` (import and include the router)
- Test: `backend/tests/test_live_history.py`

**Interfaces:**
- Consumes: `live.delete_game`, `live.keeps` (Task 3); `routers.account.current_user`; `database.begin_write`.
- Produces:
  - `live_history.status(game) -> "live" | "finished" | "unfinished"`; `live_history.asked(game) -> list[dict]`.
  - `live_history.Results(db, game)` with `.players` (active, standings order), `.answers: dict[player_id, dict[position, LiveAnswer]]`, `.correct_count(player)`, `.mistake_item_ids() -> list[int]`.
  - `live_history.summary(db, game) -> dict` with keys `id, played_at, category_name, mode, question_count, asked_count, player_count, winner, status, has_mistakes`; `live_history.detail(db, game)` = summary + `time_limit`, `standings: [{place, id, name, score, correct}]`.
  - Router `/api/me/live-games` with `_own_game(db, user, game_id, lock=False) -> LiveGame`.
  - Test helpers `play(client, clock, players, script, headers=None, finish=True) -> (room, joined)` and `only_game(client, headers) -> dict`.

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_live_history.py`:

```python
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
```

- [ ] **Step 2: Run to verify they fail**

Run: `cd backend && python -m pytest tests/test_live_history.py -q`
Expected: FAIL — 404 on `/api/me/live-games` (no such route).

- [ ] **Step 3: Implement `backend/app/live_history.py`**

```python
"""A teacher's past class games: the list, the standings, a CSV of the
results, and what to play next.

Only games hosted while signed in, and that got past the lobby, are kept
(see `live.keeps`); these are the same rows the game was played on.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models

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
```

- [ ] **Step 4: Implement `backend/app/routers/live_history.py`**

```python
"""A signed-in teacher's past class games (see app/live_history.py).

Another teacher's game, or one that never left the lobby, answers 404 as if
it did not exist.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import live, live_history, models
from ..database import begin_write, get_db
from .account import current_user

router = APIRouter(prefix="/api/me/live-games", tags=["live"])


def _own_game(db: Session, user: models.User, game_id: int, lock: bool = False) -> models.LiveGame:
    if lock:
        begin_write(db)
    stmt = select(models.LiveGame).where(
        models.LiveGame.id == game_id,
        models.LiveGame.host_user_id == user.id,
        models.LiveGame.started_at.is_not(None),
    )
    if lock:
        stmt = stmt.with_for_update()
    game = db.scalars(stmt).first()
    if game is None:
        raise HTTPException(status_code=404, detail="No such game")
    return game


@router.get("")
def list_games(user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    games = db.scalars(
        select(models.LiveGame)
        .where(
            models.LiveGame.host_user_id == user.id,
            models.LiveGame.started_at.is_not(None),
        )
        .order_by(models.LiveGame.started_at.desc(), models.LiveGame.id.desc())
    ).all()
    return [live_history.summary(db, g) for g in games]


@router.get("/{game_id}")
def get_game(game_id: int, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    return live_history.detail(db, _own_game(db, user, game_id))


@router.delete("/{game_id}", status_code=204)
def remove_game(game_id: int, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    game = _own_game(db, user, game_id, lock=True)
    if live_history.status(game) == "live":
        db.rollback()
        raise HTTPException(status_code=409, detail="Finish the game first")
    live.delete_game(db, game.id)
    db.commit()
    return None
```

In `backend/app/main.py`, change the routers import and include the new router:

```python
from .routers import account, content, live, live_history, quiz
```

```python
app.include_router(live_history.router)
```

(after `app.include_router(live.router)`).

- [ ] **Step 5: Run to verify they pass**

Run: `cd backend && python -m pytest -q`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add backend/app/live_history.py backend/app/routers/live_history.py backend/app/main.py backend/tests/test_live_history.py
git commit -m "History of past class games: list, standings, delete

/api/me/live-games lists a signed-in teacher's games that got past the
lobby, newest first, with standings per game. A game still being played
cannot be deleted.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: Results as a CSV file

**Files:**
- Modify: `backend/app/live_history.py` (append)
- Modify: `backend/app/routers/live_history.py` (append endpoint)
- Test: `backend/tests/test_live_history.py` (append)

**Interfaces:**
- Consumes: `Results`, `asked` (Task 6).
- Produces: `live_history.results_csv(db, game) -> str` (BOM included); `live_history.csv_filename(game) -> str`; `GET /api/me/live-games/{id}/results.csv`.

- [ ] **Step 1: Write the failing tests**

Append to `backend/tests/test_live_history.py`:

```python
def csv_rows(client, headers, game_id):
    res = client.get(f"/api/me/live-games/{game_id}/results.csv", headers=headers)
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/csv")
    assert 'filename="chemquiz-class-game-' in res.headers["content-disposition"]
    text = res.content.decode("utf-8")
    assert text.startswith("﻿")
    return [line.split(";") for line in text[1:].strip().split("\r\n")]


def test_results_csv(client, clock):
    t = teacher(client)
    room, joined = play(
        client, clock, ["Ann", "=cmd", "Cy", "Dan"],
        [{"Ann": "right", "=cmd": "wrong", "Dan": "right"}, {"Ann": "right"}],
        headers=t,
    )
    # The host removes Dan after the game: he is left out.
    client.post(
        f"/api/live/{room['pin']}/players/{joined['Dan']['you']['id']}/remove",
        headers=host(room["host_token"]),
    )

    rows = csv_rows(client, t, only_game(client, t)["id"])
    assert rows[0][:4] == ["Place", "Name", "Score", "Correct"]
    assert rows[0][4].startswith("Q1 Condenser ") and rows[0][5].startswith("Q2 Condenser ")
    assert rows[1][:2] == ["1", "Ann"] and rows[1][3:] == ["2", "+", "+"]
    # A name a spreadsheet would run as a formula is kept as text.
    assert rows[2][1] == "'=cmd" and rows[2][3:] == ["0", "−", ""]
    assert rows[3][1] == "Cy" and rows[3][3:] == ["0", "", ""]
    assert len(rows) == 4  # Dan is not there


def test_an_unfinished_games_csv_has_only_the_questions_asked(client, clock):
    t = teacher(client)
    room = make_room(client, headers=t, question_count=3)
    pin, token = room["pin"], room["host_token"]
    join(client, pin, "Ann")
    client.post(f"/api/live/{pin}/next", headers=host(token))  # question 1 of 3
    client.delete(f"/api/live/{pin}", headers=host(token))  # closed mid-way

    rows = csv_rows(client, t, only_game(client, t)["id"])
    assert len(rows[0]) == 4 + 1
    assert rows[1][3:] == ["0", ""]
```

- [ ] **Step 2: Run to verify they fail**

Run: `cd backend && python -m pytest tests/test_live_history.py -q -k csv`
Expected: FAIL — 404 (no route).

- [ ] **Step 3: Implement**

Append to `backend/app/live_history.py` (add `import csv`, `import datetime as dt`, `import io` to the imports at the top):

```python
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
```

Append to `backend/app/routers/live_history.py` (add `from fastapi import Response` to the fastapi import):

```python
@router.get("/{game_id}/results.csv")
def results_csv(game_id: int, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    game = _own_game(db, user, game_id)
    return Response(
        content=live_history.results_csv(db, game).encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{live_history.csv_filename(game)}"'},
    )
```

- [ ] **Step 4: Run to verify they pass**

Run: `cd backend && python -m pytest -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add backend/app/live_history.py backend/app/routers/live_history.py backend/tests/test_live_history.py
git commit -m "Download a past class game's results as CSV

One row per student with + / − / blank per question asked; semicolons
and a BOM so Excel opens it directly. Nicknames that a spreadsheet would
run as formulas are written as text.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: Play again — same settings, or work on mistakes

**Files:**
- Modify: `backend/app/live_history.py` (append)
- Modify: `backend/app/routers/live_history.py` (append endpoint)
- Test: `backend/tests/test_live_history.py` (append)

**Interfaces:**
- Consumes: `live.create_room(..., host_user, items)` (Tasks 3–4), `Results.mistake_item_ids` (Task 6).
- Produces: `live_history.replay(db, game, kind, user) -> live.Room`; `POST /api/me/live-games/{id}/replay` `{"kind": "same" | "mistakes"}` → 201, the same body as `POST /api/live`.

- [ ] **Step 1: Write the failing tests**

Append to `backend/tests/test_live_history.py`:

```python
def replay(client, headers, game_id, kind):
    return client.post(f"/api/me/live-games/{game_id}/replay", json={"kind": kind}, headers=headers)


def test_play_again_with_the_same_settings(client, clock):
    t = teacher(client)
    play(client, clock, ["Ann"], [{"Ann": "right"}, {"Ann": "wrong"}], headers=t)
    res = replay(client, t, only_game(client, t)["id"], "same")
    assert res.status_code == 201
    room = res.json()
    assert room["phase"] == "lobby" and room["owned"] is True and room["host_token"]
    assert room["question_count"] == 2 and room["category_name"] == "Condensers"


def test_work_on_mistakes_takes_the_items_under_80_percent(client, clock):
    t = teacher(client)
    five = ["A", "B", "C", "D", "E"]
    room, _ = play(client, clock, five, [
        {"A": "right", "B": "right", "C": "right", "D": "right", "E": "wrong"},  # 80%: fine
        {"A": "right", "B": "right", "C": "right"},  # 60%, two did not answer: a mistake
        {name: "wrong" for name in five},  # 0%: a mistake
    ], headers=t)
    expected = {correct_id(client, room["pin"], 2), correct_id(client, room["pin"], 3)}

    old = only_game(client, t)
    assert old["has_mistakes"] is True
    new = replay(client, t, old["id"], "mistakes").json()

    with client.session_factory() as db:
        game = db.scalars(select(models.LiveGame).where(models.LiveGame.pin == new["pin"])).one()
        assert {q["correct_id"] for q in game.questions} == expected
        assert game.mode == "choice" and game.time_limit == 20
        assert game.category_slug == "condensers"


def test_no_mistakes_nothing_to_replay(client, clock):
    t = teacher(client)
    play(client, clock, ["Ann"], [{"Ann": "right"}], headers=t)
    old = only_game(client, t)
    assert old["has_mistakes"] is False
    assert replay(client, t, old["id"], "mistakes").status_code == 409


def test_mistakes_only_count_questions_that_were_asked(client, clock):
    t = teacher(client)
    room = make_room(client, headers=t, question_count=3)
    pin, token = room["pin"], room["host_token"]
    ann = join(client, pin, "Ann")
    client.post(f"/api/live/{pin}/next", headers=host(token))
    clock.advance(live.READ_SECONDS + 1)
    client.post(
        f"/api/live/{pin}/answer",
        json={"position": 1, "choice_id": correct_id(client, pin, 1)},
        headers=host(ann["token"]),
    )
    client.delete(f"/api/live/{pin}", headers=host(token))  # closed after question 1
    # Questions 2 and 3 were never asked, so they are not mistakes.
    assert only_game(client, t)["has_mistakes"] is False


def test_replaying_a_removed_deck_is_refused(client, clock):
    t = teacher(client)
    play(client, clock, ["Ann"], [{"Ann": "wrong"}], headers=t)
    with client.session_factory() as db:
        # What Postgres's ON DELETE SET NULL leaves when the deck is removed.
        db.execute(update(models.LiveGame).values(category_id=None))
        db.commit()
    game_id = only_game(client, t)["id"]
    assert replay(client, t, game_id, "same").status_code == 409
    assert replay(client, t, game_id, "mistakes").status_code == 409


def test_replay_checks_the_kind_and_the_owner(client, clock):
    t = teacher(client)
    play(client, clock, ["Ann"], [{"Ann": "wrong"}], headers=t)
    game_id = only_game(client, t)["id"]
    assert replay(client, t, game_id, "everything").status_code == 422
    other = auth(sign_in(client, name="Bea", email="bea@example.com").json()["token"])
    assert replay(client, other, game_id, "same").status_code == 404
```

- [ ] **Step 2: Run to verify they fail**

Run: `cd backend && python -m pytest tests/test_live_history.py -q -k "replay or mistakes or again"`
Expected: FAIL — 404/405 (no route), except `test_mistakes_only_count_questions_that_were_asked` and `test_no_mistakes...` parts that only read `has_mistakes`, which may already pass.

- [ ] **Step 3: Implement**

Append to `backend/app/live_history.py` (add `from sqlalchemy.orm import selectinload` and `from . import live` to the imports):

```python
def _deck(db: Session, game: models.LiveGame) -> Optional[models.Category]:
    """The deck to play again from; None means the whole library."""
    if game.category_slug is None:
        return None
    category = db.get(models.Category, game.category_id) if game.category_id else None
    if category is None:
        raise live.LiveError("That deck is no longer on the site")
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
        )
    ids = Results(db, game).mistake_item_ids()
    if not ids:
        raise live.LiveError("The class got every question right -- nothing to go over")
    items = db.scalars(
        select(models.Item)
        .where(models.Item.id.in_(ids))
        .options(selectinload(models.Item.photos), selectinload(models.Item.category))
    ).all()
    if not items:
        raise live.LiveError("Those items are no longer on the site")
    return live.create_room(
        db,
        mode=game.mode,
        question_count=len(items),
        time_limit=game.time_limit,
        category=category,
        host_user=user,
        items=list(items),
    )
```

(also add `from typing import Optional` to the imports).

Append to `backend/app/routers/live_history.py` (add `from typing import Literal` and `from pydantic import BaseModel`):

```python
class ReplayIn(BaseModel):
    kind: Literal["same", "mistakes"]


@router.post("/{game_id}/replay", status_code=201)
def replay(
    game_id: int,
    payload: ReplayIn,
    user: models.User = Depends(current_user),
    db: Session = Depends(get_db),
):
    """Open a new room from a past game; answers like POST /api/live."""
    game = _own_game(db, user, game_id)
    try:
        room = live_history.replay(db, game, payload.kind, user)
    except live.LiveError as exc:
        db.rollback()
        raise HTTPException(status_code=exc.status, detail=str(exc)) from exc
    view = {"host_token": room.game.host_token, **live.host_view(room, live._now())}
    db.commit()
    return view
```

- [ ] **Step 4: Run to verify they pass**

Run: `cd backend && python -m pytest -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add backend/app/live_history.py backend/app/routers/live_history.py backend/tests/test_live_history.py
git commit -m "Play a past class game again: same settings, or work on mistakes

Work on mistakes asks the items fewer than 80% of the class got right
(not answering counts as wrong), among the questions actually asked.
A deck that has since been removed is refused with a clear message.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 9: Frontend API calls and helpers

**Files:**
- Modify: `src/api/client.js` (append after the live-game section)
- Create: `src/live/history.js`
- Test: `src/live/history.test.js`

**Interfaces:**
- Produces: `fetchLiveGames()`, `fetchLiveGame(id)`, `deleteLiveGame(id)`, `replayLiveGame(id, kind)`, `fetchLiveGameCsv(id) -> {blob, filename}` from `src/api/client.js`; `STATUS_LABELS`, `describeGame(game)`, `plural(n, word)`, `playedOn(seconds, locale?)`, `saveFile({blob, filename})` from `src/live/history.js`.

- [ ] **Step 1: Write the failing test**

Create `src/live/history.test.js`:

```js
import { describe, expect, it } from "vitest";

import { describeGame, plural } from "./history";

describe("describeGame", () => {
  it("names the deck, the mode and the counts", () => {
    expect(
      describeGame({ category_name: "Condensers", mode: "choice", question_count: 10, asked_count: 10, player_count: 1 }),
    ).toBe("Condensers · Name it · 10 questions · 1 player");
  });

  it("says Everything for the whole library, and how far an unfinished game got", () => {
    expect(
      describeGame({ category_name: null, mode: "inverted", question_count: 10, asked_count: 4, player_count: 3 }),
    ).toBe("Everything · Find it · 4 of 10 questions · 3 players");
  });
});

describe("plural", () => {
  it("adds an s except for one", () => {
    expect(plural(1, "game")).toBe("1 game");
    expect(plural(0, "game")).toBe("0 games");
  });
});
```

- [ ] **Step 2: Run to verify it fails**

Run: `npx vitest run src/live/history.test.js`
Expected: FAIL — cannot resolve `./history`.

- [ ] **Step 3: Implement**

Create `src/live/history.js`:

```js
/**
 * The plain logic behind the "Past games" screens, kept apart from the
 * components so it can be tested on its own.
 */

export const STATUS_LABELS = {
  live: "Still playing",
  finished: "Finished",
  unfinished: "Not finished",
};

const MODE_LABELS = { choice: "Name it", inverted: "Find it" };

export function plural(n, word) {
  return `${n} ${word}${n === 1 ? "" : "s"}`;
}

/** "Condensers · Name it · 10 questions · 24 players" */
export function describeGame(game) {
  const questions =
    game.asked_count < game.question_count
      ? `${game.asked_count} of ${plural(game.question_count, "question")}`
      : plural(game.question_count, "question");
  return [
    game.category_name ?? "Everything",
    MODE_LABELS[game.mode] ?? game.mode,
    questions,
    plural(game.player_count, "player"),
  ].join(" · ");
}

/** When a game was played (epoch seconds), in the reader's locale and time zone. */
export function playedOn(seconds, locale) {
  return new Date(seconds * 1000).toLocaleString(locale, { dateStyle: "medium", timeStyle: "short" });
}

/** Hand a downloaded file to the browser to save. */
export function saveFile({ blob, filename }) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
```

Append to `src/api/client.js`, after the live-game section:

```js
// --- past class games (signed in) -------------------------------------------------

export const fetchLiveGames = () => request("/api/me/live-games");
export const fetchLiveGame = (id) => request(`/api/me/live-games/${id}`);
export const deleteLiveGame = (id) => request(`/api/me/live-games/${id}`, { method: "DELETE" });
export const replayLiveGame = (id, kind) =>
  request(`/api/me/live-games/${id}/replay`, { method: "POST", body: JSON.stringify({ kind }) });

/**
 * A past game's results as a CSV file, with the name the server suggests.
 * Fetched rather than linked to, because a plain link cannot carry the
 * sign-in token.
 */
export async function fetchLiveGameCsv(id) {
  let response;
  try {
    response = await fetch(`${BASE_URL}/api/me/live-games/${id}/results.csv`, {
      headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
    });
  } catch {
    throw new ApiError("Could not reach the server. Is the backend running?", 0);
  }
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(describeFailure(response.status, body), response.status);
  }
  const match = /filename="([^"]+)"/.exec(response.headers.get("Content-Disposition") ?? "");
  return { blob: await response.blob(), filename: match ? match[1] : `class-game-${id}.csv` };
}
```

- [ ] **Step 4: Run to verify it passes, and lint**

Run: `npx vitest run src/live/history.test.js && npm run lint`
Expected: PASS, no lint errors.

- [ ] **Step 5: Commit**

```bash
git add src/api/client.js src/live/history.js src/live/history.test.js
git commit -m "Frontend calls and helpers for past class games

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 10: "Past games" screens, routes and links

**Files:**
- Create: `src/live/LiveHistoryPage.jsx`, `src/live/LiveGamePage.jsx`
- Modify: `src/live/components.jsx` (add `SignInToKeep`)
- Modify: `src/App.jsx` (routes + route comment)
- Modify: `src/live/LiveSetupPage.jsx`, `src/live/LiveHostPage.jsx` (`Podium`), `src/pages/ProfilePage.jsx`
- Modify: `src/live/live.css` (append)

**Interfaces:**
- Consumes: everything from Task 9; `saveHostToken` (`src/live/game.js`); `useApi` (`src/hooks/useApi.js`); `useAuth` (`src/auth/context.js`); `DemoNotice` (`src/live/components.jsx`); host view field `owned` (Task 4).

- [ ] **Step 1: Add `SignInToKeep` to `src/live/components.jsx`**

Add at the top of the file, with the other imports:

```jsx
import { Link } from "react-router-dom";
```

Append:

```jsx
/** Shown where a signed-out teacher would otherwise see their past games. */
export function SignInToKeep() {
  return (
    <p className="section-note">
      <Link to="/sign-in">Sign in</Link> to keep the results of the class games you host.
    </p>
  );
}
```

- [ ] **Step 2: Create `src/live/LiveHistoryPage.jsx`**

```jsx
import { Link } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { EmptyMessage, ErrorMessage, Loading } from "../components/StatusMessage";
import { fetchLiveGames, IS_DEMO } from "../api/client";
import { useAuth } from "../auth/context";
import { useApi } from "../hooks/useApi";
import { DemoNotice, SignInToKeep } from "./components";
import { describeGame, playedOn, STATUS_LABELS } from "./history";

/** A teacher's past class games, newest first. */
function LiveHistoryPage() {
  const { user } = useAuth();
  return (
    <main className="categories-page">
      <div className="page-layout">
        <PageHeader title="Past games" backTo="/live" />
        <section className="categories-content narrow">
          {IS_DEMO ? <DemoNotice /> : user ? <GameList /> : <SignInToKeep />}
        </section>
      </div>
    </main>
  );
}

function GameList() {
  const { data: games, error, loading, reload } = useApi(fetchLiveGames);

  if (loading) return <Loading />;
  if (error) return <ErrorMessage error={error} onRetry={reload} />;
  if (!games.length) {
    return <EmptyMessage>No games yet. Class games you host while signed in appear here.</EmptyMessage>;
  }

  return (
    <ul className="live-history-list">
      {games.map((game) => (
        <li key={game.id}>
          <Link className="live-history-row" to={`/live/history/${game.id}`}>
            <span className="live-history-when">{playedOn(game.played_at)}</span>
            <span className="live-history-what">{describeGame(game)}</span>
            <span className="live-history-foot">
              <span className={`live-status is-${game.status}`}>{STATUS_LABELS[game.status]}</span>
              {game.winner && <span>Winner: {game.winner}</span>}
            </span>
          </Link>
        </li>
      ))}
    </ul>
  );
}

export default LiveHistoryPage;
```

- [ ] **Step 3: Create `src/live/LiveGamePage.jsx`**

```jsx
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { EmptyMessage, ErrorMessage, Loading } from "../components/StatusMessage";
import { deleteLiveGame, fetchLiveGame, fetchLiveGameCsv, IS_DEMO, replayLiveGame } from "../api/client";
import { useAuth } from "../auth/context";
import { useApi } from "../hooks/useApi";
import { DemoNotice, SignInToKeep } from "./components";
import { saveHostToken } from "./game";
import { describeGame, playedOn, saveFile, STATUS_LABELS } from "./history";

/** One past class game: the standings, the results file, and what to play next. */
function LiveGamePage() {
  const { id } = useParams();
  const { user } = useAuth();
  return (
    <main className="categories-page">
      <div className="page-layout">
        <PageHeader title="Class game" backTo="/live/history" />
        <section className="categories-content narrow">
          {IS_DEMO ? <DemoNotice /> : user ? <GameDetail id={id} /> : <SignInToKeep />}
        </section>
      </div>
    </main>
  );
}

function GameDetail({ id }) {
  const navigate = useNavigate();
  const { data: game, error, loading, reload } = useApi(() => fetchLiveGame(id), [id]);
  const [busy, setBusy] = useState(null); // which button is working
  const [actionError, setActionError] = useState(null);

  if (loading) return <Loading />;
  if (error) return <ErrorMessage error={error} onRetry={reload} />;

  async function run(name, work) {
    setBusy(name);
    setActionError(null);
    try {
      await work();
    } catch (err) {
      setActionError(err);
    } finally {
      setBusy(null);
    }
  }

  const replay = (kind) =>
    run(kind, async () => {
      const room = await replayLiveGame(id, kind);
      saveHostToken(room.pin, room.host_token);
      navigate(`/live/host/${room.pin}`);
    });

  const download = () => run("csv", async () => saveFile(await fetchLiveGameCsv(id)));

  const remove = () => {
    if (!window.confirm("Delete this game from your history? This cannot be undone.")) return;
    run("delete", async () => {
      await deleteLiveGame(id);
      navigate("/live/history", { replace: true });
    });
  };

  const stillPlaying = game.status === "live";
  const played = game.standings.length > 0;

  return (
    <>
      <p className="live-history-when">
        {playedOn(game.played_at)}{" "}
        <span className={`live-status is-${game.status}`}>{STATUS_LABELS[game.status]}</span>
      </p>
      <p className="section-note">
        {describeGame(game)} · {game.time_limit}s each
      </p>

      <h2 className="section-heading">Standings</h2>
      {played ? (
        <ol className="live-standings">
          {game.standings.map((row) => (
            <li key={row.id}>
              <span className="live-standings-place">{row.place}</span>
              <span className="live-standings-name">{row.name}</span>
              <span className="live-standings-correct">
                {row.correct}/{game.asked_count} right
              </span>
              <span className="live-standings-score">{row.score}</span>
            </li>
          ))}
        </ol>
      ) : (
        <EmptyMessage>Nobody played.</EmptyMessage>
      )}

      {actionError && <ErrorMessage error={actionError} />}

      <div className="live-history-actions">
        <button type="button" className="secondary-button" onClick={download} disabled={busy !== null}>
          <span className="material-symbols-outlined" aria-hidden="true">download</span>
          {busy === "csv" ? "Preparing..." : "Download CSV"}
        </button>
        <button type="button" className="secondary-button" onClick={() => replay("same")} disabled={busy !== null}>
          <span className="material-symbols-outlined" aria-hidden="true">replay</span>
          {busy === "same" ? "Opening the room..." : "Same settings"}
        </button>
        <button
          type="button"
          className="secondary-button"
          onClick={() => replay("mistakes")}
          disabled={busy !== null || !game.has_mistakes}
        >
          <span className="material-symbols-outlined" aria-hidden="true">school</span>
          {busy === "mistakes" ? "Opening the room..." : "Work on mistakes"}
        </button>
        <button
          type="button"
          className="text-button live-history-delete"
          onClick={remove}
          disabled={busy !== null || stillPlaying}
        >
          Delete
        </button>
      </div>

      {played && !game.has_mistakes && (
        <p className="section-note">The class got every question right, so there is nothing to go over.</p>
      )}
      {stillPlaying && (
        <p className="section-note">This game is still being played. Finish it on the board to delete it.</p>
      )}
    </>
  );
}

export default LiveGamePage;
```

- [ ] **Step 4: Routes**

In `src/App.jsx`, add the imports after `import LivePlayPage from "./live/LivePlayPage";`:

```jsx
import LiveHistoryPage from "./live/LiveHistoryPage";
import LiveGamePage from "./live/LiveGamePage";
```

In the route comment, after the `/live/host/:pin` line, add:

```
 *   /live/history            a signed-in teacher's past class games
 *   /live/history/:id        one past game: standings, CSV, play again
```

and after `<Route path="/live/host/:pin" element={<LiveHostPage />} />`:

```jsx
            <Route path="/live/history" element={<LiveHistoryPage />} />
            <Route path="/live/history/:id" element={<LiveGamePage />} />
```

- [ ] **Step 5: Links**

`src/live/LiveSetupPage.jsx` — change the router import to `import { Link, useNavigate } from "react-router-dom";`, add `import { useAuth } from "../auth/context";`, add `const { user } = useAuth();` under `const { catalog } = useProgress();`, and right after the `live-setup-lead` paragraph insert:

```jsx
              <p className="section-note">
                {user ? (
                  <Link to="/live/history">Past games</Link>
                ) : (
                  <>
                    <Link to="/sign-in">Sign in</Link> to keep the results of your games.
                  </>
                )}
              </p>
```

`src/live/LiveHostPage.jsx` — in `Podium`, just before the "New game" button:

```jsx
      {state.owned && (
        <p className="live-podium-saved">
          Results saved. <Link to="/live/history">See past games</Link>
        </p>
      )}
```

(`Link` is already imported in this file.)

`src/pages/ProfilePage.jsx` — add `import { IS_DEMO } from "../api/client";` and, just before the `{user && (` sign-out block:

```jsx
          {user && !IS_DEMO && (
            <Link className="secondary-button" to="/live/history">
              Past class games
            </Link>
          )}
```

- [ ] **Step 6: Styles**

Append to `src/live/live.css`:

```css
/* ---------- past games (site style) ---------- */

.live-history-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.live-history-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px 18px;
  border: 1px solid var(--outline, #CAC4D0);
  border-radius: var(--radius-card, 20px);
  background: var(--surface-bright, #FFFFFF);
  color: var(--on-surface, #1D1B20);
  text-decoration: none;
}

.live-history-row:hover {
  background: var(--surface-container-hover, #DED5E6);
}

.live-history-when {
  margin: 0;
  font-weight: 600;
}

.live-history-what {
  color: var(--on-surface-variant, #49454F);
}

.live-history-foot {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: var(--on-surface-variant, #49454F);
}

.live-status {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 999px;
  background: var(--surface-container, #E7E0EC);
  color: var(--on-surface, #1D1B20);
  font-size: 13px;
  font-weight: 600;
}

.live-status.is-live {
  background: var(--primary, #6750A4);
  color: var(--on-primary, #FFFFFF);
}

.live-status.is-finished {
  background: var(--success-container, #D6EFE0);
  color: var(--success, #2E6B4F);
}

.live-standings {
  margin: 0 0 20px;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.live-standings li {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 16px;
  border-radius: 14px;
  background: var(--surface-container, #E7E0EC);
  font-variant-numeric: tabular-nums;
}

.live-standings-place {
  width: 1.6em;
  color: var(--on-surface-variant, #49454F);
}

.live-standings-name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 600;
}

.live-standings-correct {
  color: var(--on-surface-variant, #49454F);
  font-size: 14px;
}

.live-standings-score {
  min-width: 4em;
  text-align: right;
  font-weight: 700;
}

.live-history-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
}

.live-history-actions .secondary-button {
  width: auto;
  min-height: 48px;
  margin-top: 0;
  gap: 8px;
  font-size: 17px;
}

.live-history-actions .secondary-button:disabled {
  opacity: 0.45;
  cursor: default;
}

.live-history-delete {
  margin-left: auto;
  color: var(--error, #B3261E);
}

.live-podium-saved {
  margin: 0;
  color: var(--live-ink-soft);
}

.live-podium-saved a {
  color: inherit;
}
```

- [ ] **Step 7: Lint, tests, build**

Run: `npm run lint && npm test && npm run build`
Expected: no lint errors, all vitest tests pass, build succeeds. Do not commit anything `npm run build` writes (`dist/` is ignored; never run `build:pages`).

- [ ] **Step 8: Check it in the browser**

Start the backend with two workers and the frontend:

```bash
cd backend && uvicorn app.main:app --workers 2 --port 8000
```

```bash
npm run dev
```

In the in-app browser at http://localhost:5173: create a test account (the verification code is printed in the backend console), open **Class game** → check the "Past games" link → open a room; in two more tabs open `/join/<PIN>` and join as two players; play two questions, one wrong on purpose. Stop the backend in the middle of a question (Ctrl+C) and start it again: board and phones must carry on. Finish the game: the podium says "Results saved". Open **Past games** → the game → check the standings, **Download CSV** (opens in a spreadsheet with the right columns), **Work on mistakes** (opens a board with the item that was wrong), **Same settings**, and **Delete** (after closing). Also check `/profile` shows "Past class games", and that signed out `/live/history` asks to sign in.

- [ ] **Step 9: Commit**

```bash
git add src/live/LiveHistoryPage.jsx src/live/LiveGamePage.jsx src/live/components.jsx src/App.jsx src/live/LiveSetupPage.jsx src/live/LiveHostPage.jsx src/pages/ProfilePage.jsx src/live/live.css
git commit -m "Past games screens: list, standings, CSV, play again, delete

Linked from the class game setup screen, the profile, and the board's
final screen when the game was hosted signed in. Hidden in the demo
build, which has no live games.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 11: Documentation and final checks

**Files:**
- Modify: `README.md`

- [ ] **Step 1: README**

In the "Class game (live, like Kahoot)" section, after the paragraph edited in Task 5, add:

```
**Past games.** If you are signed in when you open the room, the game is kept
once it has started: **Past games** (on the class game screen and in your
profile) lists them with the final standings, a CSV of who answered what
(opens in Excel or Google Sheets), and two ways to play again -- the same
settings with fresh questions, or **Work on mistakes**, which asks only the
items fewer than 80% of the class got right. Games hosted without signing in
are not kept.
```

In the Routes table, after the `/quiz/:token/results` row, add:

```
| `/live` | set up a class game |
| `/live/host/:pin` | the board during a class game |
| `/live/history` | past class games (signed in) |
| `/live/history/:id` | one past game: standings, CSV, play again |
| `/join[/:pin]`, `/play/:pin` | a student joins, and plays on their phone |
```

In the Layout block, after `app/progress.py`, add:

```
  app/live.py          the class game's rules, on the live_* tables
  app/live_history.py  past class games: standings, CSV, play again
```

and update `app/models.py`'s list there to end with `QuizSession, QuizQuestion, LiveGame, LivePlayer, LiveAnswer`.

In the Tests section, run `cd backend && python -m pytest -q`, and replace `62 tests: content, quiz, accounts, progress` with the new count and `content, quiz, accounts, progress, class games`.

- [ ] **Step 2: Full check**

Run: `npm run lint && npm test && (cd backend && python -m pytest -q)`
Expected: everything passes. `git status` must show no changes under `docs/` or `src/demo/data.json`.

- [ ] **Step 3: Commit and push**

```bash
git add README.md
git commit -m "README: class games are kept in the database; past games

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git fetch origin && git rebase origin/main
git push
```

Then tell the user the PR (int-al-l/chemquiz#2) is ready to be marked "Ready for review", and remind them to update `chemquiz-v2-notes.md` in the Claude project.
