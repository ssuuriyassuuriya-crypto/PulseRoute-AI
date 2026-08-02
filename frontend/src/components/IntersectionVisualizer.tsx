import { motion } from "framer-motion";
import type { SignalState } from "../types";

const positions: Record<string, { x: number; y: number; labelX: number; labelY: number }> = {
  North: { x: 250, y: 100, labelX: 250, labelY: 35 }, South: { x: 250, y: 400, labelX: 250, labelY: 475 }, West: { x: 100, y: 250, labelX: 35, labelY: 255 }, East: { x: 400, y: 250, labelX: 465, labelY: 255 },
};
const colors: Record<string, string> = { GREEN: "#00e676", YELLOW: "#ffd600", RED: "#ff1744" };

export function IntersectionVisualizer({ signals }: { signals: SignalState | undefined }) {
  return <div className="rounded-2xl border border-white/10 bg-[#161b22] p-3 sm:p-6"><svg viewBox="0 0 500 500" className="mx-auto block w-full max-w-[35rem]" aria-label="Live four-way intersection"><rect width="500" height="500" rx="24" fill="#101722" /><path d="M190 0h120v190h190v120H310v190H190V310H0V190h190z" fill="#2a3440" /><path d="M245 0v190M245 310v190M0 245h190M310 245h190" stroke="#f8fafc" strokeDasharray="14 14" strokeWidth="3" opacity=".55" />{Object.entries(positions).map(([road, point]) => { const signal = signals?.lights[road] ?? "RED"; return <g key={road}><text x={point.labelX} y={point.labelY} fill="#cbd5e1" fontSize="15" fontWeight="600" textAnchor="middle">{road.toUpperCase()}</text><motion.circle cx={point.x} cy={point.y} r="25" fill={colors[signal]} animate={{ opacity: signal === "GREEN" ? [0.7, 1, 0.7] : 1 }} transition={{ repeat: Infinity, duration: 1.4 }} /><circle cx={point.x} cy={point.y} r="31" fill="none" stroke="rgba(255,255,255,.14)" strokeWidth="3" /><text x={point.x} y={point.y + 5} fill="#081018" fontSize="10" fontWeight="800" textAnchor="middle">{signal}</text></g>; })}<text x="250" y="257" fill="#e2e8f0" fontSize="26" fontWeight="700" textAnchor="middle">{signals?.remaining_seconds ?? "—"}s</text><text x="250" y="280" fill="#94a3b8" fontSize="12" textAnchor="middle">{signals?.mode ?? "CONNECTING"}</text></svg></div>;
}
