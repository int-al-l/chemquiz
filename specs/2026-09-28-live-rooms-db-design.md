# Live game rooms in the database, and a history of past games

Date: 2026-09-28 · Branch: `nik/live-rooms-db` · Status: design approved, awaiting spec review

## Why

The live classroom game (`backend/app/live.py`) keeps every room in the
memory of one process. That has three consequences we want to remove:

1. A backend restart or crash in the middle of a lesson ends the game.
2. The backend must run as a single process (no `uvicorn --workers N`).
3. Nothing is left after the game: a teacher cannot look back at results.

This change moves room state into the database (fixing 1 and 2) and, on top
of that, adds a history of past games for signed-in teachers (fixing 3).

A public server (students on mobile data rather than the school Wi-Fi) is a
separate, later sub-project. This design only has to keep that door open: no
SQLite-only SQL, so switching `CHEMQUIZ_DATABASE_URL` to Postgres later works.

## Decisions

- Anyone can still host a game without an account. If the host is signed in
  when the room is created, the game goes into that account's history.
- Students stay anonymous nicknames.
- History shows: the list of games, the final standings, a CSV export, and two
  replay buttons -- "Same settings" and "Work on mistakes". No per-question
  breakdown or per-student grid on screen (the CSV carries per-question marks).
- After a restart the board and phones carry on by themselves with their
  existing tokens. The question clock keeps running in real time: if the server
  was down past a question's deadline, that question simply closes.
- Storage approach: normalised tables (game / players / answers), chosen over a
  JSON snapshot per room (whole-blob rewrites on every write, a blob format to
  keep readable forever) and over Redis (a new dependency even on the teacher's
  laptop, two stores).

## 1. Data

Three new tables, in `app/models.py` next to the others. `create_all` creates
them at startup; no migration step is needed.

**`live_games`** -- one row per game.

| Column | Notes |
| --- | --- |
| `id` | primary key |
| `pin` | `String(6)`, nullable. Unique among live games via a partial unique index `WHERE pin IS NOT NULL` (supported by SQLite and Postgres). Set to NULL when the game is archived, so the PIN can be reused. |
| `host_token` | the host's secret, `String(43)`, unique |
| `host_user_id` | FK `users.id`, nullable, `ON DELETE CASCADE`. NULL = hosted without an account. |
| `mode`, `time_limit`, `question_count` | settings |
| `category_id` | FK `categories.id`, nullable, `ON DELETE SET NULL` |
| `category_slug`, `category_name` | copies, as in `QuizSession`, so history reads correctly after a deck is renamed or removed |
| `questions` | JSON text, frozen at creation, never changed: per question `position`, `correct_id` (the item id), `image_url` / `prompt`, `choices`, and `item` (the card revealed afterwards) |
| `phase` | `lobby` / `question` / `reveal` / `scoreboard` / `finished` |
| `position`, `starts_at`, `deadline`, `closed_at`, `locked` | game state, as in today's `Room` |
| `created_at`, `touched_at`, `started_at`, `finished_at` | `started_at` NULL = never left the lobby; `finished_at` NULL = not played to the end |

All live-game times are floats (epoch seconds), as in today's `live.py`: they
are compared with the server clock, sent to clients as such, and the tests
replace `live._now` with a fake clock.

**`live_players`** -- `id` (primary key; replaces today's per-room counter as
the player id in the API), `game_id` (FK, cascade, indexed), `token` (unique),
`name`, `joined_at`, `last_seen`, `score`, `streak`, `removed`.

**`live_answers`** -- `id`, `game_id` (FK, cascade), `player_id` (FK, cascade),
`position`, `choice_id`, `elapsed`, `correct`, `points`.
`UNIQUE (player_id, position)`: a second answer to the same question is refused
by the database whichever process it arrives at. Index on `(game_id, position)`
for the per-question counts.

**Lifecycle.** A purge runs when a game is created and at startup (like
`crud.purge_stale_sessions` for quizzes). A game untouched for
`ROOM_IDLE_SECONDS` (3 hours):

- owned by a signed-in host and started (`started_at` set) -> **archived**:
  `pin = NULL`, everything else kept;
- otherwise -> **deleted** with its players and answers.

The host's "Close room" (`DELETE /api/live/{pin}`) archives an owned, started
game instead of deleting it. After "Finish", the final standings stay reachable
by PIN until the purge, as today.

Players removed by the host stay in the database with `removed = true` and are
left out of standings, the CSV and the mistakes count, as today.

## 2. Requests and concurrency

Nothing about a game lives in process memory any more: `live.registry` and its
`threading.Lock` are removed. Endpoints stay plain `def`s taking
`db: Session = Depends(get_db)` (so the tests' override keeps working). The
rules -- phases, scoring, streaks, the clock -- stay in `live.py` with the same
shape, operating on the ORM rows instead of dataclasses.

**Locking.** Every action that changes a game (join, answer, next, finish,
lock, remove player, close) starts with one helper, `lock_game(db, pin)`, then
re-reads, applies the rule and commits:

- Postgres: `SELECT ... FOR UPDATE` on the game row (games do not block each other);
- SQLite: the transaction is opened with `BEGIN IMMEDIATE` (one writer for the
  whole database at a time -- fine, the writes are tiny), and the database runs
  in WAL mode (set on connect) so readers never wait for the writer.

The `live_answers` unique constraint stays as a backstop; an `IntegrityError`
there becomes 409 "You have already answered".

**Polls mostly read.** `GET /{pin}/me` and `GET /{pin}/host` do two or three
reads (game, players, answers to the current question). They write only when:

- the current question is due to close (deadline + grace passed): take the
  lock, re-check, close. If several processes race, one closes and the rest see
  it closed. There is still no background timer;
- the caller's `last_seen` is older than 3 seconds: one `UPDATE` of that
  player's row, without the game lock ("away" is shown after 8 seconds, so this
  is precise enough);
- the game's `touched_at` is older than a minute (it only feeds the 3-hour purge).

With 80 players that is roughly 25-30 small writes a second -- comfortable for
SQLite in WAL mode.

**Restart.** With nothing in memory, a restart is a pause. The polling loop in
`src/live/game.js` already keeps retrying on connection errors (only 403, 404
and 410 stop it) and picks the game up again when the server is back.

**Several processes.** `uvicorn --workers N` becomes safe; the "single process"
notes in README and `live.py` are removed.

## 3. API

**Existing `/api/live/...` endpoints keep their shapes**, so the board and
phones need no changes for stage 1. What changes:

- `POST /api/live` reads an optional `Authorization: Bearer` (the frontend
  already sends it on every request when signed in) and records
  `host_user_id`. Without it, nothing changes.
- `DELETE /api/live/{pin}` archives an owned, started game instead of deleting.
- `GET /api/live/{pin}/host` gains one field, `owned` (boolean).

**New history endpoints** require sign-in; another user's game answers 404.
They live under `/api/me/...`, like `/api/me/progress`, which also avoids a
clash with `/api/live/{pin}`.

| Request | Does |
| --- | --- |
| `GET /api/me/live-games` | Games that got past the lobby, newest first: id, date, deck, mode, question and player counts, winner, status (`live` / `finished` / `unfinished`), `has_mistakes`. |
| `GET /api/me/live-games/{id}` | Settings, status, `has_mistakes`, and standings: place, name, score, correct out of N. |
| `GET /api/me/live-games/{id}/results.csv` | The CSV below. |
| `POST /api/me/live-games/{id}/replay` `{"kind": "same" \| "mistakes"}` | Opens a new room owned by the same teacher; answers exactly like `POST /api/live`. 409 with a readable message if there are no mistakes or the deck no longer exists. |
| `DELETE /api/me/live-games/{id}` | Deletes the game from history. 409 "Finish the game first" while it is still being played (PIN set and not finished). |

A game's status: `live` while it has a PIN and is not finished; `finished` when
`finished_at` is set; `unfinished` when archived without finishing.

**Work on mistakes.** An item qualifies when fewer than 80% of the game's
active (not removed) players answered it correctly; a player who did not answer
counts as wrong. Only questions that were actually asked count (an unfinished
game's later questions are ignored). The new room asks exactly those items (in
random order), with the original deck as the pool for the other options, and
the original mode and time limit. "Same settings" draws fresh questions from
the same deck with the same mode, question count (clipped to the deck's size)
and time limit.

**CSV.** UTF-8 with a BOM, `;` as the separator, so Excel with a Russian locale
opens it with a double click (Google Sheets reads it too). One row per active
player in standings order: `Place;Name;Score;Correct`, then one column per
asked question headed like `Q3 Allihn condenser`, holding `+`, `−` or empty (no
answer). Headers are in English, like the rest of the site.

## 4. Frontend

New screens:

- **`/live/history`** -- "Past games": the list, newest first (date, deck,
  mode, players, winner, status). Signed out, it asks you to sign in.
- **`/live/history/:id`** -- one game: settings, the standings, and buttons:
  - **Download CSV** -- `fetch` with the sign-in token, saved from a blob (a
    plain link would not carry the token);
  - **Same settings** and **Work on mistakes** -- create the room and go
    straight to `/live/host/:pin`, storing the host token the way the setup
    screen does. "Work on mistakes" is disabled, with a note, when there were none;
  - **Delete** -- asks for confirmation; disabled while the game is live.

Links:

- the setup screen `/live`: "Past games" when signed in; "Sign in to keep your
  games' results" (linking to sign-in) when not;
- `/profile`: a "Past games" entry;
- the board's final screen, when `owned`: "Results saved to your history" with a link.

Demo build (GitHub Pages): there is no live game there, so the history links
are hidden, and `/live/history` opened directly explains that it needs the
server, as the setup screen does today.

Built from existing pieces (`PageHeader`, `StatusMessage`, `live.css`); new
calls go into `src/api/client.js` next to the other live-game calls.

## 5. Testing

Backend (`backend/tests/test_live.py`, plus a new `test_live_history.py`):

- All 9 existing scenarios stay. Only the helpers that peek into
  `registry.rooms` change, to read the database through `client.session_factory`.
- **Restart:** play into the middle of a question, bring up a fresh app on the
  same database file; the board and phones carry on with their old tokens.
- **Several processes:** two sessions on one SQLite file, in two threads:
  - the same player answering twice at once -> exactly one answer is stored;
  - a last-moment answer racing the deadline close -> scores and streaks stay consistent;
  - two creates forced onto the same PIN -> two different PINs.
- **Purge** (fake clock): an anonymous game is deleted; an owned, started game
  is archived; an owned game that never left the lobby is deleted; an archived
  game's PIN can be reused.
- **History:** only your own games (another user's -> 404; anonymous games
  never appear); CSV (BOM, `;`, `+` / `−` / empty, removed players left out);
  "Same settings"; "Work on mistakes" (the 80% boundary, no answer counts as
  wrong, 409 when there are none); delete (409 while live).

Frontend: `npm run lint`, the existing vitest suite and `npm run build` pass;
vitest cases only where logic sits in plain JS.

Manual check: backend with `--workers 2`, the board and two "phones" in browser
tabs, restart the backend in the middle of a question, and the game goes on.

**Known risk:** CI has no Postgres. The SQL used (partial unique index,
`FOR UPDATE`) is portable, but a real Postgres run belongs to the public-server
sub-project.

## Docs

README ("Class game": drop the single-process note, add history; the Routes
table; the test count), the docstrings of `live.py` and `models.py`. The
project notes (`chemquiz-v2-notes.md` in the "Chem Quiz" Claude project) need
updating too -- outside the repo, so the user does that.

## Order of work

One branch, `nik/live-rooms-db`, with a draft PR opened as soon as this spec is
committed (so the other person sees `live.py` is being reworked). Two stages,
each in its own commits:

1. Rooms in the database -- backend only; the frontend is untouched, since the
   API shapes do not change (the one new field, `owned`, is used in stage 2).
2. History -- the `/api/me/live-games` endpoints, then the two screens and the links.
