import { useEffect, useState } from "react";
import { Ambulance, MapPin, Navigation, Siren, Timer } from "lucide-react";
import toast from "react-hot-toast";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../services/api";
import type { EmergencySnapshot } from "../types";

export function DriverMissionPage() {
  const { session } = useAuth();
  const [snapshot, setSnapshot] = useState<EmergencySnapshot | null>(null);
  const [busy, setBusy] = useState(false);
  const refresh = async () => { if (!session) return; try { setSnapshot(await api.emergencyStatus(session.token)); } catch (error) { toast.error(error instanceof Error ? error.message : "Unable to refresh mission"); } };
  useEffect(() => { void refresh(); const interval = window.setInterval(() => void refresh(), 3_000); return () => window.clearInterval(interval); }, [session]);
  const perform = async (action: () => Promise<EmergencySnapshot>) => { setBusy(true); try { setSnapshot(await action()); } catch (error) { toast.error(error instanceof Error ? error.message : "Mission action failed"); } finally { setBusy(false); } };
  const mission = snapshot?.mission;
  const gps = snapshot?.gps;
  return <section><p className="text-sm text-rose-300">EMERGENCY RESPONSE</p><h1 className="mt-1 text-3xl font-semibold">Mission status</h1><article className="mt-6 rounded-2xl border border-white/10 bg-[#161b22] p-6"><div className="flex items-start justify-between"><div><p className="text-sm text-slate-400">{mission?.mission_id ?? "No active mission"}</p><p className="mt-1 text-xl font-semibold">{mission?.status ?? "READY"}</p></div><Siren className={mission?.status === "ACTIVE" ? "text-rose-400" : "text-slate-500"} /></div><div className="mt-7 grid gap-4 sm:grid-cols-2"><Metric icon={MapPin} label="Destination" value={mission?.hospital ?? "PulseCare General Hospital"} /><Metric icon={Timer} label="ETA" value={mission ? `${Math.ceil(mission.eta_seconds / 60)} min` : "—"} /><Metric icon={Navigation} label="Distance" value={mission ? `${(mission.distance_meters / 1000).toFixed(1)} km` : "—"} /><Metric icon={Ambulance} label="Current junction" value={gps?.current_junction ?? "Awaiting mission"} /></div><div className="mt-7 grid gap-3 sm:grid-cols-3"><button disabled={busy || mission?.status === "ACTIVE"} onClick={() => session && perform(() => api.startMission(session.token))} className="rounded-xl bg-rose-500 px-4 py-4 font-semibold text-white disabled:opacity-40">Start emergency</button><button disabled={busy || mission?.status !== "ACTIVE"} onClick={() => session && perform(() => api.requestPriority(session.token))} className="rounded-xl bg-amber-400 px-4 py-4 font-semibold text-slate-950 disabled:opacity-40">Request priority</button><button disabled={busy || mission?.status !== "ACTIVE"} onClick={() => session && perform(() => api.stopMission(session.token))} className="rounded-xl border border-white/15 px-4 py-4 font-semibold disabled:opacity-40">Stop mission</button></div></article>{snapshot?.corridor.length ? <article className="mt-5 rounded-2xl border border-white/10 bg-[#161b22] p-6"><h2 className="font-semibold">Green corridor</h2><div className="mt-4 space-y-3">{snapshot.corridor.map((point) => <div key={point.junction} className="flex items-center justify-between rounded-lg bg-white/5 px-4 py-3"><span className="text-sm">{point.junction}</span><span className={`text-xs font-semibold ${point.status === "GREEN" ? "text-emerald-300" : "text-slate-400"}`}>{point.status}</span></div>)}</div></article> : null}</section>;
}

function Metric({ icon: Icon, label, value }: { icon: typeof MapPin; label: string; value: string }) { return <div className="rounded-xl bg-white/5 p-4"><Icon size={17} className="text-emerald-300" /><p className="mt-3 text-xs text-slate-400">{label}</p><p className="mt-1 text-sm font-medium">{value}</p></div>; }
