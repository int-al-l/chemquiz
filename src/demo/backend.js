/**
 * The ChemQuiz API, running inside the browser -- for the demo build only.
 *
 * `npm run build:demo` sets VITE_DEMO, and api/client.js then sends every
 * request here instead of over the network. The rules mirror the FastAPI
 * backend (quiz building, grading, accounts, progress merging); state lives in
 * this browser's localStorage, and emails are not sent -- the code is shown on
 * screen instead (see `demoInbox`).
 */
import DATA from "./data.json";
import { mergeProgress, normalise } from "../progress/merge";

const KEY = "chemquiz.demo.db.v1";
const CHOICES = 4;

// --- storage -------------------------------------------------------------------

let memory = null;

function db() {
  if (memory) return memory;
  try {
    memory = JSON.parse(window.localStorage.getItem(KEY)) || null;
  } catch {
    memory = null;
  }
  memory = memory || { users: {}, sessions: {}, codes: {}, inbox: {} };
  return memory;
}

function save() {
  try {
    window.localStorage.setItem(KEY, JSON.stringify(memory));
  } catch {
    // Storage blocked: the demo still works for this visit.
  }
}

class HttpError extends Error {
  constructor(status, detail) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}
const fail = (status, detail) => {
  throw new HttpError(status, detail);
};

// --- content ---------------------------------------------------------------------

const cats = DATA.categories;
const items = DATA.items;
const itemBySlug = Object.fromEntries(items.map((i) => [i.slug, i]));
const itemById = Object.fromEntries(items.map((i) => [i.id, i]));

const children = (slug) => cats.filter((c) => c.parent === slug).sort((a, b) => a.order - b.order);
const subtree = (slug) => [slug, ...children(slug).flatMap((c) => subtree(c.slug))];
const itemsUnder = (slug) => {
  if (!slug) return items;
  const set = new Set(subtree(slug));
  return items.filter((i) => set.has(i.category));
};

function itemOut(i) {
  return {
    id: i.id,
    slug: i.slug,
    name: i.name,
    catalog_name: i.catalog_name,
    description: i.description,
    image_url: i.photos[0] ?? null,
    photo_urls: i.photos,
    photo_count: i.photos.length,
    category_slug: i.category,
  };
}

function catOut(c) {
  return {
    id: cats.indexOf(c) + 1,
    slug: c.slug,
    name: c.name,
    description: c.description,
    image_url: c.image,
    child_count: children(c.slug).length,
    item_count: items.filter((i) => i.category === c.slug).length,
    quizzable_count: itemsUnder(c.slug).length,
  };
}

function findCat(slug) {
  return cats.find((c) => c.slug === slug) || fail(404, `No category '${slug}'`);
}

// --- quiz ------------------------------------------------------------------------

const token = () =>
  Array.from(crypto.getRandomValues(new Uint8Array(24)), (b) => b.toString(36).padStart(2, "0")).join("");

function shuffle(list) {
  const a = [...list];
  for (let i = a.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
const pick = (list) => list[Math.floor(Math.random() * list.length)];

function distractors(answer, pool) {
  const siblings = shuffle(pool.filter((i) => i.category === answer.category && i.id !== answer.id));
  let out = siblings.slice(0, CHOICES - 1);
  const taken = new Set([answer.id, ...out.map((i) => i.id)]);
  for (const extra of [shuffle(pool), shuffle(items)]) {
    for (const i of extra) {
      if (out.length >= CHOICES - 1) break;
      if (!taken.has(i.id)) {
        out.push(i);
        taken.add(i.id);
      }
    }
  }
  return out;
}

function startQuiz({ category_slug, mode, question_count }) {
  if (!["choice", "inverted"].includes(mode)) fail(422, "Unknown quiz mode");
  const n = Number(question_count);
  if (!(n >= 1 && n <= 500)) fail(422, "Question count must be between 1 and 500");
  const cat = category_slug ? findCat(category_slug) : null;
  const pool = itemsUnder(cat?.slug);
  if (!pool.length) fail(409, "no items available for this category");

  const asked = shuffle(pool).slice(0, n);
  const questions = asked.map((item, idx) => {
    const options = shuffle([item, ...distractors(item, pool)]);
    const photo = pick(item.photos);
    return {
      position: idx + 1,
      item: item.id,
      photo,
      choices: options.map((o) => o.id),
      choicePhotos: mode === "inverted" ? options.map((o) => (o.id === item.id ? photo : pick(o.photos))) : [],
      given: null,
      givenName: null,
      correct: false,
      answered: false,
    };
  });
  const s = {
    token: token(),
    mode,
    category_slug: cat?.slug ?? null,
    category_name: cat?.name ?? null,
    created_at: new Date().toISOString(),
    completed_at: null,
    questions,
  };
  const store = db();
  // Keep only the last 20 quizzes.
  const tokens = Object.keys(store.sessions);
  if (tokens.length > 20) delete store.sessions[tokens[0]];
  store.sessions[s.token] = s;
  save();
  return sessionOut(s);
}

function getSession(t) {
  return db().sessions[t] || fail(404, "Quiz not found or expired");
}

const counts = (s) => ({
  question_count: s.questions.length,
  answered_count: s.questions.filter((q) => q.answered).length,
  correct_count: s.questions.filter((q) => q.correct).length,
  is_complete: s.questions.every((q) => q.answered),
});

function questionOut(s, q) {
  if (s.mode === "inverted") {
    return {
      position: q.position,
      image_url: null,
      prompt: itemById[q.item].name,
      choices: q.choices.map((id, i) => ({ id, image_url: q.choicePhotos[i] })),
      answered: q.answered,
    };
  }
  return {
    position: q.position,
    image_url: q.photo,
    prompt: null,
    choices: q.choices.map((id) => ({ id, name: itemById[id].name })),
    answered: q.answered,
  };
}

function sessionOut(s) {
  return {
    token: s.token,
    mode: s.mode,
    category_slug: s.category_slug,
    category_name: s.category_name,
    ...counts(s),
    questions: s.questions.map((q) => questionOut(s, q)),
  };
}

function answer(t, { position, choice_id }) {
  const s = getSession(t);
  const q = s.questions.find((x) => x.position === position) || fail(404, `Quiz has no question ${position}`);
  if (q.answered) fail(409, "Question already answered");
  if (!q.choices.includes(choice_id)) fail(422, "choice_id is not one of this question's options");
  q.answered = true;
  q.given = choice_id;
  q.givenName = itemById[choice_id].name;
  q.correct = choice_id === q.item;
  const c = counts(s);
  if (c.is_complete) s.completed_at = new Date().toISOString();
  save();
  return {
    position,
    is_correct: q.correct,
    correct_item: itemOut(itemById[q.item]),
    correct_choice_id: q.item,
    given_choice_id: choice_id,
    given_answer: q.givenName,
    answered_count: c.answered_count,
    correct_count: c.correct_count,
    is_complete: c.is_complete,
  };
}

function results(t) {
  const s = getSession(t);
  return {
    token: s.token,
    mode: s.mode,
    category_slug: s.category_slug,
    category_name: s.category_name,
    ...counts(s),
    created_at: s.created_at,
    completed_at: s.completed_at,
    questions: s.questions.map((q) => ({
      position: q.position,
      item: q.answered ? itemOut(itemById[q.item]) : null,
      image_url: q.photo,
      given_answer: q.givenName,
      is_correct: q.correct,
      answered: q.answered,
    })),
  };
}

// --- accounts ----------------------------------------------------------------------

const EMAIL = /^[^@\s]+@[^@\s.]+(\.[^@\s.]+)+$/;

function checkEmail(value) {
  const email = String(value || "").trim().toLowerCase();
  if (!EMAIL.test(email)) fail(422, "That does not look like an email address.");
  return email;
}

function checkPassword(p) {
  if (!p || p.length < 8) fail(422, "Use at least 8 characters for the password.");
  if (/^\d+$/.test(p) || /^[a-z]+$/i.test(p)) fail(422, "Mix letters with numbers or symbols in the password.");
}

async function hash(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(`chemquiz-demo:${text}`));
  return Array.from(new Uint8Array(buf), (b) => b.toString(16).padStart(2, "0")).join("");
}

function sendCode(user, purpose) {
  const code = String(Math.floor(Math.random() * 1e6)).padStart(6, "0");
  const link = token();
  const store = db();
  store.codes[`${purpose}:${user.email}`] = {
    code,
    link,
    attempts: 0,
    expires: Date.now() + 15 * 60 * 1000,
  };
  store.inbox[user.email] = { purpose, code, at: Date.now() };
  save();
}

function redeem({ email, code, token: link }, purpose) {
  const store = db();
  let key;
  if (link) {
    key = Object.keys(store.codes).find((k) => k.startsWith(`${purpose}:`) && store.codes[k].link === link);
    if (!key) fail(400, "That link is no longer valid. Ask for a new one.");
  } else {
    if (!email || !code) fail(422, "Enter the code from the email.");
    key = `${purpose}:${String(email).trim().toLowerCase()}`;
    const row = store.codes[key];
    if (!row || row.expires < Date.now()) fail(400, "That code is wrong or has expired.");
    if (row.attempts >= 5) fail(429, "Too many wrong codes. Ask for a new email.");
    if (String(code).replace(/\D/g, "") !== row.code) {
      row.attempts += 1;
      save();
      fail(400, "That code is wrong or has expired.");
    }
  }
  const userEmail = key.split(":").slice(1).join(":");
  delete store.codes[key];
  delete store.inbox[userEmail];
  const user = store.users[userEmail];
  user.verified = true;
  save();
  return user;
}

const signedIn = (u) => ({ token: u.token, email: u.email, name: u.name, saved_count: u.saved.length });

function currentUser(headers) {
  const auth = headers?.Authorization || headers?.authorization || "";
  const t = auth.replace(/^Bearer\s+/i, "");
  const user = Object.values(db().users).find((u) => u.token === t && u.verified);
  return user || fail(401, t ? "That sign-in has expired." : "Sign in to use your list.");
}

async function register({ name, email, password }) {
  email = checkEmail(email);
  if (!String(name || "").trim()) fail(422, "Please enter a name.");
  checkPassword(password);
  const store = db();
  let user = store.users[email];
  if (user?.verified) fail(409, "There is already an account with this email. Sign in instead.");
  user = user || { email, token: token(), saved: [], progress: {} };
  user.name = name.trim();
  user.password = await hash(password);
  user.verified = false;
  store.users[email] = user;
  sendCode(user, "verify");
  return { status: "code_sent", email, purpose: "verify" };
}

async function login({ email, password }) {
  email = checkEmail(email);
  const user = db().users[email];
  if (!user || user.password !== (await hash(password))) fail(401, "Wrong email or password.");
  if (!user.verified) {
    sendCode(user, "verify");
    fail(403, "Please verify your email first. We have sent you a new code.");
  }
  return signedIn(user);
}

async function reset(body) {
  checkPassword(body.password);
  const user = redeem(body, "reset");
  user.password = await hash(body.password);
  user.token = token();
  save();
  return signedIn(user);
}

// --- routing -----------------------------------------------------------------------

export async function demoRequest(path, options = {}) {
  const method = (options.method || "GET").toUpperCase();
  const body = options.body ? JSON.parse(options.body) : {};
  const url = new URL(path, "http://demo.local");
  const p = url.pathname;
  const q = url.searchParams;
  const headers = options.headers;
  let m;

  // A beat of latency, so loading states behave as they do for real.
  await new Promise((r) => setTimeout(r, 60));

  try {
    if (p === "/api/categories" && method === "GET") {
      const parent = q.get("parent");
      if (parent) findCat(parent);
      return (parent ? children(parent) : cats.filter((c) => !c.parent)).map(catOut);
    }
    if ((m = p.match(/^\/api\/categories\/([^/]+)$/))) {
      const c = findCat(decodeURIComponent(m[1]));
      const parent = c.parent ? cats.find((x) => x.slug === c.parent) : null;
      return {
        ...catOut(c),
        parent: parent ? catOut(parent) : null,
        children: children(c.slug).map(catOut),
        items: items.filter((i) => i.category === c.slug).map(itemOut),
      };
    }
    if (p === "/api/items") {
      const cat = q.get("category");
      if (cat) findCat(cat);
      return itemsUnder(cat).map(itemOut);
    }
    if ((m = p.match(/^\/api\/items\/([^/]+)$/))) {
      return itemOut(itemBySlug[decodeURIComponent(m[1])] || fail(404, "No such item"));
    }

    if (p === "/api/quiz/start" && method === "POST") return startQuiz(body);
    if ((m = p.match(/^\/api\/quiz\/([^/]+)\/answer$/))) return answer(m[1], body);
    if ((m = p.match(/^\/api\/quiz\/([^/]+)\/results$/))) return results(m[1]);
    if ((m = p.match(/^\/api\/quiz\/([^/]+)$/))) {
      if (method === "DELETE") {
        delete db().sessions[m[1]];
        save();
        return null;
      }
      return sessionOut(getSession(m[1]));
    }

    if (p === "/api/auth/register") return await register(body);
    if (p === "/api/auth/verify") return signedIn(redeem(body, "verify"));
    if (p === "/api/auth/resend") {
      const email = checkEmail(body.email);
      const u = db().users[email];
      if (u && !u.verified) sendCode(u, "verify");
      return { status: "code_sent", email, purpose: "verify" };
    }
    if (p === "/api/auth/login") return await login(body);
    if (p === "/api/auth/forgot") {
      const email = checkEmail(body.email);
      const u = db().users[email];
      if (u) sendCode(u, "reset");
      return { status: "code_sent", email, purpose: "reset" };
    }
    if (p === "/api/auth/reset") return await reset(body);
    if (p === "/api/auth/me") return signedIn(currentUser(headers));

    if (p === "/api/me/progress") {
      const user = currentUser(headers);
      if (method === "PUT") {
        user.progress = mergeProgress(user.progress, body.data);
        save();
      }
      return { data: normalise(user.progress) };
    }
    if (p === "/api/me/list/import") {
      const user = currentUser(headers);
      for (const slug of body.slugs || []) {
        if (itemBySlug[slug] && !user.saved.includes(slug)) user.saved.unshift(slug);
      }
      save();
      return user.saved.map((s) => itemOut(itemBySlug[s]));
    }
    if (p === "/api/me/list") {
      const user = currentUser(headers);
      return user.saved.filter((s) => itemBySlug[s]).map((s) => itemOut(itemBySlug[s]));
    }
    if ((m = p.match(/^\/api\/me\/list\/([^/]+)$/))) {
      const user = currentUser(headers);
      const slug = decodeURIComponent(m[1]);
      if (!itemBySlug[slug]) fail(404, `No item '${slug}'`);
      user.saved = user.saved.filter((s) => s !== slug);
      if (method === "PUT") user.saved.unshift(slug);
      save();
      return { slug, saved: method === "PUT" };
    }

    fail(404, "Not found");
  } catch (err) {
    if (err instanceof HttpError) return { __error: err };
    throw err;
  }
  return null;
}

/** The code "emailed" to this address, if one is waiting -- shown on screen in the demo. */
export function demoInbox(email) {
  const e = String(email || "").trim().toLowerCase();
  return db().inbox[e] ?? null;
}
