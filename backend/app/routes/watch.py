from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services import engagement_service
from app.utils.validators import require_fields, validate_non_negative, validate_completion_rate

bp = Blueprint("watch", __name__, url_prefix="/api/watch")


@bp.post("/start")
@jwt_required()
def start():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    require_fields(data, ["video_id"])
    result = engagement_service.start_watch(user_id, int(data["video_id"]))
    return jsonify(result), 201


@bp.post("/progress")
@jwt_required()
def progress():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    require_fields(data, ["engagement_id"])

    watch_duration = validate_non_negative(data.get("watch_duration"), "watch_duration")
    completion_rate = validate_completion_rate(data.get("completion_rate", 0))

    result = engagement_service.record_progress(
        user_id, int(data["engagement_id"]), watch_duration, completion_rate,
        seek_count=data.get("seek_count"),
    )
    return jsonify(result), 200


@bp.post("/pause")
@jwt_required()
def pause():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    require_fields(data, ["engagement_id"])
    result = engagement_service.record_pause(user_id, int(data["engagement_id"]))
    return jsonify(result), 200


@bp.post("/complete")
@jwt_required()
def complete():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    require_fields(data, ["engagement_id"])
    result = engagement_service.record_complete(user_id, int(data["engagement_id"]))
    return jsonify(result), 200


@bp.post("/end")
@jwt_required()
def end():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    require_fields(data, ["engagement_id"])
    result = engagement_service.end_watch(user_id, int(data["engagement_id"]))
    return jsonify(result), 200
