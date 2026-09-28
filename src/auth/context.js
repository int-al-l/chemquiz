import { createContext, useContext } from "react";

export const AuthContext = createContext(null);

/** Who is signed in, and how to change that. */
export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside <AuthProvider>");
  return value;
}
