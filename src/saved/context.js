import { createContext, useContext } from "react";

export const SavedContext = createContext(null);

/** The saved list, wherever it lives. */
export function useSaved() {
  const value = useContext(SavedContext);
  if (!value) throw new Error("useSaved must be used inside <SavedProvider>");
  return value;
}
