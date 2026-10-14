import { Bar } from "react-chartjs-2";

export default function CostChart({ machines }) {
  const sorted = [...machines].sort((a, b) => b.total_cost - a.total_cost);
  const data = {
    labels: sorted.map((m) => m.machine),
    datasets: [
      {
        label: "Total cost",
        data: sorted.map((m) => m.total_cost),
        backgroundColor: sorted.map((m) =>
          m.priority === "CHECK" ? "rgba(220, 38, 38, 0.7)" : "rgba(37, 99, 235, 0.7)"
        ),
      },
    ],
  };
  const options = {
    responsive: true,
    plugins: { legend: { display: false }, title: { display: true, text: "Cost by machine (worst first)" } },
  };
  return <Bar data={data} options={options} />;
}
