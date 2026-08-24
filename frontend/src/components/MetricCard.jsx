export default function MetricCard({ label, value, delta, deltaDirection, icon }) {
  return (
    <div className="ss-metric-card">
      <div className="ss-metric-label">{icon ? `${icon}  ` : ''}{label}</div>
      <div className="ss-metric-value">{value}</div>
      {delta !== undefined && delta !== null && (
        <div className={`ss-metric-delta ${deltaDirection || ''}`}>
          {deltaDirection === 'up' ? '▲' : deltaDirection === 'down' ? '▼' : ''} {delta}
        </div>
      )}
    </div>
  )
}
