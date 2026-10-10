import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchQuizzes } from "./client";

describe("request errors", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("never shows a validation error list as [object Object]", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: false, status: 422, json: () => Promise.resolve({ detail: [{ msg: "too long" }] }),
    }));
    await expect(fetchQuizzes()).rejects.toThrow("Request failed (422).");
  });
});
