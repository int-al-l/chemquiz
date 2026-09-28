import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { ApiError, fetchMyList, saveItem, unsaveItem } from "../api/client";
import { useAuth } from "../auth/context";
import { LOCAL_STORAGE_KEY, readLocal, writeLocal } from "./localList";
import { SavedContext } from "./context";

/** One frozen array, so "no slugs" is referentially stable between renders. */
const EMPTY = Object.freeze([]);

/**
 * "My list", wherever it happens to live.
 *
 * Signed in, the list is rows on the server and follows the person between
 * devices. Signed out, it falls back to this browser's localStorage so the
 * feature still works before anyone has an account -- and that local list is
 * what gets adopted on the next sign-in.
 *
 * Every page reads the same context, so saving on the results screen updates
 * the bookmark on Explore without a reload.
 *
 * Two things guard the server list against arriving out of order:
 *
 *  - It is *keyed* by the token it came from, so a reply that lands after a
 *    sign-out, or after someone else has signed in, is dropped rather than
 *    shown to the wrong person.
 *
 *  - It carries a *generation*, bumped on every save. A list fetched before a
 *    save describes the world before that save, so applying it would silently
 *    undo the bookmark the person just set -- which is exactly what it looked
 *    like when saving appeared not to work at all. A reply from an older
 *    generation is discarded.
 */
export function SavedProvider({ children }) {
  const { user, signOut } = useAuth();
  const key = user?.token ?? null;

  const [localSlugs, setLocalSlugs] = useState(readLocal);
  const [server, setServer] = useState(null); // { key, slugs }
  const [error, setError] = useState(null);

  // Incremented by every local change; a fetch started before the change is
  // stale by the time it returns.
  const generation = useRef(0);

  const refresh = useCallback(() => {
    if (!key) return undefined;
    const startedAt = generation.current;
    let active = true;

    fetchMyList()
      .then((items) => {
        if (!active || generation.current !== startedAt) return;
        setServer({ key, slugs: items.map((item) => item.slug) });
      })
      .catch((err) => {
        if (!active) return;
        if (err instanceof ApiError && err.status === 401) {
          // The token names nobody -- the account was removed, or the database
          // was rebuilt. Sign out so the UI stops claiming to be signed in.
          signOut();
          return;
        }
        setError(err);
      });

    return () => {
      active = false;
    };
  }, [key, signOut]);

  useEffect(() => refresh(), [refresh]);

  // Keep two tabs in step while signed out.
  useEffect(() => {
    if (key) return undefined;
    function onStorage(event) {
      if (event.key === LOCAL_STORAGE_KEY) setLocalSlugs(readLocal());
    }
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, [key]);

  const settled = !key || server?.key === key;
  // Memoised so the callbacks below keep a stable identity between renders.
  const slugs = useMemo(
    () => (key ? (server?.key === key ? server.slugs : EMPTY) : localSlugs),
    [key, server, localSlugs],
  );

  const toggle = useCallback(
    async (slug) => {
      const wasSaved = slugs.includes(slug);
      const next = wasSaved ? slugs.filter((s) => s !== slug) : [...slugs, slug];

      setError(null);

      if (!key) {
        setLocalSlugs(next);
        writeLocal(next);
        return;
      }

      // Any list already in flight predates this change.
      generation.current += 1;

      // Show it immediately: a bookmark that waits for the network feels broken.
      setServer({ key, slugs: next });

      try {
        await (wasSaved ? unsaveItem(slug) : saveItem(slug));
      } catch (err) {
        setServer({ key, slugs }); // put it back -- the change did not happen

        if (err instanceof ApiError && err.status === 401) {
          setError(
            new ApiError(
              "Your sign-in is no longer valid. Sign in again to save items.",
              401,
            ),
          );
          signOut();
          return;
        }
        setError(err);
      }
    },
    [slugs, key, signOut],
  );

  const remove = useCallback(
    (slug) => {
      if (slugs.includes(slug)) toggle(slug);
    },
    [slugs, toggle],
  );

  const has = useCallback((slug) => slugs.includes(slug), [slugs]);

  const value = useMemo(
    () => ({
      slugs,
      has,
      toggle,
      remove,
      error,
      dismissError: () => setError(null),
      loading: !settled,
      isSignedIn: Boolean(key),
    }),
    [slugs, has, toggle, remove, error, settled, key],
  );

  return <SavedContext.Provider value={value}>{children}</SavedContext.Provider>;
}
