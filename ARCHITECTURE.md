# Architecture

## Module 1: platform core

```text
HTTP request
  -> API router (validation and response only)
  -> Auth service / State manager
  -> typed response envelope
```

`StateManager` is the in-memory, lock-protected source of truth. Future traffic, signal, emergency, analytics, and WebSocket services will read and update its named state slices instead of maintaining parallel state.

Authentication uses signed JWT bearer tokens and assigns either `ADMIN` or `AMBULANCE_DRIVER`. Route-level role guards are available for future protected routers.

## Module 2: traffic analytics

```text
Tracked observations -> RegionMapper -> TrafficService -> StateManager
                                            |
                                            v
                                     AIDecisionService
```

Observations use normalized bounding boxes. Their center is mapped to North, South, East, or West; the road pressure score combines vehicle count, estimated queue length, and average waiting time. The selected road includes a green duration, confidence value, and human-readable reason. These services are independent of YOLO and can therefore run fully offline with simulation data.

## Module 3: adaptive signals

```text
AI decision -> AdaptiveSignalService -> green -> yellow -> next adaptive green
                         |
                         +-> StateManager -> /api/signals
```

The scheduler executes once per second inside the application lifespan. Manual overrides are protected by the admin role. Emergency locks are a service-level integration point for the green-corridor module and take precedence over both adaptive and manual modes.

## Module 4: emergency dispatch

```text
Mission start -> GPS simulator -> current route junction -> GreenCorridorService -> emergency signal lock
                       |                                                |
                       +-> mission ETA/distance                          +-> adaptive restore on arrival
```

The route data is bundled in `backend/routes_data/hospital_route.json`, so no external GPS or map service is required. Both authenticated roles may start, stop, or prioritize a mission; all actions are logged in the central state manager.

## Module 5: real-time delivery

```text
StateManager -> DashboardConnectionManager -> /ws/dashboard (one snapshot per second)
      |
      +-> Timeline API / Reports API / Health API
```

The dashboard socket requires an admin JWT supplied as the `token` query parameter. The report service derives metrics directly from central state, and the timeline exposes the bounded, chronological audit log.

## Module 6: frontend foundation

```text
Login -> AuthContext -> protected admin / driver routes
                      |
                      +-> DashboardContext -> authenticated dashboard WebSocket -> live admin UI
```

The React frontend stores the signed-in session only for the browser session, separates admin and driver layouts, and uses the dashboard WebSocket as the admin UI's sole live state channel. The driver portal uses the narrow emergency API appropriate to its restricted role.

## Module 7: operational views

```text
DashboardContext -> Smart Signals visualizer -> manual signal API
                 -> Emergency map / corridor -> emergency mission API
```

The map route is a display copy of the bundled backend simulation route; operational state, ambulance position, signal status, and mission control results always remain backend-derived.

## Module 8: vision, analytics, and reporting

```text
Demo traffic API -> vision detection view -> dashboard WebSocket -> analytics charts
                                                        +-> report API -> CSV export
```

The demo control calls a deterministic backend generator rather than fabricating analytics in the browser. The visual bounding boxes are the actual observation payload returned from backend processing; charts consume the live WebSocket state, while reports are generated server-side and exported locally as CSV.
