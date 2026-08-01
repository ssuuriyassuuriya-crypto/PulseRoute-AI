# 🔌 PulseRoute AI — API Specification

Base URL: `http://localhost:8000`  
WebSocket URL: `ws://localhost:8000/ws/dashboard`

---

## 1. Authentication Endpoints

### `POST /api/auth/login`
Authenticates users and returns JWT access tokens.
- **Request Body:**
  ```json
  {
    "username": "admin",
    "password": "admin123"
  }
  ```
- **Response:**
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "role": "ADMIN",
    "username": "admin",
    "name": "Traffic Control Officer"
  }
  ```

---

## 2. Traffic Analytics Endpoints

### `POST /api/traffic/upload`
Uploads traffic video for YOLO analytics.

### `GET /api/traffic/detect/{junction_id}`
Returns live vehicle detections and 4-region counts.

### `GET /api/analytics/junction/{junction_id}`
Returns Explainable AI metrics (selected lane, allocated duration, queue length, wait index, confidence, reasoning).

---

## 3. Emergency Dispatch Endpoints

### `POST /api/emergency/start`
Triggers an emergency green corridor mission.
- **Request Body:**
  ```json
  {
    "driver_id": "driver",
    "vehicle_plate": "TS-09-EMS-108",
    "start_junction_id": "J1_BEGUMPET",
    "destination_junction_id": "J3_BANJARA_HILLS"
  }
  ```

### `POST /api/emergency/stop`
Ends active emergency corridor and restores normal scheduling.

### `GET /api/emergency/status`
Returns current system state, active mission, and ambulance GPS telemetry.

---

## 4. WebSockets Protocol (`/ws/dashboard`)

Subscribers receive real-time JSON payloads:
```json
{
  "type": "LATEST_UPDATE",
  "timestamp": 1740000000,
  "data": {
    "system_state": "GREEN_CORRIDOR_ACTIVE",
    "junctions": { ... },
    "active_mission": { ... },
    "ambulance_gps": { ... },
    "timeline_events": [ ... ]
  }
}
```
