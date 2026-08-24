import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import * as videoService from '../services/videoService'
import VideoGrid from '../components/VideoGrid'
import CategoryFilter from '../components/CategoryFilter'
import ErrorMessage from '../components/ErrorMessage'
import { apiErrorMessage } from '../services/api'

export default function Browse() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [videos, setVideos] = useState([])
  const [categories, setCategories] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const categoryId = searchParams.get('category_id') || ''
  const sort = searchParams.get('sort') || 'newest'

  useEffect(() => {
    videoService.listCategories().then(setCategories).catch(() => {})
  }, [])

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError('')
    videoService
      .listVideos({ page, per_page: 20, category_id: categoryId || undefined, sort })
      .then((data) => {
        if (cancelled) return
        setVideos(data.items)
        setTotal(data.total)
      })
      .catch((err) => !cancelled && setError(apiErrorMessage(err)))
      .finally(() => !cancelled && setLoading(false))
    return () => { cancelled = true }
  }, [page, categoryId, sort])

  function updateParam(key, value) {
    const next = new URLSearchParams(searchParams)
    if (value) next.set(key, value)
    else next.delete(key)
    setSearchParams(next)
    setPage(1)
  }

  return (
    <div>
      <div className="ss-section-title">
        Browse
        <div style={{ display: 'flex', gap: '0.6rem' }}>
          <CategoryFilter categories={categories} value={categoryId} onChange={(v) => updateParam('category_id', v)} />
          <select className="ss-select" style={{ width: 'auto' }} value={sort} onChange={(e) => updateParam('sort', e.target.value)}>
            <option value="newest">Newest</option>
            <option value="views">Most Viewed</option>
            <option value="title">Title A-Z</option>
            <option value="duration">Duration</option>
          </select>
        </div>
      </div>

      {error ? (
        <ErrorMessage message={error} onRetry={() => setPage((p) => p)} />
      ) : (
        <>
          <VideoGrid videos={videos} loading={loading} />
          {total > 20 && (
            <div style={{ display: 'flex', justifyContent: 'center', gap: 10, marginTop: '1.5rem' }}>
              <button className="ss-btn ss-btn-outline ss-btn-sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                Prev
              </button>
              <span style={{ alignSelf: 'center', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Page {page} of {Math.ceil(total / 20)}
              </span>
              <button
                className="ss-btn ss-btn-outline ss-btn-sm"
                disabled={page >= Math.ceil(total / 20)}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
