import { useCallback, useRef, useState } from "react";

/**
 * Horizontal swipe with a finger, a mouse or a pen, plus tap detection.
 *
 * Returns the current drag offset (for the card to follow the finger), a
 * `leaving` direction while the card flies off, and pointer handlers to spread
 * onto the element. A gesture that starts on a button is left to the button.
 *
 *   onSwipe(dir)   dir is "left" or "right"; return false to refuse (the card
 *                  springs back, e.g. at the end of a deck)
 *   onTap()        a press that did not move
 */
export function useSwipe({ onSwipe, onTap, threshold = 90, disabled = false }) {
  const start = useRef(null);
  const [dx, setDx] = useState(0);
  const [dragging, setDragging] = useState(false);
  const [leaving, setLeaving] = useState(null);

  const reset = useCallback(() => {
    start.current = null;
    setDragging(false);
    setDx(0);
  }, []);

  const onPointerDown = useCallback(
    (event) => {
      if (disabled || leaving) return;
      if (event.button !== undefined && event.button !== 0) return;
      if (event.target.closest("button, a, input, [data-no-swipe]")) return;
      start.current = { x: event.clientX, y: event.clientY, t: performance.now(), id: event.pointerId };
      setDragging(true);
    },
    [disabled, leaving],
  );

  const onPointerMove = useCallback((event) => {
    const s = start.current;
    if (!s || s.id !== event.pointerId) return;
    const moveX = event.clientX - s.x;
    const moveY = event.clientY - s.y;
    if (!s.captured && Math.abs(moveX) > 6 && Math.abs(moveX) > Math.abs(moveY)) {
      s.captured = true;
      event.currentTarget.setPointerCapture?.(event.pointerId);
    }
    if (s.captured) setDx(moveX);
  }, []);

  const finish = useCallback(
    (event, cancelled = false) => {
      const s = start.current;
      if (!s || s.id !== event.pointerId) return;
      const moveX = event.clientX - s.x;
      const moveY = event.clientY - s.y;
      const elapsed = Math.max(1, performance.now() - s.t);
      const velocity = Math.abs(moveX) / elapsed;

      if (!cancelled && !s.captured && Math.abs(moveX) < 8 && Math.abs(moveY) < 8) {
        reset();
        onTap?.();
        return;
      }

      const fling = Math.abs(moveX) > threshold || (velocity > 0.6 && Math.abs(moveX) > 30);
      if (!cancelled && s.captured && fling) {
        const dir = moveX < 0 ? "left" : "right";
        start.current = null;
        setDragging(false);
        if (onSwipe?.(dir, { animate: true }) === false) {
          setDx(0);
          return;
        }
        return;
      }
      reset();
    },
    [onSwipe, onTap, reset, threshold],
  );

  /** Fly the card off in `dir`, then call `after` and bring the next one in. */
  const flyOut = useCallback((dir, after) => {
    setLeaving(dir);
    window.setTimeout(() => {
      after?.();
      setLeaving(null);
      setDx(0);
    }, 200);
  }, []);

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
