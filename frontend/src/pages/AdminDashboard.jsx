import { useEffect, useState } from 'react'
import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
} from 'recharts'
import * as analyticsService from '../services/analyticsService'
import MetricCard from '../components/MetricCard'
import ChartCard from '../components/ChartCard'
import DataTable from '../components/DataTable'
import { PageLoading } from '../components/Loading'
import ErrorMessage from '../components/ErrorMessage'
import { formatDuration, formatPercent } from '../utils/format'
import { apiErrorMessage } from '../services/api'
import { CATEGORICAL, CHART_GRID, CHART_AXIS } from '../utils/chartColors'

export default function AdminDashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    analyticsService
      .dashboardOverview()
      .then(setData)
      .catch((err) => setError(apiErrorMessage(err)))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <PageLoading />
  if (error) return <ErrorMessage message={error} />
  if (!data) return null

  return (
    <div>
      <div className="ss-section-title">Dashboard Overview</div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
        <MetricCard label="Total Users" value={data.total_users} icon="👥" />
        <MetricCard label="Total Videos" value={data.total_videos} icon="🎬" />
        <MetricCard label="Total Views (30d)" value={data.total_views} icon="👁" />
        <MetricCard label="Avg Watch Time" value={formatDuration(data.average_watch_time)} icon="⏱" />
        <MetricCard label="Completion Rate" value={formatPercent(data.average_completion_rate)} icon="✅" />
        <MetricCard label="Pause Frequency" value={data.average_pause_frequency} icon="⏸" />
        <MetricCard label="Retention Score" value={data.retention_score} icon="📈" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '1.25rem', marginBottom: '1.25rem' }}>
        <ChartCard title="Engagement Trend (7 days)" subtitle="Views & completion rate over time" empty={!data.recent_engagement_trends?.length}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data.recent_engagement_trends}>
              <CartesianGrid stroke={CHART_GRID} vertical={false} />
              <XAxis dataKey="created_at" stroke={CHART_AXIS} fontSize={12} />
              <YAxis stroke={CHART_AXIS} fontSize={12} />
              <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid #e6e1f5' }} />
              <Line type="monotone" dataKey="views" stroke={CATEGORICAL[0]} strokeWidth={2} dot={false} name="Views" />
              <Line type="monotone" dataKey="average_completion_rate" stroke={CATEGORICAL[2]} strokeWidth={2} dot={false} name="Completion %" />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Drop-off Distribution" subtitle="Where viewers stop watching" empty={!data.dropoff_distribution?.length}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.dropoff_distribution}>
              <CartesianGrid stroke={CHART_GRID} vertical={false} />
              <XAxis dataKey="range" stroke={CHART_AXIS} fontSize={11} />
              <YAxis stroke={CHART_AXIS} fontSize={12} />
              <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid #e6e1f5' }} />
              <Bar dataKey="viewers" fill={CATEGORICAL[1]} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
        <div className="ss-card">
          <div className="ss-section-title">Top Performing Videos</div>
          <DataTable
            columns={[
              { key: 'title', label: 'Title' },
              { key: 'total_views', label: 'Views' },
              { key: 'average_completion_rate', label: 'Completion', render: (r) => formatPercent(r.average_completion_rate) },
              { key: 'average_retention_score', label: 'Retention' },
            ]}
            rows={data.top_performing_videos}
            pageSize={5}
          />
        </div>

        <div className="ss-card">
          <div className="ss-section-title">Trending This Week</div>
          <DataTable
            columns={[
              { key: 'rank', label: '#' },
              { key: 'title', label: 'Title' },
              { key: 'views', label: 'Views' },
              { key: 'trending_score', label: 'Score' },
            ]}
            rows={data.trending_videos}
            pageSize={5}
          />
        </div>
      </div>

      <div style={{ marginTop: '1.25rem' }}>
        <ChartCard title="Category Performance" subtitle="Views by category" empty={!data.category_performance?.length} height={260}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.category_performance} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid stroke={CHART_GRID} horizontal={false} />
              <XAxis type="number" stroke={CHART_AXIS} fontSize={12} />
              <YAxis type="category" dataKey="category" stroke={CHART_AXIS} fontSize={12} width={90} />
              <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid #e6e1f5' }} />
              <Bar dataKey="views" fill={CATEGORICAL[0]} radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  )
}
