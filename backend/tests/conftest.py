import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from app import create_app
from app.extensions import db
from app.models import Category, Video, Role, User


@pytest.fixture()
def app():
    application = create_app("testing")
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def register(client, name="Test User", email="user@example.com", password="Password123!"):
    return client.post("/api/auth/register", json={"name": name, "email": email, "password": password})


def login(client, email="user@example.com", password="Password123!"):
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    return resp.get_json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def user_token(client):
    register(client)
    return login(client)


@pytest.fixture()
def admin_token(app, client):
    with app.app_context():
        admin = User(name="Admin", email="admin@example.com", role=Role.ADMIN)
        admin.set_password("AdminPass123!")
        db.session.add(admin)
        db.session.commit()
    return login(client, email="admin@example.com", password="AdminPass123!")


@pytest.fixture()
def category(app):
    with app.app_context():
        cat = Category(name="Drama", description="Drama shows")
        db.session.add(cat)
        db.session.commit()
        return cat.id


@pytest.fixture()
def video(app, category):
    with app.app_context():
        vid = Video(title="Test Video", category_id=category, duration=1200, views=0)
        db.session.add(vid)
        db.session.commit()
        return vid.id
