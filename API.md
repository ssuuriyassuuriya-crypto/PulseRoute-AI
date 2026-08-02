# PulseRoute AI API

All REST responses use `{ "success": true, "message": "", "data": ... }`. Send a JWT as `Authorization: Bearer <token>` for protected endpoints.

## Authentication

| Method | Path | Access | Purpose |
| --- | --- | --- | --- |
| POST | `/api/auth/login` | Public | Returns an access token for `admin` or `driver`. |
| GET | `/api/auth/me` | Authenticated | Returns the token identity and role. |

## Traffic and signals

| Method | Path | Access | Purpose |
| --- | --- | --- | --- |
| POST | `/api/traffic/observations` | Admin | Process normalized tracked observations. |
| POST | `/api/traffic/demo` | Admin | Generate deterministic offline demo traffic. |
| POST | `/api/traffic/upload` | Admin | Queue an MP4, AVI, MOV, or MKV for background vision processing. |
| GET | `/api/traffic/video` | Admin | Read video job and vision-model status. |
| GET | `/api/traffic/snapshot` | Admin | Read live road data. |
| GET | `/api/analytics` | Admin | Read metrics and explainable AI decision. |
| GET | `/api/signals` | Admin | Read live signal state. |
| POST | `/api/signals/override` | Admin | Set `{road, duration_seconds}` manual green. |
| POST | `/api/signals/reset` | Admin | Restore adaptive mode. |

## Emergency and operations

| Method | Path | Access | Purpose |
| --- | --- | --- | --- |
| GET | `/api/emergency/status` | Authenticated | Mission, GPS, and corridor snapshot. |
| POST | `/api/emergency/start` | Authenticated | Start a route simulation. |
| POST | `/api/emergency/stop` | Authenticated | Complete active simulation. |
| POST | `/api/emergency/priority` | Authenticated | Escalate active mission. |
| GET | `/api/timeline` | Admin | Bounded audit log. |
| GET | `/api/reports` | Admin | Generated operational report. |
| POST | `/api/demo/*` | Admin | Presentation-only traffic/emergency/reset controls. |

## Health and real time

`GET /api/health`, `/api/status`, `/api/health/model`, and `/api/health/websocket` expose service health. Admin dashboards connect to `WS /ws/dashboard?token=<JWT>`; it emits the whole live state snapshot once per second.
