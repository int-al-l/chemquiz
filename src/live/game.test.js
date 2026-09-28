import { describe, expect, it } from "vitest";

import { ordinal, questionClock } from "./game";

describe("questionClock", () => {
  const q = { phase: "question", starts_at: 100, deadline: 120, time_limit: 20 };

  it("counts down the reading time before answers open", () => {
    expect(questionClock(q, 98.2)).toEqual({ reading: true, left: 2, fraction: 1 });
  });

  it("then counts down the answering time", () => {
    expect(questionClock(q, 110)).toEqual({ reading: false, left: 10, fraction: 0.5 });
    expect(questionClock(q, 125).left).toBe(0);
  });

  it("is idle outside a question", () => {
    expect(questionClock({ ...q, phase: "reveal" }, 110).left).toBe(0);
    expect(questionClock(null, 0).reading).toBe(false);
  });
});

describe("ordinal", () => {
  it("names places", () => {
    expect([1, 2, 3, 4, 11, 12, 13, 21, 22, 103].map(ordinal)).toEqual([
      "1st", "2nd", "3rd", "4th", "11th", "12th", "13th", "21st", "22nd", "103rd",
    ]);
  });
});
