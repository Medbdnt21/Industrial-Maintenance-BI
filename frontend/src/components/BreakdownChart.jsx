import { Bar } from "react-chartjs-2";

export default function BreakdownChart({ machines }) {
  const sorted = [...machines].sort((a, b) => b.total_breakdowns - a.total_breakdowns);
  const data = {
    labels: sorted.map((m) => m.machine),
    datasets: [
      {
        label: "Breakdowns",
        data: sorted.map((m) => m.total_breakdowns),
        backgroundColor: sorted.map((m) =>
          m.priority === "CHECK" ? "rgba(220, 38, 38, 0.7)" : "rgba(37, 99, 235, 0.7)"
        ),
      },
    ],
  };
  const options = {
    responsive: true,
    plugins: { legend: { display: false }, title: { display: true, text: "Breakdowns by machine" } },
  };
  return <Bar data={data} options={options} />;
}
