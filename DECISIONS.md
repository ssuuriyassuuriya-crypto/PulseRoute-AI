# 💡 PulseRoute AI — Architectural Decision Records (ADRs)

---

## ADR 001: Thread-Safe Singleton State Manager
- **Context:** The system requires real-time coordination between YOLO video ingestion, signal orchestration loops, and emergency GPS telemetry.
- **Decision:** Implemented `StateManager` as a thread-safe Singleton using `threading.RLock()`.
- **Consequences:** Eliminates race conditions across async WebSocket threads and background simulation loops while keeping system state predictable.

---

## ADR 002: Unified WebSockets Endpoint (`/ws/dashboard`)
- **Context:** Previous design used fragmented HTTP polling across separate endpoints for traffic signals, video counts, and ambulance location.
- **Decision:** Unified all real-time streams into a single WebSocket endpoint `/ws/dashboard`.
- **Consequences:** Reduces network overhead, enables instant UI updates under 100ms, and simplifies client synchronization.

---

## ADR 003: Haversine Preemption Zone for Emergency Corridor
- **Context:** Emergency light locking should occur ahead of approaching ambulances without permanently locking distant intersections.
- **Decision:** Set a 1.5 km dynamic Haversine distance threshold to lock signals GREEN and automatically release locks once the vehicle passes (distance < 0.05 km).
- **Consequences:** Provides smooth green wave preemption without stalling cross-traffic unnecessarily.
