import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import * as authService from '../services/authService'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const cached = localStorage.getItem('streamsight_user')
    return cached ? JSON.parse(cached) : null
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('streamsight_token')
    if (!token) {
      setLoading(false)
      return
    }
    authService
      .fetchCurrentUser()
      .then((data) => {
        setUser(data)
        localStorage.setItem('streamsight_user', JSON.stringify(data))
      })
      .catch(() => {
        localStorage.removeItem('streamsight_token')
        localStorage.removeItem('streamsight_user')
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [])

  const login = useCallback(async (email, password) => {
    const data = await authService.login(email, password)
    localStorage.setItem('streamsight_token', data.access_token)
    localStorage.setItem('streamsight_user', JSON.stringify(data.user))
    setUser(data.user)
    return data.user
  }, [])

  const register = useCallback(async (name, email, password) => {
    const data = await authService.register(name, email, password)
    localStorage.setItem('streamsight_token', data.access_token)
    localStorage.setItem('streamsight_user', JSON.stringify(data.user))
    setUser(data.user)
    return data.user
  }, [])

  const logout = useCallback(async () => {
    await authService.logout()
    localStorage.removeItem('streamsight_token')
    localStorage.removeItem('streamsight_user')
    setUser(null)
  }, [])

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'ADMIN',
    login,
    register,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
