# Technical Decisions

## Offline-first simulation

The MVP uses a bundled route and deterministic traffic observations. This keeps the demo operational without GPS hardware, external traffic feeds, or a computer-vision model download.

## Central state manager

All domain services update a lock-protected in-memory state manager. REST endpoints, reports, and the dashboard WebSocket read from this one source to prevent competing live-state caches.

## Role boundaries

Admins receive the full dashboard WebSocket and operational controls. Ambulance drivers receive only the mission functions permitted by the backend role policy.

## Safe signal behavior

Adaptive phases always move through yellow before a new green. Green-corridor locks take precedence over manual and adaptive modes, and release returns control to the scheduler.

## Incremental frontend loading

Operational routes use lazy loading. This keeps the Leaflet map and analytics chart libraries out of the initial login/dashboard bundle.
