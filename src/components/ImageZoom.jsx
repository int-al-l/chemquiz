import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

import { useT } from "../i18n";
import { MAX_SCALE, MIN_SCALE, clampView, fittedSize, onPhoto, scaleAbout } from "./zoom";

const TAP_SLOP = 8; // px a tap may wander
const DOUBLE_TAP_MS = 300;
const DOUBLE_TAP_SCALE = 2.5;
const STEP = 2; // what the + and - buttons multiply the scale by

/** Sizes needed to place the photo; read fresh each time, as the window may turn. */
function measure(stage, img) {
  const rect = stage.getBoundingClientRect();
  const fit = fittedSize(img.naturalWidth, img.naturalHeight, img.clientWidth, img.clientHeight);
  return {
    left: rect.left,
    top: rect.top,
    stageW: rect.width,
    stageH: rect.height,
    photoW: fit.w,
    photoH: fit.h,
  };
}

/** A point on screen, measured from the centre of the stage. */
const fromCentre = (clientX, clientY, box) => ({
  x: clientX - box.left - box.stageW / 2,
  y: clientY - box.top - box.stageH / 2,
});

const stop = (event) => event.stopPropagation();

/**
 * A photograph on the whole screen, to look at closely: pinch, turn the wheel,
 * double-tap or use the + and - buttons to zoom, drag to look around. Closes
 * on the cross, Escape, or a tap on the dark area around the photo.
 *
 * It is drawn into <body>, so a parent that is moved or turned (the bottom
 * sheet, a flip card) cannot trap it, and the keys and pointer events it gets
 * stop there: 1-4 must not answer the quiz question behind it, nor a drag
 * swipe the study card away.
 */
function ImageZoom({ src, alt = "", onClose }) {
  const t = useT();
  const stageRef = useRef(null);
  const imgRef = useRef(null);
  const closeButtonRef = useRef(null);
  const onCloseRef = useRef(onClose);
  const pointers = useRef(new Map());
  const gesture = useRef(null);
  const lastTap = useRef(null);
  const closeOnClick = useRef(false);
  const [view, setView] = useState({ scale: 1, x: 0, y: 0 });
  const [gesturing, setGesturing] = useState(false);

  useEffect(() => {
    onCloseRef.current = onClose;
  });

  // Escape closes; every key stops here. The page behind cannot scroll, and
  // focus goes back where it was when the photo closes.
  useEffect(() => {
    const previous = document.activeElement;
    closeButtonRef.current?.focus();
    const { overflow } = document.body.style;
    document.body.style.overflow = "hidden";
    function onKey(event) {
      event.stopPropagation();
      if (event.key === "Escape") {
        event.preventDefault();
        onCloseRef.current();
      }
    }
    window.addEventListener("keydown", onKey, true);
    return () => {
      window.removeEventListener("keydown", onKey, true);
      document.body.style.overflow = overflow;
      previous?.focus?.();
    };
  }, []);

  // The wheel zooms about the pointer. Listened to directly, because React's
  // wheel handler is passive and could not keep the page from scrolling.
  useEffect(() => {
    const stage = stageRef.current;
    function onWheel(event) {
      event.preventDefault();
      const box = measure(stage, imgRef.current);
      const p = fromCentre(event.clientX, event.clientY, box);
      setView((v) => clampView(scaleAbout(v, p, v.scale * Math.exp(-event.deltaY * 0.002)), box));
    }
    stage.addEventListener("wheel", onWheel, { passive: false });
    return () => stage.removeEventListener("wheel", onWheel);
  }, []);

  function zoomBy(factor) {
    const box = measure(stageRef.current, imgRef.current);
    setView((v) => clampView(scaleAbout(v, { x: 0, y: 0 }, v.scale * factor), box));
  }

  // One finger drags, two pinch. Starting again whenever a finger lands or
  // lifts lets a pinch carry on as a drag with the finger that is left.
  function begin() {
    const points = [...pointers.current.values()];
    const box = measure(stageRef.current, imgRef.current);
    if (points.length >= 2) {
      const [a, b] = points;
      gesture.current = {
        kind: "pinch",
        view,
        distance: Math.hypot(a.x - b.x, a.y - b.y) || 1,
        middle: fromCentre((a.x + b.x) / 2, (a.y + b.y) / 2, box),
      };
    } else if (points.length === 1) {
      gesture.current = { kind: "drag", view, start: points[0], moved: false };
    } else {
      gesture.current = null;
    }
  }

  function onPointerDown(event) {
    if (event.pointerType === "mouse" && event.button !== 0) return;
    try {
      event.currentTarget.setPointerCapture(event.pointerId);
    } catch {
      /* the pointer is already gone; the gesture works without capture */
    }
    pointers.current.set(event.pointerId, { x: event.clientX, y: event.clientY });
    closeOnClick.current = false;
    setGesturing(true);
    begin();
  }

  function onPointerMove(event) {
    if (!pointers.current.has(event.pointerId)) return;
    pointers.current.set(event.pointerId, { x: event.clientX, y: event.clientY });
    const g = gesture.current;
    if (!g) return;
    const box = measure(stageRef.current, imgRef.current);
    if (g.kind === "pinch") {
      const [a, b] = [...pointers.current.values()];
      const middle = fromCentre((a.x + b.x) / 2, (a.y + b.y) / 2, box);
      // Scale about where the fingers came down, then follow their midpoint.
      const scaled = scaleAbout(g.view, g.middle, g.view.scale * (Math.hypot(a.x - b.x, a.y - b.y) / g.distance));
      setView(clampView({ ...scaled, x: scaled.x + middle.x - g.middle.x, y: scaled.y + middle.y - g.middle.y }, box));
      return;
    }
    const dx = event.clientX - g.start.x;
    const dy = event.clientY - g.start.y;
    if (Math.hypot(dx, dy) > TAP_SLOP) g.moved = true;
    if (g.moved && g.view.scale > MIN_SCALE) {
      setView(clampView({ ...g.view, x: g.view.x + dx, y: g.view.y + dy }, box));
    }
  }

  function onPointerUp(event) {
    if (!pointers.current.has(event.pointerId)) return;
    pointers.current.delete(event.pointerId);
    const g = gesture.current;
    if (event.type === "pointerup" && g?.kind === "drag" && !g.moved) tap(event);
    if (!pointers.current.size) setGesturing(false);
    begin();
  }

  // A double tap zooms in on that spot, or back out; a single tap off the
  // photo closes it, unless zoomed in, when it is easy to do by accident. The
  // close waits for the click that follows the tap: gone any sooner, the
  // click would land on whatever is underneath -- an answer, say.
  function tap(event) {
    const box = measure(stageRef.current, imgRef.current);
    const p = fromCentre(event.clientX, event.clientY, box);
    const now = performance.now();
    const prev = lastTap.current;
    if (prev && now - prev.time < DOUBLE_TAP_MS && Math.hypot(p.x - prev.x, p.y - prev.y) < 30) {
      lastTap.current = null;
      setView((v) =>
        v.scale > MIN_SCALE ? { scale: 1, x: 0, y: 0 } : clampView(scaleAbout(v, p, DOUBLE_TAP_SCALE), box),
      );
      return;
    }
    lastTap.current = { time: now, x: p.x, y: p.y };
    closeOnClick.current = view.scale === MIN_SCALE && !onPhoto(view, p, box);
  }

  function onStageClick() {
    if (!closeOnClick.current) return;
    closeOnClick.current = false;
    onClose();
  }

  return createPortal(
    <div
      className="zoom-root"
      role="dialog"
      aria-modal="true"
      aria-label={alt || t("zoom.title")}
      data-no-swipe
      onPointerDown={stop}
      onPointerMove={stop}
      onPointerUp={stop}
      onPointerCancel={stop}
      onClick={stop}
    >
      <div
        ref={stageRef}
        className={`zoom-stage ${gesturing ? "is-gesturing" : ""}`}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerCancel={onPointerUp}
        onClick={onStageClick}
      >
        <img
          ref={imgRef}
          className="zoom-photo"
          src={src}
          alt={alt}
          draggable="false"
          style={{ transform: `translate(${view.x}px, ${view.y}px) scale(${view.scale})` }}
        />
      </div>
      <button
        ref={closeButtonRef}
        className="zoom-close"
        onClick={onClose}
        aria-label={t("common.close")}
        type="button"
      >
        <span className="material-symbols-outlined" aria-hidden="true">close</span>
      </button>
      <div className="zoom-tools">
        <button onClick={() => zoomBy(1 / STEP)} disabled={view.scale <= MIN_SCALE} aria-label={t("zoom.out")} type="button">
          <span className="material-symbols-outlined" aria-hidden="true">zoom_out</span>
        </button>
        <button onClick={() => zoomBy(STEP)} disabled={view.scale >= MAX_SCALE} aria-label={t("zoom.in")} type="button">
          <span className="material-symbols-outlined" aria-hidden="true">zoom_in</span>
        </button>
      </div>
    </div>,
    document.body,
  );
}

/**
 * The small magnifier on a photo whose own tap already does something (answers
 * the question, turns the card over).
 */
export function ZoomButton({ onClick, className = "" }) {
  const t = useT();
  return (
    <button
      className={`zoom-button ${className}`}
      onClick={(event) => {
        event.stopPropagation();
        onClick();
      }}
      aria-label={t("zoom.open")}
      title={t("zoom.open")}
      data-no-swipe
      type="button"
    >
      <span className="material-symbols-outlined" aria-hidden="true">zoom_in</span>
    </button>
  );
}

export default ImageZoom;
