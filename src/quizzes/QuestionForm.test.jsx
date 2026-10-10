import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import QuestionForm from "./QuestionForm";

describe("QuestionForm", () => {
  beforeEach(() => window.localStorage.setItem("chemquiz.lang", "en"));

  it("can add a third and fourth answer back", () => {
    const q = { type: "quiz", text: "Q", image: null, time_limit: 20,
      options: [{ text: "A", image: null, correct: true }, { text: "B", image: null, correct: false }] };
    const onChange = vi.fn();
    render(<QuestionForm question={q} onChange={onChange} />);
    fireEvent.click(screen.getByRole("button", { name: "+ Answer" }));
    const update = onChange.mock.calls[0][0];
    const next = typeof update === "function" ? update(q) : update;
    expect(next.options).toHaveLength(3);
    expect(next.options[2]).toEqual({ text: "", image: null, correct: false });
  });
});
