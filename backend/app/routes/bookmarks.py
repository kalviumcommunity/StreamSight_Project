from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import Bookmark, Video
from app.utils.errors import NotFoundError, ConflictError

bp = Blueprint("bookmarks", __name__, url_prefix="/api/bookmarks")


@bp.get("")
@jwt_required()
def list_bookmarks():
    user_id = int(get_jwt_identity())
    bookmarks = Bookmark.query.filter_by(user_id=user_id).order_by(Bookmark.created_at.desc()).all()
    return jsonify([b.to_dict() for b in bookmarks]), 200


@bp.post("/<int:video_id>")
@jwt_required()
def add_bookmark(video_id):
    user_id = int(get_jwt_identity())
    video = Video.query.get(video_id)
    if not video or not video.is_active:
        raise NotFoundError("Video not found")

    if Bookmark.query.filter_by(user_id=user_id, video_id=video_id).first():
        raise ConflictError("Video is already bookmarked")

    bookmark = Bookmark(user_id=user_id, video_id=video_id)
    db.session.add(bookmark)
    db.session.commit()
    return jsonify(bookmark.to_dict()), 201


@bp.delete("/<int:video_id>")
@jwt_required()
def remove_bookmark(video_id):
    user_id = int(get_jwt_identity())
    bookmark = Bookmark.query.filter_by(user_id=user_id, video_id=video_id).first()
    if not bookmark:
        raise NotFoundError("Bookmark not found")
    db.session.delete(bookmark)
    db.session.commit()
    return jsonify({"message": "Bookmark removed"}), 200
