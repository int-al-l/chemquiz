/**
 * The plain logic behind the "Past games" screens, kept apart from the
 * components so it can be tested on its own.
 */

/**
 * "Condensers · Name it · 10 questions · 24 players", in the language of `t`
 * (a status is shown with t(`history.status.${game.status}`)).
 */
export function describeGame(game, t) {
  const questions =
    game.asked_count < game.question_count
      ? t("history.questions-of", { asked: game.asked_count, n: game.question_count })
      : t("history.questions", { n: game.question_count });
  const mode = game.mode === "choice" || game.mode === "inverted" ? t(`mode.${game.mode}`) : game.mode;
  return [
    game.category_name ?? t("history.everything"),
    mode,
    questions,
    t("history.players", { n: game.player_count }),
  ].join(" · ");
}

/** When a game was played (epoch seconds), in the reader's language and time zone. */
export function playedOn(seconds, lang) {
  return new Date(seconds * 1000).toLocaleString(lang, { dateStyle: "medium", timeStyle: "short" });
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
