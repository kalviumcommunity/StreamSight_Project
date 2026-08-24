def test_search_requires_query(client):
    resp = client.get("/api/search")
    assert resp.status_code == 422


def test_search_finds_video_and_tracks_activity(client, video, app):
    resp = client.get("/api/search?q=Test")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total"] == 1

    from app.models import SearchActivity
    with app.app_context():
        assert SearchActivity.query.count() == 1


def test_search_no_results(client, video):
    resp = client.get("/api/search?q=NoMatchAtAll")
    assert resp.status_code == 200
    assert resp.get_json()["total"] == 0
