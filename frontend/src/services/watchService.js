import api from './api'

export async function startWatch(videoId) {
  const { data } = await api.post('/watch/start', { video_id: videoId })
  return data
}

export async function sendProgress(engagementId, watchDuration, completionRate, seekCount) {
  const { data } = await api.post('/watch/progress', {
    engagement_id: engagementId,
    watch_duration: watchDuration,
    completion_rate: completionRate,
    seek_count: seekCount,
  })
  return data
}

export async function sendPause(engagementId) {
  const { data } = await api.post('/watch/pause', { engagement_id: engagementId })
  return data
}

export async function sendComplete(engagementId) {
  const { data } = await api.post('/watch/complete', { engagement_id: engagementId })
  return data
}

export async function sendEnd(engagementId) {
  const { data } = await api.post('/watch/end', { engagement_id: engagementId })
  return data
}

export async function fetchHistory(params = {}) {
  const { data } = await api.get('/history', { params })
  return data
}

export async function deleteHistoryEntry(id) {
  const { data } = await api.delete(`/history/${id}`)
  return data
}

export async function continueWatching(limit = 10) {
  const { data } = await api.get('/history/continue-watching', { params: { limit } })
  return data
}

export async function listBookmarks() {
  const { data } = await api.get('/bookmarks')
  return data
}

export async function addBookmark(videoId) {
  const { data } = await api.post(`/bookmarks/${videoId}`)
  return data
}

export async function removeBookmark(videoId) {
  const { data } = await api.delete(`/bookmarks/${videoId}`)
  return data
}
