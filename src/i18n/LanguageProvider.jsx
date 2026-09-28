/** Holds the interface language (see index.js); a scope fixes it for part of the page. */
import { useCallback, useContext, useEffect, useMemo, useState } from "react";

import { setRequestLanguage } from "../api/client";
import { detectLanguage, LANGUAGES, LanguageContext, readStored, writeStored } from "./index";

export function LanguageProvider({ children }) {
  // Read synchronously, so the very first requests already carry the language.
  const [lang, setLangState] = useState(() => {
    const initial = detectLanguage(readStored(), window.navigator?.language);
    setRequestLanguage(initial);
    return initial;
  });

  const setLang = useCallback((next) => {
    if (!LANGUAGES.includes(next)) return;
    setRequestLanguage(next);
    writeStored(next);
    setLangState(next);
  }, []);

  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  const value = useMemo(() => ({ lang, setLang }), [lang, setLang]);
  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

/** A part of the page in a fixed language (a class game in the teacher's). */
export function LanguageScope({ lang, children }) {
  const outer = useContext(LanguageContext);
  const value = useMemo(
    () => ({ lang: LANGUAGES.includes(lang) ? lang : outer.lang, setLang: outer.setLang }),
    [lang, outer],
  );
  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

