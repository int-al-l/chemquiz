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
