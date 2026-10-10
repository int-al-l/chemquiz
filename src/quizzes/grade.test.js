import { describe, expect, it } from "vitest";

import { answerText, formatNumber, grade, normalize } from "./grade";

// The same cases as backend/tests/test_grading.py and the normalize doctest.
describe("normalize (same as backend/app/text.py)", () => {
  it.each([
    ["Condenser, Friedrichs, with 24/40 joint", "condenser friedrichs 24 40 joint"],
    ["  Büchner  funnel ", "buchner funnel"],
    ["Ёлка", "елка"],
    ["24-40", "24 40"],
    ["the", ""],
    ["?", ""],
  ])("%s", (input, out) => expect(normalize(input)).toBe(out));
});

const QUIZ = { type: "quiz", choices: [{ id: 0, name: "A" }, { id: 1, name: "B" }, { id: 2, name: "C" }], correct_ids: [0, 2] };
const TYPED = { type: "type", accepted: ["Au", "Aurum"] };
const SLIDER = { type: "slider", min: 0, max: 1, step: 0.1, answer: 0.5, tolerance: 0.1, unit: "mol" };

describe("grade", () => {
  it("quiz: any correct option", () => {
    expect(grade(QUIZ, { choice_id: 2 })).toBe(true);
    expect(grade(QUIZ, { choice_id: 1 })).toBe(false);
  });
  it("old deck questions use correct_id", () => {
    expect(grade({ choices: [{ id: 9 }], correct_id: 9 }, { choice_id: 9 })).toBe(true);
  });
  it("typed answers are normalised", () => {
    expect(grade(TYPED, { text: " au " })).toBe(true);
    expect(grade(TYPED, { text: "AURUM!" })).toBe(true);
    expect(grade(TYPED, { text: "" })).toBe(false);
  });
  it("slider tolerance, with float noise", () => {
    expect(grade(SLIDER, { value: 0.6 })).toBe(true);
    expect(grade(SLIDER, { value: 0.30000000000000004 + 0.3 })).toBe(true);
    expect(grade(SLIDER, { value: 0.7 })).toBe(false);
  });
});

describe("answerText", () => {
  it("says the right answer", () => {
    expect(answerText(QUIZ)).toBe("A / C");
    expect(answerText(TYPED)).toBe("Au / Aurum");
    expect(answerText(SLIDER)).toBe("0.5 ± 0.1 mol");
    expect(answerText({ ...SLIDER, tolerance: 0, unit: "", answer: 100 })).toBe("100");
    expect(answerText({ item: { name: "Beaker" } })).toBe("Beaker");
  });
  it("formats numbers without float noise", () => {
    expect(formatNumber(0.30000000000000004)).toBe("0.3");
    expect(formatNumber(1234567)).toBe("1234567");
  });
});
