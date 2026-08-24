import { useEffect, useState } from 'react'
import * as analyticsService from '../services/analyticsService'
import DateRangeFilter, { toDateRangeParams } from '../components/DateRangeFilter'
import { PageLoading } from '../components/Loading'
import ErrorMessage from '../components/ErrorMessage'
import { EmptyState } from '../components/ErrorMessage'
import { formatPercent } from '../utils/format'
import { apiErrorMessage } from '../services/api'

function InsightCard({ badge, badgeClass, item, primaryMetricLabel, primaryMetricValue }) {
  return (
    <div className="ss-card" style={{ marginBottom: '0.75rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.4rem' }}>
        <div>
          <span className={`ss-badge ${badgeClass}`}>{badge}</span>
          <h3 style={{ fontSize: '1rem', margin: '0.5rem 0 0' }}>{item.video}</h3>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', margin: '0.15rem 0 0' }}>{item.category}</p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '1.4rem', fontWeight: 700 }}>{primaryMetricValue}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{primaryMetricLabel}</div>
        </div>
      </div>
      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: 0 }}>{item.reason}</p>
      <div style={{ display: 'flex', gap: '1rem', marginTop: '0.6rem', fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
        <span>Views: {item.views}</span>
        <span>Completion: {formatPercent(item.completion_rate)}</span>
        <span>Pauses: {item.pause_frequency}</span>
      </div>
    </div>
  )
}

export default function AcquisitionInsights() {
  const [days, setDays] = useState(30)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError('')
    analyticsService
      .acquisitionInsights(toDateRangeParams(days))
      .then((d) => !cancelled && setData(d))
      .catch((err) => !cancelled && setError(apiErrorMessage(err)))
      .finally(() => !cancelled && setLoading(false))
    return () => { cancelled = true }
  }, [days])

  return (
    <div>
      <div className="ss-section-title">
        Acquisition Insights
        <DateRangeFilter days={days} onChange={setDays} />
      </div>

      {error && <ErrorMessage message={error} />}
      {loading && <PageLoading />}

      {data && (
        <>
          {data.summary && (
            <div className="ss-card ss-card-elevated" style={{ marginBottom: '1.5rem' }}>
              <div className="ss-section-title">Acquisition Decision Summary</div>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                Based on current viewer engagement patterns across the selected period:
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem' }}>
                <div>
                  <div className="ss-metric-label" style={{ marginBottom: 6 }}>Top Content to Invest In</div>
                  {data.summary.top_content_to_invest_in.length === 0 ? (
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Not enough data yet</p>
                  ) : (
                    data.summary.top_content_to_invest_in.map((c, i) => (
                      <div key={i} style={{ fontSize: '0.85rem', marginBottom: 4 }}>• {c.title}</div>
                    ))
                  )}
                </div>
                <div>
                  <div className="ss-metric-label" style={{ marginBottom: 6 }}>Needs Investigation</div>
                  {data.summary.content_needing_investigation.length === 0 ? (
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>None flagged</p>
                  ) : (
                    data.summary.content_needing_investigation.map((c, i) => (
                      <div key={i} style={{ fontSize: '0.85rem', marginBottom: 4 }}>• {c.title}</div>
                    ))
                  )}
                </div>
                <div>
                  <div className="ss-metric-label" style={{ marginBottom: 6 }}>High-Potential Categories</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {data.summary.high_potential_categories.map((c) => (
                      <span key={c} className="ss-badge ss-badge-positive">{c}</span>
                    ))}
                  </div>
                </div>
                <div>
                  <div className="ss-metric-label" style={{ marginBottom: 6 }}>Weak Categories</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {data.summary.weak_categories.map((c) => (
                      <span key={c} className="ss-badge ss-badge-danger">{c}</span>
                    ))}
                  </div>
                </div>
                <div>
                  <div className="ss-metric-label" style={{ marginBottom: 6 }}>Dominant Drop-off Stage</div>
                  <span className="ss-badge ss-badge-info">{data.summary.dominant_dropoff_stage || 'N/A'}</span>
                </div>
              </div>
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
            <div>
              <div className="ss-section-title" style={{ fontSize: '0.95rem' }}>
                Strong Acquisition Candidates ({data.strong_acquisition_candidates.length})
              </div>
              {data.strong_acquisition_candidates.length === 0 ? (
                <EmptyState title="None yet" subtitle="No content meets the strong-candidate threshold for this range." />
              ) : (
                data.strong_acquisition_candidates.map((item) => (
                  <InsightCard
                    key={item.video_id}
                    badge="Strong Candidate"
                    badgeClass="ss-badge-positive"
                    item={item}
                    primaryMetricLabel="Retention Score"
                    primaryMetricValue={item.retention_score}
                  />
                ))
              )}
            </div>

            <div>
              <div className="ss-section-title" style={{ fontSize: '0.95rem' }}>
                Needs Investigation ({data.needs_investigation.length})
              </div>
              {data.needs_investigation.length === 0 ? (
                <EmptyState title="Nothing flagged" subtitle="No content shows high views with poor completion." />
              ) : (
                data.needs_investigation.map((item) => (
                  <InsightCard
                    key={item.video_id}
                    badge="Needs Investigation"
                    badgeClass="ss-badge-warning"
                    item={item}
                    primaryMetricLabel="Completion Rate"
                    primaryMetricValue={formatPercent(item.completion_rate)}
                  />
                ))
              )}
            </div>

            <div>
              <div className="ss-section-title" style={{ fontSize: '0.95rem' }}>
                Hidden Performers ({data.hidden_performers.length})
              </div>
              {data.hidden_performers.length === 0 ? (
                <EmptyState title="None found" subtitle="No low-view, high-retention content detected." />
              ) : (
                data.hidden_performers.map((item) => (
                  <InsightCard
                    key={item.video_id}
                    badge="Hidden Performer"
                    badgeClass="ss-badge-info"
                    item={item}
                    primaryMetricLabel="Retention Score"
                    primaryMetricValue={item.retention_score}
                  />
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
