import { createContext, useContext, useMemo, useState, type PropsWithChildren } from "react";
import { api } from "../services/api";
import type { User } from "../types";

interface AuthState { token: string; user: User }
interface AuthContextValue {
  session: AuthState | null;
  login: (username: string, password: string) => Promise<User>;
  logout: () => void;
}

const STORAGE_KEY = "pulseroute-session";
const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: PropsWithChildren) {
  const [session, setSession] = useState<AuthState | null>(() => {
    const saved = sessionStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) as AuthState : null;
  });
  const value = useMemo<AuthContextValue>(() => ({
    session,
    login: async (username, password) => {
      const data = await api.login(username, password);
      const next = { token: data.access_token, user: data.user };
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      setSession(next);
      return data.user;
    },
    logout: () => {
      sessionStorage.removeItem(STORAGE_KEY);
      setSession(null);
    },
  }), [session]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
