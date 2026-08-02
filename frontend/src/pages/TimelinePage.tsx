import { useEffect, useMemo, useState } from "react";
import { Search } from "lucide-react";
import toast from "react-hot-toast";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../services/api";
import type { TimelineEvent } from "../types";

export function TimelinePage() {
  const { session } = useAuth();
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [query, setQuery] = useState("");
  const [level, setLevel] = useState("ALL");
  useEffect(() => { if (!session) return; api.timeline(session.token).then(setEvents).catch((error: unknown) => toast.error(error instanceof Error ? error.message : "Unable to load timeline")); }, [session]);
  const filtered = useMemo(() => events.slice().reverse().filter((event) => (level === "ALL" || event.level === level) && event.event.toLowerCase().includes(query.toLowerCase())), [events, level, query]);
  return <section><p className="text-sm text-emerald-300">AUDIT HISTORY</p><h1 className="mt-1 text-3xl font-semibold">Timeline</h1><div className="mt-7 flex flex-wrap gap-3"><label className="flex min-w-64 flex-1 items-center gap-2 rounded-lg border border-white/10 bg-[#161b22] px-3"><Search size={16} className="text-slate-500" /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search events" className="w-full bg-transparent py-3 text-sm outline-none" /></label><select value={level} onChange={(event) => setLevel(event.target.value)} className="rounded-lg border border-white/10 bg-[#161b22] px-3 text-sm outline-none"><option value="ALL">All levels</option><option value="INFO">Info</option><option value="WARNING">Warning</option></select></div><article className="mt-5 rounded-2xl border border-white/10 bg-[#161b22] p-5">{filtered.length ? <ol className="space-y-4">{filtered.map((event) => <li key={`${event.timestamp}-${event.event}`} className="border-l-2 border-emerald-400/60 pl-4"><div className="flex flex-wrap items-center gap-x-3 gap-y-1"><p className="text-sm font-medium">{event.event}</p><span className={`text-xs ${event.level === "WARNING" ? "text-amber-300" : "text-slate-500"}`}>{event.level}</span></div><time className="mt-1 block text-xs text-slate-500">{new Date(event.timestamp).toLocaleString()}</time></li>)}</ol> : <p className="py-8 text-center text-sm text-slate-400">No events match the active filters.</p>}</article></section>;
}
