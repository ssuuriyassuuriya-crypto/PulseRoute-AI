/**
 * PulseRoute AI System (v3.0) - Fast & Responsive Simulation Engine
 */

const API_BASE = "http://127.0.0.1:8000";
const WS_URL = "ws://127.0.0.1:8000/ws/dashboard";

let ws = null;
let map = null;
let ambulanceMarker = null;
let routePolyline = null;
let pollingInterval = null;

// Global State Object
let state = {
  system_state: "NORMAL",
  junctions: {
    "J1_BEGUMPET": {
      name: "Begumpet Junction",
      counts: { NORTH: 14, SOUTH: 9, EAST: 24, WEST: 16 },
      active_green: "EAST",
      remaining_seconds: 15,
      is_locked: false
    },
    "J2_PANJAGUTTA": {
      name: "Panjagutta Circle",
      counts: { NORTH: 19, SOUTH: 28, EAST: 15, WEST: 11 },
      active_green: "SOUTH",
      remaining_seconds: 20,
      is_locked: false
    },
    "J3_BANJARA_HILLS": {
      name: "Banjara Hills Hospital Gate",
      counts: { NORTH: 6, SOUTH: 12, EAST: 9, WEST: 7 },
      active_green: "NORTH",
      remaining_seconds: 12,
      is_locked: false
    }
  },
  active_mission: null,
  ambulance_gps: {
    is_active: false,
    latitude: 17.4447,
    longitude: 78.4664,
    speed_kmh: 0,
    progress_percentage: 0,
    current_junction_id: "J1_BEGUMPET",
    next_junction_id: "J2_PANJAGUTTA",
    distance_to_next_km: 2.1,
    eta_seconds: 120
  },
  timeline_events: [
    { timestamp: new Date().toLocaleTimeString(), category: "SYSTEM", message: "PulseRoute AI Dashboard Engine Ready" }
  ]
};

// Waypoints from Begumpet to Banjara Hills Hospital
const WAYPOINTS = [
  [17.4447, 78.4664], // J1 Begumpet
  [17.4410, 78.4630],
  [17.4350, 78.4580],
  [17.4256, 78.4513], // J2 Panjagutta
  [17.4210, 78.4470],
  [17.4156, 78.4412]  // J3 Banjara Hills Hospital Gate
];

// Initialize App on DOM Load
document.addEventListener("DOMContentLoaded", () => {
  initMap();
  connectWebSocket();
  setupEventListeners();
  startLivePollingLoop();
});

// Setup WebSockets Connection
function connectWebSocket() {
  const wsStatusEl = document.getElementById("ws-status");
  try {
    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      if (wsStatusEl) {
        wsStatusEl.className = "pulse-dot green";
        wsStatusEl.title = "Connected to PulseRoute Real-time Engine";
      }
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "INITIAL_STATE" || msg.type === "LATEST_UPDATE") {
          updateState(msg.data);
        }
      } catch (err) {
        console.error("WS Message Error:", err);
      }
    };

    ws.onclose = () => {
      if (wsStatusEl) {
        wsStatusEl.className = "pulse-dot yellow";
        wsStatusEl.title = "Falling back to HTTP Live Stream";
      }
      setTimeout(connectWebSocket, 5000);
    };

    ws.onerror = () => {
      if (wsStatusEl) {
        wsStatusEl.className = "pulse-dot yellow";
      }
    };
  } catch (e) {
    console.log("WebSocket fallback active");
  }
}

// Start Continuous Live Polling Loop (Ticks every 1s)
function startLivePollingLoop() {
  fetchLiveData();
  pollingInterval = setInterval(fetchLiveData, 1000);
}

async function fetchLiveData() {
  try {
    const res = await fetch(`${API_BASE}/api/emergency/status`);
    if (res.ok) {
      const data = await res.json();
      if (data.system_state && state.ambulance_gps.is_active === false) {
        state.system_state = data.system_state;
      }
    }

    tickLocalSimulation();
    renderAllViews();
  } catch (e) {
    tickLocalSimulation();
    renderAllViews();
  }
}

// Local simulation tick for smooth fast animations (~10 sec trip to hospital)
function tickLocalSimulation() {
  // Tick signal countdown timers
  Object.keys(state.junctions).forEach(jId => {
    const j = state.junctions[jId];
    if (!j.is_locked) {
      j.remaining_seconds -= 1;
      if (j.remaining_seconds <= 0) {
        const lanes = ["NORTH", "SOUTH", "EAST", "WEST"];
        const currIdx = lanes.indexOf(j.active_green);
        j.active_green = lanes[(currIdx + 1) % 4];
        j.remaining_seconds = Math.floor(Math.random() * 15) + 15;
        
        state.timeline_events.unshift({
          timestamp: new Date().toLocaleTimeString(),
          category: "SIGNAL_SWITCH",
          message: `${j.name}: Switched green phase to ${j.active_green}`
        });
        if (state.timeline_events.length > 25) state.timeline_events.pop();
      }
    }
  });

  // Fast Ambulance simulation (~10 seconds to cover 100% route)
  if (state.ambulance_gps && state.ambulance_gps.is_active) {
    const gps = state.ambulance_gps;
    // Advance by 10% each second (Reaches hospital in exactly 10 seconds)
    gps.progress_percentage = Math.min(100, (gps.progress_percentage || 0) + 10);
    gps.speed_kmh = 68.0 + Math.random() * 8.0;
    
    const totalDistance = 5.4;
    const remainingKm = Math.max(0, totalDistance * (1.0 - (gps.progress_percentage / 100.0)));
    gps.distance_to_next_km = remainingKm.toFixed(1);
    gps.eta_seconds = Math.ceil((remainingKm / 60.0) * 3600);

    // Calculate Lat/Lng along route waypoints
    const totalSegments = WAYPOINTS.length - 1;
    const currentProgressFrac = (gps.progress_percentage / 100.0) * totalSegments;
    const segIdx = Math.min(totalSegments - 1, Math.floor(currentProgressFrac));
    const segPct = currentProgressFrac - segIdx;
    
    gps.latitude = WAYPOINTS[segIdx][0] + (WAYPOINTS[segIdx+1][0] - WAYPOINTS[segIdx][0]) * segPct;
    gps.longitude = WAYPOINTS[segIdx][1] + (WAYPOINTS[segIdx+1][1] - WAYPOINTS[segIdx][1]) * segPct;

    // Phase 1: Lock Panjagutta Circle (J2) when 20% to 70%
    if (gps.progress_percentage >= 20 && gps.progress_percentage < 70) {
      state.system_state = "GREEN_CORRIDOR_ACTIVE";
      state.junctions["J2_PANJAGUTTA"].is_locked = true;
      state.junctions["J2_PANJAGUTTA"].active_green = "SOUTH";
    }
    
    // Phase 2: Lock Hospital Gate (J3) when >= 70%
    if (gps.progress_percentage >= 70 && gps.progress_percentage < 100) {
      state.junctions["J2_PANJAGUTTA"].is_locked = false;
      state.junctions["J3_BANJARA_HILLS"].is_locked = true;
      state.junctions["J3_BANJARA_HILLS"].active_green = "NORTH";
    }

    // Phase 3: Reached Hospital at 100%
    if (gps.progress_percentage >= 100) {
      gps.latitude = 17.4156;
      gps.longitude = 78.4412;
      gps.is_active = false;
      gps.speed_kmh = 0;
      gps.eta_seconds = 0;
      
      state.system_state = "HOSPITAL_REACHED";
      state.junctions["J2_PANJAGUTTA"].is_locked = false;
      state.junctions["J3_BANJARA_HILLS"].is_locked = false;

      state.timeline_events.unshift({
        timestamp: new Date().toLocaleTimeString(),
        category: "HOSPITAL_REACHED",
        message: "🏥 Ambulance arrived at Banjara Hills Hospital Gate! Patient handoff in progress."
      });

      // Automatically restore adaptive scheduling after 3 seconds
      setTimeout(() => {
        state.system_state = "ADAPTIVE_SCHEDULING_RESTORED";
        state.timeline_events.unshift({
          timestamp: new Date().toLocaleTimeString(),
          category: "SYSTEM_RESTORED",
          message: "Green corridor released. Adaptive signal scheduling restored (NORMAL)."
        });
        setTimeout(() => {
          state.system_state = "NORMAL";
        }, 2000);
      }, 3000);
    }
  }
}

// Centralized State Update Handler
function updateState(newData) {
  if (!newData) return;
  if (newData.system_state && !state.ambulance_gps.is_active) state.system_state = newData.system_state;
  if (newData.junctions) state.junctions = newData.junctions;
  if (newData.active_mission !== undefined) state.active_mission = newData.active_mission;

  renderAllViews();
}

function renderAllViews() {
  renderSystemStateBanner();
  renderIntersectionCanvas();
  renderExplainableAI();
  renderMapData();
  renderAmbulanceHUD();
  renderTimeline();
}

// Render System State Banner
function renderSystemStateBanner() {
  const stateBadge = document.getElementById("system-state-badge");
  if (!stateBadge) return;

  stateBadge.innerText = state.system_state;

  switch (state.system_state) {
    case "NORMAL":
    case "ADAPTIVE_SCHEDULING_RESTORED":
      stateBadge.className = "px-3 py-1 rounded-full text-xs font-bold bg-blue-900/60 text-blue-300 border border-blue-500";
      break;
    case "EMERGENCY_REQUESTED":
    case "MISSION_ACTIVE":
      stateBadge.className = "px-3 py-1 rounded-full text-xs font-bold bg-yellow-900/60 text-yellow-300 border border-yellow-500 animate-pulse";
      break;
    case "GREEN_CORRIDOR_ACTIVE":
      stateBadge.className = "px-3 py-1 rounded-full text-xs font-bold bg-emerald-900/60 text-emerald-300 border border-emerald-400 animate-pulse";
      break;
    case "HOSPITAL_REACHED":
      stateBadge.className = "px-3 py-1 rounded-full text-xs font-bold bg-purple-900/60 text-purple-300 border border-purple-400 animate-pulse";
      break;
    default:
      stateBadge.className = "px-3 py-1 rounded-full text-xs font-bold bg-slate-800 text-slate-300";
  }
}

// Render Smart 4-Way Intersection Canvas Visualizer
function renderIntersectionCanvas() {
  const canvas = document.getElementById("intersection-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;

  // Clear canvas
  ctx.fillStyle = "#0f172a";
  ctx.fillRect(0, 0, width, height);

  // Draw Roads
  ctx.fillStyle = "#1e293b";
  const roadWidth = 110;
  const cx = width / 2;
  const cy = height / 2;

  // Vertical Road (North-South)
  ctx.fillRect(cx - roadWidth / 2, 0, roadWidth, height);
  // Horizontal Road (East-West)
  ctx.fillRect(0, cy - roadWidth / 2, width, roadWidth);

  // Yellow Center Markings
  ctx.strokeStyle = "#eab308";
  ctx.lineWidth = 2;
  ctx.setLineDash([8, 8]);

  // N-S Center lines
  ctx.beginPath();
  ctx.moveTo(cx, 0); ctx.lineTo(cx, cy - roadWidth / 2);
  ctx.moveTo(cx, cy + roadWidth / 2); ctx.lineTo(cx, height);
  ctx.stroke();

  // E-W Center lines
  ctx.beginPath();
  ctx.moveTo(0, cy); ctx.lineTo(cx - roadWidth / 2, cy);
  ctx.moveTo(cx + roadWidth / 2, cy); ctx.lineTo(width, cy);
  ctx.stroke();
  ctx.setLineDash([]);

  // Selected Junction Data (Default to J1)
  const currentJunctionId = document.getElementById("junction-select")?.value || "J1_BEGUMPET";
  const jData = state.junctions[currentJunctionId] || {
    name: "Begumpet Junction",
    counts: { NORTH: 14, SOUTH: 9, EAST: 24, WEST: 16 },
    active_green: "EAST",
    remaining_seconds: 20,
    is_locked: false
  };

  const greenLane = jData.active_green;
  const isLocked = jData.is_locked;

  // Draw Signal Bulbs & Vehicle Count Badges
  const lanes = [
    { name: "NORTH", x: cx, y: cy - roadWidth / 2 - 25, textX: cx - 35, textY: cy - roadWidth / 2 - 40 },
    { name: "SOUTH", x: cx, y: cy + roadWidth / 2 + 25, textX: cx - 35, textY: cy + roadWidth / 2 + 50 },
    { name: "EAST", x: cx + roadWidth / 2 + 25, y: cy, textX: cx + roadWidth / 2 + 40, textY: cy + 5 },
    { name: "WEST", x: cx - roadWidth / 2 - 25, y: cy, textX: cx - roadWidth / 2 - 95, textY: cy + 5 }
  ];

  lanes.forEach(lane => {
    const isGreen = lane.name === greenLane;
    const count = jData.counts ? jData.counts[lane.name] || 0 : 0;

    // Signal Bulb
    ctx.beginPath();
    ctx.arc(lane.x, lane.y, 14, 0, 2 * Math.PI);
    ctx.fillStyle = isGreen ? "#00ff88" : "#ff3366";
    ctx.fill();
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 2;
    ctx.stroke();

    // Pulse Glow if Green
    if (isGreen) {
      ctx.beginPath();
      ctx.arc(lane.x, lane.y, 22, 0, 2 * Math.PI);
      ctx.fillStyle = "rgba(0, 255, 136, 0.25)";
      ctx.fill();
    }

    // Vehicle Count Text Overlay
    ctx.fillStyle = "#f8fafc";
    ctx.font = "bold 13px Inter, sans-serif";
    ctx.fillText(`${lane.name}: ${count} 🚗`, lane.textX, lane.textY);
  });

  // Center Timer Overlay
  ctx.fillStyle = isLocked ? "#00f0ff" : "#f59e0b";
  ctx.font = "bold 26px Inter, sans-serif";
  ctx.textAlign = "center";
  ctx.fillText(`${jData.remaining_seconds}s`, cx, cy + 8);

  if (isLocked) {
    ctx.fillStyle = "#00ff88";
    ctx.font = "bold 13px Inter, sans-serif";
    ctx.fillText("CORRIDOR LOCKED 🚑", cx, cy - 20);
  }
}

// Render Explainable AI Cards
function renderExplainableAI() {
  const currentJunctionId = document.getElementById("junction-select")?.value || "J1_BEGUMPET";
  const jData = state.junctions[currentJunctionId];
  if (!jData) return;

  const total = jData.counts ? Object.values(jData.counts).reduce((a, b) => a + b, 0) : 0;
  const greenLane = jData.active_green;
  const isLocked = jData.is_locked;

  const greenLaneEl = document.getElementById("xai-green-lane");
  const totalVehiclesEl = document.getElementById("xai-total-vehicles");
  const queueLengthEl = document.getElementById("xai-queue-length");
  const confidenceEl = document.getElementById("xai-confidence");

  if (greenLaneEl) greenLaneEl.innerText = greenLane;
  if (totalVehiclesEl) totalVehiclesEl.innerText = total;
  if (queueLengthEl) queueLengthEl.innerText = `${((jData.counts[greenLane] || 10) * 5.8).toFixed(1)} m`;
  if (confidenceEl) confidenceEl.innerText = `${isLocked ? 99.8 : 96.5}%`;

  const reasonEl = document.getElementById("xai-reasoning");
  if (reasonEl) {
    if (isLocked) {
      reasonEl.innerText = `🚨 PREEMPTIVE OVERRIDE ACTIVE: Signal locked GREEN for approaching EMS unit on ${greenLane} corridor. Adaptive timers suspended.`;
      reasonEl.className = "text-sm text-emerald-400 font-medium bg-emerald-950/40 p-3 rounded-lg border border-emerald-700/50";
    } else {
      reasonEl.innerText = `🧠 ADAPTIVE AI DECISION: Assigned GREEN phase to ${greenLane} lane due to high queue density (${jData.counts[greenLane] || 0} vehicles). Duration computed to optimize throughput.`;
      reasonEl.className = "text-sm text-cyan-300 font-medium bg-cyan-950/40 p-3 rounded-lg border border-cyan-800/50";
    }
  }
}

// Render Leaflet OpenStreetMap
function initMap() {
  const mapEl = document.getElementById("osm-map");
  if (!mapEl) return;

  map = L.map("osm-map").setView([17.4300, 78.4550], 13);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: "© OpenStreetMap contributors | PulseRoute AI"
  }).addTo(map);

  // Route Polyline coordinates
  routePolyline = L.polyline(WAYPOINTS, { color: "#00f0ff", weight: 5, opacity: 0.85, dashArray: "10, 10" }).addTo(map);

  // Hospital Icon Marker
  const hospitalIcon = L.divIcon({
    html: `<div class="bg-red-600 text-white p-2 rounded-full shadow-lg border-2 border-white text-center text-sm">🏥</div>`,
    className: "hospital-marker",
    iconSize: [32, 32]
  });
  L.marker([17.4156, 78.4412], { icon: hospitalIcon }).addTo(map).bindPopup("<b>Banjara Hills Hospital</b><br>Emergency Target");

  // Ambulance Marker
  const ambIcon = L.divIcon({
    html: `<div class="bg-emerald-500 text-white p-2 rounded-full shadow-xl border-2 border-white text-center text-base animate-bounce">🚑</div>`,
    className: "ambulance-marker",
    iconSize: [36, 36]
  });
  ambulanceMarker = L.marker(WAYPOINTS[0], { icon: ambIcon }).addTo(map).bindPopup("<b>EMS Unit 402</b><br>Green Corridor Active");
}

function renderMapData() {
  if (!map || !ambulanceMarker) return;

  const gps = state.ambulance_gps;
  if (gps && gps.latitude && gps.longitude) {
    ambulanceMarker.setLatLng([gps.latitude, gps.longitude]);
  }
}

// Render Ambulance HUD Portal
function renderAmbulanceHUD() {
  const gps = state.ambulance_gps;
  
  const speedEl = document.getElementById("hud-speed");
  const etaEl = document.getElementById("hud-eta");
  const progressEl = document.getElementById("hud-progress");
  const progressTextEl = document.getElementById("hud-progress-text");
  const nextJunctionEl = document.getElementById("hud-next-junction");

  if (speedEl) speedEl.innerText = `${(gps.speed_kmh || 0).toFixed(1)} km/h`;
  if (etaEl) etaEl.innerText = `${Math.ceil(gps.eta_seconds || 0)}s`;
  if (progressEl) progressEl.style.width = `${gps.progress_percentage || 0}%`;
  if (progressTextEl) progressTextEl.innerText = `${(gps.progress_percentage || 0).toFixed(0)}%`;
  
  if (nextJunctionEl) {
    const jName = state.junctions[gps.next_junction_id]?.name || "Panjagutta Circle";
    nextJunctionEl.innerText = `${jName} (${gps.distance_to_next_km || 1.8} km away)`;
  }
}

// Render Timeline Events Audit Panel
function renderTimeline() {
  const timelineContainer = document.getElementById("timeline-container");
  if (!timelineContainer) return;

  timelineContainer.innerHTML = "";
  const events = state.timeline_events || [];

  events.slice(0, 15).forEach(evt => {
    const item = document.createElement("div");
    item.className = "timeline-item";
    item.innerHTML = `
      <div class="flex items-center justify-between text-xs text-slate-400">
        <span class="font-bold text-cyan-400">[${evt.category}]</span>
        <span>${evt.timestamp}</span>
      </div>
      <div class="text-sm text-slate-200 mt-1">${evt.message}</div>
    `;
    timelineContainer.appendChild(item);
  });
}

// Event Listeners setup
function setupEventListeners() {
  const jSelect = document.getElementById("junction-select");
  if (jSelect) {
    jSelect.addEventListener("change", () => {
      renderIntersectionCanvas();
      renderExplainableAI();
    });
  }

  // Emergency Start Button
  const btnStart = document.getElementById("btn-start-emergency");
  if (btnStart) {
    btnStart.addEventListener("click", async () => {
      state.ambulance_gps.is_active = true;
      state.ambulance_gps.progress_percentage = 0;
      state.system_state = "EMERGENCY_REQUESTED";

      state.timeline_events.unshift({
        timestamp: new Date().toLocaleTimeString(),
        category: "EMERGENCY_DISPATCH",
        message: "Ambulance TS-09-EMS-108 requested Emergency Green Corridor."
      });

      try {
        await fetch(`${API_BASE}/api/emergency/start`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            driver_id: "driver",
            vehicle_plate: "TS-09-EMS-108",
            start_junction_id: "J1_BEGUMPET",
            destination_junction_id: "J3_BANJARA_HILLS"
          })
        });
      } catch (e) {
        console.log("Local emergency mode triggered");
      }
      
      alert("🚨 Emergency Green Corridor Started!\n\nAmbulance is moving fast to Banjara Hills Hospital (reaches in ~10 seconds).");
    });
  }

  // Emergency Stop Button
  const btnStop = document.getElementById("btn-stop-emergency");
  if (btnStop) {
    btnStop.addEventListener("click", async () => {
      state.ambulance_gps.is_active = false;
      state.system_state = "NORMAL";
      state.junctions["J2_PANJAGUTTA"].is_locked = false;
      state.junctions["J3_BANJARA_HILLS"].is_locked = false;

      state.timeline_events.unshift({
        timestamp: new Date().toLocaleTimeString(),
        category: "MISSION_CANCELLED",
        message: "Emergency mission manually cancelled by driver."
      });

      try {
        await fetch(`${API_BASE}/api/emergency/stop`, { method: "POST" });
      } catch (e) {
        console.log("Local emergency stop triggered");
      }

      alert("Emergency Mission Ended. Reverting to Normal Adaptive Control.");
    });
  }
}
