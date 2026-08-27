import { useEffect, useRef, useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import SearchBar from './SearchBar'

function MenuIcon(props) {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <line x1="3" y1="6" x2="21" y2="6" />
      <line x1="3" y1="12" x2="21" y2="12" />
      <line x1="3" y1="18" x2="21" y2="18" />
    </svg>
  )
}

function CloseIcon(props) {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  )
}

function ChevronDownIcon(props) {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <polyline points="6 9 12 15 18 9" />
    </svg>
  )
}

function initialsOf(name) {
  if (!name) return '?'
  const parts = name.trim().split(/\s+/)
  return ((parts[0]?.[0] || '') + (parts[1]?.[0] || '')).toUpperCase() || name[0].toUpperCase()
}

const NAV_LINKS = [
  { to: '/', label: 'Home', end: true },
  { to: '/browse', label: 'Browse' },
  { to: '/continue-watching', label: 'Continue Watching' },
  { to: '/history', label: 'History' },
  { to: '/bookmarks', label: 'Bookmarks' },
]

export default function Navbar() {
  const { user, isAdmin, logout } = useAuth()
  const navigate = useNavigate()
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const userMenuRef = useRef(null)

  useEffect(() => {
    function onScroll() {
      setScrolled(window.scrollY > 4)
    }
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    function onClickOutside(e) {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target)) {
        setMenuOpen(false)
      }
    }
    function onKeyDown(e) {
      if (e.key === 'Escape') {
        setMenuOpen(false)
        setMobileOpen(false)
      }
    }
    document.addEventListener('mousedown', onClickOutside)
    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('mousedown', onClickOutside)
      document.removeEventListener('keydown', onKeyDown)
    }
  }, [])

  async function handleLogout() {
    setMenuOpen(false)
    await logout()
    navigate('/login')
  }

  const links = isAdmin ? [...NAV_LINKS, { to: '/admin/dashboard', label: 'Analytics' }] : NAV_LINKS

  return (
    <nav className={`ss-navbar${scrolled ? ' scrolled' : ''}`}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
        <button
          className="ss-navbar-toggle"
          onClick={() => setMobileOpen((o) => !o)}
          aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={mobileOpen}
        >
          {mobileOpen ? <CloseIcon /> : <MenuIcon />}
        </button>
        <NavLink to="/" className="ss-brand">
          Stream<span>Sight</span>
        </NavLink>
        <div className="ss-nav-links">
          {links.map((link) => (
            <NavLink key={link.to} to={link.to} end={link.end} className="ss-nav-link">
              {link.label}
            </NavLink>
          ))}
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.9rem' }}>
        <SearchBar compact />
        <div className="ss-user-menu" ref={userMenuRef}>
          <button className="ss-user-trigger" onClick={() => setMenuOpen((o) => !o)} aria-expanded={menuOpen}>
            <span className="ss-avatar">{initialsOf(user?.name)}</span>
            <span className="ss-user-name">{user?.name}</span>
            <ChevronDownIcon className={`ss-user-chevron${menuOpen ? ' open' : ''}`} />
          </button>
          {menuOpen && (
            <div className="ss-user-dropdown">
              <div className="ss-user-dropdown-header">
                <div className="ss-user-dropdown-name">{user?.name}</div>
                {user?.email && <div className="ss-user-dropdown-email">{user.email}</div>}
              </div>
              <button className="ss-user-dropdown-item" onClick={handleLogout}>
                Logout
              </button>
            </div>
          )}
        </div>
      </div>

      {mobileOpen && (
        <div className="ss-navbar-mobile-panel">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className="ss-nav-link"
              onClick={() => setMobileOpen(false)}
            >
              {link.label}
            </NavLink>
          ))}
        </div>
      )}
    </nav>
  )
}
