const PRESETS = [
  { label: '7 days', days: 7 },
  { label: '30 days', days: 30 },
  { label: '90 days', days: 90 },
]

export default function DateRangeFilter({ days, onChange, period, onPeriodChange }) {
  return (
    <div style={{ display: 'flex', gap: '0.5rem' }}>
      {PRESETS.map((p) => (
        <button
          key={p.days}
          className={`ss-btn ss-btn-sm ${days === p.days ? 'ss-btn-primary' : 'ss-btn-outline'}`}
          onClick={() => onChange(p.days)}
        >
          {p.label}
        </button>
      ))}
      {onPeriodChange && (
        <select className="ss-select" style={{ width: 'auto' }} value={period} onChange={(e) => onPeriodChange(e.target.value)}>
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
        </select>
      )}
    </div>
  )
}

export function toDateRangeParams(days) {
  const to = new Date()
  const from = new Date(to.getTime() - days * 24 * 3600 * 1000)
  return { date_from: from.toISOString(), date_to: to.toISOString() }
}
