from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, get_jwt,
)

from app.extensions import db
from app.models import User, Role
from app.utils.validators import require_fields, validate_email, validate_password
from app.utils.errors import ConflictError, UnauthorizedError

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    require_fields(data, ["name", "email", "password"])
    email = validate_email(data["email"])
    validate_password(data["password"])

    if User.query.filter_by(email=email).first():
        raise ConflictError("An account with this email already exists")

    user = User(name=data["name"].strip(), email=email, role=Role.USER)
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify({"user": user.to_dict(), "access_token": token}), 201


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    require_fields(data, ["email", "password"])
    email = data["email"].strip().lower()

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(data["password"]):
        raise UnauthorizedError("Invalid email or password")
    if not user.is_active:
        raise UnauthorizedError("This account has been deactivated")

    user.last_login = datetime.utcnow()
    db.session.commit()

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify({"user": user.to_dict(), "access_token": token}), 200


@bp.get("/me")
@jwt_required()
def me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        raise UnauthorizedError("User not found")
    return jsonify(user.to_dict()), 200


@bp.post("/logout")
@jwt_required()
def logout():
    # Stateless JWT: logout is handled client-side by discarding the token.
    return jsonify({"message": "Logged out successfully"}), 200
