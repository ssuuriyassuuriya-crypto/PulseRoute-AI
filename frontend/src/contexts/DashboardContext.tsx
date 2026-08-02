import { createContext, useContext, useEffect, useMemo, useState, type PropsWithChildren } from "react";
import { dashboardSocketUrl } from "../services/websocket";
import type { DashboardState } from "../types";
import { useAuth } from "./AuthContext";

interface DashboardContextValue { state: DashboardState | null; connection: "connected" | "reconnecting" | "disconnected" }
const DashboardContext = createContext<DashboardContextValue>({ state: null, connection: "disconnected" });

export function DashboardProvider({ children }: PropsWithChildren) {
  const { session } = useAuth();
  const [state, setState] = useState<DashboardState | null>(null);
  const [connection, setConnection] = useState<DashboardContextValue["connection"]>("disconnected");

  useEffect(() => {
    if (!session || session.user.role !== "ADMIN") return;
    let socket: WebSocket | undefined;
    let retry: number | undefined;
    let cancelled = false;
    const connect = () => {
      setConnection(socket ? "reconnecting" : "disconnected");
      socket = new WebSocket(dashboardSocketUrl(session.token));
      socket.onopen = () => setConnection("connected");
      socket.onmessage = (event) => setState(JSON.parse(event.data) as DashboardState);
      socket.onclose = () => {
        if (!cancelled) retry = window.setTimeout(connect, 2_000);
      };
    };
    connect();
    return () => { cancelled = true; socket?.close(); if (retry) window.clearTimeout(retry); };
  }, [session]);

  const value = useMemo(() => ({ state, connection }), [state, connection]);
  return <DashboardContext.Provider value={value}>{children}</DashboardContext.Provider>;
}

export const useDashboard = () => useContext(DashboardContext);
