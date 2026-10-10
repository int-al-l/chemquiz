"""Is an answer right? One rule per kind of question, for every game.

Works on the frozen questions a game stores (see `quizzes.freeze` and
`live._draw`). Games frozen before question types existed have no `type`
and no `correct_ids`; they are deck questions with one `correct_id`.
The solo player has a copy of these rules in src/quizzes/grade.js.
"""

from __future__ import annotations

from typing import Optional

from .text import normalize

CHOICE_TYPES = ("quiz", "tf")
# Slider values arrive as floats; 0.1 steps do not add up exactly.
EPSILON = 1e-9


def kind(q: dict) -> str:
    return q.get("type", "quiz")


def correct_ids(q: dict) -> list[int]:
    return q.get("correct_ids") or [q["correct_id"]]


def _number(value) -> Optional[float]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value


def grade(q: dict, given: dict) -> bool:
    """`given` is {"choice_id"}, {"text"} or {"value"}; ValueError if it cannot answer `q`."""
    k = kind(q)
    if k in CHOICE_TYPES:
        choice = given.get("choice_id")
        if choice not in {c["id"] for c in q["choices"]}:
            raise ValueError("not an option")
        return choice in correct_ids(q)
    if k == "type":
        text = given.get("text")
        typed = normalize(text) if isinstance(text, str) else ""
        if not typed:
            raise ValueError("nothing typed")
        return any(typed == normalize(a) for a in q["accepted"])
    value = _number(given.get("value"))
    if value is None or not q["min"] - EPSILON <= value <= q["max"] + EPSILON:
        raise ValueError("off the scale")
    return abs(value - q["answer"]) <= q["tolerance"] + EPSILON


def number_text(x: float) -> str:
    """100 -> "100", 0.5 -> "0.5", without float noise or exponents."""
    return ("%f" % x).rstrip("0").rstrip(".")


def answer_text(q: dict) -> Optional[str]:
    """The right answer in words, for the reveal; None when it is only pictures."""
    if q.get("item"):
        return q["item"]["name"]
    k = kind(q)
    if k in CHOICE_TYPES:
        right = correct_ids(q)
        names = [c["name"] for c in q["choices"] if c["id"] in right and c.get("name")]
        return " / ".join(names) or None
    if k == "type":
        return " / ".join(q["accepted"])
    text = number_text(q["answer"])
    if q["tolerance"]:
        text += f" ± {number_text(q['tolerance'])}"
    if q["unit"]:
        text += f" {q['unit']}"
    return text
