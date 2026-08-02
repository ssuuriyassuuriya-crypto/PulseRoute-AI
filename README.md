# PulseRoute AI

PulseRoute AI is an offline-capable intelligent traffic-management MVP. It will combine traffic analytics, adaptive signals, and an emergency green corridor around a FastAPI backend and React control center.

## Module 1: platform core

Module 1 provides a runnable FastAPI foundation with JWT authentication, two roles (`ADMIN`, `AMBULANCE_DRIVER`), a thread-safe central state manager, standardized API envelopes, health endpoints, and tests.

Module 2 adds offline traffic observations, region mapping, congestion/queue analytics, and explainable adaptive-signal recommendations. It accepts normalized detected bounding boxes, so it can be fed by the later YOLO pipeline or deterministic demo traffic.

Module 3 adds the adaptive signal scheduler. It runs in the FastAPI lifespan, transitions green to yellow before selecting the next AI-prioritized road, supports admin manual overrides, and provides green-corridor emergency lock extension points.

Module 4 adds emergency dispatch. A bundled Bengaluru route drives an offline GPS simulator, keeps distance/ETA live, and locks each upcoming junction green until the mission reaches the hospital or is stopped.

Module 5 exposes the central state through an authenticated admin dashboard WebSocket (`/ws/dashboard?token=...`) and adds timeline, report, and detailed health APIs. The frontend can use the socket as its single live-update channel.

Module 6 adds the Vite/React/TypeScript frontend foundation. It includes responsive role-protected layouts, the dark control-center visual system, JWT session login, a resilient admin WebSocket context, a live dashboard, and a driver mission portal.

Module 7 adds the operational Smart Signals and Emergency Dispatch views. The intersection renders each live light state and supports safe manual override; dispatch renders the bundled route on OpenStreetMap tiles, animates current ambulance location, and exposes live mission controls.

Module 8 adds a deterministic Traffic Vision demo that exercises the vehicle-to-analytics pipeline, live Recharts road analysis, and a downloadable CSV performance report.

Module 9 adds admin-only Demo Controls, searchable timeline viewing, and the final API, demo, and technical-decision documents for a repeatable presentation workflow.

Module 10 adds an optional real YOLOv8/ByteTrack ingestion path. Admins can upload MP4, AVI, MOV, or MKV video; OpenCV samples frames in a background worker, YOLO tracks supported vehicle classes, and the resulting observations update the same analytics pipeline. Place `yolov8n.pt` in `backend/models/` (or set `PULSEROUTE_VISION_MODEL_PATH`) to enable it.

### Run the frontend

```powershell
cd frontend
npm install
npm run dev
```

The development server defaults to `http://127.0.0.1:5173` and expects the backend at `http://127.0.0.1:8000`. Set `VITE_API_BASE_URL` to point to a different backend API origin. The backend already permits these local frontend origins through CORS.

### Run locally

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn app.main:app --reload --reload-dir app --reload-dir routes_data --reload-exclude .venv
```

Open `http://127.0.0.1:8000/docs` for OpenAPI documentation.

### Demo accounts

| Role | Username | Password |
| --- | --- | --- |
| Administrator | `admin` | `admin123` |
| Ambulance driver | `driver` | `driver123` |

### Current endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/api/auth/login` | Obtain a bearer token |
| GET | `/api/auth/me` | Validate the current token |
| GET | `/api/health` | Platform health snapshot |
| GET | `/api/status` | Alias for health snapshot |
| POST | `/api/traffic/observations` | Process tracked-vehicle observations (admin) |
| POST | `/api/traffic/demo` | Generate a deterministic demo traffic frame (admin) |
| GET | `/api/traffic/snapshot` | Read live road state (admin) |
| GET | `/api/analytics` | Read analytics and AI decision (admin) |
| GET | `/api/signals` | Read and refresh the live signal state (admin) |
| POST | `/api/signals/override` | Set a temporary manual green signal (admin) |
| POST | `/api/signals/reset` | Return immediately to adaptive timing (admin) |
| GET | `/api/emergency/status` | Read mission, GPS, and corridor state |
| POST | `/api/emergency/start` | Start a simulated emergency mission |
| POST | `/api/emergency/stop` | Complete the active emergency mission |
| POST | `/api/emergency/priority` | Escalate the active mission to high priority |
| GET | `/api/timeline` | Read the audit timeline (admin) |
| GET | `/api/reports` | Generate current performance metrics (admin) |
| GET | `/api/health/model` | Read vision-model health state |
| GET | `/api/health/websocket` | Read dashboard socket health and connection count |
| WS | `/ws/dashboard?token=<JWT>` | Receive the full live dashboard state (admin) |
