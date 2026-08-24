import api from './api'

export async function listVideos(params = {}) {
  const { data } = await api.get('/videos', { params })
  return data
}

export async function getVideo(id) {
  const { data } = await api.get(`/videos/${id}`)
  return data
}

export async function createVideo(payload) {
  const { data } = await api.post('/videos', payload)
  return data
}

export async function updateVideo(id, payload) {
  const { data } = await api.put(`/videos/${id}`, payload)
  return data
}

export async function deactivateVideo(id) {
  const { data } = await api.delete(`/videos/${id}`)
  return data
}

export async function listCategories() {
  const { data } = await api.get('/categories')
  return data
}

export async function createCategory(payload) {
  const { data } = await api.post('/categories', payload)
  return data
}

export async function categoryVideos(categoryId, params = {}) {
  const { data } = await api.get(`/categories/${categoryId}/videos`, { params })
  return data
}

export async function searchVideos(q, params = {}) {
  const { data } = await api.get('/search', { params: { q, ...params } })
  return data
}

export async function featuredContent() {
  const { data } = await api.get('/home/featured')
  return data
}

export async function homeTrending(params = {}) {
  const { data } = await api.get('/home/trending', { params })
  return data
}

export async function recommendedForUser(params = {}) {
  const { data } = await api.get('/home/recommended', { params })
  return data
}
