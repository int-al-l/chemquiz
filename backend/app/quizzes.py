"""Custom quizzes: a teacher's own questions, checked, and turned into the
shape a game plays.

A quiz is one JSON document (`models.CustomQuiz.questions`), edited and saved
whole. `clean_question` is the only gate a question passes on its way in --
from the editor, from cards, or from an imported file -- and `freeze` turns
the stored questions into what the class game (`live.py`) and the solo player
show and grade (`grading.py`).
"""

from __future__ import annotations

import math
import random
import re
from typing import Any, Optional

from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from . import messages
from .i18n import AppError
from .text import normalize

TYPES = ("quiz", "tf", "type", "slider")
TIME_LIMITS = (5, 10, 20, 30, 60, 90, 120, 240)
DEFAULT_TIME_LIMIT = 20
MAX_QUESTIONS = 100
TITLE_MAX = 120
TEXT_MAX = 300
OPTION_MAX = 75
ACCEPTED_MAX = 20
UNIT_MAX = 10
# Pictures are ours: a library photo or an upload, never someone else's URL.
IMAGE_RE = re.compile(r"^/static/(images|uploads)/[A-Za-z0-9_.-]+$")


class QuizError(AppError):
    """A quiz that cannot be saved; `question` is the 1-based number of the culprit."""

    def __init__(self, key: str, question: Optional[int] = None):
        super().__init__(key, status=422)
        self.question = question

    def response(self, lang: str) -> JSONResponse:
        return JSONResponse(
            status_code=self.status,
            content={"detail": messages.text(self.key, lang), "code": self.key, "question": self.question},
        )


def _text(value: Any, limit: int, key: str) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise QuizError(key)
    value = " ".join(value.split())
    if len(value) > limit:
        raise QuizError(key)
    return value


def _image(value: Any) -> Optional[str]:
    if value in (None, ""):
        return None
    if not isinstance(value, str) or not IMAGE_RE.match(value) or ".." in value:
        raise QuizError("q_image")
    return value


def _number(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise QuizError("q_slider")
    return value


def clean_question(q: Any) -> dict:
    """The question as stored, with only known fields; QuizError if it breaks a rule."""
    if not isinstance(q, dict) or q.get("type") not in TYPES:
        raise QuizError("q_type")
    kind = q["type"]
    time_limit = q.get("time_limit", DEFAULT_TIME_LIMIT)
    if isinstance(time_limit, bool) or time_limit not in TIME_LIMITS:
        raise QuizError("q_time")
    out = {
        "type": kind,
        "text": _text(q.get("text"), TEXT_MAX, "q_text_long"),
        "image": _image(q.get("image")),
        "time_limit": int(time_limit),
    }
    if not out["text"] and not out["image"]:
        raise QuizError("q_text")

    if kind == "quiz":
        options = q.get("options")
        if not isinstance(options, list) or not 2 <= len(options) <= 4:
            raise QuizError("q_options")
        out["options"] = []
        for o in options:
            if not isinstance(o, dict):
                raise QuizError("q_options")
            option = {
                "text": _text(o.get("text"), OPTION_MAX, "q_option_long"),
                "image": _image(o.get("image")),
                "correct": o.get("correct") is True,
            }
            if not option["text"] and not option["image"]:
                raise QuizError("q_option_empty")
            out["options"].append(option)
        if not any(o["correct"] for o in out["options"]):
            raise QuizError("q_correct")
    elif kind == "tf":
        if not isinstance(q.get("answer"), bool):
            raise QuizError("q_tf")
        out["answer"] = q["answer"]
    elif kind == "type":
        accepted = q.get("accepted")
        if not isinstance(accepted, list) or not 1 <= len(accepted) <= 4:
            raise QuizError("q_accepted")
        out["accepted"] = [_text(a, ACCEPTED_MAX, "q_accepted") for a in accepted]
        # An answer that normalises to nothing ("?", "the") could never be typed right.
        if not all(normalize(a) for a in out["accepted"]):
            raise QuizError("q_accepted")
    else:
        lo, hi, step, answer = (_number(q.get(k)) for k in ("min", "max", "step", "answer"))
        tolerance = _number(q.get("tolerance", 0))
        if not (lo < hi and 0 < step <= hi - lo and lo <= answer <= hi and 0 <= tolerance <= hi - lo):
            raise QuizError("q_slider")
        out.update(min=lo, max=hi, step=step, answer=answer, tolerance=tolerance,
                   unit=_text(q.get("unit"), UNIT_MAX, "q_slider"))
    return out


def clean_quiz(body: Any) -> dict:
    """{"title", "lang", "questions"} as stored; QuizError names the failing question."""
    if not isinstance(body, dict):
        raise QuizError("quiz_title")
    title = _text(body.get("title"), TITLE_MAX, "quiz_title")
    if not title:
        raise QuizError("quiz_title")
    questions = body.get("questions")
    if not isinstance(questions, list) or not 1 <= len(questions) <= MAX_QUESTIONS:
        raise QuizError("quiz_size")
    cleaned = []
    for number, q in enumerate(questions, start=1):
        try:
            cleaned.append(clean_question(q))
        except QuizError as exc:
            exc.question = number
            raise
    lang = body.get("lang") if body.get("lang") in ("en", "ru") else "en"
    return {"title": title, "lang": lang, "questions": cleaned}


def freeze(questions: list[dict], lang: str) -> list[dict]:
    """Stored questions -> the frozen shape games play and grade (see grading.py)."""
    frozen = []
    for position, q in enumerate(questions, start=1):
        f = {
            "position": position,
            "type": q["type"],
            "prompt": q["text"] or None,
            "image_url": q["image"],
            "time_limit": q["time_limit"],
            "item": None,
        }
        if q["type"] == "quiz":
            f["choices"] = [
                {"id": i, "name": o["text"] or None, "image_url": o["image"]}
                for i, o in enumerate(q["options"])
            ]
            f["correct_ids"] = [i for i, o in enumerate(q["options"]) if o["correct"]]
        elif q["type"] == "tf":
            f["choices"] = [
                {"id": 0, "name": messages.text("tf_true", lang), "image_url": None},
                {"id": 1, "name": messages.text("tf_false", lang), "image_url": None},
            ]
            f["correct_ids"] = [0 if q["answer"] else 1]
        elif q["type"] == "type":
            f["accepted"] = list(q["accepted"])
        else:
            f.update({k: q[k] for k in ("min", "max", "step", "answer", "tolerance", "unit")})
        frozen.append(f)
    return frozen


def from_cards(db: Session, slugs: list[str], mode: str, lang: str,
               rng: Optional[random.Random] = None) -> list[dict]:
    """Draft questions from library cards, the way a deck game asks them.

    Nothing is saved: the editor appends these and the teacher can change them
    like any other question. Unknown slugs are skipped.
    """
    from . import crud, live  # live imports grading, which must not import us back

    rng = rng or random.SystemRandom()
    library = crud.list_items(db)
    by_slug = {item.slug: item for item in library}
    asked = [by_slug[s] for s in dict.fromkeys(slugs) if s in by_slug]
    if not asked:
        raise AppError("no_items")
    drafts = []
    for q in live._draw(db, asked, library, mode, rng, lang):
        if mode == "inverted":
            text = messages.text("from_cards_inverted", lang, name=q["prompt"])
        else:
            text = messages.text("from_cards_choice", lang)
        drafts.append({
            "type": "quiz",
            "text": text,
            "image": q["image_url"],
            "time_limit": DEFAULT_TIME_LIMIT,
            "options": [
                {"text": c.get("name") or "", "image": c.get("image_url"), "correct": c["id"] == q["correct_id"]}
                for c in q["choices"]
            ],
        })
    return drafts
