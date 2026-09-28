"""Live classroom game endpoints (see app/live.py for the rules).

The host and each player hold a secret token, sent in the X-Live-Token
header. The PIN only finds the room; it grants nothing on its own.
"""

from __future__ import annotations

import secrets
import socket
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .. import crud, live
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


def _fail(exc: live.LiveError) -> HTTPException:
    return HTTPException(status_code=exc.status, detail=str(exc))


def _host_room(pin: str, token: Optional[str]) -> live.Room:
    room = live.registry.get(pin)
    if not token or not secrets.compare_digest(room.host_token, token):
        raise live.LiveError("Only the host can do that", status=403)
    return room


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
        raise _fail(exc) from exc
    with live.registry.lock:
        return {"host_token": room.host_token, **live.host_view(room, live._now())}


@router.get("/{pin}")
def peek(pin: str):
    """Is there a game with this PIN, and can it still be joined?"""
    with live.registry.lock:
        try:
            room = live.registry.get(pin)
        except live.LiveError as exc:
            raise _fail(exc) from exc
        return {
            "pin": room.pin,
            "phase": room.phase,
            "joinable": room.phase != "finished" and not room.locked,
            "player_count": len(room.active_players),
        }


# --- host -----------------------------------------------------------------------


@router.get("/{pin}/host")
def host_state(pin: str, x_live_token: Optional[str] = Header(None)):
    now = live._now()
    with live.registry.lock:
        try:
            room = _host_room(pin, x_live_token)
        except live.LiveError as exc:
            raise _fail(exc) from exc
        room.touched_at = now
        room.tick(now)
        return live.host_view(room, now)


def _host_action(pin: str, token: Optional[str], action):
    now = live._now()
    with live.registry.lock:
        try:
            room = _host_room(pin, token)
            room.touched_at = now
            action(room, now)
        except live.LiveError as exc:
            raise _fail(exc) from exc
        return live.host_view(room, now)


@router.post("/{pin}/next")
def host_next(pin: str, x_live_token: Optional[str] = Header(None)):
    return _host_action(pin, x_live_token, lambda room, now: room.advance(now))


@router.post("/{pin}/finish")
def host_finish(pin: str, x_live_token: Optional[str] = Header(None)):
    return _host_action(pin, x_live_token, lambda room, now: room.finish(now))


@router.post("/{pin}/lock")
def host_lock(pin: str, payload: LockIn, x_live_token: Optional[str] = Header(None)):
    def lock(room, now):
        room.locked = payload.locked

    return _host_action(pin, x_live_token, lock)


@router.post("/{pin}/players/{player_id}/remove")
def host_remove(pin: str, player_id: int, x_live_token: Optional[str] = Header(None)):
    def remove(room, now):
        for p in room.players:
            if p.id == player_id:
                p.removed = True
                room.tick(now)  # they may have been the last one to answer
                return
        raise live.LiveError("No such player", status=404)

    return _host_action(pin, x_live_token, remove)


@router.delete("/{pin}", status_code=204)
def host_close(pin: str, x_live_token: Optional[str] = Header(None)):
    with live.registry.lock:
        try:
            _host_room(pin, x_live_token)
        except live.LiveError as exc:
            raise _fail(exc) from exc
        del live.registry.rooms[pin]
    return None


# --- players ----------------------------------------------------------------------


def _player(room: live.Room, token: Optional[str]) -> live.Player:
    player = room.player_by_token(token)
    if player is None:
        raise live.LiveError("You are not in this game", status=403)
    if player.removed:
        raise live.LiveError("The host removed you from this game", status=410)
    return player


@router.post("/{pin}/join", status_code=201)
def join(pin: str, payload: JoinIn):
    now = live._now()
    with live.registry.lock:
        try:
            room = live.registry.get(pin)
            player = room.join(payload.name, now)
        except live.LiveError as exc:
            raise _fail(exc) from exc
        room.touched_at = now
        return {"token": player.token, **live.player_view(room, player, now)}


@router.get("/{pin}/me")
def player_state(pin: str, x_live_token: Optional[str] = Header(None)):
    now = live._now()
    with live.registry.lock:
        try:
            room = live.registry.get(pin)
            player = _player(room, x_live_token)
        except live.LiveError as exc:
            raise _fail(exc) from exc
        player.last_seen = now
        room.tick(now)
        return live.player_view(room, player, now)


@router.post("/{pin}/answer")
def answer(pin: str, payload: AnswerIn, x_live_token: Optional[str] = Header(None)):
    now = live._now()
    with live.registry.lock:
        try:
            room = live.registry.get(pin)
            player = _player(room, x_live_token)
            player.last_seen = now
            room.answer(player, payload.position, payload.choice_id, now)
        except live.LiveError as exc:
            raise _fail(exc) from exc
        room.touched_at = now
        return live.player_view(room, player, now)
