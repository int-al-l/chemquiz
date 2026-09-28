import { useCallback, useEffect, useRef, useState } from "react";

/**
 * Horizontal swipe with a finger, a mouse or a pen, plus tap detection.
 *
 * Returns the current drag offset (for the card to follow the finger), a
 * `leaving` direction while the card flies off, and pointer handlers to spread
 * onto the element. A gesture that starts on a button is left to the button.
 *
 *   onSwipe(dir)   dir is "left" or "right"; return false to refuse (the card
 *                  springs back, e.g. at the end of a deck)
 *   onTap()        a press that barely moved
 *
 * Tuned to be forgiving on phones:
 *  - a swipe counts after a short drag (about a sixth of the card, at most
 *    60 px) or after a quick flick of only ~20 px;
 *  - flick speed is measured over the last 100 ms, so a slow start followed
 *    by a flick still counts;
 *  - the gesture is claimed as soon as it leans sideways (up to ~60 degrees
 *    from horizontal), and the element should have `touch-action: none` so the
 *    browser never takes it over as a scroll;
 *  - a new swipe may start while the previous card is still flying away.
 */

const TAP_SLOP = 10; // px a tap may wander
const CLAIM = 5; // px of sideways travel before the drag is ours
const FLICK_SPEED = 0.18; // px per ms
const FLICK_MIN = 20; // px
const FLY_MS = 160;

export function useSwipe({ onSwipe, onTap, disabled = false }) {
  const start = useRef(null);
  const trail = useRef([]); // recent { x, t } samples for the flick speed
  const width = useRef(360);
  const pending = useRef(null); // { timer, after } of a card still flying off
  const [dx, setDx] = useState(0);
  const [dragging, setDragging] = useState(false);
  const [leaving, setLeaving] = useState(null);

  // Finish a fly-off at once, so the next gesture starts from the next card.
  const settle = useCallback(() => {
    const p = pending.current;
    if (!p) return;
    window.clearTimeout(p.timer);
    pending.current = null;
    p.after?.();
    setLeaving(null);
    setDx(0);
  }, []);

  useEffect(() => () => window.clearTimeout(pending.current?.timer), []);

  const reset = useCallback(() => {
    start.current = null;
    trail.current = [];
    setDragging(false);
    setDx(0);
  }, []);

  const onPointerDown = useCallback(
    (event) => {
      if (disabled) return;
      if (event.pointerType === "mouse" && event.button !== 0) return;
      if (event.target.closest("button, a, input, [data-no-swipe]")) return;
      settle();
      width.current = event.currentTarget.getBoundingClientRect().width || 360;
      const now = performance.now();
      start.current = { x: event.clientX, y: event.clientY, t: now, id: event.pointerId, captured: false };
      trail.current = [{ x: event.clientX, t: now }];
      setDragging(true);
    },
    [disabled, settle],
  );

  const onPointerMove = useCallback((event) => {
    const s = start.current;
    if (!s || s.id !== event.pointerId) return;
    const moveX = event.clientX - s.x;
    const moveY = event.clientY - s.y;
    const now = performance.now();
    trail.current.push({ x: event.clientX, t: now });
    while (trail.current.length > 2 && now - trail.current[0].t > 100) trail.current.shift();

    if (!s.captured && Math.abs(moveX) > CLAIM && Math.abs(moveX) > Math.abs(moveY) * 0.55) {
      s.captured = true;
      try {
        event.currentTarget.setPointerCapture?.(event.pointerId);
      } catch {
        // Some browsers refuse capture for synthetic events; dragging still works.
      }
    }
    if (s.captured) setDx(moveX);
  }, []);

  const finish = useCallback(
    (event, cancelled = false) => {
      const s = start.current;
      if (!s || s.id !== event.pointerId) return;
      const moveX = event.clientX - s.x;
      const moveY = event.clientY - s.y;

      if (!cancelled && !s.captured && Math.hypot(moveX, moveY) < TAP_SLOP) {
        reset();
        onTap?.();
        return;
      }

      const first = trail.current[0];
      const last = { x: event.clientX, t: performance.now() };
      const speed = first ? Math.abs(last.x - first.x) / Math.max(16, last.t - first.t) : 0;
      const distance = Math.min(60, width.current / 6);
      const fling =
        Math.abs(moveX) > distance || (speed > FLICK_SPEED && Math.abs(moveX) > FLICK_MIN);

      // A swipe that began mostly downward but ended well to the side still counts.
      const lateSideways = !s.captured && Math.abs(moveX) > distance && Math.abs(moveX) > Math.abs(moveY) * 0.4;

      if ((s.captured || lateSideways) && fling && !(cancelled && Math.abs(moveX) < distance)) {
        const dir = moveX < 0 ? "left" : "right";
        start.current = null;
        trail.current = [];
        setDragging(false);
        if (onSwipe?.(dir) === false) setDx(0);
        return;
      }
      reset();
    },
    [onSwipe, onTap, reset],
  );

  /** Fly the card off in `dir`, then call `after` and bring the next one in. */
  const flyOut = useCallback(
    (dir, after) => {
      settle();
      try {
        navigator.vibrate?.(8);
      } catch {
        // No vibration here; nothing to do.
      }
      setLeaving(dir);
      const timer = window.setTimeout(() => {
        pending.current = null;
        after?.();
        setLeaving(null);
        setDx(0);
      }, FLY_MS);
      pending.current = { timer, after };
    },
    [settle],
  );

  return {
    dx,
    dragging,
    leaving,
    flyOut,
    handlers: {
      onPointerDown,
      onPointerMove,
      onPointerUp: (e) => finish(e),
      onPointerCancel: (e) => finish(e, true),
    },
  };
}
