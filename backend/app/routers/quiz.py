"""Quiz endpoints.

The grading happens here rather than in the browser, so the answers to
unanswered questions are never sent to the client.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..i18n import AppError, request_lang

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


@router.post("/start", response_model=schemas.QuizSessionOut, status_code=201)
def start_quiz(
    payload: schemas.QuizStartIn, db: Session = Depends(get_db), lang: str = Depends(request_lang)
):
    category = None
    if payload.category_slug:
        category = crud.get_category_by_slug(db, payload.category_slug)
        if category is None:
            raise AppError("no_category", status=404, slug=payload.category_slug)

    session = crud.create_quiz_session(
        db,
        mode=payload.mode.value,
        question_count=payload.question_count,
        category=category,
    )

    return crud.session_payload(db, session, lang)


@router.get("/{token}", response_model=schemas.QuizSessionOut)
def get_quiz(token: str, db: Session = Depends(get_db), lang: str = Depends(request_lang)):
    session = crud.get_quiz_session(db, token)
    if session is None:
        raise AppError("quiz_not_found", status=404)
    return crud.session_payload(db, session, lang)


@router.post("/{token}/answer", response_model=schemas.QuizAnswerOut)
def answer_question(
    token: str,
    payload: schemas.QuizAnswerIn,
    db: Session = Depends(get_db),
    lang: str = Depends(request_lang),
):
    session = crud.get_quiz_session(db, token)
    if session is None:
        raise AppError("quiz_not_found", status=404)

    question = next(
        (q for q in session.questions if q.position == payload.position), None
    )
    if question is None:
        raise AppError("no_question", status=404, position=payload.position)

    if question.answered_at is not None:
        # Without this, a replayed request could turn a wrong answer into a
        # right one.
        raise AppError("question_answered")

    if payload.choice_id not in question.choice_ids:
        raise AppError("choice_not_option", status=422)

    question = crud.grade_answer(db, session, question, choice_id=payload.choice_id)
    db.refresh(session)

    return {
        "position": question.position,
        "is_correct": question.is_correct,
        "correct_item": crud.item_payload(question.item, lang),
        "correct_choice_id": question.item_id,
        "given_choice_id": question.given_choice_id,
        "given_answer": question.given_answer,
        "answered_count": session.answered_count,
        "correct_count": session.correct_count,
        "is_complete": session.is_complete,
    }


@router.get("/{token}/results", response_model=schemas.QuizResultsOut)
def get_results(token: str, db: Session = Depends(get_db), lang: str = Depends(request_lang)):
    session = crud.get_quiz_session(db, token)
    if session is None:
        raise AppError("quiz_not_found", status=404)
    return crud.results_payload(session, lang, db)


@router.delete("/{token}", status_code=204)
def abandon_quiz(token: str, db: Session = Depends(get_db)):
    session = crud.get_quiz_session(db, token)
    if session is not None:
        db.delete(session)
        db.commit()
    return None
