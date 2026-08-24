import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import * as watchService from '../services/watchService'
import { PageLoading } from '../components/Loading'
import { EmptyState } from '../components/ErrorMessage'
import { formatDate, formatDuration, formatPercent } from '../utils/format'
import { useToast } from '../context/ToastContext'

export default function History() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const { notify } = useToast()

  function load() {
    setLoading(true)
    watchService.fetchHistory({ per_page: 50 }).then((data) => setItems(data.items)).finally(() => setLoading(false))
  }

  useEffect(load, [])

  async function handleRemove(id) {
    await watchService.deleteHistoryEntry(id)
    notify('Removed from history')
    setItems((prev) => prev.filter((i) => i.id !== id))
  }

  if (loading) return <PageLoading />

  return (
    <div>
      <div className="ss-section-title">Watch History</div>
      {items.length === 0 ? (
        <EmptyState title="No watch history yet" subtitle="Videos you watch will show up here." />
      ) : (
        <div className="ss-table-wrap">
          <table className="ss-table">
            <thead>
              <tr>
                <th>Video</th>
                <th>Watched</th>
                <th>Watch Duration</th>
                <th>Completion</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td style={{ cursor: 'pointer' }} onClick={() => navigate(`/videos/${item.video_id}`)}>
                    {item.video?.title}
                  </td>
                  <td>{formatDate(item.watched_at)}</td>
                  <td>{formatDuration(item.watch_duration)}</td>
                  <td>{formatPercent(item.completion_rate)}</td>
                  <td>
                    <button className="ss-btn ss-btn-outline ss-btn-sm" onClick={() => handleRemove(item.id)}>
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
