import { useDashboard } from "../contexts/DashboardContext";

export function LiveDataPage({ title, description }: { title: string; description: string }) {
  const { state } = useDashboard();
  return <section><p className="text-sm text-emerald-300">LIVE OPERATIONS</p><h1 className="mt-1 text-3xl font-semibold">{title}</h1><p className="mt-3 max-w-2xl text-slate-400">{description}</p><pre className="mt-7 max-h-[34rem] overflow-auto rounded-xl border border-white/10 bg-[#161b22] p-5 text-xs leading-6 text-slate-300">{JSON.stringify(state ?? { status: "Connecting to live state" }, null, 2)}</pre></section>;
}
