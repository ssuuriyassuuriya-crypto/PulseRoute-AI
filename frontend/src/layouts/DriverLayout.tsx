import { LogOut, Siren } from "lucide-react";
import { Outlet } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export function DriverLayout() {
  const { logout, session } = useAuth();
  return <main className="min-h-screen bg-[#0b0f19] p-5 text-slate-100 sm:p-8"><header className="mx-auto mb-8 flex max-w-2xl items-center justify-between"><div className="flex items-center gap-3"><span className="grid h-11 w-11 place-items-center rounded-xl bg-rose-500 text-white"><Siren /></span><div><p className="font-semibold">Driver Mission</p><p className="text-xs text-slate-400">{session?.user.username}</p></div></div><button aria-label="Sign out" onClick={logout} className="rounded-lg border border-white/10 p-3 text-slate-300"><LogOut size={18} /></button></header><div className="mx-auto max-w-2xl"><Outlet /></div></main>;
}
