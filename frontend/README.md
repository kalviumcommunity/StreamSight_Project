# StreamSight Frontend

React + Vite frontend for StreamSight - a streaming platform paired with an
analytics dashboard for content acquisition teams. Talks to the Flask backend
exclusively over REST; contains no business-logic calculations (retention
scores, trending scores, drop-off buckets, acquisition recommendations are all
computed server-side and only visualized here).

## Tech Stack

React 18, Vite, React Router, Bootstrap 5 (base resets/utilities) + a custom
dark streaming theme (`src/index.css`), Axios, Recharts.

## Setup

```bash
cd frontend
npm install
cp .env.example .env    # points at the backend API, defaults to localhost:5000/api
npm run dev
```

Runs on `http://localhost:5173`. The backend must be running (see
`../backend/README.md`) and seeded so there's data to browse and chart.

## Structure

```
src/
  components/   Shared UI: Navbar, Sidebar, VideoCard/Grid, DataTable, ChartCard,
                MetricCard, Modal, ProtectedRoute (RequireAuth/RequireAdmin),
                UserLayout / AdminLayout, Loading & error/empty states
  pages/        One file per route - viewer-facing (Home, Browse, Watch, ...)
                and admin analytics (AdminDashboard, ContentAnalytics,
                ViewerAnalytics, CategoryAnalytics, SearchAnalytics,
                AcquisitionInsights, ContentManagement)
  services/     Axios wrappers per backend resource (auth, video, watch,
                analytics) - the only place that knows API routes/shapes
  context/      AuthContext (JWT + current user) and ToastContext (notifications)
  hooks/        useDebounce
  utils/        format.js (duration/date/percent formatting),
                chartColors.js (validated categorical/status palette)
```

## Auth & routing

JWT is stored in `localStorage` and attached to every request by an Axios
interceptor (`services/api.js`), which also redirects to `/login` on a 401.
`RequireAuth` gates all viewer routes; `RequireAdmin` additionally checks
`user.role === 'ADMIN'` and gates everything under `/admin/*`.

## Video playback & engagement tracking

`pages/Watch.jsx` simulates playback with a 1-second ticking timer (no real
video CDN is assumed) and calls the watch-tracking API in the same shape a
real `<video>` element's event handlers would: `watch/start` on mount,
`watch/progress` batched every 10 seconds (not on every tick), `watch/pause`
on pause, `watch/complete` at 100%, and `watch/end` on unmount/navigation away.

## Design

Dark, card-based streaming aesthetic driven entirely by CSS custom properties
in `src/index.css` (`--bg-*`, `--accent`, `--positive`/`--warning`/`--danger`).
Chart series colors in `utils/chartColors.js` are the data-viz skill's
categorical palette, re-validated against this app's actual dark chart surface
(`#14171f`) rather than assumed.

## Build

```bash
npm run build      # outputs to dist/
npm run preview    # serve the production build locally
```
