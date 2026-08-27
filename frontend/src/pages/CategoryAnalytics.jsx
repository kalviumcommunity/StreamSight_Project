import { useEffect, useState } from 'react'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts'
import * as analyticsService from '../services/analyticsService'
import ChartCard from '../components/ChartCard'
import DataTable from '../components/DataTable'
import DateRangeFilter, { toDateRangeParams } from '../components/DateRangeFilter'
import ErrorMessage from '../components/ErrorMessage'
import { formatDuration, formatPercent } from '../utils/format'
import { apiErrorMessage } from '../services/api'
import { CATEGORICAL, CHART_GRID, CHART_AXIS } from '../utils/chartColors'

export default function CategoryAnalytics() {
  const [days, setDays] = useState(30)
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError('')
    analyticsService
      .categoryAnalytics(toDateRangeParams(days))
      .then((data) => !cancelled && setRows(data))
      .catch((err) => !cancelled && setError(apiErrorMessage(err)))
      .finally(() => !cancelled && setLoading(false))
    return () => { cancelled = true }
  }, [days])

  return (
    <div>
      <div className="ss-section-title">
        Category Analytics
        <DateRangeFilter days={days} onChange={setDays} />
      </div>

      {error && <ErrorMessage message={error} />}

      <div style={{ marginBottom: '1.25rem' }}>
        <ChartCard title="Views & Completion Rate by Category" loading={loading} empty={!rows.length} height={320}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={rows}>
              <CartesianGrid stroke={CHART_GRID} vertical={false} />
              <XAxis dataKey="category" stroke={CHART_AXIS} fontSize={12} />
              <YAxis stroke={CHART_AXIS} fontSize={12} />
              <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid #e6e1f5' }} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="views" fill={CATEGORICAL[0]} name="Views" radius={[4, 4, 0, 0]} />
              <Bar dataKey="retention_score" fill={CATEGORICAL[2]} name="Retention Score" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="ss-card">
        <div className="ss-section-title">Category Ranking</div>
        <DataTable
          columns={[
            { key: 'category', label: 'Category' },
            { key: 'views', label: 'Views' },
            { key: 'unique_viewers', label: 'Unique Viewers' },
            { key: 'average_watch_duration', label: 'Avg Watch Time', render: (r) => formatDuration(r.average_watch_duration) },
            { key: 'average_completion_rate', label: 'Completion', render: (r) => formatPercent(r.average_completion_rate) },
            { key: 'average_pause_frequency', label: 'Pause Frequency' },
            { key: 'retention_score', label: 'Retention Score' },
          ]}
          rows={rows}
          loading={loading}
          pageSize={10}
        />
      </div>
    </div>
  )
}
