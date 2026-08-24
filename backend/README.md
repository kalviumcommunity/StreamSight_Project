# StreamSight Backend

Flask REST API for StreamSight, a subscription-streaming analytics platform. It powers
a simplified viewer-facing streaming experience and an analytics engine that helps
content acquisition teams understand which engagement patterns correlate with retention.

## Tech Stack

Python 3.11+, Flask, SQLAlchemy, Flask-JWT-Extended, Flask-CORS, SQLite (dev) /
PostgreSQL-ready, Pandas + NumPy for analytics, Marshmallow-style manual validation,
pytest.

## Setup

```bash
cd backend
python -m venv venv
source venv/Scripts/activate      # Windows Git Bash
# venv\Scripts\activate.bat       # Windows cmd
# source venv/bin/activate        # macOS/Linux

pip install -r requirements.txt
cp .env.example .env              # then edit secrets as needed
```

## Initialize & seed the database

```bash
python seed/seed_data.py
```

This drops and recreates all tables, then inserts categories, videos, an admin
account, ~30 demo viewers with realistic (not random) engagement profiles, watch
history, bookmarks, and search activity.

- Admin login: `admin@streamsight.io` / `Admin123!`
- Demo viewer logins: `<name><n>@streamsight.io` / `Password123!` (see console output)

## Run the server

```bash
python run.py
```

Server starts on `http://localhost:5000`. Health check: `GET /api/health`.

## Run tests

```bash
pytest
pytest tests/test_watch.py            # single file
pytest tests/test_watch.py::test_full_watch_lifecycle   # single test
```

Tests run against an in-memory SQLite database (`testing` config) and never touch
`streamsight.db`.

## Architecture

```
app/
  config.py          Environment-driven config (dev/testing)
  extensions.py       SQLAlchemy, JWT, CORS, Migrate singletons
  models/              One file per table, each with to_dict()
  routes/               Thin Flask blueprints - request parsing + response only
  services/             Business logic (engagement recording, analytics engine,
                         retention scoring, recommendations, dataset import)
  utils/                 Validators, role-based decorators, pagination/date
                         helpers, centralized error types
seed/seed_data.py      Realistic demo data generator
tests/                 pytest suite (auth, videos, watch, bookmarks, search,
                        analytics, admin)
```

Business logic is intentionally kept out of route handlers. Routes validate
input, call a service function, and serialize the result.

### Engagement-Based Retention Score

A transparent, weighted composite of engagement signals (0-100) - **not** a
scientifically validated prediction model. See `app/services/retention_service.py`
for the full formula and documentation.

```
Retention Score = (
    normalized_watch_duration   * 0.35 +
    normalized_completion_rate  * 0.35 +
    normalized_session_duration * 0.20 +
    normalized_repeat_views     * 0.10
) * 100
```

### Acquisition insight classification

Content is classified into **Strong Acquisition Candidate**, **Needs Investigation**,
or **Hidden Performer** based on completion rate, pause frequency, retention score,
repeat viewing, and early drop-off - computed from live database values, never
hardcoded. See `classify_acquisition_recommendation` in `retention_service.py`.

## API Documentation

All endpoints are prefixed with `/api`. JWT auth uses `Authorization: Bearer <token>`.
Admin-only endpoints require a user with `role: ADMIN`.

### Auth

| Method | URL | Auth | Body | Notes |
|---|---|---|---|---|
| POST | `/api/auth/register` | none | `{name, email, password}` | 201 on success, 409 if email exists, 422 on validation failure |
| POST | `/api/auth/login` | none | `{email, password}` | Returns `{user, access_token}`, 401 on bad credentials |
| GET | `/api/auth/me` | required | - | Returns current user |
| POST | `/api/auth/logout` | required | - | Stateless; client discards token |

### Users

| Method | URL | Auth | Query | Notes |
|---|---|---|---|---|
| GET | `/api/users` | admin | `page, per_page` | Paginated user list |

### Categories

| Method | URL | Auth | Body/Query | Notes |
|---|---|---|---|---|
| GET | `/api/categories` | none | - | All categories |
| GET | `/api/categories/:id` | none | - | 404 if missing |
| GET | `/api/categories/:id/videos` | none | `page, per_page` | Active videos in category |
| POST | `/api/categories` | admin | `{name, description}` | 409 if name exists |
| PUT | `/api/categories/:id` | admin | `{name?, description?}` | |
| DELETE | `/api/categories/:id` | admin | - | |

### Videos

| Method | URL | Auth | Query/Body | Notes |
|---|---|---|---|---|
| GET | `/api/videos` | none | `page, per_page, search, category_id, sort=newest|views|title|duration` | Active videos only |
| GET | `/api/videos/:id` | none | - | 404 if inactive/missing |
| POST | `/api/videos` | admin | `{title, category_id, duration, description?, thumbnail_url?, video_url?, release_date?}` | |
| PUT | `/api/videos/:id` | admin | any subset of above + `is_active` | |
| DELETE | `/api/videos/:id` | admin | - | Soft delete (`is_active=false`) |

### Search

| Method | URL | Auth | Query | Notes |
|---|---|---|---|---|
| GET | `/api/search` | optional | `q (required), category_id, sort, page, per_page` | Every search is recorded to `SearchActivity` |

### Watch Tracking

| Method | URL | Auth | Body | Notes |
|---|---|---|---|---|
| POST | `/api/watch/start` | required | `{video_id}` | Creates session + engagement, increments video views |
| POST | `/api/watch/progress` | required | `{engagement_id, watch_duration, completion_rate, seek_count?}` | Periodic update from player |
| POST | `/api/watch/pause` | required | `{engagement_id}` | Increments pause_count |
| POST | `/api/watch/complete` | required | `{engagement_id}` | Sets completion to 100%, marks history completed |
| POST | `/api/watch/end` | required | `{engagement_id}` | Closes session, computes session_duration |

All watch endpoints 404 if the engagement doesn't belong to the caller.
`watch_duration` must be >= 0; `completion_rate` must be 0-100 (422 otherwise).

### History & Bookmarks

| Method | URL | Auth | Notes |
|---|---|---|---|
| GET | `/api/history` | required | Paginated, newest first |
| DELETE | `/api/history/:id` | required | 404 if not owned |
| GET | `/api/history/continue-watching` | required | `0 < completion_rate < 90`, most recent first |
| GET | `/api/bookmarks` | required | |
| POST | `/api/bookmarks/:video_id` | required | 409 if already bookmarked |
| DELETE | `/api/bookmarks/:video_id` | required | |

### Home (public-facing recommendations)

| Method | URL | Auth | Notes |
|---|---|---|---|
| GET | `/api/home/featured` | none | Highest-viewed active video |
| GET | `/api/home/trending` | none | `period=daily|weekly|monthly, limit` |
| GET | `/api/home/recommended` | required | Trending content in the user's watched categories, excluding completed videos |

### Analytics (admin only)

| Method | URL | Query | Returns |
|---|---|---|---|
| GET | `/api/analytics/summary` | `date_from, date_to, category_id, video_id` | total_views, average_watch_time, average_completion_rate, average_pause_frequency |
| GET | `/api/analytics/content` | same | Per-video performance incl. retention score, replay rate, bookmarks |
| GET | `/api/analytics/dropoff` | same | Viewer counts/percentages in 5 completion buckets |
| GET | `/api/analytics/trending` | `period, limit` | Ranked trending content |
| GET | `/api/analytics/categories` | `date_from, date_to` | Per-category engagement + retention |
| GET | `/api/analytics/searches` | `limit` | Top keywords, top searched categories |
| GET | `/api/analytics/search-trends` | `period` | Search volume over time + zero-result queries |
| GET | `/api/analytics/trends` | `period, date_from, date_to` | Time-series views/watch-time/completion/pause/retention |
| GET | `/api/analytics/acquisition-insights` | `date_from, date_to` | Strong/Needs-Investigation/Hidden-Performer buckets + text summary |

`date_from`/`date_to` are ISO datetimes; defaults to the trailing 30 days.

### Dashboard

| Method | URL | Auth | Notes |
|---|---|---|---|
| GET | `/api/dashboard/overview` | admin | One aggregated payload: totals, top content, trending, category performance, drop-off, recent trends |

### Admin data management

| Method | URL | Auth | Body | Notes |
|---|---|---|---|---|
| GET | `/api/admin/engagement` | admin | `page, per_page` | Raw engagement rows |
| POST | `/api/admin/import/engagement` | admin | multipart `file` (CSV/JSON/XLSX) | Validates, dedupes, and imports engagement rows; returns a report with total/valid/invalid counts, missing values, duplicates, and per-row validation failures |

### Error format

All errors return `{"error": "message"}` (optionally with a `details` field) and one
of: `400, 401, 403, 404, 409, 422, 500`.
