/** A custom quiz's questions as the editor holds them (the stored shape, see backend/app/quizzes.py). */

export const TYPES = ["quiz", "tf", "type", "slider"];
export const TIME_LIMITS = [5, 10, 20, 30, 60, 90, 120, 240];
export const TYPE_ICONS = { quiz: "grid_view", tf: "rule", type: "keyboard", slider: "linear_scale" };

export function blankQuestion(type) {
  const base = { type, text: "", image: null, time_limit: 20 };
  if (type === "quiz") {
    return { ...base, options: [0, 1, 2, 3].map((i) => ({ text: "", image: null, correct: i === 0 })) };
  }
  if (type === "tf") return { ...base, answer: true };
  if (type === "type") return { ...base, accepted: [""] };
  return { ...base, min: 0, max: 100, step: 1, answer: 50, tolerance: 0, unit: "" };
}

/** Drop empty third/fourth options and empty accepted answers, which the server would refuse. */
export function tidy(q) {
  if (q.type === "quiz") return { ...q, options: q.options.filter((o, i) => i < 2 || o.text.trim() || o.image) };
  if (q.type === "type") return { ...q, accepted: q.accepted.filter((a) => a.trim()) };
  return q;
}

export function move(list, index, by) {
  const to = index + by;
  if (to < 0 || to >= list.length) return list;
  const next = [...list];
  [next[index], next[to]] = [next[to], next[index]];
  return next;
}
