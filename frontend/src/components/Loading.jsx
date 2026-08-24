export function Spinner({ size = 28 }) {
  return (
    <div
      style={{
        width: size,
        height: size,
        border: '3px solid var(--border)',
        borderTopColor: 'var(--accent)',
        borderRadius: '50%',
        animation: 'ss-spin 0.8s linear infinite',
        margin: '0 auto',
      }}
    >
      <style>{'@keyframes ss-spin { to { transform: rotate(360deg); } }'}</style>
    </div>
  )
}

export function PageLoading() {
  return (
    <div className="ss-empty-state">
      <Spinner size={36} />
      <p style={{ marginTop: '1rem' }}>Loading...</p>
    </div>
  )
}

export function SkeletonGrid({ count = 8 }) {
  return (
    <div className="ss-video-grid">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i}>
          <div className="ss-skeleton" style={{ aspectRatio: '16 / 9', borderRadius: 10 }} />
          <div className="ss-skeleton" style={{ height: 14, marginTop: 8, width: '80%' }} />
          <div className="ss-skeleton" style={{ height: 12, marginTop: 6, width: '50%' }} />
        </div>
      ))}
    </div>
  )
}

export function SkeletonRows({ count = 5 }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="ss-skeleton" style={{ height: 42, borderRadius: 8 }} />
      ))}
    </div>
  )
}
