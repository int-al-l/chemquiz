import { createContext, useContext } from "react";

export const ProgressContext = createContext(null);

/** XP, levels, card mastery and the deck catalogue. */
export function useProgress() {
  const value = useContext(ProgressContext);
  if (!value) throw new Error("useProgress must be used inside <ProgressProvider>");
  return value;
}
