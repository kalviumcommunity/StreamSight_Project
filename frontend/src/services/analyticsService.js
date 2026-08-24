import api from './api'

export async function dashboardOverview() {
  const { data } = await api.get('/dashboard/overview')
  return data
}

export async function analyticsSummary(params = {}) {
  const { data } = await api.get('/analytics/summary', { params })
  return data
}

export async function contentPerformance(params = {}) {
  const { data } = await api.get('/analytics/content', { params })
  return data
}

export async function dropoffAnalysis(params = {}) {
  const { data } = await api.get('/analytics/dropoff', { params })
  return data
}

export async function trendingContent(params = {}) {
  const { data } = await api.get('/analytics/trending', { params })
  return data
}

export async function categoryAnalytics(params = {}) {
  const { data } = await api.get('/analytics/categories', { params })
  return data
}

export async function searchAnalytics(params = {}) {
  const { data } = await api.get('/analytics/searches', { params })
  return data
}

export async function searchTrends(params = {}) {
  const { data } = await api.get('/analytics/search-trends', { params })
  return data
}

export async function engagementTrends(params = {}) {
  const { data } = await api.get('/analytics/trends', { params })
  return data
}

export async function acquisitionInsights(params = {}) {
  const { data } = await api.get('/analytics/acquisition-insights', { params })
  return data
}

export async function listUsers(params = {}) {
  const { data } = await api.get('/users', { params })
  return data
}

export async function listEngagement(params = {}) {
  const { data } = await api.get('/admin/engagement', { params })
  return data
}

export async function importEngagementFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post('/admin/import/engagement', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}
