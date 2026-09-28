"""A signed-in teacher's past class games (see app/live_history.py).

Another teacher's game, or one that never left the lobby, answers 404 as if
it did not exist.
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
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


@router.get("/{game_id}/results.csv")
def results_csv(game_id: int, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    game = _own_game(db, user, game_id)
    return Response(
        content=live_history.results_csv(db, game).encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{live_history.csv_filename(game)}"'},
    )


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
