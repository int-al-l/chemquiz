import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import ImageZoom, { ZoomButton } from "./ImageZoom";
import { MAX_SCALE, clampView, fittedSize, onPhoto, scaleAbout } from "./zoom";

describe("zoom arithmetic", () => {
  const box = { stageW: 400, stageH: 800, photoW: 200, photoH: 600 };

  it("keeps the point under the fingers in place", () => {
    // A point q of the photo is drawn at view + scale * q. At the fitted size,
    // unmoved, the point under p is q = p; after zooming it must still be at p.
    const p = { x: 50, y: -100 };
    const view = scaleAbout({ scale: 1, x: 0, y: 0 }, p, 2);
    expect(view.scale).toBe(2);
    expect(view.x + view.scale * p.x).toBeCloseTo(p.x);
    expect(view.y + view.scale * p.y).toBeCloseTo(p.y);
  });

  it("never zooms out past the fitted size or in past the limit", () => {
    expect(scaleAbout({ scale: 1, x: 0, y: 0 }, { x: 0, y: 0 }, 0.3).scale).toBe(1);
    expect(scaleAbout({ scale: 4, x: 0, y: 0 }, { x: 0, y: 0 }, 40).scale).toBe(MAX_SCALE);
  });

  it("lets the photo move only as far as it overhangs the screen", () => {
    // At its fitted size the photo stays centred.
    expect(clampView({ scale: 1, x: 120, y: -90 }, box)).toEqual({ scale: 1, x: 0, y: 0 });
    // At 3x it is 600 x 1800 on a 400 x 800 screen: 100 px spare each side, 500 up and down.
    expect(clampView({ scale: 3, x: 999, y: -999 }, box)).toEqual({ scale: 3, x: 100, y: -500 });
  });

  it("tells the photo from the dark area around it", () => {
    const view = { scale: 1, x: 0, y: 0 };
    expect(onPhoto(view, { x: 90, y: 0 }, box)).toBe(true);
    expect(onPhoto(view, { x: 150, y: 0 }, box)).toBe(false);
  });

  it("works out the size object-fit: contain draws at", () => {
    expect(fittedSize(300, 900, 400, 600)).toEqual({ w: 200, h: 600 });
    expect(fittedSize(0, 0, 400, 600)).toEqual({ w: 400, h: 600 });
  });
});

describe("ImageZoom", () => {
  it("shows the photo over the page and closes on the cross", () => {
    const onClose = vi.fn();
    render(<ImageZoom src="/static/images/a.jpg" alt="Spinning band column" onClose={onClose} />);
    const dialog = screen.getByRole("dialog", { name: "Spinning band column" });
    expect(dialog.parentElement).toBe(document.body);
    expect(document.body.style.overflow).toBe("hidden");
    fireEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("takes Escape and every other key for itself", () => {
    const onClose = vi.fn();
    const pageKeys = vi.fn();
    window.addEventListener("keydown", pageKeys);
    render(<ImageZoom src="/a.jpg" onClose={onClose} />);
    fireEvent.keyDown(window, { key: "1" });
    fireEvent.keyDown(window, { key: "Escape" });
    window.removeEventListener("keydown", pageKeys);
    expect(onClose).toHaveBeenCalledTimes(1);
    // 1-4 would answer the quiz question behind the photo.
    expect(pageKeys).not.toHaveBeenCalled();
  });

  it("zooms with the buttons", () => {
    render(<ImageZoom src="/a.jpg" onClose={() => {}} />);
    const zoomOut = screen.getByRole("button", { name: "Zoom out" });
    expect(zoomOut).toBeDisabled();
    fireEvent.click(screen.getByRole("button", { name: "Zoom in" }));
    expect(zoomOut).toBeEnabled();
    expect(document.querySelector(".zoom-photo").style.transform).toContain("scale(2)");
  });

  it("gives the page back its scrolling when it closes", () => {
    document.body.style.overflow = "auto";
    const { unmount } = render(<ImageZoom src="/a.jpg" onClose={() => {}} />);
    unmount();
    expect(document.body.style.overflow).toBe("auto");
    document.body.style.overflow = "";
  });
});

describe("ZoomButton", () => {
  it("opens the photo without the click reaching what it sits on", () => {
    const onOpen = vi.fn();
    const onCard = vi.fn();
    render(
      <div onClick={onCard}>
        <ZoomButton onClick={onOpen} />
      </div>,
    );
    fireEvent.click(screen.getByRole("button", { name: "Zoom in on the photo" }));
    expect(onOpen).toHaveBeenCalledTimes(1);
    expect(onCard).not.toHaveBeenCalled();
  });
});
