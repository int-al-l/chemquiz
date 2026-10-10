import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import AnswerInput from "./AnswerInput";

describe("AnswerInput", () => {
  it("quiz and true/false: a tap answers", () => {
    const onAnswer = vi.fn();
    render(<AnswerInput question={{ type: "tf", choices: [{ id: 0, name: "True" }, { id: 1, name: "False" }] }} onAnswer={onAnswer} />);
    fireEvent.click(screen.getByRole("button", { name: "False" }));
    expect(onAnswer).toHaveBeenCalledWith({ choice_id: 1 });
  });

  it("type answer: sends what was typed", () => {
    const onAnswer = vi.fn();
    render(<AnswerInput question={{ type: "type" }} onAnswer={onAnswer} />);
    fireEvent.change(screen.getByLabelText("Type your answer"), { target: { value: "Au" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));
    expect(onAnswer).toHaveBeenCalledWith({ text: "Au" });
  });

  it("slider: starts in the middle and sends the value", () => {
    const onAnswer = vi.fn();
    render(<AnswerInput question={{ type: "slider", min: 0, max: 200, step: 1, unit: "°C" }} onAnswer={onAnswer} />);
    fireEvent.change(screen.getByLabelText("Pick a value"), { target: { value: "120" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));
    expect(onAnswer).toHaveBeenCalledWith({ value: 120 });
  });
});
