# Custom quizzes: your own questions, cards from the library, Excel/Word import

Date: 2026-10-10 · Branch: `nik/custom-quizzes` · Status: design approved, awaiting spec review

## Why

Today every question is made from a glassware card: "photo → four names" or
"name → four photos". A teacher cannot ask anything else. This change lets a
signed-in user build their own quiz, Kahoot-style, out of:

- questions they write themselves (four types, below);
- cards picked from our library, turned into ordinary editable questions;
- rows of a filled-in Excel or Word template.

The quiz is then played as a class game (PIN, phones, board) or solo.

## Decisions

- A quiz belongs to its author and is visible only to them. No sharing, no
  public library.
- Question types: **quiz** (2–4 options, one or more correct), **true/false**,
  **type answer**, **slider**. Not now: puzzle, poll, double/no points.
- Per question: time limit, picture, pictures in the options.
- Scoring is the existing one for every type: 500–1000 by speed, plus the
  streak bonus.
- Storage: one row per quiz with the questions as a JSON document, saved whole.
  Chosen over normalised question/option tables (three times the code, for
  queries we don't need). Live games already freeze their questions as JSON,
  so a custom quiz drops into them nearly as is.
- Solo play of a custom quiz runs in the browser. The quiz is the author's own,
  so the answers being on the client hides nothing. Solo custom runs give no
  XP, streak or progress (progress is tied to cards).
- Import is parsed on the server with the standard library (`zipfile` + XML).
  No new dependencies. Pictures in the files are not imported.
- The GitHub Pages demo has no backend: the new pages show a notice under
  `IS_DEMO`, as the class game already does.

## 1. Data

New table in `backend/app/models.py`:

**CustomQuiz** `custom_quizzes`: `id`, `user_id` (FK users, indexed), `title`
(≤ 120 chars), `lang` (`en`/`ru`, the language the quiz is written in; used for
the live game's interface language default), `questions` (JSON text),
`created_at`, `updated_at`.

New columns, added by `migrate.add_missing_columns`:

- `LiveGame.custom_quiz_id` (nullable int, no FK: the quiz may be deleted while
  its past games stay in history).
- `LiveAnswer.answer` (nullable text): the typed text or the slider value.
  `choice_id` stays for quiz/true-false answers. It is NOT NULL in existing
  databases and `add_missing_columns` cannot relax that, so typed and slider
  answers store `-1` there.

### Question document

Validated by pydantic in `backend/app/schemas.py`, a discriminated union on
`type`. Common fields: `type`, `text` (≤ 300 chars; may be empty only when
`image` is set), `image` (URL or null), `time_limit` ∈ {5, 10, 20, 30, 60, 90,
120, 240}.

| type     | own fields                                                        | rules |
|----------|-------------------------------------------------------------------|-------|
| `quiz`   | `options: [{text, image, correct}]`                               | 2–4 options; each has text (≤ 75) or image; ≥ 1 correct |
| `tf`     | `answer: bool`                                                    | options are fixed: True / False, localized on display |
| `type`   | `accepted: [str]`                                                 | 1–4 strings, each 1–20 chars |
| `slider` | `min, max, step, answer, tolerance, unit`                         | min < max; step > 0; min ≤ answer ≤ max; 0 ≤ tolerance ≤ max − min; unit ≤ 10 chars |

A quiz holds 1–100 questions. Images must be URLs we issued: `/static/images/…`
(library photos) or `/static/uploads/…` (uploads). Anything else is rejected.

### Grading — `backend/app/grading.py`

`grade(question, answer) -> bool`, used by the live game and mirrored in the
frontend for solo play:

- `quiz`: `answer.choice_id` is an option index (0–3); correct if that option
  is correct. Deck questions keep item ids as option ids and their `correct_id`.
- `tf`: `answer.choice_id` is 0 (true) or 1 (false); correct if it matches.
- `type`: `normalize(answer.text)` equals the `normalize` of any accepted
  string. `normalize` is the existing alias normaliser, `backend/app/text.py`.
- `slider`: `|answer.value − question.answer| ≤ tolerance`; the value must be
  within min..max or it is `not_an_option`.

## 2. API

All under `/api/quizzes`, `current_user` required, 404 for someone else's quiz.

- `GET /api/quizzes`: the user's quizzes: `{id, title, question_count, updated_at}`.
- `POST /api/quizzes` `{title, lang, questions}` → the quiz.
- `GET /api/quizzes/{id}` → `{id, title, lang, questions, …}`.
- `PUT /api/quizzes/{id}`: replace title, lang, questions.
- `DELETE /api/quizzes/{id}`.
- `POST /api/quizzes/from-cards` `{item_slugs, mode: "choice"|"inverted", lang}`
  → `{questions}`, drafts only, nothing saved. Built with `crud.draw_questions`
  (distractors from the card's own deck). `choice` gives a `quiz` question with
  the card's photo and four name options; `inverted` gives the name as text and
  four photo options. Time limit 20 s. Up to 100 slugs.
- `POST /api/quizzes/import` (multipart `file`) → `{questions, errors}` where
  `errors` is `[{row, message}]`. Nothing saved. `.xlsx` or `.docx`, ≤ 2 MB,
  total unpacked size ≤ 20 MB, else 422.
- `POST /api/uploads` (multipart `file`) → `{url}`. Image ≤ 5 MB. Pillow opens
  it (rejects non-images), drops EXIF, shrinks to ≤ 1600 px on the long side,
  re-encodes as JPEG to `backend/static/uploads/<random>.jpg`. A new
  `UPLOADS_DIR` in `config.py`, mounted next to the images.
  Uploads are not tied to a quiz and are never cleaned up
  (`ponytail:` orphaned uploads stay; sweep unreferenced files if disk matters).

Server errors are new keys in `backend/app/messages.py` (en + ru).

## 3. Import template

Two files in `public/templates/`: `chemquiz-template.xlsx` and
`chemquiz-template.docx`. The same columns, Kahoot-like, with example rows for
each type and a header row:

| Type | Question | Answer 1 | Answer 2 | Answer 3 | Answer 4 | Time (s) | Correct |
|------|----------|----------|----------|----------|----------|----------|---------|

- **Type**: `quiz`/`квиз`, `tf`/`верно-неверно`, `type`/`ввод`, `slider`/`ползунок`
  (case-insensitive). Empty means `quiz`.
- **quiz**: Answers 1–4 are options (at least 2); Correct is the option numbers,
  comma-separated (`1` or `2,4`).
- **tf**: Correct is `true`/`верно` or `false`/`неверно`; Answers are ignored.
- **type**: Answers 1–4 are the accepted answers; Correct is ignored.
- **slider**: Answer 1 = min, Answer 2 = max, Answer 3 = tolerance (empty → 0),
  Answer 4 = unit; Correct = the value; step is 1, or 0.1 when any of the
  numbers has a fraction. Decimal comma accepted.
- **Time**: empty → 20; otherwise rounded up to the nearest allowed limit.

Reading:

- xlsx: the first worksheet, via `xl/sharedStrings.xml` + `xl/worksheets/sheet1.xml`
  (shared, inline and numeric cells).
- docx: the first table in `word/document.xml`; a cell's text is its `w:t` runs
  joined, paragraphs joined by a space.

The header row is recognised by the word "Question"/"Вопрос" in column 2 and
skipped; fully empty rows are skipped. Each other row becomes a question or an
error. A row that fails validation is reported by its row number and not
imported; the rest are. Over 100 rows is an error for the rows past 100.

The template files are made once by a small script, `tools/make_quiz_templates.py`
(stdlib `zipfile`, writes minimal valid OOXML), and committed. The import tests
parse these same files.

## 4. Class game

- `LiveSetupPage` gets a source switch: **Deck** / **My quiz** (signed-in
  only). With a quiz, the deck, mode, count and time fields are hidden.
- `POST /api/live` accepts `custom_quiz_id` instead of `category_slug`;
  `live.create_room(custom_quiz=…)` freezes the quiz's questions into
  `LiveGame.questions`, numbered, with each question's own `time_limit`.
  `LiveGame.mode` is `"custom"`, `time_limit` is the longest question's.
- Deck games freeze their questions as `type: "quiz"` with the game's time
  limit, so the board, phones and history read one shape. Old games in the
  database (no `type`) are read as deck questions.
- Wherever the round's clock is computed (`deadline`, `elapsed`, the points
  fraction, and the `time_limit` sent in the snapshot to board and phones),
  the question's `time_limit` is used when present, else the game's.
- `POST /api/live/{pin}/answer` takes `{position, choice_id}` (unchanged) or
  `{position, text}` or `{position, value}`; `Room.answer` calls `grade()`.
  Scoring unchanged.
- `_question_public` sends `type`, `text`, `image_url`, the options without
  `correct`, and for slider `min, max, step, unit`. Nothing that gives the
  answer away (no accepted strings, no slider answer).
- `_reveal` adds what each type needs:
  - quiz / tf: the correct option(s) and vote counts, as now.
  - type: the accepted answers and the right count.
  - slider: answer ± tolerance, unit, and the right count.
  For deck questions the card (`item`) is still shown with its description.
- Phones: four coloured buttons (quiz, with option images when present), two
  buttons (tf), a text box with Send (type), a slider with the value shown and
  Send (slider). The board shows the question text, image, and options.
- History:
  - CSV column headers use the question text (deck games: the card name, as now).
  - "Same settings" for a custom game makes a new room from the same quiz;
    if the quiz was deleted → `quiz_gone`.
  - "Work on mistakes" for a custom game asks the questions (by position)
    fewer than 80% got right, from the frozen questions, so it works even if the
    quiz was edited or deleted since.

## 5. Screens

All strings in `src/i18n/en.js` and `ru.js`.

- **My quizzes** `/quizzes`: linked from the profile and from the class game
  setup. A list with Create, Edit, Delete (with confirm), Play solo, Host in class.
- **Editor** `/quizzes/new`, `/quizzes/:id`:
  - title field;
  - question list on the left (number, type icon, first words), ↑ ↓ to move,
    × to delete;
  - the selected question's form on the right, changing with its type;
  - buttons: **+ Question** (type picker), **+ From library** (deck → tick cards
    → photo→names / name→photos → added at the end), **Import** (links to the two
    templates, then file picker; the imported questions are appended and the
    errors listed), **Save**.
  - leaving with unsaved changes asks for confirmation.
  - validation errors from the server are shown on the question they belong to.
- **Solo player** `/quizzes/:id/play`: one question at a time with the same
  question view as the phone, the timer, right/wrong after each answer, a score
  screen at the end with "Play again".
- The question view (prompt + answer input for each type) is one component,
  `src/quizzes/QuestionView.jsx`, used by the phone and the solo player.

## 6. Tests

Backend (`backend/tests/`):

- `test_quizzes.py`: CRUD and ownership; schema rules (one failing case per
  rule); `from-cards` in both modes; upload accepts a PNG and rejects a
  non-image and an oversized file.
- `test_grading.py`: `grade()` for every type, including normalisation and
  slider tolerance edges.
- `test_quiz_import.py`: both committed templates parse into the expected
  questions; a bad row gives an error with its row number and the others still
  import; a non-zip and an oversized file are rejected.
- `test_live.py` additions: a custom-quiz game end to end with one question of
  each type and per-question time limits; the public question leaks no answer;
  "same" and "mistakes" replays for a custom game; an old-format deck game still
  plays.

Frontend: `QuestionView` renders and submits each type; the solo grader matches
the backend on the same cases.

Checks before pushing: `npm run lint && npm test`, `cd backend && python -m pytest -q`.

## Not doing now

Double / no points, puzzle and poll types, sharing quizzes, pictures inside
imported files, drag-and-drop ordering, solo progress/XP for custom quizzes,
demo-build support. Each fits on top of the same JSON document later.
