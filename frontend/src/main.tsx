import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import App from "./App";
import { AuthProvider } from "./contexts/AuthContext";
import "./styles/index.css";

createRoot(document.getElementById("root")!).render(<StrictMode><BrowserRouter><AuthProvider><App /><Toaster position="top-right" toastOptions={{ style: { background: "#161b22", color: "#e2e8f0" } }} /></AuthProvider></BrowserRouter></StrictMode>);
