import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { apiErrorMessage } from '../services/api'
import { EyeIcon, EyeOffIcon } from '../components/PasswordIcons'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!email || !password) {
      setError('Please enter both email and password')
      return
    }
    setLoading(true)
    try {
      const user = await login(email, password)
      const redirectTo = location.state?.from || (user.role === 'ADMIN' ? '/admin/dashboard' : '/')
      navigate(redirectTo, { replace: true })
    } catch (err) {
      setError(apiErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="ss-auth-shell">
      <div className="ss-auth-card">
        <div className="ss-brand" style={{ fontSize: '1.5rem', marginBottom: '1.5rem', justifyContent: 'center' }}>
          Stream<span>Sight</span>
        </div>
        <h1 style={{ fontSize: '1.15rem', marginBottom: '1.25rem' }}>Sign in to your account</h1>

        {error && (
          <div className="ss-badge ss-badge-danger" style={{ display: 'block', marginBottom: '1rem', padding: '0.6rem' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="ss-form-group">
            <label className="ss-label">Email</label>
            <input className="ss-input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoFocus />
          </div>
          <div className="ss-form-group">
            <label className="ss-label">Password</label>
            <div className="ss-password-wrap">
              <input
                className="ss-input"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button
                type="button"
                className="ss-password-toggle"
                onClick={() => setShowPassword((s) => !s)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                tabIndex={-1}
              >
                {showPassword ? <EyeOffIcon /> : <EyeIcon />}
              </button>
            </div>
          </div>
          <button className="ss-btn ss-btn-primary" style={{ width: '100%' }} disabled={loading} type="submit">
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p style={{ marginTop: '1.25rem', fontSize: '0.85rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
          Don't have an account? <Link to="/register" style={{ color: 'var(--accent)' }}>Create an Account</Link>
        </p>
      </div>
    </div>
  )
}
