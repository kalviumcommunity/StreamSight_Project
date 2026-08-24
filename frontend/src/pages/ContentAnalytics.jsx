import { useEffect, useState } from 'react'
import * as analyticsService from '../services/analyticsService'
import * as videoService from '../services/videoService'
import DataTable from '../components/DataTable'
import DateRangeFilter, { toDateRangeParams } from '../components/DateRangeFilter'
import CategoryFilter from '../components/CategoryFilter'
import { PageLoading } from '../components/Loading'
import ErrorMessage from '../components/ErrorMessage'
import { formatPercent, formatDuration } from '../utils/format'
import { apiErrorMessage } from '../services/api'

function statusBadge(retentionScore) {
  if (retentionScore >= 65) return <span className="ss-badge ss-badge-positive">Strong</span>
  if (retentionScore >= 40) return <span className="ss-badge ss-badge-warning">Average</span>
  return <span className="ss-badge ss-badge-danger">Weak</span>
}

export default function ContentAnalytics() {
  const [days, setDays] = useState(30)
  const [categoryId, setCategoryId] = useState('')
  const [categories, setCategories] = useState([])
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    videoService.listCategories().then(setCategories).catch(() => {})
  }, [])

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError('')
    analyticsService
      .contentPerformance({ ...toDateRangeParams(days), category_id: categoryId || undefined })
      .then((data) => !cancelled && setRows(data))
      .catch((err) => !cancelled && setError(apiErrorMessage(err)))
      .finally(() => !cancelled && setLoading(false))
    return () => { cancelled = true }
  }, [days, categoryId])

  return (
    <div>
      <div className="ss-section-title">
        Content Performance
        <div style={{ display: 'flex', gap: '0.6rem' }}>
          <CategoryFilter categories={categories} value={categoryId} onChange={setCategoryId} />
          <DateRangeFilter days={days} onChange={setDays} />
        </div>
      </div>

      {error ? (
        <ErrorMessage message={error} />
      ) : loading ? (
        <PageLoading />
      ) : (
        <div className="ss-card">
          <DataTable
            columns={[
              { key: 'title', label: 'Content' },
              { key: 'category', label: 'Category' },
              { key: 'total_views', label: 'Views' },
              { key: 'unique_viewers', label: 'Unique Viewers' },
              { key: 'average_watch_duration', label: 'Avg Watch Time', render: (r) => formatDuration(r.average_watch_duration) },
              { key: 'average_completion_rate', label: 'Completion', render: (r) => formatPercent(r.average_completion_rate) },
              { key: 'average_pause_count', label: 'Avg Pauses' },
              { key: 'replay_rate', label: 'Replay Rate', render: (r) => formatPercent(r.replay_rate) },
              { key: 'bookmark_count', label: 'Bookmarks' },
              { key: 'average_retention_score', label: 'Retention' },
              { key: 'status', label: 'Status', sortable: false, render: (r) => statusBadge(r.average_retention_score) },
            ]}
            rows={rows}
            pageSize={12}
            emptyTitle="No content performance data for this range"
          />
        </div>
      )}
    </div>
  )
}
