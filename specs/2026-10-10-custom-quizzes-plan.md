# Custom quizzes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A signed-in teacher builds their own Kahoot-style quiz (quiz / true-false / type answer / slider), from scratch, from library cards, or from an Excel/Word template, and runs it as a class game or plays it solo.

**Architecture:** A quiz is one JSON document (`CustomQuiz.questions`), checked by `quizzes.clean_question`. `quizzes.freeze` turns it into the "frozen" shape that live games already store in `LiveGame.questions`; `grading.grade` judges an answer against a frozen question for every type. The solo player fetches frozen questions (with answers: it is the author's own quiz) and grades in the browser with a JS port of the same grader.

**Tech Stack:** FastAPI + SQLAlchemy 2 + SQLite (backend), Pillow (uploads), stdlib `zipfile` + `xml.etree` (import), React 19 + react-router 7 + Vite + vitest (frontend).

**Spec:** `specs/2026-10-10-custom-quizzes-design.md`

## Global Constraints

- Python 3.11 in CI: no 3.12+ syntax.
- No new Python or JS dependencies. Pillow moves from the "catalog pipelines" block to the site block of `backend/requirements.txt` and is added to CI's pip line.
- Question time limits: exactly `(5, 10, 20, 30, 60, 90, 120, 240)` seconds; default 20.
- Limits: title ≤ 120, question text ≤ 300, option text ≤ 75, accepted answer ≤ 20 (1–4 of them), unit ≤ 10, 2–4 quiz options, 1–100 questions per quiz.
- Images: only `/static/images/<name>` or `/static/uploads/<name>`, name `[A-Za-z0-9_.-]+`.
- Uploads ≤ 5 MB, re-encoded JPEG ≤ 1600 px long side. Import files ≤ 2 MB, unpacked ≤ 20 MB.
- Scoring unchanged: 1000 → 500 linear in elapsed/limit, +100 per streak step, cap 500.
- Every user-visible server message is a key in `backend/app/messages.py` with `en` and `ru`; every frontend string is a key in both `src/i18n/en.js` and `src/i18n/ru.js` (the i18n tests enforce identical keys).
- Do not edit or commit `docs/` or `src/demo/data.json`.
- New pages show a demo notice when `IS_DEMO`.
- Checks: `npm run lint && npm test`, `cd backend && python -m pytest -q`.

## Review Focus

1. Russian-locale Excel turns `1,2` in the Correct column into the number `1.2` → still read as options 1 and 2 (Task 4 test `test_correct_numbers_survive_excel_decimal_comma`).
2. A transparent PNG uploaded as a question picture → white background, not black (Task 3 test `test_transparent_png_gets_a_white_background`).
3. An accepted answer that normalises to nothing (`"?"`, `"the"`) → refused on save, never an unanswerable question (Task 1 test `test_accepted_answer_must_survive_normalising`).
4. A slider value that is a float a hair past `max` (0.1 steps) → accepted, not "not an option" (Task 1 test `test_slider_edges_allow_float_noise`).
5. A game frozen before this change (no `type`, no `correct_ids` in its questions) → still plays and shows in history (Task 5 test `test_a_game_frozen_before_question_types_still_plays`).

---

## File map

Backend (`backend/app/`):
- Create `quizzes.py`: validation (`clean_question`, `clean_quiz`, `QuizError`), `freeze`, `from_cards`.
- Create `grading.py`: `correct_ids`, `grade`, `answer_text`.
- Create `quiz_import.py`: `read_rows`, `row_to_question`, `parse`.
- Create `routers/quizzes.py`: `/api/quizzes…`.
- Create `routers/uploads.py`: `/api/uploads`.
- Modify `models.py`: `CustomQuiz`; `LiveGame.custom_quiz_id`; `LiveAnswer.answer`.
- Modify `messages.py`, `config.py`, `main.py`, `live.py`, `live_history.py`, `routers/live.py`.
- Tests: `tests/test_grading.py`, `tests/test_quizzes.py`, `tests/test_uploads.py`, `tests/test_quiz_import.py`; additions to `tests/test_live.py`, `tests/test_live_history.py`.

Tools / static:
- Create `tools/make_quiz_templates.py` → writes `public/templates/chemquiz-template.xlsx` and `.docx` (committed).

Frontend (`src/`):
- Create `quizzes/grade.js` (+ test), `quizzes/model.js` (+ test), `quizzes/AnswerInput.jsx` (+ test), `quizzes/MyQuizzesPage.jsx`, `quizzes/QuizEditorPage.jsx`, `quizzes/QuestionForm.jsx`, `quizzes/LibraryPicker.jsx`, `quizzes/ImportPanel.jsx`, `quizzes/SoloPlayPage.jsx`, `quizzes/quizzes.css`.
- Modify `api/client.js`, `App.jsx`, `pages/ProfilePage.jsx`, `live/LiveSetupPage.jsx`, `live/LiveHostPage.jsx`, `live/LivePlayPage.jsx`, `live/history.js`, `i18n/en.js`, `i18n/ru.js`.

Other: `.gitignore` (`backend/static/uploads/`), `.github/workflows/ci.yml` (Pillow), `backend/requirements.txt`, `README.md`.

### The frozen question shape (used by live games and the solo player)

```
{ position, type: "quiz"|"tf"|"type"|"slider", prompt: str|None, image_url: str|None,
  time_limit: int|None,          # None for deck games: the game's limit applies
  item: dict|None,               # deck games: the card, revealed afterwards
  # quiz / tf:
  choices: [{id, name?, image_url?}], correct_ids: [int], correct_id?: int (deck games)
  # type:   accepted: [str]
  # slider: min, max, step, answer, tolerance, unit }
```

Old games stored before this change have no `type` (→ `"quiz"`) and no `correct_ids` (→ `[correct_id]`).

---

### Task 1: Question rules, freezing and grading (pure functions)

**Files:**
- Create: `backend/app/quizzes.py`
- Create: `backend/app/grading.py`
- Modify: `backend/app/messages.py` (new keys)
- Test: `backend/tests/test_grading.py`, `backend/tests/test_quizzes.py` (unit part)

**Interfaces:**
- Produces: `quizzes.TIME_LIMITS`, `quizzes.DEFAULT_TIME_LIMIT`, `quizzes.MAX_QUESTIONS`, `quizzes.QuizError(key, question=None)` (subclass of `AppError`, status 422, response adds `"question"`), `quizzes.clean_question(q) -> dict`, `quizzes.clean_quiz(body) -> {"title","lang","questions"}`, `quizzes.freeze(questions, lang) -> list[dict]`; `grading.correct_ids(q) -> list[int]`, `grading.grade(q, given: dict) -> bool` (raises `ValueError` when `given` cannot answer `q`), `grading.answer_text(q) -> str|None`.

- [ ] **Step 1: Add the messages**

In `backend/app/messages.py`, add a block before `# --- accounts ---`:

```python
    # --- custom quizzes ---
    "q_type": {"en": "Unknown question type", "ru": "Неизвестный тип вопроса"},
    "q_time": {"en": "Pick a time limit from the list", "ru": "Выберите время из списка"},
    "q_text": {"en": "Write the question or add a picture", "ru": "Напишите вопрос или добавьте картинку"},
    "q_text_long": {"en": "The question is too long (at most 300 characters)", "ru": "Слишком длинный вопрос (не больше 300 символов)"},
    "q_image": {"en": "That picture cannot be used", "ru": "Эту картинку нельзя использовать"},
    "q_options": {"en": "A quiz question needs 2 to 4 answers", "ru": "В вопросе нужно от 2 до 4 вариантов ответа"},
    "q_option_empty": {"en": "Every answer needs text or a picture", "ru": "У каждого варианта должен быть текст или картинка"},
    "q_option_long": {"en": "An answer is too long (at most 75 characters)", "ru": "Слишком длинный вариант (не больше 75 символов)"},
    "q_correct": {"en": "Mark at least one answer as correct", "ru": "Отметьте хотя бы один правильный вариант"},
    "q_tf": {"en": "Say whether the statement is true or false", "ru": "Укажите, верно утверждение или нет"},
    "q_accepted": {"en": "Give 1 to 4 accepted answers, each up to 20 characters", "ru": "Укажите от 1 до 4 правильных ответов, каждый не длиннее 20 символов"},
    "q_slider": {"en": "Check the slider: min below max, the answer between them, step above zero", "ru": "Проверьте ползунок: минимум меньше максимума, ответ между ними, шаг больше нуля"},
    "quiz_title": {"en": "Give the quiz a title (at most 120 characters)", "ru": "Назовите квиз (не больше 120 символов)"},
    "quiz_size": {"en": "A quiz holds 1 to 100 questions", "ru": "В квизе может быть от 1 до 100 вопросов"},
    "no_quiz": {"en": "No such quiz", "ru": "Такого квиза нет"},
    "quiz_gone": {"en": "That quiz has been deleted", "ru": "Этот квиз удалён"},
    "tf_true": {"en": "True", "ru": "Верно"},
    "tf_false": {"en": "False", "ru": "Неверно"},
    "from_cards_choice": {"en": "What is this?", "ru": "Что это?"},
    "from_cards_inverted": {"en": "Find the {name}", "ru": "Найдите: {name}"},
    "import_bad_file": {"en": "Upload the .xlsx or .docx template", "ru": "Загрузите шаблон в формате .xlsx или .docx"},
    "import_too_big": {"en": "The file is too large (at most 2 MB)", "ru": "Файл слишком большой (не больше 2 МБ)"},
    "import_no_table": {"en": "There is no question table in the file", "ru": "В файле нет таблицы с вопросами"},
    "import_type": {"en": "Unknown type in the Type column", "ru": "Неизвестный тип в столбце «Тип»"},
    "import_correct": {"en": "Fill in the Correct column", "ru": "Заполните столбец «Правильный»"},
    "import_too_many": {"en": "Only the first 100 questions were imported", "ru": "Импортированы только первые 100 вопросов"},
    "upload_bad": {"en": "That file is not a picture", "ru": "Этот файл — не картинка"},
    "upload_too_big": {"en": "The picture is too large (at most 5 MB)", "ru": "Картинка слишком большая (не больше 5 МБ)"},
```

- [ ] **Step 2: Write the failing grading tests**

`backend/tests/test_grading.py`:

```python
"""Is an answer right, for every kind of question a game can ask."""

import pytest

from app.grading import answer_text, correct_ids, grade

QUIZ = {"type": "quiz", "choices": [{"id": 0, "name": "A"}, {"id": 1, "name": "B"}, {"id": 2, "name": "C"}],
        "correct_ids": [0, 2]}
TF = {"type": "tf", "choices": [{"id": 0, "name": "True"}, {"id": 1, "name": "False"}], "correct_ids": [1]}
TYPED = {"type": "type", "accepted": ["Au", "Aurum"]}
SLIDER = {"type": "slider", "min": 0, "max": 1, "step": 0.1, "answer": 0.5, "tolerance": 0.1, "unit": "mol"}
OLD_DECK = {"choices": [{"id": 7, "name": "Flask"}, {"id": 9, "name": "Beaker"}], "correct_id": 9,
            "item": {"name": "Beaker"}}


def test_quiz_any_correct_option_counts():
    assert grade(QUIZ, {"choice_id": 0}) and grade(QUIZ, {"choice_id": 2})
    assert not grade(QUIZ, {"choice_id": 1})


def test_true_false():
    assert grade(TF, {"choice_id": 1}) and not grade(TF, {"choice_id": 0})


def test_a_game_frozen_before_types_grades_by_correct_id():
    assert correct_ids(OLD_DECK) == [9]
    assert grade(OLD_DECK, {"choice_id": 9}) and not grade(OLD_DECK, {"choice_id": 7})


def test_typed_answers_are_compared_normalised():
    assert grade(TYPED, {"text": "  au "}) and grade(TYPED, {"text": "AURUM!"})
    assert not grade(TYPED, {"text": "Ag"})


def test_slider_tolerance_edges():
    assert grade(SLIDER, {"value": 0.6}) and grade(SLIDER, {"value": 0.4})
    assert not grade(SLIDER, {"value": 0.7})


def test_slider_edges_allow_float_noise():
    assert grade(SLIDER, {"value": 0.30000000000000004 + 0.3}) is True
    assert grade(SLIDER, {"value": 1.0000000000000002}) is False  # in range, just wrong


@pytest.mark.parametrize("q, given", [
    (QUIZ, {"choice_id": 5}), (QUIZ, {"text": "A"}), (TF, {}),
    (TYPED, {"text": "   "}), (TYPED, {"choice_id": 0}),
    (SLIDER, {"value": 2}), (SLIDER, {"value": True}), (SLIDER, {"text": "0.5"}),
])
def test_what_cannot_be_an_answer_is_refused(q, given):
    with pytest.raises(ValueError):
        grade(q, given)


def test_answer_text():
    assert answer_text(QUIZ) == "A / C"
    assert answer_text(TYPED) == "Au / Aurum"
    assert answer_text(SLIDER) == "0.5 ± 0.1 mol"
    assert answer_text({**SLIDER, "tolerance": 0, "unit": "", "answer": 100}) == "100"
    assert answer_text(OLD_DECK) == "Beaker"
    pictures = {"type": "quiz", "choices": [{"id": 0, "image_url": "/x.jpg"}], "correct_ids": [0]}
    assert answer_text(pictures) is None
```

- [ ] **Step 3: Run it to see it fail**

Run: `cd backend && python -m pytest tests/test_grading.py -q`
Expected: FAIL, `ModuleNotFoundError: No module named 'app.grading'`.

- [ ] **Step 4: Write `backend/app/grading.py`**

```python
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
```

- [ ] **Step 5: Run the grading tests**

Run: `cd backend && python -m pytest tests/test_grading.py -q`
Expected: PASS.

- [ ] **Step 6: Write the failing question-rules tests**

`backend/tests/test_quizzes.py` (the API part is added in Task 2):

```python
"""Custom quizzes: the rules a question must meet, freezing, and the API."""

from __future__ import annotations

import pytest

from app import quizzes
from app.quizzes import QuizError, clean_question, clean_quiz, freeze


def quiz_q(**kw):
    q = {"type": "quiz", "text": "Pick B", "time_limit": 20,
         "options": [{"text": "A", "correct": False}, {"text": "B", "correct": True}]}
    q.update(kw)
    return q


def slider_q(**kw):
    q = {"type": "slider", "text": "Boiling point", "min": 0, "max": 200, "step": 1,
         "answer": 100, "tolerance": 2, "unit": "°C"}
    q.update(kw)
    return q


GOOD = [
    quiz_q(),
    {"type": "tf", "text": "Water is wet", "answer": True, "time_limit": 5},
    {"type": "type", "text": "Symbol of gold?", "accepted": ["Au"]},
    slider_q(),
    quiz_q(text="", image="/static/uploads/abc_D-1.jpg",
           options=[{"image": "/static/images/flask-1.jpg", "correct": True}, {"text": "B"}]),
]


@pytest.mark.parametrize("q", GOOD)
def test_good_questions_pass(q):
    clean = clean_question(q)
    assert clean["type"] == q["type"]
    assert clean["time_limit"] == q.get("time_limit", 20)


def test_cleaning_keeps_only_known_fields_and_tidies_text():
    clean = clean_question(quiz_q(text="  Pick\n  B ", extra="x"))
    assert clean == {"type": "quiz", "text": "Pick B", "image": None, "time_limit": 20,
                     "options": [{"text": "A", "image": None, "correct": False},
                                 {"text": "B", "image": None, "correct": True}]}


@pytest.mark.parametrize("q, key", [
    ({"type": "poll", "text": "x"}, "q_type"),
    (quiz_q(time_limit=15), "q_time"),
    (quiz_q(time_limit=True), "q_time"),
    (quiz_q(text=""), "q_text"),
    (quiz_q(text="x" * 301), "q_text_long"),
    (quiz_q(image="https://evil.example/x.jpg"), "q_image"),
    (quiz_q(image="/static/uploads/../../etc"), "q_image"),
    (quiz_q(options=[{"text": "A", "correct": True}]), "q_options"),
    (quiz_q(options=[{"text": str(i), "correct": True} for i in range(5)]), "q_options"),
    (quiz_q(options=[{"text": "", "correct": True}, {"text": "B"}]), "q_option_empty"),
    (quiz_q(options=[{"text": "x" * 76, "correct": True}, {"text": "B"}]), "q_option_long"),
    (quiz_q(options=[{"text": "A"}, {"text": "B"}]), "q_correct"),
    ({"type": "tf", "text": "x", "answer": "yes"}, "q_tf"),
    ({"type": "type", "text": "x", "accepted": []}, "q_accepted"),
    ({"type": "type", "text": "x", "accepted": ["x" * 21]}, "q_accepted"),
    ({"type": "type", "text": "x", "accepted": ["a", "b", "c", "d", "e"]}, "q_accepted"),
    (slider_q(min=10, max=10), "q_slider"),
    (slider_q(step=0), "q_slider"),
    (slider_q(answer=300), "q_slider"),
    (slider_q(tolerance=-1), "q_slider"),
    (slider_q(answer="100"), "q_slider"),
    (slider_q(answer=float("nan")), "q_slider"),
    (slider_q(unit="x" * 11), "q_slider"),
])
def test_each_rule(q, key):
    with pytest.raises(QuizError) as err:
        clean_question(q)
    assert err.value.key == key


def test_accepted_answer_must_survive_normalising():
    for nothing in ("?", "the", "  "):
        with pytest.raises(QuizError):
            clean_question({"type": "type", "text": "x", "accepted": [nothing]})


def test_a_quiz_names_the_question_that_fails():
    body = {"title": "T", "lang": "ru", "questions": [quiz_q(), quiz_q(options=[])]}
    with pytest.raises(QuizError) as err:
        clean_quiz(body)
    assert err.value.question == 2 and err.value.key == "q_options"


@pytest.mark.parametrize("body, key", [
    ({"title": "", "questions": [quiz_q()]}, "quiz_title"),
    ({"title": "x" * 121, "questions": [quiz_q()]}, "quiz_title"),
    ({"title": "T", "questions": []}, "quiz_size"),
    ({"title": "T", "questions": [quiz_q()] * 101}, "quiz_size"),
])
def test_quiz_rules(body, key):
    with pytest.raises(QuizError) as err:
        clean_quiz(body)
    assert err.value.key == key


def test_unknown_language_falls_back_to_english():
    assert clean_quiz({"title": "T", "lang": "de", "questions": [quiz_q()]})["lang"] == "en"


def test_freeze():
    stored = [clean_question(q) for q in GOOD[:4]]
    q1, q2, q3, q4 = freeze(stored, "ru")
    assert q1 == {"position": 1, "type": "quiz", "prompt": "Pick B", "image_url": None, "time_limit": 20,
                  "item": None, "choices": [{"id": 0, "name": "A", "image_url": None},
                                            {"id": 1, "name": "B", "image_url": None}],
                  "correct_ids": [1]}
    assert [c["name"] for c in q2["choices"]] == ["Верно", "Неверно"] and q2["correct_ids"] == [0]
    assert q2["time_limit"] == 5
    assert q3["accepted"] == ["Au"] and "choices" not in q3
    assert (q4["min"], q4["max"], q4["answer"], q4["tolerance"], q4["unit"]) == (0, 200, 100, 2, "°C")
    assert [q["position"] for q in (q1, q2, q3, q4)] == [1, 2, 3, 4]
    assert quizzes.TIME_LIMITS == (5, 10, 20, 30, 60, 90, 120, 240)
```

- [ ] **Step 7: Run it to see it fail**

Run: `cd backend && python -m pytest tests/test_quizzes.py -q`
Expected: FAIL, `ModuleNotFoundError: No module named 'app.quizzes'`.

- [ ] **Step 8: Write `backend/app/quizzes.py`** (without `from_cards`, added in Task 2)

```python
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
import re
from typing import Any, Optional

from fastapi.responses import JSONResponse

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
```

- [ ] **Step 9: Run the tests**

Run: `cd backend && python -m pytest tests/test_quizzes.py tests/test_grading.py tests/test_i18n.py -q`
Expected: PASS (test_i18n checks every message has en and ru).

- [ ] **Step 10: Commit**

```bash
git add backend/app/quizzes.py backend/app/grading.py backend/app/messages.py backend/tests/test_quizzes.py backend/tests/test_grading.py
git commit -m "Custom quizzes: question rules, freezing and grading for four question types"
```

---

### Task 2: The quiz table and `/api/quizzes`

**Files:**
- Modify: `backend/app/models.py` (add `CustomQuiz` after `UserProgress`; add a sentence to the module docstring)
- Modify: `backend/app/quizzes.py` (add `from_cards`)
- Create: `backend/app/routers/quizzes.py`
- Modify: `backend/app/main.py` (include the router)
- Test: `backend/tests/test_quizzes.py` (API part)

**Interfaces:**
- Consumes: `quizzes.clean_quiz`, `quizzes.freeze`, `live._draw(db, asked, pool, mode, rng, lang)`, `crud.list_items(db)`, `account.current_user`, `i18n.request_lang`.
- Produces: `models.CustomQuiz(id, user_id, title, lang, questions, created_at, updated_at)`; `quizzes.from_cards(db, slugs, mode, lang, rng=None) -> list[dict]`; routes `GET/POST /api/quizzes`, `GET/PUT/DELETE /api/quizzes/{id}`, `GET /api/quizzes/{id}/play`, `POST /api/quizzes/from-cards`; helper `routers.quizzes.own_quiz(db, user, quiz_id)`.

- [ ] **Step 1: Write the failing API tests** (append to `backend/tests/test_quizzes.py`)

```python
from test_api import auth, client, sign_in  # noqa: F401,E402 -- the seeded test app


def teacher(client, email="anton@example.com"):
    return auth(sign_in(client, email=email).json()["token"])


BODY = {"title": "Mixed", "lang": "en", "questions": GOOD[:4]}


def test_quiz_crud(client):
    t = teacher(client)
    assert client.get("/api/quizzes", headers=t).json() == []
    made = client.post("/api/quizzes", json=BODY, headers=t)
    assert made.status_code == 201, made.text
    quiz = made.json()
    assert quiz["title"] == "Mixed" and len(quiz["questions"]) == 4

    listed = client.get("/api/quizzes", headers=t).json()
    assert [(q["id"], q["title"], q["question_count"]) for q in listed] == [(quiz["id"], "Mixed", 4)]

    changed = client.put(f"/api/quizzes/{quiz['id']}", json={**BODY, "title": "Renamed"}, headers=t).json()
    assert changed["title"] == "Renamed"
    assert client.get(f"/api/quizzes/{quiz['id']}", headers=t).json()["title"] == "Renamed"

    assert client.delete(f"/api/quizzes/{quiz['id']}", headers=t).status_code == 204
    assert client.get(f"/api/quizzes/{quiz['id']}", headers=t).status_code == 404


def test_quizzes_are_private(client):
    mine = teacher(client)
    theirs = teacher(client, email="bea@example.com")
    quiz_id = client.post("/api/quizzes", json=BODY, headers=theirs).json()["id"]
    assert client.get("/api/quizzes").status_code == 401
    assert client.get("/api/quizzes", headers=mine).json() == []
    for res in (
        client.get(f"/api/quizzes/{quiz_id}", headers=mine),
        client.put(f"/api/quizzes/{quiz_id}", json=BODY, headers=mine),
        client.delete(f"/api/quizzes/{quiz_id}", headers=mine),
        client.get(f"/api/quizzes/{quiz_id}/play", headers=mine),
    ):
        assert res.status_code == 404


def test_a_bad_question_is_named_in_the_request_language(client):
    t = {**teacher(client), "Accept-Language": "ru"}
    body = {**BODY, "questions": [GOOD[0], quiz_q(options=[{"text": "A"}, {"text": "B"}])]}
    res = client.post("/api/quizzes", json=body, headers=t)
    assert res.status_code == 422
    assert res.json() == {"detail": "Отметьте хотя бы один правильный вариант", "code": "q_correct", "question": 2}


def test_play_gives_the_frozen_questions_with_answers(client):
    t = teacher(client)
    quiz_id = client.post("/api/quizzes", json=BODY, headers=t).json()["id"]
    played = client.get(f"/api/quizzes/{quiz_id}/play", headers={**t, "Accept-Language": "ru"}).json()
    assert played["title"] == "Mixed"
    assert played["questions"][0]["correct_ids"] == [1]
    assert played["questions"][1]["choices"][0]["name"] == "Верно"


@pytest.mark.parametrize("mode", ["choice", "inverted"])
def test_questions_from_cards(client, mode):
    t = teacher(client)
    res = client.post("/api/quizzes/from-cards",
                      json={"item_slugs": ["condenser-1", "bubbler-0", "nope"], "mode": mode, "lang": "en"},
                      headers=t)
    assert res.status_code == 200, res.text
    made = res.json()["questions"]
    assert len(made) == 2
    for q in made:
        clean_question(q)  # every drafted question is saveable as it is
        assert q["type"] == "quiz" and len(q["options"]) == 4
        assert sum(o["correct"] for o in q["options"]) == 1
    first = made[0]
    right = next(o for o in first["options"] if o["correct"])
    if mode == "choice":
        assert first["text"] == "What is this?" and first["image"].startswith("/static/images/condenser-1")
        assert right["text"] == "Condenser 1"
    else:
        assert first["text"] == "Find the Condenser 1" and first["image"] is None
        assert right["image"].startswith("/static/images/condenser-1")


def test_from_cards_needs_known_cards(client):
    res = client.post("/api/quizzes/from-cards", json={"item_slugs": ["nope"]}, headers=teacher(client))
    assert res.status_code == 409
```

- [ ] **Step 2: Run them to see them fail**

Run: `cd backend && python -m pytest tests/test_quizzes.py -q`
Expected: the new tests FAIL with 404 on `/api/quizzes`.

- [ ] **Step 3: Add the model** in `backend/app/models.py`, after `UserProgress`:

```python
class CustomQuiz(Base):
    """A teacher's own quiz (the rules are in `app/quizzes.py`).

    The questions are one JSON document, saved whole by the editor. Only the
    author sees the quiz. Games played from it keep their own frozen copy, so
    editing or deleting the quiz leaves past games as they were.
    """

    __tablename__ = "custom_quizzes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(120))
    lang: Mapped[str] = mapped_column(String(2), default="en")
    questions: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
```

Add to the module docstring: `A teacher's own quizzes are CustomQuiz rows (app/quizzes.py).`

- [ ] **Step 4: Add `from_cards` to `backend/app/quizzes.py`**

Add imports `import random` and `from sqlalchemy.orm import Session`, then:

```python
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
```

- [ ] **Step 5: Write `backend/app/routers/quizzes.py`**

```python
"""A signed-in teacher's own quizzes (see app/quizzes.py).

Someone else's quiz answers 404, as if it did not exist.
"""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, quizzes
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
        {"id": q.id, "title": q.title, "question_count": len(q.questions), "updated_at": q.updated_at}
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
```

- [ ] **Step 6: Register the router** in `backend/app/main.py`: import `quizzes` in `from .routers import account, content, live, live_history, quiz, quizzes` and add `app.include_router(quizzes.router)` after `live_history`.

- [ ] **Step 7: Run the tests**

Run: `cd backend && python -m pytest tests/test_quizzes.py -q`
Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add backend/app/models.py backend/app/quizzes.py backend/app/routers/quizzes.py backend/app/main.py backend/tests/test_quizzes.py
git commit -m "Custom quizzes: storage, /api/quizzes, and questions drafted from library cards"
```

---

### Task 3: Picture uploads

**Files:**
- Modify: `backend/app/config.py`, `backend/app/main.py`
- Create: `backend/app/routers/uploads.py`
- Modify: `backend/requirements.txt`, `.github/workflows/ci.yml`, `.gitignore`
- Test: `backend/tests/test_uploads.py`

**Interfaces:**
- Produces: `config.UPLOADS_DIR`, `config.UPLOADS_URL_PREFIX = "/static/uploads"`; `POST /api/uploads` (multipart `file`) → `201 {"url": "/static/uploads/<token>.jpg"}`.

- [ ] **Step 1: Write the failing tests** `backend/tests/test_uploads.py`:

```python
"""Pictures for questions: only real images, made small and plain."""

from __future__ import annotations

import io

import pytest
from PIL import Image

from app import config
from app.quizzes import IMAGE_RE
from test_api import auth, client, sign_in  # noqa: F401 -- the seeded test app


@pytest.fixture()
def uploads(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "UPLOADS_DIR", tmp_path)
    return tmp_path


def png(size=(10, 10), color=(255, 0, 0, 255), mode="RGBA"):
    out = io.BytesIO()
    Image.new(mode, size, color).save(out, "PNG")
    return out.getvalue()


def send(client, data, headers, name="pic.png"):
    return client.post("/api/uploads", files={"file": (name, data, "image/png")}, headers=headers)


def teacher(client):
    return auth(sign_in(client).json()["token"])


def test_an_upload_becomes_a_jpeg_we_serve(client, uploads):
    res = send(client, png(size=(3000, 1000)), teacher(client))
    assert res.status_code == 201, res.text
    url = res.json()["url"]
    assert IMAGE_RE.match(url) and url.endswith(".jpg")
    with Image.open(uploads / url.rsplit("/", 1)[1]) as img:
        assert img.format == "JPEG" and max(img.size) == 1600


def test_transparent_png_gets_a_white_background(client, uploads):
    url = send(client, png(color=(0, 0, 0, 0)), teacher(client)).json()["url"]
    with Image.open(uploads / url.rsplit("/", 1)[1]) as img:
        assert min(img.convert("L").getdata()) > 240


def test_not_a_picture(client, uploads):
    res = send(client, b"%PDF-1.4 hello", teacher(client), name="x.pdf")
    assert res.status_code == 422 and res.json()["code"] == "upload_bad"


def test_too_big(client, uploads, monkeypatch):
    from app.routers import uploads as route
    monkeypatch.setattr(route, "MAX_BYTES", 100)
    res = send(client, png(size=(200, 200), mode="RGB", color=(1, 2, 3)), teacher(client))
    assert res.status_code == 413 and res.json()["code"] == "upload_too_big"


def test_sign_in_required(client, uploads):
    assert send(client, png(), {}).status_code == 401
```

- [ ] **Step 2: Run them to see them fail**

Run: `cd backend && python -m pytest tests/test_uploads.py -q`
Expected: FAIL (404 / `ImportError`).

- [ ] **Step 3: Config** in `backend/app/config.py`, after `IMAGES_URL_PREFIX`:

```python
# Pictures teachers upload for their own quizzes (served from STATIC_DIR too).
UPLOADS_DIR = STATIC_DIR / "uploads"
UPLOADS_URL_PREFIX = "/static/uploads"
```

- [ ] **Step 4: Write `backend/app/routers/uploads.py`**

```python
"""Pictures teachers add to their own questions.

Whatever arrives is opened with Pillow and saved again as a plain JPEG under a
random name: anything that is not an image is refused, metadata (a phone's
GPS position) is dropped, and nothing the uploader named reaches the disk.
"""

from __future__ import annotations

import io
import secrets

from fastapi import APIRouter, Depends, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError

from .. import config, models
from ..i18n import AppError
from .account import current_user

router = APIRouter(prefix="/api/uploads", tags=["quizzes"])

MAX_BYTES = 5 * 1024 * 1024
LONG_SIDE = 1600
# ponytail: uploads are never cleaned up; sweep files no quiz mentions if disk ever matters.


def _flatten(img: Image.Image) -> Image.Image:
    """RGB on white: JPEG has no transparency, and a transparent PNG turns black."""
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        background = Image.new("RGB", img.size, "white")
        background.paste(img, mask=img.getchannel("A"))
        return background
    return img.convert("RGB")


@router.post("", status_code=201)
def upload(file: UploadFile, user: models.User = Depends(current_user)):
    data = file.file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise AppError("upload_too_big", status=413)
    try:
        with Image.open(io.BytesIO(data)) as img:
            img = _flatten(ImageOps.exif_transpose(img))  # upright before EXIF is dropped
            img.thumbnail((LONG_SIDE, LONG_SIDE))
            name = f"{secrets.token_urlsafe(12)}.jpg"
            config.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
            img.save(config.UPLOADS_DIR / name, "JPEG", quality=85)
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise AppError("upload_bad", status=422) from exc
    return {"url": f"{config.UPLOADS_URL_PREFIX}/{name}"}
```

- [ ] **Step 5: Wire it up**
  - `backend/app/main.py`: `from .config import CORS_ORIGINS, IMAGES_DIR, STATIC_DIR, UPLOADS_DIR`; in `lifespan` after `IMAGES_DIR.mkdir(...)` add `UPLOADS_DIR.mkdir(parents=True, exist_ok=True)`; import `uploads` in the routers line and `app.include_router(uploads.router)`.
  - `backend/requirements.txt`: move `Pillow>=10.0` up under `python-multipart>=0.0.9` with the comment line `# question pictures (also used by the catalog pipelines)`.
  - `.github/workflows/ci.yml`: add `"Pillow>=10.0"` to the backend `pip install` line.
  - `.gitignore`: under `# Python / backend` add `backend/static/uploads/`.

- [ ] **Step 6: Run the tests**

Run: `cd backend && python -m pytest tests/test_uploads.py -q`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add backend/app/config.py backend/app/main.py backend/app/routers/uploads.py backend/requirements.txt .github/workflows/ci.yml .gitignore backend/tests/test_uploads.py
git commit -m "Custom quizzes: picture uploads, re-encoded to plain JPEG"
```

---

### Task 4: Import from the Excel / Word template

**Files:**
- Create: `tools/make_quiz_templates.py`
- Create (generated, committed): `public/templates/chemquiz-template.xlsx`, `public/templates/chemquiz-template.docx`
- Create: `backend/app/quiz_import.py`
- Modify: `backend/app/routers/quizzes.py` (`POST /import`)
- Test: `backend/tests/test_quiz_import.py`

**Interfaces:**
- Consumes: `quizzes.clean_question`, `quizzes.QuizError`, `quizzes.TIME_LIMITS`, `quizzes.MAX_QUESTIONS`, `messages.text`.
- Produces: `tools/make_quiz_templates.py` with `xlsx_bytes(rows, notes) -> bytes`, `docx_bytes(rows, notes) -> bytes`, `HEADER`, `EXAMPLES`; `quiz_import.read_rows(data) -> list[tuple[int, list[str]]]`, `quiz_import.row_to_question(cells) -> dict`, `quiz_import.parse(data, lang) -> (questions, errors)`; route `POST /api/quizzes/import` → `{"questions": [...], "errors": [{"row", "message"}]}`.

- [ ] **Step 1: Write the template maker** `tools/make_quiz_templates.py`:

```python
"""Write the import templates teachers download: public/templates/chemquiz-template.xlsx and .docx.

Plain OOXML written with zipfile, so no Office library is needed. Run from the
repository root after changing the examples, and commit both files:

    python tools/make_quiz_templates.py

backend/app/quiz_import.py reads what this writes (its tests parse these files).
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "public" / "templates"

HEADER = ["Тип / Type", "Вопрос / Question", "Ответ 1 / Answer 1", "Ответ 2 / Answer 2",
          "Ответ 3 / Answer 3", "Ответ 4 / Answer 4", "Время, с / Time, s", "Правильный / Correct"]
EXAMPLES = [
    ["квиз", "В какой колбе удобно перегонять жидкость?", "Колба Вюрца", "Мерная колба",
     "Коническая колба", "Колба Бунзена", "20", "1"],
    ["квиз", "Какие из этих веществ — кислоты?", "HCl", "NaOH", "H2SO4", "NaCl", "30", "1, 3"],
    ["верно-неверно", "Колбу Бунзена используют для фильтрования под вакуумом", "", "", "", "", "10", "верно"],
    ["ввод", "Химический символ золота?", "Au", "", "", "", "20", ""],
    ["ползунок", "Температура кипения воды при нормальном давлении", "0", "200", "2", "°C", "20", "100"],
]
NOTES = [
    "Как заполнять (How to fill this in)",
    "Одна строка — один вопрос. Первая строка — заголовок, её не трогайте.",
    "Тип: квиз, верно-неверно, ввод, ползунок (или quiz, tf, type, slider). Пусто — квиз.",
    "Квиз: 2–4 ответа; в «Правильный» — номера верных ответов через запятую (1 или 2, 4).",
    "Верно-неверно: в «Правильный» — верно или неверно; ответы не нужны.",
    "Ввод: в ответах 1–4 — допустимые варианты ответа (до 20 символов).",
    "Ползунок: ответ 1 — минимум, ответ 2 — максимум, ответ 3 — допуск (±), ответ 4 — единицы; в «Правильный» — значение.",
    "Время: 5, 10, 20, 30, 60, 90, 120 или 240 секунд; пусто — 20.",
    "Картинки добавляются потом, в редакторе.",
]

_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'


def _zip(files: dict[str, str]) -> bytes:
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name, body in files.items():
            z.writestr(name, body)
    return out.getvalue()


def _col(index: int) -> str:
    letters = ""
    index += 1
    while index:
        index, rest = divmod(index - 1, 26)
        letters = chr(65 + rest) + letters
    return letters


def _sheet(rows: list[list[str]], widths: list[int]) -> str:
    cols = "".join(f'<col min="{i}" max="{i}" width="{w}" customWidth="1"/>' for i, w in enumerate(widths, 1))
    body = []
    for r, row in enumerate(rows, start=1):
        cells = "".join(
            f'<c r="{_col(c)}{r}" t="inlineStr"><is><t xml:space="preserve">{escape(v)}</t></is></c>'
            for c, v in enumerate(row) if v != ""
        )
        body.append(f'<row r="{r}">{cells}</row>')
    return f'{_XML}<worksheet xmlns="{_MAIN}"><cols>{cols}</cols><sheetData>{"".join(body)}</sheetData></worksheet>'


def xlsx_bytes(rows: list[list[str]], notes: list[str]) -> bytes:
    """A workbook: the questions on the first sheet, the notes on a second one."""
    return _zip({
        "[Content_Types].xml": (
            f'{_XML}<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            '<Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            '</Types>'
        ),
        "_rels/.rels": (
            f'{_XML}<Relationships xmlns="{_PKG}">'
            f'<Relationship Id="rId1" Type="{_REL}/officeDocument" Target="xl/workbook.xml"/></Relationships>'
        ),
        "xl/workbook.xml": (
            f'{_XML}<workbook xmlns="{_MAIN}" xmlns:r="{_REL}"><sheets>'
            '<sheet name="Вопросы" sheetId="1" r:id="rId1"/><sheet name="Инструкция" sheetId="2" r:id="rId2"/>'
            '</sheets></workbook>'
        ),
        "xl/_rels/workbook.xml.rels": (
            f'{_XML}<Relationships xmlns="{_PKG}">'
            f'<Relationship Id="rId1" Type="{_REL}/worksheet" Target="worksheets/sheet1.xml"/>'
            f'<Relationship Id="rId2" Type="{_REL}/worksheet" Target="worksheets/sheet2.xml"/>'
            '</Relationships>'
        ),
        "xl/worksheets/sheet1.xml": _sheet(rows, [16, 60, 22, 22, 22, 22, 14, 18]),
        "xl/worksheets/sheet2.xml": _sheet([[n] for n in notes], [120]),
    })


def docx_bytes(rows: list[list[str]], notes: list[str]) -> bytes:
    """A document: the notes as paragraphs, then the questions as a bordered table."""
    def para(text, bold=False):
        props = "<w:rPr><w:b/></w:rPr>" if bold else ""
        return f'<w:p><w:r>{props}<w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>'

    border = "".join(f'<w:{side} w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
                     for side in ("top", "left", "bottom", "right", "insideH", "insideV"))
    table_rows = "".join(
        "<w:tr>" + "".join(f"<w:tc>{para(v, bold=(r == 0))}</w:tc>" for v in row) + "</w:tr>"
        for r, row in enumerate(rows)
    )
    landscape = '<w:sectPr><w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/></w:sectPr>'
    document = (
        f'{_XML}<w:document xmlns:w="{_W}"><w:body>'
        + "".join(para(n, bold=(i == 0)) for i, n in enumerate(notes))
        + f'<w:tbl><w:tblPr><w:tblBorders>{border}</w:tblBorders></w:tblPr>{table_rows}</w:tbl>'
        + para("") + landscape + "</w:body></w:document>"
    )
    return _zip({
        "[Content_Types].xml": (
            f'{_XML}<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '</Types>'
        ),
        "_rels/.rels": (
            f'{_XML}<Relationships xmlns="{_PKG}">'
            f'<Relationship Id="rId1" Type="{_REL}/officeDocument" Target="word/document.xml"/></Relationships>'
        ),
        "word/document.xml": document,
    })


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [HEADER, *EXAMPLES]
    (OUT / "chemquiz-template.xlsx").write_bytes(xlsx_bytes(rows, NOTES))
    (OUT / "chemquiz-template.docx").write_bytes(docx_bytes(rows, NOTES))
    print(f"wrote {OUT}/chemquiz-template.xlsx and .docx")
```

- [ ] **Step 2: Generate the templates**

Run: `python tools/make_quiz_templates.py`
Expected: `wrote …/public/templates/chemquiz-template.xlsx and .docx`. Open both once (Excel/Numbers/LibreOffice and Word/Pages) to check they open with the table visible; if Excel complains, report it rather than switching to a library.

- [ ] **Step 3: Write the failing import tests** `backend/tests/test_quiz_import.py`:

```python
"""Questions from a filled-in Excel or Word template."""

from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

import pytest

from app import quiz_import
from app.i18n import AppError
from test_api import auth, client, sign_in  # noqa: F401 -- the seeded test app

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from make_quiz_templates import EXAMPLES, HEADER, docx_bytes, xlsx_bytes  # noqa: E402

TEMPLATES = ROOT / "public" / "templates"

EXPECTED = [
    {"type": "quiz", "text": "В какой колбе удобно перегонять жидкость?", "image": None, "time_limit": 20,
     "options": [{"text": "Колба Вюрца", "image": None, "correct": True},
                 {"text": "Мерная колба", "image": None, "correct": False},
                 {"text": "Коническая колба", "image": None, "correct": False},
                 {"text": "Колба Бунзена", "image": None, "correct": False}]},
    {"type": "quiz", "text": "Какие из этих веществ — кислоты?", "image": None, "time_limit": 30,
     "options": [{"text": "HCl", "image": None, "correct": True},
                 {"text": "NaOH", "image": None, "correct": False},
                 {"text": "H2SO4", "image": None, "correct": True},
                 {"text": "NaCl", "image": None, "correct": False}]},
    {"type": "tf", "text": "Колбу Бунзена используют для фильтрования под вакуумом", "image": None,
     "time_limit": 10, "answer": True},
    {"type": "type", "text": "Химический символ золота?", "image": None, "time_limit": 20, "accepted": ["Au"]},
    {"type": "slider", "text": "Температура кипения воды при нормальном давлении", "image": None,
     "time_limit": 20, "min": 0, "max": 200, "step": 1, "answer": 100, "tolerance": 2, "unit": "°C"},
]


@pytest.mark.parametrize("name", ["chemquiz-template.xlsx", "chemquiz-template.docx"])
def test_the_templates_import_as_their_examples(name):
    questions, errors = quiz_import.parse((TEMPLATES / name).read_bytes(), "ru")
    assert errors == []
    assert questions == EXPECTED


@pytest.mark.parametrize("make", [xlsx_bytes, docx_bytes])
def test_a_bad_row_is_reported_and_the_rest_still_import(make):
    rows = [HEADER, EXAMPLES[0], ["квиз", "Нет правильного", "A", "B", "", "", "", "3"],
            ["", "", "", "", "", "", "", ""], ["опрос", "?", "", "", "", "", "", ""], EXAMPLES[3]]
    questions, errors = quiz_import.parse(make(rows, ["notes"]), "en")
    assert [q["text"] for q in questions] == [EXPECTED[0]["text"], EXPECTED[3]["text"]]
    assert errors == [{"row": 3, "message": "Mark at least one answer as correct"},
                      {"row": 5, "message": "Unknown type in the Type column"}]


def test_correct_numbers_survive_excel_decimal_comma():
    # Russian Excel stores a typed "1,2" as the number 1.2.
    q = quiz_import.row_to_question(["", "Q", "A", "B", "C", "", "", "1.2"])
    assert [o["correct"] for o in q["options"]] == [True, True, False]


def test_slider_numbers_with_a_decimal_comma_and_fractional_step():
    q = quiz_import.row_to_question(["ползунок", "pH", "0", "14", "0,5", "", "", "7,4"])
    assert (q["min"], q["max"], q["tolerance"], q["answer"], q["step"]) == (0, 14, 0.5, 7.4, 0.1)


@pytest.mark.parametrize("cell, limit", [("", 20), ("15", 20), ("3", 5), ("240", 240), ("999", 240)])
def test_time_is_rounded_up_to_an_allowed_limit(cell, limit):
    assert quiz_import.row_to_question(["ввод", "Q", "x", "", "", "", cell, ""])["time_limit"] == limit


def test_a_question_containing_the_word_question_is_not_a_header():
    rows = [HEADER, ["ввод", "Вопрос на засыпку: символ золота?", "Au", "", "", "", "", ""]]
    questions, _ = quiz_import.parse(xlsx_bytes(rows, []), "ru")
    assert len(questions) == 1


def test_only_the_first_hundred_questions():
    rows = [HEADER] + [EXAMPLES[3]] * 101
    questions, errors = quiz_import.parse(xlsx_bytes(rows, []), "en")
    assert len(questions) == 100
    assert errors == [{"row": 102, "message": "Only the first 100 questions were imported"}]


def test_not_an_office_file():
    with pytest.raises(AppError) as err:
        quiz_import.parse(b"hello", "en")
    assert err.value.key == "import_bad_file"


def test_a_zip_bomb_is_refused():
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("word/document.xml", "0" * (21 * 1024 * 1024))
    with pytest.raises(AppError) as err:
        quiz_import.parse(out.getvalue(), "en")
    assert err.value.key == "import_too_big"


def test_a_word_file_without_a_table():
    with pytest.raises(AppError) as err:
        quiz_import.parse(zipfile_without_table(), "en")
    assert err.value.key == "import_no_table"


def zipfile_without_table() -> bytes:
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as z:
        z.writestr("word/document.xml",
                   '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                   "<w:body><w:p/></w:body></w:document>")
    return out.getvalue()


def test_import_endpoint(client):
    t = auth(sign_in(client).json()["token"])
    data = (TEMPLATES / "chemquiz-template.xlsx").read_bytes()
    res = client.post("/api/quizzes/import", files={"file": ("q.xlsx", data)}, headers=t)
    assert res.status_code == 200, res.text
    assert len(res.json()["questions"]) == 5 and res.json()["errors"] == []
    assert client.post("/api/quizzes/import", files={"file": ("q.xlsx", data)}).status_code == 401
```

- [ ] **Step 4: Run them to see them fail**

Run: `cd backend && python -m pytest tests/test_quiz_import.py -q`
Expected: FAIL, `ImportError: cannot import name 'quiz_import'`.

- [ ] **Step 5: Write `backend/app/quiz_import.py`**

```python
"""Questions from a filled-in template: the first sheet of an Excel workbook
or the first table of a Word document (tools/make_quiz_templates.py writes
both templates).

Columns, Kahoot-style: Type | Question | Answer 1-4 | Time (s) | Correct.
Each row is checked by `quizzes.clean_question`; a row that fails is reported
by its number and skipped, the others still come in. Nothing is saved here:
the editor shows the result and the teacher saves it.

Read with the standard library: an .xlsx or .docx is a zip of XML.
"""

from __future__ import annotations

import io
import re
import zipfile
import xml.etree.ElementTree as ET

from . import messages
from .i18n import AppError
from .quizzes import MAX_QUESTIONS, TIME_LIMITS, QuizError, clean_question

MAX_FILE = 2 * 1024 * 1024
# A zip is small on the wire and may be huge inside.
MAX_UNPACKED = 20 * 1024 * 1024
COLUMNS = 8

_S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

TYPES = {
    "": "quiz", "quiz": "quiz", "квиз": "quiz",
    "tf": "tf", "true/false": "tf", "true-false": "tf", "верно-неверно": "tf", "верно/неверно": "tf",
    "type": "type", "ввод": "type",
    "slider": "slider", "ползунок": "slider",
}
TRUE = {"true", "верно", "да", "yes", "1"}
FALSE = {"false", "неверно", "нет", "no", "0"}
HEADER_START = ("вопрос", "question")


def read_rows(data: bytes) -> list[tuple[int, list[str]]]:
    """(row number, cell texts) for each row of the file's question table."""
    if len(data) > MAX_FILE:
        raise AppError("import_too_big", status=413)
    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
        if sum(i.file_size for i in archive.infolist()) > MAX_UNPACKED:
            raise AppError("import_too_big", status=413)
        names = set(archive.namelist())
        if "xl/workbook.xml" in names:
            return _xlsx_rows(archive)
        if "word/document.xml" in names:
            return _docx_rows(archive)
    except (zipfile.BadZipFile, ET.ParseError, KeyError, StopIteration, IndexError, ValueError):
        pass
    raise AppError("import_bad_file", status=422)


def _column(ref: str, fallback: int) -> int:
    """"C5" -> 2."""
    letters = re.match(r"[A-Z]*", ref).group()
    if not letters:
        return fallback
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1


def _first_sheet(archive: zipfile.ZipFile) -> str:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    rid = workbook.find(f"{_S}sheets/{_S}sheet").get(f"{_R}id")
    rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    target = next(r.get("Target") for r in rels if r.get("Id") == rid)
    return target.lstrip("/") if target.startswith("/") else f"xl/{target}"


def _xlsx_rows(archive: zipfile.ZipFile) -> list[tuple[int, list[str]]]:
    shared = []
    if "xl/sharedStrings.xml" in archive.namelist():
        for si in ET.fromstring(archive.read("xl/sharedStrings.xml")).iter(f"{_S}si"):
            shared.append("".join(t.text or "" for t in si.iter(f"{_S}t")))
    rows = []
    for index, row in enumerate(ET.fromstring(archive.read(_first_sheet(archive))).iter(f"{_S}row"), 1):
        cells: dict[int, str] = {}
        for position, c in enumerate(row.iter(f"{_S}c")):
            kind = c.get("t")
            if kind == "inlineStr":
                value = "".join(t.text or "" for t in c.iter(f"{_S}t"))
            else:
                v = c.find(f"{_S}v")
                value = v.text if v is not None and v.text else ""
                if kind == "s" and value:
                    value = shared[int(value)]
                elif kind == "b":
                    value = "true" if value == "1" else "false"
            cells[_column(c.get("r", ""), position)] = value.strip()
        width = max(cells, default=-1) + 1
        rows.append((int(row.get("r") or index), [cells.get(i, "") for i in range(width)]))
    return rows


def _docx_rows(archive: zipfile.ZipFile) -> list[tuple[int, list[str]]]:
    table = ET.fromstring(archive.read("word/document.xml")).find(f".//{_W}tbl")
    if table is None:
        raise AppError("import_no_table", status=422)
    rows = []
    for number, tr in enumerate(table.findall(f"{_W}tr"), start=1):
        row = []
        for tc in tr.findall(f"{_W}tc"):
            paragraphs = ("".join(t.text or "" for t in p.iter(f"{_W}t")).strip() for p in tc.findall(f"{_W}p"))
            row.append(" ".join(p for p in paragraphs if p))
        rows.append((number, row))
    return rows


def _number(cell: str) -> float:
    try:
        value = float(cell.replace(",", ".").replace(" ", "").replace(" ", ""))
    except ValueError as exc:
        raise QuizError("q_slider") from exc
    return int(value) if value.is_integer() else value


def _time(cell: str) -> int:
    if not cell.strip():
        return 20
    try:
        seconds = float(cell.replace(",", "."))
    except ValueError as exc:
        raise QuizError("q_time") from exc
    return next((t for t in TIME_LIMITS if t >= seconds), TIME_LIMITS[-1])


def row_to_question(cells: list[str]) -> dict:
    """One row (8 cells) as a question in the stored shape, not yet checked."""
    kind_cell, text, a1, a2, a3, a4, time_cell, correct = (list(cells) + [""] * COLUMNS)[:COLUMNS]
    kind = TYPES.get(kind_cell.strip().lower().replace(" ", ""))
    if kind is None:
        raise QuizError("import_type")
    q = {"type": kind, "text": text, "time_limit": _time(time_cell)}
    answers = [a1, a2, a3, a4]
    if kind == "quiz":
        # Any non-digit separates the numbers: "1, 3", "1;3", and Russian
        # Excel's 1.2 for a typed "1,2".
        picked = {int(n) for n in re.findall(r"\d+", correct)}
        if not picked:
            raise QuizError("import_correct")
        q["options"] = [{"text": a, "image": None, "correct": i in picked}
                        for i, a in enumerate(answers, start=1) if a]
    elif kind == "tf":
        word = correct.strip().lower()
        if word not in TRUE | FALSE:
            raise QuizError("import_correct")
        q["answer"] = word in TRUE
    elif kind == "type":
        q["accepted"] = [a for a in answers if a]
    else:
        lo, hi, value = _number(a1), _number(a2), _number(correct)
        tolerance = _number(a3) if a3.strip() else 0
        fractional = any(isinstance(x, float) for x in (lo, hi, tolerance, value))
        q.update(min=lo, max=hi, step=0.1 if fractional else 1, answer=value, tolerance=tolerance, unit=a4)
    return q


def parse(data: bytes, lang: str) -> tuple[list[dict], list[dict]]:
    """The file's questions, checked, and an error for each row that failed."""
    questions: list[dict] = []
    errors: list[dict] = []
    header_seen = False
    for number, cells in read_rows(data):
        if not any(cells):
            continue
        question_cell = (cells[1] if len(cells) > 1 else "").strip().lower()
        # The header: the first row, if its Question cell says so. Only once, so
        # a first question that starts with "Вопрос..." is still a question.
        if not header_seen and not questions and not errors and question_cell.startswith(HEADER_START):
            header_seen = True
            continue
        if len(questions) >= MAX_QUESTIONS:
            errors.append({"row": number, "message": messages.text("import_too_many", lang)})
            break
        try:
            questions.append(clean_question(row_to_question(cells)))
        except QuizError as exc:
            errors.append({"row": number, "message": messages.text(exc.key, lang)})
    return questions, errors
```

- [ ] **Step 6: Add the endpoint** to `backend/app/routers/quizzes.py`, before `@router.get("/{quiz_id}")`:

```python
@router.post("/import")
def import_file(file: UploadFile, lang: str = Depends(request_lang),
                user: models.User = Depends(current_user)):
    """Questions from a filled-in template, for the editor to show; nothing is saved."""
    questions, errors = quiz_import.parse(file.file.read(quiz_import.MAX_FILE + 1), lang)
    return {"questions": questions, "errors": errors}
```

Add `UploadFile` to the fastapi import and `quiz_import` to `from .. import models, quizzes, quiz_import`.

- [ ] **Step 7: Run the tests**

Run: `cd backend && python -m pytest tests/test_quiz_import.py -q`
Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add tools/make_quiz_templates.py public/templates backend/app/quiz_import.py backend/app/routers/quizzes.py backend/tests/test_quiz_import.py
git commit -m "Custom quizzes: import questions from the Excel or Word template"
```

---

### Task 5: Class games on a custom quiz

**Files:**
- Modify: `backend/app/models.py` (`LiveGame.custom_quiz_id`, `LiveAnswer.answer`, `LiveGame.mode` comment)
- Modify: `backend/app/live.py`
- Modify: `backend/app/routers/live.py`
- Test: `backend/tests/test_live.py` (append)

**Interfaces:**
- Consumes: `grading.grade/correct_ids/answer_text/CHOICE_TYPES/kind`, `quizzes.freeze`, `routers.quizzes.own_quiz`.
- Produces: `live.create_custom_room(db, *, questions, title, quiz_id, host_user, lang, rng=None) -> Room`; `Room.time_limit() -> int`; `Room.answer(player, position, given: dict, now)`; snapshot question gains `type`, `time_limit`, slider `min/max/step/unit`; reveal gains `type`, `correct_ids`, `answer_text`; `you.answered` (bool) and `you.answer` (text). `POST /api/live` accepts `custom_quiz_id`. Answer body: `{position, choice_id}` | `{position, text}` | `{position, value}`.

- [ ] **Step 1: Write the failing tests** (append to `backend/tests/test_live.py`):

```python
# --- custom quizzes -------------------------------------------------------------

CUSTOM = {
    "title": "Mixed",
    "lang": "en",
    "questions": [
        {"type": "quiz", "text": "Pick B", "time_limit": 10,
         "options": [{"text": "A"}, {"text": "B", "correct": True}]},
        {"type": "tf", "text": "Water is wet", "time_limit": 5, "answer": True},
        {"type": "type", "text": "Symbol of gold?", "time_limit": 30, "accepted": ["Au"]},
        {"type": "slider", "text": "Boiling point", "time_limit": 20, "min": 0, "max": 200, "step": 1,
         "answer": 100, "tolerance": 2, "unit": "°C"},
    ],
}
RIGHT = [{"choice_id": 1}, {"choice_id": 0}, {"text": " au "}, {"value": 101}]


def custom_room(client, headers, quiz=CUSTOM, lang="en"):
    quiz_id = client.post("/api/quizzes", json=quiz, headers=headers).json()["id"]
    res = client.post("/api/live", json={"custom_quiz_id": quiz_id, "lang": lang}, headers=headers)
    assert res.status_code == 201, res.text
    return res.json()


def test_a_custom_quiz_plays_every_question_type(client, clock):
    t = teacher(client)
    room = custom_room(client, t)
    pin, token = room["pin"], room["host_token"]
    assert (room["mode"], room["question_count"], room["category_name"]) == ("custom", 4, "Mixed")
    ann = join(client, pin, "Ann")["token"]
    for position, (given, limit) in enumerate(zip(RIGHT, [10, 5, 30, 20]), start=1):
        board = client.post(f"/api/live/{pin}/next", headers=host(token)).json()
        assert board["time_limit"] == limit and board["deadline"] - board["starts_at"] == limit
        assert board["question"]["type"] == CUSTOM["questions"][position - 1]["type"]
        clock.advance(live.READ_SECONDS)
        me = client.post(f"/api/live/{pin}/answer", json={"position": position, **given}, headers=host(ann))
        assert me.status_code == 200, me.text
        assert me.json()["you"]["result"]["correct"] is True  # the only player answered: revealed
        assert me.json()["reveal"]["answer_text"]
        client.post(f"/api/live/{pin}/next", headers=host(token))  # standings
    # Instant right answers: 1000 each, plus 100, 200 and 300 for the streak.
    assert client.get(f"/api/live/{pin}/me", headers=host(ann)).json()["you"]["score"] == 4600


def test_points_shrink_over_the_questions_own_time(client, clock):
    t = teacher(client)
    room = custom_room(client, t)
    pin, token = room["pin"], room["host_token"]
    ann = join(client, pin, "Ann")["token"]
    client.post(f"/api/live/{pin}/next", headers=host(token))
    clock.advance(live.READ_SECONDS + 5)  # half of question 1's 10 seconds
    me = client.post(f"/api/live/{pin}/answer", json={"position": 1, "choice_id": 1}, headers=host(ann)).json()
    assert me["you"]["result"]["points"] == 750


def test_a_custom_question_does_not_give_its_answer_away(client, clock):
    t = teacher(client)
    room = custom_room(client, t)
    pin, token = room["pin"], room["host_token"]
    ann = join(client, pin, "Ann")["token"]
    secret = {"correct_ids", "correct_id", "accepted", "answer", "tolerance", "item"}
    for _ in CUSTOM["questions"]:
        board = client.post(f"/api/live/{pin}/next", headers=host(token)).json()
        phone = client.get(f"/api/live/{pin}/me", headers=host(ann)).json()
        for view in (board["question"], phone["question"]):
            assert not secret & set(view), view
        assert board["reveal"] is None and phone["reveal"] is None
        client.post(f"/api/live/{pin}/next", headers=host(token))  # close
        client.post(f"/api/live/{pin}/next", headers=host(token))  # standings


@pytest.mark.parametrize("position, given", [
    (1, {"choice_id": 7}), (1, {"text": "B"}), (3, {"text": "   "}), (3, {"choice_id": 0}),
    (4, {"value": 201}), (4, {}),
])
def test_answers_that_do_not_fit_the_question(client, clock, position, given):
    t = teacher(client)
    room = custom_room(client, t)
    pin, token = room["pin"], room["host_token"]
    ann = join(client, pin, "Ann")["token"]
    for _ in range(position - 1):
        for _ in range(3):
            client.post(f"/api/live/{pin}/next", headers=host(token))  # open, close, standings
    client.post(f"/api/live/{pin}/next", headers=host(token))
    clock.advance(live.READ_SECONDS)
    res = client.post(f"/api/live/{pin}/answer", json={"position": position, **given}, headers=host(ann))
    assert res.status_code == 422 and res.json()["code"] == "not_an_option"


def test_true_false_speaks_the_games_language(client, clock):
    t = teacher(client)
    room = custom_room(client, t, lang="ru")
    pin, token = room["pin"], room["host_token"]
    join(client, pin, "Ann")
    for _ in range(3):
        client.post(f"/api/live/{pin}/next", headers=host(token))
    board = client.post(f"/api/live/{pin}/next", headers=host(token)).json()
    assert [c["name"] for c in board["question"]["choices"]] == ["Верно", "Неверно"]


def test_a_custom_game_needs_your_own_quiz(client, clock):
    mine = teacher(client)
    quiz_id = client.post("/api/quizzes", json=CUSTOM, headers=mine).json()["id"]
    theirs = auth(sign_in(client, name="Bea", email="bea@example.com").json()["token"])
    assert client.post("/api/live", json={"custom_quiz_id": quiz_id}).status_code == 401
    assert client.post("/api/live", json={"custom_quiz_id": quiz_id}, headers=theirs).status_code == 404


def test_a_game_frozen_before_question_types_still_plays(client, clock):
    room = make_room(client, question_count=1)
    pin, token = room["pin"], room["host_token"]
    with client.session_factory() as db:
        game = db.scalars(select(models.LiveGame).where(models.LiveGame.pin == pin)).one()
        game.questions = [{k: v for k, v in q.items() if k not in ("type", "correct_ids", "time_limit")}
                          for q in game.questions]
        db.commit()
    ann = join(client, pin, "Ann")["token"]
    board = client.post(f"/api/live/{pin}/next", headers=host(token)).json()
    assert board["time_limit"] == 20 and board["question"]["type"] == "quiz"
    clock.advance(live.READ_SECONDS)
    right = correct_id(client, pin, 1)
    me = client.post(f"/api/live/{pin}/answer", json={"position": 1, "choice_id": right}, headers=host(ann)).json()
    assert me["you"]["result"]["correct"] is True
    assert me["reveal"]["correct_ids"] == [right] and me["reveal"]["item"]["id"] == right
```

- [ ] **Step 2: Run them to see them fail**

Run: `cd backend && python -m pytest tests/test_live.py -q -k "custom or frozen or fit or language"`
Expected: FAIL (`custom_quiz_id` ignored → 404 deck / KeyError).

- [ ] **Step 3: Models.** In `LiveGame`, change the `mode` comment to `# "choice" or "inverted" (a deck game, as in QuizSession) or "custom" (a teacher's own quiz).` and add after `category_name`:

```python
    # The teacher's own quiz this game was made from (custom games), for
    # "Same settings". No foreign key: the quiz may be deleted, the game stays.
    custom_quiz_id: Mapped[Optional[int]] = mapped_column(Integer, default=None)
```

In `LiveAnswer`, change `choice_id` and add `answer`:

```python
    # The option picked; -1 for a typed or slider answer (the column is NOT
    # NULL in databases made before those existed).
    choice_id: Mapped[int] = mapped_column(Integer)
    # What was typed, or the slider's value.
    answer: Mapped[Optional[str]] = mapped_column(String(100), default=None)
```

- [ ] **Step 4: `live.py` — deck questions carry a type.** In `_draw`, in the appended dict add `"type": "quiz",` as the first key and `"correct_ids": [item.id],` after `"correct_id": item.id,`. Add `from . import crud, grading, models` (replace the existing `from . import crud, models`).

- [ ] **Step 5: `live.py` — per-question clock.** Add to `Room`, under `# -- lookups --`:

```python
    def time_limit(self) -> int:
        """Seconds for the question on screen: its own (custom quizzes) or the game's."""
        q = self.question
        return (q or {}).get("time_limit") or self.game.time_limit
```

In `_open_question`, change `game.deadline = game.starts_at + game.time_limit` to `game.deadline = game.starts_at + self.time_limit()` (the position is already set two lines above). In `_clock`, change `"time_limit": game.time_limit,` to `"time_limit": room.time_limit(),`.

- [ ] **Step 6: `live.py` — answers of every kind.** Replace `Room.answer` with:

```python
    def answer(
        self, player: models.LivePlayer, position: int, given: dict, now: float
    ) -> models.LiveAnswer:
        """`given` is {"choice_id"}, {"text"} or {"value"}, whichever the question asks for."""
        self.tick(now)
        game = self.game
        question = self.question
        if game.phase != "question" or question is None or position != game.position:
            raise LiveError("too_late")
        if now < (game.starts_at or 0):
            raise LiveError("not_open_yet")
        if player.id in self.answers:
            raise LiveError("already_answered")
        try:
            correct = grading.grade(question, given)
        except ValueError:
            raise LiveError("not_an_option", status=422) from None

        limit = self.time_limit()
        elapsed = max(0.0, min(now - game.starts_at, float(limit)))
        points = 0
        if correct:
            player.streak += 1
            fraction = elapsed / limit
            points = round(MAX_POINTS - (MAX_POINTS - MIN_POINTS) * fraction)
            points += min((player.streak - 1) * STREAK_BONUS, STREAK_BONUS_CAP)
        else:
            player.streak = 0
        player.score += points

        choice = grading.kind(question) in grading.CHOICE_TYPES
        typed = given.get("text") if "text" in given else given.get("value")
        answer = models.LiveAnswer(
            game_id=game.id,
            player_id=player.id,
            position=position,
            choice_id=given["choice_id"] if choice else -1,
            answer=None if choice else str(typed).strip()[:100],
            elapsed=elapsed,
            correct=correct,
            points=points,
        )
        self.db.add(answer)
        self.answers[player.id] = answer
        self.tick(now)
        return answer
```

- [ ] **Step 7: `live.py` — opening a room from a custom quiz.** Split the PIN loop out of `create_room`: move everything from `now = _now()` to the final `raise LiveError("no_free_pins", status=503)` into

```python
def _open(db: Session, settings: dict, rng: random.Random) -> Room:
    """A new room with these settings and a free PIN."""
    now = _now()
    purge(db, now)
    # (the existing `for _ in range(PIN_TRIES): ...` loop, unchanged)
    raise LiveError("no_free_pins", status=503)
```

and end `create_room` with `return _open(db, settings, rng)`. Then add:

```python
def create_custom_room(
    db: Session,
    *,
    questions: list[dict],
    title: str,
    quiz_id: Optional[int],
    host_user: Optional[models.User] = None,
    lang: str = "en",
    rng: Optional[random.Random] = None,
) -> Room:
    """Open a room for frozen questions from a teacher's own quiz (see
    quizzes.freeze), in order. Also used by "Work on mistakes" with a subset."""
    if not questions:
        raise LiveError("no_items")
    questions = [{**q, "position": n} for n, q in enumerate(questions, start=1)]
    settings = dict(
        host_user_id=host_user.id if host_user else None,
        mode="custom",
        time_limit=max(q.get("time_limit") or DEFAULT_TIME_LIMIT for q in questions),
        question_count=len(questions),
        category_id=None,
        category_slug=None,
        category_name=title,
        custom_quiz_id=quiz_id,
        lang=lang,
        questions=questions,
    )
    return _open(db, settings, rng or random.SystemRandom())
```

- [ ] **Step 8: `live.py` — what the board and phones see.** Replace `_question_public` and the return of `_reveal`:

```python
def _question_public(q: dict) -> dict:
    """The question without its answer."""
    kind = grading.kind(q)
    out = {
        "position": q["position"],
        "type": kind,
        "image_url": q["image_url"],
        "prompt": q["prompt"],
        "time_limit": q.get("time_limit"),
    }
    if kind in grading.CHOICE_TYPES:
        out["choices"] = q["choices"]
    if kind == "slider":
        out.update({k: q[k] for k in ("min", "max", "step", "unit")})
    return out
```

In `_reveal`: build `counts` only for choice questions (`counts = {c["id"]: 0 for c in q.get("choices", [])}`; the loop already only counts ids in `counts`), and return:

```python
    return {
        "type": grading.kind(q),
        "correct_id": q.get("correct_id"),
        "correct_ids": grading.correct_ids(q) if q.get("choices") else [],
        "item": q.get("item"),
        "answer_text": grading.answer_text(q),
        "counts": [{"id": cid, "count": n} for cid, n in counts.items()],
        "right_count": right,
    }
```

In `player_view`'s `you`, add after `"answered_id"`:

```python
        "answered": answer is not None,
        "answer": answer.answer if answer else None,
```

- [ ] **Step 9: Router.** In `backend/app/routers/live.py`:

```python
class CreateIn(BaseModel):
    category_slug: Optional[str] = None
    custom_quiz_id: Optional[int] = None
    mode: str = "choice"
    question_count: int = Field(10, ge=1, le=MAX_QUESTION_COUNT)
    time_limit: int = live.DEFAULT_TIME_LIMIT
    lang: Literal["en", "ru"] = "en"


class AnswerIn(BaseModel):
    position: int
    choice_id: Optional[int] = None
    text: Optional[str] = Field(None, max_length=100)
    value: Optional[float] = None
```

At the top of `create`, before the mode check:

```python
    if payload.custom_quiz_id is not None:
        if user is None:
            raise AppError("sign_in_required", status=401)
        quiz = own_quiz(db, user, payload.custom_quiz_id)
        try:
            room = live.create_custom_room(
                db,
                questions=quizzes.freeze(quiz.questions, payload.lang),
                title=quiz.title,
                quiz_id=quiz.id,
                host_user=user,
                lang=payload.lang,
            )
        except live.LiveError as exc:
            raise _fail(db, exc) from exc
        view = {"host_token": room.game.host_token, **live.host_view(room, live._now())}
        db.commit()
        return view
```

Imports: `from .. import crud, live, models, quizzes` and `from .quizzes import own_quiz`. In `answer`, change the call to
`room.answer(player, payload.position, payload.model_dump(exclude_none=True, exclude={"position"}), now)`.

- [ ] **Step 10: Run all live tests**

Run: `cd backend && python -m pytest tests/test_live*.py -q`
Expected: PASS, the old ones included.

- [ ] **Step 11: Commit**

```bash
git add backend/app/models.py backend/app/live.py backend/app/routers/live.py backend/tests/test_live.py
git commit -m "Class games on a custom quiz: four question types, per-question time"
```

---

### Task 6: Past games of a custom quiz

**Files:**
- Modify: `backend/app/live_history.py`
- Test: `backend/tests/test_live_history.py` (append)

**Interfaces:**
- Consumes: `live.create_custom_room`, `models.CustomQuiz`.
- Produces: `Results.mistakes() -> list[dict]` (replaces `mistake_item_ids`); CSV header label per question; `replay` handles `mode == "custom"`.

- [ ] **Step 1: Write the failing tests** (append to `backend/tests/test_live_history.py`):

```python
from test_live import CUSTOM, RIGHT, custom_room  # noqa: E402


def play_custom(client, clock, headers, right_positions):
    """Ann plays CUSTOM, answering right at the given positions and wrong elsewhere."""
    room = custom_room(client, headers)
    pin, token = room["pin"], room["host_token"]
    ann = join(client, pin, "Ann")["token"]
    wrong = [{"choice_id": 0}, {"choice_id": 1}, {"text": "Ag"}, {"value": 0}]
    for position in range(1, len(CUSTOM["questions"]) + 1):
        client.post(f"/api/live/{pin}/next", headers=host(token))
        clock.advance(live.READ_SECONDS)
        given = RIGHT[position - 1] if position in right_positions else wrong[position - 1]
        client.post(f"/api/live/{pin}/answer", json={"position": position, **given}, headers=host(ann))
        client.post(f"/api/live/{pin}/next", headers=host(token))  # standings
    client.post(f"/api/live/{pin}/next", headers=host(token))  # finish
    return only_game(client, headers)


def test_a_custom_game_in_history(client, clock):
    t = teacher(client)
    game = play_custom(client, clock, t, right_positions={1, 2})
    assert game["mode"] == "custom" and game["category_name"] == "Mixed" and game["has_mistakes"]
    csv_text = client.get(f"/api/me/live-games/{game['id']}/results.csv", headers=t).text
    header = csv_text.lstrip("﻿").splitlines()[0]
    assert header == "Place;Name;Score;Correct;Q1 Pick B;Q2 Water is wet;Q3 Symbol of gold?;Q4 Boiling point"


def test_custom_mistakes_ask_only_what_was_missed(client, clock):
    t = teacher(client)
    game = play_custom(client, clock, t, right_positions={1, 2})
    new = replay(client, t, game["id"], "mistakes")
    assert new.status_code == 201, new.text
    assert new.json()["mode"] == "custom" and new.json()["question_count"] == 2
    with client.session_factory() as db:
        fresh = db.scalars(select(models.LiveGame).where(models.LiveGame.pin == new.json()["pin"])).one()
        assert [(q["position"], q["prompt"]) for q in fresh.questions] == [(1, "Symbol of gold?"), (2, "Boiling point")]


def test_custom_same_settings_needs_the_quiz(client, clock):
    t = teacher(client)
    game = play_custom(client, clock, t, right_positions={1})
    again = replay(client, t, game["id"], "same")
    assert again.status_code == 201 and again.json()["question_count"] == 4
    client.delete(f"/api/live/{again.json()['pin']}", headers=host(again.json()["host_token"]))

    [quiz] = client.get("/api/quizzes", headers=t).json()
    client.delete(f"/api/quizzes/{quiz['id']}", headers=t)
    gone = replay(client, t, game["id"], "same")
    assert gone.status_code == 409 and gone.json()["code"] == "quiz_gone"
    assert replay(client, t, game["id"], "mistakes").status_code == 201  # from the frozen copy
```

- [ ] **Step 2: Run them to see them fail**

Run: `cd backend && python -m pytest tests/test_live_history.py -q -k custom`
Expected: FAIL (CSV `KeyError: 'item'` / `NoneType` subscript).

- [ ] **Step 3: Implement** in `backend/app/live_history.py`:

Replace `mistake_item_ids` with:

```python
    def mistakes(self) -> list[dict]:
        """The questions fewer than MISTAKE_THRESHOLD of the class got right."""
        if not self.players:
            return []
        missed = []
        for q in asked(self.game):
            right = sum(
                1 for p in self.players
                if (a := self.answers[p.id].get(q["position"])) is not None and a.correct
            )
            if right < MISTAKE_THRESHOLD * len(self.players):
                missed.append(q)
        return missed
```

In `_summary`: `"has_mistakes": bool(results.mistakes()),`.

Add a label helper and use it in the CSV header:

```python
def _label(q: dict) -> str:
    """A question as a column heading: the card for deck games, else its text."""
    if q.get("item"):
        return q["item"]["name"]
    return q.get("prompt") or ""
```

`*(_cell(f"Q{q['position']} {_label(q)}".strip()) for q in questions)]`.

At the top of `replay`, before `category = _deck(db, game)`:

```python
    if game.mode == "custom":
        if kind == "same":
            quiz = db.get(models.CustomQuiz, game.custom_quiz_id) if game.custom_quiz_id else None
            if quiz is None or quiz.user_id != user.id:
                raise live.LiveError("quiz_gone")
            questions = quizzes.freeze(quiz.questions, game.lang)
            title, quiz_id = quiz.title, quiz.id
        else:
            questions = Results(db, game).mistakes()
            title, quiz_id = game.category_name, game.custom_quiz_id
        if not questions:
            raise live.LiveError("no_mistakes")
        return live.create_custom_room(db, questions=questions, title=title, quiz_id=quiz_id,
                                       host_user=user, lang=game.lang)
```

Then in the deck branch replace `ids = Results(db, game).mistake_item_ids()` with `ids = [q["correct_id"] for q in Results(db, game).mistakes()]`. Import: `from . import live, models, quizzes`.

- [ ] **Step 4: Run all backend tests**

Run: `cd backend && python -m pytest -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/live_history.py backend/tests/test_live_history.py
git commit -m "Past games of a custom quiz: CSV headings, same quiz again, work on mistakes"
```

---

### Task 7: Frontend building blocks: API, grader, question model, answer input

**Files:**
- Modify: `src/api/client.js`
- Create: `src/quizzes/grade.js`, `src/quizzes/grade.test.js`
- Create: `src/quizzes/model.js`, `src/quizzes/model.test.js`
- Create: `src/quizzes/AnswerInput.jsx`, `src/quizzes/AnswerInput.test.jsx`
- Create: `src/quizzes/quizzes.css`; modify `src/App.jsx` (import the CSS)
- Modify: `src/i18n/en.js`, `src/i18n/ru.js` (the `quizzes.play.*` keys)

**Interfaces:**
- Produces (client.js): `ApiError.body`; `fetchQuizzes()`, `fetchMyQuiz(id)`, `createQuiz(body)`, `updateQuiz(id, body)`, `deleteQuiz(id)`, `playQuiz(id)`, `questionsFromCards({slugs, mode, lang})`, `importQuiz(file)`, `uploadImage(file)`; `createLiveGame({..., customQuizId})`; `liveAnswer(pin, token, {position, choiceId, text, value})`.
- Produces: `grade.js` → `normalize(s)`, `grade(q, given)`, `answerText(q)`, `formatNumber(x)`; `model.js` → `TYPES`, `TIME_LIMITS`, `blankQuestion(type)`, `tidy(q)`, `move(list, index, by)`; `AnswerInput({question, onAnswer, disabled})`.

- [ ] **Step 1: API client.** In `src/api/client.js`:

Give `ApiError` the body: constructor `(message, status, body = null)` with `this.body = body;`, and pass `body` in `request()`: `throw new ApiError(describeFailure(response.status, body), response.status, body);`.

Add after the live section:

```js
// --- custom quizzes (signed in) -------------------------------------------------

export const fetchQuizzes = () => request("/api/quizzes");
export const fetchMyQuiz = (id) => request(`/api/quizzes/${id}`);
export const createQuiz = (body) => request("/api/quizzes", { method: "POST", body: JSON.stringify(body) });
export const updateQuiz = (id, body) =>
  request(`/api/quizzes/${id}`, { method: "PUT", body: JSON.stringify(body) });
export const deleteQuiz = (id) => request(`/api/quizzes/${id}`, { method: "DELETE" });
export const playQuiz = (id) => request(`/api/quizzes/${id}/play`);
export const questionsFromCards = ({ slugs, mode, lang }) =>
  request("/api/quizzes/from-cards", {
    method: "POST",
    body: JSON.stringify({ item_slugs: slugs, mode, lang }),
  });

/** Send a file as multipart form data: request() always sends JSON. */
async function sendFile(path, file) {
  const form = new FormData();
  form.append("file", file);
  let response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method: "POST",
      body: form,
      headers: {
        "Accept-Language": requestLanguage,
        ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
      },
    });
  } catch {
    throw new ApiError(translate(requestLanguage, "api.unreachable"), 0);
  }
  const body = await response.json().catch(() => null);
  if (!response.ok) throw new ApiError(describeFailure(response.status, body), response.status, body);
  return body;
}

export const importQuiz = (file) => sendFile("/api/quizzes/import", file);
export const uploadImage = (file) => sendFile("/api/uploads", file);
```

Change `createLiveGame` to take `customQuizId` and send `custom_quiz_id: customQuizId ?? null`. Change `liveAnswer`:

```js
export const liveAnswer = (pin, token, { position, choiceId, text, value }) =>
  live(`/${pin}/answer`, token, {
    method: "POST",
    body: JSON.stringify({ position, choice_id: choiceId ?? null, text: text ?? null, value: value ?? null }),
  });
```

- [ ] **Step 2: Write the failing grader tests** `src/quizzes/grade.test.js`:

```js
import { describe, expect, it } from "vitest";

import { answerText, formatNumber, grade, normalize } from "./grade";

// The same cases as backend/tests/test_grading.py and the normalize doctest.
describe("normalize (same as backend/app/text.py)", () => {
  it.each([
    ["Condenser, Friedrichs, with 24/40 joint", "condenser friedrichs 24 40 joint"],
    ["  Büchner  funnel ", "buchner funnel"],
    ["Ёлка", "елка"],
    ["24-40", "24 40"],
    ["the", ""],
    ["?", ""],
  ])("%s", (input, out) => expect(normalize(input)).toBe(out));
});

const QUIZ = { type: "quiz", choices: [{ id: 0, name: "A" }, { id: 1, name: "B" }, { id: 2, name: "C" }], correct_ids: [0, 2] };
const TYPED = { type: "type", accepted: ["Au", "Aurum"] };
const SLIDER = { type: "slider", min: 0, max: 1, step: 0.1, answer: 0.5, tolerance: 0.1, unit: "mol" };

describe("grade", () => {
  it("quiz: any correct option", () => {
    expect(grade(QUIZ, { choice_id: 2 })).toBe(true);
    expect(grade(QUIZ, { choice_id: 1 })).toBe(false);
  });
  it("old deck questions use correct_id", () => {
    expect(grade({ choices: [{ id: 9 }], correct_id: 9 }, { choice_id: 9 })).toBe(true);
  });
  it("typed answers are normalised", () => {
    expect(grade(TYPED, { text: " au " })).toBe(true);
    expect(grade(TYPED, { text: "AURUM!" })).toBe(true);
    expect(grade(TYPED, { text: "" })).toBe(false);
  });
  it("slider tolerance, with float noise", () => {
    expect(grade(SLIDER, { value: 0.6 })).toBe(true);
    expect(grade(SLIDER, { value: 0.30000000000000004 + 0.3 })).toBe(true);
    expect(grade(SLIDER, { value: 0.7 })).toBe(false);
  });
});

describe("answerText", () => {
  it("says the right answer", () => {
    expect(answerText(QUIZ)).toBe("A / C");
    expect(answerText(TYPED)).toBe("Au / Aurum");
    expect(answerText(SLIDER)).toBe("0.5 ± 0.1 mol");
    expect(answerText({ ...SLIDER, tolerance: 0, unit: "", answer: 100 })).toBe("100");
    expect(answerText({ item: { name: "Beaker" } })).toBe("Beaker");
  });
  it("formats numbers without float noise", () => {
    expect(formatNumber(0.30000000000000004)).toBe("0.3");
    expect(formatNumber(1234567)).toBe("1234567");
  });
});
```

- [ ] **Step 3: Run it to see it fail**

Run: `npx vitest run src/quizzes/grade.test.js`
Expected: FAIL, cannot resolve `./grade`.

- [ ] **Step 4: Write `src/quizzes/grade.js`**

```js
/**
 * Is an answer right? The solo player's copy of backend/app/grading.py and
 * the normaliser in backend/app/text.py -- keep the three in step (the tests
 * on both sides share their cases).
 */

const STOPWORDS = new Set(["a", "an", "the", "with", "and"]);
const EPSILON = 1e-9;

export function normalize(value) {
  if (!value) return "";
  let text = value.normalize("NFKD").replace(/\p{M}/gu, "").toLowerCase();
  text = text.replace(/(\d)\s*[/-]\s*(\d)/g, "$1 $2");
  text = text.replace(/[^\p{L}\p{N}_\s/]/gu, " ").replace(/\//g, " ").replace(/\s+/g, " ").trim();
  return text
    .split(" ")
    .filter((t) => t && !STOPWORDS.has(t))
    .join(" ");
}

const kind = (q) => q.type ?? "quiz";
export const correctIds = (q) => q.correct_ids ?? [q.correct_id];

export function grade(q, given) {
  const k = kind(q);
  if (k === "quiz" || k === "tf") return correctIds(q).includes(given.choice_id);
  if (k === "type") {
    const typed = normalize(given.text ?? "");
    return Boolean(typed) && q.accepted.some((a) => normalize(a) === typed);
  }
  return Math.abs(given.value - q.answer) <= q.tolerance + EPSILON;
}

/** 0.30000000000000004 -> "0.3", 100 -> "100". */
export function formatNumber(x) {
  return String(Number(Number(x).toFixed(6)));
}

/** The right answer in words; null when it is only pictures. */
export function answerText(q) {
  if (q.item) return q.item.name;
  const k = kind(q);
  if (k === "quiz" || k === "tf") {
    const right = correctIds(q);
    const names = q.choices.filter((c) => right.includes(c.id) && c.name).map((c) => c.name);
    return names.join(" / ") || null;
  }
  if (k === "type") return q.accepted.join(" / ");
  let text = formatNumber(q.answer);
  if (q.tolerance) text += ` ± ${formatNumber(q.tolerance)}`;
  if (q.unit) text += ` ${q.unit}`;
  return text;
}
```

- [ ] **Step 5: Run it**

Run: `npx vitest run src/quizzes/grade.test.js`
Expected: PASS.

- [ ] **Step 6: Write the failing model tests** `src/quizzes/model.test.js`:

```js
import { describe, expect, it } from "vitest";

import { blankQuestion, move, tidy, TIME_LIMITS, TYPES } from "./model";

describe("question model", () => {
  it("has a blank of every type", () => {
    for (const type of TYPES) expect(blankQuestion(type).type).toBe(type);
    expect(blankQuestion("quiz").options).toHaveLength(4);
    expect(TIME_LIMITS).toEqual([5, 10, 20, 30, 60, 90, 120, 240]);
  });

  it("drops the blanks a teacher leaves before saving", () => {
    const q = blankQuestion("quiz");
    q.options[0].text = "A";
    q.options[2].text = "C";
    expect(tidy(q).options.map((o) => o.text)).toEqual(["A", "", "C"]); // the first two always stay
    expect(tidy({ ...blankQuestion("type"), accepted: ["Au", " ", ""] }).accepted).toEqual(["Au"]);
  });

  it("moves a question up and down, not off the ends", () => {
    expect(move(["a", "b", "c"], 2, -1)).toEqual(["a", "c", "b"]);
    expect(move(["a", "b", "c"], 0, -1)).toEqual(["a", "b", "c"]);
  });
});
```

- [ ] **Step 7: Write `src/quizzes/model.js`**

```js
/** A custom quiz's questions as the editor holds them (the stored shape, see backend/app/quizzes.py). */

export const TYPES = ["quiz", "tf", "type", "slider"];
export const TIME_LIMITS = [5, 10, 20, 30, 60, 90, 120, 240];
export const TYPE_ICONS = { quiz: "grid_view", tf: "rule", type: "keyboard", slider: "linear_scale" };

export function blankQuestion(type) {
  const base = { type, text: "", image: null, time_limit: 20 };
  if (type === "quiz") {
    return { ...base, options: [0, 1, 2, 3].map((i) => ({ text: "", image: null, correct: i === 0 })) };
  }
  if (type === "tf") return { ...base, answer: true };
  if (type === "type") return { ...base, accepted: [""] };
  return { ...base, min: 0, max: 100, step: 1, answer: 50, tolerance: 0, unit: "" };
}

/** Drop empty third/fourth options and empty accepted answers, which the server would refuse. */
export function tidy(q) {
  if (q.type === "quiz") return { ...q, options: q.options.filter((o, i) => i < 2 || o.text.trim() || o.image) };
  if (q.type === "type") return { ...q, accepted: q.accepted.filter((a) => a.trim()) };
  return q;
}

export function move(list, index, by) {
  const to = index + by;
  if (to < 0 || to >= list.length) return list;
  const next = [...list];
  [next[index], next[to]] = [next[to], next[index]];
  return next;
}
```

Run: `npx vitest run src/quizzes/model.test.js` → PASS.

- [ ] **Step 8: i18n keys for playing.** Add to `src/i18n/en.js` (and the Russian in `ru.js`):

| key | en | ru |
|---|---|---|
| `quizzes.play.typeHere` | Type your answer | Введите ответ |
| `quizzes.play.send` | Send | Отправить |
| `quizzes.play.pickValue` | Pick a value | Выберите значение |

- [ ] **Step 9: Write the failing AnswerInput test** `src/quizzes/AnswerInput.test.jsx`:

```jsx
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import AnswerInput from "./AnswerInput";

describe("AnswerInput", () => {
  it("quiz and true/false: a tap answers", () => {
    const onAnswer = vi.fn();
    render(<AnswerInput question={{ type: "tf", choices: [{ id: 0, name: "True" }, { id: 1, name: "False" }] }} onAnswer={onAnswer} />);
    fireEvent.click(screen.getByRole("button", { name: "False" }));
    expect(onAnswer).toHaveBeenCalledWith({ choice_id: 1 });
  });

  it("type answer: sends what was typed", () => {
    const onAnswer = vi.fn();
    render(<AnswerInput question={{ type: "type" }} onAnswer={onAnswer} />);
    fireEvent.change(screen.getByLabelText("Type your answer"), { target: { value: "Au" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));
    expect(onAnswer).toHaveBeenCalledWith({ text: "Au" });
  });

  it("slider: starts in the middle and sends the value", () => {
    const onAnswer = vi.fn();
    render(<AnswerInput question={{ type: "slider", min: 0, max: 200, step: 1, unit: "°C" }} onAnswer={onAnswer} />);
    fireEvent.change(screen.getByLabelText("Pick a value"), { target: { value: "120" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));
    expect(onAnswer).toHaveBeenCalledWith({ value: 120 });
  });
});
```

(If the default language in tests is not English, set `window.localStorage.setItem("chemquiz.lang", "en")` in a `beforeEach`, as JoinPage.test.jsx does for Russian.)

- [ ] **Step 10: Write `src/quizzes/AnswerInput.jsx`**

```jsx
import { useState } from "react";

import { imageSrc } from "../api/client";
import { useT } from "../i18n";
import { Shape } from "../live/components";
import { OPTION_STYLES } from "../live/game";
import { formatNumber } from "./grade";

/**
 * How a player answers one question of a custom quiz: the coloured option
 * buttons, a text box, or a slider. Shared by the phone in a class game and
 * the solo player. `question` is the answer-free shape; `onAnswer` receives
 * {choice_id}, {text} or {value}.
 */
function AnswerInput({ question, onAnswer, disabled = false }) {
  const t = useT();
  const kind = question.type ?? "quiz";
  if (kind === "type") return <TypedAnswer onAnswer={onAnswer} disabled={disabled} />;
  if (kind === "slider") return <SliderAnswer question={question} onAnswer={onAnswer} disabled={disabled} />;
  return (
    <div className={`live-phone-options ${kind === "tf" ? "is-two" : ""}`}>
      {question.choices.map((choice, i) => {
        const style = OPTION_STYLES[i];
        return (
          <button
            key={choice.id}
            type="button"
            className={`live-phone-option is-${style.key}`}
            disabled={disabled}
            onClick={() => onAnswer({ choice_id: choice.id })}
            aria-label={choice.name ?? t(`live.shape.${style.key}`)}
          >
            <Shape index={i} size={choice.image_url ? 22 : 28} />
            {choice.image_url && <img src={imageSrc(choice.image_url)} alt="" draggable="false" />}
            {choice.name && <span>{choice.name}</span>}
          </button>
        );
      })}
    </div>
  );
}

function TypedAnswer({ onAnswer, disabled }) {
  const t = useT();
  const [text, setText] = useState("");
  return (
    <form
      className="answer-typed"
      onSubmit={(e) => {
        e.preventDefault();
        if (text.trim()) onAnswer({ text });
      }}
    >
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        maxLength={40}
        autoComplete="off"
        autoCapitalize="off"
        aria-label={t("quizzes.play.typeHere")}
        placeholder={t("quizzes.play.typeHere")}
        disabled={disabled}
      />
      <button type="submit" className="primary-button" disabled={disabled || !text.trim()}>
        {t("quizzes.play.send")}
      </button>
    </form>
  );
}

function SliderAnswer({ question, onAnswer, disabled }) {
  const t = useT();
  const { min, max, step, unit } = question;
  // Start in the middle, on a step; never past max by float rounding.
  const [value, setValue] = useState(() => Math.min(max, min + Math.round((max - min) / 2 / step) * step));
  return (
    <form
      className="answer-slider"
      onSubmit={(e) => {
        e.preventDefault();
        onAnswer({ value });
      }}
    >
      <output className="answer-slider-value">
        {formatNumber(value)} {unit}
      </output>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => setValue(Number(e.target.value))}
        aria-label={t("quizzes.play.pickValue")}
        disabled={disabled}
      />
      <div className="answer-slider-ends">
        <span>{formatNumber(min)}</span>
        <span>{formatNumber(max)}</span>
      </div>
      <button type="submit" className="primary-button" disabled={disabled}>
        {t("quizzes.play.send")}
      </button>
    </form>
  );
}

export default AnswerInput;
```

- [ ] **Step 11: Styles** `src/quizzes/quizzes.css` (imported in `src/App.jsx` after `./live/live.css`):

```css
/* Custom quizzes: answering (shared with the phone), the editor, the list. */

.live-phone-options.is-two { grid-template-columns: 1fr 1fr; grid-auto-rows: minmax(0, 1fr); }
.live-phone-option img { max-width: 100%; max-height: 60%; object-fit: contain; border-radius: 10px; background: #fff; }

.answer-typed, .answer-slider { display: flex; flex-direction: column; gap: 12px; width: 100%; }
.answer-typed input { font: inherit; font-size: 20px; padding: 14px 16px; border-radius: 14px; border: 2px solid var(--line, #d0d5dd); }
.answer-slider input[type="range"] { width: 100%; accent-color: var(--accent, #2f6fed); }
.answer-slider-value { font-size: 36px; font-weight: 700; text-align: center; }
.answer-slider-ends { display: flex; justify-content: space-between; opacity: 0.7; }

.quiz-list { display: grid; gap: 12px; padding: 0; list-style: none; }
.quiz-list li { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; padding: 14px 16px; border-radius: 16px; background: var(--card, #fff); box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08); }
.quiz-list-title { flex: 1 1 200px; font-weight: 600; }

.quiz-editor { display: grid; grid-template-columns: minmax(200px, 280px) 1fr; gap: 20px; align-items: start; }
@media (max-width: 760px) { .quiz-editor { grid-template-columns: 1fr; } }
.quiz-editor-list { display: grid; gap: 6px; padding: 0; margin: 0; list-style: none; }
.quiz-editor-list li { display: flex; align-items: center; gap: 4px; }
.quiz-editor-item { flex: 1; min-width: 0; display: flex; align-items: center; gap: 8px; padding: 10px 12px; border: 2px solid transparent; border-radius: 12px; background: var(--card, #fff); font: inherit; text-align: left; cursor: pointer; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.quiz-editor-item.is-selected { border-color: var(--accent, #2f6fed); }
.quiz-editor-item.has-error { border-color: #d92d20; }
.quiz-icon-button { border: 0; background: none; padding: 6px; cursor: pointer; border-radius: 8px; font: inherit; }
.quiz-icon-button:disabled { opacity: 0.3; cursor: default; }

.question-form { display: grid; gap: 14px; padding: 18px; border-radius: 18px; background: var(--card, #fff); }
.question-form label { display: grid; gap: 6px; font-weight: 600; }
.question-form input[type="text"], .question-form input[type="number"], .question-form textarea { font: inherit; font-weight: 400; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--line, #d0d5dd); }
.question-form textarea { min-height: 70px; resize: vertical; }
.question-options { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
@media (max-width: 520px) { .question-options { grid-template-columns: 1fr; } }
.question-option { display: grid; gap: 6px; padding: 10px; border-radius: 12px; color: #fff; }
.question-option input[type="text"] { color: #111; }
.question-option.is-red { background: var(--opt-red, #e21b3c); }
.question-option.is-blue { background: var(--opt-blue, #1368ce); }
.question-option.is-amber { background: var(--opt-amber, #d89e00); }
.question-option.is-green { background: var(--opt-green, #26890c); }
.question-option-row { display: flex; align-items: center; gap: 8px; }
.question-image { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.question-image img { max-height: 120px; max-width: 200px; border-radius: 10px; object-fit: contain; background: #fff; }
.question-option .question-image img { max-height: 60px; }
.question-numbers { display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 10px; }
.quiz-panel { display: grid; gap: 12px; padding: 16px; border-radius: 16px; background: var(--card, #fff); }
.quiz-card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 8px; max-height: 360px; overflow: auto; }
.quiz-card { display: grid; gap: 4px; padding: 6px; border: 2px solid transparent; border-radius: 12px; background: var(--surface, #f5f6f8); font: inherit; font-size: 13px; cursor: pointer; text-align: left; }
.quiz-card.is-selected { border-color: var(--accent, #2f6fed); }
.quiz-card img { width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 8px; background: #fff; }
.quiz-errors { margin: 0; padding-left: 18px; color: #b42318; }
.quiz-actions { display: flex; flex-wrap: wrap; gap: 8px; }
.solo-feedback { display: grid; gap: 8px; justify-items: center; text-align: center; }
```

- [ ] **Step 12: Run frontend checks**

Run: `npm run lint && npm test`
Expected: PASS.

- [ ] **Step 13: Commit**

```bash
git add src/api/client.js src/quizzes src/App.jsx src/i18n/en.js src/i18n/ru.js
git commit -m "Custom quizzes frontend: API calls, grader, question model, answer input"
```

---

### Task 8: My quizzes and the editor

**Files:**
- Create: `src/quizzes/MyQuizzesPage.jsx`, `src/quizzes/QuizEditorPage.jsx`, `src/quizzes/QuestionForm.jsx`, `src/quizzes/LibraryPicker.jsx`, `src/quizzes/ImportPanel.jsx`
- Modify: `src/App.jsx` (routes + the route list comment), `src/pages/ProfilePage.jsx` (link), `src/i18n/en.js`, `src/i18n/ru.js`

**Interfaces:**
- Consumes: everything from Task 7; `useAuth()` from `../auth/context`; `useProgress().catalog` (`{items: [{slug, name, image_url, category_slug}], decks: [{slug, name, cards: [slug]}]}`); `useApi(loader, deps)` → `{data, error, loading, reload}`; `PageHeader({title, backTo, onBack})`; `Loading`, `ErrorMessage`, `EmptyMessage`.
- Produces: routes `/quizzes`, `/quizzes/new`, `/quizzes/:id`; `MyQuizzesPage` links to `/quizzes/:id/play` and `/live?quiz=:id`.

- [ ] **Step 1: i18n keys** (en / ru), add to both files:

| key | en | ru |
|---|---|---|
| `quizzes.title` | My quizzes | Мои квизы |
| `quizzes.lead` | Your own questions, for a class game or to try yourself. | Свои вопросы — для игры в классе или чтобы пройти самому. |
| `quizzes.create` | New quiz | Новый квиз |
| `quizzes.empty` | No quizzes yet. | Квизов пока нет. |
| `quizzes.signIn` | {signIn} to make your own quizzes. | {signIn}, чтобы составлять свои квизы. |
| `quizzes.demo` | Your own quizzes need the full site with its server; the demo cannot keep them. | Свои квизы работают только на полной версии сайта с сервером; демо их не сохраняет. |
| `quizzes.questions` | { one: "{n} question", other: "{n} questions" } | { one: "{n} вопрос", few: "{n} вопроса", many: "{n} вопросов", other: "{n} вопроса" } |
| `quizzes.edit` | Edit | Изменить |
| `quizzes.delete` | Delete | Удалить |
| `quizzes.confirmDelete` | Delete “{title}”? Past games stay in history. | Удалить «{title}»? Прошлые игры останутся в истории. |
| `quizzes.playSolo` | Play | Пройти |
| `quizzes.host` | Host in class | Играть в классе |
| `quizzes.myQuizzes` | My quizzes | Мои квизы |
| `quizzes.editor.newTitle` | New quiz | Новый квиз |
| `quizzes.editor.title` | Title | Название |
| `quizzes.editor.lang` | Language of the quiz | Язык квиза |
| `quizzes.editor.add` | Question | Вопрос |
| `quizzes.editor.fromLibrary` | From the library | Из нашей базы |
| `quizzes.editor.import` | Import | Импорт |
| `quizzes.editor.save` | Save | Сохранить |
| `quizzes.editor.saving` | Saving... | Сохраняем... |
| `quizzes.editor.saved` | Saved | Сохранено |
| `quizzes.editor.unsaved` | Leave without saving? | Уйти без сохранения? |
| `quizzes.editor.untitled` | (no text) | (без текста) |
| `quizzes.editor.up` | Move up | Выше |
| `quizzes.editor.down` | Move down | Ниже |
| `quizzes.editor.remove` | Delete question | Удалить вопрос |
| `quizzes.editor.questionN` | Question {n} | Вопрос {n} |
| `quizzes.type.quiz` | Quiz | Квиз |
| `quizzes.type.tf` | True / false | Верно / неверно |
| `quizzes.type.type` | Type answer | Ввод ответа |
| `quizzes.type.slider` | Slider | Ползунок |
| `quizzes.form.type` | Type | Тип |
| `quizzes.form.text` | Question | Вопрос |
| `quizzes.form.time` | Time | Время |
| `quizzes.form.seconds` | {n} s | {n} с |
| `quizzes.form.image` | Picture | Картинка |
| `quizzes.form.addImage` | Add picture | Добавить картинку |
| `quizzes.form.removeImage` | Remove picture | Убрать картинку |
| `quizzes.form.uploading` | Uploading... | Загружаем... |
| `quizzes.form.answer` | Answer {n} | Ответ {n} |
| `quizzes.form.correct` | Correct | Верный |
| `quizzes.form.statementIs` | The statement is | Утверждение |
| `quizzes.form.accepted` | Accepted answers (up to 4, case and punctuation do not matter) | Правильные ответы (до 4; регистр и знаки не важны) |
| `quizzes.form.addAccepted` | Another answer | Ещё вариант |
| `quizzes.form.min` | Min | Минимум |
| `quizzes.form.max` | Max | Максимум |
| `quizzes.form.step` | Step | Шаг |
| `quizzes.form.value` | Right value | Правильное значение |
| `quizzes.form.tolerance` | Tolerance ± | Допуск ± |
| `quizzes.form.unit` | Unit | Единицы |
| `quizzes.library.deck` | Deck | Колода |
| `quizzes.library.selectAll` | Select all | Выбрать все |
| `quizzes.library.add` | { one: "Add {n} question", other: "Add {n} questions" } | { one: "Добавить {n} вопрос", few: "Добавить {n} вопроса", many: "Добавить {n} вопросов", other: "Добавить {n} вопроса" } |
| `quizzes.import.lead` | Fill in a template and upload it. Pictures are added afterwards, here. | Заполните шаблон и загрузите его. Картинки добавляются потом, здесь. |
| `quizzes.import.excel` | Excel template | Шаблон Excel |
| `quizzes.import.word` | Word template | Шаблон Word |
| `quizzes.import.choose` | Upload a filled-in template | Загрузить заполненный шаблон |
| `quizzes.import.added` | { one: "Added {n} question.", other: "Added {n} questions." } | { one: "Добавлен {n} вопрос.", few: "Добавлено {n} вопроса.", many: "Добавлено {n} вопросов.", other: "Добавлено {n} вопроса." } |
| `quizzes.import.row` | Row {row}: {message} | Строка {row}: {message} |
| `profile.myQuizzes` | My quizzes | Мои квизы |

(Use the plural-object format exactly as existing plural keys in each file do.)

- [ ] **Step 2: `src/quizzes/MyQuizzesPage.jsx`**

```jsx
import { useCallback } from "react";
import { Link } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { EmptyMessage, ErrorMessage, Loading } from "../components/StatusMessage";
import { deleteQuiz, fetchQuizzes, IS_DEMO } from "../api/client";
import { useAuth } from "../auth/context";
import { useApi } from "../hooks/useApi";
import { rich, useT } from "../i18n";

/** A teacher's own quizzes: make one, change it, play it, or take it to class. */
function MyQuizzesPage() {
  const t = useT();
  const { user } = useAuth();

  return (
    <main className="setup-page">
      <div className="page-layout setup">
        <PageHeader title={t("quizzes.title")} backTo="/" />
        <section className="setup-content">
          {IS_DEMO ? (
            <p className="section-note">{t("quizzes.demo")}</p>
          ) : !user ? (
            <p className="section-note">
              {rich(t("quizzes.signIn"), { signIn: <Link to="/sign-in">{t("common.signInLink")}</Link> })}
            </p>
          ) : (
            <QuizList t={t} />
          )}
        </section>
      </div>
    </main>
  );
}

function QuizList({ t }) {
  const loader = useCallback(() => fetchQuizzes(), []);
  const { data: quizzes, error, loading, reload } = useApi(loader);

  async function remove(quiz) {
    if (!window.confirm(t("quizzes.confirmDelete", { title: quiz.title }))) return;
    await deleteQuiz(quiz.id);
    reload();
  }

  return (
    <>
      <p className="setup-lead">{t("quizzes.lead")}</p>
      <Link className="primary-button" to="/quizzes/new">
        {t("quizzes.create")}
      </Link>
      {loading && <Loading />}
      {error && <ErrorMessage error={error} onRetry={reload} />}
      {quizzes && quizzes.length === 0 && <EmptyMessage>{t("quizzes.empty")}</EmptyMessage>}
      {quizzes && quizzes.length > 0 && (
        <ul className="quiz-list">
          {quizzes.map((quiz) => (
            <li key={quiz.id}>
              <span className="quiz-list-title">
                {quiz.title}
                <span className="option-note"> · {t("quizzes.questions", { n: quiz.question_count })}</span>
              </span>
              <Link className="secondary-button" to={`/live?quiz=${quiz.id}`}>
                {t("quizzes.host")}
              </Link>
              <Link className="secondary-button" to={`/quizzes/${quiz.id}/play`}>
                {t("quizzes.playSolo")}
              </Link>
              <Link className="text-button" to={`/quizzes/${quiz.id}`}>
                {t("quizzes.edit")}
              </Link>
              <button type="button" className="text-button" onClick={() => remove(quiz)}>
                {t("quizzes.delete")}
              </button>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}

export default MyQuizzesPage;
```

- [ ] **Step 3: `src/quizzes/QuestionForm.jsx`**

```jsx
import { useRef, useState } from "react";

import { imageSrc, uploadImage } from "../api/client";
import { ErrorMessage } from "../components/StatusMessage";
import { useT } from "../i18n";
import { OPTION_STYLES } from "../live/game";
import { blankQuestion, TIME_LIMITS, TYPES } from "./model";

/** The selected question's fields; they change with its type. `onChange` gets the whole new question. */
function QuestionForm({ question: q, onChange, error }) {
  const t = useT();
  const set = (patch) => onChange({ ...q, ...patch });

  function changeType(type) {
    if (type === q.type) return;
    // Keep what carries over: the text, the picture and the time.
    onChange({ ...blankQuestion(type), text: q.text, image: q.image, time_limit: q.time_limit });
  }

  return (
    <div className="question-form">
      {error && <ErrorMessage error={error} />}
      <div className="option-row option-row-tight" role="group" aria-label={t("quizzes.form.type")}>
        {TYPES.map((type) => (
          <button
            key={type}
            type="button"
            className={`option-button option-button-small ${q.type === type ? "is-selected" : ""}`}
            aria-pressed={q.type === type}
            onClick={() => changeType(type)}
          >
            {t(`quizzes.type.${type}`)}
          </button>
        ))}
      </div>

      <label>
        {t("quizzes.form.text")}
        <textarea value={q.text} maxLength={300} onChange={(e) => set({ text: e.target.value })} />
      </label>

      <ImageField label={t("quizzes.form.image")} value={q.image} onChange={(image) => set({ image })} />

      <label>
        {t("quizzes.form.time")}
        <select value={q.time_limit} onChange={(e) => set({ time_limit: Number(e.target.value) })}>
          {TIME_LIMITS.map((s) => (
            <option key={s} value={s}>
              {t("quizzes.form.seconds", { n: s })}
            </option>
          ))}
        </select>
      </label>

      {q.type === "quiz" && <QuizOptions q={q} set={set} t={t} />}
      {q.type === "tf" && (
        <fieldset className="option-group">
          <legend className="option-legend">{t("quizzes.form.statementIs")}</legend>
          <div className="option-row option-row-tight">
            {[true, false].map((value) => (
              <button
                key={String(value)}
                type="button"
                className={`option-button option-button-small ${q.answer === value ? "is-selected" : ""}`}
                aria-pressed={q.answer === value}
                onClick={() => set({ answer: value })}
              >
                {value ? t("live.tf.true") : t("live.tf.false")}
              </button>
            ))}
          </div>
        </fieldset>
      )}
      {q.type === "type" && <AcceptedAnswers q={q} set={set} t={t} />}
      {q.type === "slider" && <SliderFields q={q} set={set} t={t} />}
    </div>
  );
}

function QuizOptions({ q, set, t }) {
  const setOption = (i, patch) => set({ options: q.options.map((o, j) => (j === i ? { ...o, ...patch } : o)) });
  return (
    <div className="question-options">
      {q.options.map((o, i) => (
        <div key={i} className={`question-option is-${OPTION_STYLES[i].key}`}>
          <input
            type="text"
            value={o.text}
            maxLength={75}
            aria-label={t("quizzes.form.answer", { n: i + 1 })}
            placeholder={t("quizzes.form.answer", { n: i + 1 })}
            onChange={(e) => setOption(i, { text: e.target.value })}
          />
          <div className="question-option-row">
            <label className="question-option-row">
              <input type="checkbox" checked={o.correct} onChange={(e) => setOption(i, { correct: e.target.checked })} />
              {t("quizzes.form.correct")}
            </label>
          </div>
          <ImageField value={o.image} onChange={(image) => setOption(i, { image })} small />
        </div>
      ))}
    </div>
  );
}

function AcceptedAnswers({ q, set, t }) {
  return (
    <fieldset className="option-group">
      <legend className="option-legend">{t("quizzes.form.accepted")}</legend>
      {q.accepted.map((a, i) => (
        <input
          key={i}
          type="text"
          value={a}
          maxLength={20}
          aria-label={t("quizzes.form.answer", { n: i + 1 })}
          onChange={(e) => set({ accepted: q.accepted.map((b, j) => (j === i ? e.target.value : b)) })}
        />
      ))}
      {q.accepted.length < 4 && (
        <button type="button" className="text-button" onClick={() => set({ accepted: [...q.accepted, ""] })}>
          {t("quizzes.form.addAccepted")}
        </button>
      )}
    </fieldset>
  );
}

function SliderFields({ q, set, t }) {
  const num = (key) => (
    <label key={key}>
      {t(`quizzes.form.${key === "answer" ? "value" : key}`)}
      <input
        type="number"
        value={q[key]}
        step="any"
        onChange={(e) => set({ [key]: e.target.value === "" ? "" : Number(e.target.value) })}
      />
    </label>
  );
  return (
    <div className="question-numbers">
      {["min", "max", "step", "answer", "tolerance"].map(num)}
      <label>
        {t("quizzes.form.unit")}
        <input type="text" value={q.unit} maxLength={10} onChange={(e) => set({ unit: e.target.value })} />
      </label>
    </div>
  );
}

/** Pick a picture from the device; it is uploaded straight away and its URL kept. */
function ImageField({ label, value, onChange, small = false }) {
  const t = useT();
  const input = useRef(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  async function pick(e) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    setBusy(true);
    setError(null);
    try {
      onChange((await uploadImage(file)).url);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="question-image">
      {label && !small && <span>{label}</span>}
      {value && <img src={imageSrc(value)} alt="" />}
      <input ref={input} type="file" accept="image/*" hidden onChange={pick} />
      <button type="button" className="text-button" disabled={busy} onClick={() => input.current?.click()}>
        {busy ? t("quizzes.form.uploading") : t("quizzes.form.addImage")}
      </button>
      {value && (
        <button type="button" className="text-button" onClick={() => onChange(null)}>
          {t("quizzes.form.removeImage")}
        </button>
      )}
      {error && <ErrorMessage error={error} />}
    </div>
  );
}

export default QuestionForm;
```

Add i18n keys `live.tf.true` ("True" / "Верно") and `live.tf.false` ("False" / "Неверно").

- [ ] **Step 4: `src/quizzes/LibraryPicker.jsx`**

```jsx
import { useState } from "react";

import { imageSrc, questionsFromCards } from "../api/client";
import { ErrorMessage, Loading } from "../components/StatusMessage";
import { useT } from "../i18n";
import { useProgress } from "../progress/context";

/** Pick cards from our library; each becomes a "photo → names" or "name → photos" question. */
function LibraryPicker({ lang, onAdd }) {
  const t = useT();
  const { catalog } = useProgress();
  const [deck, setDeck] = useState(null);
  const [mode, setMode] = useState("choice");
  const [picked, setPicked] = useState(() => new Set());
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  if (!catalog) return <Loading />;
  const decks = catalog.decks ?? [];
  const inDeck = deck ? new Set(decks.find((d) => d.slug === deck)?.cards ?? []) : null;
  const cards = catalog.items.filter((item) => !inDeck || inDeck.has(item.slug));

  function toggle(slug) {
    const next = new Set(picked);
    if (next.has(slug)) next.delete(slug);
    else next.add(slug);
    setPicked(next);
  }

  async function add() {
    setBusy(true);
    setError(null);
    try {
      const { questions } = await questionsFromCards({ slugs: [...picked], mode, lang });
      onAdd(questions);
      setPicked(new Set());
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="quiz-panel">
      <label>
        {t("quizzes.library.deck")}{" "}
        <select value={deck ?? ""} onChange={(e) => setDeck(e.target.value || null)}>
          <option value="">{t("history.everything")}</option>
          {decks.map((d) => (
            <option key={d.slug} value={d.slug}>
              {d.group ? `${d.group} · ${d.name}` : d.name}
            </option>
          ))}
        </select>
      </label>
      <div className="option-row option-row-tight">
        {["choice", "inverted"].map((m) => (
          <button
            key={m}
            type="button"
            className={`option-button option-button-small ${mode === m ? "is-selected" : ""}`}
            aria-pressed={mode === m}
            onClick={() => setMode(m)}
          >
            {t(`mode.${m}`)}
          </button>
        ))}
        <button type="button" className="text-button" onClick={() => setPicked(new Set(cards.map((c) => c.slug)))}>
          {t("quizzes.library.selectAll")}
        </button>
      </div>
      <div className="quiz-card-grid">
        {cards.map((card) => (
          <button
            key={card.slug}
            type="button"
            className={`quiz-card ${picked.has(card.slug) ? "is-selected" : ""}`}
            aria-pressed={picked.has(card.slug)}
            onClick={() => toggle(card.slug)}
          >
            {card.image_url && <img src={imageSrc(card.image_url)} alt="" loading="lazy" />}
            {card.name}
          </button>
        ))}
      </div>
      {error && <ErrorMessage error={error} />}
      <button type="button" className="primary-button" disabled={busy || picked.size === 0} onClick={add}>
        {t("quizzes.library.add", { n: picked.size })}
      </button>
    </section>
  );
}

export default LibraryPicker;
```

Note: `catalog.items` from `fetchItems()` is in the interface language; the server writes the drafts in `lang` (the quiz's language), which is what the class will see.

- [ ] **Step 5: `src/quizzes/ImportPanel.jsx`**

```jsx
import { useState } from "react";

import { importQuiz } from "../api/client";
import { ErrorMessage } from "../components/StatusMessage";
import { useT } from "../i18n";

const TEMPLATES = `${import.meta.env.BASE_URL}templates/chemquiz-template`;

/** Download a template, fill it in, upload it: the questions are appended to the editor. */
function ImportPanel({ onAdd }) {
  const t = useT();
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  async function upload(e) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const res = await importQuiz(file);
      onAdd(res.questions);
      setResult(res);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="quiz-panel">
      <p>{t("quizzes.import.lead")}</p>
      <div className="quiz-actions">
        <a className="secondary-button" href={`${TEMPLATES}.xlsx`} download>
          {t("quizzes.import.excel")}
        </a>
        <a className="secondary-button" href={`${TEMPLATES}.docx`} download>
          {t("quizzes.import.word")}
        </a>
        <label className="primary-button">
          {t("quizzes.import.choose")}
          <input type="file" accept=".xlsx,.docx" hidden disabled={busy} onChange={upload} />
        </label>
      </div>
      {error && <ErrorMessage error={error} />}
      {result && <p>{t("quizzes.import.added", { n: result.questions.length })}</p>}
      {result?.errors.length > 0 && (
        <ul className="quiz-errors">
          {result.errors.map((e) => (
            <li key={e.row}>{t("quizzes.import.row", e)}</li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default ImportPanel;
```

- [ ] **Step 6: `src/quizzes/QuizEditorPage.jsx`**

```jsx
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { ErrorMessage, Loading } from "../components/StatusMessage";
import { createQuiz, fetchMyQuiz, IS_DEMO, updateQuiz } from "../api/client";
import { useAuth } from "../auth/context";
import { rich, useLang, useT } from "../i18n";
import ImportPanel from "./ImportPanel";
import LibraryPicker from "./LibraryPicker";
import { blankQuestion, move, tidy, TYPE_ICONS, TYPES } from "./model";
import QuestionForm from "./QuestionForm";

/**
 * Build or change a custom quiz: the questions on the left, the chosen one's
 * form on the right; add from scratch, from the library, or from a template.
 * Saved whole with one request; the server checks every question and names
 * the first one it refuses, which is then selected.
 */
function QuizEditorPage() {
  const { id } = useParams();
  const t = useT();
  const { user } = useAuth();

  if (IS_DEMO || !user) {
    return (
      <main className="setup-page">
        <div className="page-layout setup">
          <PageHeader title={t("quizzes.title")} backTo="/quizzes" />
          <p className="section-note">
            {IS_DEMO
              ? t("quizzes.demo")
              : rich(t("quizzes.signIn"), { signIn: <Link to="/sign-in">{t("common.signInLink")}</Link> })}
          </p>
        </div>
      </main>
    );
  }
  return <Editor key={id ?? "new"} id={id} />;
}

function Editor({ id }) {
  const t = useT();
  const navigate = useNavigate();
  const { lang: userLang } = useLang();

  const [quiz, setQuiz] = useState(id ? null : { title: "", lang: userLang, questions: [blankQuestion("quiz")] });
  const [loadError, setLoadError] = useState(null);
  const [selected, setSelected] = useState(0);
  const [panel, setPanel] = useState(null); // null | "library" | "import"
  const [dirty, setDirty] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState(null); // {message, question}

  useEffect(() => {
    if (!id) return undefined;
    let active = true;
    fetchMyQuiz(id)
      .then((q) => active && setQuiz({ title: q.title, lang: q.lang, questions: q.questions }))
      .catch((err) => active && setLoadError(err));
    return () => {
      active = false;
    };
  }, [id]);

  useEffect(() => {
    if (!dirty) return undefined;
    const warn = (e) => {
      e.preventDefault();
      e.returnValue = "";
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [dirty]);

  if (loadError) return <ErrorMessage error={loadError} />;
  if (!quiz) return <Loading />;

  const questions = quiz.questions;
  const current = questions[Math.min(selected, questions.length - 1)];

  function change(patch) {
    setQuiz((q) => ({ ...q, ...patch }));
    setDirty(true);
    setSaved(false);
  }
  const setQuestions = (list) => change({ questions: list });

  function append(list) {
    if (!list.length) return;
    setQuestions([...questions, ...list]);
    setSelected(questions.length);
    setPanel(null);
  }

  function remove(index) {
    const next = questions.filter((_, i) => i !== index);
    setQuestions(next.length ? next : [blankQuestion("quiz")]);
    setSelected(Math.max(0, Math.min(selected, next.length - 1)));
  }

  async function save() {
    setSaving(true);
    setError(null);
    const body = { ...quiz, questions: questions.map(tidy) };
    try {
      const result = id ? await updateQuiz(id, body) : await createQuiz(body);
      setDirty(false);
      setSaved(true);
      if (!id) navigate(`/quizzes/${result.id}`, { replace: true });
    } catch (err) {
      const question = err.body?.question ?? null;
      setError({ message: err.message, question });
      if (question) setSelected(question - 1);
    } finally {
      setSaving(false);
    }
  }

  function back() {
    if (!dirty || window.confirm(t("quizzes.editor.unsaved"))) navigate("/quizzes");
  }

  const errorHere = error?.question === selected + 1 ? error : null;

  return (
    <main className="setup-page">
      <div className="page-layout">
        <PageHeader title={id ? quiz.title || t("quizzes.title") : t("quizzes.editor.newTitle")} onBack={back} />

        <div className="question-form">
          <label>
            {t("quizzes.editor.title")}
            <input type="text" value={quiz.title} maxLength={120} onChange={(e) => change({ title: e.target.value })} />
          </label>
          <div className="option-row option-row-tight" role="group" aria-label={t("quizzes.editor.lang")}>
            {["en", "ru"].map((code) => (
              <button
                key={code}
                type="button"
                className={`option-button option-button-small ${quiz.lang === code ? "is-selected" : ""}`}
                aria-pressed={quiz.lang === code}
                onClick={() => change({ lang: code })}
              >
                {t(`live.setup.lang.${code}`)}
              </button>
            ))}
          </div>
        </div>

        <div className="quiz-actions">
          {TYPES.map((type) => (
            <button key={type} type="button" className="secondary-button" onClick={() => append([blankQuestion(type)])}>
              + {t(`quizzes.type.${type}`)}
            </button>
          ))}
          <button type="button" className="secondary-button" onClick={() => setPanel(panel === "library" ? null : "library")}>
            {t("quizzes.editor.fromLibrary")}
          </button>
          <button type="button" className="secondary-button" onClick={() => setPanel(panel === "import" ? null : "import")}>
            {t("quizzes.editor.import")}
          </button>
        </div>

        {panel === "library" && <LibraryPicker lang={quiz.lang} onAdd={append} />}
        {panel === "import" && <ImportPanel onAdd={append} />}

        <div className="quiz-editor">
          <ol className="quiz-editor-list">
            {questions.map((q, i) => (
              <li key={i}>
                <button
                  type="button"
                  className={`quiz-editor-item ${i === selected ? "is-selected" : ""} ${error?.question === i + 1 ? "has-error" : ""}`}
                  onClick={() => setSelected(i)}
                >
                  <span className="material-symbols-outlined" aria-hidden="true">
                    {TYPE_ICONS[q.type]}
                  </span>
                  {i + 1}. {q.text || t("quizzes.editor.untitled")}
                </button>
                <button type="button" className="quiz-icon-button" disabled={i === 0} aria-label={t("quizzes.editor.up")}
                  onClick={() => { setQuestions(move(questions, i, -1)); setSelected(i - 1); }}>
                  ↑
                </button>
                <button type="button" className="quiz-icon-button" disabled={i === questions.length - 1}
                  aria-label={t("quizzes.editor.down")}
                  onClick={() => { setQuestions(move(questions, i, 1)); setSelected(i + 1); }}>
                  ↓
                </button>
                <button type="button" className="quiz-icon-button" aria-label={t("quizzes.editor.remove")} onClick={() => remove(i)}>
                  ×
                </button>
              </li>
            ))}
          </ol>

          <QuestionForm
            question={current}
            error={errorHere}
            onChange={(q) => setQuestions(questions.map((old, i) => (i === selected ? q : old)))}
          />
        </div>

        {error && !error.question && <ErrorMessage error={error} />}
        <button type="button" className="primary-button" onClick={save} disabled={saving}>
          {saving ? t("quizzes.editor.saving") : saved ? t("quizzes.editor.saved") : t("quizzes.editor.save")}
        </button>
      </div>
    </main>
  );
}

export default QuizEditorPage;
```

Note: run Prettier-style formatting is not enforced, but `npm run lint` is; split the inline `onClick` blocks over lines if eslint complains.

- [ ] **Step 7: Routes and links.**
  - `src/App.jsx`: import `MyQuizzesPage`, `QuizEditorPage` (and `SoloPlayPage` in Task 9). Inside `<Route element={<AppShell />}>` add `/quizzes`, `/quizzes/new`, `/quizzes/:id`. Add to the route list comment:
    ```
     *   /quizzes                 a teacher's own quizzes
     *   /quizzes/new, /:id       the quiz editor
     *   /quizzes/:id/play        play your own quiz alone
    ```
  - `src/pages/ProfilePage.jsx`: next to the "Past class games" link, inside the same `user && !IS_DEMO` condition, add `<Link className="secondary-button" to="/quizzes">{t("profile.myQuizzes")}</Link>`.

- [ ] **Step 8: Check it by hand**

Run the backend (`cd backend && uvicorn app.main:app --reload --port 8000`) and `npm run dev`. Sign in, open `/quizzes`, create a quiz with one question of each type, add 3 cards from the library, import `public/templates/chemquiz-template.xlsx`, upload a picture, save, reload the page and see everything back. Save with a quiz question that has no correct answer and see that question selected with the message.

- [ ] **Step 9: Lint, test, commit**

Run: `npm run lint && npm test`
Expected: PASS.

```bash
git add src/quizzes src/App.jsx src/pages/ProfilePage.jsx src/i18n/en.js src/i18n/ru.js
git commit -m "Custom quizzes: My quizzes list and the editor (library cards, template import, pictures)"
```

---

### Task 9: Solo play

**Files:**
- Create: `src/quizzes/SoloPlayPage.jsx`
- Modify: `src/App.jsx` (focused route `/quizzes/:id/play`), `src/i18n/en.js`, `src/i18n/ru.js`

**Interfaces:**
- Consumes: `playQuiz(id)` → `{id, title, questions: frozen}`; `grade`, `answerText` from `./grade`; `AnswerInput`.

- [ ] **Step 1: i18n keys**

| key | en | ru |
|---|---|---|
| `quizzes.play.question` | Question {n} of {total} | Вопрос {n} из {total} |
| `quizzes.play.right` | Right! | Верно! |
| `quizzes.play.wrong` | Not quite | Неверно |
| `quizzes.play.timeUp` | Time's up | Время вышло |
| `quizzes.play.itWas` | Answer: {answer} | Ответ: {answer} |
| `quizzes.play.next` | Next | Дальше |
| `quizzes.play.done` | {right} of {total} right | Верно {right} из {total} |
| `quizzes.play.again` | Play again | Ещё раз |
| `quizzes.play.backToList` | My quizzes | Мои квизы |

- [ ] **Step 2: `src/quizzes/SoloPlayPage.jsx`**

```jsx
import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import PageHeader from "../components/PageHeader";
import { ErrorMessage, Loading } from "../components/StatusMessage";
import { imageSrc, IS_DEMO, playQuiz } from "../api/client";
import { useApi } from "../hooks/useApi";
import { useT } from "../i18n";
import AnswerInput from "./AnswerInput";
import { answerText, grade } from "./grade";

/**
 * Play your own quiz alone: one question at a time against its clock, right
 * or wrong straight after, the score at the end. Graded here in the browser
 * (grade.js): it is the author's own quiz, so there is nothing to keep secret.
 * Does not count towards XP or card progress, which belong to the library.
 */
function SoloPlayPage() {
  const { id } = useParams();
  const t = useT();
  const loader = useCallback(() => playQuiz(id), [id]);
  const { data, error, loading, reload } = useApi(loader, [id]);

  if (IS_DEMO) return <p className="section-note">{t("quizzes.demo")}</p>;
  return (
    <main className="live-phone">
      <PageHeader title={data?.title ?? t("quizzes.title")} backTo="/quizzes" />
      {loading && <Loading />}
      {error && <ErrorMessage error={error} onRetry={reload} />}
      {data && <Run key={data.id} quiz={data} t={t} />}
    </main>
  );
}

function Run({ quiz, t }) {
  const [index, setIndex] = useState(0);
  const [right, setRight] = useState(0);
  const [answered, setAnswered] = useState(null); // {correct} once answered
  const [left, setLeft] = useState(quiz.questions[0].time_limit);
  const q = quiz.questions[index];
  const done = index >= quiz.questions.length;
  // Running out of time is an answer too: derived, not stored.
  const result = answered ?? (left <= 0 ? { correct: false, timedOut: true } : null);

  useEffect(() => {
    if (done || result) return undefined;
    const timer = setTimeout(() => setLeft((s) => s - 1), 1000);
    return () => clearTimeout(timer);
  }, [left, result, done]);

  function answer(given) {
    if (result) return;
    const correct = grade(q, given);
    if (correct) setRight((n) => n + 1);
    setAnswered({ correct, timedOut: false });
  }

  function next() {
    const n = index + 1;
    setIndex(n);
    setAnswered(null);
    if (n < quiz.questions.length) setLeft(quiz.questions[n].time_limit);
  }

  function again() {
    setIndex(0);
    setRight(0);
    setAnswered(null);
    setLeft(quiz.questions[0].time_limit);
  }

  if (done) {
    return (
      <section className="live-phone-card">
        <h1>{t("quizzes.play.done", { right, total: quiz.questions.length })}</h1>
        <button type="button" className="primary-button live-inline-button" onClick={again}>
          {t("quizzes.play.again")}
        </button>
        <Link className="text-button" to="/quizzes">
          {t("quizzes.play.backToList")}
        </Link>
      </section>
    );
  }

  const answerWords = answerText(q);
  return (
    <section className="live-phone-question is-custom">
      <p className="live-phone-muted">{t("quizzes.play.question", { n: index + 1, total: quiz.questions.length })}</p>
      {!result && (
        <div className="live-phone-timer" aria-hidden="true">
          <span style={{ width: `${(left / q.time_limit) * 100}%` }} />
        </div>
      )}
      {q.prompt && <p className="live-phone-prompt">{q.prompt}</p>}
      {q.image_url && <img className="live-phone-photo" src={imageSrc(q.image_url)} alt="" draggable="false" />}
      {result ? (
        <div className={`solo-feedback live-phone-result ${result.correct ? "is-right" : "is-wrong"}`}>
          <h1>
            {result.timedOut ? t("quizzes.play.timeUp") : result.correct ? t("quizzes.play.right") : t("quizzes.play.wrong")}
          </h1>
          {!result.correct && answerWords && <p>{t("quizzes.play.itWas", { answer: answerWords })}</p>}
          <button type="button" className="primary-button live-inline-button" onClick={next}>
            {t("quizzes.play.next")}
          </button>
        </div>
      ) : (
        <AnswerInput key={index} question={q} onAnswer={answer} />
      )}
    </section>
  );
}

export default SoloPlayPage;
```

- [ ] **Step 3: Route.** In `src/App.jsx`, among the focused screens: `<Route path="/quizzes/:id/play" element={<SoloPlayPage />} />`.

- [ ] **Step 4: Check by hand** — play the quiz from Task 8 Step 8: answer each type right once and wrong once (Play again), let one question time out.

- [ ] **Step 5: Lint, test, commit**

Run: `npm run lint && npm test` → PASS.

```bash
git add src/quizzes/SoloPlayPage.jsx src/App.jsx src/i18n/en.js src/i18n/ru.js
git commit -m "Custom quizzes: play your own quiz solo"
```

---

### Task 10: Custom quizzes in the class game screens

**Files:**
- Modify: `src/live/LiveSetupPage.jsx`, `src/live/LiveHostPage.jsx`, `src/live/LivePlayPage.jsx`, `src/live/history.js`, `src/i18n/en.js`, `src/i18n/ru.js`
- Test: `src/live/history.test.js` (one case)

**Interfaces:**
- Consumes: `fetchQuizzes()`, `createLiveGame({customQuizId, lang})`, `liveAnswer(pin, token, {position, choiceId, text, value})`, `AnswerInput`; snapshot fields from Task 5 (`question.type`, `reveal.correct_ids`, `reveal.answer_text`, `you.answered`).

- [ ] **Step 1: i18n keys**

| key | en | ru |
|---|---|---|
| `live.setup.source` | Questions | Вопросы |
| `live.setup.fromDeck` | A deck | Колода |
| `live.setup.fromQuiz` | My quiz | Мой квиз |
| `live.setup.noQuizzes` | You have no quizzes yet. {make} | У вас пока нет квизов. {make} |
| `live.setup.makeOne` | Make one | Создать |
| `live.setup.quizNote` | { one: "{n} question, times set per question", other: "{n} questions, times set per question" } | { one: "{n} вопрос, время задано в каждом", few: "{n} вопроса, время задано в каждом", many: "{n} вопросов, время задано в каждом", other: "{n} вопроса, время задано в каждом" } |
| `live.host.answerNow` | Answer on your phones | Отвечайте на телефонах |
| `live.host.typeOnPhones` | Type the answer on your phone | Напишите ответ на телефоне |
| `live.host.sliderRange` | Pick a value from {min} to {max} {unit} | Выберите значение от {min} до {max} {unit} |
| `live.play.itWasAnswer` | Answer: {answer} | Ответ: {answer} |
| `mode.custom` | Own quiz | Свой квиз |

- [ ] **Step 2: history label test** — add to `src/live/history.test.js` a case asserting that a game with `mode: "custom"` gets the label `t("mode.custom")` (follow the file's existing pattern for `choice`). Then in `src/live/history.js` change the `mode` line to:

```js
  const mode = ["choice", "inverted", "custom"].includes(game.mode) ? t(`mode.${game.mode}`) : game.mode;
```

- [ ] **Step 3: Setup page.** In `src/live/LiveSetupPage.jsx`:
  - imports: `useSearchParams` from react-router-dom, `fetchQuizzes`, and `useEffect`.
  - state:

```jsx
  const [params] = useSearchParams();
  const [source, setSource] = useState(params.get("quiz") ? "quiz" : "deck");
  const [quizId, setQuizId] = useState(params.get("quiz") ? Number(params.get("quiz")) : null);
  const [quizzes, setQuizzes] = useState(null);

  useEffect(() => {
    if (!user || IS_DEMO) return;
    fetchQuizzes()
      .then((list) => {
        setQuizzes(list);
        setQuizId((id) => id ?? list[0]?.id ?? null);
      })
      .catch(() => setQuizzes([]));
  }, [user]);
  const quiz = quizzes?.find((q) => q.id === quizId);
```

  - `create()` sends `source === "quiz" ? { customQuizId: quizId, lang: gameLang } : { categorySlug: deck, mode, questionCount: length, timeLimit, lang: gameLang }`.
  - Right after the past-games note, when `user`, render the source switch (two `option-button option-button-small`, labels `live.setup.fromDeck` / `live.setup.fromQuiz`, legend `live.setup.source`).
  - When `source === "quiz"`: render a fieldset listing `quizzes` as `live-deck` buttons (icon `quiz`, name = title, note = `quizzes.questions`), or `rich(t("live.setup.noQuizzes"), { make: <Link to="/quizzes/new">{t("live.setup.makeOne")}</Link> })` when the list is empty; hide the deck, answer-by, questions and time fieldsets (wrap them in `source === "deck" && (...)`); keep the language fieldset.
  - The open button: disabled when `source === "quiz" && !quiz`; its note is `t("live.setup.quizNote", { n: quiz.question_count })` for a quiz, the existing note otherwise.

- [ ] **Step 4: Board.** In `src/live/LiveHostPage.jsx` `QuestionBoard`:

```jsx
  const custom = state.mode === "custom";
  const kind = q?.type ?? "quiz";
  const rightIds = reveal ? (reveal.correct_ids?.length ? reveal.correct_ids : [reveal.correct_id]) : [];
  const photos = inverted || (custom && q?.choices?.some((c) => c.image_url));
```

  - status text when not revealed: `clock.reading ? t("live.host.getReady") : custom ? t("live.host.answerNow") : inverted ? … : …`.
  - stage: when `custom`, instead of the prompt/photo branch render

```jsx
          <div className="live-q-prompt">
            {q.prompt && <strong>{q.prompt}</strong>}
            {q.image_url && (
              <div className="live-q-photo">
                <img src={imageSrc(q.image_url)} alt="" draggable="false" />
              </div>
            )}
            {!reveal && kind === "type" && <span>{t("live.host.typeOnPhones")}</span>}
            {!reveal && kind === "slider" && (
              <span>{t("live.host.sliderRange", { min: formatNumber(q.min), max: formatNumber(q.max), unit: q.unit })}</span>
            )}
          </div>
```

  - reveal aside: `reveal.item ? (existing aside) : reveal.answer_text && (<aside className="live-q-explain"><span className="live-q-explain-label">{t("live.host.answer")}</span><strong>{reveal.answer_text}</strong></aside>)`.
  - options list only when `q.choices`: `isRight = reveal && rightIds.includes(choice.id)`; `<ul className={`live-options ${photos ? "is-photos" : ""}`}>`; the option body: `inverted ? <img …/> : (<>{choice.image_url && <img src={imageSrc(choice.image_url)} alt={choice.name ?? t(`live.shape.${style.key}`)} draggable="false" />}{choice.name && <span className="live-option-text">{choice.name}</span>}</>)`.
  - import `formatNumber` from `../quizzes/grade`.

- [ ] **Step 5: Phone.** In `src/live/LivePlayPage.jsx`:
  - Progress crediting: in the first effect, after `if (!state?.reveal || !state.you.result) return;` add `if (!state.reveal.item) return; // a custom question: not a card, nothing to learn into`.
  - `send(given)` takes the answer object:

```jsx
  async function send(given) {
    if (!state || picked?.position === state.position || state.you.answered) return;
    setPicked({ position: state.position, id: given.choice_id ?? -1 });
    setAnswerError(null);
    if (navigator.vibrate) navigator.vibrate(30);
    try {
      apply(await liveAnswer(pin, token, {
        position: state.position, choiceId: given.choice_id, text: given.text, value: given.value,
      }));
    } catch (err) {
      setPicked(null);
      setAnswerError(err);
    }
  }
```

  - The `PhoneQuestion` call: `picked={picked?.position === state.position ? picked.id : you.answered ? you.answered_id : null}`.
  - In `PhoneQuestion`, the deck buttons call `onPick({ choice_id: choice.id })`. In the "sent" branch use `const index = q.choices ? q.choices.findIndex((c) => c.id === picked) : -1;` and when `index < 0` render the card without a colour class and without the Shape. Before the deck `return`, add the custom branch:

```jsx
  if (state.mode === "custom") {
    return (
      <section className="live-phone-question is-custom">
        <div className="live-phone-timer" aria-hidden="true">
          <span style={{ width: `${clock.fraction * 100}%` }} />
        </div>
        {q.prompt && <p className="live-phone-prompt">{q.prompt}</p>}
        {q.image_url && <img className="live-phone-photo" src={imageSrc(q.image_url)} alt="" draggable="false" />}
        {error && <ErrorMessage error={error} />}
        <AnswerInput question={q} onAnswer={onPick} />
      </section>
    );
  }
```

  - In `PhoneResult`, replace the "it was" line with:

```jsx
      {!result.correct && reveal?.item && <p>{t("live.play.itWas", { name: reveal.item.name })}</p>}
      {!result.correct && !reveal?.item && reveal?.answer_text && (
        <p>{t("live.play.itWasAnswer", { answer: reveal.answer_text })}</p>
      )}
```

- [ ] **Step 6: Check by hand** — `npm run dev:class` + backend; host a custom quiz from `/quizzes` → "Host in class"; join from a phone (or a second browser window at `/join`); play all four types; confirm the board highlights the right options, shows the answer text for typed and slider questions, and the per-question timer; then host a normal deck game and confirm it plays as before. Check `/live/history`: the custom game shows "Own quiz", the CSV opens, "Work on mistakes" starts.

- [ ] **Step 7: Lint, test, commit**

Run: `npm run lint && npm test` → PASS.

```bash
git add src/live src/i18n/en.js src/i18n/ru.js
git commit -m "Class game screens: host a custom quiz; board and phones for every question type"
```

---

### Task 11: Docs, full checks, pull request

**Files:**
- Modify: `README.md`

- [ ] **Step 1: README** — after "Class game (live, like Kahoot)" add a short section "Your own quizzes": where (`/quizzes`, Profile → My quizzes), the four question types, "From the library", the two templates in `public/templates/` (regenerate with `python tools/make_quiz_templates.py`), pictures stored in `backend/static/uploads/` (not committed), and that solo runs do not count towards XP.

- [ ] **Step 2: Full checks**

```bash
npm run lint && npm test
cd backend && python -m pytest -q
```
Expected: all PASS. Make sure `git status` shows no changes in `docs/` or `src/demo/data.json`.

- [ ] **Step 3: Rebase and push**

```bash
git fetch origin && git rebase origin/main
git push -u origin nik/custom-quizzes
```

- [ ] **Step 4: Open the PR** into `main` with a summary of the feature, the new endpoints, the Pillow CI change, the note that `claude/chemquiz-v2-notes.md` in the "Chem Quiz" Claude project should record the "custom quizzes" decisions (JSON document per quiz, solo graded in the browser, import via stdlib), and the attribution line.
