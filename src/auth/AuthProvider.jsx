import { useCallback, useEffect, useState } from "react";

import { fetchMe, importList, setAuthToken } from "../api/client";
import { clearLocal, readLocal } from "../saved/localList";
import { AuthContext } from "./context";

/**
 * Who is signed in, for the whole app.
 *
 * The session token lives in localStorage so a refresh does not sign anyone
 * out, and is handed to the API client on every change. Getting a token takes
 * a password (or a code emailed to the address); the pages that do that call
 * `completeSignIn` with the account the server returned.
 */

const STORAGE_KEY = "chemquiz.auth.v1";

function readStored() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : null;
    return parsed && typeof parsed.token === "string" ? parsed : null;
  } catch {
    return null;
  }
}

function writeStored(user) {
  try {
    if (user) window.localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
    else window.localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Private window or blocked storage: the sign-in lasts this visit only.
  }
}

export function AuthProvider({ children }) {
  // Read synchronously so the first render already knows who is signed in, and
  // no screen flashes its signed-out state before settling.
  const [user, setUser] = useState(() => {
    const stored = readStored();
    setAuthToken(stored?.token ?? null);
    return stored;
  });

  // A stored token can be stale -- the database was reset, or the account
  // removed. Confirm it once on load and sign out quietly if it is no longer
  // good, rather than letting every later request fail with a 401.
  useEffect(() => {
    if (!readStored()) return undefined;
    let active = true;

    fetchMe()
      .then((fresh) => {
        if (!active) return;
        setUser(fresh);
        writeStored(fresh);
      })
      .catch((error) => {
        if (!active || error?.status !== 401) return;
        // Any other failure is the backend being down, which is not a reason
        // to throw away a valid sign-in.
        setAuthToken(null);
        setUser(null);
        writeStored(null);
      });

    return () => {
      active = false;
    };
    // Runs once on mount by design: the stored token is read inside.
  }, []);

  const completeSignIn = useCallback(async (fresh) => {
    setAuthToken(fresh.token);

    // Carry over anything saved in this browser before signing in. It adds
    // rather than replaces, so signing in on a second device cannot wipe the
    // account's existing list.
    const adopt = readLocal();
    if (adopt.length) {
      try {
        await importList(adopt);
        clearLocal();
      } catch {
        // Not worth failing the sign-in over.
      }
    }

    setUser(fresh);
    writeStored(fresh);
    return fresh;
  }, []);

  const signOut = useCallback(() => {
    setAuthToken(null);
    setUser(null);
    writeStored(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, completeSignIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}
