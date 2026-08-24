import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'

export default function UserLayout() {
  return (
    <div className="app-shell">
      <Navbar />
      <main className="ss-main" style={{ maxWidth: 1400, margin: '0 auto', width: '100%' }}>
        <Outlet />
      </main>
    </div>
  )
}
