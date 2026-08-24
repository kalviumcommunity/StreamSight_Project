from tests.conftest import register, login, auth_headers


def test_full_watch_lifecycle(client, video):
    register(client)
    token = login(client)
    headers = auth_headers(token)

    start = client.post("/api/watch/start", json={"video_id": video}, headers=headers)
    assert start.status_code == 201
    engagement_id = start.get_json()["engagement_id"]

    progress = client.post("/api/watch/progress", json={
        "engagement_id": engagement_id, "watch_duration": 300, "completion_rate": 40,
    }, headers=headers)
    assert progress.status_code == 200
    assert progress.get_json()["completion_rate"] == 40

    pause = client.post("/api/watch/pause", json={"engagement_id": engagement_id}, headers=headers)
    assert pause.status_code == 200
    assert pause.get_json()["pause_count"] == 1

    complete = client.post("/api/watch/complete", json={"engagement_id": engagement_id}, headers=headers)
    assert complete.status_code == 200
    assert complete.get_json()["completion_rate"] == 100

    end = client.post("/api/watch/end", json={"engagement_id": engagement_id}, headers=headers)
    assert end.status_code == 200
    assert end.get_json()["session"] is not None


def test_negative_watch_duration_rejected(client, video):
    register(client)
    token = login(client)
    headers = auth_headers(token)

    start = client.post("/api/watch/start", json={"video_id": video}, headers=headers)
    engagement_id = start.get_json()["engagement_id"]

    resp = client.post("/api/watch/progress", json={
        "engagement_id": engagement_id, "watch_duration": -10, "completion_rate": 20,
    }, headers=headers)
    assert resp.status_code == 422


def test_completion_rate_over_100_rejected(client, video):
    register(client)
    token = login(client)
    headers = auth_headers(token)

    start = client.post("/api/watch/start", json={"video_id": video}, headers=headers)
    engagement_id = start.get_json()["engagement_id"]

    resp = client.post("/api/watch/progress", json={
        "engagement_id": engagement_id, "watch_duration": 10, "completion_rate": 150,
    }, headers=headers)
    assert resp.status_code == 422


def test_cannot_progress_another_users_engagement(client, video):
    register(client, email="owner@example.com")
    owner_token = login(client, email="owner@example.com")
    start = client.post("/api/watch/start", json={"video_id": video}, headers=auth_headers(owner_token))
    engagement_id = start.get_json()["engagement_id"]

    register(client, email="intruder@example.com")
    intruder_token = login(client, email="intruder@example.com")
    resp = client.post("/api/watch/progress", json={
        "engagement_id": engagement_id, "watch_duration": 10, "completion_rate": 10,
    }, headers=auth_headers(intruder_token))
    assert resp.status_code == 404
