import { describe, expect, it } from "vitest";

import { describeGame, plural } from "./history";

describe("describeGame", () => {
  it("names the deck, the mode and the counts", () => {
    expect(
      describeGame({ category_name: "Condensers", mode: "choice", question_count: 10, asked_count: 10, player_count: 1 }),
    ).toBe("Condensers · Name it · 10 questions · 1 player");
  });

  it("says Everything for the whole library, and how far an unfinished game got", () => {
    expect(
      describeGame({ category_name: null, mode: "inverted", question_count: 10, asked_count: 4, player_count: 3 }),
    ).toBe("Everything · Find it · 4 of 10 questions · 3 players");
  });
});

describe("plural", () => {
  it("adds an s except for one", () => {
    expect(plural(1, "game")).toBe("1 game");
    expect(plural(0, "game")).toBe("0 games");
  });
});
