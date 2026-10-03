import { useCallback, useEffect, useState } from "react";

/**
 * Overlays -- a bottom sheet, a photo full screen -- that the phone's Back
 * button closes, instead of leaving the page underneath (and the quiz with
 * it).
 *
 * Opening one adds an entry to the browser history: the same address, with
 * the overlay's name in the entry's state. Back takes the entry off again and
 * the overlay closes. Closing it on the page (the cross, Escape) goes back
 * too, so no stray entries are left for Back to step through. Overlays stack
 * -- a photo opened from the sheet -- and each stays open while its name is
 * in the current entry's list.
 *
 * The router keeps its own data in the same state object, so it is copied
 * along and the router sees the same location throughout.
 */

const overlays = () => window.history.state?.overlays ?? [];

/** [value, open(value = true), close()]; value is null while closed. */
export function useBackClose(name) {
  const [value, setValue] = useState(null);
  const isOpen = value !== null;

  useEffect(() => {
    if (!isOpen) return undefined;
    const onPop = () => {
      if (!overlays().includes(name)) setValue(null);
    };
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, [isOpen, name]);

  const open = useCallback(
    (next = true) => {
      if (!overlays().includes(name)) {
        window.history.pushState({ ...window.history.state, overlays: [...overlays(), name] }, "");
      }
      setValue(next);
    },
    [name],
  );

  const close = useCallback(() => {
    // Going back fires popstate, which closes it.
    if (overlays().at(-1) === name) window.history.back();
    else setValue(null);
  }, [name]);

  return [value, open, close];
}

let pending = null;

/**
 * Take every open overlay's entry off the history, then run `then` -- for a
 * step that must not race the Back, such as replacing the address. A second
 * call while the first is still going back is ignored, so pressing Next twice
 * cannot go back one entry too many.
 */
export function closeOverlaysThen(then) {
  if (pending) return;
  const n = overlays().length;
  if (!n) {
    then();
    return;
  }
  pending = then;
  const onPop = () => {
    window.removeEventListener("popstate", onPop);
    const run = pending;
    pending = null;
    run();
  };
  window.addEventListener("popstate", onPop);
  window.history.go(-n);
}
