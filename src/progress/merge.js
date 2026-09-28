/**
 * Merge two progress documents. Mirrors backend/app/progress.py -- keep the
 * two in step.
 *
 *   days    per date the larger value wins (total XP is their sum)
 *   cards   per card the most recently studied record wins
 *   badges  union, earliest unlock time kept
 *   stats   per key the larger value wins
 *   goal    from the more recently updated document
 */
import { emptyProgress } from "./engine";

const num = (v, d = 0) => (typeof v === "number" && Number.isFinite(v) ? v : d);

export function normalise(doc) {
  const base = emptyProgress();
  if (!doc || typeof doc !== "object") return base;
  const obj = (v) => (v && typeof v === "object" && !Array.isArray(v) ? v : {});
  return {
    v: 1,
    days: obj(doc.days),
    cards: obj(doc.cards),
    badges: obj(doc.badges),
    stats: obj(doc.stats),
    goal: num(doc.goal, 50) || 50,
    updated: num(doc.updated),
  };
}

export function mergeProgress(a, b) {
  a = normalise(a);
  b = normalise(b);

  const days = { ...a.days };
  for (const [k, v] of Object.entries(b.days)) days[k] = Math.max(num(days[k]), num(v));

  const cards = { ...a.cards };
  for (const [slug, card] of Object.entries(b.cards)) {
    const mine = cards[slug];
    if (!mine || num(card?.last) > num(mine?.last)) cards[slug] = card;
  }

  const badges = { ...a.badges };
  for (const [k, v] of Object.entries(b.badges)) {
    badges[k] = k in badges ? Math.min(num(badges[k]), num(v)) : num(v);
  }

  const stats = { ...a.stats };
  for (const [k, v] of Object.entries(b.stats)) stats[k] = Math.max(num(stats[k]), num(v));

  const newer = a.updated >= b.updated ? a : b;
  return { v: 1, days, cards, badges, stats, goal: newer.goal, updated: Math.max(a.updated, b.updated) };
}

export function isEmptyProgress(doc) {
  const d = normalise(doc);
  return !Object.keys(d.days).length && !Object.keys(d.cards).length;
}
