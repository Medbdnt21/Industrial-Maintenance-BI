import { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import { fetchTimeseries } from "../api";

export default function TrendChart() {
  const [cost, setCost] = useState([]);
  const [breakdowns, setBreakdowns] = useState([]);

  useEffect(() => {
    fetchTimeseries("cost").then((d) => setCost(d.points)).catch(console.error);
    fetchTimeseries("breakdowns").then((d) => setBreakdowns(d.points)).catch(console.error);
  }, []);

  const labels = cost.map((p) => p.month);
  const data = {
    labels,
    datasets: [
      {
        label: "Cost",
        data: cost.map((p) => p.cost),
        borderColor: "rgb(37, 99, 235)",
        backgroundColor: "rgba(37, 99, 235, 0.2)",
        yAxisID: "y",
        tension: 0.25,
      },
      {
        label: "Breakdowns",
        data: breakdowns.map((p) => p.breakdowns),
        borderColor: "rgb(220, 38, 38)",
        backgroundColor: "rgba(220, 38, 38, 0.2)",
        yAxisID: "y1",
        tension: 0.25,
      },
    ],
  };
  const options = {
    responsive: true,
    interaction: { mode: "index", intersect: false },
    plugins: { title: { display: true, text: "Monthly trend: cost vs breakdowns" } },
    scales: {
      y: { type: "linear", position: "left", title: { display: true, text: "Cost" } },
      y1: { type: "linear", position: "right", grid: { drawOnChartArea: false }, title: { display: true, text: "Breakdowns" } },
    },
  };
  return <Line data={data} options={options} />;
}
