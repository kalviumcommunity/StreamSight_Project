import { useEffect, useState } from 'react'
import * as watchService from '../services/watchService'
import VideoGrid from '../components/VideoGrid'
import { PageLoading } from '../components/Loading'

export default function ContinueWatching() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    watchService.continueWatching(50).then(setItems).finally(() => setLoading(false))
  }, [])

  if (loading) return <PageLoading />

  return (
    <div>
      <div className="ss-section-title">Continue Watching</div>
      <VideoGrid videos={items} emptyTitle="Nothing to continue - start watching something!" />
    </div>
  )
}
