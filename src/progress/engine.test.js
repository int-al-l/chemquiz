import { describe, expect, it } from "vitest";

import * as e from "./engine";
import { mergeProgress } from "./merge";

const DAY = 24 * 3600 * 1000;
const T0 = new Date(2026, 8, 28, 12, 0, 0).getTime();

describe("levels", () => {
  it("starts at level 1 and follows the thresholds", () => {
    expect(e.levelInfo(0).level).toBe(1);
    expect(e.levelInfo(49).level).toBe(1);
    expect(e.levelInfo(50).level).toBe(2);
    expect(e.levelInfo(150).level).toBe(3);
    expect(e.levelInfo(300).level).toBe(4);
    const l = e.levelInfo(100);
    expect(l.into).toBe(50);
    expect(l.span).toBe(100);
    expect(l.toNext).toBe(50);
  });

  it("names levels", () => {
    expect(e.titleFor(1)).toBe("Lab Rookie");
    expect(e.titleFor(8)).toBe("Bench Chemist");
    expect(e.titleFor(25)).toBe("Master Glassblower");
  });
});

describe("cards", () => {
  it("gives XP for the first look only", () => {
    let r = e.lookAt(e.emptyProgress(), "flask", T0);
    expect(r.gained).toBe(e.XP.firstLook);
    r = e.lookAt(r.doc, "flask", T0 + 1);
    expect(r.gained).toBe(0);
  });

  it("moves a known card up a box only when it is due", () => {
    let doc = e.emptyProgress();
    // Known at first sight: straight to box 2.
    doc = e.studyAnswer(doc, "flask", true, T0).doc;
    expect(doc.cards.flask.box).toBe(2);
    expect(e.isDue(doc.cards.flask, T0 + 3600 * 1000)).toBe(false);
    // Box 2 waits 20 hours: knowing it early does not move it.
    const early = e.studyAnswer(doc, "flask", true, T0 + 2000);
    expect(early.doc.cards.flask.box).toBe(2);
    expect(early.gained).toBe(e.XP.knowEarly);
    const later = e.studyAnswer(doc, "flask", true, T0 + DAY);
    expect(later.doc.cards.flask.box).toBe(3);
    expect(later.gained).toBe(e.XP.knowDue);
  });

  it("sends a card back to box 1 when it is still being learnt", () => {
    let doc = e.emptyProgress();
    doc = { ...doc, cards: { flask: { box: 4, seen: 5, last: T0, due: T0 } } };
    doc = e.studyAnswer(doc, "flask", false, T0).doc;
    expect(doc.cards.flask.box).toBe(1);
    expect(e.mastery(doc.cards.flask)).toBe("learning");
    // Back in ten minutes.
    expect(e.isDue(doc.cards.flask, T0 + 5 * 60 * 1000)).toBe(false);
    expect(e.isDue(doc.cards.flask, T0 + 11 * 60 * 1000)).toBe(true);
  });

  it("reports mastery", () => {
    expect(e.mastery(undefined)).toBe("new");
    expect(e.mastery({ seen: 1, box: 1 })).toBe("learning");
    expect(e.mastery({ seen: 1, box: 3 })).toBe("familiar");
    expect(e.mastery({ seen: 1, box: 5 })).toBe("mastered");
  });

  it("lists due cards, most overdue first", () => {
    const doc = {
      ...e.emptyProgress(),
      cards: {
        a: { seen: 1, box: 2, due: T0 - 10 },
        b: { seen: 1, box: 2, due: T0 - 100 },
        c: { seen: 1, box: 2, due: T0 + 100 },
      },
    };
    expect(e.dueSlugs(doc, ["a", "b", "c", "d"], T0)).toEqual(["b", "a"]);
  });
});

describe("quiz", () => {
  it("adds a combo bonus, capped", () => {
    const d = e.emptyProgress();
    expect(e.quizAnswer(d, "x", true, 1, T0).gained).toBe(10);
    expect(e.quizAnswer(d, "x", true, 3, T0).gained).toBe(14);
    expect(e.quizAnswer(d, "x", true, 50, T0).gained).toBe(20);
    expect(e.quizAnswer(d, "x", false, 0, T0).gained).toBe(1);
  });

  it("rewards a perfect quiz of five or more", () => {
    const d = e.emptyProgress();
    expect(e.quizFinished(d, { correct: 5, total: 5 }, T0).gained).toBe(35);
    expect(e.quizFinished(d, { correct: 4, total: 4 }, T0).gained).toBe(10);
  });
});

describe("streaks, goals and badges", () => {
  it("counts consecutive days, allowing today to be empty so far", () => {
    const key = (offset) => e.dayKey(T0 + offset * DAY);
    const doc = { ...e.emptyProgress(), days: { [key(-1)]: 5, [key(-2)]: 5, [key(-4)]: 5 } };
    expect(e.streak(doc, T0)).toBe(2);
    expect(e.streak({ ...doc, days: { ...doc.days, [key(0)]: 1 } }, T0)).toBe(3);
  });

  it("awards the daily goal once and unlocks badges", () => {
    let doc = { ...e.emptyProgress(), goal: 30 };
    const before = doc;
    doc = e.quizAnswer(doc, "flask", true, 1, T0).doc;
    doc = e.quizAnswer(doc, "beaker", true, 2, T0).doc;
    doc = e.quizAnswer(doc, "vial", true, 3, T0).doc;
    doc = e.quizFinished(doc, { correct: 3, total: 3 }, T0).doc;
    const decks = [{ slug: "flasks", name: "Flasks", cards: ["flask"] }];
    const settled = e.settle(before, doc, 46, decks, T0);
    const types = settled.notes.map((n) => n.type);
    expect(types).toContain("goal");
    expect(types).toContain("level");
    expect(settled.doc.badges["first-quiz"]).toBe(T0);
    expect(settled.doc.badges["first-look"]).toBe(T0);
    expect(settled.doc.badges["deck-seen:flasks"]).toBe(T0);
    expect(e.totalXp(settled.doc)).toBe(46 + e.XP.dailyGoal);

    const again = e.settle(settled.doc, settled.doc, 0, decks, T0);
    expect(again.notes.filter((n) => n.type === "goal")).toHaveLength(0);
  });
});

describe("merge", () => {
  it("adds up different days, keeps the newest card and the earliest badge", () => {
    const phone = { days: { "2026-09-27": 40 }, cards: { a: { box: 2, last: 100 } }, badges: { x: 5 }, updated: 100 };
    const laptop = {
      days: { "2026-09-27": 10, "2026-09-28": 25 },
      cards: { a: { box: 3, last: 200 }, b: { box: 1, last: 50 } },
      badges: { x: 3 },
      goal: 100,
      updated: 200,
    };
    const m = mergeProgress(phone, laptop);
    expect(m.days).toEqual({ "2026-09-27": 40, "2026-09-28": 25 });
    expect(m.cards.a.box).toBe(3);
    expect(m.cards.b.box).toBe(1);
    expect(m.badges.x).toBe(3);
    expect(m.goal).toBe(100);
    expect(mergeProgress(laptop, phone)).toEqual(m);
  });
});
