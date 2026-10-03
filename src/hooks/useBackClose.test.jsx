import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { closeOverlaysThen, useBackClose } from "./useBackClose";

const overlays = () => window.history.state?.overlays ?? [];

/** Back to a clean entry between tests. */
afterEach(async () => {
  const n = overlays().length;
  if (n) {
    window.history.go(-n);
    await waitFor(() => expect(overlays()).toEqual([]));
  }
});

describe("useBackClose", () => {
  it("adds a history entry when it opens, keeping what the router stored there", () => {
    window.history.replaceState({ idx: 3, key: "abc" }, "");
    const before = window.history.length;
    const { result } = renderHook(() => useBackClose("why"));
    act(() => result.current[1]());
    expect(result.current[0]).toBe(true);
    expect(window.history.length).toBe(before + 1);
    expect(window.history.state).toMatchObject({ idx: 3, key: "abc", overlays: ["why"] });
  });

  it("closes on Back instead of leaving the page", async () => {
    const { result } = renderHook(() => useBackClose("why"));
    act(() => result.current[1]());
    act(() => window.history.back());
    await waitFor(() => expect(result.current[0]).toBeNull());
    expect(overlays()).toEqual([]);
  });

  it("takes its entry off again when closed on the page", async () => {
    const { result } = renderHook(() => useBackClose("photo"));
    act(() => result.current[1]("/static/images/a.jpg"));
    expect(result.current[0]).toBe("/static/images/a.jpg");
    act(() => result.current[2]());
    await waitFor(() => expect(result.current[0]).toBeNull());
    expect(overlays()).toEqual([]);
  });

  it("closes only the top overlay of a stack", async () => {
    const sheet = renderHook(() => useBackClose("why"));
    const photo = renderHook(() => useBackClose("photo"));
    act(() => sheet.result.current[1]());
    act(() => photo.result.current[1]("a.jpg"));
    expect(overlays()).toEqual(["why", "photo"]);
    act(() => window.history.back());
    await waitFor(() => expect(photo.result.current[0]).toBeNull());
    expect(sheet.result.current[0]).toBe(true);
    expect(overlays()).toEqual(["why"]);
  });
});

describe("closeOverlaysThen", () => {
  it("runs at once when nothing is open", () => {
    const then = vi.fn();
    closeOverlaysThen(then);
    expect(then).toHaveBeenCalledTimes(1);
  });

  it("waits for every overlay entry to go, and ignores a second press meanwhile", async () => {
    const sheet = renderHook(() => useBackClose("why"));
    const photo = renderHook(() => useBackClose("photo"));
    act(() => sheet.result.current[1]());
    act(() => photo.result.current[1]("a.jpg"));
    const then = vi.fn(() => expect(overlays()).toEqual([]));
    const again = vi.fn();
    act(() => {
      closeOverlaysThen(then);
      closeOverlaysThen(again);
    });
    await waitFor(() => expect(then).toHaveBeenCalledTimes(1));
    expect(again).not.toHaveBeenCalled();
    expect(sheet.result.current[0]).toBeNull();
    expect(photo.result.current[0]).toBeNull();
  });
});
