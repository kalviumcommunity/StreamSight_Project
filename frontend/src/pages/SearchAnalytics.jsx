import { useEffect, useState } from 'react'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'
import * as analyticsService from '../services/analyticsService'
import ChartCard from '../components/ChartCard'
import DataTable from '../components/DataTable'
import ErrorMessage from '../components/ErrorMessage'
import { apiErrorMessage } from '../services/api'
import { CATEGORICAL, CHART_GRID, CHART_AXIS } from '../utils/chartColors'

export default function SearchAnalytics() {
  const [period, setPeriod] = useState('daily')
  const [analytics, setAnalytics] = useState(null)
  const [trends, setTrends] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError('')
    Promise.all([
      analyticsService.searchAnalytics({ limit: 10 }),
      analyticsService.searchTrends({ period }),
    ])
      .then(([a, t]) => {
        if (cancelled) return
        setAnalytics(a)
        setTrends(t)
      })
      .catch((err) => !cancelled && setError(apiErrorMessage(err)))
      .finally(() => !cancelled && setLoading(false))
    return () => { cancelled = true }
  }, [period])

  return (
    <div>
      <div className="ss-section-title">
        Search Analytics
        <select className="ss-select" style={{ width: 'auto' }} value={period} onChange={(e) => setPeriod(e.target.value)}>
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
        </select>
      </div>

      {error && <ErrorMessage message={error} />}

      <div style={{ marginBottom: '1.25rem' }}>
        <ChartCard title="Search Volume Over Time" loading={loading} empty={!trends?.trend?.length}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={trends?.trend || []}>
              <CartesianGrid stroke={CHART_GRID} vertical={false} />
              <XAxis dataKey="timestamp" stroke={CHART_AXIS} fontSize={11} />
              <YAxis stroke={CHART_AXIS} fontSize={12} />
              <Tooltip contentStyle={{ background: '#1c202b', border: '1px solid #262b38' }} />
              <Bar dataKey="count" fill={CATEGORICAL[0]} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1.25rem' }}>
        <div className="ss-card">
          <div className="ss-section-title">Most Searched Keywords</div>
          <DataTable
            columns={[
              { key: 'query', label: 'Keyword' },
              { key: 'count', label: 'Searches' },
            ]}
            rows={analytics?.top_keywords || []}
            loading={loading}
            pageSize={10}
          />
        </div>

        <div className="ss-card">
          <div className="ss-section-title">Most Searched Categories</div>
          <DataTable
            columns={[
              { key: 'category', label: 'Category' },
              { key: 'count', label: 'Searches' },
            ]}
            rows={analytics?.top_categories || []}
            loading={loading}
            pageSize={10}
          />
        </div>

        <div className="ss-card">
          <div className="ss-section-title">Unsuccessful Searches</div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: -6, marginBottom: 10 }}>
            Queries that returned zero results - potential content demand.
          </p>
          <DataTable
            columns={[
              { key: 'query', label: 'Query' },
              { key: 'count', label: 'Times Searched' },
            ]}
            rows={trends?.no_result_searches || []}
            loading={loading}
            pageSize={10}
            emptyTitle="No zero-result searches"
          />
        </div>
      </div>
    </div>
  )
}
