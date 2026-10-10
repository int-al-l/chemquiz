import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

let finishUpload;
vi.mock("../api/client", async (original) => ({
  ...(await original()),
  uploadImage: vi.fn(() => new Promise((resolve) => (finishUpload = resolve))),
  importQuiz: vi.fn().mockResolvedValue({
    questions: [{ type: "type", text: "Symbol of gold?", image: null, time_limit: 20, accepted: ["Au"] }],
    errors: [],
  }),
}));
vi.mock("../auth/context", () => ({ useAuth: () => ({ user: { id: 1 } }) }));
vi.mock("../progress/context", () => ({ useProgress: () => ({ catalog: { items: [], decks: [] } }) }));

import QuizEditorPage from "./QuizEditorPage";

function renderEditor() {
  return render(
    <MemoryRouter initialEntries={["/quizzes/new"]}>
      <Routes>
        <Route path="/quizzes/new" element={<QuizEditorPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

const items = () => [...document.querySelectorAll(".quiz-editor-item")].map((b) => b.textContent);

describe("quiz editor", () => {
  beforeEach(() => window.localStorage.setItem("chemquiz.lang", "en"));

  it("keeps what was typed while a picture was uploading", async () => {
    renderEditor();
    const file = document.querySelectorAll('input[type="file"]')[0];
    fireEvent.change(file, { target: { files: [new File(["x"], "a.png", { type: "image/png" })] } });
    fireEvent.change(screen.getByLabelText("Question"), { target: { value: "Typed meanwhile" } });
    await act(async () => finishUpload({ url: "/static/uploads/a.jpg" }));
    await waitFor(() => expect(document.querySelector('img[src="/static/uploads/a.jpg"]')).toBeTruthy());
    expect(screen.getByLabelText("Question").value).toBe("Typed meanwhile");
  });

  it("an import into a new quiz replaces its untouched blank question", async () => {
    renderEditor();
    fireEvent.click(screen.getByRole("button", { name: "Import" }));
    const file = document.querySelector('input[accept=".xlsx,.docx"]');
    fireEvent.change(file, { target: { files: [new File(["x"], "q.xlsx")] } });
    await waitFor(() => expect(items()).toHaveLength(1));
    expect(items()[0]).toContain("Symbol of gold?");
  });
});
