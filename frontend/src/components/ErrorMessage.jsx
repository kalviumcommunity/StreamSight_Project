export default function ErrorMessage({ message = 'Something went wrong.', onRetry }) {
  return (
    <div className="ss-empty-state">
      <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>⚠</div>
      <p>{message}</p>
      {onRetry && (
        <button className="ss-btn ss-btn-outline ss-btn-sm" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  )
}

export function EmptyState({ title = 'Nothing here yet', subtitle, action }) {
  return (
    <div className="ss-empty-state">
      <p style={{ fontSize: '1rem', color: 'var(--text-primary)', marginBottom: '0.25rem' }}>{title}</p>
      {subtitle && <p style={{ fontSize: '0.88rem' }}>{subtitle}</p>}
      {action}
    </div>
  )
}
