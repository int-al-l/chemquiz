import { describe, expect, it } from "vitest";

import { blankQuestion, move, tidy, TIME_LIMITS, TYPES } from "./model";

describe("question model", () => {
  it("has a blank of every type", () => {
    for (const type of TYPES) expect(blankQuestion(type).type).toBe(type);
    expect(blankQuestion("quiz").options).toHaveLength(4);
    expect(TIME_LIMITS).toEqual([5, 10, 20, 30, 60, 90, 120, 240]);
  });

  it("drops the blanks a teacher leaves before saving", () => {
    const q = blankQuestion("quiz");
    q.options[0].text = "A";
    q.options[2].text = "C";
    expect(tidy(q).options.map((o) => o.text)).toEqual(["A", "", "C"]); // the first two always stay
    expect(tidy({ ...blankQuestion("type"), accepted: ["Au", " ", ""] }).accepted).toEqual(["Au"]);
  });

  it("moves a question up and down, not off the ends", () => {
    expect(move(["a", "b", "c"], 2, -1)).toEqual(["a", "c", "b"]);
    expect(move(["a", "b", "c"], 0, -1)).toEqual(["a", "b", "c"]);
  });
});
