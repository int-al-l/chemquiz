/**
 * The arithmetic behind ImageZoom, kept apart so it can be tested without a
 * browser.
 *
 * A view is { scale, x, y }: the photo is drawn at its fitted size times
 * `scale`, its centre moved (x, y) px from the centre of the screen. Points
 * are measured from that centre too.
 */

export const MIN_SCALE = 1;
export const MAX_SCALE = 5;

const clamp = (value, low, high) => Math.min(high, Math.max(low, value));

/** Scale to `next`, keeping the point `p` where it is on screen. */
export function scaleAbout(view, p, next) {
  const scale = clamp(next, MIN_SCALE, MAX_SCALE);
  const k = scale / view.scale;
  return { scale, x: p.x - (p.x - view.x) * k, y: p.y - (p.y - view.y) * k };
}

/**
 * Keep the photo on screen: it may move only as far as it overhangs the
 * screen, so at its fitted size it stays centred and its edge never comes
 * away from the screen's edge.
 *
 *   box = { stageW, stageH, photoW, photoH }   photo size before scaling
 */
export function clampView(view, box) {
  const scale = clamp(view.scale, MIN_SCALE, MAX_SCALE);
  const maxX = Math.max(0, (box.photoW * scale - box.stageW) / 2);
  const maxY = Math.max(0, (box.photoH * scale - box.stageH) / 2);
  return { scale, x: clamp(view.x, -maxX, maxX) || 0, y: clamp(view.y, -maxY, maxY) || 0 };
}

/** Whether the point `p` falls on the photo rather than the dark area around it. */
export function onPhoto(view, p, box) {
  return (
    Math.abs(p.x - view.x) <= (box.photoW * view.scale) / 2 &&
    Math.abs(p.y - view.y) <= (box.photoH * view.scale) / 2
  );
}

/**
 * The size an image is drawn at by `object-fit: contain` in a box of
 * `boxW` x `boxH`.
 */
export function fittedSize(naturalW, naturalH, boxW, boxH) {
  if (!naturalW || !naturalH) return { w: boxW, h: boxH };
  const f = Math.min(boxW / naturalW, boxH / naturalH);
  return { w: naturalW * f, h: naturalH * f };
}
