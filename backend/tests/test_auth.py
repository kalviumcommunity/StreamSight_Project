from tests.conftest import register, login, auth_headers


def test_register_creates_user(client):
    resp = register(client)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["user"]["email"] == "user@example.com"
    assert "access_token" in body


def test_register_duplicate_email_conflict(client):
    register(client)
    resp = register(client)
    assert resp.status_code == 409


def test_register_invalid_email_rejected(client):
    resp = client.post("/api/auth/register", json={
        "name": "Bad Email", "email": "not-an-email", "password": "Password123!",
    })
    assert resp.status_code == 422


def test_register_short_password_rejected(client):
    resp = client.post("/api/auth/register", json={
        "name": "Short Pw", "email": "short@example.com", "password": "123",
    })
    assert resp.status_code == 422


def test_login_success(client):
    register(client)
    resp = client.post("/api/auth/login", json={"email": "user@example.com", "password": "Password123!"})
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()


def test_login_wrong_password(client):
    register(client)
    resp = client.post("/api/auth/login", json={"email": "user@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_me_requires_auth(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_returns_current_user(client):
    register(client)
    token = login(client)
    resp = client.get("/api/auth/me", headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.get_json()["email"] == "user@example.com"
