import { expect, test, vi } from "vitest";

// Card ids are positions in data.json, so a quiz saved before the catalog was
// rebuilt would grade a syringe photo as "TLC plate". Such quizzes must expire.
test("a quiz saved against another catalog is expired, not graded", async () => {
  window.localStorage.clear();
  let { demoRequest } = await import("./backend.js");
  const quiz = await demoRequest("/api/quiz/start", {
    method: "POST",
    body: JSON.stringify({ mode: "choice", question_count: 3 }),
  });
  expect((await demoRequest(`/api/quiz/${quiz.token}`)).token).toBe(quiz.token);

  const stored = JSON.parse(window.localStorage.getItem("chemquiz.demo.db.v1"));
  delete stored.sessions[quiz.token].catalog; // as saved before stamps existed
  window.localStorage.setItem("chemquiz.demo.db.v1", JSON.stringify(stored));
  vi.resetModules();
  ({ demoRequest } = await import("./backend.js"));

  expect((await demoRequest(`/api/quiz/${quiz.token}`)).__error.code).toBe("quiz_not_found");
});
