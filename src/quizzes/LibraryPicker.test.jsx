import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const items = Array.from({ length: 150 }, (_, i) => ({ slug: `card-${i}`, name: `Card ${i}`, image_url: null }));
vi.mock("../progress/context", () => ({ useProgress: () => ({ catalog: { items, decks: [] } }) }));

import LibraryPicker from "./LibraryPicker";

describe("LibraryPicker", () => {
  beforeEach(() => window.localStorage.setItem("chemquiz.lang", "en"));

  it("takes at most 100 cards at a time, the server's limit", () => {
    render(<LibraryPicker lang="en" onAdd={() => {}} />);
    fireEvent.click(screen.getByRole("button", { name: "Select all" }));
    expect(screen.getByRole("button", { name: "Add 100 questions" })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Card 140" }));
    expect(screen.getByRole("button", { name: "Add 100 questions" })).toBeTruthy();
  });
});
