import { act, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { detectLanguage, translate, useLang } from "./index";
import { LanguageProvider } from "./LanguageProvider";
import en from "./en";
import ru from "./ru";
import { useApi } from "../hooks/useApi";

describe("dictionaries", () => {
  it("have the same keys", () => {
    expect(Object.keys(ru).sort()).toEqual(Object.keys(en).sort());
  });

  it("use plural objects in both or neither", () => {
    for (const key of Object.keys(en)) {
      expect(typeof ru[key], key).toBe(typeof en[key]);
    }
  });
});

describe("translate", () => {
  it("fills values and picks Russian plural forms", () => {
    const cases = { 1: "1 карточка", 2: "2 карточки", 5: "5 карточек", 11: "11 карточек",
      21: "21 карточка", 22: "22 карточки", 25: "25 карточек" };
    for (const [n, text] of Object.entries(cases)) {
      expect(translate("ru", "common.cards", { n: Number(n) })).toBe(text);
    }
    expect(translate("en", "common.cards", { n: 1 })).toBe("1 card");
    expect(translate("en", "common.cards", { n: 3 })).toBe("3 cards");
  });

  it("falls back to English, then to the key", () => {
    expect(translate("ru", "no.such.key")).toBe("no.such.key");
    expect(translate("de", "common.cards", { n: 2 })).toBe("2 cards");
  });
});

describe("detectLanguage", () => {
  it("prefers the stored choice, then the browser", () => {
    expect(detectLanguage("en", "ru-RU")).toBe("en");
    expect(detectLanguage(null, "ru-RU")).toBe("ru");
    expect(detectLanguage(null, "en-GB")).toBe("en");
    expect(detectLanguage("xx", "RU")).toBe("ru");
    expect(detectLanguage(null, undefined)).toBe("en");
  });
});

function Probe({ loader }) {
  const { data } = useApi(loader);
  const { setLang } = useLang();
  return (
    <>
      <span>{data ?? "…"}</span>
      <button onClick={() => setLang("ru")}>ru</button>
    </>
  );
}

describe("switching language", () => {
  it("re-fetches what useApi loaded", async () => {
    window.localStorage.setItem("chemquiz.lang", "en");
    const loader = vi.fn().mockResolvedValueOnce("Beaker").mockResolvedValueOnce("Стакан");
    render(<LanguageProvider><Probe loader={loader} /></LanguageProvider>);
    expect(await screen.findByText("Beaker")).toBeTruthy();
    await act(async () => screen.getByText("ru").click());
    expect(await screen.findByText("Стакан")).toBeTruthy();
    expect(loader).toHaveBeenCalledTimes(2);
    expect(document.documentElement.lang).toBe("ru");
  });
});
