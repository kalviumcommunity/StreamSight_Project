from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import WatchHistory
from app.services.recommendation_service import continue_watching
from app.utils.validators import validate_pagination
from app.utils.helpers import paginate_query
from app.utils.errors import NotFoundError

bp = Blueprint("history", __name__, url_prefix="/api/history")


@bp.get("")
@jwt_required()
def list_history():
    user_id = int(get_jwt_identity())
    page, per_page = validate_pagination(request.args)
    query = WatchHistory.query.filter_by(user_id=user_id).order_by(WatchHistory.watched_at.desc())
    result = paginate_query(query, page, per_page)
    return jsonify({**result, "items": [h.to_dict() for h in result["items"]]}), 200


@bp.delete("/<int:history_id>")
@jwt_required()
def delete_history(history_id):
    user_id = int(get_jwt_identity())
    entry = WatchHistory.query.get(history_id)
    if not entry or entry.user_id != user_id:
        raise NotFoundError("History entry not found")
    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": "History entry deleted"}), 200


@bp.get("/continue-watching")
@jwt_required()
def continue_watching_route():
    user_id = int(get_jwt_identity())
    limit = int(request.args.get("limit", 10))
    return jsonify(continue_watching(user_id, limit)), 200
