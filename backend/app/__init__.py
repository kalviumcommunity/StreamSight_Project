import os

from flask import Flask, jsonify

from app.config import config_by_name
from app.extensions import db, jwt, cors, migrate
from app.utils.errors import register_error_handlers


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["development"]))

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["FRONTEND_URL"]}})

    register_error_handlers(app)
    _register_jwt_handlers(jwt)

    from app.routes import register_routes
    register_routes(app)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    return app


def _register_jwt_handlers(jwt_manager):
    @jwt_manager.unauthorized_loader
    def missing_token(reason):
        return jsonify({"error": "Authentication required"}), 401

    @jwt_manager.invalid_token_loader
    def invalid_token(reason):
        return jsonify({"error": "Invalid authentication token"}), 401

    @jwt_manager.expired_token_loader
    def expired_token(header, payload):
        return jsonify({"error": "Authentication token has expired"}), 401
