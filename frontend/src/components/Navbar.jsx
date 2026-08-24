import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import SearchBar from './SearchBar'

export default function Navbar() {
  const { user, isAdmin, logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/login')
  }

  return (
    <nav className="ss-navbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
        <NavLink to="/" className="ss-brand">
          Stream<span>Sight</span>
        </NavLink>
        <div className="ss-nav-links">
          <NavLink to="/" end>Home</NavLink>
          <NavLink to="/browse">Browse</NavLink>
          <NavLink to="/continue-watching">Continue Watching</NavLink>
          <NavLink to="/history">History</NavLink>
          <NavLink to="/bookmarks">Bookmarks</NavLink>
          {isAdmin && <NavLink to="/admin/dashboard">Analytics</NavLink>}
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.9rem' }}>
        <SearchBar compact />
        <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{user?.name}</span>
        <button className="ss-btn ss-btn-outline ss-btn-sm" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </nav>
  )
}
