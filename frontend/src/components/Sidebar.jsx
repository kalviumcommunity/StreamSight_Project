import { NavLink } from 'react-router-dom'

const LINKS = [
  { to: '/admin/dashboard', label: 'Overview', icon: '📊' },
  { to: '/admin/content', label: 'Content Performance', icon: '🎬' },
  { to: '/admin/viewers', label: 'Viewer Engagement', icon: '👥' },
  { to: '/admin/categories', label: 'Category Analytics', icon: '🗂' },
  { to: '/admin/search', label: 'Search Analytics', icon: '🔍' },
  { to: '/admin/acquisition', label: 'Acquisition Insights', icon: '💡' },
  { to: '/admin/manage', label: 'Content Management', icon: '⚙️' },
]

export default function Sidebar() {
  return (
    <aside className="ss-sidebar">
      {LINKS.map((link) => (
        <NavLink key={link.to} to={link.to} className={({ isActive }) => (isActive ? 'active' : '')}>
          <span>{link.icon}</span> {link.label}
        </NavLink>
      ))}
    </aside>
  )
}
