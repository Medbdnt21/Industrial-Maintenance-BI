import { useEffect, useState } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { fetchAlerts, fetchMachines } from "./api";
import KpiCards from "./components/KpiCards";
import CostChart from "./components/CostChart";
import BreakdownChart from "./components/BreakdownChart";
import MtbfMttrChart from "./components/MtbfMttrChart";
import TrendChart from "./components/TrendChart";
import AlertTable from "./components/AlertTable";
import MachineDetail from "./components/MachineDetail";

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend);

export default function App() {
  const [machines, setMachines] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [error, setError] = useState(null);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    fetchMachines().then(setMachines).catch((e) => setError(String(e)));
    fetchAlerts().then(setAlerts).catch((e) => setError(String(e)));
  }, []);

  if (error) return <p className="error">API error: {error} — is backend running on :8000?</p>;

  return (
    <main className="container">
      <header>
        <h1>Industrial Maintenance BI</h1>
        <p className="muted">Breakdowns · Costs · MTBF · MTTR · Machines to check</p>
      </header>

      <KpiCards />

      <section className="panel">
        <h2>Machines to check</h2>
        <p className="muted">Score = KPIs in worst quartile (0–4). Score ≥ 2 = check.</p>
        <AlertTable alerts={alerts} onSelect={setSelected} />
      </section>

      <section className="grid-2">
        <div className="panel">{machines.length > 0 && <CostChart machines={machines} />}</div>
        <div className="panel">{machines.length > 0 && <BreakdownChart machines={machines} />}</div>
        <div className="panel">{machines.length > 0 && <MtbfMttrChart machines={machines} />}</div>
        <div className="panel"><TrendChart /></div>
      </section>

      <section className="panel">
        <div className="detail-head">
          <h2>Machine detail</h2>
          <select
            value={selected ?? ""}
            onChange={(e) => setSelected(e.target.value ? Number(e.target.value) : null)}
          >
            <option value="">Select machine…</option>
            {machines.map((m) => (
              <option key={m.machine_id} value={m.machine_id}>
                {m.machine}
              </option>
            ))}
          </select>
        </div>
        <MachineDetail machineId={selected} onClose={() => setSelected(null)} />
      </section>
    </main>
  );
}
