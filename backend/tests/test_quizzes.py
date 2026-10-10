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
