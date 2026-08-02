import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./contexts/AuthContext";
import { DashboardProvider } from "./contexts/DashboardContext";
import { AdminLayout } from "./layouts/AdminLayout";
import { DriverLayout } from "./layouts/DriverLayout";
import { LoginPage } from "./pages/LoginPage";

const DashboardPage = lazy(() => import("./pages/DashboardPage").then((module) => ({ default: module.DashboardPage })));
const TrafficVisionPage = lazy(() => import("./pages/TrafficVisionPage").then((module) => ({ default: module.TrafficVisionPage })));
const AnalyticsPage = lazy(() => import("./pages/AnalyticsPage").then((module) => ({ default: module.AnalyticsPage })));
const ReportsPage = lazy(() => import("./pages/ReportsPage").then((module) => ({ default: module.ReportsPage })));
const TimelinePage = lazy(() => import("./pages/TimelinePage").then((module) => ({ default: module.TimelinePage })));
const DemoControlsPage = lazy(() => import("./pages/DemoControlsPage").then((module) => ({ default: module.DemoControlsPage })));
const DriverMissionPage = lazy(() => import("./pages/DriverMissionPage").then((module) => ({ default: module.DriverMissionPage })));
const EmergencyDispatchPage = lazy(() => import("./pages/EmergencyDispatchPage").then((module) => ({ default: module.EmergencyDispatchPage })));
const LiveDataPage = lazy(() => import("./pages/LiveDataPage").then((module) => ({ default: module.LiveDataPage })));
const SmartSignalsPage = lazy(() => import("./pages/SmartSignalsPage").then((module) => ({ default: module.SmartSignalsPage })));

function Protected({ role, children }: { role: "ADMIN" | "AMBULANCE_DRIVER"; children: React.ReactNode }) { const { session } = useAuth(); return !session ? <Navigate to="/login" replace /> : session.user.role !== role ? <Navigate to={session.user.role === "ADMIN" ? "/dashboard" : "/mission"} replace /> : <>{children}</>; }

export default function App() { return <DashboardProvider><Suspense fallback={<main className="grid min-h-screen place-items-center bg-[#0b0f19] text-slate-400">Loading operational view…</main>}><Routes><Route path="/login" element={<LoginPage />} /><Route path="/" element={<Navigate to="/dashboard" replace />} /><Route path="/dashboard" element={<Protected role="ADMIN"><AdminLayout /></Protected>}><Route index element={<DashboardPage />} /></Route><Route path="/traffic" element={<Protected role="ADMIN"><AdminLayout /></Protected>}><Route index element={<TrafficVisionPage />} /></Route><Route path="/signals" element={<Protected role="ADMIN"><AdminLayout /></Protected>}><Route index element={<SmartSignalsPage />} /></Route><Route path="/emergency" element={<Protected role="ADMIN"><AdminLayout /></Protected>}><Route index element={<EmergencyDispatchPage />} /></Route><Route path="/analytics" element={<Protected role="ADMIN"><AdminLayout /></Protected>}><Route index element={<AnalyticsPage />} /></Route><Route path="/reports" element={<Protected role="ADMIN"><AdminLayout /></Protected>}><Route index element={<ReportsPage />} /></Route><Route path="/timeline" element={<Protected role="ADMIN"><AdminLayout /></Protected>}><Route index element={<TimelinePage />} /></Route><Route path="/demo" element={<Protected role="ADMIN"><AdminLayout /></Protected>}><Route index element={<DemoControlsPage />} /></Route><Route path="/mission" element={<Protected role="AMBULANCE_DRIVER"><DriverLayout /></Protected>}><Route index element={<DriverMissionPage />} /></Route><Route path="*" element={<Navigate to="/" replace />} /></Routes></Suspense></DashboardProvider>; }
