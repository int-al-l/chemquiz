import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import {
  fetchCategories,
  fetchCategory,
  fetchItems,
  fetchProgress,
  pushProgress,
} from "../api/client";
import { useAuth } from "../auth/context";
import { useLang } from "../i18n";
import { ProgressContext } from "./context";
import * as engine from "./engine";
import { isEmptyProgress, mergeProgress, normalise } from "./merge";

/**
 * Learning progress for the whole app: XP, levels, card mastery, streaks and
 * badges, plus the catalogue of decks they are measured against.
 *
 * Signed out, progress lives in this browser. Signed in, it lives on the
 * account; on sign-in the browser's guest progress is merged into it (the
 * same way "My list" is adopted), so nothing earned before making an account
 * is lost.
 */

const GUEST_KEY = "chemquiz.progress.guest.v1";
const userKey = (email) => `chemquiz.progress.user.v1.${email}`;

function readDoc(key) {
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? normalise(JSON.parse(raw)) : engine.emptyProgress();
  } catch {
    return engine.emptyProgress();
  }
}

function writeDoc(key, doc) {
  try {
    window.localStorage.setItem(key, JSON.stringify(doc));
  } catch {
    // Storage blocked: progress lasts this visit (and, signed in, the server has it).
  }
}

function removeDoc(key) {
  try {
    window.localStorage.removeItem(key);
  } catch {
    // ignore
  }
}

/** Every deck (leaf category) with its card slugs, and every item. */
async function loadCatalog() {
  const [items, roots] = await Promise.all([fetchItems(), fetchCategories()]);
  const details = await Promise.all(
    roots.map((root) => (root.child_count > 0 ? fetchCategory(root.slug) : Promise.resolve(null))),
  );

  const decks = [];
  roots.forEach((root, i) => {
    const children = details[i]?.children ?? [];
    const leaves = children.length ? children : [root];
    for (const leaf of leaves) {
      decks.push({
        slug: leaf.slug,
        name: leaf.name,
        description: leaf.description,
        image_url: leaf.image_url,
        group: children.length ? root.name : null,
        cards: [],
      });
    }
  });

  const bySlug = Object.fromEntries(decks.map((d) => [d.slug, d]));
  for (const item of items) {
    bySlug[item.category_slug]?.cards.push(item.slug);
  }
  return { items, decks: decks.filter((d) => d.cards.length) };
}

let toastId = 0;

export function ProgressProvider({ children }) {
  const { user } = useAuth();
  const email = user?.email ?? null;
  // A different person means a different document: start the store afresh.
  return (
    <ProgressStore key={email ?? "guest"} email={email}>
      {children}
    </ProgressStore>
  );
}

function ProgressStore({ email, children }) {
  const storageKey = email ? userKey(email) : GUEST_KEY;

  const [doc, setDocState] = useState(() => readDoc(storageKey));
  const docRef = useRef(doc);
  const keyRef = useRef(storageKey);
  const [toasts, setToasts] = useState([]);
  const [catalog, setCatalog] = useState(null);
  const pushTimer = useRef(null);

  const setDoc = useCallback((next) => {
    docRef.current = next;
    setDocState(next);
    writeDoc(keyRef.current, next);
  }, []);

  // --- catalogue ----------------------------------------------------------
  // Deck and card names come in the interface language, so a switch reloads
  // them; the progress itself is keyed by slug and does not change.
  const { lang } = useLang();
  const reloadCatalog = useCallback(() => {
    loadCatalog()
      .then(setCatalog)
      .catch(() => setCatalog((c) => c ?? { items: [], decks: [], failed: true }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang]);
  useEffect(() => reloadCatalog(), [reloadCatalog]);

  // --- signed in: fetch the account's copy and merge ------------------------
  const [syncing, setSyncing] = useState(Boolean(email));
  useEffect(() => {
    if (!email) return undefined;
    let active = true;

    const guest = readDoc(GUEST_KEY);
    const adopt = !isEmptyProgress(guest);

    fetchProgress()
      .then(({ data }) => {
        if (!active) return null;
        let merged = mergeProgress(data, docRef.current);
        if (adopt) merged = mergeProgress(merged, guest);
        setDoc(merged);
        return pushProgress(merged).then(() => {
          if (adopt) removeDoc(GUEST_KEY);
        });
      })
      .catch(() => {
        // Offline or the server is down: keep the local copy, push later.
      })
      .finally(() => active && setSyncing(false));

    return () => {
      active = false;
    };
  }, [email, setDoc]);

  // --- pushing changes to the account --------------------------------------
  const schedulePush = useCallback(() => {
    if (!email) return;
    window.clearTimeout(pushTimer.current);
    pushTimer.current = window.setTimeout(() => {
      const sent = docRef.current;
      pushProgress(sent)
        .then(({ data }) => {
          // Anything recorded while the request was in flight is kept.
          setDoc(mergeProgress(data, docRef.current));
        })
        .catch(() => {});
    }, 1200);
  }, [email, setDoc]);

  useEffect(() => () => window.clearTimeout(pushTimer.current), []);

  // --- toasts --------------------------------------------------------------
  const dismissToast = useCallback((id) => {
    setToasts((list) => list.filter((t) => t.id !== id));
  }, []);

  const xpToast = useRef(null); // { id, amount, timer }

  const showNotes = useCallback(
    (notes) => {
      if (!notes.length) return;
      const others = [];
      for (const note of notes) {
        if (note.type !== "xp") {
          others.push({ ...note, id: ++toastId });
          continue;
        }
        // XP pops arriving in quick succession add up in one pop.
        const live = xpToast.current;
        const amount = (live?.amount ?? 0) + note.amount;
        const id = live?.id ?? ++toastId;
        window.clearTimeout(live?.timer);
        const timer = window.setTimeout(() => {
          xpToast.current = null;
          dismissToast(id);
        }, 1400);
        xpToast.current = { id, amount, timer };
        setToasts((list) => {
          const rest = list.filter((t) => t.id !== id);
          return [{ type: "xp", amount, id, bump: Date.now() }, ...rest].slice(0, 5);
        });
      }
      if (others.length) {
        setToasts((list) => [...list, ...others].slice(-5));
        for (const t of others) window.setTimeout(() => dismissToast(t.id), 3800);
      }
    },
    [dismissToast],
  );

  // --- recording events ------------------------------------------------------
  const decks = catalog?.decks;

  /** Apply one engine event, settle bonuses/badges, save, and toast. */
  const apply = useCallback(
    (event, { quiet = false } = {}) => {
      const before = docRef.current;
      const now = Date.now();
      const { doc: after, gained } = event(before, now);
      if (after === before) return 0;
      const settled = engine.settle(before, after, gained, decks, now);
      setDoc(settled.doc);
      schedulePush();
      showNotes(quiet ? settled.notes.filter((n) => n.type !== "xp") : settled.notes);
      return gained;
    },
    [decks, setDoc, schedulePush, showNotes],
  );

  const actions = useMemo(
    () => ({
      lookAt: (slug) => apply((d, now) => engine.lookAt(d, slug, now)),
      studyAnswer: (slug, known) => apply((d, now) => engine.studyAnswer(d, slug, known, now)),
      roundFinished: () => apply((d, now) => engine.roundFinished(d, now)),
      quizAnswer: (slug, correct, combo) =>
        apply((d, now) => engine.quizAnswer(d, slug, correct, combo, now)),
      quizFinished: (score) => apply((d, now) => engine.quizFinished(d, score, now)),
      setGoal: (goal) =>
        apply((d, now) => ({ doc: { ...d, goal, updated: now }, gained: 0 })),
    }),
    [apply],
  );

  const value = useMemo(() => {
    const xp = engine.totalXp(doc);
    return {
      doc,
      xp,
      level: engine.levelInfo(xp),
      streak: engine.streak(doc),
      today: engine.todayXp(doc),
      goal: doc.goal ?? 50,
      catalog,
      reloadCatalog,
      syncing,
      toasts,
      dismissToast,
      ...actions,
    };
  }, [doc, catalog, reloadCatalog, syncing, toasts, dismissToast, actions]);

  return <ProgressContext.Provider value={value}>{children}</ProgressContext.Provider>;
}
