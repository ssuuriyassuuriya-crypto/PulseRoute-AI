import type { ApiEnvelope, EmergencySnapshot, LoginData, ReportData, SignalState, TimelineEvent, TrafficProcessingResult, VisionStatus } from "../types";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api";

async function request<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  const body = (await response.json()) as ApiEnvelope<T> | { detail?: string; error?: string };
  if (!response.ok) {
    const message = "detail" in body ? body.detail : "error" in body ? body.error : undefined;
    throw new Error(message ?? "Request failed");
  }
  return (body as ApiEnvelope<T>).data;
}

export const api = {
  login: (username: string, password: string) => request<LoginData>("/auth/login", {
    method: "POST", body: JSON.stringify({ username, password }),
  }),
  emergencyStatus: (token: string) => request<EmergencySnapshot>("/emergency/status", {}, token),
  startMission: (token: string) => request<EmergencySnapshot>("/emergency/start", {
    method: "POST", body: JSON.stringify({}),
  }, token),
  stopMission: (token: string) => request<EmergencySnapshot>("/emergency/stop", { method: "POST" }, token),
  requestPriority: (token: string) => request<EmergencySnapshot>("/emergency/priority", { method: "POST" }, token),
  getSignals: (token: string) => request<SignalState>("/signals", {}, token),
  overrideSignal: (token: string, road: string, durationSeconds: number) => request<SignalState>("/signals/override", {
    method: "POST", body: JSON.stringify({ road, duration_seconds: durationSeconds }),
  }, token),
  resetSignals: (token: string) => request<SignalState>("/signals/reset", { method: "POST" }, token),
  generateDemoTraffic: (token: string) => request<TrafficProcessingResult>("/traffic/demo", { method: "POST" }, token),
  report: (token: string) => request<ReportData>("/reports", {}, token),
  timeline: (token: string) => request<TimelineEvent[]>("/timeline", {}, token),
  demoPlayTraffic: (token: string) => request<unknown>("/demo/play-traffic", { method: "POST" }, token),
  demoTriggerEmergency: (token: string) => request<unknown>("/demo/trigger-emergency", { method: "POST" }, token),
  demoStopEmergency: (token: string) => request<unknown>("/demo/stop-emergency", { method: "POST" }, token),
  demoResetSimulation: (token: string) => request<unknown>("/demo/reset-simulation", { method: "POST" }, token),
  demoClearLogs: (token: string) => request<unknown>("/demo/clear-logs", { method: "POST" }, token),
  uploadVideo: async (token: string, video: File): Promise<{ file_name: string; vision: VisionStatus }> => {
    const body = new FormData();
    body.append("video", video);
    const response = await fetch(`${API_BASE_URL}/traffic/upload`, { method: "POST", headers: { Authorization: `Bearer ${token}` }, body });
    const payload = await response.json() as ApiEnvelope<{ file_name: string; vision: VisionStatus }> | { detail?: string };
    if (!response.ok) throw new Error("detail" in payload ? payload.detail ?? "Upload failed" : "Upload failed");
    return (payload as ApiEnvelope<{ file_name: string; vision: VisionStatus }>).data;
  },
};
