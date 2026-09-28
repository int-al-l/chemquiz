import { act, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "../api/client";
import { AuthContext } from "../auth/context";
import { SavedProvider } from "./SavedProvider";
import { useSaved } from "./context";
import { LOCAL_STORAGE_KEY } from "./localList";

/**
 * These cover the ordering bugs, which are the ones that actually shipped.
 *
 * The first was invisible in every hand test: the list fetched on page load
 * would land *after* a save and overwrite it, so the bookmark filled in and
 * then emptied itself. On a fast loopback the fetch always won the race and
 * everything looked fine.
 */

vi.mock("../api/client", async () => {
  const actual = await vi.importActual("../api/client");
  return {
    ...actual,
    fetchMyList: vi.fn(),
    saveItem: vi.fn(),
    unsaveItem: vi.fn(),
  };
});

const { fetchMyList, saveItem, unsaveItem } = await import("../api/client");

/** A promise whose resolution this test controls. */
function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

function Probe() {
  const { slugs, has, toggle, error } = useSaved();
  return (
    <div>
      <span data-testid="slugs">{slugs.join(",")}</span>
      <span data-testid="has-flask">{String(has("flask"))}</span>
      <span data-testid="error">{error ? error.message : ""}</span>
      <button onClick={() => toggle("flask")}>toggle flask</button>
    </div>
  );
}

function renderSaved({ user, signOut = vi.fn() } = {}) {
  const auth = { user, completeSignIn: vi.fn(), signOut };
  render(
    <AuthContext.Provider value={auth}>
      <SavedProvider>
        <Probe />
      </SavedProvider>
    </AuthContext.Provider>,
  );
  return { signOut };
}

const SIGNED_IN = { token: "tok-1", email: "a@b.c", name: "A", saved_count: 0 };

beforeEach(() => {
  vi.clearAllMocks();
  window.localStorage.clear();
  fetchMyList.mockResolvedValue([]);
  saveItem.mockResolvedValue({ saved: true });
  unsaveItem.mockResolvedValue({ saved: false });
});

describe("signed in", () => {
  it("a list fetched before a save does not undo that save", async () => {
    // The fetch starts on mount and is still in flight when the user saves.
    const inFlight = deferred();
    fetchMyList.mockReturnValue(inFlight.promise);

    renderSaved({ user: SIGNED_IN });

    await act(async () => {
      screen.getByText("toggle flask").click();
    });
    expect(screen.getByTestId("has-flask")).toHaveTextContent("true");
    expect(saveItem).toHaveBeenCalledWith("flask");

    // The reply describes the world before the save. Applying it would empty
    // the bookmark the person just set -- the bug this test exists for.
    await act(async () => {
      inFlight.resolve([]);
      await inFlight.promise;
    });

    expect(screen.getByTestId("has-flask")).toHaveTextContent("true");
  });

  it("shows the server's list once it arrives", async () => {
    fetchMyList.mockResolvedValue([{ slug: "beaker" }, { slug: "funnel" }]);
    renderSaved({ user: SIGNED_IN });

    await waitFor(() =>
      expect(screen.getByTestId("slugs")).toHaveTextContent("beaker,funnel"),
    );
  });

  it("saving calls the server and keeps the bookmark on", async () => {
    renderSaved({ user: SIGNED_IN });
    await waitFor(() => expect(fetchMyList).toHaveBeenCalled());

    await act(async () => {
      screen.getByText("toggle flask").click();
    });

    expect(saveItem).toHaveBeenCalledWith("flask");
    expect(screen.getByTestId("has-flask")).toHaveTextContent("true");
  });

  it("unsaving an item already on the list calls delete", async () => {
    fetchMyList.mockResolvedValue([{ slug: "flask" }]);
    renderSaved({ user: SIGNED_IN });
    await waitFor(() =>
      expect(screen.getByTestId("has-flask")).toHaveTextContent("true"),
    );

    await act(async () => {
      screen.getByText("toggle flask").click();
    });

    expect(unsaveItem).toHaveBeenCalledWith("flask");
    expect(screen.getByTestId("has-flask")).toHaveTextContent("false");
  });

  it("a failed save puts the bookmark back and says why", async () => {
    saveItem.mockRejectedValue(new ApiError("Server exploded", 500));
    renderSaved({ user: SIGNED_IN });
    await waitFor(() => expect(fetchMyList).toHaveBeenCalled());

    await act(async () => {
      screen.getByText("toggle flask").click();
    });

    // Silently reverting is what made this look like a dead button.
    expect(screen.getByTestId("has-flask")).toHaveTextContent("false");
    expect(screen.getByTestId("error")).toHaveTextContent("Server exploded");
  });

  it("a save rejected as unauthorised signs the person out", async () => {
    saveItem.mockRejectedValue(new ApiError("expired", 401));
    const { signOut } = renderSaved({ user: SIGNED_IN });
    await waitFor(() => expect(fetchMyList).toHaveBeenCalled());

    await act(async () => {
      screen.getByText("toggle flask").click();
    });

    expect(signOut).toHaveBeenCalled();
    expect(screen.getByTestId("error")).toHaveTextContent("Sign in again");
  });

  it("a stale token found on load signs the person out quietly", async () => {
    fetchMyList.mockRejectedValue(new ApiError("expired", 401));
    const { signOut } = renderSaved({ user: SIGNED_IN });

    await waitFor(() => expect(signOut).toHaveBeenCalled());
    // Nothing to tell them off about: they simply are not signed in.
    expect(screen.getByTestId("error")).toHaveTextContent("");
  });
});

describe("signed out", () => {
  it("saves to this browser and never calls the server", async () => {
    renderSaved({ user: null });

    await act(async () => {
      screen.getByText("toggle flask").click();
    });

    expect(screen.getByTestId("has-flask")).toHaveTextContent("true");
    expect(saveItem).not.toHaveBeenCalled();
    expect(fetchMyList).not.toHaveBeenCalled();
    expect(JSON.parse(window.localStorage.getItem(LOCAL_STORAGE_KEY))).toEqual([
      "flask",
    ]);
  });

  it("starts from whatever this browser already had", async () => {
    window.localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(["beaker"]));
    renderSaved({ user: null });
    expect(screen.getByTestId("slugs")).toHaveTextContent("beaker");
  });
});
