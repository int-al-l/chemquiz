/**
 * The plain logic behind the "Past games" screens, kept apart from the
 * components so it can be tested on its own.
 */

export const STATUS_LABELS = {
  live: "Still playing",
  finished: "Finished",
  unfinished: "Not finished",
};

const MODE_LABELS = { choice: "Name it", inverted: "Find it" };

export function plural(n, word) {
  return `${n} ${word}${n === 1 ? "" : "s"}`;
}

/** "Condensers · Name it · 10 questions · 24 players" */
export function describeGame(game) {
  const questions =
    game.asked_count < game.question_count
      ? `${game.asked_count} of ${plural(game.question_count, "question")}`
      : plural(game.question_count, "question");
  return [
    game.category_name ?? "Everything",
    MODE_LABELS[game.mode] ?? game.mode,
    questions,
    plural(game.player_count, "player"),
  ].join(" · ");
}

/** When a game was played (epoch seconds), in the reader's locale and time zone. */
export function playedOn(seconds, locale) {
  return new Date(seconds * 1000).toLocaleString(locale, { dateStyle: "medium", timeStyle: "short" });
}

/** Hand a downloaded file to the browser to save. */
export function saveFile({ blob, filename }) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
