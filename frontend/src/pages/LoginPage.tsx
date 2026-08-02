import { useState, type FormEvent } from "react";
import { motion } from "framer-motion";
import { RadioTower } from "lucide-react";
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [loading, setLoading] = useState(false);
  const submit = async (event: FormEvent) => { event.preventDefault(); setLoading(true); try { const user = await login(username, password); navigate(user.role === "ADMIN" ? "/dashboard" : "/mission", { replace: true }); } catch (error) { toast.error(error instanceof Error ? error.message : "Sign in failed"); } finally { setLoading(false); } };
  return <main className="grid min-h-screen place-items-center bg-[#0b0f19] p-5 text-slate-100"><motion.form initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} onSubmit={submit} className="w-full max-w-md rounded-2xl border border-white/10 bg-[#161b22] p-7 shadow-2xl shadow-black/30"><span className="mb-6 grid h-12 w-12 place-items-center rounded-xl bg-emerald-400 text-slate-950"><RadioTower /></span><h1 className="text-2xl font-semibold">PulseRoute AI</h1><p className="mt-2 text-sm text-slate-400">Sign in to the intelligent traffic command center.</p><label className="mt-7 block text-sm">Username<input value={username} onChange={(event) => setUsername(event.target.value)} className="mt-2 w-full rounded-lg border border-white/10 bg-[#0b0f19] px-3 py-3 outline-none ring-emerald-400 focus:ring-2" autoComplete="username" required /></label><label className="mt-4 block text-sm">Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} className="mt-2 w-full rounded-lg border border-white/10 bg-[#0b0f19] px-3 py-3 outline-none ring-emerald-400 focus:ring-2" autoComplete="current-password" required /></label><button disabled={loading} className="mt-7 w-full rounded-lg bg-emerald-400 py-3 font-semibold text-slate-950 transition hover:bg-emerald-300 disabled:opacity-60">{loading ? "Signing in…" : "Sign in"}</button><p className="mt-5 text-xs text-slate-500">Demo: admin / admin123 · driver / driver123</p></motion.form></main>;
}
