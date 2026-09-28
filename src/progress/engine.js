/**
 * Learning progress: the rules, as pure functions over a plain document.
 *
 * The document (kept in localStorage for guests, on the server for accounts):
 *
 *   {
 *     v: 1,
 *     days:   { "2026-09-28": 45, ... }   XP earned per local date
 *     cards:  { slug: { box, seen, right, wrong, last, due } }
 *     badges: { id: unlockedAtMs }
 *     stats:  { quizzes, perfect, bestCombo, rounds, ... }  (also "goal:<date>" flags)
 *     goal:   50                           daily XP goal
 *     updated: ms
 *   }
 *
 * Total XP is the sum of `days`, which is what lets two devices' progress be
 * merged without double counting (see merge.js and backend/app/progress.py).
 *
 * Cards move through Leitner boxes 1..5. "I know it" moves a card up one box
 * when it is due; "still learning" or a wrong quiz answer sends it back to 1.
 * Each box has a waiting time before the card is due again, so review sessions
 * bring back exactly the cards that are about to be forgotten.
 */

const HOUR = 3600 * 1000;

/** Hours before a card in each box is due again (index = box). Box 1 --
 *  "still learning" -- comes back after ten minutes; a card known at first
 *  sight starts in box 2 and waits a day. */
export const BOX_WAIT_HOURS = [0, 1 / 6, 20, 68, 164, 380];

/** The box a known card moves to. */
function promote(before) {
  if (!before.seen || (before.box ?? 0) === 0) return 2;
  return Math.min(MAX_BOX, (before.box ?? 0) + 1);
}
export const MAX_BOX = 5;

export const XP = {
  firstLook: 2,       // flipping a card for the first time ever
  knowDue: 5,         // study: "I know it" on a new or due card
  knowEarly: 1,       // study: "I know it" on a card that is not due yet
  stillLearning: 1,   // study: honest effort still counts
  roundDone: 10,      // study: finishing a round
  quizCorrect: 10,    // plus the combo bonus below
  comboStep: 2,       // extra XP per consecutive correct answer...
  comboCap: 10,       // ...up to this much
  quizWrong: 1,
  quizDone: 10,
  quizPerfect: 25,    // all correct, at least 5 questions
  dailyGoal: 20,
};

export const GOAL_CHOICES = [30, 50, 100, 200];

export function emptyProgress() {
  return { v: 1, days: {}, cards: {}, badges: {}, stats: {}, goal: 50, updated: 0 };
}

/** Local calendar date as YYYY-MM-DD -- streaks follow the person's own days. */
export function dayKey(ms = Date.now()) {
  const d = new Date(ms);
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

// --- levels ------------------------------------------------------------------

/** XP needed to reach `level` (level 1 needs 0). 50, 150, 300, 500, ... */
export function xpForLevel(level) {
  return 25 * level * (level - 1);
}

const TITLES = [
  [1, "Lab Rookie"],
  [3, "Glassware Apprentice"],
  [5, "Bench Hand"],
  [8, "Bench Chemist"],
  [11, "Synthesis Pro"],
  [15, "Distillation Master"],
  [20, "Master Glassblower"],
];

export function titleFor(level) {
  let title = TITLES[0][1];
  for (const [from, name] of TITLES) if (level >= from) title = name;
  return title;
}

export function totalXp(doc) {
  return Object.values(doc.days ?? {}).reduce((sum, v) => sum + (Number(v) || 0), 0);
}

export function levelInfo(xp) {
  let level = 1;
  while (xpForLevel(level + 1) <= xp) level += 1;
  const floor = xpForLevel(level);
  const next = xpForLevel(level + 1);
  return {
    level,
    title: titleFor(level),
    xp,
    into: xp - floor,
    span: next - floor,
    toNext: next - xp,
    fraction: (xp - floor) / (next - floor),
  };
}

// --- streaks and goals -----------------------------------------------------------

export function todayXp(doc, now = Date.now()) {
  return doc.days?.[dayKey(now)] ?? 0;
}

/** Consecutive days with any XP, ending today (or yesterday, if today is still empty). */
export function streak(doc, now = Date.now()) {
  const days = doc.days ?? {};
  let cursor = new Date(now);
  if (!days[dayKey(cursor.getTime())]) cursor.setDate(cursor.getDate() - 1);
  let count = 0;
  while (days[dayKey(cursor.getTime())] > 0) {
    count += 1;
    cursor.setDate(cursor.getDate() - 1);
  }
  return count;
}

/** The last `n` days, oldest first, for a small activity strip. */
export function recentDays(doc, n = 7, now = Date.now()) {
  const out = [];
  const cursor = new Date(now);
  cursor.setDate(cursor.getDate() - (n - 1));
  for (let i = 0; i < n; i += 1) {
    const key = dayKey(cursor.getTime());
    out.push({ key, xp: doc.days?.[key] ?? 0, weekday: cursor.getDay() });
    cursor.setDate(cursor.getDate() + 1);
  }
  return out;
}

// --- cards -------------------------------------------------------------------

export function mastery(card) {
  if (!card || !card.seen) return "new";
  if ((card.box ?? 0) >= 4) return "mastered";
  if ((card.box ?? 0) >= 3) return "familiar";
  return "learning";
}

export const MASTERY_LABEL = {
  new: "New",
  learning: "Learning",
  familiar: "Familiar",
  mastered: "Mastered",
};

export function isDue(card, now = Date.now()) {
  return Boolean(card && card.seen && (card.box ?? 0) >= 1 && (card.due ?? 0) <= now);
}

function withBox(card, box, now) {
  return { ...card, box, due: now + BOX_WAIT_HOURS[box] * HOUR };
}

// --- events ------------------------------------------------------------------
//
// Each event takes the document and returns { doc, gained, notes } where
// `gained` is XP earned and `notes` are things worth telling the person
// (level ups and new badges are added later by `settle`).

function addXp(doc, amount, now) {
  if (!amount) return doc;
  const key = dayKey(now);
  return { ...doc, days: { ...doc.days, [key]: (doc.days?.[key] ?? 0) + amount } };
}

function bump(doc, stat, by = 1) {
  return { ...doc, stats: { ...doc.stats, [stat]: (doc.stats?.[stat] ?? 0) + by } };
}

function putCard(doc, slug, card) {
  return { ...doc, cards: { ...doc.cards, [slug]: card } };
}

/** The card was turned over (or otherwise looked at properly). */
export function lookAt(doc, slug, now = Date.now()) {
  const card = doc.cards?.[slug];
  if (card?.seen) return { doc, gained: 0 };
  const next = putCard(doc, slug, { box: 0, seen: 1, right: 0, wrong: 0, last: now, due: now });
  return { doc: addXp(next, XP.firstLook, now), gained: XP.firstLook };
}

/** Study mode: the person sorted a card as known (true) or still learning (false). */
export function studyAnswer(doc, slug, known, now = Date.now()) {
  const before = doc.cards?.[slug] ?? { box: 0, seen: 0, right: 0, wrong: 0 };
  let gained = before.seen ? 0 : XP.firstLook;
  let card = { ...before, seen: (before.seen ?? 0) + 1, last: now };

  if (known) {
    const due = !before.seen || (before.box ?? 0) === 0 || isDue(before, now);
    card.right = (card.right ?? 0) + 1;
    if (due) {
      card = withBox(card, promote(before), now);
      gained += XP.knowDue;
    } else {
      card.due = before.due;
      gained += XP.knowEarly;
    }
  } else {
    card.wrong = (card.wrong ?? 0) + 1;
    card = withBox(card, 1, now);
    gained += XP.stillLearning;
  }

  let next = putCard(doc, slug, card);
  next = bump(next, "studied");
  return { doc: addXp(next, gained, now), gained };
}

export function roundFinished(doc, now = Date.now()) {
  const next = bump(doc, "rounds");
  return { doc: addXp(next, XP.roundDone, now), gained: XP.roundDone };
}

/** One quiz answer. `combo` is the run of correct answers *including* this one. */
export function quizAnswer(doc, slug, correct, combo, now = Date.now()) {
  const before = doc.cards?.[slug] ?? { box: 0, seen: 0, right: 0, wrong: 0 };
  let card = { ...before, seen: (before.seen ?? 0) + 1, last: now };
  let gained;

  if (correct) {
    card.right = (card.right ?? 0) + 1;
    const due = !before.seen || (before.box ?? 0) === 0 || isDue(before, now);
    card = due ? withBox(card, promote(before), now) : { ...card, due: before.due };
    gained = XP.quizCorrect + Math.min(XP.comboCap, Math.max(0, combo - 1) * XP.comboStep);
  } else {
    card.wrong = (card.wrong ?? 0) + 1;
    card = withBox(card, 1, now);
    gained = XP.quizWrong;
  }

  let next = putCard(doc, slug, card);
  next = bump(next, "quizAnswers");
  if (correct) next = bump(next, "quizCorrect");
  if (combo > (next.stats?.bestCombo ?? 0)) {
    next = { ...next, stats: { ...next.stats, bestCombo: combo } };
  }
  return { doc: addXp(next, gained, now), gained };
}

export function quizFinished(doc, { correct, total }, now = Date.now()) {
  let next = bump(doc, "quizzes");
  let gained = XP.quizDone;
  if (total >= 5 && correct === total) {
    next = bump(next, "perfect");
    gained += XP.quizPerfect;
  }
  return { doc: addXp(next, gained, now), gained };
}

// --- badges ------------------------------------------------------------------

const seenCount = (doc) => Object.values(doc.cards ?? {}).filter((c) => c.seen).length;

/** Badges that do not depend on the catalogue. */
export const BADGES = [
  { id: "first-look", icon: "visibility", title: "First look", blurb: "Turn over your first card", test: (d) => seenCount(d) >= 1 },
  { id: "seen-25", icon: "style", title: "Curious mind", blurb: "Study 25 different cards", test: (d) => seenCount(d) >= 25 },
  { id: "seen-75", icon: "collections_bookmark", title: "Collector", blurb: "Study 75 different cards", test: (d) => seenCount(d) >= 75 },
  { id: "first-quiz", icon: "quiz", title: "First quiz", blurb: "Finish a quiz", test: (d) => (d.stats?.quizzes ?? 0) >= 1 },
  { id: "perfect", icon: "workspace_premium", title: "Flawless", blurb: "Get every answer right in a quiz of 5 or more", test: (d) => (d.stats?.perfect ?? 0) >= 1 },
  { id: "combo-10", icon: "local_fire_department", title: "On fire", blurb: "10 correct answers in a row", test: (d) => (d.stats?.bestCombo ?? 0) >= 10 },
  { id: "rounds-5", icon: "repeat", title: "Drill sergeant", blurb: "Finish 5 study rounds", test: (d) => (d.stats?.rounds ?? 0) >= 5 },
  { id: "streak-3", icon: "bolt", title: "Warming up", blurb: "Study 3 days in a row", test: (d, now) => streak(d, now) >= 3 },
  { id: "streak-7", icon: "whatshot", title: "One week strong", blurb: "Study 7 days in a row", test: (d, now) => streak(d, now) >= 7 },
  { id: "streak-30", icon: "military_tech", title: "Unstoppable", blurb: "Study 30 days in a row", test: (d, now) => streak(d, now) >= 30 },
  { id: "level-5", icon: "science", title: "Bench Hand", blurb: "Reach level 5", test: (d) => levelInfo(totalXp(d)).level >= 5 },
  { id: "level-10", icon: "biotech", title: "Bench Chemist", blurb: "Reach level 10", test: (d) => levelInfo(totalXp(d)).level >= 10 },
];

/**
 * Badges for each deck: "explorer" when every card has been studied, "master"
 * when every card is mastered. `decks` is [{ slug, name, cards: [slug] }].
 */
export function deckBadges(decks) {
  const out = [];
  for (const deck of decks ?? []) {
    if (!deck.cards?.length) continue;
    out.push({
      id: `deck-seen:${deck.slug}`,
      icon: "explore",
      deck: deck.name,
      title: `${deck.name} explorer`,
      blurb: `Study every card in ${deck.name}`,
      test: (d) => deck.cards.every((s) => d.cards?.[s]?.seen),
    });
    out.push({
      id: `deck-master:${deck.slug}`,
      icon: "emoji_events",
      deck: deck.name,
      title: `${deck.name} master`,
      blurb: `Master every card in ${deck.name}`,
      test: (d) => deck.cards.every((s) => mastery(d.cards?.[s]) === "mastered"),
    });
  }
  return out;
}

/**
 * After any event: award the daily-goal bonus, unlock badges, and report
 * level-ups. Returns { doc, notes } where notes are
 *   { type: "xp", amount } | { type: "level", level, title } |
 *   { type: "badge", badge } | { type: "goal" }
 */
export function settle(before, after, gained, decks, now = Date.now()) {
  const notes = [];
  let doc = after;
  let bonus = 0;

  const key = dayKey(now);
  const flag = `goal:${key}`;
  if (!doc.stats?.[flag] && todayXp(doc, now) >= (doc.goal ?? 50)) {
    doc = addXp({ ...doc, stats: { ...doc.stats, [flag]: 1 } }, XP.dailyGoal, now);
    bonus = XP.dailyGoal;
    notes.push({ type: "goal" });
  }

  if (gained + bonus > 0) notes.unshift({ type: "xp", amount: gained + bonus });

  const was = levelInfo(totalXp(before)).level;
  const is = levelInfo(totalXp(doc));
  if (is.level > was) {
    const newTitle = titleFor(was) !== is.title;
    notes.push({ type: "level", level: is.level, title: is.title, newTitle });
  }

  for (const badge of [...BADGES, ...deckBadges(decks)]) {
    if (doc.badges?.[badge.id]) continue;
    if (badge.test(doc, now)) {
      doc = { ...doc, badges: { ...doc.badges, [badge.id]: now } };
      notes.push({ type: "badge", badge });
    }
  }

  return { doc: { ...doc, updated: now }, notes };
}

/** Summary counts for a set of card slugs. */
export function deckSummary(doc, slugs, now = Date.now()) {
  const out = { total: slugs.length, new: 0, learning: 0, familiar: 0, mastered: 0, due: 0 };
  for (const slug of slugs) {
    const card = doc.cards?.[slug];
    out[mastery(card)] += 1;
    if (isDue(card, now)) out.due += 1;
  }
  return out;
}

/** Slugs due for review, most overdue first. */
export function dueSlugs(doc, slugs, now = Date.now()) {
  return slugs
    .filter((s) => isDue(doc.cards?.[s], now))
    .sort((a, b) => (doc.cards[a].due ?? 0) - (doc.cards[b].due ?? 0));
}
