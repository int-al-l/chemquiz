/**
 * Thin wrapper around the ChemQuiz API.
 *
 * In development, Vite proxies /api and /static to the FastAPI server on port
 * 8000 (see vite.config.js), so the browser only ever talks to one origin and
 * there is no CORS to think about. Set VITE_API_BASE_URL to point a production
 * build at a backend on a different host.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

/**
 * The signed-in user's token, kept here so every request can carry it without
 * each caller passing it around. Set by the auth provider on sign-in and
 * cleared on sign-out.
 */
let authToken = null;

export function setAuthToken(token) {
  authToken = token ?? null;
}

/** Thrown for any non-2xx response, carrying the server's message. */
export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/** True in the demo build (`npm run build:demo`), where the API runs in the browser. */
export const IS_DEMO = Boolean(import.meta.env.VITE_DEMO);

async function demo(path, options) {
  const { demoRequest } = await import("../demo/backend.js");
  const result = await demoRequest(path, {
    ...options,
    headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
  });
  if (result && result.__error) {
    throw new ApiError(result.__error.detail, result.__error.status);
  }
  return result;
}

/** Demo build only: the code "emailed" to this address, or null. */
export async function demoInbox(email) {
  if (!IS_DEMO) return null;
  const mod = await import("../demo/backend.js");
  return mod.demoInbox(email);
}

async function request(path, options = {}) {
  if (IS_DEMO) return demo(path, options);

  let response;

  try {
    response = await fetch(`${BASE_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
        ...options.headers,
      },
    });
  } catch {
    // fetch only rejects when the request never got a reply at all.
    throw new ApiError(
      "Could not reach the server. Is the backend running?",
      0,
    );
  }

  if (response.status === 204) {
    return null;
  }

  const body = await response.json().catch(() => null);

  if (!response.ok) {
    throw new ApiError(describeFailure(response.status, body), response.status);
  }

  return body;
}

/**
 * Turn a failed response into something the person can act on.
 *
 * The gateway codes are the common case in development and they do not mean
 * the request was wrong -- they mean the Vite proxy forwarded to port 8000 and
 * found nothing listening, which is almost always a backend that is not
 * running. Saying so beats printing a number.
 */
function describeFailure(status, body) {
  if (body?.detail) {
    return body.detail;
  }

  if (status === 502 || status === 503 || status === 504) {
    return (
      "The backend is not responding. Start it with " +
      "`uvicorn app.main:app --reload --port 8000` from the backend folder, " +
      "then try again."
    );
  }

  if (status === 404) {
    return "That is not on the server. It may have been renamed or removed.";
  }

  if (status >= 500) {
    return "The server hit an error. Check the terminal running uvicorn for the traceback.";
  }

  return `Request failed (${status}).`;
}

/** Turn an API-relative image path into something an <img> can load. */
export function imageSrc(imageUrl) {
  if (!imageUrl) return null;
  return `${BASE_URL}${imageUrl}`;
}

// --- content ---------------------------------------------------------------

export function fetchCategories(parentSlug) {
  const query = parentSlug ? `?parent=${encodeURIComponent(parentSlug)}` : "";
  return request(`/api/categories${query}`);
}

export function fetchCategory(slug) {
  return request(`/api/categories/${encodeURIComponent(slug)}`);
}

export function fetchItems(categorySlug) {
  const query = categorySlug
    ? `?category=${encodeURIComponent(categorySlug)}`
    : "";
  return request(`/api/items${query}`);
}

// --- quiz ------------------------------------------------------------------

export function startQuiz({ categorySlug, mode, questionCount }) {
  return request("/api/quiz/start", {
    method: "POST",
    body: JSON.stringify({
      category_slug: categorySlug ?? null,
      mode,
      question_count: questionCount,
    }),
  });
}

export function fetchQuiz(token) {
  return request(`/api/quiz/${token}`);
}

export function submitAnswer(token, { position, choiceId }) {
  return request(`/api/quiz/${token}/answer`, {
    method: "POST",
    body: JSON.stringify({ position, choice_id: choiceId }),
  });
}

export function fetchResults(token) {
  return request(`/api/quiz/${token}/results`);
}

// --- account ---------------------------------------------------------------

function post(path, body) {
  return request(path, { method: "POST", body: JSON.stringify(body) });
}

/** Create an account; a verification code is emailed. */
export function register({ name, email, password }) {
  return post("/api/auth/register", { name, email, password });
}

/** Redeem a verification email: `{ email, code }` or `{ token }` from the link. */
export function verifyEmail({ email, code, token }) {
  return post("/api/auth/verify", { email: email ?? null, code: code ?? null, token: token ?? null });
}

export function resendVerification(email) {
  return post("/api/auth/resend", { email });
}

export function login({ email, password }) {
  return post("/api/auth/login", { email, password });
}

export function forgotPassword(email) {
  return post("/api/auth/forgot", { email });
}

/** Set a new password with `{ email, code }` or `{ token }` from the email. */
export function resetPassword({ email, code, token, password }) {
  return post("/api/auth/reset", {
    email: email ?? null, code: code ?? null, token: token ?? null, password,
  });
}

/** Confirm a stored token is still good, or find out that it is not. */
export function fetchMe() {
  return request("/api/auth/me");
}

export function fetchMyList() {
  return request("/api/me/list");
}

export function saveItem(slug) {
  return request(`/api/me/list/${encodeURIComponent(slug)}`, { method: "PUT" });
}

export function unsaveItem(slug) {
  return request(`/api/me/list/${encodeURIComponent(slug)}`, { method: "DELETE" });
}

/** Hand the server a list that was kept in this browser before signing in. */
export function importList(slugs) {
  return request("/api/me/list/import", {
    method: "POST",
    body: JSON.stringify({ slugs }),
  });
}

// --- progress --------------------------------------------------------------

export function fetchProgress() {
  return request("/api/me/progress");
}

/** Send the browser's copy; the server merges and returns the result. */
export function pushProgress(data) {
  return request("/api/me/progress", { method: "PUT", body: JSON.stringify({ data }) });
}
