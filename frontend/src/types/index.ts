export type Role = "ADMIN" | "AMBULANCE_DRIVER";

export interface User {
  username: string;
  role: Role;
}

export interface ApiEnvelope<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface LoginData {
  access_token: string;
  token_type: string;
  user: User;
}

export interface SignalState {
  mode: "ADAPTIVE" | "MANUAL" | "EMERGENCY";
  phase: "GREEN" | "YELLOW";
  current_green: string;
  remaining_seconds: number;
  lights: Record<string, string>;
  emergency_lock: boolean;
}

export interface RoadMetric {
  road: string;
  vehicle_count: number;
  queue_length_meters: number;
  average_wait_seconds: number;
  density_score: number;
  congestion: string;
  recommended_green_seconds: number;
}

export interface VehicleObservation {
  tracking_id: string;
  vehicle_class: "car" | "bus" | "truck" | "motorcycle";
  confidence: number;
  bbox: { x1: number; y1: number; x2: number; y2: number };
  waiting_seconds: number;
}

export interface TrafficProcessingResult {
  roads: Record<string, RoadMetric>;
  decision: Decision;
  observations: VehicleObservation[];
}

export interface ReportData {
  generated_at: string;
  vehicles_processed: number;
  average_wait_seconds: number;
  signal_utilization: string;
  delay_saved_seconds: number;
  green_corridor_activations: number;
  mission_status: string;
  mission_eta_seconds: number;
}

export interface Decision {
  road: string;
  vehicles: number;
  density: string;
  score: number;
  green_time: number;
  confidence: number;
  reason: string;
}

export interface Mission {
  mission_id: string;
  driver: string;
  hospital: string;
  status: string;
  priority: string;
  distance_meters: number;
  eta_seconds: number;
}

export interface Gps {
  latitude: number;
  longitude: number;
  speed_kph: number;
  distance_meters: number;
  eta_seconds: number;
  current_junction: string;
  upcoming_junction?: string;
  route_index: number;
}

export interface TimelineEvent {
  timestamp: string;
  event: string;
  level: string;
}

export interface DashboardState {
  roads: Record<string, { metrics?: RoadMetric }>;
  signals: SignalState;
  analytics: { roads?: Record<string, RoadMetric> };
  ai_decision: Decision | null;
  mission: Mission | { status: "IDLE" };
  gps: Gps | Record<string, never>;
  metrics: { total_vehicles?: number };
  logs: TimelineEvent[];
  system_health: Record<string, string>;
  video?: { status: string; file_name?: string; frames_processed?: number; fps?: number; last_observation_count?: number; error?: string };
}

export interface VisionStatus {
  status: string;
  model_path: string;
  message: string;
}

export interface EmergencySnapshot {
  mission: Mission | null;
  gps: Gps | null;
  corridor: { junction: string; road: string; status: string }[];
}
