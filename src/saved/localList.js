/**
 * The saved list as kept in this browser.
 *
 * Used while nobody is signed in, and handed to the server on the next sign-in
 * so a list started before making an account is not lost.
 *
 * Every access is guarded: localStorage throws in a private window and in some
 * embedded browsers, and a bookmark feature is not worth a blank page.
 */

const STORAGE_KEY = "chemquiz.mylist.v1";

export function readLocal() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed.filter((s) => typeof s === "string") : [];
  } catch {
    return [];
  }
}

export function writeLocal(slugs) {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(slugs));
  } catch {
    // Out of quota or storage blocked: the list lasts this visit only.
  }
}

export function clearLocal() {
  writeLocal([]);
}

export const LOCAL_STORAGE_KEY = STORAGE_KEY;
