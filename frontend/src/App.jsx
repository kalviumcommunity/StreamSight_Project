import { Routes, Route, Navigate } from 'react-router-dom'
import { RequireAuth, RequireAdmin } from './components/ProtectedRoute'
import UserLayout from './components/UserLayout'
import AdminLayout from './components/AdminLayout'

import Login from './pages/Login'
import Register from './pages/Register'
import Home from './pages/Home'
import Browse from './pages/Browse'
import VideoDetails from './pages/VideoDetails'
import Watch from './pages/Watch'
import History from './pages/History'
import ContinueWatching from './pages/ContinueWatching'
import Bookmarks from './pages/Bookmarks'
import SearchResults from './pages/SearchResults'

import AdminDashboard from './pages/AdminDashboard'
import ContentAnalytics from './pages/ContentAnalytics'
import ViewerAnalytics from './pages/ViewerAnalytics'
import CategoryAnalytics from './pages/CategoryAnalytics'
import SearchAnalytics from './pages/SearchAnalytics'
import AcquisitionInsights from './pages/AcquisitionInsights'
import ContentManagement from './pages/ContentManagement'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route element={<RequireAuth />}>
        <Route element={<UserLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/browse" element={<Browse />} />
          <Route path="/videos/:id" element={<VideoDetails />} />
          <Route path="/watch/:id" element={<Watch />} />
          <Route path="/history" element={<History />} />
          <Route path="/continue-watching" element={<ContinueWatching />} />
          <Route path="/bookmarks" element={<Bookmarks />} />
          <Route path="/search" element={<SearchResults />} />
        </Route>
      </Route>

      <Route element={<RequireAdmin />}>
        <Route element={<AdminLayout />}>
          <Route path="/admin/dashboard" element={<AdminDashboard />} />
          <Route path="/admin/content" element={<ContentAnalytics />} />
          <Route path="/admin/viewers" element={<ViewerAnalytics />} />
          <Route path="/admin/categories" element={<CategoryAnalytics />} />
          <Route path="/admin/search" element={<SearchAnalytics />} />
          <Route path="/admin/acquisition" element={<AcquisitionInsights />} />
          <Route path="/admin/manage" element={<ContentManagement />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
