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
