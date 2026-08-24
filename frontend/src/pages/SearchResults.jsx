import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import * as videoService from '../services/videoService'
import VideoGrid from '../components/VideoGrid'
import CategoryFilter from '../components/CategoryFilter'
import { EmptyState } from '../components/ErrorMessage'
import { apiErrorMessage } from '../services/api'

export default function SearchResults() {
  const [searchParams] = useSearchParams()
  const q = searchParams.get('q') || ''
  const [videos, setVideos] = useState([])
  const [categories, setCategories] = useState([])
  const [categoryId, setCategoryId] = useState('')
  const [sort, setSort] = useState('relevance')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    videoService.listCategories().then(setCategories).catch(() => {})
  }, [])

  useEffect(() => {
    if (!q) {
      setVideos([])
      setLoading(false)
      return
    }
    let cancelled = false
    setLoading(true)
    setError('')
    videoService
      .searchVideos(q, { category_id: categoryId || undefined, sort, per_page: 30 })
      .then((data) => !cancelled && setVideos(data.items))
      .catch((err) => !cancelled && setError(apiErrorMessage(err)))
      .finally(() => !cancelled && setLoading(false))
    return () => { cancelled = true }
  }, [q, categoryId, sort])

  return (
    <div>
      <div className="ss-section-title">
        Search results for "{q}"
        <div style={{ display: 'flex', gap: '0.6rem' }}>
          <CategoryFilter categories={categories} value={categoryId} onChange={setCategoryId} />
          <select className="ss-select" style={{ width: 'auto' }} value={sort} onChange={(e) => setSort(e.target.value)}>
            <option value="relevance">Relevance</option>
            <option value="views">Most Viewed</option>
            <option value="newest">Newest</option>
          </select>
        </div>
      </div>

      {!q ? (
        <EmptyState title="Type something to search" />
      ) : error ? (
        <EmptyState title={error} />
      ) : (
        <VideoGrid videos={videos} loading={loading} emptyTitle={`No results for "${q}"`} />
      )}
    </div>
  )
}
