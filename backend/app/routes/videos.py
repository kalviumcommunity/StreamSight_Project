from datetime import datetime

from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models import Video, Category
from app.utils.decorators import admin_required
from app.utils.validators import require_fields, validate_positive, validate_pagination
from app.utils.helpers import paginate_query
from app.utils.errors import NotFoundError, ValidationError

bp = Blueprint("videos", __name__, url_prefix="/api/videos")


@bp.get("")
def list_videos():
    page, per_page = validate_pagination(request.args)
    query = Video.query.filter_by(is_active=True)

    search = request.args.get("search")
    if search:
        query = query.filter(Video.title.ilike(f"%{search}%"))

    category_id = request.args.get("category_id")
    if category_id:
        query = query.filter_by(category_id=int(category_id))

    sort = request.args.get("sort", "newest")
    if sort == "views":
        query = query.order_by(Video.views.desc())
    elif sort == "title":
        query = query.order_by(Video.title.asc())
    elif sort == "duration":
        query = query.order_by(Video.duration.desc())
    else:
        query = query.order_by(Video.created_at.desc())

    result = paginate_query(query, page, per_page)
    return jsonify({**result, "items": [v.to_dict() for v in result["items"]]}), 200


@bp.get("/<int:video_id>")
def get_video(video_id):
    video = Video.query.get(video_id)
    if not video or not video.is_active:
        raise NotFoundError("Video not found")
    return jsonify(video.to_dict()), 200


def _parse_video_payload(data, existing=None):
    if not existing:
        require_fields(data, ["title", "category_id", "duration"])

    if "category_id" in data:
        if not Category.query.get(data["category_id"]):
            raise ValidationError("Invalid category_id")

    if "duration" in data:
        validate_positive(data["duration"], "duration")

    release_date = data.get("release_date")
    parsed_date = None
    if release_date:
        try:
            parsed_date = datetime.fromisoformat(release_date).date()
        except ValueError:
            raise ValidationError("release_date must be an ISO date (YYYY-MM-DD)")
    return parsed_date


@bp.post("")
@admin_required
def create_video():
    data = request.get_json(silent=True) or {}
    parsed_date = _parse_video_payload(data)

    video = Video(
        title=data["title"].strip(),
        description=data.get("description"),
        category_id=data["category_id"],
        duration=int(data["duration"]),
        thumbnail_url=data.get("thumbnail_url"),
        video_url=data.get("video_url"),
        release_date=parsed_date,
    )
    db.session.add(video)
    db.session.commit()
    return jsonify(video.to_dict()), 201


@bp.put("/<int:video_id>")
@admin_required
def update_video(video_id):
    video = Video.query.get(video_id)
    if not video:
        raise NotFoundError("Video not found")

    data = request.get_json(silent=True) or {}
    parsed_date = _parse_video_payload(data, existing=video)

    for field in ["title", "description", "category_id", "thumbnail_url", "video_url"]:
        if field in data:
            setattr(video, field, data[field].strip() if isinstance(data.get(field), str) else data[field])
    if "duration" in data:
        video.duration = int(data["duration"])
    if "release_date" in data:
        video.release_date = parsed_date
    if "is_active" in data:
        video.is_active = bool(data["is_active"])

    db.session.commit()
    return jsonify(video.to_dict()), 200


@bp.delete("/<int:video_id>")
@admin_required
def deactivate_video(video_id):
    video = Video.query.get(video_id)
    if not video:
        raise NotFoundError("Video not found")
    video.is_active = False
    db.session.commit()
    return jsonify({"message": "Video deactivated"}), 200
