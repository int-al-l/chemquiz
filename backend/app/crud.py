"""Database access and the quiz rules.

Route handlers stay thin; everything that decides *what* happens lives here.
"""

from __future__ import annotations

import datetime as dt
import random
import secrets
from typing import Iterable, Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from . import models
from .config import CHOICES_PER_QUESTION, IMAGES_URL_PREFIX, SESSION_TTL_HOURS


# --- helpers --------------------------------------------------------------


def image_url(filename: Optional[str]) -> Optional[str]:
    if not filename:
        return None
    return f"{IMAGES_URL_PREFIX}/{filename}"


def descendant_category_ids(db: Session, root_id: int) -> list[int]:
    """Every category id in the subtree rooted at `root_id`, including itself.

    Walked in Python rather than with a recursive CTE: the tree is a handful of
    levels deep and this keeps the query portable across SQLite and Postgres.
    """
    found = [root_id]
    frontier = [root_id]
    while frontier:
        rows = db.execute(
            select(models.Category.id).where(models.Category.parent_id.in_(frontier))
        ).scalars().all()
        rows = [r for r in rows if r not in found]
        if not rows:
            break
        found.extend(rows)
        frontier = rows
    return found


def count_items_in_subtree(db: Session, category_id: int) -> int:
    ids = descendant_category_ids(db, category_id)
    return db.execute(
        select(func.count(models.Item.id)).where(models.Item.category_id.in_(ids))
    ).scalar_one()


# --- content queries ------------------------------------------------------


def get_category_by_slug(db: Session, slug: str) -> Optional[models.Category]:
    return db.execute(
        select(models.Category)
        .where(models.Category.slug == slug)
        .options(
            selectinload(models.Category.children),
            selectinload(models.Category.items).selectinload(models.Item.photos),
            selectinload(models.Category.parent),
        )
    ).scalar_one_or_none()


def list_root_categories(db: Session) -> Sequence[models.Category]:
    return db.execute(
        select(models.Category)
        .where(models.Category.parent_id.is_(None))
        .options(selectinload(models.Category.children), selectinload(models.Category.items))
        .order_by(models.Category.sort_order, models.Category.name)
    ).scalars().all()


def list_items(
    db: Session, category_id: Optional[int] = None, include_descendants: bool = True
) -> Sequence[models.Item]:
    stmt = (
        select(models.Item)
        .options(selectinload(models.Item.photos), selectinload(models.Item.category))
        .order_by(models.Item.sort_order, models.Item.name)
    )
    if category_id is not None:
        ids = (
            descendant_category_ids(db, category_id)
            if include_descendants
            else [category_id]
        )
        stmt = stmt.where(models.Item.category_id.in_(ids))
    return db.execute(stmt).scalars().all()


# --- quiz -----------------------------------------------------------------


def _pick_distractors(
    db: Session,
    answer: models.Item,
    pool: Sequence[models.Item],
    how_many: int,
    rng: random.Random,
) -> list[models.Item]:
    """Choose plausible wrong options.

    Siblings first -- telling two condensers apart is the actual skill, whereas
    a condenser next to three amino acids is answerable without knowing
    anything. Widen to the whole pool only when the sibling set is too small.
    """
    siblings = [i for i in pool if i.category_id == answer.category_id and i.id != answer.id]
    rng.shuffle(siblings)
    chosen = siblings[:how_many]

    if len(chosen) < how_many:
        chosen_ids = {i.id for i in chosen} | {answer.id}
        others = [i for i in pool if i.id not in chosen_ids]
        rng.shuffle(others)
        chosen.extend(others[: how_many - len(chosen)])

    if len(chosen) < how_many:
        # Fall back to the whole library: a tiny category should still be playable.
        chosen_ids = {i.id for i in chosen} | {answer.id}
        extra = db.execute(
            select(models.Item).where(models.Item.id.notin_(chosen_ids))
        ).scalars().all()
        extra = list(extra)
        rng.shuffle(extra)
        chosen.extend(extra[: how_many - len(chosen)])

    return chosen[:how_many]


def create_quiz_session(
    db: Session,
    *,
    mode: str,
    question_count: int,
    category: Optional[models.Category] = None,
    rng: Optional[random.Random] = None,
) -> models.QuizSession:
    """Build a full session up front.

    Questions are fixed at start time -- item order, the options and their
    order, and every photograph shown -- so a reload or a back-button press
    shows the same quiz rather than silently rerolling it.
    """
    rng = rng or random.Random()

    pool = list(list_items(db, category.id if category else None))
    if not pool:
        raise ValueError("no items available for this category")

    order = list(pool)
    rng.shuffle(order)

    # Ask for more than we have and the quiz simply gets shorter, rather than
    # repeating items within one run. An item appears at most once, so the same
    # piece of glassware is never the answer twice -- even though it may own
    # several photographs.
    asked = order[: min(question_count, len(order))]

    session = models.QuizSession(
        token=secrets.token_urlsafe(32)[:43],
        category_id=category.id if category else None,
        category_slug=category.slug if category else None,
        category_name=category.name if category else None,
        mode=mode,
        question_count=len(asked),
    )
    db.add(session)
    db.flush()

    for position, drawn in enumerate(draw_questions(db, asked, pool, mode, rng), start=1):
        item, options, photo, picks = drawn
        choice_ids = ",".join(str(o.id) for o in options)
        choice_photo_ids = (
            ",".join(str(p.id) if p else "" for p in picks) if mode == "inverted" else ""
        )
        db.add(
            models.QuizQuestion(
                session_id=session.id,
                position=position,
                item_id=item.id,
                photo_id=photo.id if photo else None,
                choice_item_ids=choice_ids,
                choice_photo_ids=choice_photo_ids,
            )
        )

    db.commit()
    db.refresh(session)
    return session


def draw_questions(
    db: Session,
    asked: Sequence[models.Item],
    pool: Sequence[models.Item],
    mode: str,
    rng: random.Random,
) -> list[tuple]:
    """Options and photographs for each asked item, fixed up front.

    Returns (item, options, photo, option_photos) per question. Shared by the
    solo quiz and the live classroom game, so both ask the same kind of
    question.
    """
    drawn = []
    for item in asked:
        distractors = _pick_distractors(db, item, pool, CHOICES_PER_QUESTION - 1, rng)
        options = [item, *distractors]
        rng.shuffle(options)

        # Show one of this item's photographs, chosen now and remembered, so a
        # refresh does not swap the picture mid-question.
        photo = rng.choice(item.photos) if item.photos else None

        picks: list = []
        if mode == "inverted":
            # One picture per option, fixed now for the same reason.
            for option in options:
                if option.id == item.id:
                    picks.append(photo)
                else:
                    picks.append(rng.choice(option.photos) if option.photos else None)

        drawn.append((item, options, photo, picks))
    return drawn


def get_quiz_session(db: Session, token: str) -> Optional[models.QuizSession]:
    return db.execute(
        select(models.QuizSession)
        .where(models.QuizSession.token == token)
        .options(
            selectinload(models.QuizSession.questions)
            .selectinload(models.QuizQuestion.item)
            .selectinload(models.Item.photos),
            selectinload(models.QuizSession.questions).selectinload(
                models.QuizQuestion.photo
            ),
        )
    ).scalar_one_or_none()


def grade_answer(
    db: Session,
    session: models.QuizSession,
    question: models.QuizQuestion,
    *,
    choice_id: int,
) -> models.QuizQuestion:
    """Record and mark one answer. Re-answering a question is refused upstream."""
    question.is_correct = choice_id == question.item_id
    picked = db.get(models.Item, choice_id)
    question.given_answer = picked.name if picked else None
    question.given_choice_id = choice_id

    question.answered_at = models.utcnow()
    db.flush()

    if all(q.answered_at is not None for q in session.questions):
        session.completed_at = models.utcnow()

    db.commit()
    db.refresh(question)
    return question


def purge_stale_sessions(db: Session) -> int:
    """Drop sessions older than the TTL.

    Nobody owns a session yet, so there is nothing to lose and no reason to let
    the table grow forever.
    """
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=SESSION_TTL_HOURS)
    stale = db.execute(
        select(models.QuizSession).where(models.QuizSession.created_at < cutoff)
    ).scalars().all()
    for session in stale:
        db.delete(session)
    if stale:
        db.commit()
    return len(stale)


# --- serialisation --------------------------------------------------------


def item_payload(item: models.Item) -> dict:
    return {
        "id": item.id,
        "slug": item.slug,
        "name": item.name,
        "catalog_name": item.catalog_name,
        "description": item.description,
        "image_url": image_url(item.cover),
        "photo_urls": [image_url(p.filename) for p in item.photos],
        "photo_count": len(item.photos),
        # Parallel to photo_urls: the attribution a photo needs, or None.
        "photo_credits": [p.credit for p in item.photos],
        "category_slug": item.category.slug if item.category is not None else None,
    }


def category_payload(db: Session, category: models.Category) -> dict:
    return {
        "id": category.id,
        "slug": category.slug,
        "name": category.name,
        "description": category.description,
        "image_url": image_url(category.image),
        "child_count": len(category.children),
        "item_count": len(category.items),
        "quizzable_count": count_items_in_subtree(db, category.id),
    }


def question_payload(db: Session, question: models.QuizQuestion, mode: str) -> dict:
    """Serialise a question for the player -- never including the answer."""
    ids = question.choice_ids
    by_id = {}
    if ids:
        items = db.execute(
            select(models.Item)
            .where(models.Item.id.in_(ids))
            .options(selectinload(models.Item.photos))
        ).scalars().all()
        by_id = {i.id: i for i in items}

    choices: list[dict] = []
    if mode == "inverted":
        photo_ids = question.choice_photo_list
        photos = {}
        wanted = [p for p in photo_ids if p]
        if wanted:
            photos = {
                p.id: p
                for p in db.execute(
                    select(models.ItemPhoto).where(models.ItemPhoto.id.in_(wanted))
                ).scalars()
            }
        for index, item_id in enumerate(ids):
            if item_id not in by_id:
                continue
            photo = photos.get(photo_ids[index]) if index < len(photo_ids) else None
            filename = photo.filename if photo else by_id[item_id].cover
            choices.append({"id": item_id, "image_url": image_url(filename)})
        return {
            "position": question.position,
            "image_url": None,
            "prompt": question.item.name,
            "choices": choices,
            "answered": question.answered_at is not None,
        }

    # Preserve the order fixed at start time.
    choices = [{"id": i, "name": by_id[i].name} for i in ids if i in by_id]
    return {
        "position": question.position,
        "image_url": question_image_url(question),
        "prompt": None,
        "choices": choices,
        "answered": question.answered_at is not None,
    }


def question_image_url(question: models.QuizQuestion) -> Optional[str]:
    """The photograph this question shows -- its fixed variant, or the cover."""
    if question.photo is not None:
        return image_url(question.photo.filename)
    return image_url(question.item.cover)


def session_payload(db: Session, session: models.QuizSession) -> dict:
    return {
        "token": session.token,
        "mode": session.mode,
        "question_count": session.question_count,
        "category_slug": session.category_slug,
        "category_name": session.category_name,
        "answered_count": session.answered_count,
        "correct_count": session.correct_count,
        "is_complete": session.is_complete,
        "questions": [
            question_payload(db, q, session.mode) for q in session.questions
        ],
    }


def results_payload(session: models.QuizSession) -> dict:
    """Serialise a session's results.

    An unanswered question carries no item. Otherwise this endpoint would be a
    way to read the whole answer key mid-quiz, which is exactly what grading
    server-side is meant to prevent.
    """
    questions = []
    for q in session.questions:
        answered = q.answered_at is not None
        questions.append(
            {
                "position": q.position,
                "item": item_payload(q.item) if answered else None,
                # The photograph asked about, not the item's cover -- the review
                # list should show the picture the player actually saw.
                "image_url": question_image_url(q),
                "given_answer": q.given_answer,
                "is_correct": q.is_correct,
                "answered": answered,
            }
        )

    return {
        "token": session.token,
        "mode": session.mode,
        "category_slug": session.category_slug,
        "category_name": session.category_name,
        "question_count": session.question_count,
        "answered_count": session.answered_count,
        "correct_count": session.correct_count,
        "is_complete": session.is_complete,
        "created_at": session.created_at,
        "completed_at": session.completed_at,
        "questions": questions,
    }
