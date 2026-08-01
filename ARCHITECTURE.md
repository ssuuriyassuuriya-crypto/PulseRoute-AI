# 🏗️ PulseRoute AI — System Architecture (v3.0)

PulseRoute AI is designed as a modular, decoupled Intelligent Traffic Management System (ITMS).

---

## 1. Centralized System State Machine

The system core operates as a thread-safe global singleton state manager (`backend/state/state_manager.py`) transitioning between 6 key states:

```
[NORMAL]
   │ (Traffic monitoring & adaptive density cycle)
   ▼
[EMERGENCY_REQUESTED]
   │ (Ambulance driver logs mission & target hospital)
   ▼
[MISSION_ACTIVE]
   │ (GPS tracking connected & route loaded)
   ▼
[GREEN_CORRIDOR_ACTIVE]
   │ (Preemptive green light lock on upcoming junction)
   ▼
[HOSPITAL_REACHED]
   │ (Ambulance clears final corridor junction)
   ▼
[ADAPTIVE_SCHEDULING_RESTORED]
   │ (Locks released; returns to NORMAL)
```

---

## 2. Information Pipelines

### A. Traffic Analytics Pipeline
```text
[Video Stream / Camera] ──► [YOLOv8 Detection] ──► [ByteTrack Tracking] ──► [Region Mapping N/S/E/W]
                                                                                      │
                                                                                      ▼
[Dashboard UI] ◄── [Unified WebSockets /ws/dashboard] ◄── [Orchestration Service] ◄── [Road Analytics Engine]
```

### B. Emergency Green Corridor Pipeline
```text
[Ambulance Driver HUD] ──► [Emergency Dispatch API] ──► [GPS Simulator / Telemetry]
                                                                    │
                                                                    ▼
[Leaflet Map / Signal Locks] ◄── [WebSockets Broadcast] ◄── [Green Corridor Preemption]
```

---

## 3. Module Hierarchy

- `backend/constants/`: Single source of truth for thresholds, timings, and routes.
- `backend/state/`: Thread-safe global singleton state manager.
- `backend/services/`: Decoupled business logic services (YOLO, Analytics, Orchestration, Green Corridor, Emergency, Simulation, Report, Timeline).
- `backend/api/`: REST API route controllers.
- `backend/main.py`: FastAPI application entry point & `/ws/dashboard` WebSocket server.
- `frontend/`: Carbon dark single-page web app with HTML5 Canvas intersection visualizer & Leaflet OpenStreetMap renderer.
