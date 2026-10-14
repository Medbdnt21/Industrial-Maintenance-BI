const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function get(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`${path} -> ${res.status}`);
  return res.json();
}

export const fetchOverview = () => get("/api/overview");
export const fetchMachines = () => get("/api/machines");
export const fetchAlerts = () => get("/api/alerts");
export const fetchMachine = (id) => get(`/api/machines/${id}`);
export const fetchTimeseries = (metric) => get(`/api/timeseries?metric=${metric}`);
