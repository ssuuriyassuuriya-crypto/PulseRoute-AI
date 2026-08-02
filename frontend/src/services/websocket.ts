import { API_BASE_URL } from "./api";

export function dashboardSocketUrl(token: string): string {
  const backendOrigin = new URL(API_BASE_URL).origin;
  const websocketOrigin = backendOrigin.replace(/^http/, "ws");
  return `${websocketOrigin}/ws/dashboard?token=${encodeURIComponent(token)}`;
}
