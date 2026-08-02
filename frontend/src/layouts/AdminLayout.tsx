import { Ambulance, BarChart3, LayoutDashboard, LogOut, RadioTower, TrafficCone, Video, FileText, ListTree, SlidersHorizontal } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";
import { StatusPill } from "../components/StatusPill";
import { useAuth } from "../contexts/AuthContext";
import { useDashboard } from "../contexts/DashboardContext";

const links = [
  { to: "/dashboard", label: "Mission Control", icon: LayoutDashboard },
  { to: "/traffic", label: "Traffic Vision", icon: Video },
  { to: "/signals", label: "Smart Signals", icon: TrafficCone },
  { to: "/emergency", label: "Emergency Dispatch", icon: Ambulance },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/reports", label: "Reports", icon: FileText },
  { to: "/timeline", label: "Timeline", icon: ListTree },
  { to: "/demo", label: "Demo Controls", icon: SlidersHorizontal },
];

export function AdminLayout() {
  const { logout, session } = useAuth();
  const { connection } = useDashboard();
  return <div className="min-h-screen bg-[#0b0f19] text-slate-100 lg:grid lg:grid-cols-[17rem_1fr]">
    <aside className="border-b border-white/10 bg-[#101722] p-5 lg:border-b-0 lg:border-r">
      <div className="mb-8 flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-emerald-400 text-slate-950"><RadioTower size={22} /></span><div><p className="font-semibold">PulseRoute AI</p><p className="text-xs text-slate-400">Traffic command center</p></div></div>
      <nav className="grid grid-cols-2 gap-2 lg:grid-cols-1">{links.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} className={({ isActive }) => `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition ${isActive ? "bg-emerald-400/15 text-emerald-300" : "text-slate-400 hover:bg-white/5 hover:text-white"}`}><Icon size={17} />{label}</NavLink>)}</nav>
      <button onClick={logout} className="mt-6 flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-slate-400 hover:bg-white/5 hover:text-white"><LogOut size={17} />Sign out</button>
    </aside>
    <main><header className="flex items-center justify-between border-b border-white/10 px-5 py-4 lg:px-8"><div><p className="text-sm text-slate-400">Signed in as {session?.user.username}</p><p className="font-semibold">Administrator</p></div><StatusPill status={connection} /></header><div className="p-5 lg:p-8"><Outlet /></div></main>
  </div>;
}
