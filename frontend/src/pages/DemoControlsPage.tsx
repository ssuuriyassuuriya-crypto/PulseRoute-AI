import { Eraser, Play, RotateCcw, Siren, Square } from "lucide-react";
import { type ComponentType, useState } from "react";
import toast from "react-hot-toast";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../services/api";

interface Control { label: string; description: string; action: (token: string) => Promise<unknown>; icon: ComponentType<{ size?: number; className?: string }>; tone: string }

export function DemoControlsPage() {
  const { session } = useAuth();
  const [running, setRunning] = useState<string | null>(null);
  const controls: Control[] = [
    { label: "Play demo traffic", description: "Creates a high-congestion, tracked traffic frame.", action: api.demoPlayTraffic, icon: Play, tone: "bg-emerald-400 text-slate-950" },
    { label: "Trigger emergency", description: "Starts the ambulance simulation and green corridor.", action: api.demoTriggerEmergency, icon: Siren, tone: "bg-rose-500 text-white" },
    { label: "Stop emergency", description: "Completes or clears the current mission safely.", action: api.demoStopEmergency, icon: Square, tone: "bg-amber-400 text-slate-950" },
    { label: "Reset simulation", description: "Resets GPS, mission, traffic, and adaptive signals.", action: api.demoResetSimulation, icon: RotateCcw, tone: "bg-sky-400 text-slate-950" },
    { label: "Clear timeline", description: "Removes the current bounded audit timeline.", action: api.demoClearLogs, icon: Eraser, tone: "bg-white/10 text-slate-100" },
  ];
  const execute = async (control: Control) => { if (!session) return; setRunning(control.label); try { await control.action(session.token); toast.success(`${control.label} complete`); } catch (error) { toast.error(error instanceof Error ? error.message : "Demo action failed"); } finally { setRunning(null); } };
  return <section><p className="text-sm text-emerald-300">ADMIN-ONLY OPERATIONS</p><h1 className="mt-1 text-3xl font-semibold">Demo controls</h1><p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400">Use these controls to reset the presentation state and demonstrate the traffic, signal, and emergency workflows in a predictable order.</p><div className="mt-7 grid gap-4 md:grid-cols-2 xl:grid-cols-3">{controls.map((control) => { const Icon = control.icon; return <article key={control.label} className="rounded-2xl border border-white/10 bg-[#161b22] p-5"><Icon size={20} className="text-slate-300" /><h2 className="mt-5 font-semibold">{control.label}</h2><p className="mt-2 min-h-10 text-sm leading-5 text-slate-400">{control.description}</p><button disabled={running !== null} onClick={() => void execute(control)} className={`mt-5 w-full rounded-lg px-4 py-3 text-sm font-semibold disabled:opacity-40 ${control.tone}`}>{running === control.label ? "Working…" : control.label}</button></article>; })}</div></section>;
}
