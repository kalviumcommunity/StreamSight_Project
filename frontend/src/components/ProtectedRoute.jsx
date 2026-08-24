import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { PageLoading } from './Loading'

export function RequireAuth() {
  const { isAuthenticated, loading } = useAuth()
  if (loading) return <PageLoading />
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />
}

export function RequireAdmin() {
  const { isAuthenticated, isAdmin, loading } = useAuth()
  if (loading) return <PageLoading />
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return isAdmin ? <Outlet /> : <Navigate to="/" replace />
}
