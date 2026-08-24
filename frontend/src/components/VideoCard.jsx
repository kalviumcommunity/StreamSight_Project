import { useNavigate } from 'react-router-dom'
import { formatDuration, formatViews } from '../utils/format'

export default function VideoCard({ video, progress }) {
  const navigate = useNavigate()
  if (!video) return null

  return (
    <div className="ss-video-card" onClick={() => navigate(`/videos/${video.id}`)}>
      <img
        className="ss-video-thumb"
        src={video.thumbnail_url || 'https://placehold.co/400x225/1c202b/6b7280?text=StreamSight'}
        alt={video.title}
        loading="lazy"
      />
      <div className="ss-video-body">
        <p className="ss-video-title">{video.title}</p>
        <div className="ss-video-meta">
          <span>{video.category?.name || video.category}</span>
          <span>{formatDuration(video.duration)}</span>
        </div>
        {video.views !== undefined && (
          <div className="ss-video-meta">
            <span>{formatViews(video.views)}</span>
          </div>
        )}
        {progress !== undefined && (
          <div className="ss-progress-track">
            <div className="ss-progress-fill" style={{ width: `${Math.min(progress, 100)}%` }} />
          </div>
        )}
      </div>
    </div>
  )
}
