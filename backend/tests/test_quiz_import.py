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
