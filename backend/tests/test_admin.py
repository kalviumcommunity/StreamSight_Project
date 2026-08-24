import io

from tests.conftest import auth_headers, register, login


def test_list_users_requires_admin(client, user_token):
    resp = client.get("/api/users", headers=auth_headers(user_token))
    assert resp.status_code == 403


def test_list_users_as_admin(client, admin_token):
    resp = client.get("/api/users", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    assert resp.get_json()["total"] >= 1


def test_import_engagement_csv(client, admin_token, video):
    register(client)
    from app.models import User
    resp = client.get("/api/users", headers=auth_headers(admin_token))
    user_id = next(u["id"] for u in resp.get_json()["items"] if u["email"] == "user@example.com")

    csv_content = (
        "user_id,video_id,watch_duration,completion_rate,pause_count\n"
        f"{user_id},{video},500,80,1\n"
        f"{user_id},{video},-5,50,0\n"  # invalid: negative watch_duration
        "999999,999999,100,50,0\n"  # invalid: unknown user/video
    )
    data = {
        "file": (io.BytesIO(csv_content.encode("utf-8")), "engagement.csv"),
    }
    resp = client.post(
        "/api/admin/import/engagement",
        data=data,
        headers=auth_headers(admin_token),
        content_type="multipart/form-data",
    )
    assert resp.status_code == 200
    report = resp.get_json()
    assert report["total_records"] == 3
    assert report["valid_records"] == 1
    assert report["invalid_records"] == 2


def test_import_missing_file(client, admin_token):
    resp = client.post("/api/admin/import/engagement", headers=auth_headers(admin_token))
    assert resp.status_code == 422


def test_import_missing_required_columns(client, admin_token):
    csv_content = "user_id,video_id\n1,1\n"
    data = {"file": (io.BytesIO(csv_content.encode("utf-8")), "bad.csv")}
    resp = client.post(
        "/api/admin/import/engagement", data=data, headers=auth_headers(admin_token),
        content_type="multipart/form-data",
    )
    assert resp.status_code == 422
