# 🎬 PulseRoute AI — Demo Walkthrough Script

---

## Step-by-Step Demo Routine for Presenters

1. **Launch Backend Server:**
   ```bash
   python -m uvicorn backend.main:app --reload
   ```

2. **Open Dashboard:**
   Open `frontend/index.html` in your web browser.

3. **Demonstrate Normal Adaptive Signal Control:**
   - Observe the **Admin Dashboard**.
   - Note the **Smart 4-Way Intersection Visualizer** drawing active green lights, live countdown timers, and vehicle counters.
   - Point out the **Explainable AI Decision Intelligence Panel** displaying total vehicle count, queue length, confidence score, and natural language reasoning.

4. **Trigger Emergency Green Corridor:**
   - Click **Ambulance HUD** button in top navbar.
   - Click **START EMERGENCY CORRIDOR**.
   - Switch back to **Admin Dashboard**.

5. **Observe System State Transition & Green Corridor Lock:**
   - Watch top banner transition from `NORMAL` ➔ `EMERGENCY_REQUESTED` ➔ `MISSION_ACTIVE` ➔ `GREEN_CORRIDOR_ACTIVE`.
   - Observe the **OpenStreetMap Pane** showing the animated ambulance 🚑 moving smoothly along the Hyderabad route towards Banjara Hills Hospital 🏥.
   - Observe the **Smart Intersection Canvas** display `CORRIDOR LOCKED 🚑` with green light override locked on the corridor lane.
   - Point out the **Timeline Audit Log** recording state switches and preemption events.

6. **Mission Completion & Restoration:**
   - Once the ambulance reaches the hospital, observe state transition to `HOSPITAL_REACHED` and then `ADAPTIVE_SCHEDULING_RESTORED`.
   - Intersection signals revert back to adaptive density scheduling.
