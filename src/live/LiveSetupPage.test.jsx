import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

vi.mock("../api/client", async (original) => ({
  ...(await original()),
  fetchQuizzes: vi.fn().mockResolvedValue([{ id: 5, title: "Посуда", lang: "ru", question_count: 2 }]),
}));
vi.mock("../auth/context", () => ({ useAuth: () => ({ user: { id: 1 } }) }));
vi.mock("../progress/context", () => ({ useProgress: () => ({ catalog: { items: [], decks: [] } }) }));

import LiveSetupPage from "./LiveSetupPage";

describe("class game setup with an own quiz", () => {
  it("plays the quiz in the language it was written in", async () => {
    window.localStorage.setItem("chemquiz.lang", "en");
    render(
      <MemoryRouter initialEntries={["/live?quiz=5"]}>
        <Routes>
          <Route path="/live" element={<LiveSetupPage />} />
        </Routes>
      </MemoryRouter>,
    );
    await screen.findByText("Посуда");
    await waitFor(() => expect(screen.getByRole("button", { name: "Русский" }).getAttribute("aria-pressed")).toBe("true"));
  });
});
