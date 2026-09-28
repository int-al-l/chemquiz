"""Live classroom game endpoints (see app/live.py for the rules).

The host and each player hold a secret token, sent in the X-Live-Token
header. The PIN only finds the room; it grants nothing on its own.

Each endpoint builds its reply before it commits: after a commit, every row
would be read again one at a time.
"""

from __future__ import annotations

import socket
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import crud, live, models
from ..config import MAX_QUESTION_COUNT, QUIZ_MODES
from ..database import get_db
from ..i18n import AppError
from .account import optional_user

router = APIRouter(prefix="/api/live", tags=["live"])


class CreateIn(BaseModel):
    category_slug: Optional[str] = None
    mode: str = "choice"
    question_count: int = Field(10, ge=1, le=MAX_QUESTION_COUNT)
    time_limit: int = live.DEFAULT_TIME_LIMIT
    lang: Literal["en", "ru"] = "en"


class JoinIn(BaseModel):
    name: str = Field(..., max_length=200)


class AnswerIn(BaseModel):
    position: int
    choice_id: int


class LockIn(BaseModel):
    locked: bool


def _fail(db: Session, exc: AppError, room: Optional[live.Room] = None) -> AppError:
    """Undo whatever the request started; errors about a known game speak its language."""
    # Read before the rollback: afterwards it would be a fresh query, and the
    # game may have been closed in between.
    if room is not None:
        exc.lang = room.game.lang
    db.rollback()
    return exc


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
def create(
    payload: CreateIn,
    db: Session = Depends(get_db),
    user: Optional[models.User] = Depends(optional_user),
):
    if payload.mode not in QUIZ_MODES:
        raise AppError("unknown_mode", status=422, mode=payload.mode)
    if payload.time_limit not in live.TIME_LIMITS:
        raise AppError("bad_time_limit", status=422)
    category = None
    if payload.category_slug:
        category = crud.get_category_by_slug(db, payload.category_slug)
        if category is None:
            raise AppError("no_category", status=404, slug=payload.category_slug)
    try:
        room = live.create_room(
            db,
            mode=payload.mode,
            question_count=payload.question_count,
            time_limit=payload.time_limit,
            category=category,
            host_user=user,
            lang=payload.lang,
        )
    except live.LiveError as exc:
        raise _fail(db, exc) from exc
    view = {"host_token": room.game.host_token, **live.host_view(room, live._now())}
    db.commit()
    return view


@router.get("/{pin}")
def peek(pin: str, db: Session = Depends(get_db)):
    """Is there a game with this PIN, and can it still be joined?"""
    room = None
    try:
        room = live.open_room(db, pin)
    except live.LiveError as exc:
        raise _fail(db, exc, room) from exc
    game = room.game
    return {
        "pin": game.pin,
        "phase": game.phase,
        "lang": game.lang,
        "joinable": game.phase != "finished" and not game.locked,
        "player_count": len(room.active_players),
    }


# --- host -----------------------------------------------------------------------


@router.get("/{pin}/host")
def host_state(pin: str, x_live_token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    now = live._now()
    room = None
    try:
        room = live.open_room(db, pin)
        live.check_host(room, x_live_token)
        room = live.poll(db, room, now)
    except live.LiveError as exc:
        raise _fail(db, exc, room) from exc
    view = live.host_view(room, now)
    live.mark_touched(db, room, now)
    db.commit()
    return view


def _host_action(pin: str, token: Optional[str], db: Session, action):
    now = live._now()
    room = None
    try:
        room = live.open_room(db, pin, lock=True)
        live.check_host(room, token)
        room.game.touched_at = now
        action(room, now)
        db.flush()
    except live.LiveError as exc:
        raise _fail(db, exc, room) from exc
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
    room = None
    try:
        room = live.open_room(db, pin, lock=True)
        live.check_host(room, x_live_token)
    except live.LiveError as exc:
        raise _fail(db, exc, room) from exc
    live.retire(db, room.game)
    db.commit()
    return None


# --- players ----------------------------------------------------------------------


def _player(room: live.Room, token: Optional[str]) -> models.LivePlayer:
    player = room.player_by_token(token)
    if player is None:
        raise live.LiveError("not_in_game", status=403)
    if player.removed:
        raise live.LiveError("removed_from_game", status=410)
    return player


@router.post("/{pin}/join", status_code=201)
def join(pin: str, payload: JoinIn, db: Session = Depends(get_db)):
    now = live._now()
    room = None
    try:
        room = live.open_room(db, pin, lock=True)
        player = room.join(payload.name, now)
        room.game.touched_at = now
        db.flush()
    except live.LiveError as exc:
        raise _fail(db, exc, room) from exc
    view = {"token": player.token, **live.player_view(room, player, now)}
    db.commit()
    return view


@router.get("/{pin}/me")
def player_state(pin: str, x_live_token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    now = live._now()
    room = None
    try:
        room = live.open_room(db, pin)
        player = _player(room, x_live_token)
        room = live.poll(db, room, now)
    except live.LiveError as exc:
        raise _fail(db, exc, room) from exc
    view = live.player_view(room, player, now)
    live.mark_seen(db, room, player, now)
    db.commit()
    return view


@router.post("/{pin}/answer")
def answer(
    pin: str, payload: AnswerIn, x_live_token: Optional[str] = Header(None), db: Session = Depends(get_db)
):
    now = live._now()
    room = None
    try:
        room = live.open_room(db, pin, lock=True)
        player = _player(room, x_live_token)
        player.last_seen = now
        room.answer(player, payload.position, payload.choice_id, now)
        room.game.touched_at = now
        db.flush()
    except live.LiveError as exc:
        raise _fail(db, exc, room) from exc
    except IntegrityError as exc:
        # The database's own guard against a second answer (see LiveAnswer).
        raise _fail(db, live.LiveError("already_answered"), room) from exc
    view = live.player_view(room, player, now)
    db.commit()
    return view
