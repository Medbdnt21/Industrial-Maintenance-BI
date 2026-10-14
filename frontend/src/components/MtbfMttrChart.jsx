import { Bar } from "react-chartjs-2";

export default function MtbfMttrChart({ machines }) {
  const sorted = [...machines].sort((a, b) => a.avg_mtbf - b.avg_mtbf);
  const data = {
    labels: sorted.map((m) => m.machine),
    datasets: [
      {
        label: "Avg MTBF (h)",
        data: sorted.map((m) => m.avg_mtbf),
        backgroundColor: "rgba(22, 163, 74, 0.7)",
      },
      {
        label: "Avg MTTR (h)",
        data: sorted.map((m) => m.avg_mttr),
        backgroundColor: "rgba(245, 158, 11, 0.7)",
      },
    ],
  };
  const options = {
    responsive: true,
    plugins: {
      title: { display: true, text: "MTBF (higher = better) vs MTTR (lower = better)" },
    },
  };
  return <Bar data={data} options={options} />;
}
