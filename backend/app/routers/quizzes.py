"""A signed-in teacher's own quizzes (see app/quizzes.py).

Someone else's quiz answers 404, as if it did not exist.
"""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Body, Depends, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, quiz_import, quizzes
from ..database import get_db
from ..i18n import AppError, request_lang
from .account import current_user

router = APIRouter(prefix="/api/quizzes", tags=["quizzes"])


def own_quiz(db: Session, user: models.User, quiz_id: int) -> models.CustomQuiz:
    quiz = db.get(models.CustomQuiz, quiz_id)
    if quiz is None or quiz.user_id != user.id:
        raise AppError("no_quiz", status=404)
    return quiz


def _out(quiz: models.CustomQuiz) -> dict:
    return {
        "id": quiz.id,
        "title": quiz.title,
        "lang": quiz.lang,
        "questions": quiz.questions,
        "question_count": len(quiz.questions),
        "updated_at": quiz.updated_at,
    }


@router.get("")
def list_quizzes(user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(
        select(models.CustomQuiz)
        .where(models.CustomQuiz.user_id == user.id)
        .order_by(models.CustomQuiz.updated_at.desc(), models.CustomQuiz.id.desc())
    ).all()
    return [
        {"id": q.id, "title": q.title, "lang": q.lang, "question_count": len(q.questions), "updated_at": q.updated_at}
        for q in rows
    ]


@router.post("", status_code=201)
def create_quiz(payload: Any = Body(...), user: models.User = Depends(current_user),
                db: Session = Depends(get_db)):
    quiz = models.CustomQuiz(user_id=user.id, **quizzes.clean_quiz(payload))
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return _out(quiz)


class FromCardsIn(BaseModel):
    item_slugs: list[str] = Field(..., min_length=1, max_length=quizzes.MAX_QUESTIONS)
    mode: Literal["choice", "inverted"] = "choice"
    lang: Literal["en", "ru"] = "en"


@router.post("/from-cards")
def from_cards(payload: FromCardsIn, user: models.User = Depends(current_user),
               db: Session = Depends(get_db)):
    return {"questions": quizzes.from_cards(db, payload.item_slugs, payload.mode, payload.lang)}


@router.post("/import")
def import_file(file: UploadFile, lang: str = Depends(request_lang),
                user: models.User = Depends(current_user)):
    """Questions from a filled-in template, for the editor to show; nothing is saved."""
    questions, errors = quiz_import.parse(file.file.read(quiz_import.MAX_FILE + 1), lang)
    return {"questions": questions, "errors": errors}


@router.get("/{quiz_id}")
def get_quiz(quiz_id: int, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    return _out(own_quiz(db, user, quiz_id))


@router.get("/{quiz_id}/play")
def play_quiz(quiz_id: int, lang: str = Depends(request_lang),
              user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    """The questions as a game asks them, answers included: the solo player
    is the author, who knows them anyway."""
    quiz = own_quiz(db, user, quiz_id)
    return {"id": quiz.id, "title": quiz.title, "questions": quizzes.freeze(quiz.questions, lang)}


@router.put("/{quiz_id}")
def update_quiz(quiz_id: int, payload: Any = Body(...), user: models.User = Depends(current_user),
                db: Session = Depends(get_db)):
    quiz = own_quiz(db, user, quiz_id)
    for field, value in quizzes.clean_quiz(payload).items():
        setattr(quiz, field, value)
    quiz.updated_at = models.utcnow()
    db.commit()
    db.refresh(quiz)
    return _out(quiz)


@router.delete("/{quiz_id}", status_code=204)
def delete_quiz(quiz_id: int, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    db.delete(own_quiz(db, user, quiz_id))
    db.commit()
    return None
