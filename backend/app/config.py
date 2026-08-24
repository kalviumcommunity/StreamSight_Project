import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def _engine_options():
    """Enable TLS for managed MySQL providers (e.g. Aiven) that require it.

    PyMySQL only opens a TLS connection when passed a truthy `ssl` dict, and
    Aiven's certificate isn't in the local trust store, so verification is
    disabled the same way `ssl-mode=REQUIRED` behaves (encrypted, unverified).
    """
    if os.environ.get("DATABASE_SSL", "false").lower() == "true":
        return {"connect_args": {"ssl": {"check_hostname": False, "verify_mode": False}}}
    return {}


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'streamsight.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = _engine_options()
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)


config_by_name = {
    "development": Config,
    "production": Config,
    "testing": TestingConfig,
}
