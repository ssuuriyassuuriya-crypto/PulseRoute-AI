import { useEffect, useState } from "react";
import { Download, FileText } from "lucide-react";
import toast from "react-hot-toast";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../services/api";
import type { ReportData } from "../types";

export function ReportsPage() {
  const { session } = useAuth();
  const [report, setReport] = useState<ReportData | null>(null);
  const refresh = async () => { if (!session) return; try { setReport(await api.report(session.token)); } catch (error) { toast.error(error instanceof Error ? error.message : "Unable to load report"); } };
  useEffect(() => { void refresh(); }, [session]);
  const exportCsv = () => { if (!report) return; const csv = Object.entries(report).map(([key, value]) => `${key},${value}`).join("\n"); const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" })); const anchor = document.createElement("a"); anchor.href = url; anchor.download = "pulseroute-report.csv"; anchor.click(); URL.revokeObjectURL(url); };
  const items = report ? [{ label: "Vehicles processed", value: report.vehicles_processed }, { label: "Average wait", value: `${report.average_wait_seconds}s` }, { label: "Delay saved", value: `${report.delay_saved_seconds}s` }, { label: "Signal utilization", value: report.signal_utilization }, { label: "Corridor activations", value: report.green_corridor_activations }, { label: "Mission status", value: report.mission_status }] : [];
  return <section><div className="flex flex-wrap items-end justify-between gap-4"><div><p className="text-sm text-emerald-300">OPERATIONAL REPORTING</p><h1 className="mt-1 text-3xl font-semibold">Reports</h1></div><button disabled={!report} onClick={exportCsv} className="inline-flex items-center gap-2 rounded-lg bg-emerald-400 px-4 py-3 font-semibold text-slate-950 disabled:opacity-50"><Download size={17} />Download CSV</button></div><article className="mt-7 rounded-2xl border border-white/10 bg-[#161b22] p-6"><div className="flex items-center gap-2"><FileText className="text-sky-300" /><h2 className="font-semibold">Current performance summary</h2></div>{report ? <><p className="mt-2 text-sm text-slate-400">Generated {new Date(report.generated_at).toLocaleString()}</p><div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">{items.map((item) => <div key={item.label} className="rounded-xl bg-white/5 p-4"><p className="text-sm text-slate-400">{item.label}</p><p className="mt-2 text-2xl font-semibold">{item.value}</p></div>)}</div></> : <p className="mt-6 text-sm text-slate-400">Loading report data…</p>}</article></section>;
}
