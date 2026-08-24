import { useEffect, useRef, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import * as videoService from '../services/videoService'
import * as watchService from '../services/watchService'
import { PageLoading } from '../components/Loading'
import VideoGrid from '../components/VideoGrid'
import { formatClock } from '../utils/format'
import { useToast } from '../context/ToastContext'

const PROGRESS_INTERVAL_SECONDS = 10

export default function Watch() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { notify } = useToast()

  const [video, setVideo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [engagementId, setEngagementId] = useState(null)
  const [elapsed, setElapsed] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [completed, setCompleted] = useState(false)
  const [related, setRelated] = useState([])
  const [pauseCount, setPauseCount] = useState(0)

  const elapsedRef = useRef(0)
  const engagementRef = useRef(null)
  const lastSyncRef = useRef(0)
  const seekCountRef = useRef(0)
  const endedRef = useRef(false)
  const startedForIdRef = useRef(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    videoService.getVideo(id).then((v) => {
      if (cancelled) return
      setVideo(v)
      videoService.categoryVideos(v.category_id, { per_page: 8 }).then((data) => {
        if (!cancelled) setRelated(data.items.filter((r) => r.id !== Number(id)))
      })
    }).finally(() => !cancelled && setLoading(false))

    if (startedForIdRef.current !== id) {
      startedForIdRef.current = id
      watchService.startWatch(id).then((data) => {
        if (cancelled) return
        setEngagementId(data.engagement_id)
        engagementRef.current = data.engagement_id
        setIsPlaying(true)
      })
    }

    return () => {
      cancelled = true
      finalizeSession()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  useEffect(() => {
    if (!isPlaying || !video || completed) return
    const timer = setInterval(() => {
      const next = Math.min(elapsedRef.current + 1, video.duration)
      elapsedRef.current = next
      setElapsed(next)
      if (next - lastSyncRef.current >= PROGRESS_INTERVAL_SECONDS) {
        syncProgress(next)
      }
      if (next >= video.duration) {
        handleComplete(next)
      }
    }, 1000)
    return () => clearInterval(timer)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isPlaying, video, completed])

  async function syncProgress(elapsedSeconds) {
    if (!engagementRef.current || !video) return
    lastSyncRef.current = elapsedSeconds
    const completionRate = Math.min(100, (elapsedSeconds / video.duration) * 100)
    try {
      await watchService.sendProgress(engagementRef.current, elapsedSeconds, completionRate, seekCountRef.current)
      seekCountRef.current = 0
    } catch {
      // best-effort - the next periodic sync will retry with the latest elapsed time
    }
  }

  async function handlePause() {
    setIsPlaying(false)
    if (!engagementRef.current) return
    setPauseCount((c) => c + 1)
    await syncProgress(elapsedRef.current)
    try {
      await watchService.sendPause(engagementRef.current)
    } catch {
      // ignore
    }
  }

  function handleResume() {
    setIsPlaying(true)
  }

  async function handleComplete(finalElapsed) {
    setIsPlaying(false)
    setCompleted(true)
    if (!engagementRef.current) return
    try {
      await syncProgress(finalElapsed)
      await watchService.sendComplete(engagementRef.current)
      notify('Video completed - added to your history')
    } catch {
      // ignore
    }
  }

  async function finalizeSession() {
    if (endedRef.current || !engagementRef.current) return
    endedRef.current = true
    try {
      await watchService.sendEnd(engagementRef.current)
    } catch {
      // ignore - best effort cleanup
    }
  }

  async function handleReplay() {
    endedRef.current = false
    setCompleted(false)
    setElapsed(0)
    elapsedRef.current = 0
    lastSyncRef.current = 0
    const data = await watchService.startWatch(id)
    setEngagementId(data.engagement_id)
    engagementRef.current = data.engagement_id
    setIsPlaying(true)
  }

  function handleSeek(e) {
    const value = Number(e.target.value)
    seekCountRef.current += 1
    setElapsed(value)
    elapsedRef.current = value
  }

  if (loading || !video) return <PageLoading />

  const progressPct = video.duration ? (elapsed / video.duration) * 100 : 0

  return (
    <div>
      <div className="ss-card" style={{ marginBottom: '1.5rem' }}>
        <div
          style={{
            aspectRatio: '16 / 9',
            background: '#000',
            borderRadius: 10,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '1rem',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          <img
            src={video.thumbnail_url}
            alt={video.title}
            style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', opacity: 0.35 }}
          />
          <button
            className="ss-btn ss-btn-primary"
            style={{ position: 'relative', fontSize: '1.1rem', padding: '0.8rem 1.6rem', borderRadius: '50%' }}
            onClick={completed ? handleReplay : isPlaying ? handlePause : handleResume}
          >
            {completed ? '↺' : isPlaying ? '⏸' : '▶'}
          </button>
        </div>

        <input
          type="range"
          min={0}
          max={video.duration}
          value={elapsed}
          onChange={handleSeek}
          style={{ width: '100%', accentColor: 'var(--accent)' }}
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
          <span>{formatClock(elapsed)}</span>
          <span>{formatClock(video.duration)}</span>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem' }}>
          <div>
            <h1 style={{ fontSize: '1.3rem', margin: 0 }}>{video.title}</h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', margin: '0.25rem 0 0' }}>
              {video.category?.name} • Pauses: {pauseCount} • {completed ? 'Completed' : `${Math.round(progressPct)}% watched`}
            </p>
          </div>
          <button className="ss-btn ss-btn-outline ss-btn-sm" onClick={() => navigate(-1)}>
            Back
          </button>
        </div>
      </div>

      {completed && (
        <>
          <div className="ss-section-title">Up Next</div>
          <VideoGrid videos={related} />
        </>
      )}
    </div>
  )
}
