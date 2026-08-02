export function StatusPill({ status }: { status: string }) {
  const color = status === "connected" || status === "healthy" || status === "GREEN" ? "bg-emerald-400" : status === "reconnecting" || status === "YELLOW" ? "bg-amber-400" : "bg-rose-500";
  return <span className="inline-flex items-center gap-2 rounded-full bg-white/5 px-3 py-1 text-xs font-medium text-slate-200"><span className={`h-2 w-2 rounded-full ${color}`} />{status}</span>;
}
