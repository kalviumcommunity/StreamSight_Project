from tests.conftest import auth_headers


def test_list_videos_public(client, video):
    resp = client.get("/api/videos")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total"] == 1


def test_get_video_not_found(client):
    resp = client.get("/api/videos/999")
    assert resp.status_code == 404


def test_create_video_requires_admin(client, category, user_token):
    resp = client.post("/api/videos", json={
        "title": "New Video", "category_id": category, "duration": 1000,
    }, headers=auth_headers(user_token))
    assert resp.status_code == 403


def test_create_video_as_admin(client, category, admin_token):
    resp = client.post("/api/videos", json={
        "title": "Admin Video", "category_id": category, "duration": 1000,
    }, headers=auth_headers(admin_token))
    assert resp.status_code == 201
    assert resp.get_json()["title"] == "Admin Video"


def test_create_video_invalid_category(client, admin_token):
    resp = client.post("/api/videos", json={
        "title": "Bad Cat", "category_id": 999, "duration": 1000,
    }, headers=auth_headers(admin_token))
    assert resp.status_code == 422


def test_deactivate_video(client, admin_token, video):
    resp = client.delete(f"/api/videos/{video}", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    resp = client.get(f"/api/videos/{video}")
    assert resp.status_code == 404
