import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

vi.mock("../api/client", async (original) => ({
  ...(await original()),
  peekLiveGame: vi.fn().mockResolvedValue({ pin: "123456", phase: "lobby", joinable: true, player_count: 0, lang: "ru" }),
}));

import JoinPage from "./JoinPage";
import { peekLiveGame } from "../api/client";

describe("joining by QR code", () => {
  it("asks the game for its language and speaks it", async () => {
    window.localStorage.setItem("chemquiz.lang", "en");
    render(
      <MemoryRouter initialEntries={["/join/123456"]}>
        <Routes>
          <Route path="/join/:pin" element={<JoinPage />} />
        </Routes>
      </MemoryRouter>,
    );
    expect(await screen.findByText("Ваше имя")).toBeTruthy();
    expect(peekLiveGame).toHaveBeenCalledWith("123456");
  });
});
