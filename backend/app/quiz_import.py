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
