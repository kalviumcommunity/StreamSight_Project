from tests.conftest import register, login, auth_headers


def test_add_and_list_bookmark(client, video):
    register(client)
    token = login(client)
    headers = auth_headers(token)

    resp = client.post(f"/api/bookmarks/{video}", headers=headers)
    assert resp.status_code == 201

    resp = client.get("/api/bookmarks", headers=headers)
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_duplicate_bookmark_rejected(client, video):
    register(client)
    token = login(client)
    headers = auth_headers(token)

    client.post(f"/api/bookmarks/{video}", headers=headers)
    resp = client.post(f"/api/bookmarks/{video}", headers=headers)
    assert resp.status_code == 409


def test_remove_bookmark(client, video):
    register(client)
    token = login(client)
    headers = auth_headers(token)

    client.post(f"/api/bookmarks/{video}", headers=headers)
    resp = client.delete(f"/api/bookmarks/{video}", headers=headers)
    assert resp.status_code == 200

    resp = client.get("/api/bookmarks", headers=headers)
    assert len(resp.get_json()) == 0
