import { CircleMarker, MapContainer, Polyline, TileLayer, Tooltip } from "react-leaflet";
import type { Gps } from "../types";

import "leaflet/dist/leaflet.css";

const route: [number, number][] = [[12.9618, 77.5901], [12.9645, 77.5914], [12.9672, 77.5927], [12.9698, 77.5938], [12.9722, 77.5946]];
const junctions = ["J1 · Residency Road", "J2 · Richmond Circle", "J3 · MG Road", "J4 · Cubbon Road", "PulseCare Hospital"];

export function EmergencyMap({ gps, routeIndex = 0 }: { gps?: Gps; routeIndex?: number }) {
  const position: [number, number] = gps ? [gps.latitude, gps.longitude] : route[0];
  return <div className="h-[30rem] overflow-hidden rounded-2xl border border-white/10"><MapContainer center={position} zoom={14} className="h-full w-full" scrollWheelZoom><TileLayer attribution="&copy; OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" /><Polyline positions={route} pathOptions={{ color: "#2979ff", weight: 5, opacity: 0.85 }} />{route.map((point, index) => { const state = index < routeIndex ? "passed" : index === routeIndex ? "green" : "waiting"; const color = state === "green" ? "#00e676" : state === "passed" ? "#64748b" : "#ffd600"; return <CircleMarker key={junctions[index]} center={point} radius={index === route.length - 1 ? 10 : 7} pathOptions={{ color, fillColor: color, fillOpacity: 0.95 }}><Tooltip>{junctions[index]} · {state.toUpperCase()}</Tooltip></CircleMarker>; })}<CircleMarker center={position} radius={11} pathOptions={{ color: "#fff", weight: 3, fillColor: "#ff1744", fillOpacity: 1 }}><Tooltip permanent>Ambulance</Tooltip></CircleMarker></MapContainer></div>;
}
