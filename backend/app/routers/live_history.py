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
