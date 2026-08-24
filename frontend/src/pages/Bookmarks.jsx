import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import * as watchService from '../services/watchService'
import { PageLoading } from '../components/Loading'
import { EmptyState } from '../components/ErrorMessage'
import { useToast } from '../context/ToastContext'
import { apiErrorMessage } from '../services/api'

export default function Bookmarks() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const { notify } = useToast()

  useEffect(() => {
    watchService.listBookmarks().then(setItems).finally(() => setLoading(false))
  }, [])

  async function handleRemove(videoId) {
    try {
      await watchService.removeBookmark(videoId)
      setItems((prev) => prev.filter((b) => b.video_id !== videoId))
      notify('Bookmark removed')
    } catch (err) {
      notify(apiErrorMessage(err), 'error')
    }
  }

  if (loading) return <PageLoading />

  return (
    <div>
      <div className="ss-section-title">Bookmarks</div>
      {items.length === 0 ? (
        <EmptyState title="No bookmarks yet" subtitle="Save videos to watch later." />
      ) : (
        <div className="ss-video-grid">
          {items.map((b) => (
            <div key={b.id} className="ss-video-card">
              <img
                className="ss-video-thumb"
                src={b.video?.thumbnail_url || 'https://placehold.co/400x225/1c202b/6b7280?text=StreamSight'}
                alt={b.video?.title}
                onClick={() => navigate(`/videos/${b.video_id}`)}
              />
              <div className="ss-video-body">
                <p className="ss-video-title">{b.video?.title}</p>
                <button className="ss-btn ss-btn-outline ss-btn-sm" style={{ width: '100%', marginTop: 6 }} onClick={() => handleRemove(b.video_id)}>
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
