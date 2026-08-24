import { useEffect, useState } from 'react'
import { ResponsiveContainer, LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'
import * as analyticsService from '../services/analyticsService'
import ChartCard from '../components/ChartCard'
import MetricCard from '../components/MetricCard'
import DateRangeFilter, { toDateRangeParams } from '../components/DateRangeFilter'
import ErrorMessage from '../components/ErrorMessage'
import { formatDuration, formatPercent } from '../utils/format'
import { apiErrorMessage } from '../services/api'
import { CATEGORICAL, CHART_GRID, CHART_AXIS } from '../utils/chartColors'

export default function ViewerAnalytics() {
  const [days, setDays] = useState(30)
  const [period, setPeriod] = useState('daily')
  const [trends, setTrends] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError('')
    const params = { ...toDateRangeParams(days), period }
    Promise.all([
      analyticsService.engagementTrends(params),
      analyticsService.analyticsSummary(toDateRangeParams(days)),
    ])
      .then(([t, s]) => {
        if (cancelled) return
        setTrends(t)
        setSummary(s)
      })
      .catch((err) => !cancelled && setError(apiErrorMessage(err)))
      .finally(() => !cancelled && setLoading(false))
    return () => { cancelled = true }
  }, [days, period])

  return (
    <div>
      <div className="ss-section-title">
        Viewer Engagement
        <DateRangeFilter days={days} onChange={setDays} period={period} onPeriodChange={setPeriod} />
      </div>

      {error && <ErrorMessage message={error} />}

      {summary && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
          <MetricCard label="Total Views" value={summary.total_views} icon="👁" />
          <MetricCard label="Avg Watch Time" value={formatDuration(summary.average_watch_time)} icon="⏱" />
          <MetricCard label="Completion Rate" value={formatPercent(summary.average_completion_rate)} icon="✅" />
          <MetricCard label="Pause Frequency" value={summary.average_pause_frequency} icon="⏸" />
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', marginBottom: '1.25rem' }}>
        <ChartCard title="Watch Time Trend" loading={loading} empty={!trends.length}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trends}>
              <CartesianGrid stroke={CHART_GRID} vertical={false} />
              <XAxis dataKey="created_at" stroke={CHART_AXIS} fontSize={11} />
              <YAxis stroke={CHART_AXIS} fontSize={12} />
              <Tooltip contentStyle={{ background: '#1c202b', border: '1px solid #262b38' }} />
              <Line type="monotone" dataKey="average_watch_time" stroke={CATEGORICAL[0]} strokeWidth={2} dot={false} name="Avg Watch Time (s)" />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Completion Rate Trend" loading={loading} empty={!trends.length}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trends}>
              <CartesianGrid stroke={CHART_GRID} vertical={false} />
              <XAxis dataKey="created_at" stroke={CHART_AXIS} fontSize={11} />
              <YAxis stroke={CHART_AXIS} fontSize={12} />
              <Tooltip contentStyle={{ background: '#1c202b', border: '1px solid #262b38' }} />
              <Line type="monotone" dataKey="average_completion_rate" stroke={CATEGORICAL[2]} strokeWidth={2} dot={false} name="Completion %" />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
        <ChartCard title="Pause Frequency" loading={loading} empty={!trends.length}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={trends}>
              <CartesianGrid stroke={CHART_GRID} vertical={false} />
              <XAxis dataKey="created_at" stroke={CHART_AXIS} fontSize={11} />
              <YAxis stroke={CHART_AXIS} fontSize={12} />
              <Tooltip contentStyle={{ background: '#1c202b', border: '1px solid #262b38' }} />
              <Bar dataKey="average_pause_frequency" fill={CATEGORICAL[3]} radius={[4, 4, 0, 0]} name="Avg Pauses" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Viewer Retention Score" loading={loading} empty={!trends.length}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trends}>
              <CartesianGrid stroke={CHART_GRID} vertical={false} />
              <XAxis dataKey="created_at" stroke={CHART_AXIS} fontSize={11} />
              <YAxis stroke={CHART_AXIS} fontSize={12} domain={[0, 100]} />
              <Tooltip contentStyle={{ background: '#1c202b', border: '1px solid #262b38' }} />
              <Line type="monotone" dataKey="retention_score" stroke={CATEGORICAL[6]} strokeWidth={2} dot={false} name="Retention Score" />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  )
}
