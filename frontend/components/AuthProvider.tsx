"use client";

import { createContext, useContext, useMemo, useState } from "react";

type AuthContextType = {
  token: string;
  setToken: (token: string) => void;
  clearToken: () => void;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setTokenState] = useState("");
  const value = useMemo(
    () => ({
      token,
      setToken: (newToken: string) => setTokenState(newToken),
      clearToken: () => setTokenState("")
    }),
    [token]
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return ctx;
}
