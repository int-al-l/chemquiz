/**
 * State and timing shared by the board (host) and the phones (players) in a
 * live game. The components that draw them are in components.jsx.
 */
import { useEffect, useRef, useState } from "react";

/**
 * Each option has a colour *and* a shape, so it can be called out across a
 * classroom ("the blue diamond") and told apart by anyone who cannot rely on
 * colour alone.
 */
export const OPTION_STYLES = [
  { key: "red", label: "Triangle" },
  { key: "blue", label: "Diamond" },
  { key: "amber", label: "Circle" },
  { key: "green", label: "Square" },
];

// --- secrets kept on this device --------------------------------------------------
//
// localStorage rather than sessionStorage: a phone that locks mid-lesson, or a
// board whose tab is refreshed, should drop straight back into the game.

const HOST_KEY = (pin) => `chemquiz.live.host.${pin}`;
const PLAYER_KEY = (pin) => `chemquiz.live.player.${pin}`;

function read(key) {
  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;
  }
}

function write(key, value) {
  try {
    if (value == null) window.localStorage.removeItem(key);
    else window.localStorage.setItem(key, value);
  } catch {
    /* private mode: the game still works until the tab closes */
  }
}

export const hostToken = (pin) => read(HOST_KEY(pin));
export const saveHostToken = (pin, token) => write(HOST_KEY(pin), token);
export const playerToken = (pin) => read(PLAYER_KEY(pin));
export const savePlayerToken = (pin, token) => write(PLAYER_KEY(pin), token);

// --- keeping up with the server ---------------------------------------------------

/** Errors that mean "stop asking": gone, not yours, or removed. */
const FINAL = new Set([403, 404, 410]);

/**
 * Ask the server for the game's state every `interval` ms.
 *
 * Polling rather than a socket: it survives school Wi-Fi, proxies and phones
 * that sleep, and a phone that wakes up simply asks again. At one request a
 * second per phone, a class of thirty is nothing for the server.
 *
 * Also tracks how far this device's clock is from the server's, so countdowns
 * agree between the board and every phone.
 */
export function useLivePoll(fetcher, interval, enabled = true) {
  const [state, setState] = useState(null);
  const [error, setError] = useState(null);
  const offset = useRef(0);
  const fetcherRef = useRef(fetcher);

  useEffect(() => {
    fetcherRef.current = fetcher;
  });

  function take(snapshot) {
    if (snapshot && typeof snapshot.now === "number") {
      offset.current = snapshot.now * 1000 - Date.now();
    }
    setState(snapshot);
    setError(null);
  }

  useEffect(() => {
    if (!enabled) return undefined;
    let alive = true;
    let timer = null;

    async function loop() {
      try {
        const snapshot = await fetcherRef.current();
        if (!alive) return;
        take(snapshot);
      } catch (err) {
        if (!alive) return;
        setError(err);
        if (FINAL.has(err.status)) {
          return;
        }
      }
      timer = window.setTimeout(loop, interval);
    }

    loop();
    return () => {
      alive = false;
      window.clearTimeout(timer);
    };
  }, [interval, enabled]);

  return { state, error, apply: take, offset };
}

/** The server's current time in seconds, redrawn a few times a second. */
export function useServerNow(offset, running = true) {
  const [now, setNow] = useState(() => (Date.now() + offset.current) / 1000);
  useEffect(() => {
    if (!running) return undefined;
    const id = window.setInterval(() => setNow((Date.now() + offset.current) / 1000), 200);
    return () => window.clearInterval(id);
  }, [offset, running]);
  return now;
}

/**
 * Where the clock stands in a question: reading time before answers open,
 * then the answering time counting down.
 */
export function questionClock(state, now) {
  if (!state || state.phase !== "question" || !state.starts_at) {
    return { reading: false, left: 0, fraction: 0 };
  }
  if (now < state.starts_at) {
    return { reading: true, left: Math.ceil(state.starts_at - now), fraction: 1 };
  }
  const left = Math.max(0, state.deadline - now);
  return { reading: false, left: Math.ceil(left), fraction: left / state.time_limit };
}

export function ordinal(n) {
  const s = ["th", "st", "nd", "rd"];
  const v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
}
