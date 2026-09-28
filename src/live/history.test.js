import { describe, expect, it } from "vitest";

import { translate } from "../i18n";
import { describeGame } from "./history";

const tEn = (key, values) => translate("en", key, values);
const tRu = (key, values) => translate("ru", key, values);

describe("describeGame", () => {
  it("names the deck, the mode and the counts", () => {
    expect(
      describeGame({ category_name: "Condensers", mode: "choice", question_count: 10, asked_count: 10, player_count: 1 }, tEn),
    ).toBe("Condensers · Name it · 10 questions · 1 player");
  });

  it("says Everything for the whole library, and how far an unfinished game got", () => {
    expect(
      describeGame({ category_name: null, mode: "inverted", question_count: 10, asked_count: 4, player_count: 3 }, tEn),
    ).toBe("Everything · Find it · 4 of 10 questions · 3 players");
  });

  it("speaks Russian", () => {
    expect(
      describeGame({ category_name: "Холодильники", mode: "choice", question_count: 5, asked_count: 5, player_count: 22 }, tRu),
    ).toBe("Холодильники · Назови · 5 вопросов · 22 игрока");
  });
});
