from app.extensions import db
from app.models import Engagement, WatchSession
from app.services.retention_service import calculate_retention_score
from tests.conftest import auth_headers


def _seed_engagement(app, user_id, video_id, watch_duration, completion_rate, pause_count=0, replay_count=0):
    with app.app_context():
        session = WatchSession(user_id=user_id, session_duration=watch_duration + 30)
        db.session.add(session)
        db.session.flush()
        engagement = Engagement(
            user_id=user_id, video_id=video_id, session_id=session.id,
            watch_duration=watch_duration, completion_rate=completion_rate,
            pause_count=pause_count, replay_count=replay_count,
        )
        db.session.add(engagement)
        db.session.commit()


def test_retention_score_is_bounded():
    score = calculate_retention_score(
        avg_watch_duration=1200, avg_video_duration=1200, avg_completion_rate=100,
        avg_session_duration=3600, repeat_view_count=3,
    )
    assert score == 100.0

    zero_score = calculate_retention_score(0, 1200, 0, 0, 0)
    assert zero_score == 0.0


def test_content_performance_endpoint(app, client, admin_token, video):
    from app.models import User, Role
    with app.app_context():
        viewer = User(name="Viewer", email="viewer@example.com", role=Role.USER)
        viewer.set_password("Password123!")
        db.session.add(viewer)
        db.session.commit()
        viewer_id = viewer.id

    _seed_engagement(app, viewer_id, video, watch_duration=1100, completion_rate=95, pause_count=1)

    resp = client.get("/api/analytics/content", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    body = resp.get_json()
    assert len(body) == 1
    assert body[0]["total_views"] == 1
    assert body[0]["average_completion_rate"] == 95


def test_dropoff_analysis_buckets(app, client, admin_token, video):
    from app.models import User, Role
    with app.app_context():
        viewer = User(name="Viewer2", email="viewer2@example.com", role=Role.USER)
        viewer.set_password("Password123!")
        db.session.add(viewer)
        db.session.commit()
        viewer_id = viewer.id

    _seed_engagement(app, viewer_id, video, watch_duration=100, completion_rate=10)

    resp = client.get("/api/analytics/dropoff", headers=admin_token and {"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    buckets = {b["range"]: b for b in resp.get_json()}
    assert buckets["0-25%"]["viewers"] == 1


def test_analytics_requires_admin(client, user_token):
    resp = client.get("/api/analytics/content", headers=auth_headers(user_token))
    assert resp.status_code == 403
