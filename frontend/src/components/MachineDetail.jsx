import { useEffect, useState } from "react";
import { Bar } from "react-chartjs-2";
import { fetchMachine } from "../api";

export default function MachineDetail({ machineId, onClose }) {
  const [detail, setDetail] = useState(null);

  useEffect(() => {
    if (machineId == null) return;
    setDetail(null);
    fetchMachine(machineId).then(setDetail).catch(console.error);
  }, [machineId]);

  if (machineId == null) return null;

  const data = detail
    ? {
        labels: detail.series.map((p) => p.month),
        datasets: [
          {
            label: "Cost",
            data: detail.series.map((p) => p.cost),
            backgroundColor: "rgba(37, 99, 235, 0.7)",
            yAxisID: "y",
          },
          {
            label: "Breakdowns",
            data: detail.series.map((p) => p.breakdowns),
            backgroundColor: "rgba(220, 38, 38, 0.7)",
            yAxisID: "y1",
          },
        ],
      }
    : null;

  const options = {
    responsive: true,
    plugins: { title: { display: true, text: detail ? `${detail.machine.machine} — monthly detail` : "Loading…" } },
    scales: {
      y: { type: "linear", position: "left" },
      y1: { type: "linear", position: "right", grid: { drawOnChartArea: false } },
    },
  };

  return (
    <section className="detail">
      <div className="detail-head">
        {detail && (
          <div className="detail-stats">
            <span>cost <b>{detail.machine.total_cost.toLocaleString()}</b></span>
            <span>breakdowns <b>{detail.machine.total_breakdowns}</b></span>
            <span>MTBF <b>{detail.machine.avg_mtbf} h</b></span>
            <span>MTTR <b>{detail.machine.avg_mttr} h</b></span>
            <span className={detail.machine.priority === "CHECK" ? "badge" : "ok"}>
              {detail.machine.priority} (score {detail.machine.score})
            </span>
          </div>
        )}
        <button onClick={onClose}>Close</button>
      </div>
      {data && <Bar data={data} options={options} />}
    </section>
  );
}
