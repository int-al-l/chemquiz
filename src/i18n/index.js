/**
 * The interface language: which one, and the texts in it.
 *
 * The choice is kept on the device (localStorage) and, until a person makes
 * one, follows the browser. The API client is told too, so the server sends
 * card names and errors in the same language.
 */
import { Fragment, createContext, createElement, useCallback, useContext } from "react";

import en from "./en";
import ru from "./ru";

export const LANGUAGES = ["en", "ru"];
const DICTIONARIES = { en, ru };
const STORAGE_KEY = "chemquiz.lang";

export function detectLanguage(stored, browser) {
  if (LANGUAGES.includes(stored)) return stored;
  return (browser || "").toLowerCase().startsWith("ru") ? "ru" : "en";
}

export function readStored() {
  try {
    return window.localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

export function writeStored(lang) {
  try {
    window.localStorage.setItem(STORAGE_KEY, lang);
  } catch {
    /* private mode: the choice lasts until the tab closes */
  }
}

export function translate(lang, key, values = {}) {
  const own = DICTIONARIES[lang]?.[key];
  const entry = own ?? en[key];
  if (entry === undefined) return key;
  let text = entry;
  if (typeof entry === "object") {
    const form = new Intl.PluralRules(own !== undefined ? lang : "en").select(values.n ?? 0);
    text = entry[form] ?? entry.other;
  }
  return text.replace(/\{(\w+)\}/g, (match, name) => (name in values ? String(values[name]) : match));
}

/** "Lab Rookie" -> "level.lab-rookie": level titles are stored in English, translated when shown. */
export function titleKey(title) {
  return `level.${title.toLowerCase().replace(/[^a-z]+/g, "-").replace(/^-|-$/g, "")}`;
}

/**
 * Put React nodes (a link, bold text) into a translated sentence:
 * rich("Tap {link} to go", { link: <Link/> }). The whole sentence stays one key.
 */
export function rich(text, nodes) {
  return text
    .split(/\{(\w+)\}/)
    .map((part, i) => (i % 2 ? createElement(Fragment, { key: i }, nodes[part] ?? `{${part}}`) : part));
}

/**
 * A badge's title and blurb in the interface language. The engine keeps them in
 * English; a deck badge ("deck-seen:flasks") names its deck.
 */
export function badgeText(t, badge) {
  const base = badge.id.split(":")[0];
  return {
    title: t(`badge.${base}.title`, { deck: badge.deck }),
    blurb: t(`badge.${base}.blurb`, { deck: badge.deck }),
  };
}

export const LanguageContext = createContext({ lang: "en", setLang: () => {} });

export function useLang() {
  return useContext(LanguageContext);
}

export function useT() {
  const { lang } = useLang();
  return useCallback((key, values) => translate(lang, key, values), [lang]);
}
