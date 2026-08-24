from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.analytics_service import trending_content
from app.services.recommendation_service import featured_content, recommended_for_user

bp = Blueprint("home", __name__, url_prefix="/api/home")


@bp.get("/featured")
def featured():
    return jsonify(featured_content()), 200


@bp.get("/trending")
def trending():
    period = request.args.get("period", "weekly")
    limit = int(request.args.get("limit", 10))
    return jsonify(trending_content(period, limit)), 200


@bp.get("/recommended")
@jwt_required()
def recommended():
    user_id = int(get_jwt_identity())
    limit = int(request.args.get("limit", 10))
    return jsonify(recommended_for_user(user_id, limit)), 200
