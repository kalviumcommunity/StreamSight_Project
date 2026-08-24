import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import * as videoService from '../services/videoService'
import * as watchService from '../services/watchService'
import { PageLoading } from '../components/Loading'
import ErrorMessage from '../components/ErrorMessage'
import VideoGrid from '../components/VideoGrid'
import { formatDuration, formatViews, formatDate } from '../utils/format'
import { apiErrorMessage } from '../services/api'
import { useToast } from '../context/ToastContext'

export default function VideoDetails() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { notify } = useToast()
  const [video, setVideo] = useState(null)
  const [related, setRelated] = useState([])
  const [bookmarked, setBookmarked] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError('')
    Promise.all([
      videoService.getVideo(id),
      watchService.listBookmarks().catch(() => []),
    ])
      .then(([v, bookmarks]) => {
        if (cancelled) return
        setVideo(v)
        setBookmarked(bookmarks.some((b) => b.video_id === Number(id)))
        return videoService.categoryVideos(v.category_id, { per_page: 8 })
      })
      .then((data) => {
        if (cancelled || !data) return
        setRelated(data.items.filter((r) => r.id !== Number(id)))
      })
      .catch((err) => !cancelled && setError(apiErrorMessage(err)))
      .finally(() => !cancelled && setLoading(false))
    return () => { cancelled = true }
  }, [id])

  async function toggleBookmark() {
    try {
      if (bookmarked) {
        await watchService.removeBookmark(id)
        notify('Removed from bookmarks')
      } else {
        await watchService.addBookmark(id)
        notify('Added to bookmarks')
      }
      setBookmarked((b) => !b)
    } catch (err) {
      notify(apiErrorMessage(err), 'error')
    }
  }

  if (loading) return <PageLoading />
  if (error) return <ErrorMessage message={error} />
  if (!video) return null

  return (
    <div>
      <div className="ss-card" style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', marginBottom: '2rem' }}>
        <img
          src={video.thumbnail_url || 'https://placehold.co/480x270/1c202b/6b7280?text=StreamSight'}
          alt={video.title}
          style={{ width: 340, maxWidth: '100%', borderRadius: 10, objectFit: 'cover' }}
        />
        <div style={{ flex: 1, minWidth: 260 }}>
          <h1 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>{video.title}</h1>
          <div style={{ display: 'flex', gap: '0.75rem', color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.9rem' }}>
            <span>{video.category?.name}</span>
            <span>•</span>
            <span>{formatDuration(video.duration)}</span>
            <span>•</span>
            <span>{formatViews(video.views)}</span>
            <span>•</span>
            <span>{formatDate(video.release_date)}</span>
          </div>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>{video.description}</p>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button className="ss-btn ss-btn-primary" onClick={() => navigate(`/watch/${video.id}`)}>
              ▶ Watch Now
            </button>
            <button className="ss-btn ss-btn-outline" onClick={toggleBookmark}>
              {bookmarked ? '★ Bookmarked' : '☆ Add Bookmark'}
            </button>
          </div>
        </div>
      </div>

      <div className="ss-section-title">More Like This</div>
      <VideoGrid videos={related} />
    </div>
  )
}
