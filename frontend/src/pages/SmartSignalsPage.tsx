import { useState } from "react";
import { BrainCircuit, RotateCcw, ShieldAlert, SlidersHorizontal } from "lucide-react";
import toast from "react-hot-toast";
import { IntersectionVisualizer } from "../components/IntersectionVisualizer";
import { useAuth } from "../contexts/AuthContext";
import { useDashboard } from "../contexts/DashboardContext";
import { api } from "../services/api";

const roads = ["North", "East", "South", "West"];

export function SmartSignalsPage() {
  const { session } = useAuth();
  const { state } = useDashboard();
  const [busy, setBusy] = useState(false);
  const signals = state?.signals;
  const decision = state?.ai_decision;
  const operate = async (operation: () => Promise<unknown>, message: string) => { setBusy(true); try { await operation(); toast.success(message); } catch (error) { toast.error(error instanceof Error ? error.message : "Signal operation failed"); } finally { setBusy(false); } };
  return <section><div className="flex flex-wrap items-end justify-between gap-4"><div><p className="text-sm text-emerald-300">ADAPTIVE INTERSECTION</p><h1 className="mt-1 text-3xl font-semibold">Smart signals</h1></div>{signals?.emergency_lock && <span className="inline-flex items-center gap-2 rounded-full bg-rose-500/15 px-3 py-2 text-sm text-rose-300"><ShieldAlert size={16} />Emergency corridor locked</span>}</div><div className="mt-7 grid gap-5 xl:grid-cols-[.8fr_1.4fr_.8fr]"><aside className="rounded-2xl border border-white/10 bg-[#161b22] p-5"><div className="flex items-center gap-2"><BrainCircuit className="text-emerald-300" size={20} /><h2 className="font-semibold">AI decision</h2></div>{decision ? <dl className="mt-6 space-y-4 text-sm"><Data label="Prioritized road" value={decision.road} /><Data label="Vehicles" value={decision.vehicles} /><Data label="Congestion" value={decision.density} /><Data label="Score" value={decision.score} /><Data label="Green time" value={`${decision.green_time}s`} /><Data label="Confidence" value={`${decision.confidence}%`} /><div className="border-t border-white/10 pt-4"><dt className="text-slate-500">Reason</dt><dd className="mt-2 leading-6 text-slate-300">{decision.reason}</dd></div></dl> : <p className="mt-5 text-sm text-slate-400">Submit a traffic frame to activate AI prioritization.</p>}</aside><IntersectionVisualizer signals={signals} /><aside className="rounded-2xl border border-white/10 bg-[#161b22] p-5"><div className="flex items-center gap-2"><SlidersHorizontal className="text-amber-300" size={20} /><h2 className="font-semibold">Manual control</h2></div><p className="mt-2 text-sm leading-6 text-slate-400">Set a 30-second green phase. Controls are blocked during an emergency lock.</p><div className="mt-5 grid grid-cols-2 gap-2">{roads.map((road) => <button key={road} disabled={busy || signals?.emergency_lock} onClick={() => session && operate(() => api.overrideSignal(session.token, road, 30), `${road} override active`)} className="rounded-lg border border-white/10 bg-white/5 px-3 py-3 text-sm hover:border-emerald-400/50 hover:text-emerald-300 disabled:opacity-40">{road}</button>)}</div><button disabled={busy || signals?.emergency_lock} onClick={() => session && operate(() => api.resetSignals(session.token), "Adaptive mode restored")} className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-400 px-3 py-3 text-sm font-semibold text-slate-950 disabled:opacity-40"><RotateCcw size={16} />Restore adaptive mode</button></aside></div></section>;
}

function Data({ label, value }: { label: string; value: string | number }) { return <div className="flex justify-between gap-4"><dt className="text-slate-400">{label}</dt><dd className="font-medium text-slate-100">{value}</dd></div>; }
