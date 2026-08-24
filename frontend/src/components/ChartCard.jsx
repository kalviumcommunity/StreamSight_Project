import { PageLoading } from './Loading'
import ErrorMessage from './ErrorMessage'
import { EmptyState } from './ErrorMessage'

export default function ChartCard({ title, subtitle, action, loading, error, empty, children, height = 280 }) {
  return (
    <div className="ss-card">
      <div className="ss-section-title">
        <div>
          <div>{title}</div>
          {subtitle && (
            <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', fontWeight: 400 }}>{subtitle}</div>
          )}
        </div>
        {action}
      </div>
      <div style={{ height }}>
        {loading ? (
          <PageLoading />
        ) : error ? (
          <ErrorMessage message={error} />
        ) : empty ? (
          <EmptyState title="No data for this range" />
        ) : (
          children
        )}
      </div>
    </div>
  )
}
