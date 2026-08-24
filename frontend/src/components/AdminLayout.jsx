import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'
import Sidebar from './Sidebar'

export default function AdminLayout() {
  return (
    <div className="app-shell">
      <Navbar />
      <div className="ss-layout">
        <Sidebar />
        <main className="ss-main">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
