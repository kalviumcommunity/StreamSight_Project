import VideoCard from './VideoCard'
import { SkeletonGrid } from './Loading'
import { EmptyState } from './ErrorMessage'

export default function VideoGrid({ videos, loading, emptyTitle = 'No videos found', horizontal = false }) {
  if (loading) return <SkeletonGrid />
  if (!videos || videos.length === 0) return <EmptyState title={emptyTitle} />

  return (
    <div className={horizontal ? 'ss-hscroll' : 'ss-video-grid'}>
      {videos.map((v) => (
        <VideoCard key={v.id || v.video_id} video={v.video || v} progress={v.completion_rate} />
      ))}
    </div>
  )
}
