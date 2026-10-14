export default function AlertTable({ alerts, onSelect }) {
  if (!alerts.length) return <p className="muted">No machines need checking.</p>;

  return (
    <table className="alert-table">
      <thead>
        <tr>
          <th>Machine</th>
          <th>Priority</th>
          <th>Score</th>
          <th>Why</th>
        </tr>
      </thead>
      <tbody>
        {alerts.map((a) => (
          <tr key={a.machine_id} onClick={() => onSelect(a.machine_id)} title="View detail">
            <td className="machine-link">{a.machine}</td>
            <td><span className="badge">{a.priority}</span></td>
            <td>{a.score} / 4</td>
            <td>{a.flag_reasons.join(", ")}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
