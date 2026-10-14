import { useEffect, useState } from "react";
import { fetchOverview } from "../api";

const fmt = (n) => n?.toLocaleString("en-US", { maximumFractionDigits: 2 });

export default function KpiCards() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchOverview().then(setData).catch(console.error);
  }, []);

  if (!data) return <p className="muted">Loading overview…</p>;

  const cards = [
    { label: "Total cost", value: fmt(data.total_cost), hint: "currency units" },
    { label: "Total breakdowns", value: fmt(data.total_breakdowns), hint: `${data.machines} machines` },
    { label: "Avg MTBF", value: `${fmt(data.avg_mtbf)} h`, hint: "time between breakdowns" },
    { label: "Avg MTTR", value: `${fmt(data.avg_mttr)} h`, hint: "time to repair" },
  ];

  return (
    <div className="kpi-grid">
      {cards.map((c) => (
        <div className="kpi-card" key={c.label}>
          <span className="kpi-label">{c.label}</span>
          <span className="kpi-value">{c.value}</span>
          <span className="kpi-hint">{c.hint}</span>
        </div>
      ))}
    </div>
  );
}
