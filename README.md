# ChemQuiz

A quiz site for identifying chemistry glassware from photographs.

React + Vite on the front, FastAPI + SQLite on the back. Flashcards with spaced
repetition, XP, levels, streaks and badges; two quiz modes; accounts with email
verification. Content: 74 pieces of glassware in 8 decks, with 252
photographs from the SYNTHWARE catalogue at chengduglassware.com (chosen and
cropped by `catalog/synthware/`). The names and descriptions are written for
the site, for someone meeting the glassware for the first time.

## Running it

Two processes. Start the backend first.

**Backend** (from `backend/`):

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The server creates the database and loads `seed_data.py` into it the first time
it starts, so there is no separate setup step. Run `python seed.py` yourself to
reload after editing the content, or `python seed.py --reset` to wipe and
rebuild (which also clears accounts and saved lists).

The API is then on http://localhost:8000, with interactive docs at
http://localhost:8000/docs.

**Frontend** (from the project root):

```bash
npm install
npm run dev
```

http://localhost:5173. Vite proxies `/api` and `/static` through to port 8000,
so the browser only ever sees one origin and CORS never comes up.

## Class game (live, like Kahoot)

The teacher's screen is the board; students answer on their phones.

1. Start the backend as above, then the frontend with `npm run dev:class`
   (the same as `npm run dev`, but reachable from other devices on the
   network).
2. On the board, open **Host a class game**, pick a deck, the mode, the number
   of questions and the time per question, and open the room.
3. Students scan the QR code, or go to the address shown and type the 6-digit
   PIN, then pick a nickname. The host can remove a player or lock the room.
4. Press **Start** (or Space). Each question is on the board for 3 seconds
   before answers open; it closes when time runs out or everyone has answered.
   Then the board shows the right answer and how the class voted, then the
   standings. A right answer scores 500-1000 points depending on speed, plus
   100 per answer in a row (up to 500).

The phones and the teacher's laptop must be on the same network, and the
firewall must allow port 5173. If the board is opened as `localhost`, it asks
the server for the laptop's network address and puts that in the QR code.

Games are kept in the database, so restarting the backend is only a pause:
the board and the phones pick the game up again by themselves. The backend
can also run as several processes (`uvicorn app.main:app --workers 4`). The
browser-only demo on GitHub Pages cannot connect phones, so it explains that
instead.

**Past games.** If you are signed in when you open the room, the game is kept
once it has started: **Past games** (on the class game screen and in your
profile) lists them with the final standings, a CSV of who answered what
(opens in Excel or Google Sheets), and two ways to play again -- the same
settings with fresh questions, or **Work on mistakes**, which asks only the
items fewer than 80% of the class got right. Games hosted without signing in
are not kept.

**Language of a game.** The teacher picks English or Russian when opening the
room; the board and every phone follow it, whatever language the phones are
set to.

## Demo build (no backend)

`npm run build:demo` builds a version that runs entirely in the browser: the
API is replaced by `src/demo/backend.js`, which follows the same rules as the
FastAPI backend and keeps everything (accounts included) in the browser's
localStorage. No email is sent -- the verification code is shown on screen.
The output in `dist-demo/` is plain static files (hash-based URLs), so it can be
hosted anywhere.

`npm run build:pages` writes the same build into `docs/`, which GitHub Pages
serves (Settings -> Pages -> branch `main`, folder `/docs`) at
https://int-al-l.github.io/chemquiz/ . A GitHub Action
(`.github/workflows/pages.yml`) re-runs it, together with
`python tools/make_demo_data.py`, after every merge to `main` and commits the
result, so there is no need to do it by hand.

## Working together

Two people work on this repo. Every change goes on its own branch and into
`main` through a pull request; CI checks each one. `docs/` and
`src/demo/data.json` are rebuilt automatically after each merge, so don't commit
them by hand. The full rules are in [CLAUDE.md](CLAUDE.md), which Claude reads
at the start of every session.

## Layout

```
src/
  api/client.js        every call to the backend
  auth/                who is signed in (provider, context, hook)
  saved/               "My list": the server when signed in, localStorage when not
  progress/            XP, levels, spaced repetition, badges (engine.js), and sync
  hooks/useApi.js      loading and error state for a fetch
  components/          PageHeader, Thumbnail, StatusMessage
  pages/               one file per route
  live/                the class game: setup, board, join, phone
backend/
  app/models.py        Category, Item, ItemPhoto, ItemAlias, User, SavedItem,
                       QuizSession, QuizQuestion, LiveGame, LivePlayer, LiveAnswer
  app/crud.py          queries and the quiz rules
  app/routers/         HTTP endpoints
  app/text.py          name normalisation for aliases
  app/security.py      password hashing, one-time codes
  app/mailer.py        sending the verification and reset emails
  app/progress.py      merging progress documents
  app/live.py          the class game's rules, on the live_* tables
  app/live_history.py  past class games: standings, CSV, play again
  seed_data.py         the content itself, hand-checked
  seed.py              loads seed_data.py into the database
  static/images/       glassware photographs
  tests/               pytest suite
catalog/synthware/     which Synthware photos show each card, and the build
catalog/*.py           the earlier Kemtech PDF pipeline (no longer used)
tools/fetch_synthware.py  downloads the Synthware catalogue (run it locally)
tools/fetch_labware_shop.py  downloads Synthware's shop, labware-shop.com (run it locally)
```

## Routes

| URL | Screen |
| --- | --- |
| `/` | main menu: level, streak, daily goal, Review when cards are due |
| `/explore` | every deck with its mastery bar |
| `/explore/:slug` | one deck as flashcards; `?mode=study` or `?mode=grid` |
| `/explore/all`, `/explore/saved` | every card; My list as a deck |
| `/review` | cards due for spaced review |
| `/list` | saved items |
| `/profile` | level, stats, week chart, daily goal, badges, sign out |
| `/sign-in` | sign in, or create an account |
| `/verify-email` | the six-digit code, or `?token=` from the emailed link |
| `/reset-password` | forgotten password (code, or `?token=` from the link) |
| `/quiz/setup[/:slug]` | choose mode and length |
| `/quiz/:token` | a quiz in progress |
| `/quiz/:token/results` | the score afterwards |
| `/live` | set up a class game |
| `/live/host/:pin` | the board during a class game |
| `/live/history` | past class games (signed in) |
| `/live/history/:id` | one past game: standings, CSV, play again |
| `/join[/:pin]`, `/play/:pin` | a student joins, and plays on their phone |

## Languages

The site speaks English and Russian. The switch is on the main menu and in
the profile; until someone picks, it follows the browser. Card and deck texts
come from the server in the chosen language: English from
`backend/seed_data.py`, Russian from `backend/content_ru.py` (hand-edited --
add an entry there for every new card; a test fails until you do, and the
site shows the English text meanwhile). Interface texts are in
`src/i18n/en.js` and `ru.js`; server messages in `backend/app/messages.py`.
The browser sends the choice as `Accept-Language`, and errors come back as
`{"detail": ..., "code": ...}` in that language.

## Learning with cards

A deck is a category. Each card is mostly photograph, with the name in a strip
underneath (the eye button hides names, to test yourself); tapping turns it
over to the description. Swipe left and right to move between cards, or use the
arrow keys and space bar.

**Study** mode is the Quizlet-style sort: swipe right "I know it", left "still
learning". Cards still being learnt come back in the next round until none are
left. Every answer, here and in quizzes, moves the card through Leitner boxes
1-5 (`src/progress/engine.js`): a card known at first sight starts in box 2 and
comes back tomorrow; each later "know it" on a due card moves it up a box and
roughly triples the wait; "still learning" or a wrong quiz answer sends it back
to box 1 (ten minutes). **Review** gathers whatever is due, across every deck.

Mastery shown on cards and decks: *new*, *learning* (box 1-2), *familiar*
(box 3), *mastered* (box 4-5).

**XP and levels.** First look at a card 2, "know it" on a due card 5 (1 if not
due yet), "still learning" 1, finishing a round 10; a correct quiz answer 10
plus 2 per answer in the current streak (up to +10), a wrong one 1, finishing a
quiz 10, a perfect quiz of 5 or more +25, reaching the daily goal +20. Level
*n* needs 25*n*(*n*-1) XP (50, 150, 300, 500...), with titles from Lab Rookie to
Master Glassblower. There is a daily-goal ring, a day streak, a week chart and
badges (including "explorer" and "master" for each deck).

Progress is a JSON document. Signed out it lives in `localStorage`; signed in
it is stored on the account (`/api/me/progress`) and the guest progress is
merged in on sign-in. Two devices merge rather than overwrite: XP is kept per
day, so days earned on different devices add up; for each card the most
recently studied record wins (`src/progress/merge.js`, mirrored in
`backend/app/progress.py`).

## How a quiz works

A quiz is built once, server-side, and addressed by an unguessable token. All
the questions, and in multiple-choice mode all the options and their order, are
fixed at that moment, so a refresh or a back-button press resumes the same quiz
rather than quietly rerolling it.

There are two modes. **Name it** (`choice`) shows a photograph and four names;
**Find it** (`inverted`) shows a name and four photographs, sent without their
names. The number of questions is typed in or picked (up to the number of
pieces in the category).

The answers stay on the server. A question payload carries nothing that says
which option is right. Grading happens in
`POST /api/quiz/{token}/answer`, and the results endpoint withholds an item
until its question has been answered. Answering the same question twice is
refused, so a replayed request cannot turn a wrong answer into a right one.

The play screen is laid out to fit one phone screen (`100dvh`): the question
fills the middle, and a bottom bar always holds the Next button. After an
answer, "Why?" opens the description in a sheet from the bottom rather than
pushing Next off screen. Keys 1-4 answer, Enter moves on.

## One item, many photographs

The catalog describes the same piece of glassware many times over: a 50 mL and a
100 mL conical flask, a condenser with and without removable hose connections.
Those are not separate things to learn, so they are folded into one **item** --
one card in Explore -- carrying several **photos**.

That fold is what keeps the quiz honest. A question's four options are four
different items, and entries that a photograph cannot tell apart were merged
into one item during curation, so a question can never offer two right answers.
Meanwhile a question picks one of the item's photographs at random, so the same
piece of glassware looks different from one quiz to the next.

Which photographs belong to which card is recorded in
`catalog/synthware/curate.py`.

## Accounts

Email and password. Creating an account emails a **six-digit code and a link**
(either one confirms the address); an account cannot sign in until it is
confirmed. "Forgot password" sends the same kind of email. Passwords are hashed
with scrypt (`app/security.py`); codes are stored hashed, expire after 15
minutes, allow 5 wrong tries, and can be re-sent once a minute. Changing the
password signs every other device out. Accounts from the old passwordless
version are asked to use "Forgot password" to set one.

The browser keeps a session token and sends it as `Authorization: Bearer`.
"My list" and progress follow the account; before signing in both live in the
browser and are adopted on sign-in (added, never replacing).

### Sending the emails

Set these before starting the backend. Without `CHEMQUIZ_SMTP_HOST`, emails are
**printed to the backend console** instead, which is enough to try everything
locally.

| Variable | Example |
| --- | --- |
| `CHEMQUIZ_SMTP_HOST` | `smtp.gmail.com` |
| `CHEMQUIZ_SMTP_PORT` | `587` (or `465` with `ssl`) |
| `CHEMQUIZ_SMTP_SECURITY` | `starttls`, `ssl` or `none` |
| `CHEMQUIZ_SMTP_USER` | `you@gmail.com` |
| `CHEMQUIZ_SMTP_PASSWORD` | for Gmail, an *app password* (Google Account > Security > App passwords) |
| `CHEMQUIZ_MAIL_FROM` | `ChemQuiz <you@gmail.com>` |
| `CHEMQUIZ_PUBLIC_URL` | where the site is served, for the link in the email: `http://localhost:5173` |

Any SMTP provider works (Gmail, Yandex, Mail.ru, Resend, SendGrid, Mailgun).

## Adding content

Either edit `backend/seed_data.py` by hand and re-run `python seed.py` -- it
upserts by slug and removes cards that are no longer listed -- or regenerate
from the Synthware catalogue:

```bash
python tools/fetch_synthware.py              # needs access to chengduglassware.com
python tools/fetch_labware_shop.py           # optional: labware-shop.com; move its labware/ into synthware/
python catalog/synthware/build.py synthware  # crop photos, rewrite seed_data.py
cd backend && python seed.py
```

A photo whose download is missing this time is kept as the earlier build made
it, so the build also runs with only part of the downloads.

`catalog/synthware/curate.py` holds the choices: which product photos show
each card (clean product shots only -- never the advertising posters with
dimension arrows and captions, which Synthware uses as many main images),
the new cards and their text, and the cards dropped for lack of a clean photo.
`catalog/synthware/labware.py` does the same for the sharper photos from
labware-shop.com (stems `lw:...`), and `curate.COMMONS` for Wikimedia Commons.
`build.py --sheets DIR` writes contact sheets for checking the result by eye.

Whichever way a card is added, give it a Russian name and description in
`backend/content_ru.py` (keyed by the card's slug).

## Tests

```bash
cd backend && python -m pytest    # 123 tests: content, quiz, accounts, progress, class games, languages
npm test                          # vitest: saved-list provider, progress engine
npm run lint                      # eslint, including the React hooks rules
npm run build
```

The frontend tests exist for one reason: the bugs that reached the browser were
all about *ordering*, not logic. A list fetched on page load would land after a
save and overwrite it, so the bookmark filled in and then emptied itself --
invisible on a fast connection, constant on a slow one.
`src/saved/SavedProvider.test.jsx` drives those orderings on purpose.

## Not built yet

* `Base.metadata.create_all` builds the schema at startup, and
  `app/migrate.py` adds any new columns to an existing SQLite database.
  Introduce Alembic before the schema needs anything more than that.
* Quiz sessions are deleted 24 hours after they are created.
* No rate limit on password guessing beyond the per-code limits; put the site
  behind a proxy with request limits before it is public.
