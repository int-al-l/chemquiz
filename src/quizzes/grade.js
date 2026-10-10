/**
 * Is an answer right? The solo player's copy of backend/app/grading.py and
 * the normaliser in backend/app/text.py -- keep the three in step (the tests
 * on both sides share their cases).
 */

const STOPWORDS = new Set(["a", "an", "the", "with", "and"]);
const EPSILON = 1e-9;

export function normalize(value) {
  if (!value) return "";
  let text = value.normalize("NFKD").replace(/\p{M}/gu, "").toLowerCase();
  text = text.replace(/(\d)\s*[/-]\s*(\d)/g, "$1 $2");
  text = text.replace(/[^\p{L}\p{N}_\s/]/gu, " ").replace(/\//g, " ").replace(/\s+/g, " ").trim();
  return text
    .split(" ")
    .filter((t) => t && !STOPWORDS.has(t))
    .join(" ");
}

const kind = (q) => q.type ?? "quiz";
export const correctIds = (q) => q.correct_ids ?? [q.correct_id];

export function grade(q, given) {
  const k = kind(q);
  if (k === "quiz" || k === "tf") return correctIds(q).includes(given.choice_id);
  if (k === "type") {
    const typed = normalize(given.text ?? "");
    return Boolean(typed) && q.accepted.some((a) => normalize(a) === typed);
  }
  return Math.abs(given.value - q.answer) <= q.tolerance + EPSILON;
}

/** 0.30000000000000004 -> "0.3", 100 -> "100". */
export function formatNumber(x) {
  return String(Number(Number(x).toFixed(6)));
}

/** The right answer in words; null when it is only pictures. */
export function answerText(q) {
  if (q.item) return q.item.name;
  const k = kind(q);
  if (k === "quiz" || k === "tf") {
    const right = correctIds(q);
    const names = q.choices.filter((c) => right.includes(c.id) && c.name).map((c) => c.name);
    return names.join(" / ") || null;
  }
  if (k === "type") return q.accepted.join(" / ");
  let text = formatNumber(q.answer);
  if (q.tolerance) text += ` ± ${formatNumber(q.tolerance)}`;
  if (q.unit) text += ` ${q.unit}`;
  return text;
}
