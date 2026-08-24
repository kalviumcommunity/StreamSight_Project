import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import * as videoService from '../services/videoService'
import * as watchService from '../services/watchService'
import VideoGrid from '../components/VideoGrid'
import { formatDuration } from '../utils/format'
import { PageLoading } from '../components/Loading'

export default function Home() {
  const [featured, setFeatured] = useState(null)
  const [trending, setTrending] = useState([])
  const [continueWatching, setContinueWatching] = useState([])
  const [recommended, setRecommended] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      const results = await Promise.allSettled([
        videoService.featuredContent(),
        videoService.homeTrending({ period: 'weekly', limit: 10 }),
        watchService.continueWatching(10),
        videoService.recommendedForUser({ limit: 10 }),
        videoService.listCategories(),
      ])
      if (cancelled) return
      const [f, t, cw, rec, cats] = results
      setFeatured(f.status === 'fulfilled' ? f.value : null)
      setTrending(t.status === 'fulfilled' ? t.value : [])
      setContinueWatching(cw.status === 'fulfilled' ? cw.value : [])
      setRecommended(rec.status === 'fulfilled' ? rec.value : [])
      setCategories(cats.status === 'fulfilled' ? cats.value : [])
      setLoading(false)
    }
    load()
    return () => { cancelled = true }
  }, [])

  if (loading) return <PageLoading />

  return (
    <div>
      {featured && (
        <div className="ss-hero">
          <div style={{ maxWidth: 600 }}>
            <div className="ss-badge ss-badge-info" style={{ marginBottom: '0.75rem' }}>Featured</div>
            <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{featured.title}</h1>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>{featured.description}</p>
            <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              <span>{featured.category?.name}</span>
              <span>•</span>
              <span>{formatDuration(featured.duration)}</span>
            </div>
            <button className="ss-btn ss-btn-primary" onClick={() => navigate(`/watch/${featured.id}`)}>
              ▶ Watch Now
            </button>
          </div>
        </div>
      )}

      {continueWatching.length > 0 && (
        <section style={{ marginBottom: '2rem' }}>
          <div className="ss-section-title">
            Continue Watching
            <Link to="/continue-watching" style={{ fontSize: '0.8rem', color: 'var(--accent)' }}>See all</Link>
          </div>
          <VideoGrid videos={continueWatching} horizontal />
        </section>
      )}

      <section style={{ marginBottom: '2rem' }}>
        <div className="ss-section-title">Trending Now</div>
        <VideoGrid
          videos={trending.map((t) => ({
            id: t.video_id, title: t.title, category: t.category, duration: t.duration,
            views: t.views, thumbnail_url: t.thumbnail_url,
          }))}
          horizontal
        />
      </section>

      {recommended.length > 0 && (
        <section style={{ marginBottom: '2rem' }}>
          <div className="ss-section-title">Recommended For You</div>
          <VideoGrid
            videos={recommended.map((t) => ({
              id: t.video_id, title: t.title, category: t.category, duration: t.duration,
              views: t.views, thumbnail_url: t.thumbnail_url,
            }))}
            horizontal
          />
        </section>
      )}

      <section>
        <div className="ss-section-title">Browse Categories</div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.6rem' }}>
          {categories.map((c) => (
            <div
              key={c.id}
              className="ss-badge ss-badge-neutral"
              style={{ cursor: 'pointer', padding: '0.5rem 1rem', fontSize: '0.85rem' }}
              onClick={() => navigate(`/browse?category_id=${c.id}`)}
            >
              {c.name}
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
