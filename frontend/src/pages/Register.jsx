import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { apiErrorMessage } from '../services/api'
import { EyeIcon, EyeOffIcon } from '../components/PasswordIcons'

export default function Register() {
  const [form, setForm] = useState({ name: '', email: '', password: '', confirmPassword: '' })
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (!form.name || !form.email || !form.password) {
      setError('All fields are required')
      return
    }
    if (form.password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }
    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    setLoading(true)
    try {
      await register(form.name, form.email, form.password)
      navigate('/', { replace: true })
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
        <h1 style={{ fontSize: '1.15rem', marginBottom: '1.25rem' }}>Create your account</h1>

        {error && (
          <div className="ss-badge ss-badge-danger" style={{ display: 'block', marginBottom: '1rem', padding: '0.6rem' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="ss-form-group">
            <label className="ss-label">Name</label>
            <input className="ss-input" value={form.name} onChange={(e) => update('name', e.target.value)} autoFocus />
          </div>
          <div className="ss-form-group">
            <label className="ss-label">Email</label>
            <input className="ss-input" type="email" value={form.email} onChange={(e) => update('email', e.target.value)} />
          </div>
          <div className="ss-form-group">
            <label className="ss-label">Password</label>
            <div className="ss-password-wrap">
              <input
                className="ss-input"
                type={showPassword ? 'text' : 'password'}
                value={form.password}
                onChange={(e) => update('password', e.target.value)}
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
          <div className="ss-form-group">
            <label className="ss-label">Confirm Password</label>
            <div className="ss-password-wrap">
              <input
                className="ss-input"
                type={showConfirmPassword ? 'text' : 'password'}
                value={form.confirmPassword}
                onChange={(e) => update('confirmPassword', e.target.value)}
              />
              <button
                type="button"
                className="ss-password-toggle"
                onClick={() => setShowConfirmPassword((s) => !s)}
                aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                tabIndex={-1}
              >
                {showConfirmPassword ? <EyeOffIcon /> : <EyeIcon />}
              </button>
            </div>
          </div>
          <button className="ss-btn ss-btn-primary" style={{ width: '100%' }} disabled={loading} type="submit">
            {loading ? 'Creating account...' : 'Create'}
          </button>
        </form>

        <p style={{ marginTop: '1.25rem', fontSize: '0.85rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
          Already have an account? <Link to="/login" style={{ color: 'var(--accent)' }}>Sign in</Link>
        </p>
      </div>
    </div>
  )
}
